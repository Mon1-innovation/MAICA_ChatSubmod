# -*- coding: utf-8 -*-
import time
import os
import shutil
import requests
import struct
import subprocess
import hashlib
from bot_interface import logger


try:
    text_type = unicode
except NameError:
    text_type = str


class MAICAVistaFilesManager(object):
    """MVista图片管理器，用于上传、删除、下载图片并管理本地UUID记录"""

    THUMBNAIL_VERSION = 1
    THUMBNAIL_MAX_WIDTH = 600
    THUMBNAIL_MAX_HEIGHT = 300
    _THUMBNAIL_KEYS = (
        "thumb_path",
        "thumb_width",
        "thumb_height",
        "thumb_version",
    )


    def __init__(self, base_url, access_token, cache_path=None):
        """初始化管理器

        Args:
            base_url: API基础URL
            access_token: 访问令牌
            cache_path: 缓存目录路径，若提供则自动创建并缓存上传文件
        """
        self.base_url = base_url.rstrip('/')
        self.access_token = access_token
        self._cache_path = None
        self.cache_path = cache_path
        self.files = []
        self.cloud_files = []
        self._cloud_files_cache_time = 0
        self._cloud_files_cache_ttl = 240
        self.android = False
        self.magick_path = None

    @staticmethod
    def _probe_image_size(file_path):
        """读取受支持图片的头部尺寸，无法确定时返回None。"""
        image_size = None

        try:
            with open(file_path, 'rb') as f:
                head = f.read(24)
                if len(head) < 24:
                    return None

                # PNG
                if head[:8] == b'\x89PNG\r\n\x1a\n':
                    f.seek(16)
                    image_size = struct.unpack('>II', f.read(8))

                # JPEG
                elif head[:2] == b'\xff\xd8':
                    f.seek(0)
                    size = 2
                    ftype = 0
                    while not 0xc0 <= ftype <= 0xcf or ftype in (0xc4, 0xc8, 0xcc):
                        f.seek(size, 1)
                        byte = f.read(1)
                        while ord(byte) == 0xff:
                            byte = f.read(1)
                        ftype = ord(byte)
                        size = struct.unpack('>H', f.read(2))[0] - 2
                    f.seek(1, 1)
                    height, width = struct.unpack('>HH', f.read(4))
                    image_size = (width, height)

                # GIF
                elif head[:6] in (b'GIF87a', b'GIF89a'):
                    image_size = struct.unpack('<HH', head[6:10])

                # BMP
                elif head[:2] == b'BM':
                    f.seek(18)
                    width, height = struct.unpack('<ii', f.read(8))
                    image_size = (width, abs(height))

                # WebP
                elif head[:4] == b'RIFF' and head[8:12] == b'WEBP':
                    if head[12:16] == b'VP8 ':
                        f.seek(26)
                        width, height = struct.unpack('<HH', f.read(4))
                        image_size = (width & 0x3fff, height & 0x3fff)
                    elif head[12:16] == b'VP8L':
                        f.seek(21)
                        data = struct.unpack('<I', f.read(4))[0]
                        width = (data & 0x3fff) + 1
                        height = ((data >> 14) & 0x3fff) + 1
                        image_size = (width, height)
                    elif head[12:16] == b'VP8X':
                        f.seek(24)
                        width = struct.unpack('<I', f.read(3) + b'\x00')[0] + 1
                        height = struct.unpack('<I', f.read(3) + b'\x00')[0] + 1
                        image_size = (width, height)

        except Exception:
            return None

        if image_size is None:
            return None

        width, height = image_size
        if width <= 0 or height <= 0:
            return None

        return (width, height)

    @staticmethod
    def _get_image_size(file_path):
        """获取图片尺寸；保留旧记录所需的200x200兼容回退。"""
        return MAICAVistaFilesManager._probe_image_size(file_path) or (200, 200)

    @staticmethod
    def _digest(value):
        if isinstance(value, bytes):
            encoded = value
        else:
            encoded = text_type(value).encode('utf-8')
        return hashlib.sha256(encoded).hexdigest()

    def _thumbnail_output_path(self, identifier):
        if not self.cache_path:
            return None
        filename = "thumb_{}.png".format(self._digest(identifier))
        return os.path.join(self.cache_path, filename)

    def _thumbnail_display_path(self, file_path):
        if not self.android:
            return file_path.replace('\\', '/')
        return os.path.join(
            "Submods",
            "MAICA_ChatSubmod",
            "vista_cache",
            os.path.basename(file_path),
        ).replace('\\', '/')

    def _thumbnail_disk_path(self, file_path):
        if not file_path:
            return None
        normalized = os.path.normpath(file_path)
        if os.path.isabs(normalized) or not self.cache_path:
            return normalized
        return os.path.join(self.cache_path, os.path.basename(normalized))

    def _thumbnail_path_is_managed(self, file_path):
        if not self.cache_path or not file_path:
            return False

        disk_path = os.path.abspath(self._thumbnail_disk_path(file_path))
        cache_path = os.path.abspath(self.cache_path)
        try:
            relative_path = os.path.relpath(disk_path, cache_path)
        except (OSError, ValueError):
            return False

        if relative_path == os.pardir or relative_path.startswith(os.pardir + os.sep):
            return False

        filename = os.path.basename(disk_path)
        return filename.startswith("thumb_") and filename.endswith(".png")

    @classmethod
    def _thumbnail_dimensions_are_safe(cls, width, height):
        return (
            width > 0
            and height > 0
            and width <= cls.THUMBNAIL_MAX_WIDTH
            and height <= cls.THUMBNAIL_MAX_HEIGHT
        )

    def _clear_thumbnail_metadata(self, entry):
        for key in self._THUMBNAIL_KEYS:
            entry.pop(key, None)

    def get_thumbnail_info(self, entry):
        """返回经过头部校验的缩略图路径和尺寸，不会读取原图。"""
        if not isinstance(entry, dict):
            return None
        if entry.get("thumb_version") != self.THUMBNAIL_VERSION:
            return None

        try:
            width = int(entry.get("thumb_width"))
            height = int(entry.get("thumb_height"))
        except (TypeError, ValueError):
            return None

        if not self._thumbnail_dimensions_are_safe(width, height):
            return None

        thumb_path = entry.get("thumb_path")
        if not self._thumbnail_path_is_managed(thumb_path):
            return None

        disk_path = self._thumbnail_disk_path(thumb_path)
        if not disk_path or not os.path.exists(disk_path):
            return None
        if self._probe_image_size(disk_path) != (width, height):
            return None

        return (entry["thumb_path"], width, height)

    def _remove_generated_file(self, file_path):
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

    def _generate_thumbnail(self, source_path, identifier):
        if not self.cache_path or not self.magick_path:
            return None
        if not source_path or not os.path.exists(source_path):
            return None

        output_path = self._thumbnail_output_path(identifier)
        self._remove_generated_file(output_path)
        geometry = "{}x{}>".format(
            self.THUMBNAIL_MAX_WIDTH,
            self.THUMBNAIL_MAX_HEIGHT,
        )
        command = [
            self.magick_path,
            source_path + "[0]",
            '-auto-orient',
            '-thumbnail',
            geometry,
            '-strip',
            output_path,
        ]

        try:
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                return_code = subprocess.call(command, startupinfo=startupinfo)
            else:
                return_code = subprocess.call(command)

            if return_code != 0:
                raise RuntimeError("ImageMagick exited with status {}".format(return_code))

            dimensions = self._probe_image_size(output_path)
            if dimensions is None or not self._thumbnail_dimensions_are_safe(*dimensions):
                raise ValueError("generated thumbnail has invalid dimensions")

            return (output_path, dimensions[0], dimensions[1])

        except Exception as e:
            self._remove_generated_file(output_path)
            logger.error("fail to generate thumbnail: {}".format(str(e)))
            return None

    def ensure_thumbnail(self, entry):
        """确保记录拥有可安全交给Ren'Py解码的受限尺寸缩略图。"""
        if self.get_thumbnail_info(entry) is not None:
            return True

        legacy_thumb_path = self._thumbnail_disk_path(entry.get("thumb_path"))
        source_path = entry.get("path")
        if not source_path or not os.path.exists(source_path):
            source_path = legacy_thumb_path

        identifier = entry.get("uuid") or source_path
        generated = self._generate_thumbnail(source_path, identifier)
        if generated is None:
            self._clear_thumbnail_metadata(entry)
            return False

        thumb_path, width, height = generated
        entry["thumb_path"] = self._thumbnail_display_path(thumb_path)
        entry["thumb_width"] = width
        entry["thumb_height"] = height
        entry["thumb_version"] = self.THUMBNAIL_VERSION
        return True

    def prepare_thumbnails(self):
        for entry in list(self.files):
            try:
                self.ensure_thumbnail(entry)
            except Exception as e:
                self._clear_thumbnail_metadata(entry)
                logger.error("fail to prepare thumbnail: {}".format(str(e)))

    def create_local_preview(self, file_path):
        """为未上传的MPostal附件创建安全预览记录。"""
        if not file_path:
            return None

        try:
            stat = os.stat(file_path)
            signature = "{}|{}|{}".format(
                os.path.abspath(file_path),
                stat.st_size,
                stat.st_mtime,
            )
        except Exception:
            signature = os.path.abspath(file_path)

        entry = {"uuid": "local:" + signature, "path": file_path}
        if not self.ensure_thumbnail(entry):
            return None

        return dict(
            (key, entry[key])
            for key in self._THUMBNAIL_KEYS
            if key in entry
        )

    @property
    def cache_path(self):
        return self._cache_path

    @cache_path.setter
    def cache_path(self, value):
        self._cache_path = value
        if value and not os.path.exists(value):
            os.makedirs(value)

    def add(self, uuid, file_path=None, upload_time=None, width=None, height=None, thumb_path=None):
        """添加UUID到本地记录（最新的在前）"""
        entry = {"uuid": uuid, "upload_time": upload_time or time.time()}
        if file_path:
            entry["path"] = file_path.replace('\\', '/')
            # 如果没有提供宽高，尝试从文件读取
            if width is None or height is None:
                if os.path.exists(file_path):
                    width, height = self._get_image_size(file_path)
                else:
                    width, height = 200, 200
        # 如果仍然没有宽高，使用默认值
        entry["width"] = width if width is not None else 200
        entry["height"] = height if height is not None else 200
        if thumb_path:
            if not self.android:
                entry["thumb_path"] = thumb_path.replace('\\', '/')
            else:
                entry["thumb_path"] = os.path.join("Submods", "MAICA_ChatSubmod", "vista_cache", os.path.basename(thumb_path))
        self.files.insert(0, entry)
        return entry

    def remove(self, identifier):
        """从本地记录删除UUID

        Args:
            identifier: UUID字符串或索引（从0开始）
        """
        if isinstance(identifier, int):
            if 0 <= identifier < len(self.files):
                del self.files[identifier]
        else:
            self.files = [f for f in self.files if f.get("uuid") != identifier]

    def clear(self):
        """清空本地所有记录"""
        self.files = []

    def get_uuids(self):
        """获取所有本地存储的UUID"""
        return [f.get("uuid") for f in self.files]

    def get_info(self, uuid):
        """获取指定UUID的详细信息"""
        for f in self.files:
            if f.get("uuid") == uuid:
                return f

    def export_list(self):
        """导出为列表"""
        return list(self.files)

    def import_list(self, data):
        """从列表导入数据"""
        self.files = []
        for entry in data:
            if "path" in entry:
                entry["path"] = entry["path"].replace('\\', '/')
            # 如果没有宽高信息，尝试从文件读取或使用默认值
            if "width" not in entry or "height" not in entry:
                if "path" in entry and os.path.exists(entry["path"]):
                    width, height = self._get_image_size(entry["path"])
                    entry["width"] = width
                    entry["height"] = height
                else:
                    entry["width"] = entry.get("width", 200)
                    entry["height"] = entry.get("height", 200)
            self.files.append(entry)

    def upload(self, file_path):
        """上传图片到服务器（POST /vista）

        Args:
            file_path: 图片文件路径（最大32MB）

        Returns:
            服务器分配的UUID
        """
        with open(file_path, 'rb') as f:
            files = {'content': f}
            data = {'access_token': self.access_token}
            resp = requests.post(self.base_url + '/vista', data=data, files=files, timeout=(5.0, 60.0))
            result = resp.json()
            if result.get('success'):
                uuid = result.get('content')
                cached_path = file_path
                if self.cache_path:
                    ext = os.path.splitext(file_path)[1]
                    cached_path = os.path.join(self.cache_path, uuid + ext)
                    # 只有当源文件不在缓存目录中时才复制
                    if os.path.abspath(file_path) != os.path.abspath(cached_path):
                        shutil.copy2(file_path, cached_path)
                entry = self.add(uuid, file_path=cached_path)
                if self.cache_path and not self.ensure_thumbnail(entry):
                    logger.error("thumbnail unavailable for MVista image {}".format(uuid))
                if self.cloud_files and uuid not in self.cloud_files:
                    self.cloud_files.append(uuid)
                return uuid
            raise Exception(result.get('exception'))

    def reupload(self, identifier):
        """重新上传已过期的图片

        Args:
            identifier: UUID字符串或索引（从0开始）

        Returns:
            新的UUID
        """
        if isinstance(identifier, int):
            if 0 <= identifier < len(self.files):
                entry = self.files[identifier]
            else:
                raise ValueError("Invalid index")
        else:
            entry = next((f for f in self.files if f.get("uuid") == identifier), None)
            if not entry:
                raise ValueError("UUID not found")

        file_path = entry.get("path")
        if not file_path:
            raise ValueError("No file path stored for this entry")

        new_uuid = self.upload(file_path)
        self.files = [item for item in self.files if item is not entry]
        if entry.get("uuid") in self.cloud_files:
            self.cloud_files.remove(entry.get("uuid"))
        return new_uuid

    def delete(self, identifier=None):
        """删除服务器上的图片（DELETE /vista）

        Args:
            identifier: UUID字符串、索引或None（删除全部）
        """
        uuid = identifier
        if isinstance(identifier, int):
            if not 0 <= identifier < len(self.files):
                raise ValueError("Invalid index")
            uuid = self.files[identifier].get("uuid")

        data = {'access_token': self.access_token}
        if uuid is not None:
            data['content'] = uuid
        resp = requests.delete(self.base_url + '/vista', json=data, timeout=(5.0, 30.0))
        result = resp.json()
        if not result.get('success'):
            raise Exception(result.get('exception'))
        if identifier is None:
            self.clear()
            self.cloud_files = []
        else:
            self.remove(identifier)
            if uuid in self.cloud_files:
                self.cloud_files.remove(uuid)

    def download(self, uuid):
        """下载图片（GET /vista）

        Args:
            uuid: 图片UUID

        Returns:
            图片二进制数据或UUID列表
        """
        resp = requests.get(self.base_url + '/vista', params={'content': uuid}, timeout=(5.0, 60.0))
        if resp.headers.get('content-type', '').startswith('image/'):
            return resp.content
        result = resp.json()
        if not result.get('success'):
            raise Exception(result.get('exception'))
        return result.get('content')

    def list_remote(self, force_refresh=False):
        """获取服务器上可用的图片UUID列表（GET /vista/list）

        Args:
            force_refresh: 强制刷新缓存

        Returns:
            UUID列表
        """
        current_time = time.time()
        if not force_refresh and self.cloud_files and (current_time - self._cloud_files_cache_time) < self._cloud_files_cache_ttl:
            return self.cloud_files

        resp = requests.get(
            self.base_url + '/vista/list',
            params={'access_token': self.access_token},
            timeout=(5.0, 30.0)
        )
        result = resp.json()
        if result.get('success'):
            self.cloud_files = result.get('content')
            self._cloud_files_cache_time = current_time
            return self.cloud_files
        raise Exception(result.get('exception'))
