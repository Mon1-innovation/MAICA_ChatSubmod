from bot_interface import *

class MaicaAi(ChatBotInterface):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.hashes import SHA1
    from cryptography.hazmat.primitives.asymmetric import rsa
    import json
    import base64
    import asyncio
    import websockets
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
    chat_session = 0
    wss_session = None
    def __init__(self, account, pwd, token = "") -> None:
        super().__init__(account, pwd, token)
        # 加密
        data = {
            "username":account,
            "password":pwd
        }
        message = json.dumps(data).encode('utf-8')
        ciphertext = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=SHA1()),
                algorithm=SHA1(),
                label=None
            )
        )
        # 发送ciphertext
        wss_session = websockets.connect(url)
