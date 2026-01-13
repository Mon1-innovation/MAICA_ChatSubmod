# -*- coding: utf-8 -*-

class DefaultLogger(object):
    """
    默认日志记录器，用于在没有提供日志记录器的情况下输出日志信息。
    """
    def debug(self, msg):
        """输出调试级别的日志"""
        print("[DEBUG] {}".format(msg))

    def info(self, msg):
        """输出信息级别的日志"""
        print("[INFO] {}".format(msg))

    def error(self, msg):
        """输出错误级别的日志"""
        print("[ERROR] {}".format(msg))

    def warning(self, msg):
        """输出警告级别的日志"""
        print("[WARNING] {}".format(msg))


logger = DefaultLogger()


class MaicaProviderManager:
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

    def __init__(self, provider_id=None):
        """
        初始化MaicaProviderManager实例

        Args:
            provider_id: 服务提供商ID，如果为None则使用默认值
        """
        self.provider_id = provider_id
        self._last_provider_id = provider_id
        self._servers = [self._fakelocalprovider]
        self._isMaicaNameServer = None

    def get_provider(self):
        """获取服务提供商列表"""
        self._servers = []
        import requests
        try:
            res = requests.get(self._provider_list, json={})
            if res.status_code != 200:
                logger.error("Cannot get providers because server return non 200: {}".format(res.content))
                self._isfailedresponse["description"] = "Cannot get providers because server {}".format(res.status_code)
                self._servers.append(self._isfailedresponse)
                self._servers.append(self._fakelocalprovider)
                return False
            res = res.json()

            if res["success"]:
                self._isMaicaNameServer = res["content"].get("isMaicaNameServer")
                self._servers = res["content"].get("servers")
                self._servers.append(self._fakelocalprovider)

                if not self.provider_id:
                    self.provider_id = self._last_provider_id

                return True
            else:
                self._isfailedresponse["description"] = res["exception"]
                self._servers.append(self._isfailedresponse)
                self._servers.append(self._fakelocalprovider)
                logger.error("Cannot get providers because server return: {}".format(res))
                return False
        except Exception as e:
            logger.error("Error getting providers: {}".format(e))
            self._servers.append(self._isfailedresponse)
            self._servers.append(self._fakelocalprovider)
            return False

    def _get_server_by_id(self, server_id):
        """根据ID获取服务器信息"""
        for server in self._servers:
            if int(server["id"]) == server_id:
                return server
        logger.error("Cannot find server by id: {}, returning default failed response".format(server_id))
        return self._isfailedresponse

    def get_wssurl(self):
        """获取WebSocket URL"""
        if self.provider_id is None:
            logger.warning("Cannot find server by id: {}, returning default failed response".format(self.provider_id))
            return self._isfailedresponse["wsInterface"] + "/"
        return self._get_server_by_id(self.provider_id)["wsInterface"] + "/"

    def get_api_url(self):
        """获取API URL"""
        if self.provider_id is None:
            logger.warning("Cannot find server by id: {}, returning default failed response".format(self.provider_id))
            return self._isfailedresponse["httpInterface"] + "/"
        return self._get_server_by_id(self.provider_id)["httpInterface"] + "/"

    def get_server_info(self):
        """获取当前服务器信息"""
        if self.provider_id is None:
            logger.error("Cannot find server by id: {}, returning default failed response".format(self.provider_id))
            return self._isfailedresponse
        return self._get_server_by_id(self.provider_id)

    def set_provider_id(self, provider_id):
        """设置provider_id"""
        self.provider_id = provider_id
        if provider_id:
            self._last_provider_id = provider_id

    def get_provider_id(self):
        """获取provider_id"""
        return self.provider_id
