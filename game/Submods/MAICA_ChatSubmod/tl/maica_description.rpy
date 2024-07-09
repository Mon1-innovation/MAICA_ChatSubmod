translate english python in maica:
    maica._descriptions.update({
        maica.MaicaAiStatus.NOT_READY: u"Waiting for account setup",
        maica.MaicaAiStatus.WAIT_AUTH: u"Account acquired, verifying",
        maica.MaicaAiStatus.WAIT_SERVER_TOKEN: u"Waiting for token verification",
        maica.MaicaAiStatus.WAIT_USE_TOKEN: u"Waiting for token",
        maica.MaicaAiStatus.SESSION_CREATED: u"Session opened, waiting for model choice",
        maica.MaicaAiStatus.WAIT_MODEL_INFOMATION: u"Waiting for model information",
        maica.MaicaAiStatus.MESSAGE_WAIT_INPUT: u"MAICA is ready for query",
        maica.MaicaAiStatus.MESSAGE_WAIT_SEND: u"Message acquired, pending delivery",
        maica.MaicaAiStatus.MESSAGE_WAITING_RESPONSE: u"Message sent, waiting for server response",
        maica.MaicaAiStatus.MESSAGE_DONE: u"MAICA streaming finished",
        maica.MaicaAiStatus.REQUEST_RESET_SESSION: u"Requesting session reset",
        maica.MaicaAiStatus.SESSION_RESETED: u"Session reseted, connection closed",
        maica.MaicaAiStatus.REQUEST_PING: u"Send PING",
        maica.MaicaAiStatus.TOKEN_FAILED: u"Token verification failed",
        maica.MaicaAiStatus.MODEL_NOT_FOUND: u"Model choice incorrect",
        maica.MaicaAiStatus.TOKEN_MAX_EXCEEDED:u"Session length over 28672 tokens, part of session is cut",
        maica.MaicaAiStatus.TOKEN_24000_EXCEEDED:u"Session length over 24576 tokens, will be cutted as exceeding 28672",
        maica.MaicaAiStatus.WSS_CLOSED_UNEXCEPTED:u"Websocket closed unexpectedly, check log for details",
        maica.MaicaAiStatus.SAVEFILE_NOTFOUND:u"Savefile for current session not found"
    })
    store.mas_setEVLPropValues("maica_main", prompt="I want to go to heaven forest", category=["You", "Us", "Mod"])