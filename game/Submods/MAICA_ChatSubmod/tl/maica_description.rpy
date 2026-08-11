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
            maica_instance.MaicaAiStatus.TOKEN_FAILED: u"Token验证失败",
            maica_instance.MaicaAiStatus.MODEL_NOT_FOUND: u"模型选择错误",
            maica_instance.MaicaAiStatus.TOKEN_MAX_EXCEEDED:u"会话长度已超出限制, 部分会话将被裁剪",
            maica_instance.MaicaAiStatus.TOKEN_24000_EXCEEDED:u"会话长度接近阈值, 超出后将被裁剪",
            maica_instance.MaicaAiStatus.WSS_CLOSED_UNEXCEPTED:u"WebSocket异常关闭, 请查看submod_log获取详细信息" if PY2 else u"WebSocket异常关闭, 请重新确认datapack是否正确解压, 并查看submod_log获取详细信息",
            maica_instance.MaicaAiStatus.SAVEFILE_NOTFOUND:u"未找到当前会话的存档文件",
            maica_instance.MaicaAiStatus.SERVER_MAINTAIN:u"服务器正在维护, 请等待后续公告",
            maica_instance.MaicaAiStatus.WRONE_INPUT:u"输入错误, 请检查是否有拼写错误",
            maica_instance.MaicaAiStatus.CERTIFI_BROKEN:u"SSL/TLS已损坏, 可能由其他子模组导致. 需要完全重新安装MAS",
            maica_instance.MaicaAiStatus.CERTIFI_AUTO_FIX:u"SSL/TLS已损坏, 请重启游戏以应用补丁. 如果问题持续, 请完全重新安装MAS",
            maica_instance.MaicaAiStatus.TOOLONG_CONTENT_LENGTH:u"内容长度超出限制, 可考虑禁用大型MTrigger项目",
            maica_instance.MaicaAiStatus.IS_SOURCECODE:u"检测到源码安装. 请改用发布版安装",

        })
        maica_instance.MaicaAiStatus._descriptions.update({
            maica_instance.MaicaAiStatus.MESSAGE_WAIT_SEND_MPOSTAL: u"正在等待发送MPostal请求",  # 新增
            maica_instance.MaicaAiStatus.SEND_SETTING: u"正在上传设置",  # 新增
            maica_instance.MaicaAiStatus.FAILED_GET_NODE: u"获取服务节点失败, 服务器可能正在维护或离线",  # 新增
            maica_instance.MaicaAiStatus.WEBSOCKET_CONNECTING: u"WebSocket正在连接(这应该很快完成)",  # 新增
            maica_instance.MaicaAiStatus.VERSION_OLD: u"检测到安装版本过旧, 请更新到最新版",  # 新增
        })
        maica_instance.MaicaAiStatus._descriptions.update({
            maica_instance.MaicaAiStatus.NO_INTERTENT: u"检测到子模组离线. 请根据Readme重新检查安装和网络连接",  # 新增
        })
        store.mas_setEVLPropValues("maica_main", prompt="我们去天堂树林吧", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_mods_preferences", prompt="我想修改我的偏好", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_wants_preferences_reread", prompt="关于我的偏好", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_chr_reread", prompt="关于HeavenForest.sce", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_prepend_reread", prompt="天堂树林到底是什么", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_wants_mspire_reread", prompt="关于'MSpire'", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_wants_mpostal_reread", prompt="关于'MPostal'", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_pre_set_location", prompt="[player]的住址", category=["你", "我们", "模组", "MAICA"])
        store.mas_setEVLPropValues("maica_pre_wants_mvista", prompt="关于'MVista'", category=["你", "我们", "模组", "MAICA"])
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
