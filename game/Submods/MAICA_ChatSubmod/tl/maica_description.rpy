translate english python in maica:
    maica.MaicaAiStatus._descriptions.update({
        maica.MaicaAiStatus.NOT_READY: u"Waiting for account setup",
        maica.MaicaAiStatus.WAIT_AVAILABILITY:u"Service status acquiring failed, restart the game for MaicaAi.accessable()",
        maica.MaicaAiStatus.WAIT_AUTH: u"Account acquired, verifying",
        maica.MaicaAiStatus.WAIT_SERVER_TOKEN: u"Waiting for token verification",
        maica.MaicaAiStatus.WAIT_USE_TOKEN: u"Waiting for token",
        maica.MaicaAiStatus.SESSION_CREATED: u"Session opened, waiting for model choice",
        maica.MaicaAiStatus.WAIT_MODEL_INFOMATION: u"Waiting for model information",
        maica.MaicaAiStatus.MESSAGE_WAIT_INPUT: u"MAICA is ready for query",
        maica.MaicaAiStatus.MESSAGE_WAIT_SEND: u"Message acquired, pending delivery",
        maica.MaicaAiStatus.MESSAGE_WAITING_RESPONSE: u"Message sent, waiting for server response",
        maica.MaicaAiStatus.MESSAGE_WAIT_SEND_MSPIRE: u"Waiting for MSpire request to launch",
        maica.MaicaAiStatus.MESSAGE_DONE: u"MAICA streaming finished",
        maica.MaicaAiStatus.REQUEST_RESET_SESSION: u"Requesting session reset",
        maica.MaicaAiStatus.SESSION_RESETED: u"Session reseted, connection closed",
        maica.MaicaAiStatus.REQUEST_PING: u"Send PING",
        maica.MaicaAiStatus.TOKEN_FAILED: u"Token verification failed",
        maica.MaicaAiStatus.MODEL_NOT_FOUND: u"Model choice incorrect",
        maica.MaicaAiStatus.TOKEN_MAX_EXCEEDED:u"Session length over 28672 tokens, part of session is cut",
        maica.MaicaAiStatus.TOKEN_24000_EXCEEDED:u"Session length over 24576 tokens, will be cutted as exceeding 28672",
        maica.MaicaAiStatus.WSS_CLOSED_UNEXCEPTED:u"Websocket closed unexpectedly, check log for details",
        maica.MaicaAiStatus.SAVEFILE_NOTFOUND:u"Savefile for current session not found",
        maica.MaicaAiStatus.SERVER_MAINTAIN:u"Server is under maintaince, please wait for further announcement",
        maica.MaicaAiStatus.WRONE_INPUT:u"Wrong input, check for possible typo",
        maica.MaicaAiStatus.CERTIFI_BROKEN:u"You have a corrupted copy of MAS--likely because of other submods. Reinstallation required",
        maica.MaicaAiStatus.CERTIFI_AUTO_FIX:u"Launched an autofix to cert module--restart the game to take effect",
        maica.MaicaAiStatus.TOOLONG_CONTENT_LENGTH:u"Content too long, you should turn off big MTrigger.",

    })
    store.mas_setEVLPropValues("maica_main", prompt="I want to go to Heaven Forest", category=["You", "Us", "Mod", "MAICA"])
    store.mas_setEVLPropValues("maica_mods_preferences", prompt="I've something to change about my preferences", category=["You", "Us", "Mod", "MAICA"])
    store.mas_setEVLPropValues("maica_wants_preferences_reread", prompt="关于补充偏好", category=["You", "Us", "Mod", "MAICA"])
    store.mas_setEVLPropValues("maica_chr_reread", prompt="天堂树林的角色文件", category=["You", "Us", "Mod", "MAICA"])
    store.mas_setEVLPropValues("maica_prepend_reread", prompt="天堂树林到底是什么", category=["You", "Us", "Mod", "MAICA"])
    store.mas_setEVLPropValues("maica_wants_mspire_reread", prompt="关于'MSpire'", category=["You", "Us", "Mod", "MAICA"])
    store.mas_setEVLPropValues("maica_wants_mpostal_reread", prompt="关于'MPostal'", category=["You", "Us", "Mod", "MAICA"])
