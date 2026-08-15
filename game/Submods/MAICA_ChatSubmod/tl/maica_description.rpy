translate chinese python in maica:
    from bot_interface import PY2, PY3

    try:
        maica_instance.MaicaAiStatus._descriptions.update({
            maica_instance.MaicaAiStatus.NOT_READY: u"等待账号设置",
            maica_instance.MaicaAiStatus.WAIT_AVAILABILITY:u"核心尚未初始化, 如果问题持续请检查mas.log",
            maica_instance.MaicaAiStatus.WAIT_AUTH: u"已获取账号, 正在验证",
            maica_instance.MaicaAiStatus.WAIT_SERVER_TOKEN: u"正在等待Token验证",
            maica_instance.MaicaAiStatus.WAIT_USE_TOKEN: u"正在等待Token",
            maica_instance.MaicaAiStatus.SESSION_CREATED: u"会话已开启, 等待选择模型",
            maica_instance.MaicaAiStatus.WAIT_MODEL_INFOMATION: u"正在等待模型信息",
            maica_instance.MaicaAiStatus.MESSAGE_WAIT_INPUT: u"MAICA已准备好接收询问",
            maica_instance.MaicaAiStatus.SSL_FAILED_BUT_OKAY: u"MAICA正在回退到普通连接. 这通常可以视为正常情况",
            maica_instance.MaicaAiStatus.MESSAGE_WAIT_SEND: u"已获取消息, 等待发送",
            maica_instance.MaicaAiStatus.MESSAGE_WAITING_RESPONSE: u"消息已发送, 正在等待服务器响应",
            maica_instance.MaicaAiStatus.MESSAGE_WAIT_SEND_MSPIRE: u"正在等待发送MSpire请求",
            maica_instance.MaicaAiStatus.MESSAGE_DONE: u"MAICA流式传输已结束",
            maica_instance.MaicaAiStatus.REQUEST_RESET_SESSION: u"正在请求重置会话",
            maica_instance.MaicaAiStatus.SESSION_RESETED: u"会话已重置, 连接已关闭",
            maica_instance.MaicaAiStatus.REQUEST_PING: u"正在发送PING",
            maica_instance.MaicaAiStatus.TOKEN_MISSING: u"尚未配置令牌",
            maica_instance.MaicaAiStatus.TOKEN_CORRUPTED: u"令牌已损坏",
            maica_instance.MaicaAiStatus.TOKEN_INVALID: u"账号或密码无效",
            maica_instance.MaicaAiStatus.LOGIN_BLOCKED: u"登录暂时被阻止",
            maica_instance.MaicaAiStatus.ACCOUNT_BANNED: u"账号已被封禁",
            maica_instance.MaicaAiStatus.EMAIL_UNVERIFIED: u"账号邮箱尚未验证",
            maica_instance.MaicaAiStatus.TOS_UNACCEPTED: u"尚未接受最新服务条款",
            maica_instance.MaicaAiStatus.CONNECTION_REUSE_DENIED: u"账号已存在活动连接",
            maica_instance.MaicaAiStatus.SERVER_REJECTED: u"发生用户级别错误",
            maica_instance.MaicaAiStatus.SERVER_ERROR: u"发生服务器级别错误",
            maica_instance.MaicaAiStatus.TOKEN_GENERATION_FAILED: u"令牌生成失败",
            maica_instance.MaicaAiStatus.CONNECT_PROBLEM: u"无法连接服务器, 请检查网络和submod_log",
            maica_instance.MaicaAiStatus.RESPONSE_INVALID: u"服务器响应无效",
            maica_instance.MaicaAiStatus.TOKEN_MAX_EXCEEDED:u"会话长度已超出限制, 部分会话已裁剪",
            maica_instance.MaicaAiStatus.TOKEN_WARN_EXCEEDED:u"会话长度接近限制, 超出后将被裁剪",
            maica_instance.MaicaAiStatus.SERVER_MAINTAIN:u"服务器正在维护, 请等待后续公告",
            maica_instance.MaicaAiStatus.CERTIFI_BROKEN:u"SSL/TLS已损坏, 可能由其他子模组导致. 需要完全重新安装MAS",

        })
        maica_instance.MaicaAiStatus._descriptions.update({
            maica_instance.MaicaAiStatus.MESSAGE_WAIT_SEND_MPOSTAL: u"正在等待发送MPostal请求",  # 新增
            maica_instance.MaicaAiStatus.SEND_SETTING: u"正在上传设置",  # 新增
            maica_instance.MaicaAiStatus.FAILED_GET_NODE: u"获取服务节点失败, 服务器可能正在维护或离线",  # 新增
            maica_instance.MaicaAiStatus.WEBSOCKET_CONNECTING: u"WebSocket正在连接(这应该很快完成)",  # 新增
            maica_instance.MaicaAiStatus.VERSION_OLD: u"检测到安装版本过旧, 请更新到最新版",  # 新增
        })
        maica_instance.MaicaAiStatus._descriptions.update({
            maica_instance.MaicaAiStatus.NO_INTERNET: u"检测到子模组离线. 请根据Readme重新检查安装和网络连接",  # 新增
        })
        store.mas_setEVLPropValues("maica_main", prompt="我们去天堂树林吧", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_wants_preferences_reread", prompt="[player]的偏好", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_chr_reread", prompt="关于HeavenForest.sce", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_prepend_reread", prompt="天堂树林到底是什么", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_wants_mspire_reread", prompt="关于'MSpire'", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_wants_mpostal_reread", prompt="关于'MPostal'", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_set_location_reread", prompt="[player]的住址", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_wants_mvista_reread", prompt="关于'MVista'", category=["你", "我们", "模组", "MAICA"])
    except Exception as e:
        import store
        store.mas_submod_utils.submod_log.error("MAICA Blessland seemingly not exist: {}".format(e))


translate chinese python:

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
