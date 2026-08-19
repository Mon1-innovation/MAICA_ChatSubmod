# -*- coding: utf-8 -*-

from bot_interface import logger
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
        self._servers = [self._fakelocalprovider]
        self._isMaicaNameServer = None
        self._last_missing_provider_id = object()

    def get_provider(self):
        """获取服务提供商列表"""
        import requests
        try:
            res = requests.get(self._provider_list, json={}, timeout=HTTP_TIMEOUT)
            if res.status_code != 200:
                logger.error("Cannot get providers because server return non 200: {}".format(res.content))
                self._isfailedresponse["description"] = "Cannot get providers because server {}".format(res.status_code)
                new_servers = [self._isfailedresponse, self._fakelocalprovider]
            else:
                res = res.json()
                if res["success"]:
                    self._isMaicaNameServer = res["content"].get("isMaicaNameServer")
                    new_servers = res["content"].get("servers", [])
                    new_servers.append(self._fakelocalprovider)

                    if not self._provider_id:
                        self._provider_id = self._last_provider_id

                    self._servers = new_servers
                    return True
                else:
                    self._isfailedresponse["description"] = res["exception"]
                    new_servers = [self._isfailedresponse, self._fakelocalprovider]
                    logger.error("Cannot get providers because server return: {}".format(res))
        except Exception as e:
            logger.error("Error getting providers: {}".format(e))
            new_servers = [self._isfailedresponse, self._fakelocalprovider]

        self._servers = new_servers
        return False

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
