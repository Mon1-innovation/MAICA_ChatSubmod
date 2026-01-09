translate english python in maica:
    from bot_interface import PY2, PY3
    try:
        maica.MaicaAiStatus._descriptions.update({
            maica.MaicaAiStatus.NOT_READY: u"Waiting for account setup",
            maica.MaicaAiStatus.WAIT_AVAILABILITY:u"Service status acquiring failed, restart the game and check mas.log if issue persists",
            maica.MaicaAiStatus.WAIT_AUTH: u"Account acquired, verifying",
            maica.MaicaAiStatus.WAIT_SERVER_TOKEN: u"Waiting for token verification",
            maica.MaicaAiStatus.WAIT_USE_TOKEN: u"Waiting for token",
            maica.MaicaAiStatus.SESSION_CREATED: u"Session opened, waiting for model choice",
            maica.MaicaAiStatus.WAIT_MODEL_INFOMATION: u"Waiting for model information",
            maica.MaicaAiStatus.MESSAGE_WAIT_INPUT: u"MAICA is ready for query",
            maica.MaicaAiStatus.SSL_FAILED_BUT_OKAY: u"MAICA falling back to plain connection. This can be considered normal",
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
            maica.MaicaAiStatus.WSS_CLOSED_UNEXCEPTED:u"Websocket closed unexpectedly, check submod_log for details" if PY2 else u"Websocket closed unexpectedly, please reconfirm datapack extraction, check submod_log for details",
            maica.MaicaAiStatus.SAVEFILE_NOTFOUND:u"Savefile for current session not found",
            maica.MaicaAiStatus.SERVER_MAINTAIN:u"Server is under maintaince, please wait for further announcement",
            maica.MaicaAiStatus.WRONE_INPUT:u"Wrong input, check for possible typo",
            maica.MaicaAiStatus.CERTIFI_BROKEN:u"You have a corrupted copy of MAS--likely because of other submods. Reinstallation required",
            maica.MaicaAiStatus.CERTIFI_AUTO_FIX:u"Tried autofixing broken cert module--restart the game to take effect, clean install if it doesn't.",
            maica.MaicaAiStatus.TOOLONG_CONTENT_LENGTH:u"Content too long, you should turn off big MTrigger.",
            maica.MaicaAiStatus.IS_SOURCECODE:u"This is a sourcecode copy, not an official release. Please download the latest release from the Releases page.",

        })
        maica.MaicaAiStatus._descriptions.update({
            maica.MaicaAiStatus.MESSAGE_WAIT_SEND_MPOSTAL: u"Waiting to send MPostal request",  # 新增
            maica.MaicaAiStatus.SEND_SETTING: u"Uploading settings",  # 新增
            maica.MaicaAiStatus.FAILED_GET_NODE: u"Failed to get service node, server may be under maintenance or offline",  # 新增
            maica.MaicaAiStatus.WEBSOCKET_CONNECTING: u"WebSocket is connecting (this should be quick)",  # 新增
            maica.MaicaAiStatus.VERSION_OLD: u"Submod version is outdated, please update to the latest version",  # 新增
        })
        maica.MaicaAiStatus._descriptions.update({
            maica.MaicaAiStatus.NO_INTERTENT: u"Submod offline, double check installation and connectivity according to Readme",  # 新增
        })
        store.mas_setEVLPropValues("maica_main", prompt="I want to go to Heaven Forest", category=["you", "us", "mod", "MAICA"])
        store.mas_setEVLPropValues("maica_mods_preferences", prompt="I've something to change about my preferences", category=["you", "us", "mod", "MAICA"])
        store.mas_setEVLPropValues("maica_wants_preferences_reread", prompt="About my preferences", category=["you", "us", "mod", "MAICA"])
        store.mas_setEVLPropValues("maica_chr_reread", prompt="About HeavenForest.sce", category=["you", "us", "mod", "MAICA"])
        store.mas_setEVLPropValues("maica_prepend_reread", prompt="What is Heaven Forest after all", category=["you", "us", "mod", "MAICA"])
        store.mas_setEVLPropValues("maica_wants_mspire_reread", prompt="About 'MSpire'", category=["you", "us", "mod", "MAICA"])
        store.mas_setEVLPropValues("maica_wants_mpostal_reread", prompt="About 'MPostal'", category=["you", "us", "mod", "MAICA"])
        store.mas_setEVLPropValues("maica_pre_set_location", prompt="Where [player] lives", category=["you", "us", "mod", "MAICA"])
        store.mas_setEVLPropValues("maica_pre_wants_mvista", prompt="Aboue 'MVista'", category=["you", "us", "mod", "MAICA"])
    except Exception as e:
        import store
        store.mas_submod_utils.submod_log.error("Failed while translating MAICA descriptions: {}".format(e))


translate english python:

    import maica_provider_manager as mpm

    mpm.MaicaProviderManager._isfailedresponse.update(
        {
            "name":"ERROR: Unable to retrieve node information.",
            "description": "Check the update log to get the current service status, or check submod_log.log for the cause of the failure.",
            "isOfficial": False,
            "portalPage": "https://forum.monika.love/d/3954",
            "servingModel": "Check the update log to get the current service status, or check submod_log.log for the cause of the failure.",
            "modelLink": "",
            "wsInterface": "wss://maicadev.monika.love/websocket",
            "httpInterface": "https://maicadev.monika.love/api"
        }
    )
    mpm.MaicaProviderManager._fakelocalprovider.update(
        {
            "name":"Local Deployment",
            "description": "When you have an available local deployment, select this node.",
            "isOfficial": False,
            "portalPage": "https://github.com/PencilMario/MAICA",
            "servingModel": "None",
            "modelLink": "",
            "wsInterface": "ws://127.0.0.1:5000",
            "httpInterface": "http://127.0.0.1:6000",
        }
    )
