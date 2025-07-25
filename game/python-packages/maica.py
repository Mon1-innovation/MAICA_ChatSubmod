# -*- coding: utf-8 -*-

from bot_interface import *
import bot_interface
import emotion_analyze_v2

import websocket
import maica_mtrigger
from maica_mtrigger import MTriggerAction
websocket._logging._logger = logger
websocket._logging.enableTrace(False)
import datetime

def milliseconds_to_hms(timestamp_ms):
    # 将毫秒转换为秒
    timestamp_s = timestamp_ms / 1000.0
    # 创建一个UTC时间戳对应的datetime对象
    dt = datetime.datetime.utcfromtimestamp(timestamp_s)
    return dt.strftime("%H:%M:%S")

class MaicaAi(ChatBotInterface):
    SUPPORT_BACKEND = 1.0011
    ascii_icon = """                                                             

    __  ___ ___     ____ ______ ___ 
   /  |/  //   |   /  _// ____//   |
  / /|_/ // /| |   / / / /    / /| |
 / /  / // ___ | _/ / / /___ / ___ |
/_/  /_//_/  |_|/___/ \____//_/  |_| v
                                    
"""
    class MaicaAiModel:
        maica_main = "maica_main"
        maica_core = "maica_core"
    class MaicaAiLang:
        zh_cn = "zh"
        en = "en"
    class MaicaMSpiretype:
        percise_page = "percise_page"
        fuzzy_page = "fuzzy_page"
        in_percise_category = "in_percise_category"
        in_fuzzy_category = "in_fuzzy_category"
        in_fuzzy_all = "in_fuzzy_all"

    class MaicaAiStatus:
        # 未准备好
        NOT_READY = 10000
        # websocket正在连接
        WEBSOCKET_CONNECTING = 10020
        # 账户信息已准备好，准备令牌验证
        WAIT_AUTH = 10100
        # 等待令牌验证结果
        WAIT_SERVER_TOKEN = 10101
        # 传入令牌
        WAIT_USE_TOKEN = 10102
        # 令牌已传入，session已开启，应该选择模型了
        SESSION_CREATED = 10106
        # 等待模型信息
        WAIT_MODEL_INFOMATION = 10110
        # maica 已准备好，等待玩家输入
        MESSAGE_WAIT_INPUT = 10302
        # ssl证书获取错误, 但使用plain能够连接
        SSL_FAILED_BUT_OKAY = 10322
        # 已输入消息，等待消息发送
        MESSAGE_WAIT_SEND = 10300
        # 发送MSpire请求
        MESSAGE_WAIT_SEND_MSPIRE = 10304
        # 发送MPostal请求
        MESSAGE_WAIT_SEND_MPOSTAL = 10305
        # 已发送消息，等待MAICA回应
        MESSAGE_WAITING_RESPONSE = 10301
        # MAICA 已经输出完毕
        MESSAGE_DONE = 10303

        # 请求重置session
        REQUEST_RESET_SESSION = 11000

        # session已重置，websocket已关闭
        SESSION_RESETED = 12000

        # 请求心跳包
        REQUEST_PING = 11100
        # 发送设置项
        SEND_SETTING = 11200
        # 等待设置结果
        WAIT_SETTING_RESPONSE = 11201
        #############################Submod 错误状态码
        # 疑似网络问题
        # 令牌验证失败
        TOKEN_FAILED = 13400
        # 选择的 model 不正确
        MODEL_NOT_FOUND = 13401
        # wss异常关闭
        WSS_CLOSED_UNEXCEPTED = 13402
        # 玩家数据未找到
        SAVEFILE_NOTFOUND = 13403
        # 网络问题
        CONNECT_PROBLEM = 13404
        # 服务器维护中
        SERVER_MAINTAIN = 13405
        # 错误的输入
        WRONE_INPUT = 13406
        # 证书模块损坏
        CERTIFI_BROKEN = 13407
        # 证书模块损坏, 但是自动修复成功, 需要重启
        CERTIFI_AUTO_FIX = 13408
        # 等待可用性验证
        WAIT_AVAILABILITY = 13409
        # 获取节点失败
        FAILED_GET_NODE = 13410
        # 版本过旧
        VERSION_OLD = 13411
        # 发送内容过长
        TOOLONG_CONTENT_LENGTH = 13412
        # 无网络
        NO_INTERTENT = 13413
        ######################### MAICA 服务器状态码
        MAIKA_PREFIX = 5000
        @classmethod
        def is_1xx(cls, code):
            return 100 <= int(code) - cls.MAIKA_PREFIX <= 199
        
        @classmethod
        def is_submod_exception(cls, code):
            return 13400 <= code <= 13499
        
        # session 已超过 32768token
        TOKEN_MAX_EXCEEDED = MAIKA_PREFIX + 204
        # session > 24000token
        TOKEN_24000_EXCEEDED = MAIKA_PREFIX + 200

        _descriptions = {
            NOT_READY: u"未准备好, 等待配置账户信息",
            WAIT_AVAILABILITY:u"需要验证可用性, 请重启. 若问题仍然存在则检查mas.log",
            WAIT_AUTH: u"账户信息已确认，连接MAICA服务器验证中",
            WAIT_SERVER_TOKEN: u"等待令牌验证结果",
            WAIT_USE_TOKEN: u"等待传入令牌",
            SESSION_CREATED: u"令牌已传入，session已开启，应该选择模型了",
            WAIT_MODEL_INFOMATION: u"等待模型信息",
            MESSAGE_WAIT_INPUT: u"maica 已准备好，等待玩家输入",
            SSL_FAILED_BUT_OKAY: u"maica 未能获取设备根证书, 已回退到无加密模式. 这一般不会影响正常功能",
            MESSAGE_WAIT_SEND: u"已输入消息，等待消息发送",
            MESSAGE_WAITING_RESPONSE: u"已发送消息，等待MAICA回应",
            MESSAGE_WAIT_SEND_MSPIRE: u"等待发送 MSpire 请求",
            MESSAGE_WAIT_SEND_MPOSTAL: u"等待发送 MPostal 请求",
            MESSAGE_DONE: u"MAICA 已经输出完毕",
            REQUEST_RESET_SESSION: u"请求重置 session",
            SESSION_RESETED: u"session 已重置，websocket 已关闭",
            REQUEST_PING: u"请求心跳包",
            TOKEN_FAILED: u"令牌验证失败",
            CONNECT_PROBLEM: u"无法连接服务器, 请检查网络, 查看submod_log以获取详细信息",
            MODEL_NOT_FOUND: u"选择的 model 不正确",
            TOKEN_MAX_EXCEEDED:u"session 已超过 28672 token, 对话已被裁剪",
            TOKEN_24000_EXCEEDED:u"session 已超过 24576 token, 如需要历史记录请及时保存, 对话将很快被裁剪",
            WSS_CLOSED_UNEXCEPTED:u"websocket 异常关闭, 查看submod_log以获取详细信息" if PY2 else u"websocket 异常关闭, 请确认已安装数据包, 查看submod_log以获取详细信息",
            SAVEFILE_NOTFOUND:u"玩家存档未找到, 请确保当前对话会话已经上传存档",
            SERVER_MAINTAIN:u"服务器维护中, 请关注相关通知",
            WRONE_INPUT:u"错误的输入, 请检查输入内容",
            CERTIFI_BROKEN:u"证书模块损坏, 请重新安装MAS",
            CERTIFI_AUTO_FIX:u"证书模块损坏, 已尝试自动修复, 若重启无效请干净安装",
            SEND_SETTING:u"上传设置中",
            FAILED_GET_NODE:u"获取服务节点失败",
            WEBSOCKET_CONNECTING:u"websocket 正在连接（这应该很快）",
            VERSION_OLD:u"子模组版本过旧, 请升级至最新版",
            TOOLONG_CONTENT_LENGTH:u"发送内容过长, 请查看 MTrigger 列表并关闭不需要的触发器",
            NO_INTERTENT:u"子模组未能联网, 根据 Readme 说明检查安装和网络连接",
        }
        @classmethod
        def get_description(cls, code):
            return cls._descriptions.get(code, u"未知状态码: {}".format(code))
            
        
        #@classmethod
        #def add_status_code(cls, name, code, description):
        #    if code in cls._descriptions:
        #        raise ValueError("状态码 {} 已存在，不能重复添加。".format(code))
        #    cls._descriptions[code] = description
        #    setattr(cls, "{}".format(name), code)
    class ExternalLoggingHandler(logging.Handler):
        def __init__(self, maica_console_log_func):
            self.maica_console_log_func = maica_console_log_func
            self.leveling_filter = re.compile(r'^.*?<DISABLE_VERBOSITY>')
            super(MaicaAi.ExternalLoggingHandler, self).__init__()
        def emit(self, record):
            log_message = self.format(record)
            log_message = self.leveling_filter.sub('', log_message, re.I)
            self.maica_console_log_func(log_message)

    class MaicaProviderManager:
        isMaicaNameServer = None
        isfailedresponse = {
            "id": 0,
            "name":"ERROR",
            "deviceName": "Cannot find server",
            "isOfficial": False,
            "portalPage": "https://www.google.com",
            "servingModel": "None",
            "modelLink": "",
            "wsInterface": "wss://maicadev.monika.love/websocket",
            "httpInterface": "https://maicadev.monika.love/api/"
        }
        fakelocalprovider = {
            "id": 9999,
            "name":"Local Deployment",
            "deviceName": "This is your local deployment of MAICA",
            "isOfficial": False,
            "portalPage": "https://github.com/PencilMario/MAICA",
            "servingModel": "None",
            "modelLink": "",
            "wsInterface": "ws://127.0.0.1:5000/",
            "httpInterface": "http://127.0.0.1:6000/",
        }
        servers = []
        provider_list = "https://maicadev.monika.love/api/servers"
        @classmethod
        def get_provider(cls):
            cls.servers = []
            import requests
            res = requests.post(cls.provider_list, json={})
            cls.servers.append(cls.fakelocalprovider)
            if res.status_code != 200:
                logger.error("Cannot get providers because server return non 200: {}".format(res.content))
                cls.servers.append(cls.isfailedresponse)
                #raise Exception("Cannot get providers because server error")
                return False
            res = res.json()
            
            if res["success"]:
                cls.isMaicaNameServer = res["servers"].get("isMaicaNameServer")
                cls.servers = res["servers"].get("servers")
                return True
            else:
                cls.isfailedresponse["deviceName"] = res["exception"]
                cls.servers.append(cls.isfailedresponse)
                logger.error("Cannot get providers because server return: {}".format(res))
                return False
        @classmethod
        def get_server_by_id(cls, id):
            for server in cls.servers:
                if int(server["id"]) == id:
                    return server
            cls.isfailedresponse["deviceName"] = "Cannot find server by id: {}".format(id)
            return cls.isfailedresponse
        @classmethod
        def get_wssurl_by_id(cls, id):
            if not id:
                return cls.isfailedresponse["wsInterface"]
            return cls.get_server_by_id(id)["wsInterface"]

        @classmethod
        def get_api_url_by_id(cls, id):
            if not id:
                return cls.isfailedresponse["httpInterface"]
            return cls.get_server_by_id(id)["httpInterface"]

            
    public_key_pem = """\
-----BEGIN RSA PUBLIC KEY-----
MIIBCgKCAQEA2IHJQAPwWuynuivzvu/97/EbN+ttYoNmJyvu9RC/M9CHXCi1Emgc
/KIluhzfJesBU/E/TX/xeuwURuGcyhIBk0qmba8GOADVjedt1OHcP6DJQJwu6+Bp
kGd8BIqYFHjbsNwkBZiq7s0nRiHig0asd+Hhl/pwplXH/SIjASMlDPijF24OUSfP
+D7eRohyO4sWuj6WTExDq7VoCGz4DBGM3we9wN1YpWMikcb9RdDg+f610MUrzQVf
l3tCkUjgHS+RhNtksuynpwm84Mg1MlbgU5s5alXKmAqQTTJ2IG61PHtrrCTVQA9M
t9vozy56WuHPfv3KZTwrvZaIVSAExEL17wIDAQAB
-----END RSA PUBLIC KEY-----
"""
    def_modelconfig = {
        "top_p":[0.1, 1.0, 0.7],
        "temperature":[0.0, 1.0, 0.4],
        "max_tokens":[0, 2048, None],
        "frequency_penalty":[0.0, 1.0, 0.3],
        "presence_penalty":[0.0, 1.0, 0.0],
        "seed":[0, 99999, None]
    }
    
    MAX_CHATSESSION = 9

    def __init__(self, account, pwd, token = ""):
        """
        初始化函数，用于创建MaicaAI对象
        
        Args:
            account (str): MaicaAI账号
            pwd (str): MaicaAI密码
            token (str, optional): MaicaAI的token，默认为空字符串
        
        Returns:
            None
        """
        import threading
        self.__accessable = False
        self._serving_status = ""
        self.stat = {}
        self.multi_lock = threading.Lock()
        self.MoodStatus = emotion_analyze_v2.EmoSelector(None, None, None)
        self.public_key = None
        self.ciphertext = None
        self.chat_session = 1
        self.wss_session = None
        self.wss_thread = None
        self.user_acc = ""
        self.model = self.MaicaAiModel.maica_core
        self.sf_extraction = False
        self.stream_output = True
        self.update_screen_func = None
        self.content_func = None
        # 待发送消息队列
        self.senddata_queue = Queue() if not PY3 else bot_interface.Queue()
        self.TalkSpilter = bot_interface.TalkSplitV2()
        self._current_topic = ""
        self.status = self.MaicaAiStatus.WAIT_AVAILABILITY
        self.target_lang = self.MaicaAiLang.zh_cn
        self.history_status = None
        self.modelconfig = {}
        self.reset_stat()
        self.auto_reconnect = False
        self.mspire_category = []
        self.mspire_session = 0
        self.mspire_sample = 250
        self.mspire_type = self.MaicaMSpiretype.in_fuzzy_all
        self._gen_time = 0.0
        self.in_mas = True
        self.provider_id = None
        self.is_outdated = None
        self.max_history_token = 28672
        self._in_mspire = False
        self.mspire_use_cache = False
        self.mtrigger_manager = maica_mtrigger.MTriggerManager()
        
        self.__ws_cookie = ""
        self.enable_strict_mode = False
        self.workload_raw = {
            "None":{
                "0": {
                    "name": "Super PP 0",
                    "vram": "100000 MiB",
                    "mean_utilization": 100,
                    "mean_memory": 21811,
                    "mean_consumption": 100
                },                
                "1": {
                    "name": "if you see this, requests workload is failed",
                    "vram": "100000 MiB",
                    "mean_utilization": 0,
                    "mean_memory": 21811,
                    "mean_consumption": 100
                },
            },
            "None2":{
                "0": {
                    "name": "Super PP 2",
                    "vram": "100000 MiB",
                    "mean_utilization": 0,
                    "mean_memory": 21811,
                    "mean_consumption": 100
                },                
                "1": {
                    "name": "Super PP 3",
                    "vram": "100000 MiB",
                    "mean_utilization": 0,
                    "mean_memory": 21811,
                    "mean_consumption": 100
                },
            }
        }
        self.console_logger = logging.getLogger(name="mas_console_logger")
        self.console_logger.setLevel(logging.DEBUG)
        h = self.ExternalLoggingHandler(self.send_to_outside_func)
        h.setFormatter(logging.Formatter("<%(levelname)s>|%(message)s"))
        self.console_logger.addHandler(h)
        class logger_both:
            def __init__(self, flogger):
                self.flogger = flogger
            def info(self, msg):
                logger.info(msg)
                self.flogger.info(msg)
            def error(self, msg):
                logger.error(msg)
                self.flogger.error(msg)
            def warning(self, msg):
                logger.warning(msg)
                self.flogger.warning(msg)
            def debug(self, msg):
                logger.debug(msg)
                self.flogger.debug(msg)
        maica_mtrigger.logger = logger_both(self.console_logger)




    
    def reset_stat(self):
        self.stat = {
            "message_count":0,
            "received_token":0,
            "mspire_count":0,
            "received_token_by_session":[0] * (self.MAX_CHATSESSION+1),
            "mpostal_count":0
        }
    def send_to_outside_func(self, content):
        content = u"{}".format(content)
        import unicodedata
        if self.content_func is None:
            return
        max_len = 33 * 2
        content = content.replace("\"", "").replace("'", "")
        l = content.split("\n")
        def calculate_length(s):
            
            length = 0
            for char in s:
                # 使用unicodedata模块判断字符宽度
                if unicodedata.east_asian_width(char) in ('F', 'W'):
                    length += 2
                else:
                    length += 1
            return length

        def split_string(s, max_len):
            result = []
            current_str = ""
            current_len = 0

            for char in s:
                char_len = 2 if unicodedata.east_asian_width(char) in ('F', 'W') else 1

                if current_len + char_len > max_len:
                    result.append(current_str)
                    current_str = char
                    current_len = char_len
                else:
                    current_str += char
                    current_len += char_len

            if current_str:
                result.append(current_str)

            return result
        def process_lines(l, max_len):
            processed_list = []
            for line in l:
                if calculate_length(line) > max_len:
                    processed_list.extend(split_string(line, max_len))
                else:
                    processed_list.append(line)
            return processed_list
        for i in process_lines(l, max_len):
            if PY2:
                self.content_func(str(key_replace(i.replace("\n", ""), bot_interface.renpy_symbol)).decode())
            elif PY3:
                self.content_func(str(key_replace(i.replace("\n", ""), bot_interface.renpy_symbol)))

    def update_stat(self, new):
        self.stat.update(new)
    def get_message(self, add_pause = True):
        res = self.message_list.get()
        if len(self.message_list) < 1:
            talk = self.TalkSpilter.split_present_sentence()
            if talk:
                talk = self.MoodStatus.analyze(talk)
                emote = self.MoodStatus.get_emote()
                self._append_to_message_list(emote,talk)
        return (res[0], bot_interface.add_pauses(res[1]) if add_pause else res[1])
    def _gen_token(self, account, pwd, token, email = None):
        if token != "":
            self.ciphertext = token
            return
        if not self.__accessable and token == "":
            return logger.error("Maica server not serving.")
        import requests
        data = {
            "username":account,
            "password":pwd
        }
        if email:
            data = {
            "email":email,
            "password":pwd
        }
        try:
            response = requests.post(self.MaicaProviderManager.get_api_url_by_id(self.provider_id) + "register", json=data, timeout=5)
        except Exception as e:
            import traceback
            self.status = self.MaicaAiStatus.CONNECT_PROBLEM
            logger.error("Maica::_gen_token requests.post failed because can't connect to server: {}".format(e))
            return
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success"):
                self.ciphertext = response_data.get("token")
            else:
                self.status = self.MaicaAiStatus.CONNECT_PROBLEM,
                logger.error("Maica::_gen_token response process failed because server response failed: {}".format(response_data))
        else:
            self.status = self.MaicaAiStatus.CONNECT_PROBLEM
            logger.error("Maica::_gen_token response process failed because server return {}".format(response.status_code))
        return
    
    def has_token(self):
        return len(self.ciphertext) > 5

    def _verify_token(self):
        """
        验证token是否有效。
        
        Returns:
            bool: 验证结果。
        
        """
        import requests
        try:
            res = requests.post(self.MaicaProviderManager.get_api_url_by_id(self.provider_id) + "legality", json={"access_token": self.ciphertext})
            if res.status_code == 200:
                res = res.json()
                if res.get("success", False):
                    return res
                else:
                    logger.warning("Maica::_verify_token not passed: {}".format(res))
                    return res
            else:
                logger.error("Maica::_verify_token requests.post failed because can't connect to server: {}".format(res.text))
                return {"success":False, "exception": "Maica::_verify_token requests.post failed"}

        except Exception as e:
            import traceback
            logger.error("Maica::_verify_token requests.post failed because can't connect to server: {}".format(traceback.format_exc()))
            return {"success":False, "exception": "Maica::_verify_token failed"}


    def init_connect(self):
        import threading
        threading.Thread(target=self._init_connect).start()
        

    
    def _init_connect(self):
        if not self.__accessable:
            return logger.error("Maica server not serving.")
        if self.multi_lock.locked():
            return logger.warning("Maica::_init_connect try to create multi connection")
        self.status = self.MaicaAiStatus.WEBSOCKET_CONNECTING
        self.multi_lock.acquire()
        import websocket
        url = self.MaicaProviderManager.get_wssurl_by_id(self.provider_id)
        logger.debug("_init_connect to {}".format(url))
        self.wss_session = websocket.WebSocketApp(url, on_open=self._on_open, on_message=self._on_message, on_error=self._on_error
                                                  , on_close=self._on_close)
        self.wss_session.ping_payload = "PING"
        self.status = self.MaicaAiStatus.WAIT_AUTH
        try:
            self.wss_session.run_forever()
        except Exception as e:
            import traceback
            self.console_logger.error("wss_session.run_forever() failed: {}".format(e))
            logger.error("Maica::_init_connect wss_session.run_forever() failed: {}".format(traceback.format_exc()))
        finally:
            if self.multi_lock.locked():
                self.multi_lock.release()
                logger.info("Maica::_init_connect released lock because wss closed")
        
        
    # 检查参数合法性
    def _check_modelconfig(self):    
        for i in self.def_modelconfig:
            if i in self.modelconfig:
                if not self.def_modelconfig[i][0] <= self.modelconfig[i] <= self.def_modelconfig[i][1]:
                    if self.def_modelconfig[i][2] == None:
                        logger.warning("modelconfig {} is invaild: reset {} -> deleted".format(i, self.modelconfig[i]))
                        self.console_logger.warning("<submod> modelconfig {} is invaild: reset {} -> deleted".format(i, self.modelconfig[i]))
                        del self.modelconfig[i]
                    else:
                        logger.warning("modelconfig {} is invaild: reset  {} -> {}".format(i, self.modelconfig[i], self.def_modelconfig[i][2]))
                        self.console_logger.warning("<submod> modelconfig {} is invaild: reset {} -> {}".format(i, self.modelconfig[i], self.def_modelconfig[i][2]))
                        self.modelconfig[i] = self.def_modelconfig[i][2]
            
    def is_responding(self):
        """返回maica是否正在返回消息"""
        return self.status in (self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE, self.MaicaAiStatus.MESSAGE_WAIT_SEND, self.MaicaAiStatus.MESSAGE_WAIT_SEND_MSPIRE, self.MaicaAiStatus.MESSAGE_WAIT_SEND_MPOSTAL)

    def is_ready_to_input(self):
        """返回maica是否可以接受输入消息了"""
        return self.status in (self.MaicaAiStatus.MESSAGE_WAIT_INPUT, self.MaicaAiStatus.SSL_FAILED_BUT_OKAY, self.MaicaAiStatus.MESSAGE_DONE) and self.is_connected()

    def is_accessable(self):
        """返回maica是否可用"""
        return self.__accessable

    def is_failed(self):
        """返回maica是否处于异常状态"""
        return self.MaicaAiStatus.is_submod_exception(self.status)\
            or not self.is_connected()

    def is_in_exception(self):
        return self.MaicaAiStatus.is_submod_exception(self.status)

    def is_connected(self):
        """返回maica是否连接服务器, 不检查状态码"""
        return self.wss_session.keep_running if self.wss_session else False #\
            #or self.wss_thread.is_alive() if self.wss_thread else False

    def get_status_description(self):
        """返回maica当前状态描述"""
        return self.MaicaAiStatus.get_description(self.status)

    def len_message_queue(self):
        """返回maica已接收并完成分句的台词数"""
        return self.message_list.size()
    
    def start_MSpire(self):
        if not self.__accessable:
            return logger.error("Maica server not serving.")
        if not self.is_ready_to_input():
            return logger.error("Maica is not ready to input")
        self.stat['mspire_count'] += 1
        self.status = self.MaicaAiStatus.MESSAGE_WAIT_SEND_MSPIRE
        self._in_mspire = True
    
    def start_MPostal(self, content, title=""):
        if not self.__accessable:
            return logger.error("Maica server not serving.")
        if not self.is_ready_to_input():
            return logger.error("Maica is not ready to input")
        self.stat['mpostal_count'] += 1
        self.senddata_queue.put(
                {
                    "header": title,
                    "content": key_replace(content, chinese_to_english_punctuation),
                    "bypass_mt": True
                }
            )
        self.status = self.MaicaAiStatus.MESSAGE_WAIT_SEND_MPOSTAL
        #self._in_mspire = True


    def _on_open(self, wsapp):
        import time, threading, random

        def build_setting_config():
            self._check_modelconfig()
            #data = {
            #    "model_params":{},
            #    "perf_params":{},
            #    "super_params":{}
            #}
            #data["model_params"] = {"model":self.model, "sf_extraction":self.sf_extraction, "stream_output":self.stream_output, "target_lang":self.target_lang, "max_token":self.max_history_token, "deformation":True}
            #for param in ['esc_aggressive', 'tnd_aggressive', 'mf_aggressive', 'sfe_aggressive', 'nsfw_acceptive', 'pre_additive', 'post_additive', 'amt_aggressive']:
            #    if param in self.modelconfig:
            #        data['perf_params'][param] = self.modelconfig[param]
            #for param in ['top_p', 'temperature', 'max_tokens', 'frequency_penalty', 'presence_penalty', 'seed']:
            #    if param in self.modelconfig:
            #        data['super_params'][param] = self.modelconfig[param]
            #if self.enable_strict_mode and self.__ws_cookie != "":
            #    data['cookie'] = self.__ws_cookie
            return self.send_settings()
            

        def send_message():
            try:
                import json
                from websocket import WebSocketConnectionClosedException
                from maica_mtrigger import MTriggerMethod
                while True:
                    if not wsapp.keep_running:
                        logger.info("websocket is closed")
                        break
                    time.sleep(1)
                    # 消息已进入队列，等待发送
                    if self.status == self.MaicaAiStatus.MESSAGE_WAIT_SEND:
                        
                        if PY2:
                            message = str(self.senddata_queue.get()).decode().strip()
                        else:
                            message = str(self.senddata_queue.get()).strip()
                        self._current_topic = message
                        dict = {"chat_session":self.chat_session, "query":message, "trigger":self.mtrigger_manager.build_data(MTriggerMethod.request)}
                        if self.enable_strict_mode and self.__ws_cookie != "":
                            dict["cookie"] = self.__ws_cookie
                        message = json.dumps(dict, ensure_ascii=False) 
                        logger.debug("_on_open::self.MaicaAiStatus.MESSAGE_WAIT_SEND: {}".format(message))
                        self.wss_session.send(
                            message
                        )   
                        self.status = self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE
                    elif self.status == self.MaicaAiStatus.MESSAGE_WAIT_SEND_MSPIRE:
                        dict = {
                            "chat_session":self.mspire_session, 
                            "inspire":{
                                    "type":self.mspire_type,
                                    "sample":250,
                                    "title": random.choice(self.mspire_category),
                                } if len(self.mspire_category) else True,
                            "use_cache":self.mspire_use_cache,
                            }
                        self.status = self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE
                        logger.debug("_on_open::self.MaicaAiStatus.MESSAGE_WAIT_SEND_MSPIRE: {}".format(dict))
                        if self.enable_strict_mode and self.__ws_cookie != "":
                            dict["cookie"] = self.__ws_cookie

                        self.wss_session.send(
                            json.dumps(dict, ensure_ascii=False) 
                        )
                    elif self.status == self.MaicaAiStatus.MESSAGE_WAIT_SEND_MPOSTAL:
                        #if PY2:
                        #    message = str(self.senddata_queue.get()).decode().strip()
                        #else:
                        #    message = str(self.senddata_queue.get()).strip()
                        message = self.senddata_queue.get()
                        dict = {"type": "query", "chat_session":0, "postmail":message}
                        if self.enable_strict_mode and self.__ws_cookie != "":
                            dict["cookie"] = self.__ws_cookie
                        message = json.dumps(dict, ensure_ascii=False) 
                        logger.debug("_on_open::self.MaicaAiStatus.MESSAGE_WAIT_SEND_MPOSTAL: {}".format(message))
                        self.wss_session.send(
                            message
                        )   
                        self.status = self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE

                    # 身份验证
                    elif self.status == self.MaicaAiStatus.WAIT_AUTH:
                        self.status = self.MaicaAiStatus.WAIT_SERVER_TOKEN
                        self.wss_session.send(self.ciphertext)
                    # 连接已建立，选择模型
                    elif self.status == self.MaicaAiStatus.SESSION_CREATED:
                        self.send_settings()
                        threading.Thread(target=self.send_mtrigger).start()
                        self.status = self.MaicaAiStatus.WAIT_MODEL_INFOMATION
                    # 要求重置model
                    elif self.status == self.MaicaAiStatus.REQUEST_RESET_SESSION:
                        dict = {"chat_session":self.chat_session, "purge":True}
                        if self.enable_strict_mode and self.__ws_cookie != "":
                            dict["cookie"] = self.__ws_cookie

                        self.wss_session.send(
                            json.dumps(dict)
                        )
                        self.stat["received_token_by_session"][self.chat_session] = 0
                        self.status = self.MaicaAiStatus.SESSION_RESETED
                        self.wss_session.close()
                        break 
                    # 发送设置, 切记仅在闲置时进行 
                    elif self.status == self.MaicaAiStatus.SEND_SETTING:
                        self.wss_session.send(
                            json.dumps(build_setting_config())
                        )
                        self.status = self.MaicaAiStatus.WAIT_SETTING_RESPONSE

            except WebSocketConnectionClosedException as e:
                import traceback
                logger.warning("exception is ocurrred (maybe reconnect to fast, will close wss_session): \n{}".format(traceback.format_exc()))
                self.console_logger.error("!!SUBMOD ERROR when send_message: {}".format(e))
                self.close_wss_session()
                self.multi_lock.release()
            except Exception as e:
                import traceback
                logger.error("exception is ocurrred: \n{}".format(traceback.format_exc()))
                self.console_logger.error("!!SUBMOD ERROR when send_message: {}".format(e))
        self.wss_thread = threading.Thread(target=send_message)
        self.wss_thread.start()
    _pos = 0
    def send_settings(self):
        import json
        def build_setting_config():
            self._check_modelconfig()
            data = {
                "model_params":{},
                "perf_params":{},
                "super_params":{}
            }
            data["model_params"] = {"model":self.model, "sf_extraction":self.sf_extraction, "stream_output":self.stream_output, "target_lang":self.target_lang, "max_token":self.max_history_token, "deformation":True}
            for param in ['esc_aggressive', 'tnd_aggressive', 'mf_aggressive', 'sfe_aggressive', 'nsfw_acceptive', 'pre_additive', 'post_additive', 'amt_aggressive']:
                if param in self.modelconfig:
                    data['perf_params'][param] = self.modelconfig[param]
            for param in ['top_p', 'temperature', 'max_tokens', 'frequency_penalty', 'presence_penalty', 'seed']:
                if param in self.modelconfig:
                    data['super_params'][param] = self.modelconfig[param]
            if self.enable_strict_mode and self.__ws_cookie != "":
                data['cookie'] = self.__ws_cookie
            return data
        data = build_setting_config()
        if self.is_connected():
            logger.debug("send_settings: {}".format(json.dumps(build_setting_config())))
            self.wss_session.send(
                json.dumps(build_setting_config())
            )
            return data
        else:
            logger.warning("You should connected to send settings")
            return {}
    def _on_message(self, wsapp, message):
        try:
            self.__on_message(wsapp, message)
        except Exception as e:
            import traceback
            self.console_logger.debug("!!SUBMOD ERROR when on_message: {}".format(e))
            logger.error("exception is ocurrred: \n{}".format(traceback.format_exc()))
            logger.error("when processing context: {}".format(message))
    def __on_message(self, wsapp, message):
        import json, time
        data = json.loads(message)
        if data.get("status", "unknown") in ('ws_cookie'):
            logger.debug("_on_message: S{} received '{}'/'{}'[{}]: {}".format(
                (milliseconds_to_hms(data["time_ms"]))  + "." + str(data["time_ms"] % 1000).zfill(3)if "time_ms" in data else "unknown server timestamp",
                data["status"] if "status" in data else "unknown status",
                data["type"] if "type" in data else "unknown type",
                data["code"] if "code" in data else "unknown code",
                "--content filtered--"
            ))    
        else:
            logger.debug("_on_message: S{} received '{}'/'{}'[{}]: {}".format(
                (milliseconds_to_hms(data["time_ms"]))  + "." + str(data["time_ms"] % 1000).zfill(3)if "time_ms" in data else "unknown server timestamp",
                data["status"] if "status" in data else "unknown status",
                data["type"] if "type" in data else "unknown type",
                data["code"] if "code" in data else "unknown code",
                data["content"] if "content" in data else "unknown content"
            ))    
        if data.get("type", False) != "carriage":
            if data.get("type", "unknown") == "info":
                self.console_logger.info("<{}> {}".format(data.get("status", "Status"), data.get("content", "Error: Data frame is received but content is empty")))
            else:
                self.console_logger.debug("<{}> {}".format(data.get("status", "Status"), data.get("content", "Error: Data frame is received but content is empty")))

        if 400 <= int(data.get("code", 200)) < 500:
            self.console_logger.error("!!MAICA RESPONSE ERROR: {}-{}".format(data.get("status", "4xxStatus"), data.get("content", "Error: Code 4xx is received but content is empty")))
            self.status = self.MaicaAiStatus.WSS_CLOSED_UNEXCEPTED
            self.wss_session.close()
        if 500 <= int(data.get("code", 200)) < 600:
            self.console_logger.error("!!MAICA SERVER FATAL: {}-{}".format(data.get("status", "5xxStatus"), data.get("content", "Error: Code 5xx is received but content is empty")))
            self.status = self.MaicaAiStatus.WSS_CLOSED_UNEXCEPTED
            self.wss_session.close()
        if data["status"] == "delete_hint":
            self.history_status = self.MaicaAiStatus.TOKEN_24000_EXCEEDED
        elif data["status"] == "delete":
            self.history_status = self.MaicaAiStatus.TOKEN_MAX_EXCEEDED 
        # 错误code处理
        if data.get("status") == "wrong_input":
            self.console_logger.error("!!SUBMOD ERROR: {}".format("Wrong input, maybe you should check your setting"))
            self.status = self.MaicaAiStatus.WRONE_INPUT
            self.wss_session.close()
        elif data.get("status") == "unauthorized":
            self.console_logger.error("!!SUBMOD ERROR: {}".format("May be wrong password"))
            self.status = self.MaicaAiStatus.TOKEN_FAILED
            self.wss_session.close()
        elif data.get("status") == "length_exceeded":
            self.console_logger.error("!!SUBMOD ERROR: {}".format("Content too long!"))
            self.status = self.MaicaAiStatus.TOOLONG_CONTENT_LENGTH
            self.wss_session.close()
        if data["status"] == "nickname":
            self.user_acc = data["content"]
            logger.info("maica: Login as '{}'".format(self.user_acc))
        if data['status'] == "mtrigger_trigger":
            param = data['content'][1]
            self.mtrigger_manager.triggered(data['content'][0], data['content'][1] if len(data['content']) >= 2 else None)
            self.mtrigger_manager.run_trigger(MTriggerAction.instant)
        if data['status'] == "ws_cookie":
            self.__ws_cookie = data['content']
        
        ## data处理：
        ## 当MESSAGE_WAITING_RESPONSE时, 如果收到ping, 证明服务端已发送streaming_done但是我们没收到
        ## 直接将data.status改写为streaming_done
        #if self.status == self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE and data['status'] == "ping_reaction":
        #    data['status'] = "streaming_done"
        #    data['content'] = "streaming_done losted!"
        #    logger.warning("streaming_done likely losted")
        #    self.send_to_outside_func("!!SUBMOD WARN: streaming_done maybe losted")

        # 发送令牌，等待回应
        if self.status == self.MaicaAiStatus.WAIT_SERVER_TOKEN:
            if data['status'] == "thread_ready":
                self.status = self.MaicaAiStatus.SESSION_CREATED            
        elif self.status in (self.MaicaAiStatus.WAIT_MODEL_INFOMATION, self.MaicaAiStatus.WAIT_SETTING_RESPONSE):
            if not data['status'] in ("ok", "thread_ready", "params_set"):
                self.status = self.MaicaAiStatus.MODEL_NOT_FOUND
            else:# data['status'] == "thread_ready":
                self.status = self.MaicaAiStatus.MESSAGE_WAIT_INPUT
        elif self.status == self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE:
            self._gen_time = time.time()
            if data['status'] == "continue":
                self.stat["received_token"] += 1
                self.stat["received_token_by_session"][self.chat_session if not self._in_mspire else self.mspire_session] += 1
                self.TalkSpilter.add_part(data['content'])
                if len(self.message_list) == 0:
                    res = self.TalkSpilter.split_present_sentence()
                    if res:
                        res = self.MoodStatus.analyze(res)
                        emote = self.MoodStatus.get_emote()
                        self._append_to_message_list(emote,res)
            if data['status'] == "reply": # MPostal
                 self._append_to_message_list('1eua', self.MoodStatus.analyze(data['content']))
            if data['status'] == "savefile_notfound":
                self.status = self.MaicaAiStatus.SAVEFILE_NOTFOUND
                self.console_logger.error("!!SUBMOD ERROR:savefile not found, please check your savefile is uploaded")
                self.wss_session.close()
            if data['status'] == "loop_finished":
                self._in_mspire = False
                talks = self.TalkSpilter.announce_stop()
                for item in talks:
                    t = self.MoodStatus.analyze(item)
                    emote = self.MoodStatus.get_emote()
                    self._append_to_message_list(emote,t)
                self.status = self.MaicaAiStatus.MESSAGE_DONE
                self.MoodStatus.reset()
                
        if self.update_screen_func:
            self.update_screen_func(0)
    def _on_error(self, wsapp, error):
        logger.error("MaicaAi::_on_error {}".format(error))
        self.status = self.MaicaAiStatus.WSS_CLOSED_UNEXCEPTED
        self.close_wss_session()

    def _on_close(self, wsapp, close_status_code=None, close_msg=None):
        logger.debug("MaicaAi::_on_close {}|{}".format(close_status_code, close_msg))
        self.__ws_cookie = ""
        if self.multi_lock.locked():
            self.multi_lock.release()
        raise Exception("Websocket closed, raising to cleanup")

        
    def chat(self, message):
        if not self.__accessable:
            return logger.error("Maica is not serving")
        if not self.is_ready_to_input():
            return logger.error("Maica is not ready to input")
        message = str(message)
        self.senddata_queue.clear()
        self.senddata_queue.put(key_replace(message, chinese_to_english_punctuation))
        self.stat['message_count'] += 1
        self.status = self.MaicaAiStatus.MESSAGE_WAIT_SEND

    def _append_to_message_list(self, emote, message):
        if len(message) == 0:
            return
        elif message[0] == " ":
            message = message[1:]
        message_step1 = key_replace(str(message), bot_interface.renpy_symbol_big_bracket_only, bot_interface.renpy_symbol_percentage, bot_interface.renpy_symbol_enter)
        self.message_list.put((emote, message_step1))
    def upload_save(self, dict):
        """
        向Maica服务上传并保存存档数据。
        
        Args:
            dict (dict): 要上传的数据，必须为字典类型。
            session (int, optional): 会话ID。默认为1。
        
        Returns:
            dict: 如果上传成功，则返回Maica服务返回的JSON响应；否则返回空字典。
        
        """

        if not self.__accessable:
            logger.error("upload_save::Maica is not serving")
            return {}
        if self.ciphertext in ("", None):
            logger.error("upload_save:: token is null")
            return {}
        import requests, json
        content = json.dumps(
                {
                    "access_token": self.ciphertext,
                    "chat_session": self.chat_session,
                    "content": dict
                }
            )
        res = requests.post(
            self.MaicaProviderManager.get_api_url_by_id(self.provider_id) + "savefile",
            data = content
        )
        if res.status_code == 200:
            return res.json()
        else:
            logger.error("upload_save:: return non http 200:: {}".format(res.text))
            return {}

    def get_history(self, lines = 0):
        """
        获取与Maica的历史聊天记录
        
        Args:
            lines (int, optional): 需要获取的聊天记录条数
                当lines为正整数n时, 接口只返回对话历史的前n项, 应注意其中第一项为最后一次生效的system字段.
                当lines为负整数-n时, 接口只返回对话历史的后n项, 此时返回的对话历史仍然以正序排列.
                当lines为0时, 接口返回全部对话历史--可能会很长.
        
        Returns:
            dict: 包含历史聊天记录的字典。
        
        Raises:
            无
        
        """
        
        if not self.__accessable:
            return logger.error("Maica is not serving")
        import requests, json
        res = requests.post(
            self.MaicaProviderManager.get_api_url_by_id(self.provider_id) + "history",
            data = json.dumps(
                {
                    "access_token": self.ciphertext,
                    "chat_session": self.chat_session,
                    "rounds": lines
                },
            )
        )
        return res.json()
    def upload_history(self, history):
        """
        将历史记录上传到Maica服务器
        
        Args:
            history (dict): 
        
        Returns:
            bool: True表示成功，False表示失败
        
        """

        if not self.__accessable:
            return logger.error("Maica is not serving")
        import requests, json
        res = requests.post(
            self.MaicaProviderManager.get_api_url_by_id(self.provider_id) + "restore",
            data = json.dumps(
                {
                    "access_token": self.ciphertext,
                    "chat_session": self.chat_session,
                    "history": history
                },
            )
        )
        return res.json()
        
    def reset_chat_session(self):
        """
        重置当前聊天会话。
        
        Args:
            无。
        
        Returns:
            无返回值。
        
        Raises:
            无。
        
        """

        if not self.__accessable:
            return logger.error("Maica is not serving")
        import json
        self.status = self.MaicaAiStatus.REQUEST_RESET_SESSION
        dict = {"chat_session":self.chat_session, "purge":True}
        if self.enable_strict_mode and self.__ws_cookie != "":
            dict["cookie"] = self.__ws_cookie
        self.wss_session.send(
            json.dumps(dict)
        )
        self.stat["received_token_by_session"][self.chat_session] = 0
        self.status = self.MaicaAiStatus.SESSION_RESETED
        self.history_status = None
        self.wss_session.close()

    def update_workload(self):
        """
        更新工作负载信息（后台执行）。

        Args:
            无。

        Returns:
            threading.Thread对象，可以用于检查线程的状态。
        """
        import requests
        import threading
        if not self.__accessable:
            logger.error("Maica is not serving")
            return None

        def task():
            res = requests.post(self.MaicaProviderManager.get_api_url_by_id(self.provider_id) + "workload")
            if res.status_code == 200:
                data = res.json()
                if data["success"]:
                    self.workload_raw = data["workload"]
                logger.debug("Workload updated successfully.")
            else:
                logger.error("Failed to update workload.")

        thread = threading.Thread(target=task)
        thread.daemon = True  # Optional: allow the program to exit even if the thread is running
        thread.start()
        return thread

    def get_workload_lite(self):
        """
        获取最高负载设备的占用
        
        Args:
            无。
        
        Returns:
            工作负载信息简化版。
        
        """

        data = {
            "avg_usage": 0,
            "max_usage": 0,
            "total_vmem": 0,
            "total_inuse_vmem": 0,
            "total_w": 0,
            "mem_pencent":0
        }
        if not self.__accessable:
            return data
    # Use iteritems() for Python 2
        avgcount = 0
        if PY2:
            for group in self.workload_raw.itervalues():
                for card in group.itervalues():
                    if card["mean_utilization"] > data["max_usage"]:
                        data["max_usage"] = card["mean_utilization"]
                    data["avg_usage"] += card["mean_utilization"]
                    avgcount+=1
                    data["total_vmem"] += int(card["vram"][:-4].strip())
                    data["total_inuse_vmem"] += card["mean_memory"]
                    data["total_w"] += card["mean_consumption"]
        elif PY3:
            for group in self.workload_raw.values():
                for card in group.values():
                    if card["mean_utilization"] > data["max_usage"]:
                        data["max_usage"] = card["mean_utilization"]
                    data["avg_usage"] += card["mean_utilization"]
                    avgcount+=1
                    data["total_vmem"] += int(card["vram"][:-4].strip())
                    data["total_inuse_vmem"] += card["mean_memory"]
                    data["total_w"] += card["mean_consumption"]
        if avgcount > 0:
            data["avg_usage"] /= avgcount
        return data

    

    def close_wss_session(self):
        """
        关闭WebSocket会话。
        
        Args:
            无参数。
        
        Returns:
            无返回值。
        
        """

        if self.wss_session:
            self.wss_session.close()
    
    def send_mtrigger(self):
        try:
            from maica_mtrigger import MTriggerMethod
            res = self.mtrigger_manager.send_to_table(self.ciphertext, self.chat_session, self.mtrigger_manager.build_data(MTriggerMethod.table))
            if res.json().get('success', False):
                logger.debug("send_mtrigger success")

            else:
                logger.error("send_mtrigger failed: {}".format(res.json()))

        except:
            import traceback
            logger.error("send_mtrigger error: {}".format(traceback.format_exc()))



    def ping(self, host, port=80, timeout=2):
        """通过 TCP 连接检测主机可达性，成功返回 True，否则返回 False"""
        import socket
        try:
            socket.create_connection((host, port), timeout=timeout).close()
            return True
        except:
            return False

    def can_access_internet(self):
        """
        Check if either Baidu or Google is reachable.
        Returns True if at least one is reachable, False otherwise.
        """
        baidu_reachable = self.ping("www.baidu.com")
        google_reachable = self.ping("www.google.com")
        
        return baidu_reachable or google_reachable
    def accessable(self):
        """
        检查Maica服务是否可访问
        注意, 在开始使用前, 必须先使用该函数来检查MAICA服务器是否可用
        
        Args:
            无
        
        Returns:
            无返回值，该函数主要用于更新类的状态
        
        Raises:
            无
        """
        #self.__accessable = True
        #self.status = self.MaicaAiStatus.NOT_READY
        #return
        if not self.can_access_internet():
            self.status = self.MaicaAiStatus.NO_INTERTENT
            logger.error("accessable(): no internet connection")
            self.__accessable = False
            return
        if self.status == self.MaicaAiStatus.CERTIFI_AUTO_FIX:
            logger.error("accessable(): certifi auto fix, need restart")
            self.__accessable = False
            return
        try:
            if not self.MaicaProviderManager.get_provider():
                if self.provider_id != 9999:
                    self.status = self.MaicaAiStatus.FAILED_GET_NODE
                    self.__accessable = False
                    return

        except Exception as e:
            logger.error("accessable(): Maica get Service Provider Error: {}".format(e))
            if self.provider_id != 9999:
                self.status = self.MaicaAiStatus.FAILED_GET_NODE
                self.__accessable = False
                return

        if self.in_mas:
            try:
                import certifi
                certifi.set_parent_dir
            except AttributeError:
                logger.error("accessable(): certifi is broken")
                self.status = self.MaicaAiStatus.CERTIFI_BROKEN
                self.__accessable = False
                return
                
        import requests, json
        res = requests.post(self.MaicaProviderManager.get_api_url_by_id(self.provider_id) + "accessibility")
        d = res.json()
        if d.get(u"success", False):
            self._serving_status = d["accessibility"]
            if d.get("accessibility", None) != "serving":
                self.status = self.MaicaAiStatus.SERVER_MAINTAIN
                self.__accessable = False
                logger.error("accessable(): Maica is not serving: {}".format(d["accessibility"]))
            else:
                self.__accessable = True
                self.status = self.MaicaAiStatus.NOT_READY
        else:
            self.status = self.MaicaAiStatus.SERVER_MAINTAIN
            self.__accessable = False
            logger.error("accessable(): Maica is not serving: {}".format(d["accessibility"]))
        


    def disable(self, status_code = MaicaAiStatus.CONNECT_PROBLEM):
        self.status = status_code
        self.__accessable = False



            

        


