# -*- coding: utf-8 -*-

from bot_interface import *
import bot_interface
import emotion_analyze_v2

import websocket
websocket._logging._logger = logger
websocket._logging.enableTrace(False)


class MaicaAi(ChatBotInterface):
    ascii_icon = """                                                             

    __  ___ ___     ____ ______ ___ 
   /  |/  //   |   /  _// ____//   |
  / /|_/ // /| |   / / / /    / /| |
 / /  / // ___ | _/ / / /___ / ___ |
/_/  /_//_/  |_|/___/ \____//_/  |_|
                                    
"""
    class MaicaAiModel:
        maica_main = "maica_main"
        maica_core = "maica_core"
    
    class MaicaAiLang:
        zh_cn = "zh"
        en = "en"
    class MaicaAiStatus:
        # 未准备好
        NOT_READY = 10000
        # 等待可用性验证
        WAIT_AVAILABILITY = 10001
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
        # 已输入消息，等待消息发送
        MESSAGE_WAIT_SEND = 10300
        # 发送MSpire请求
        MESSAGE_WAIT_SEND_MSPIRE = 10304
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
            WAIT_AVAILABILITY:u"需要验证可用性, 请执行MaicaAi.accessable()",
            WAIT_AUTH: u"账户信息已确认，连接MAICA服务器验证中",
            WAIT_SERVER_TOKEN: u"等待令牌验证结果",
            WAIT_USE_TOKEN: u"等待传入令牌",
            SESSION_CREATED: u"令牌已传入，session已开启，应该选择模型了",
            WAIT_MODEL_INFOMATION: u"等待模型信息",
            MESSAGE_WAIT_INPUT: u"maica 已准备好，等待玩家输入",
            MESSAGE_WAIT_SEND: u"已输入消息，等待消息发送",
            MESSAGE_WAITING_RESPONSE: u"已发送消息，等待MAICA回应",
            MESSAGE_WAIT_SEND_MSPIRE: u"等待发送MSpire请求",
            MESSAGE_DONE: u"MAICA 已经输出完毕",
            REQUEST_RESET_SESSION: u"请求重置session",
            SESSION_RESETED: u"session已重置，websocket已关闭",
            REQUEST_PING: u"请求心跳包",
            TOKEN_FAILED: u"令牌验证失败",
            CONNECT_PROBLEM: u"无法连接服务器, 请检查本地网络问题, 查看submod_log以获取详细信息",
            MODEL_NOT_FOUND: u"选择的 model 不正确",
            TOKEN_MAX_EXCEEDED:u"session 已超过 28672 token, 可能有部分对话已被删除",
            TOKEN_24000_EXCEEDED:u"session 已超过 24576 token, 如需要历史记录请及时保存, 对话可能已删除过",
            WSS_CLOSED_UNEXCEPTED:u"websocket异常关闭, 查看submod_log以获取详细信息",
            SAVEFILE_NOTFOUND:u"玩家存档未找到, 请确保当前对话会话已经上传存档",
            SERVER_MAINTAIN:u"服务器维护中, 请关注相关通知",
            WRONE_INPUT:u"错误的输入, 请检查输入内容",
            CERTIFI_BROKEN:u"证书模块损坏, 请重新安装MAS",
            CERTIFI_AUTO_FIX:u"证书模块损坏, 但是自动修复成功, 需要重启MAS",
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

    
    url = "wss://maicadev.monika.love/websocket"
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
        "max_tokens":[0, 1024, None],
        "frequency_penalty":[0.0, 1.0, 0.3],
        "presence_penalty":[0.0, 1.0, 0.0],
        "seed":[0, 999, None]
    }
    
    MAX_CHATSESSION = 9

    def __init__(self, account, pwd, token = ""):
        import threading
        self.__accessable = False
        self._serving_status = ""
        self.stat = {}
        self.multi_lock = threading.RLock()
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
        self._received = ""
        self._current_topic = ""
        self.status = self.MaicaAiStatus.WAIT_AVAILABILITY
        self.target_lang = self.MaicaAiLang.zh_cn
        self.history_status = None
        self.modelconfig = {}
        self.reset_stat()
        self.auto_reconnect = False
        self.mspire_category = ["视觉小说", "恋爱冒险游戏"]
        self.mspire_session = 0
        self._gen_time = 0.0
        self.in_mas = True


    def reset_stat(self):
        self.stat = {
            "message_count":0,
            "received_token":0,
            "mspire_count":0,
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
            self.content_func(key_replace(i.replace("\n", ""), bot_interface.renpy_symbol).decode())
    def update_stat(self, new):
        self.stat.update(new)
    def get_message(self):
        return self.message_list.get()
    def _gen_token(self, account, pwd, token, email = None):
        if token != "":
            self.ciphertext = token
            return
        if PY2:
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
                response = requests.post("https://maicadev.monika.love/api/register", json=data)
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
        if PY3:
            import json, base64
            from Crypto.Cipher import PKCS1_OAEP
            from Crypto.PublicKey import RSA
            self.public_key = RSA.import_key(self.public_key_pem)
            cipher = PKCS1_OAEP.new(self.public_key)
            # 加密
            data = {
                "username":account,
                "password":pwd
            }
            message = json.dumps(data, ensure_ascii=False).encode('utf-8')
            print(message)
            self.ciphertext = base64.b64encode(cipher.encrypt(message)).decode('utf-8')
            

    def init_connect(self):
        import threading
        threading.Thread(target=self._init_connect).start()

    def _init_connect(self):
        if not self.__accessable:
            return logger.error("Maica server not serving.")
        logger.debug("_init_connect")
        if not self.multi_lock.acquire(blocking=False):
            return logger.warning("Maica::_init_connect try to create multi connection")
        import websocket
        self.wss_session = websocket.WebSocketApp(self.url, on_open=self._on_open, on_message=self._on_message, on_error=self._on_error
                                                  , on_close=self._on_close)
        self.wss_session.ping_payload = "PING"
        self.status = self.MaicaAiStatus.WAIT_AUTH
        try:
            self.wss_session.run_forever()
        except Exception as e:
            import traceback
            self.send_to_outside_func("wss_session.run_forever() failed: {}".format(e))
            logger.error("Maica::_init_connect wss_session.run_forever() failed: {}".format(traceback.format_exc()))
        finally:
            self.multi_lock.release()
            logger.info("Maica::_init_connect released lock")
        
        
    # 检查参数合法性
    def _check_modelconfig(self):    
        for i in self.def_modelconfig:
            if i in self.modelconfig:
                if not self.def_modelconfig[i][0] <= self.modelconfig[i] <= self.def_modelconfig[i][1]:
                    if self.def_modelconfig[i][2] == None:
                        logger.warning("modelconfig {} is invaild: reset {} -> deleted".format(i, self.modelconfig[i]))
                        self.send_to_outside_func("<submod> modelconfig {} is invaild: reset {} -> deleted".format(i, self.modelconfig[i]))
                        del self.modelconfig[i]
                    else:
                        logger.warning("modelconfig {} is invaild: reset  {} -> {}".format(i, self.modelconfig[i], self.def_modelconfig[i][2]))
                        self.send_to_outside_func("<submod> modelconfig {} is invaild: reset {} -> {}".format(i, self.modelconfig[i], self.def_modelconfig[i][2]))
                        self.modelconfig[i] = self.def_modelconfig[i][2]
            
    def is_responding(self):
        """返回maica是否正在返回消息"""
        return self.status in (self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE, self.MaicaAiStatus.MESSAGE_WAIT_SEND, self.MaicaAiStatus.MESSAGE_WAIT_SEND_MSPIRE)

    def is_ready_to_input(self):
        """返回maica是否可以发送消息了"""
        return self.status in (self.MaicaAiStatus.MESSAGE_WAIT_INPUT, self.MaicaAiStatus.MESSAGE_DONE)

    def is_failed(self):
        """返回maica是否处于异常状态"""
        return self.MaicaAiStatus.is_submod_exception(self.status)\
            or not self.is_connected()

    def is_connected(self):
        """返回maica是否连接服务器, 不检查状态码"""
        return self.wss_session.keep_running if self.wss_session else False \
            and self.wss_thread.is_alive() if self.wss_thread else False

    def len_message_queue(self):
        """返回maica已接收并完成分句的台词数"""
        return self.message_list.size()
    
    def start_MSpire(self):
        if not self.__accessable:
            return logger.error("Maica server not serving.")
        self.stat['mspire_count'] += 1
        self.status = self.MaicaAiStatus.MESSAGE_WAIT_SEND_MSPIRE
    def _on_open(self, wsapp):
        logger.info("_on_open")
        import time, threading, random
        def send_message():
            try:
                import json
                while True:
                    if self.wss_session.keep_running == False:
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
                        dict = {"chat_session":self.chat_session, "query":message}
                        self._check_modelconfig()
                        dict.update(self.modelconfig)
                        logger.debug(dict)
                        message = json.dumps(dict, ensure_ascii=False) 
                        #print(f"_on_open::self.MaicaAiStatus.MESSAGE_WAIT_SEND: {message}")
                        self.wss_session.send(
                            message
                        )   
                        self.status = self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE
                    elif self.status == self.MaicaAiStatus.MESSAGE_WAIT_SEND_MSPIRE:
                        dict = {"chat_session":self.mspire_session, "inspire":True if len(self.mspire_category) == 0 else self.mspire_category[random.randint(0, len(self.mspire_category)-1)]}
                        logger.debug(dict)
                        self._check_modelconfig()
                        dict.update(self.modelconfig)
                        self.status = self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE
                        self.wss_session.send(
                            json.dumps(dict, ensure_ascii=False) 
                        )

                    # 身份验证
                    elif self.status == self.MaicaAiStatus.WAIT_AUTH:
                        self.status = self.MaicaAiStatus.WAIT_SERVER_TOKEN
                        self.wss_session.send(self.ciphertext)
                        logger.info(self.status)
                    # 连接已建立，选择模型
                    elif self.status == self.MaicaAiStatus.SESSION_CREATED:
                        self.wss_session.send(
                            json.dumps({"model":self.model, "sf_extraction":self.sf_extraction, "stream_output":self.stream_output, "target_lang":self.target_lang})
                        )
                        self.status = self.MaicaAiStatus.WAIT_MODEL_INFOMATION
                    # 要求重置model
                    elif self.status == self.MaicaAiStatus.REQUEST_RESET_SESSION:
                        self.wss_session.send(
                            json.dumps({"chat_session":self.chat_session, "purge":True})
                        )
                        self.status = self.MaicaAiStatus.SESSION_RESETED
                        self.wss_session.close()
                        break
            except Exception as e:
                import traceback
                logger.error("exception is ocurrred: \n{}".format(traceback.format_exc()))
                self.send_to_outside_func("!!SUBMOD ERROR when send_message: {}".format(e))
        self.wss_thread = threading.Thread(target=send_message)
        self.wss_thread.start()
    _pos = 0
    def _on_message(self, wsapp, message):
        try:
            self.__on_message(wsapp, message)
        except Exception as e:
            import traceback
            self.send_to_outside_func("!!SUBMOD ERROR when on_message: {}".format(e))
            logger.error("exception is ocurrred: \n{}".format(traceback.format_exc()))
    def __on_message(self, wsapp, message):
        import json, time
        data = json.loads(message)
        logger.debug("_on_message: {}".format(data))    
        if data.get("type", False) != "carriage":
            self.send_to_outside_func("<{}> {}".format(data.get("status", "Status"), data.get("content", "Error: Data frame is received but content is empty")))
        if 500 <= int(data.get("code", 200)) < 600:
            self.send_to_outside_func("!!MAICA SERVER ERROR: {}-{}".format(data.get("status", "5xxStatus"), data.get("content", "Error: Code 5xx is received but content is empty")))
            self.status = self.MaicaAiStatus.WSS_CLOSED_UNEXCEPTED
            self.wss_session.close()
        logger.debug("data.status in process: {}".format(data["status"] in ("delete_hint", "delete", "session_created", "nickname", "ok", "continue", "streaming_done")))
        # 到达上限状态接收
        if data["status"] == "delete_hint":
            self.history_status = self.MaicaAiStatus.TOKEN_24000_EXCEEDED
        elif data["status"] == "delete":
            self.history_status = self.MaicaAiStatus.TOKEN_MAX_EXCEEDED 
        # 错误code处理
        if data.get("status") == "wrong_input":
            self.send_to_outside_func("!!SUBMOD ERROR: {}".format("Wrong input, maybe you should check your setting"))
            self.wss_session.close()
            self.status = self.MaicaAiStatus.WRONE_INPUT
            
        # 发送令牌，等待回应
        if self.status == self.MaicaAiStatus.WAIT_SERVER_TOKEN:
            if data['status'] != "session_created":
                self.status = self.MaicaAiStatus.TOKEN_FAILED
                self.wss_session.close()
            else:
                self.status = self.MaicaAiStatus.SESSION_CREATED
        if self.status == self.MaicaAiStatus.SESSION_CREATED:
            if data["status"] == "nickname":
                self.user_acc = data["content"]
                logger.info("以身份 {} 登录".format(self.user_acc))
        elif self.status == self.MaicaAiStatus.WAIT_MODEL_INFOMATION:
            if data['status'] != "ok":
                self.status = self.MaicaAiStatus.MODEL_NOT_FOUND
            else:
                self.status = self.MaicaAiStatus.MESSAGE_WAIT_INPUT
        elif self.status == self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE:
            logger.debug("MESSAGE_WAITING_RESPONSE:: status in process: {}".format(data["status"] in ("continue", "streaming_done")))
            if data['status'] == "continue":
                self.stat["received_token"] += 1
                self._received = self._received + data['content']
                if re.match(r"[0-9]\s*\.\s*$", self._received[self._pos:]):
                    isnum = 0
                else:
                    isnum = is_a_talk(self._received[self._pos:])
                logger.debug("MESSAGE_WAITING_RESPONSE:: isnum: {}".format(isnum))
                if isnum:
                    raw_message = self._received[self._pos:self._pos + isnum]
                    res = self.MoodStatus.analyze(raw_message)
                    logger.debug("MESSAGE_WAITING_RESPONSE::res: {}".format(res))
                    emote = self.MoodStatus.get_emote()
                    logger.debug("MESSAGE_WAITING_RESPONSE::emote: {}".format(emote))
                    logger.debug("MESSAGE_WAITING_RESPONSE::MoodStatus: pre_mood:{} strength:m{:.2f}/r{:.2f}".format(self.MoodStatus.pre_mood, self.MoodStatus.main_strength, self.MoodStatus.repeat_strength))
                    self.send_to_outside_func("<submod> MoodStatus: pre_mood:{} strength:m{:.2f}/r{:.2f}".format(self.MoodStatus.pre_mood, self.MoodStatus.main_strength, self.MoodStatus.repeat_strength))

                    self._append_to_message_list(emote, res.strip())
                    logger.debug("Server:{}".format(self._received[self._pos:self._pos + isnum]))
                    self._pos = self._pos + isnum
            if data['status'] == "savefile_notfound":
                self.status = self.MaicaAiStatus.SAVEFILE_NOTFOUND
                self.send_to_outside_func("!!SUBMOD ERROR:savefile not found, please check your savefile is uploaded")
                self.wss_session.close()
            if data['status'] == "streaming_done":
                if "not is_a_talk(self._received[self._pos:])" and len(self._received)- 1 - self._pos > 2:
                    raw_message = self._received[self._pos:]
                    res = self.MoodStatus.analyze(raw_message)
                    logger.debug("MESSAGE_WAITING_RESPONSE::res: {}".format(res))
                    emote = self.MoodStatus.get_emote()
                    logger.debug("MESSAGE_WAITING_RESPONSE::emote: {}".format(emote))
                    self.send_to_outside_func("<submod> MoodStatus: pre_mood:{} strength:m{}/r{}".format(self.MoodStatus.pre_mood, self.MoodStatus.main_strength, self.MoodStatus.repeat_strength))
                    self._append_to_message_list(emote, res.strip())
                    logger.debug("Server: {}".format(self._received[self._pos:]))
                logger.debug("User input: {}".format(self._current_topic))
                logger.debug("Responsed message: {}".format(self._received))
                self._pos = 0
                self._received = ""
                self.status = self.MaicaAiStatus.MESSAGE_DONE
                self.MoodStatus.reset()
                self._gen_time = time.time()
        if self.update_screen_func:
            self.update_screen_func(0)
    def _on_error(self, wsapp, error):
        logger.error("MaicaAi::_on_error {}".format(error))
        self.status = self.MaicaAiStatus.WSS_CLOSED_UNEXCEPTED
        self.close_wss_session()

    def _on_close(self, wsapp, close_status_code=None, close_msg=None):
        if close_status_code or close_msg:
            logger.info("MaicaAi::_on_close {}|{}".format(close_status_code, close_msg))
        
    def chat(self, message):
        #if not self.status in (self.MaicaAiStatus.MESSAGE_WAIT_INPUT, self.MaicaAiStatus.MESSAGE_DONE):
        #    raise RuntimeError("Maica not ready to chat")
        if not self.__accessable:
            return logger.error("Maica is not serving")
        message = str(message)
        self.senddata_queue.clear()
        self.senddata_queue.put(key_replace(message, chinese_to_english_punctuation))
        self.stat['message_count'] += 1
        self.status = self.MaicaAiStatus.MESSAGE_WAIT_SEND

    def _append_to_message_list(self, emote, message):
        self.message_list.put((emote, key_replace(str(message), bot_interface.renpy_symbol_big_bracket_only)))
    def upload_save(self, dict, session=1):
        if not self.__accessable:
            return logger.error("Maica is not serving")
        import requests, json
        res = requests.post(
            "https://maicadev.monika.love/api/savefile",
            data = json.dumps(
                {
                    "access_token": self.ciphertext,
                    "chat_session": session,
                    "content": dict
                },
            )
        )
        return res.json()

    def get_history(self, lines = 0):
        if not self.__accessable:
            return logger.error("Maica is not serving")
        import requests, json
        res = requests.post(
            "https://maicadev.monika.love/api/history",
            data = json.dumps(
                {
                    "access_token": self.ciphertext,
                    "chat_session": self.chat_session,
                    "lines": lines
                },
            )
        )
        return res.json()
    
    def reset_chat_session(self):
        if not self.__accessable:
            return logger.error("Maica is not serving")
        import json
        self.status = self.MaicaAiStatus.REQUEST_RESET_SESSION
        self.wss_session.send(
            json.dumps({"chat_session":self.chat_session, "purge":True})
        )
        self.status = self.MaicaAiStatus.SESSION_RESETED
        self.history_status = None
        self.wss_session.close()

    def close_wss_session(self):
        self.wss_session.close()

    def accessable(self):
        if self.in_mas:
            try:
                import certifi
                certifi.set_parent_dir
            except AttributeError:
                logger.error("certifi is broken")
                self.status = self.MaicaAiStatus.CERTIFI_BROKEN
                self.__accessable = False
                return
                
        import requests, json
        res = requests.post("https://maicadev.monika.love/api/accessibility")
        d = res.json()
        if d["success"]:
            self._serving_status = d["accessibility"]
            if d["accessibility"] != "serving":
                self.status = self.MaicaAiStatus.SERVER_MAINTAIN
                self.__accessable = False
                logger.error("Maica is not serving: {}".format(d["accessibility"]))
            else:
                self.__accessable = True
                self.status = self.MaicaAiStatus.NOT_READY
        else:
            self.status = self.MaicaAiStatus.SERVER_MAINTAIN
            self.__accessable = False
            logger.error("Maica is not serving: {}".format(d["accessibility"]))
            

        


