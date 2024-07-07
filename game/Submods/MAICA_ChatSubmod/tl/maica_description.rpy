translate english python in maica:
    maica._descriptions = {
        maica.MaicaAiStatus.NOT_READY: u"未准备好, 等待配置账户信息",
        maica.MaicaAiStatus.WAIT_AUTH: u"账户信息已确认，连接MAICA服务器验证中",
        maica.MaicaAiStatus.WAIT_SERVER_TOKEN: u"等待令牌验证结果",
        maica.MaicaAiStatus.WAIT_USE_TOKEN: u"等待传入令牌",
        maica.MaicaAiStatus.SESSION_CREATED: u"令牌已传入，session已开启，应该选择模型了",
        maica.MaicaAiStatus.WAIT_MODEL_INFOMATION: u"等待模型信息",
        maica.MaicaAiStatus.MESSAGE_WAIT_INPUT: u"maica 已准备好，等待玩家输入",
        maica.MaicaAiStatus.MESSAGE_WAIT_SEND: u"已输入消息，等待消息发送",
        maica.MaicaAiStatus.MESSAGE_WAITING_RESPONSE: u"已发送消息，等待MAICA回应",
        maica.MaicaAiStatus.MESSAGE_DONE: u"MAICA 已经输出完毕",
        maica.MaicaAiStatus.REQUEST_RESET_SESSION: u"请求重置session",
        maica.MaicaAiStatus.SESSION_RESETED: u"session已重置，websocket已关闭",
        maica.MaicaAiStatus.REQUEST_PING: u"请求心跳包",
        maica.MaicaAiStatus.TOKEN_FAILED: u"令牌验证失败",
        maica.MaicaAiStatus.MODEL_NOT_FOUND: u"选择的 model 不正确",
        maica.MaicaAiStatus.TOKEN_MAX_EXCEEDED:u"session 已超过 28672 token, 可能有部分对话已被删除",
        maica.MaicaAiStatus.TOKEN_24000_EXCEEDED:u"session 已超过 24576 token, 如需要历史记录请及时保存, 对话可能已删除过",
        maica.MaicaAiStatus.WSS_CLOSED_UNEXCEPTED:u"websocket异常关闭, 查看log以获取详细信息"
    }