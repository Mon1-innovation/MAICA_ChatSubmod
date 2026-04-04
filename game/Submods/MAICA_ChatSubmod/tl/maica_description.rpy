translate english python in maica:
    try:
        from bot_interface import PY2, PY3
    except Exception:
        from mtts import PY2, PY3
    try:
        maica_instance.MaicaAiStatus._descriptions.update({
            maica_instance.MaicaAiStatus.NOT_READY: u"Waiting for account setup",
            maica_instance.MaicaAiStatus.WAIT_AVAILABILITY:u"Core not initialized, check mas.log if issue persists",
            maica_instance.MaicaAiStatus.WAIT_AUTH: u"Account acquired, verifying",
            maica_instance.MaicaAiStatus.WAIT_SERVER_TOKEN: u"Waiting for token verification",
            maica_instance.MaicaAiStatus.WAIT_USE_TOKEN: u"Waiting for token",
            maica_instance.MaicaAiStatus.SESSION_CREATED: u"Session opened, waiting for model choice",
            maica_instance.MaicaAiStatus.WAIT_MODEL_INFOMATION: u"Waiting for model information",
            maica_instance.MaicaAiStatus.MESSAGE_WAIT_INPUT: u"MAICA is ready for query",
            maica_instance.MaicaAiStatus.SSL_FAILED_BUT_OKAY: u"MAICA falling back to plain connection. This can be considered normal",
            maica_instance.MaicaAiStatus.MESSAGE_WAIT_SEND: u"Message acquired, pending delivery",
            maica_instance.MaicaAiStatus.MESSAGE_WAITING_RESPONSE: u"Message sent, waiting for server response",
            maica_instance.MaicaAiStatus.MESSAGE_WAIT_SEND_MSPIRE: u"Waiting for MSpire request to launch",
            maica_instance.MaicaAiStatus.MESSAGE_DONE: u"MAICA streaming finished",
            maica_instance.MaicaAiStatus.REQUEST_RESET_SESSION: u"Requesting session reset",
            maica_instance.MaicaAiStatus.SESSION_RESETED: u"Session reseted, connection closed",
            maica_instance.MaicaAiStatus.REQUEST_PING: u"Send PING",
            maica_instance.MaicaAiStatus.TOKEN_FAILED: u"Token verification failed",
            maica_instance.MaicaAiStatus.MODEL_NOT_FOUND: u"Model choice incorrect",
            maica_instance.MaicaAiStatus.TOKEN_MAX_EXCEEDED:u"Session length exceeded, part of session is cropped",
            maica_instance.MaicaAiStatus.TOKEN_24000_EXCEEDED:u"Session length near threshold, will be cropped when exceeding",
            maica_instance.MaicaAiStatus.WSS_CLOSED_UNEXCEPTED:u"Websocket closed unexpectedly, check submod_log for details" if PY2 else u"Websocket closed unexpectedly, please reconfirm datapack extraction, check submod_log for details",
            maica_instance.MaicaAiStatus.SAVEFILE_NOTFOUND:u"Savefile for current session not found",
            maica_instance.MaicaAiStatus.SERVER_MAINTAIN:u"Server is under maintaince, please wait for further announcement",
            maica_instance.MaicaAiStatus.WRONE_INPUT:u"Wrong input, check for possible typo",
            maica_instance.MaicaAiStatus.CERTIFI_BROKEN:u"SSL/TLS corrupted, possibly caused by other submods. Clean reinstalling MAS required",
            maica_instance.MaicaAiStatus.CERTIFI_AUTO_FIX:u"SSL/TLS corrupted, restart the game to apply patch. Clean reinstall MAS if issue persists",
            maica_instance.MaicaAiStatus.TOOLONG_CONTENT_LENGTH:u"Content length exceeded, consider disabling large MTrigger items",
            maica_instance.MaicaAiStatus.IS_SOURCECODE:u"Source code installation detected. Please install from release instead",

        })
        maica_instance.MaicaAiStatus._descriptions.update({
            maica_instance.MaicaAiStatus.MESSAGE_WAIT_SEND_MPOSTAL: u"Waiting to send MPostal request",  # 新增
            maica_instance.MaicaAiStatus.SEND_SETTING: u"Uploading settings",  # 新增
            maica_instance.MaicaAiStatus.FAILED_GET_NODE: u"Failed to get service node, server may be under maintenance or offline",  # 新增
            maica_instance.MaicaAiStatus.WEBSOCKET_CONNECTING: u"WebSocket is connecting (this should be quick)",  # 新增
            maica_instance.MaicaAiStatus.VERSION_OLD: u"Stale installation detected. Please update to latest release",  # 新增
        })
        maica_instance.MaicaAiStatus._descriptions.update({
            maica_instance.MaicaAiStatus.NO_INTERTENT: u"Submod offline detected. Double check installation and connectivity according to Readme",  # 新增
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
        store.mas_submod_utils.submod_log.error("MAICA Blessland seemingly not exist: {}".format(e))


translate english python:

    try:
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
    except Exception as e:
        import store
        store.mas_submod_utils.submod_log.error("MAICA Blessland seemingly not exist: {}".format(e))
