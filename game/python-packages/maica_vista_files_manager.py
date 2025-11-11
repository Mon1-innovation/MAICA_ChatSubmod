# -*- coding: utf-8 -*-
import time
import os
import shutil
import requests

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

    @property
    def cache_path(self):
        return self._cache_path

    @cache_path.setter
    def cache_path(self, value):
        self._cache_path = value
        if value and not os.path.exists(value):
            os.makedirs(value)

    def add(self, uuid, file_path=None, upload_time=None):
        """添加UUID到本地记录（最新的在前）"""
        entry = {"uuid": uuid, "upload_time": upload_time or time.time()}
        if file_path:
            entry["path"] = file_path.replace('\\', '/')
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

    def export_list(self):
        """导出为列表"""
        return list(self.files)

    def import_list(self, data):
        """从列表导入数据"""
        self.files = []
        for entry in data:
            if "path" in entry:
                entry["path"] = entry["path"].replace('\\', '/')
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
                if self.cache_path:
                    cached_path = os.path.join(self.cache_path, os.path.basename(file_path))
                    shutil.copy2(file_path, cached_path)
                self.add(uuid, file_path=cached_path)
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
        if result.get('success'):
            if identifier is None:
                self.clear()
            else:
                self.remove(identifier)
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

    def list_remote(self):
        """获取服务器上可用的图片UUID列表（GET /vista）

        Returns:
            UUID列表
        """
        resp = requests.get(self.base_url + '/vista', params={'access_token': self.access_token})
        result = resp.json()
        if result.get('success'):
            return result.get('content')
        raise Exception(result.get('exception'))
