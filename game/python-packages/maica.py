from bot_interface import *
import logging

import logging

logger = logging.getLogger()
logger.setLevel('DEBUG')
BASIC_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
chlr = logging.StreamHandler() # 输出到控制台的handler
chlr.setFormatter(formatter)
chlr.setLevel('INFO')  # 也可以不设置，不设置就默认用logger的level
fhlr = logging.FileHandler('example.log')
fhlr.setFormatter(formatter)
logger.addHandler(chlr)
logger.addHandler(fhlr)
logger.info('this is info')

class MaicaAi(ChatBotInterface):
    class MaicaAiModel:
        maica_main = "maica_main"
        maica_main_nostream = "maica_main_nostream"
        maica_core = "maica_core"
        maica_core_nostream = "maica_core_nostream"
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

        ######### MAICA 服务器状态码
        MAIKA_PREFIX = 5000
        def is_1xx(self, code):
            return 100 <= int(code) - self.MAIKA_PREFIX <= 199
        
        # session 已超过 32768token
        TOKEN_MAX_EXCEEDED = MAIKA_PREFIX + 204
        # session > 24000token
        TOKEN_24000_EXCEEDED = MAIKA_PREFIX + 200
    import json
    import base64
    import asyncio
    import websocket
    
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
    public_key = None
    ciphertext = None
    chat_session = 1
    wss_session = None

    user_acc = ""

    model = MaicaAiModel.maica_core

    sf_extraction = False
    # 待发送消息队列
    senddata_queue = Queue()
    _received = ""
    status = MaicaAiStatus.NOT_READY

    def __init__(self, account, pwd, token = "") -> None:
        super().__init__(account, pwd, token)
        self._gen_token(account, pwd, token)

    def _gen_token(self, account, pwd, token):
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
        self.token = token
        if token == "":
            message = json.dumps(data, ensure_ascii=False).encode('utf-8')
            print(message)
            self.ciphertext = base64.b64encode(cipher.encrypt(message))
        else:
            self.ciphertext = token

    def init_connect(self):
        import threading
        threading.Thread(target=self._init_connect).start()

    def _init_connect(self):
        print("_init_connect")
        import websocket
        self.wss_session = websocket.WebSocketApp(self.url, on_open=self._on_open, on_message=self._on_message)
        self.status = self.MaicaAiStatus.WAIT_AUTH
        if self.wss_session.run_forever():
            raise RuntimeError("websocket 已关闭")
    
    def _on_open(self, wsapp):
        logger.info("_on_open")
        import time, threading
        def send_message():
            import json
            while True:
                logger.info(self.status)
                time.sleep(1)
                # 消息已进入队列，等待发送
                if self.status == self.MaicaAiStatus.MESSAGE_WAIT_SEND:
                    message = json.dumps({"chat_session":self.chat_session, "query":self.senddata_queue.get()}, ensure_ascii=False)
                    print(f"_on_open::self.MaicaAiStatus.MESSAGE_WAIT_SEND: {message}")
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
                        json.dumps({"model":self.model, "sf_extraction":self.sf_extraction})
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
                

        threading.Thread(target=send_message).start()
    _pos = 0
    def _on_message(self, wsapp, message):
        logger.info(f"_on_message {message}")
        import json
        data = json.loads(message)
        logger.info("_on_message:")
        # 发送令牌，等待回应
        if self.status == self.MaicaAiStatus.WAIT_SERVER_TOKEN:
            if data['status'] != "session_created":
                self.status = self.MaicaAiStatus.TOKEN_FAILED
                self.wss_session.close()
            else:
                self.status = self.MaicaAiStatus.SESSION_CREATED
        elif self.status == self.MaicaAiStatus.WAIT_MODEL_INFOMATION:
            if data['status'] != "ok":
                self.status = self.MaicaAiStatus.MODEL_NOT_FOUND
            else:
                self.status = self.MaicaAiStatus.MESSAGE_WAIT_INPUT
        elif self.status == self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE:
            if data['status'] == "continue":
                self._received = self._received + data['content']
                isnum = is_a_talk(self._received[self._pos:])
                if isnum:
                    self.message_list.put(("1eua", self._received[self._pos:self._pos + isnum]))
                    print(self._received[self._pos:self._pos + isnum])
                    self._pos = self._pos + isnum
            if data['status'] == "streaming_done":
                if not is_a_talk(self._received[self._pos:]) and len(self._received)- 1 - self._pos > 2:
                    self.message_list.put(("1eua", self._received[self._pos:]))
                    print(self._received[self._pos:])
                self._pos = 0
                self._received = ""
                self.status = self.MaicaAiStatus.MESSAGE_DONE
                
    def chat(self, message):
        if not self.status in (self.MaicaAiStatus.MESSAGE_WAIT_INPUT, self.MaicaAiStatus.MESSAGE_DONE):
            raise RuntimeError("Maica 当前未准备好接受消息")
        self.senddata_queue.put(message)
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
                ensure_ascii=False
            )
        )
        print(res.content.decode())


        


