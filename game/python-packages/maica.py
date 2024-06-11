from bot_interface import *

class MaicaAi(ChatBotInterface):
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
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.hashes import SHA1
    from cryptography.hazmat.primitives.asymmetric import rsa
    import json
    import base64
    import asyncio
    import websocket
    
    url = "wss://maicadev.monika.love/websocket"
    public_key_pem = b"""
-----BEGIN RSA PUBLIC KEY-----
MIIBCgKCAQEA2IHJQAPwWuynuivzvu/97/EbN+ttYoNmJyvu9RC/M9CHXCi1Emgc
/KIluhzfJesBU/E/TX/xeuwURuGcyhIBk0qmba8GOADVjedt1OHcP6DJQJwu6+Bp
kGd8BIqYFHjbsNwkBZiq7s0nRiHig0asd+Hhl/pwplXH/SIjASMlDPijF24OUSfP
+D7eRohyO4sWuj6WTExDq7VoCGz4DBGM3we9wN1YpWMikcb9RdDg+f610MUrzQVf
l3tCkUjgHS+RhNtksuynpwm84Mg1MlbgU5s5alXKmAqQTTJ2IG61PHtrrCTVQA9M
t9vozy56WuHPfv3KZTwrvZaIVSAExEL17wIDAQAB
-----END RSA PUBLIC KEY-----
"""
    public_key = serialization.load_pem_public_key(public_key_pem)
    ciphertext = None
    chat_session = 0
    wss_session = None

    model = "maica_main"
    sf_extraction = True
    # 待发送消息队列
    senddata_queue = Queue()
    _received = ""
    status = MaicaAiStatus.NOT_READY

    def __init__(self, account, pwd, token = "") -> None:
        super().__init__(account, pwd, token)
        import json, websocket
        # 加密
        data = {
            "username":account,
            "password":pwd
        }
        self.token = token
        message = json.dumps(data).encode('utf-8')
        self.ciphertext = self.public_key.encrypt(
            message,
            self.padding.OAEP(
                mgf=self.padding.MGF1(algorithm=self.SHA1()),
                algorithm=self.SHA1(),
                label=None
            )
        )

    def init_connect(self):
        import websocket
        self.wss_session = websocket.WebSocketApp(self.url, on_open=self._on_open, on_message=self._on_message, on_close=None)
        self.status = self.MaicaAiStatus.WAIT_AUTH
        if self.wss_session:
            raise Exception("websocket 创建失败")
    def _on_open(self, wsapp):
        import time, threading
        def send_message():
            import json
            while True:
                if self.status == self.MaicaAiStatus.MESSAGE_WAIT_SEND:
                    self.wss_session.send(
                        json.dumps({"chat_session":self.chat_session, "query":self.senddata_queue.get()})
                    )
                    self.status = self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE
                elif self.status == self.MaicaAiStatus.WAIT_AUTH:
                    # 如果token空
                    self.wss_session.send(self.ciphertext)
                    self.status == self.MaicaAiStatus.WAIT_SERVER_TOKEN
                elif self.status == self.MaicaAiStatus.SESSION_CREATED:
                    self.wss_session.send(
                        json.dumps({"model":self.model, "sf_extraction":self.sf_extraction})
                    )
                    self.status == self.MaicaAiStatus.WAIT_MODEL_INFOMATION
                elif self.status == self.MaicaAiStatus.REQUEST_RESET_SESSION:
                    self.wss_session.send(
                        json.dumps({"chat_session":self.chat_session, "purge":True})
                    )
                    self.status = self.MaicaAiStatus.SESSION_RESETED
                    self.wss_session.close()
                

        threading.Thread(target=send_message).start()
    _pos = 0
    def _on_message(self, wsapp, message):
        import json
        data = json.loads(message)

        if self.status == self.MaicaAiStatus.WAIT_SERVER_TOKEN:
            if data['status'] != "ok":
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
                if not is_a_talk(self._received[self._pos:]):
                    pass
                else:
                    self.message_list.put(("1eua", self._received[self._pos:]))
                    self._pos = len(self._received)
            if data['status'] == "streaming_done":
                if not is_a_talk(self._received[self._pos:]) and len(self._received)- 1 - self._pos > 2:
                    self.message_list.put(("1eua", self._received[self._pos:]))
                self._pos = 0
                self.status = self.MaicaAiStatus.MESSAGE_WAIT_INPUT
                
    def chat(self, message):
        if self.status != self.MaicaAiStatus.MESSAGE_WAIT_INPUT:
            raise RuntimeError("Maica 当前未准备好接受消息")
        self.senddata_queue.put(message)
        self.status = self.MaicaAiStatus.MESSAGE_WAIT_SEND


        


