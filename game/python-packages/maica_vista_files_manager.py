# -*- coding: utf-8 -*-
import time
import os
import shutil
import requests
import struct
import subprocess
from bot_interface import logger

class MAICAVistaFilesManager(object):
    """MVista图片管理器，用于上传、删除、下载图片并管理本地UUID记录"""


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
    def _get_image_size(file_path):
        """获取图片尺寸（不使用第三方库）

        Args:
            file_path: 图片文件路径

        Returns:
            (width, height) 元组，失败时返回 (200, 200)
        """
        try:
            with open(file_path, 'rb') as f:
                head = f.read(24)
                if len(head) < 24:
                    return (200, 200)

                # PNG
                if head[:8] == b'\x89PNG\r\n\x1a\n':
                    f.seek(16)
                    return struct.unpack('>II', f.read(8))

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
                    return (width, height)

                # GIF
                elif head[:6] in (b'GIF87a', b'GIF89a'):
                    return struct.unpack('<HH', head[6:10])

                # BMP
                elif head[:2] == b'BM':
                    return struct.unpack('<II', head[18:26])

                # WebP
                elif head[:4] == b'RIFF' and head[8:12] == b'WEBP':
                    if head[12:16] == b'VP8 ':
                        f.seek(26)
                        width, height = struct.unpack('<HH', f.read(4))
                        return (width & 0x3fff, height & 0x3fff)
                    elif head[12:16] == b'VP8L':
                        f.seek(21)
                        data = struct.unpack('<I', f.read(4))[0]
                        width = (data & 0x3fff) + 1
                        height = ((data >> 14) & 0x3fff) + 1
                        return (width, height)
                    elif head[12:16] == b'VP8X':
                        f.seek(24)
                        width = struct.unpack('<I', b'\x00' + f.read(3))[0] + 1
                        height = struct.unpack('<I', b'\x00' + f.read(3))[0] + 1
                        return (width, height)

        except Exception:
            pass

        return (200, 200)

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
            resp = requests.post(self.base_url + '/vista', data=data, files=files)
            result = resp.json()
            if result.get('success'):
                uuid = result.get('content')
                cached_path = file_path
                thumb_path = None
                if self.cache_path:
                    ext = os.path.splitext(file_path)[1]
                    cached_path = os.path.join(self.cache_path, uuid + ext)
                    # 只有当源文件不在缓存目录中时才复制
                    if os.path.abspath(file_path) != os.path.abspath(cached_path):
                        shutil.copy2(file_path, cached_path)
                    # 生成缩略图
                    try:
                        width, height = self._get_image_size(file_path)
                        max_side = max(width, height)
                        if max_side > 500:
                            thumb_path = os.path.join(self.cache_path, 'thumb_' + uuid + ext)
                            if self.magick_path:
                                subprocess.call([self.magick_path, file_path, '-resize', '500x500', thumb_path])
                            else:
                                if os.path.abspath(file_path) != os.path.abspath(thumb_path):
                                    shutil.copy2(file_path, thumb_path)
                    except Exception as e:
                        logger.error("fail to generate thumbnail: {}".format(str(e)))
                self.add(uuid, file_path=cached_path, thumb_path=thumb_path)
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

        self.remove(identifier)
        return self.upload(file_path)

    def delete(self, identifier=None):
        """删除服务器上的图片（DELETE /vista）

        Args:
            identifier: UUID字符串、索引或None（删除全部）
        """
        data = {'access_token': self.access_token}
        if identifier is not None:
            data['content'] = identifier
        resp = requests.delete(self.base_url + '/vista', json=data)
        result = resp.json()
        if identifier:
            self.remove(identifier)
        if result.get('success'):
            if identifier is None:
                self.clear()
                self.cloud_files = []
                if self.cloud_files and identifier in self.cloud_files:
                    self.cloud_files.remove(identifier)
        else:
            raise Exception(result.get('exception'))

    def download(self, uuid):
        """下载图片（GET /vista）

        Args:
            uuid: 图片UUID

        Returns:
            图片二进制数据或UUID列表
        """
        resp = requests.get(self.base_url + '/vista', params={'content': uuid})
        if resp.headers.get('content-type', '').startswith('image/'):
            return resp.content
        result = resp.json()
        if not result.get('success'):
            raise Exception(result.get('exception'))
        return result.get('content')

    def list_remote(self, force_refresh=False):
        """获取服务器上可用的图片UUID列表（GET /vista）

        Args:
            force_refresh: 强制刷新缓存

        Returns:
            UUID列表
        """
        current_time = time.time()
        if not force_refresh and self.cloud_files and (current_time - self._cloud_files_cache_time) < self._cloud_files_cache_ttl:
            return self.cloud_files

        resp = requests.get(self.base_url + '/vista', params={'access_token': self.access_token})
        result = resp.json()
        if result.get('success'):
            self.cloud_files = result.get('content')
            self._cloud_files_cache_time = current_time
            return self.cloud_files
        raise Exception(result.get('exception'))
