# -*- coding: utf-8 -*-

from bot_interface import *
import bot_interface
import emotion_analyze_v2

import websocket
websocket._logging._logger = logger
websocket._logging.enableTrace(True)


class MaicaAi(ChatBotInterface):
    class MaicaAiModel:
        maica_main = "maica_main"
        maica_core = "maica_core"
    class MaicaAiStatus:
        # 未准备好
        NOT_READY = 10000
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

        # 令牌验证失败
        TOKEN_FAILED = 13400
        # 选择的 model 不正确
        MODEL_NOT_FOUND = 13401
        # wss异常关闭
        WSS_CLOSED_UNEXCEPTED = 13402
        ######### MAICA 服务器状态码
        MAIKA_PREFIX = 5000
        @classmethod
        def is_1xx(cls, code):
            return 100 <= int(code) - cls.MAIKA_PREFIX <= 199
        
        # session 已超过 32768token
        TOKEN_MAX_EXCEEDED = MAIKA_PREFIX + 204
        # session > 24000token
        TOKEN_24000_EXCEEDED = MAIKA_PREFIX + 200

        _descriptions = {
            NOT_READY: u"未准备好, 等待配置账户信息",
            WAIT_AUTH: u"账户信息已确认，连接MAICA服务器验证中",
            WAIT_SERVER_TOKEN: u"等待令牌验证结果",
            WAIT_USE_TOKEN: u"等待传入令牌",
            SESSION_CREATED: u"令牌已传入，session已开启，应该选择模型了",
            WAIT_MODEL_INFOMATION: u"等待模型信息",
            MESSAGE_WAIT_INPUT: u"maica 已准备好，等待玩家输入",
            MESSAGE_WAIT_SEND: u"已输入消息，等待消息发送",
            MESSAGE_WAITING_RESPONSE: u"已发送消息，等待MAICA回应",
            MESSAGE_DONE: u"MAICA 已经输出完毕",
            REQUEST_RESET_SESSION: u"请求重置session",
            SESSION_RESETED: u"session已重置，websocket已关闭",
            REQUEST_PING: u"请求心跳包",
            TOKEN_FAILED: u"令牌验证失败",
            MODEL_NOT_FOUND: u"选择的 model 不正确",
            TOKEN_MAX_EXCEEDED:u"session 已超过 28672 token, 可能有部分对话已被删除",
            TOKEN_24000_EXCEEDED:u"session 已超过 24576 token, 如需要历史记录请及时保存, 对话可能已删除过",
            WSS_CLOSED_UNEXCEPTED:u"websocket异常关闭, 查看log以获取详细信息"
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
        "max_tokens":[0, 128, None],
        "frequency_penalty":[0.0, 1.0, 0.0],
        "presence_penalty":[0.0, 1.0, 0.0],
        "seed":[0, 999, None]
    }
    

    def __init__(self, account, pwd, token = ""):
        import threading
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
        # 待发送消息队列
        self.senddata_queue = Queue() if not PY3 else bot_interface.Queue()
        self._received = ""
        self.status = self.MaicaAiStatus.NOT_READY
        self.history_status = None
        self._gen_token(account, pwd, token) if account != "" and pwd != "" else ""
        self.modelconfig = {}
        self.reset_stat()
        self.auto_reconnect = False
    def reset_stat(self):
        self.stat = {
            "message_count":0,
            "received_token":0
        }
    def update_stat(self, new):
        self.stat.update(new)
    def get_message(self):
        return self.message_list.get()
    def _gen_token(self, account, pwd, token, email = None):
        if PY2:
            import requests
            data = {
                "username":account,
                "password":pwd
            }
            response = requests.post("https://maicadev.monika.love/api/register", json=data)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("success"):
                    self.ciphertext = response_data.get("token")
                else:
                    raise Exception("Token Generate Fail: {}".format(response_data.get("exception")))
            else:
                raise Exception("Request Fail: {}".format(response.status_code))
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
            if token == "":
                message = json.dumps(data, ensure_ascii=False).encode('utf-8')
                print(message)
                self.ciphertext = base64.b64encode(cipher.encrypt(message)).decode('utf-8')
            else:
                self.ciphertext = token

    def init_connect(self):
        import threading
        threading.Thread(target=self._init_connect).start()

    def _init_connect(self):
        logger.debug("_init_connect")
        if not self.multi_lock.acquire(1):
            return logger.warning("Maica::_init_connect try to create multi connection")
        import websocket
        self.wss_session = websocket.WebSocketApp(self.url, on_open=self._on_open, on_message=self._on_message, on_error=self._on_error
                                                  , on_close=self._on_close)
        self.wss_session.ping_payload = "PING"
        self.status = self.MaicaAiStatus.WAIT_AUTH
        self.wss_session.run_forever()
        self.multi_lock.release()
        
        
    # 检查参数合法性
    def _check_modelconfig(self):
        for i in self.def_modelconfig:
            if i in self.modelconfig:
                if i in ("max_tokens", "seed"):
                    if type(self.modelconfig[i]) != int:
                        logger.warning("modelconfig {} is invaild: reset {} -> {}".format(i, self.modelconfig[i], round(self.modelconfig[i])))
                        self.modelconfig[i] = round(self.modelconfig[i])
                if not self.def_modelconfig[i][0] <= self.modelconfig[i] <= self.def_modelconfig[i][1]:
                    if self.def_modelconfig[i][2] == None:
                        logger.warning("modelconfig {} is invaild: reset {} -> deleted".format(i, self.modelconfig[i]))
                        del self.modelconfig[i]
                    else:
                        logger.warning("modelconfig {} is invaild: reset  {} -> {}".format(i, self.modelconfig[i], self.def_modelconfig[i][2]))
                        self.modelconfig[i] = self.def_modelconfig[i][2]
            
    def is_responding(self):
        """返回maica是否正在返回消息"""
        return self.status in (self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE, self.MaicaAiStatus.MESSAGE_WAIT_SEND)

    def is_ready_to_input(self):
        """返回maica是否可以发送消息了"""
        return self.status in (self.MaicaAiStatus.MESSAGE_WAIT_INPUT, self.MaicaAiStatus.MESSAGE_DONE)
    
    def len_message_queue(self):
        """返回maica已接收并完成分句的台词数"""
        if PY2:
            return self.message_list.size()
        return len(self.message_list.queue)
            
    def _on_open(self, wsapp):
        logger.info("_on_open")
        import time, threading
        def send_message():
            import json
            while True:
                if self.wss_session.keep_running == False:
                    logger.info("websocket is closed")
                    break
                time.sleep(1)
                # 消息已进入队列，等待发送
                if self.status == self.MaicaAiStatus.MESSAGE_WAIT_SEND:
                    if PY2:
                        message = self.senddata_queue.get().decode().strip()
                    else:
                        message = self.senddata_queue.get().strip()
                    dict = {"chat_session":self.chat_session, "query":message}
                    logger.debug(dict)
                    self._check_modelconfig()
                    dict.update(self.modelconfig)
                    message = json.dumps(dict, ensure_ascii=False) 
                    #print(f"_on_open::self.MaicaAiStatus.MESSAGE_WAIT_SEND: {message}")
                    self.wss_session.send(
                        message
                    )   
                    self.status = self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE

                # 身份验证
                elif self.status == self.MaicaAiStatus.WAIT_AUTH:
                    self.status = self.MaicaAiStatus.WAIT_SERVER_TOKEN
                    self.wss_session.send(self.ciphertext)
                    logger.info(self.status)
                # 连接已建立，选择模型
                elif self.status == self.MaicaAiStatus.SESSION_CREATED:
                    self.wss_session.send(
                        json.dumps({"model":self.model, "sf_extraction":self.sf_extraction, "stream_output":self.stream_output})
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
        self.wss_thread = threading.Thread(target=send_message)
        self.wss_thread.start()
    _pos = 0
    def _on_message(self, wsapp, message):
        logger.debug("_on_message: {}".format(message))
        
        logger.debug("self.status: {}".format(self.status))
        import json
        data = json.loads(message)
        logger.debug("data.status in process: {}".format(data["status"] in ("delete_hint", "delete", "session_created", "nickname", "ok", "continue", "streaming_done")))
        if data["status"] == "delete_hint":
            self.history_status = self.MaicaAiStatus.TOKEN_24000_EXCEEDED
        elif data["status"] == "delete":
            self.history_status = self.MaicaAiStatus.TOKEN_MAX_EXCEEDED 
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
                isnum = is_a_talk(self._received[self._pos:])
                logger.debug("MESSAGE_WAITING_RESPONSE:: isnum: {}".format(isnum))
                if isnum:
                    try:
                        raw_message = self._received[self._pos:self._pos + isnum]
                        res = self.MoodStatus.analyze(raw_message)
                        logger.debug("MESSAGE_WAITING_RESPONSE::res: {}".format(res))
                        emote = self.MoodStatus.get_emote()
                        logger.debug("MESSAGE_WAITING_RESPONSE::emote: {}".format(emote))
                        logger.debug("MESSAGE_WAITING_RESPONSE::MoodStatus: pre_mood:{} strength:m{}/r{}".format(self.MoodStatus.pre_mood, self.MoodStatus.main_strength, self.MoodStatus.repeat_strength))
                        self.message_list.put((emote, res.strip()))
                        logger.debug("Server:",self._received[self._pos:self._pos + isnum])
                        self._pos = self._pos + isnum
                    except Exception as e:
                        import traceback
                        logger.error("MESSAGE_WAITING_RESPONSE::exception is ocurrred: \n{}".format(traceback.format_exc()))

            if data['status'] == "streaming_done":
                try:
                    if "not is_a_talk(self._received[self._pos:])" and len(self._received)- 1 - self._pos > 2:
                        raw_message = self._received[self._pos:]
                        res = self.MoodStatus.analyze(raw_message)
                        logger.debug("MESSAGE_WAITING_RESPONSE::res: {}".format(res))
                        emote = self.MoodStatus.get_emote()
                        logger.debug("MESSAGE_WAITING_RESPONSE::emote: {}".format(emote))
                        self.message_list.put((emote, res.strip()))
                        logger.debug("Server:",self._received[self._pos:])
                except Exception as e:
                    import traceback
                    logger.error("MESSAGE_WAITING_RESPONSE::exception is ocurrred: \n{}".format(traceback.format_exc()))
                self._pos = 0
                self._received = ""
                self.status = self.MaicaAiStatus.MESSAGE_DONE
                self.MoodStatus.reset()
        if self.update_screen_func:
            self.update_screen_func(0)
    def _on_error(self, wsapp, error):
        logger.error("MaicaAi::_on_error {}".format(error))
        self.status = self.MaicaAiStatus.WSS_CLOSED_UNEXCEPTED
        self.close_wss_session()

    def _on_close(self, wsapp, close_status_code, close_msg):
        if close_status_code or close_msg:
            logger.info("MaicaAi::_on_close {}|{}".format(close_status_code, close_msg))
        
    def chat(self, message):
        if not self.status in (self.MaicaAiStatus.MESSAGE_WAIT_INPUT, self.MaicaAiStatus.MESSAGE_DONE):
            raise RuntimeError("Maica not ready to chat")
        
        self.senddata_queue.put(key_replace(message, chinese_to_english_punctuation))
        self.stat['message_count'] += 1
        self.status = self.MaicaAiStatus.MESSAGE_WAIT_SEND


    def upload_save(self, dict):
        import requests, json
        res = requests.post(
            "https://maicadev.monika.love/api/savefile",
            data = json.dumps(
                {
                    "access_token": self.ciphertext,
                    "chat_session": self.chat_session,
                    "content": dict
                },
            )
        )
        return res.json()

    def get_history(self, lines = 0):
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
        import json
        self.status = self.MaicaAiStatus.REQUEST_RESET_SESSION
        self.wss_session.send(
            json.dumps({"chat_session":self.chat_session, "purge":True})
        )
        self.status = self.MaicaAiStatus.SESSION_RESETED
        self.wss_session.close()

    def close_wss_session(self):
        self.wss_session.close()
        self.wss_session.keep_running = False


        


