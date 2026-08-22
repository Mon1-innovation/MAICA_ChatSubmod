# -*- coding: utf-8 -*-

import threading

from bot_interface import logger, to_unicode
HTTP_TIMEOUT = (5.0, 30.0)


class MaicaProviderManager(object):
    """MAICA服务提供商管理器 - 实例化模式"""

    # 类级别的共享数据
    _isfailedresponse = {
        "id": 0,
        "name": u"ERROR: 无法获取节点信息",
        "description": u"查看更新日志来获取当前的服务状态, 或者查看submod_log.log获取失败原因",
        "isOfficial": False,
        "portalPage": "https://forum.monika.love/d/3954",
        "servingModel": u"查看更新日志来获取当前的服务状态, 或者查看submod_log.log获取失败原因",
        "modelLink": "",
        "wsInterface": "wss://maicadev.monika.love/websocket",
        "httpInterface": "https://maicadev.monika.love/api"
    }

    _fakelocalprovider = {
        "id": 9999,
        "name": u"本地部署",
        "description": u"当你有可用的本地部署时, 选择此节点",
        "isOfficial": False,
        "portalPage": "https://github.com/PencilMario/MAICA",
        "servingModel": "None",
        "modelLink": "",
        "wsInterface": "ws://127.0.0.1:5000",
        "httpInterface": "http://127.0.0.1:6000",
    }

    _provider_list = "https://maicadev.monika.love/api/servers"

    def __init__(self, pid=None):
        """
        初始化MaicaProviderManager实例

        Args:
            pid: 服务提供商ID，如果为None则使用默认值
        """
        self._provider_id = pid
        self._last_provider_id = pid
        self._isfailedresponse = self._isfailedresponse.copy()
        self._servers = [self._fakelocalprovider]
        self._isMaicaNameServer = None
        self._last_missing_provider_id = object()
        self._refresh_lock = threading.Lock()
        self._refresh_in_progress = False
        self._last_refresh_error = None
        self._has_valid_provider_catalog = False

    def _record_refresh_failure(self, message, code=None):
        message = to_unicode(message)
        self._last_refresh_error = {
            "status": "client_provider_unavailable",
            "exception": message,
            "code": code,
        }
        self._isfailedresponse["description"] = message
        if not self._has_valid_provider_catalog:
            self._servers = [self._isfailedresponse, self._fakelocalprovider]
        return False

    def is_refreshing(self):
        return self._refresh_in_progress

    def get_last_refresh_error(self):
        if self._last_refresh_error is None:
            return None
        return self._last_refresh_error.copy()

    def get_servers(self):
        return list(self._servers)

    def get_provider(self):
        """获取服务提供商列表"""
        import requests
        self._refresh_lock.acquire()
        self._refresh_in_progress = True
        try:
            res = requests.get(self._provider_list, timeout=HTTP_TIMEOUT)
            if res.status_code != 200:
                logger.error("Cannot get providers because server return non 200: {}".format(res.content))
                return self._record_refresh_failure(
                    "Provider list server returned HTTP {}".format(res.status_code),
                    res.status_code,
                )

            payload = res.json()
            if not isinstance(payload, dict):
                return self._record_refresh_failure(
                    "Provider list server returned an invalid response"
                )
            if not payload.get("success"):
                message = payload.get("exception") or "Provider list request was rejected"
                logger.error("Cannot get providers because server return: {}".format(payload))
                return self._record_refresh_failure(message, res.status_code)

            content = payload.get("content")
            if not isinstance(content, dict) or not isinstance(content.get("servers"), list):
                return self._record_refresh_failure(
                    "Provider list response did not contain a valid server list",
                    res.status_code,
                )

            new_servers = list(content["servers"])
            new_servers.append(self._fakelocalprovider)
            self._isMaicaNameServer = content.get("isMaicaNameServer")

            if not self._provider_id:
                self._provider_id = self._last_provider_id

            self._servers = new_servers
            self._last_refresh_error = None
            self._has_valid_provider_catalog = True
            return True
        except Exception as e:
            message = to_unicode(e)
            logger.error("Error getting providers: {}".format(message))
            return self._record_refresh_failure(message)
        finally:
            self._refresh_in_progress = False
            self._refresh_lock.release()

    def _get_server_by_id(self, server_id):
        """根据ID获取服务器信息"""
        try:
            requested_id = int(server_id)
        except (TypeError, ValueError):
            requested_id = None
        for server in self._servers:
            if int(server["id"]) == requested_id:
                self._last_missing_provider_id = object()
                return server
        if self._last_missing_provider_id != server_id:
            logger.warning(
                "Provider id {!r} is unavailable; using the fallback endpoint".format(
                    server_id
                )
            )
            self._last_missing_provider_id = server_id
        return self._isfailedresponse

    def get_wssurl(self):
        """获取WebSocket URL"""
        url = self._get_server_by_id(self._provider_id)["wsInterface"]
        if isinstance(url, str):
            url = url.strip('/')
        return url

    def get_api_url(self):
        """获取API URL"""
        url = self._get_server_by_id(self._provider_id)["httpInterface"]
        if isinstance(url, str):
            url = url.strip('/')
        return url

    def get_server_info(self):
        """获取当前服务器信息"""
        return self._get_server_by_id(self._provider_id)
    def set_provider_id(self, pid):
        """设置provider_id"""
        changed = pid != self._provider_id
        self._provider_id = pid
        if changed:
            self._last_missing_provider_id = object()
        if pid:
            self._last_provider_id = pid

    def get_provider_id(self):
        """获取provider_id"""
        return self._provider_id
