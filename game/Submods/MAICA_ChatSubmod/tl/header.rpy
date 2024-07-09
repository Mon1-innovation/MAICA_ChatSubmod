# TODO: Translation updated at 2024-07-07 20:52

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:140
    old "未连接"
    new "Not connected"

    # game/Submods/MAICA_ChatSubmod/header.rpy:140
    old "已连接"
    new "Connection established"

    # game/Submods/MAICA_ChatSubmod/header.rpy:140
    old "已断开"
    new "Connection closed"

    # game/Submods/MAICA_ChatSubmod/header.rpy:147
    old "> MAICA通信状态: [maica.maica.status]|[maica.maica.MaicaAiStatus.get_description(maica.maica.status)]"
    new "> MAICA connection status: [maica.maica.status]|[maica.maica.MaicaAiStatus.get_description(maica.maica.status)]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:151
    old "> Websocket:[stat]"
    new "> Websocket:[stat]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:157
    old "> 生成令牌"
    new "> Generate token"

    # game/Submods/MAICA_ChatSubmod/header.rpy:160
    old "> 使用已保存令牌连接"
    new "> Connect with current token"

    # game/Submods/MAICA_ChatSubmod/header.rpy:165
    old "上传存档信息"
    new "> Upload savefile information"

    # game/Submods/MAICA_ChatSubmod/header.rpy:168
    old "重置当前对话"
    new "> Purge current session"

    # game/Submods/MAICA_ChatSubmod/header.rpy:171
    old "导出当前对话"
    new "> Export current session"

    # game/Submods/MAICA_ChatSubmod/header.rpy:174
    old "退出当前DCC账号"
    new "> Lougout current account"

    # game/Submods/MAICA_ChatSubmod/header.rpy:177
    old "> MAICA对话设置 *部分选项需要重新连接"
    new "> MAICA chat settings *some options may require reconnection to take effect"

    # game/Submods/MAICA_ChatSubmod/header.rpy:201
    old "累计对话轮次: [store.maica.maica.stat.get('message_count')]"
    new "Total conversation rounds: [store.maica.maica.stat.get('message_count')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:204
    old "累计收到Token: [store.maica.maica.stat.get('received_token')]"
    new "Total tokens recieved: [store.maica.maica.stat.get('received_token')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:206
    old "重置统计数据"
    new "Reset statistics"

    # game/Submods/MAICA_ChatSubmod/header.rpy:211
    old "自动重连: [persistent.maica_setting_dict.get('auto_connect')]"
    new "Auto reconnect: [persistent.maica_setting_dict.get('auto_connect')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:213
    old "连接断开时自动重连"
    new "Automatically reconnect on connection close"

    # game/Submods/MAICA_ChatSubmod/header.rpy:216
    old "当前MAICA模型: [persistent.maica_setting_dict.get('maica_model')]"
    new "Current MAICA model: [persistent.maica_setting_dict.get('maica_model')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:218
    old "maica_main：完全能力模型，maica_core: 核心能力模型\n完全能力的前置响应延迟偏高"
    new "maica_main: MAICA full functionality; maica_core: MAICA LLM functionality\nmaica_main has a higher response latency"

    # game/Submods/MAICA_ChatSubmod/header.rpy:222
    old "目标语言: [persistent.maica_setting_dict.get('target_lang')]"
    new "Target language: [persistent.maica_setting_dict.get('target_lang')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:224
    old "你与莫妮卡的沟通语言\n通过system prompt实现, 不能保证输出语言严格正确"
    new "The language you prefer recieving\nAchieved by modding system prompt, cannot guarantee correct output"

    # game/Submods/MAICA_ChatSubmod/header.rpy:229
    old "使用高级参数: [persistent.maica_setting_dict.get('use_custom_model_config')]"
    new "Use advanced parameters: [persistent.maica_setting_dict.get('use_custom_model_config')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:231
    old "在使用前, 请务必查看子模组根目录的custom_modelconfig.json\n否则可能导致意料之外的问题\n子模组将读取该json作为对话参数"
    new "Make sure config file custom_modelconfig.json makes sense before use"

    # game/Submods/MAICA_ChatSubmod/header.rpy:234
    old "刷新参数"
    new "Flush options"

    # game/Submods/MAICA_ChatSubmod/header.rpy:238
    old "使用存档数据: [persistent.maica_setting_dict.get('sf_extraction')]"
    new "Use persistent file: [persistent.maica_setting_dict.get('sf_extraction')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:240
    old "关闭时, 模型将不会使用存档数据\n在开启前请务必先上传存档"
    new "Decides if use uploaded savefile or not\nMust have savefile uploaded if set to on"

    # game/Submods/MAICA_ChatSubmod/header.rpy:244
    old "当前使用会话: [persistent.maica_setting_dict.get('chat_session')]"
    new "Session currently in use: [persistent.maica_setting_dict.get('chat_session')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:246
    old "chat_session为0为单轮对话模式, 不同的对话之间相互独立, 需要分别上传存档"
    new "Disable session storage by setting chat_session 0. Sessions use savefiles individually"

    # game/Submods/MAICA_ChatSubmod/header.rpy:250
    old "输出到控制台: [persistent.maica_setting_dict.get('console')]"
    new "Debugging console: [persistent.maica_setting_dict.get('console')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:252
    old "在对话期间是否使用console显示相关信息, wzt的癖好\n说谁呢, 不觉得这很酷吗"
    new "Show debugging console while chatting\nI think this looks cool xd"

    # game/Submods/MAICA_ChatSubmod/header.rpy:256
    old "清除玩家补充信息: 当前共有[len(persistent.mas_player_additions)]条"
    new "Purge additional player preferences: currently [len(persistent.mas_player_additions)]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:258
    old "由你补充的一些数据"
    new "Player complemented preferences data"

    # game/Submods/MAICA_ChatSubmod/header.rpy:261
    old "导出至根目录"
    new "Export to game root directory"

    # game/Submods/MAICA_ChatSubmod/header.rpy:263
    old "导出至game/Submods/MAICA_ChatSubmod/player_information.txt"
    new "Export to game/Submods/MAICA_ChatSubmod/player_information.txt"

    # game/Submods/MAICA_ChatSubmod/header.rpy:270
    old "保存设置"
    new "Save settings"

    # game/Submods/MAICA_ChatSubmod/header.rpy:292
    old "输入 DCC 账号用户名"
    new "Enter DCC username "

    # game/Submods/MAICA_ChatSubmod/header.rpy:294
    old "或"
    new "or "

    # game/Submods/MAICA_ChatSubmod/header.rpy:295
    old "输入 DCC 账号邮箱"
    new "enter DCC register email"

    # game/Submods/MAICA_ChatSubmod/header.rpy:296
    old "请输入DCC 账号邮箱"
    new "Enter DCC register email"

    # game/Submods/MAICA_ChatSubmod/header.rpy:299
    old "输入 DCC 账号密码"
    new "Enter DCC password"

    # game/Submods/MAICA_ChatSubmod/header.rpy:300
    old "请输入DCC 账号密码"
    new "Enter DCC password"

    # game/Submods/MAICA_ChatSubmod/header.rpy:305
    old "连接至服务器生成MAICA令牌"
    new "Generate token online"

    # game/Submods/MAICA_ChatSubmod/header.rpy:312
    old "生成MAICA令牌"
    new "Generate token"

    # game/Submods/MAICA_ChatSubmod/header.rpy:318
    old "取消"
    new "Cancel"

# TODO: Translation updated at 2024-07-09 18:46

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:99
    old "上传成功"
    new "Upload success"

    # game/Submods/MAICA_ChatSubmod/header.rpy:99
    old "上传失败"
    new "Upload failed"

    # game/Submods/MAICA_ChatSubmod/header.rpy:140
    old "加载高级参数失败, 查看submod_log.log来获取详细原因"
    new "Failed initializing advanced params, check submod_log.log"

    # game/Submods/MAICA_ChatSubmod/header.rpy:220
    old "自动重连: [persistent.maica_setting_dict.get('auto_reconnect')]"
    new "Auto reconnect: [persistent.maica_setting_dict.get('auto_reconnect')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:264
    old "控制台字体: [persistent.maica_setting_dict.get('console_font')]"
    new "Console font: [persistent.maica_setting_dict.get('console_font')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:266
    old "console使用的字体\nmplus-1mn-medium.ttf为默认字体\nSarasaMonoTC-SemiBold.ttf对于非英文字符有更好的显示效果"
    new "Decides what font should console display in. mplus-1mn-medium.ttf for default, SarasaMonoTC-SemiBold.ttf may behave better with non-ascii characters."

    # game/Submods/MAICA_ChatSubmod/header.rpy:272
    old "由你补充的一些数据, 增删后需要重新上传存档"
    new "User defined preference data, needs re-uploading savefile to take effect"

    # game/Submods/MAICA_ChatSubmod/header.rpy:276
    old "增加信息"
    new "Add preference"

    # game/Submods/MAICA_ChatSubmod/header.rpy:277
    old "增加信息的事件将于关闭设置后推送"
    new "Preference addition will be sent on closing settings"

    # game/Submods/MAICA_ChatSubmod/header.rpy:282
    old "点击后将推送相关事件"
    new "Click me to push events"

    # game/Submods/MAICA_ChatSubmod/header.rpy:329
    old "请输入DCC 账号用户名"
    new "Enter DCC account username"

