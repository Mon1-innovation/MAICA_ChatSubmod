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
    old "> Websocket: [stat]"
    new "> Websocket: [stat]"

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
    new "> Reset current session"

    # game/Submods/MAICA_ChatSubmod/header.rpy:171
    old "导出当前对话"
    new "> Export current session"

    # game/Submods/MAICA_ChatSubmod/header.rpy:174
    old "退出当前DCC账号"
    new "> Lougout current account"

    # game/Submods/MAICA_ChatSubmod/header.rpy:177
    old "> MAICA参数与设置 *部分选项需要重新连接"
    new "> MAICA params and settings *some options may need reconnection"

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
    new "Export to directory"

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
    new "Enter DCC register email"

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
    new "Decides what font should console display in. \nmplus-1mn-medium.ttf for default, SarasaMonoTC-SemiBold.ttf may behave better with non-ascii characters."

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

# TODO: Translation updated at 2024-07-11 22:18

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:289
    old "编辑信息"
    new "Edit information"

    # game/Submods/MAICA_ChatSubmod/header.rpy:306
    old "MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"
    new "MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:308
    old "是否允许由MSpire生成的对话, MSpire不受MFocus影响, 需要关闭重复对话"
    new "Enable or disable MSpire topics generation. Turn off repetive conversation to take effect."

    # game/Submods/MAICA_ChatSubmod/header.rpy:311
    old "对话范围编辑"
    new "Edit topic range"

    # game/Submods/MAICA_ChatSubmod/header.rpy:317
    old "范围为维基百科的category页面"
    new "The range should be the title of a wikipedia category page"

    # game/Submods/MAICA_ChatSubmod/header.rpy:320
    old "间隔: [persistent.maica_setting_dict.get('mspire_interval')]分钟"
    new "Interval: [persistent.maica_setting_dict.get('mspire_interval')] Minute(s)"

    # game/Submods/MAICA_ChatSubmod/header.rpy:325
    old "MSpire对话的最低间隔分钟"
    new "The minimum interval triggering MSpire"

    # game/Submods/MAICA_ChatSubmod/header.rpy:330
    old "submod_log.log 等级:[logging.getLevelName(store.mas_submod_utils.submod_log.level)]"
    new "submod_log.log verbosity: [logging.getLevelName(store.mas_submod_utils.submod_log.level)]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:332
    old "这将影响submod_log.log中每条log的等级, 低于该等级的log将不会记录\n这也会影响其他子模组"
    new "Filter lower level logs\nThis affects every installed submod"

# TODO: Translation updated at 2024-08-04 13:15

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:280
    old "{a=https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Document.txt#L81}{i}{u}MAICA 官方文档{/i}{/u}{/a}"
    new "{a=https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Document.txt#L81}{i}{u}Official document of MAICA API{/i}{/u}{/a}"

    # game/Submods/MAICA_ChatSubmod/header.rpy:282
    old "{a=https://www.openaidoc.com.cn/api-reference/chat}{i}{u}OPENAI 中文文档{/i}{/u}{/a}"
    new "{a=https://platform.openai.com/docs/api-reference/chat}{i}{u}OPENAI documents{/i}{/u}{/a}"

    # game/Submods/MAICA_ChatSubmod/header.rpy:287
    old "模型选择的范围, 模型考虑概率质量值在前 top_p 的标记的结果, 因此，0.1 意味着仅考虑概率质量值前 10% 的标记"
    new "The token choice range in sequence of probability. Model will only choose the next token from the top_p/1 former part of all tokens."

    # game/Submods/MAICA_ChatSubmod/header.rpy:301
    old "模型输出的随机性, 较高的值会使输出更随机, 而较低的值则会使其更加专注和确定"
    new "The randomness of output. Temperature was added to token weights to dilute their default probabilities, so higher temperature suggests creativity and lower suggests precision."

    # game/Submods/MAICA_ChatSubmod/header.rpy:312
    old "模型输出的长度限制, 较高的值会使输出更长"
    new "The max length model can output in a single round. Model will try to fit this value but oversized responses will be chopped."

    # game/Submods/MAICA_ChatSubmod/header.rpy:324
    old "频率惩罚, 正值基于新标记在文本中的现有频率对其进行惩罚, 降低模型重复相同行的可能性"
    new "Higher Frequency penalty prevents model from repeating one pattern for times. Minimum was limited to 0.2 by MAICA to avoid catastrophic repetition."

    # game/Submods/MAICA_ChatSubmod/header.rpy:336
    old "正值基于新标记出现在文本中的情况对其进行惩罚, 增加模型谈论新话题的可能性"
    new "Higher Presence penalty prevents model from repeating the input, enhances the possibility of topic switching."

    # game/Submods/MAICA_ChatSubmod/header.rpy:358
    old "0时只调用MFocus直接选择的工具. 当其为1时总是会调用时间与节日工具. 当其为2时还会额外调用日期工具.\n为2时, 且mas_geolocation存在, tnd_aggressive还会额外调用当前天气工具.\n可能补偿MFocus命中率低下的问题, 但也可能会干扰模型对部分问题的判断."
    new "Set 0 for no MFocus enforcing. Set 1 for enforcing time and events. Set 2 for enforcing time, date, events and weather(if possible). May offset low MFocus hit rate but may also cause misunderstanding of queries."

    # game/Submods/MAICA_ChatSubmod/header.rpy:372
    old "总是尽可能使用MFocus的最终输出替代指导构型信息. 启用此功能可能提升模型的复杂信息梳理能力 \n但也可能会造成人称或格式的混乱"
    new "Set true for always using MFocus final answer instead of combined instructs if possible. May improve capability of concluding information but may also result in confusion in personality and response format."

    # game/Submods/MAICA_ChatSubmod/header.rpy:377
    old "指定sfe_aggressive为true将总是以用户的真名替代prompt中的[[player]字段. \n启用此功能可能有利于模型理解玩家的姓名, 但也可能会造成总体拟合能力的下降和信息编造"
    new "Set true for always using player name in place of [[player]s in prompts. May help model understanding player's name but may also result in overall performance decline and information makeups."

    # game/Submods/MAICA_ChatSubmod/header.rpy:382
    old "当esc_aggressive为true时会调用agent模型对MFocus联网搜集的信息整理一次.\n 启用此功能会改善模型对联网检索信息的专注能力, 但也会降低涉及联网搜索query的响应速度."
    new "Set true for concluding internet information gathered by AgentLM again. Helps model focusing on search results but will lag specific responses."

    # game/Submods/MAICA_ChatSubmod/header.rpy:470
    old "累计MSpire轮次: [store.maica.maica.stat.get('mspire_count')]"
    new "Total MSpire rounds: [store.maica.maica.stat.get('mspire_count')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:501
    old "高级参数会大幅影响模型的表现"
    new "Advanced params can impact model performance severely, use with extreme care."

    # game/Submods/MAICA_ChatSubmod/header.rpy:504
    old "设置高级参数"
    new "Adjust advanced params"

    # game/Submods/MAICA_ChatSubmod/header.rpy:510
    old "关闭时, 模型将不会使用存档数据\n每次重启游戏将自动上传存档"
    new "Set false for not uploading savefiles. Savefile is uploaded on game launching by default."

    # game/Submods/MAICA_ChatSubmod/header.rpy:569
    old "间隔"
    new "Frequency"

    # game/Submods/MAICA_ChatSubmod/header.rpy:577
    old "[persistent.maica_setting_dict.get('mspire_interval')]分钟"
    new "[persistent.maica_setting_dict.get('mspire_interval')] minutes"

    # game/Submods/MAICA_ChatSubmod/header.rpy:579
    old "使用会话: [persistent.maica_setting_dict.get('mspire_session')]"
    new "Using session: [persistent.maica_setting_dict.get('mspire_session')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:584
    old "MSpire所使用的会话\nMSpire使用过多可能会导致模型定位混乱"
    new "Use chat session for MSpire\nMay lead to response pattern corruption."
    
# TODO: Translation updated at 2024-09-30 08:15

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:96
    old "验证失败, 请检查账号密码"
    new "Authentication failed, recheck your account and password"

    # game/Submods/MAICA_ChatSubmod/header.rpy:98
    old "验证成功"
    new "Authentication passed"

    # game/Submods/MAICA_ChatSubmod/header.rpy:143
    old "验证成功{#maica_location}"
    new "Verification passed"

    # game/Submods/MAICA_ChatSubmod/header.rpy:147
    old "已导出至game/Submods/MAICA_ChatSubmod/chat_history.txt"
    new "Exported to game/Submods/MAICA_ChatSubmod/chat_history.txt"

    # game/Submods/MAICA_ChatSubmod/header.rpy:175
    old "正在上传设置"
    new "Uploading settings"

    # game/Submods/MAICA_ChatSubmod/header.rpy:175
    old "不能上传设置, 请等待MAICA准备好聊天\n请等待状态码改变后手动上传设置"
    new "Please ensure connection is ready first"

    # game/Submods/MAICA_ChatSubmod/header.rpy:275
    old "> 警告: 与 Better Loading 不兼容"
    new "> Warning: Blessland is not compatible with Better Loading"

    # game/Submods/MAICA_ChatSubmod/header.rpy:298
    old "> 手动上传设置"
    new "> Upload settings"

    # game/Submods/MAICA_ChatSubmod/header.rpy:301
    old "> 手动上传设置 [[不能上传, 因为MAICA未准备好/忙碌中]"
    new "> Upload settings [[Ensure connection ready first]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:304
    old "> 重置当前对话"
    new "> Reset current chat session"

    # game/Submods/MAICA_ChatSubmod/header.rpy:307
    old "> 导出当前对话"
    new "> Export current conversation history"

    # game/Submods/MAICA_ChatSubmod/header.rpy:310
    old "> 退出当前DCC账号"
    new "> Logout"

    # game/Submods/MAICA_ChatSubmod/header.rpy:356
    old " <官方服务>"
    new " <Official>"

    # game/Submods/MAICA_ChatSubmod/header.rpy:359
    old "说明: "
    new "Intro: "

    # game/Submods/MAICA_ChatSubmod/header.rpy:361
    old "当前模型: "
    new "Model: "

    # game/Submods/MAICA_ChatSubmod/header.rpy:365
    old "> 使用该节点"
    new "> Switch to provider"

    # game/Submods/MAICA_ChatSubmod/header.rpy:372
    old "更新节点列表"
    new "Refresh providers list"

    # game/Submods/MAICA_ChatSubmod/header.rpy:376
    old "关闭"
    new "Close"

    # game/Submods/MAICA_ChatSubmod/header.rpy:520
    old "当nsfw_acceptive为true时会改变system指引, 使模型对NSFW场景更为宽容.\n 启用此功能可能提高特定场合表现, 但也可能会造成模型核心能力下降和注意力混乱.\n请注意, 目前为止MAICA尚未使用任何NSFW数据集进行训练, 因此nsfw_acceptive的效果十分薄弱.\n 此后或许会有针对性的改善."
    new "Enabling may improve performance in particular occasion.\nBut also may result in overall performance decrease."

    # game/Submods/MAICA_ChatSubmod/header.rpy:605
    old "服务提供节点: [store.maica.maica.provider_manager.get_server_info().get('name', 'Unknown')]"
    new "Current provider: [store.maica.maica.provider_manager.get_server_info().get('name', 'Unknown')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:607
    old "设置服务器节点"
    new "Choose provider"

    # game/Submods/MAICA_ChatSubmod/header.rpy:695
    old "范围为维基百科的category页面\n如果无法找到catrgory将会提示错误输入"
    new "Accepts existing categories of wikipedia\nWill fail if category doesn't exist"

    # game/Submods/MAICA_ChatSubmod/header.rpy:750
    old "重置设置"
    new "Reset defaults"

    # game/Submods/MAICA_ChatSubmod/header.rpy:751
    old "设置已重置"
    new "Reset finished"

    # game/Submods/MAICA_ChatSubmod/header.rpy:776
    old "改为用户名登录"
    new "Use username instead"

    # game/Submods/MAICA_ChatSubmod/header.rpy:781
    old "改为邮箱登录"
    new "Use Email instead"


# TODO: Translation updated at 2024-11-14 17:15

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:2
    old "MAICA官方前端子模组"
    new "MAICA Official Submod Frontend"

    # game/Submods/MAICA_ChatSubmod/header.rpy:275
    old "> 无法验证版本号, 如果出现问题请更新至最新版"
    new "> Cannot verify version, try updating submod yourself if problems encountered"

    # game/Submods/MAICA_ChatSubmod/header.rpy:280
    old "> 当前版本已不再支持, 请更新至最新版"
    new "> Support has ended for current version, please update submod"

    # game/Submods/MAICA_ChatSubmod/header.rpy:331
    old "> 更新日志与服务状态"
    new "> Changelogs and serving status"

    # game/Submods/MAICA_ChatSubmod/header.rpy:878
    old "※ 使用MAICA Blessland, 即认为你同意 {a=https://maica.monika.love/tos_zh}{i}{u}MAICA服务条款{/i}{/u}{/a}"
    new "※ By using MAICA Blessland, you have acknowledged and agree to obey {a=https://maica.monika.love/tos_en}{i}{u}MAICA TOS{/i}{/u}{/a}"

    # game/Submods/MAICA_ChatSubmod/header.rpy:950
    old "算了"
    new "Nevermind"

    # game/Submods/MAICA_ChatSubmod/header.rpy:954
    old "粘贴"
    new "Paste"

# TODO: Translation updated at 2024-11-22 18:00

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:349
    old "> 更新日志与服务状态 {size=-10}*有新更新"
    new "> Update and service status tracker {size=-10}* Update available"

    # game/Submods/MAICA_ChatSubmod/header.rpy:459
    old "√ 已启用"
    new "√ Enabled"

    # game/Submods/MAICA_ChatSubmod/header.rpy:462
    old "× 已禁用"
    new "× Disabled"

    # game/Submods/MAICA_ChatSubmod/header.rpy:466
    old "※ 当前不满足触发条件"
    new "※ Trigger condition not satisfied"

    # game/Submods/MAICA_ChatSubmod/header.rpy:555
    old "{a=https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Document.txt}{i}{u}MAICA 官方文档{/i}{/u}{/a}"
    new "{a=https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Document.txt}{i}{u}MAICA Official API references{/i}{/u}{/a}"

    # game/Submods/MAICA_ChatSubmod/header.rpy:559
    old "{size=-10}注意: 只有已被勾选(标记了X)的高级设置才会被使用, 未使用的设置将使用服务端的默认设置"
    new "{size=-10}Notice: Only checked (X) advanced settings will take effect, unchecked ones will remain default"

    # game/Submods/MAICA_ChatSubmod/header.rpy:562
    old "{size=-10}你当前未启用'使用高级参数', 该页的所有设置都不会生效!"
    new "{size=-10}You have not enabled advanced parameters, thus settings on this page will not take effect!"

    # game/Submods/MAICA_ChatSubmod/header.rpy:567
    old "{size=-10}================超参数================"
    new "{size=-10}================Super params================"

    # game/Submods/MAICA_ChatSubmod/header.rpy:640
    old "{size=-10}================偏好================"
    new "{size=-10}================Preferences================"

    # game/Submods/MAICA_ChatSubmod/header.rpy:678
    old "相当于pre_additive数值轮次的历史对话将被加入MFocus.\n此功能强度越高, 越可能提高MFocus在自然对话中的触发率, 但也越可能干扰MFocus的判断或导致其表现异常."
    new "Rounds equal to pre_additive value will be added for MFocus to analyze.\nMay improve MFocus accuracy performance, but may also result in misbehavior."

    # game/Submods/MAICA_ChatSubmod/header.rpy:689
    old "相当于post_additive数值轮次的历史对话将被加入MTrigger.\n此功能强度越高, 越可能提高MTrigger在自然对话中的触发率, 但也越可能干扰MTrigger的判断或导致其表现异常."
    new "Rounds equal to post_additive value will be added for MTrigger to analyze.\nMay improve MTrigger accuracy performance, but may also result in misbehavior."

    # game/Submods/MAICA_ChatSubmod/header.rpy:701
    old "当amt_aggressive为true时会要求MFocus预检MTrigger内容(若存在), 以告知核心模型要求是否可以完成. \n启用此功能会改善MTrigger与核心模型的表现失步问题, 但也会降低涉及MTrigger对话的响应速度.\n当对话未使用MTrigger或仅有好感触发器, 此功能不会生效."
    new "Set to true to pre-analyze MTrigger items by MFocus(if both exists) to inform core model if request could be done. \nMay improve synchronousity of MTrigger, but also increases delay."

    # game/Submods/MAICA_ChatSubmod/header.rpy:786
    old "每个会话累计Token: [store.maica.maica.stat.get('received_token_by_session')]"
    new "Overall tokens recieved: [store.maica.maica.stat.get('received_token_by_session')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:789
    old "当前用户: [store.maica.maica.user_acc]"
    new "Current user: [store.maica.maica.user_acc]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:840
    old "会话长度: "
    new "Chat session length: "

    # game/Submods/MAICA_ChatSubmod/header.rpy:845
    old "此参数意在缓解对话历史累积导致的响应速度过慢问题. 请避免将其设置得过小, 否则可能影响模型的正常语言能力."
    new "This setting is intended to reduce performance issue when history goes too long. Choose a reasonable value or model coherence may be impacted."

    # game/Submods/MAICA_ChatSubmod/header.rpy:847
    old "[persistent.maica_setting_dict.get('max_history_token')]"
    new "[persistent.maica_setting_dict.get('max_history_token')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:850
    old "上传对话历史到会话 [store.maica.maica.chat_session]"
    new "Recover history to chat session [store.maica.maica.chat_session]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:930
    old "MTrigger列表"
    new "Mtrigger triggers list"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1019
    old "{size=-10}※ 使用MAICA Blessland, 即认为你同意 {a=https://maica.monika.love/tos_zh}{i}{u}MAICA服务条款{/i}{/u}{/a}"
    new "{size=-10}※ By using MAICA Blessland, you agree to {a=https://maica.monika.love/tos_en}{i}{u}MAICA TOS{/i}{/u}{/a}"

# TODO: Translation updated at 2024-11-28 07:51

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:155
    old "未找到game/Submods/MAICA_ChatSubmod/chat_history.txt"
    new "game/Submods/MAICA_ChatSubmod/chat_history.txt not found"

    # game/Submods/MAICA_ChatSubmod/header.rpy:190
    old "暂未上传设置, 请等待MAICA准备好聊天\n待状态码改变后手动上传设置"
    new "Please ensure connection is ready before uploading settings"

    # game/Submods/MAICA_ChatSubmod/header.rpy:308
    old "> 警告: 与 Log Screen 一起使用时, 请将'submod_log'的详细程度提高至info及以上"
    new "> Warning: set 'submod_log' logger verbosity to 'info' or lower when using with Log Screen"

    # game/Submods/MAICA_ChatSubmod/header.rpy:336
    old "> 手动上传设置 [[请先使MAICA完成连接]"
    new "> Manually upload settings [[Ensure connection is ready first]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:345
    old "> 上传对话历史到会话 [store.maica.maica.chat_session]"
    new "> Upload chat history to session [store.maica.maica.chat_session]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:353
    old "> MAICA参数与设置 {size=-10}*部分选项重新连接生效"
    new "> MAICA params and settings {size=-10}*May need restarting to take effect"

    # game/Submods/MAICA_ChatSubmod/header.rpy:628
    old "重现惩罚, 正值基于新标记出现在文本中的情况对其进行惩罚, 增加模型谈论新话题的可能性"
    new "Higher Presence penalty prevents model from repeating the input, enhances the possibility of topic switching."

    # game/Submods/MAICA_ChatSubmod/header.rpy:653
    old "当其为0时只调用MFocus直接选择的工具. 为1时总是会调用时间与节日工具. 为2时还会额外调用日期工具.\n当其为2且mas_geolocation存在时, tnd_aggressive还会额外调用当前天气工具.\n越高越可能补偿MFocus命中率低下的问题, 但也越可能会干扰模型对部分问题的判断."
    new "Set 0 for no MFocus enforcing. Set 1 for enforcing time and events.\nSet 2 for enforcing time, date, events and weather(if possible).\nMay offset low MFocus hit rate but may also cause misunderstanding of queries."

    # game/Submods/MAICA_ChatSubmod/header.rpy:665
    old "总是尽可能使用MFocus的最终输出替代指导构型信息.\n启用可能提升模型的复杂信息梳理能力, 但也可能会造成速度下降或专注扰乱"
    new "Set true for always using MFocus final answer instead of combined instructs if possible.\nMay improve capability of concluding information but may also result in confusion in personality and response format."

    # game/Submods/MAICA_ChatSubmod/header.rpy:670
    old "总是以用户的真名替代prompt中的[[player]字段.\n启用此功能可能有利于模型理解玩家的姓名, 但也可能会造成总体拟合能力的下降和信息编造"
    new "Set true for always using player name in place of [[player]s in prompts.\nMay help model understanding player's name but may also result in overall performance decline and information makeups."

    # game/Submods/MAICA_ChatSubmod/header.rpy:675
    old "调用agent模型对MFocus联网搜集的信息整理一次.\n启用此功能会改善模型对联网检索信息的专注能力, 但也会降低涉及联网搜索query的响应速度."
    new "Set true for concluding internet information gathered by AgentLM again.\nHelps model focusing on search results but will lag specific responses."

    # game/Submods/MAICA_ChatSubmod/header.rpy:680
    old "要求MFocus预检MTrigger内容(若存在), 以告知核心模型要求是否可以完成. \n启用此功能会改善MTrigger与核心模型的表现失步问题, 但也会降低涉及MTrigger对话的响应速度.\n当对话未使用MTrigger或仅有好感触发器, 此功能不会生效."
    new "Set true to request MFocus pre-analyzing MTrigger triggers on query's possibility.\nMay benefit on core-trigger sync but will lag specific responses.\nWill not take effect if no trigger aside from affection is activated."

    # game/Submods/MAICA_ChatSubmod/header.rpy:685
    old "改变system指引, 使模型对NSFW场景更为宽容.\n经测试启用此功能对模型总体表现(意外地)有利, 但也存在降低模型专注能力和造成混乱的风险."
    new "Set true to guide core model being more tolerant on toxic scenes.\nMay improve overall core performance (unexpectedly but proved true)\n but may also decrease attention performance and cause confusion."

# TODO: Translation updated at 2024-11-29 20:06

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:141
    old "MAICA: 存档上传成功"
    new "MAICA: Savefile uploaded successfully"

    # game/Submods/MAICA_ChatSubmod/header.rpy:141
    old "MAICA: 存档上传失败"
    new "MAICA; Savefile failed to upload"

    # game/Submods/MAICA_ChatSubmod/header.rpy:145
    old "MAICA: 会话已重置"
    new "MAICA: Chat session reset"

    # game/Submods/MAICA_ChatSubmod/header.rpy:150
    old "MAICA: 历史已导出至game/Submods/MAICA_ChatSubmod/chat_history.txt"
    new "MAICA: History exported to game/Submods/MAICA_ChatSubmod/chat_history.txt"

    # game/Submods/MAICA_ChatSubmod/header.rpy:155
    old "MAICA: 未找到历史game/Submods/MAICA_ChatSubmod/chat_history.txt"
    new "MAICA: History not found at game/Submods/MAICA_ChatSubmod/chat_history.txt"

    # game/Submods/MAICA_ChatSubmod/header.rpy:160
    old "MAICA: 历史上传成功"
    new "MAICA: History uploaded"

    old "MAICA: 历史上传失败, 查看submod_log获取详细原因."
    new "MAICA: Failed to upload history, check submod_log.log for details."

    # game/Submods/MAICA_ChatSubmod/header.rpy:190
    old "MAICA: 已上传设置"
    new "MAICA: Settings uploaded"

    # game/Submods/MAICA_ChatSubmod/header.rpy:190
    old "MAICA: 请等待连接就绪后手动上传"
    new "MAICA: Do a manual upload after connection ready"

    # game/Submods/MAICA_ChatSubmod/header.rpy:223
    old "MAICA: 加载高级参数失败, 查看submod_log.log获取详细原因"
    new "MAICA: Advanced settings failed to serialize, check submod_log.log"

    # game/Submods/MAICA_ChatSubmod/header.rpy:960
    old "MAICA: 设置已重置"
    new "MAICA: Settings reset"

# TODO: Translation updated at 2024-12-02 17:16

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:319
    old "> Websocket: "
    new "> Websocket: "

    # game/Submods/MAICA_ChatSubmod/header.rpy:463
    old "MTrigger空间使用情况: "
    new "MTrigger space usage: "

    # game/Submods/MAICA_ChatSubmod/header.rpy:473
    old "空间占用: -"
    new "Space used: -"

    # game/Submods/MAICA_ChatSubmod/header.rpy:477
    old "空间占用: request"
    new "Space used: request"

    # game/Submods/MAICA_ChatSubmod/header.rpy:483
    old "空间占用: table"
    new "Space used: table"

    # game/Submods/MAICA_ChatSubmod/header.rpy:960
    old "搜索方式: [persistent.maica_setting_dict.get('mspire_search_type')]"
    new "Search type: [persistent.maica_setting_dict.get('mspire_search_type')]"

    old "{size=-10}* 如果对话卡住了, 点我断开连接"
    new "{size=-10}* If chat is stuck, click me to disconnect"

    old "{size=-10}※ 还没有DCC账号? {a=https://forum.monika.love/signup}{i}{u}注册一个{/u}{/i}{/a}"
    new "{size=-10}※ Don't have DCC account yet? {a=https://forum.monika.love/signup}{i}{u}Sign up.{/u}{/i}{/a}"

    old "严格反劫持: [persistent.maica_setting_dict.get('strict_mode')]"
    new "Strict anti-hijack: [persistent.maica_setting_dict.get('strict_mode')]"

# TODO: Translation updated at 2025-02-01 08:24

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:105
    old "失败原因: "
    new "Reason: "

    # game/Submods/MAICA_ChatSubmod/header.rpy:330
    old "> 你当前的MAS构建版本过旧, 可能影响正常运行, 请升级至最新版本"
    new "> Your current MAS version is below the lowest compatible version, please update"

    # game/Submods/MAICA_ChatSubmod/header.rpy:513
    old "> 注意: 当空间不足时将自动关闭部分MTrigger!"
    new "> Notice: Some MTriggers will be disabled if content length exceeds!"

    # game/Submods/MAICA_ChatSubmod/header.rpy:599
    old "{size=15}因能力有限, 阅读信件后信件列表将在返回太空教室后重新显示."
    new "{size=15}MPostal list will be shown after returning to the spaceroom."

    # game/Submods/MAICA_ChatSubmod/header.rpy:606
    old "信件状态: "
    new "MPostal status:"

    # game/Submods/MAICA_ChatSubmod/header.rpy:608
    old "寄信时间: "
    new "Last post sent at: "

    # game/Submods/MAICA_ChatSubmod/header.rpy:610
    old "\n[player]: \n"
    new "\n[player]: \n"

    # game/Submods/MAICA_ChatSubmod/header.rpy:613
    old "[m_name]: \n"
    new "[m_name]: \n"

    # game/Submods/MAICA_ChatSubmod/header.rpy:616
    old "阅读[player]写的信"
    new "Read [player]'s letter"

    # game/Submods/MAICA_ChatSubmod/header.rpy:624
    old "阅读[m_name]的回信"
    new "Read [m_name]'s reply"

    # game/Submods/MAICA_ChatSubmod/header.rpy:992
    old "累计发信数: [store.maica.maica.stat.get('mpostal_count')]"
    new "MPostal sent count: [store.maica.maica.stat.get('mpostal_count')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1015
    old "严格模式下, 将会在每次发送时携带cookie信息"
    new "Strict anti-hijack enables MAICA websocket cookie"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1125
    old "状态码更新速度"
    new "Status code refreshing frequency"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1130
    old "在Submod界面处的状态码更新频率"
    new "The refreshing frequency of status code on Submod screen"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1140
    old "MPostal历史信件"
    new "Reread MPostal letters"

    old "回信时显示控制台"
    new "Show console on MPostal writing reply"

# TODO: Translation updated at 2025-02-17 12:47

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:655
    old "重新寄信"
    new "Resend mail"

    # game/Submods/MAICA_ChatSubmod/header.rpy:721
    old "平均功耗: "
    new "Mean power consumption: "

    # game/Submods/MAICA_ChatSubmod/header.rpy:726
    old "下次更新数据"
    new "Analytics refresh"

    # game/Submods/MAICA_ChatSubmod/header.rpy:836
    old "{size=-10}如果这里没有你的时区, 请根据你当地的UTC时间选择"
    new "{size=-10}If your timezone is not listed here, decide by your local UTC timezone."

    # game/Submods/MAICA_ChatSubmod/header.rpy:839
    old "根据语言自动选择"
    new "Language default"

    # game/Submods/MAICA_ChatSubmod/header.rpy:843
    old "根据系统时区自动选择"
    new "System default"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1141
    old "选择时区: [persistent.maica_advanced_setting.get('tz') or 'Asia/Shanghai' if store.maica.maica.target_lang == store.maica.maica.MaicaAiLang.zh_cn else 'America/Indiana/Vincennes']"
    new "Set timezone: [persistent.maica_advanced_setting.get('tz') or 'Asia/Shanghai' if store.maica.maica.target_lang == store.maica.maica.MaicaAiLang.zh_cn else 'America/Indiana/Vincennes']"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1413
    old "控制台log等级: [logging.getLevelName(store.maica.maica.console_logger.level)]"
    new "Console logging verbosity: [logging.getLevelName(store.maica.maica.console_logger.level)]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1415
    old "这将影响控制台中每条log的等级, 低于该等级的log将不会记录"
    new "Filter lower level logs shown in console"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1440
    old "查看后端负载"
    new "Check server load status"

# TODO: Translation updated at 2025-02-23 15:54

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:1445
    old "信件回复时间"
    new "MPostal reply delay"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1450
    old "回信所需要的最低时间"
    new "The minimum delay before MPostal replies"

# TODO: Translation updated at 2025-04-08 11:52

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:1086
    old "!已启用42seed"
    new "!Seed locked to 42"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1341
    old "锁定最佳实践"
    new "Enforce best practice"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1343
    old "锁定seed为42, 该设置覆盖高级参数中的seed\n启用会完全排除生成中的随机性, 在统计学上稳定性更佳"
    new "Set seed to 42 and override the corresponding advanced section.\nThis removes the randomness in generation completely and performs better statistically."

    # game/Submods/MAICA_ChatSubmod/header.rpy:1426
    old "MSpire使用缓存"
    new "Use cache for MSpire"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1428
    old "启用MSpire缓存, 且使用默认高级参数并固定种子为42\n"
    new "Enable MSpire cache, disable advanced settings and set seed to 42 for MSpire.\n"

# TODO: Translation updated at 2025-05-04 21:00

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:430
    old "> 支持 MAICA"
    new "> Donate for MAICA"

    # game/Submods/MAICA_ChatSubmod/header.rpy:700
    old "首先很感谢你有心捐赠.\n我们收到的捐赠基本上不可能回本, 但你不必有任何压力."
    new "We're grateful for your being willing to donate.\nThe donate will likely never cover our cost, but that's okay anyway."

    # game/Submods/MAICA_ChatSubmod/header.rpy:702
    old "请注意, 向MAICA捐赠不会提供任何特权, 除了论坛捐赠页名单和捐赠徽章."
    new "Please note that donating to MAICA doesn't give you any actual privilege. It's simply donation."

# TODO: Translation updated at 2025-05-09 10:13

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:432
    old "> 向 MAICA 捐赠"
    new "> Donate to MAICA"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1173
    old "!已启用最佳实践"
    new "!Best practice enabled"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1568
    old "动态的天堂树林"
    new "Dynamic Heaven Forest"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1570
    old "使用动态摇曳和改良光影的天堂树林, 略微增加渲染压力. 重启生效\n如果产生显存相关错误, 删减精灵包或禁用此选项"
    new "Use dynamic forest background with improved illumination\nIncreases render consume slightly. Restart to take effect\nRemove some spritepacks or disable this if VRAM overflows"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1684
    old "seed范围错误, 请重新输入种子"
    new "Seed out of range, retry"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1704
    old "请输入种子, 范围为0-99999"
    new "Choose a seed from 0-99999"

# TODO: Translation updated at 2025-09-09 08:20

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:395
    old "> 警告: 找不到证书, 你是不是忘记安装数据包了?"
    new "> Warning: no certification found, check datapack installation"

    # game/Submods/MAICA_ChatSubmod/header.rpy:520
    old "> 打开官网"
    new "> Go to portal page"

    # game/Submods/MAICA_ChatSubmod/header.rpy:537
    old "测试当前节点可用性"
    new "Test current node avaliability"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1451
    old "使用MTrigger: [persistent.maica_setting_dict.get('enable_mt')]"
    new "MTrigger enabled: [persistent.maica_setting_dict.get('enable_mt')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1454
    old "使用MFocus: [persistent.maica_setting_dict.get('enable_mf')]"
    new "MFocus enabled: [persistent.maica_setting_dict.get('enable_mf')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1746
    old "请输入种子(整数)"
    new "Choose a seed (integer)"

# TODO: Translation updated at 2025-09-15 16:02

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:406
    old "> 警告: 与 Log Screen 一起使用时, 请将'submod_log'的过滤级别提高至info及以上"
    new "> Warning: set 'submod_log' logger verbosity to 'info' or lower when using with Log Screen"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1124
    old "token权重过滤范围. 非常不建议动这个"
    new "Token weight filter percentage. Seriously do not touch this"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1137
    old "token选择的随机程度. 数值越高, 模型输出会越偏离普遍最佳情况"
    new "The randomness tokens are chosen. Higher this value, larger the offset between model performance and generally best performance"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1148
    old "模型一轮生成的token数限制. 一般而言不会影响表现, 只会截断超长的部分"
    new "The limit of tokens model can generate one round. Normally don't affect performance, but stops generating on hitting the limit"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1160
    old "token频率惩罚. 数值越高, 反复出现的token越不可能继续出现, 一般会产生更短且更延拓的结果"
    new "Token frequency penalty. Higher this value, less likely repeatedly appeared tokens continue appearing, usually resulting in shorter and more expanding generation"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1172
    old "token重现惩罚. 数值越高, 出现过的token越不可能再次出现, 一般会产生更跳跃的结果"
    new "Token presence penalty. Higher this value, less likely appeared tokens appear again, usually resulting in more jumping generation"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1233
    old "即使MFocus未调用工具, 也提供一些工具的结果.\n+ 其值越高, 越能避免信息缺乏导致的幻觉, 并产生灵活体贴的表现\n- 其值越高, 越有可能产生注意力涣散和专注混乱"
    new "Acquire some information even if not called explicitly.\n+ Higher: keen and less hallucination\n- Higher: higher likeability of distraction and misfocusing"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1245
    old "要求agent模型生成最终指导, 并替代默认MFocus指导.\n+ 信息密度更高, 更容易维持语言自然\n- 表现十分依赖agent模型自身的能力\n- 启用时一般会无效化tnd_aggressive"
    new "Require agent model to generate guidance instead of default MFocus mechanism.\n+ Higher information density and naturalness\n- Heavily depends on agent instruction following behavior\n- Will likely neutralize tnd_aggressive"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1250
    old "将prompt和引导中的[[player]字段替换为玩家真名.\n+ 模型对玩家的名字有实质性理解\n- 明显更容易发生表现离群和专注混乱"
    new "Replace [[player] in prompt with player's real name.\n+ Model has real understanding of player's name\n- Significantly higher likeability of performance offset and degration"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1255
    old "在MFocus调用互联网搜索的情况下, 要求其整理一遍结果.\n+ 大多数情况下信息密度更高, 更容易维持语言自然\n- 涉及互联网搜索时生成速度更慢"
    new "Require MFocus to sort internet search results.\n+ Higher information density and naturalness in most cases\n- Higher time consumption when query involves searching internet"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1261
    old "当MTrigger存在时, 要求MFocus预检玩家的请求并提供指导.\n+ 比较明显地改善MTrigger失步问题\n- 在少数情况下对语言的自然性产生破坏\n* 当对话未使用MTrigger或仅有好感触发器, 此功能不会生效"
    new "Require MFocus to precheck query for MTrigger.\n+ Significantly reduces MTrigger desync\n- Seldom negative impact on naturalness\n* Only works with MTrigger enabled"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1268
    old "要求模型宽容正面地对待有毒内容.\n+ (出乎意料地)在大多数场合下对模型表现有正面作用, 即使不涉及有毒内容\n- 在少数情况下造成意料之外的问题"
    new "Require model to handle toxic content positively and pardonly.\n+ (Suprisingly) benefits overall performance in most cases\n- May lead to unexpected problems in rare cases"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1275
    old "在MFocus介入时, 额外提供上下文以供分析. 范围0-5.\n+ 改善MFocus对连贯对话的理解能力\n- 明显更容易破坏MFocus的应答模式"
    new "Provide history context for MFocus, in range of 0-5 rounds.\n+ Improves MFocus' understanding to serial conversation\n- Significant risk of breaking MFocus reply pattern"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1286
    old "在MTrigger介入时, 额外提供上下文以供分析. 范围0-5.\n+ 改善MTrigger对连贯对话的理解能力\n- 更容易破坏MTrigger的应答模式"
    new "Provide history context for MTrigger, in range of 0-5 rounds.\n+ Improves MTrigger's understanding to serial conversation\n- Risk of breaking MTrigger reply pattern"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1464
    old "ws严格模式: [persistent.maica_setting_dict.get('strict_mode')]"
    new "Websocket strict mode: [persistent.maica_setting_dict.get('strict_mode')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1479
    old "目标生成语言. 仅支持\"zh\"或\"en\".\n* 该参数不能100%保证生成语言是目标语言\n* 该参数影响范围广泛, 包括默认时区, 节日文化等, 并不止目标生成语言. 建议设为你的实际母语\n* 截至文档编纂时为止, MAICA官方部署的英文能力仍然弱于中文"
    new "Target generation language. Supports \"zh\" or \"en\".\n* Does not 100% guarantee generation language\n* This setting also affects default timezone, festivals, culture and more\n* Up to when this was written, MAICA official deployment's English performance is still weaker than Chinese"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1484
    old "使用自定义高级参数: [persistent.maica_setting_dict.get('use_custom_model_config')]"
    new "Enable customized advanced parameters: [persistent.maica_setting_dict.get('use_custom_model_config')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1486
    old "高级参数可能大幅影响模型的表现.\n* 默认的高级参数已经是实践中的普遍最优配置, 不建议启用"
    new "Advanced parameters could significantly affect the model's performance.\n* The default is already the best field-tested config, so it's not suggested to enable this"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1494
    old "锁定seed为42, 该设置覆盖高级参数中的seed.\n* 启用会完全排除生成中的随机性, 在统计学上稳定性更佳, 且更易于复现"
    new "Designate seed to 42, which overrides seed in advanced parameters.\n* Removes randomness in generation, makes performance more stable and reproducable."

    # game/Submods/MAICA_ChatSubmod/header.rpy:1500
    old "关闭时, 模型将不会使用存档数据.\n* 每次重启游戏将自动上传存档数据"
    new "Model will ignore savefile data if this is disabled.\n* MAICA Blessland uploads savefile on each restart automatically"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1506
    old "每个session独立保存和应用对话记录.\n* 设为0以不记录和不使用对话记录(单轮对话)"
    new "Each session stores and applies history context independently.\n* Set to 0 to disable context (single round conversation)"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1514
    old "会话保留的最大长度. 范围512-28672.\n* 按字符数计算. 每3个ASCII字符只占用一个字符长度\n* 字符数超过限制后, MAICA会裁剪其中较早的部分, 直至少于限制的 2/3\n* 过大或过小的值可能导致表现和性能问题"
    new "Max length each session will preserve, in range of 512-28672.\n* Every 3 ASCII characters occupy one space\n* MAICA crops the former part of context on exceeding to no more than 2/3 left\n* Too high or too low value can cause performance and generation quality issues"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1579
    old "启用MSpire缓存.\n* 会强制使用默认高级参数并固定最佳实践"
    new "Enable MSpire cache.\n* Forces default super params and best practice"

# TODO: Translation updated at 2025-09-23 23:29

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:329
    old "MAICA: 已放弃设置修改"
    new "MAICA: Settings discarded"

    # game/Submods/MAICA_ChatSubmod/header.rpy:503
    old "> 未能联网验证版本信息, 如果出现问题请尝试更新"
    new "> Couldn't acquire online version stream, please check updates manually"

    # game/Submods/MAICA_ChatSubmod/header.rpy:509
    old "> 当前版本支持已终止, 请更新至最新版"
    new "> Support for current version has ended, an update is required"

    # game/Submods/MAICA_ChatSubmod/header.rpy:541
    old "> 使用账号生成令牌"
    new "> Generate token from account"

    # game/Submods/MAICA_ChatSubmod/header.rpy:561
    old "> 手动上传设置 [[请先等待连接建立]"
    new "> Upload settings manually [[wait for connection establishment first]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:563
    old "> 重置当前对话 [[请先等待连接建立]"
    new "> Reset current chat session [[wait for connection establishment first]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:571
    old "{size=-10}* 如果对话卡住, 退出以断开连接"
    new "{size=-10}* If conversation hangs, logout to interrupt"

    # game/Submods/MAICA_ChatSubmod/header.rpy:694
    old "连接与安全"
    new "Connection and Safety"

    # game/Submods/MAICA_ChatSubmod/header.rpy:704
    old "未登录"
    new "Not logged in"

    # game/Submods/MAICA_ChatSubmod/header.rpy:705
    old "当前用户: [user_disp]"
    new "Current user: [user_disp]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:707
    old "如需更换或退出账号, 请在Submods界面退出登录.\n* 要修改账号信息或密码, 请前往注册网站"
    new "To change account or logout, navigate to Submods menu.\n* To change account properties or password, navigate to registration site"

    # game/Submods/MAICA_ChatSubmod/header.rpy:723
    old "行为与表现"
    new "Performance and Behavior"

    # game/Submods/MAICA_ChatSubmod/header.rpy:729
    old "一个agent模型先于核心模型接收相同或相似的输入内容, 并调用工具以获取信息. 这些信息会被提供给核心模型.\n* MFocus是MAICA的重要功能之一, 一般不建议禁用"
    new "An agent model will recieve input prior to the core model, and acquire information with tools.\n* MFocus is a major mechanism of MAICA, suggested to enable"

    # game/Submods/MAICA_ChatSubmod/header.rpy:736
    old "一个agent模型后于核心模型接收本轮的输入输出, 并调用工具以指示前端作出角色行为.\n* MTrigger是MAICA的重要功能之一, 一般不建议禁用"
    new "An agent model will recieve input subsequent to the core model, and guide character's action.\n* MTrigger is a major mechanism of MAICA, suggested to enable"

    # game/Submods/MAICA_ChatSubmod/header.rpy:748
    old "时区设置: [persistent.maica_setting_dict.get('tz')]"
    new "Timezone: [persistent.maica_setting_dict.get('tz')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:782
    old "会话与数据"
    new "Sessions and Data"

    # game/Submods/MAICA_ChatSubmod/header.rpy:792
    old "当前会话"
    new "Current chat session"

    # game/Submods/MAICA_ChatSubmod/header.rpy:796
    old "会话长度"
    new "Chat session length"

    # game/Submods/MAICA_ChatSubmod/header.rpy:807
    old "由你补充的设定信息, 由MFocus检索并呈递到核心模型.\n* 需要重新上传存档生效"
    new "User-provided implementations, handled and sent to core model by MFocus.\n* May need a restart for changes to take effect"

    # game/Submods/MAICA_ChatSubmod/header.rpy:810
    old "当前有[len(persistent.mas_player_additions)]条自定义MFocus信息"
    new "[len(persistent.mas_player_additions)] MFocus info present"

    # game/Submods/MAICA_ChatSubmod/header.rpy:828
    old "编辑MFocus信息"
    new "Edit MFocus info"

    # game/Submods/MAICA_ChatSubmod/header.rpy:847
    old "导出自定义MFocus信息到主目录"
    new "Export MFocus info to main directory"

    # game/Submods/MAICA_ChatSubmod/header.rpy:853
    old "工具与功能"
    new "Tools and Functions"

    # game/Submods/MAICA_ChatSubmod/header.rpy:858
    old "启用MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"
    new "Enable MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:860
    old "是否允许由MSpire生成的对话.\n* 必须关闭复述话题才能启用\n* MSpire话题不使用MFocus和MTrigger"
    new "Enable MSpire to generate vanilla-like conversations.\n* Repeat topics must be disabled to take effect\n* MSpire doesn't use MF/MT"

    # game/Submods/MAICA_ChatSubmod/header.rpy:867
    old "是否允许由MSpire生成的对话.\n! 复述话题已启用, MSpire不会生效"
    new "Enable MSpire to generate vanilla-like conversations.\n! Repeat topice enabled, with which MSpire conflicts"

    # game/Submods/MAICA_ChatSubmod/header.rpy:877
    old "MSpire话题"
    new "MSpire topics"

    # game/Submods/MAICA_ChatSubmod/header.rpy:881
    old "MSpire对话的最小时间间隔"
    new "Minimal interval of MSpire conversations"

    # game/Submods/MAICA_ChatSubmod/header.rpy:882
    old "MSpire最小间隔"
    new "MSpire minimal interval"

    # game/Submods/MAICA_ChatSubmod/header.rpy:887
    old "MSpire搜索方式: [persistent.maica_setting_dict.get('mspire_search_type')]"
    new "MSpire searching method: [persistent.maica_setting_dict.get('mspire_search_type')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:891
    old "MSpire搜索话题的模式"
    new "Way of MSpire searching for topics"

    # game/Submods/MAICA_ChatSubmod/header.rpy:905
    old "查看和配置MTrigger条目"
    new "Configure MTrigger triggers"

    # game/Submods/MAICA_ChatSubmod/header.rpy:921
    old "查看MPostal历史信件"
    new "Reread MPostal history letters"

    # game/Submods/MAICA_ChatSubmod/header.rpy:924
    old "MPostal回信的最小时间间隔"
    new "Minimal interval of MPostal replies"

    # game/Submods/MAICA_ChatSubmod/header.rpy:925
    old "MPostal最小间隔"
    new "MPostal minimal interval"

    # game/Submods/MAICA_ChatSubmod/header.rpy:928
    old "界面与日志"
    new "Interfaces and Log"

    # game/Submods/MAICA_ChatSubmod/header.rpy:932
    old "submod_log.log 等级: [logging.getLevelName(persistent.maica_setting_dict['log_level'])]"
    new "submod_log.log verbosity: [logging.getLevelName(persistent.maica_setting_dict['log_level'])]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:934
    old "重要性低于设置等级的log将不会被记录在submod_log.log中.\n* 这也会影响其他子模组"
    new "Lower level logs will not appear in submod_log.log.\n* This effect is global"

    # game/Submods/MAICA_ChatSubmod/header.rpy:938
    old "状态码更新频率"
    new "Status code update interval"

    # game/Submods/MAICA_ChatSubmod/header.rpy:944
    old "使用动态摇曳和改良光影的天堂树林, 略微增加渲染压力. 重启生效.\n* 如果产生显存相关错误, 删减精灵包或禁用此选项"
    new "Use dynamic forest background with improved illumination, may increase render consumation. Restart to take effect.\n* Remove some spritepacks or disable this if VRAM overflows"

    # game/Submods/MAICA_ChatSubmod/header.rpy:970
    old "控制台log等级: [logging.getLevelName(persistent.maica_setting_dict['log_conlevel'])]"
    new "Console logging verbosity: [logging.getLevelName(persistent.maica_setting_dict['log_conlevel'])]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:972
    old "重要性低于设置等级的log将不会显示在控制台中"
    new "Lower level logs will not appear in console"

    # game/Submods/MAICA_ChatSubmod/header.rpy:980
    old "统计与信息"
    new "Statics and Information"

    # game/Submods/MAICA_ChatSubmod/header.rpy:984
    old "展开性能监控"
    new "Expand performance monitor"

    # game/Submods/MAICA_ChatSubmod/header.rpy:984
    old "收起性能监控"
    new "Retract performance monitor"

    # game/Submods/MAICA_ChatSubmod/header.rpy:988
    old "显示/收起服务器的性能状态指标"
    new "Expand/retract server performance monitor"

    # game/Submods/MAICA_ChatSubmod/header.rpy:998
    old "展开统计数据"
    new "Expand statics"

    # game/Submods/MAICA_ChatSubmod/header.rpy:998
    old "收起统计数据"
    new "Retract statics"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1002
    old "显示/收起你的使用统计数据"
    new "Expand/retract client-side statics"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1019
    old "放弃修改"
    new "Discard modifications"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1025
    old "MAICA: 已重置设置"
    new "MAICA: Settings reset"

# TODO: Translation updated at 2025-09-24 16:28

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:402
    old "MAICA: 信息已导出至game/Submods/MAICA_ChatSubmod/player_information.txt"
    new "MAICA: Exported to game/Submods/MAICA_ChatSubmod/player_information.txt"

# TODO: Translation updated at 2025-09-28 16:56

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:759
    old "地理位置: [persistent.mas_geolocation]"
    new "Geolocation: [persistent.mas_geolocation]"

# TODO: Translation updated at 2025-10-06 22:29

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:543
    old "> 警告: 未检测到MAICA库版本信息. 请从Release下载安装MAICA, 而不是源代码"
    new "> Warning: MAICA Libs version not found. Please install from Release, not source code"

    # game/Submods/MAICA_ChatSubmod/header.rpy:548
    old "> 警告: MAICA库版本[libv]与UI版本[uiv]不符. 请从Release完整地更新MAICA"
    new "> Warning: MAICA Libs v[libv] mismatch with UI v[uiv]. Please fully update from Release"

# TODO: Translation updated at 2025-11-14 17:16

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:788
    old "断点续传: [persistent.maica_setting_dict.get('auto_resume')]"
    new "Generation resume: [persistent.maica_setting_dict.get('auto_resume')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:790
    old "若生成回复时网络中断, 重连后续传丢失的部分"
    new "Resume streaming on reconnection to recover lost chunks"

    # game/Submods/MAICA_ChatSubmod/header.rpy:794
    old "保持连接活跃: [persistent.maica_setting_dict.get('keep_alive')]"
    new "Keep connection active: [persistent.maica_setting_dict.get('keep_alive')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:796
    old "定期发送心跳包保持长连接活跃, 并检测网络延迟"
    new "Send ping packets timely to keep connection alive and calculate lag"

    # game/Submods/MAICA_ChatSubmod/header.rpy:841
    old "会话劣化检测: [persistent.maica_setting_dict.get('dscl_pvn')]"
    new "Session quality review: [persistent.maica_setting_dict.get('dscl_pvn')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:843
    old "对话长度超过3轮后, 在每轮对话结束时, 要求MNerve介入检查输出合理性.\n+ 量化地检测判断会话劣化情况, 以免用户注意不到\n- 产生额外的MNerve开销"
    new "Require MNerve to check generation quality after session exceeds 3 rounds.\n+ Quantitatively evaluate generation quality\n- Extra consumation of MNerve"

    # game/Submods/MAICA_ChatSubmod/header.rpy:985
    old "MVista图片"
    new "MVista images"

    # game/Submods/MAICA_ChatSubmod/header.rpy:987
    old "查看和管理用于MVista的图片.\n* 请仔细阅读TOS, 对你自己的隐私负责"
    new "View and manage MVista images.\n* Please read TOS carefully and be responsible for your own privacy"

    # game/Submods/MAICA_ChatSubmod/header.rpy:995
    old "查看和管理用于MVista的图片.\n! MVista尚未解锁, 请继续和莫妮卡交互或送信, 并耐心等待"
    new "View and manage MVista images.\n! MVista not unlocked, please continue chatting with Monika patiently or send her letters"

    # game/Submods/MAICA_ChatSubmod/header.rpy:1150
    old "选择图片 | 当前已选择 "
    new "Choose images | "

    # game/Submods/MAICA_ChatSubmod/header.rpy:1150
    old " 张"
    new " chosen"

# TODO: Translation updated at 2025-12-05 19:39

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:581
    old "> 警告: 当前系统非Unicode语言不是简体中文, 可能导致包含中文的响应出现问题"
    new "> Warning: Current system 'non-unicode language' is not Chinese, expect possible encoding issues"

# TODO: Translation updated at 2025-12-07 15:44

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:856
    old "实时后处理: [persistent.maica_setting_dict.get('pprt')]"
    new "Realtime post proceeding: [persistent.maica_setting_dict.get('pprt')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:858
    old "启用后端自动断句和实时后处理功能.\n* 非特殊情况不建议关闭"
    new "Enable backend sentence breaking and realtime post proceeding.\n* Suggested to enable in normal cases"

# TODO: Translation updated at 2025-12-19 17:00

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:860
    old "输入语言检测: [persistent.maica_setting_dict.get('input_lang_detect')]"
    new "Input language detection: [persistent.maica_setting_dict.get('input_lang_detect')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:862
    old "检测输入语言与目标生成语言是否相符.\n* 非特殊情况不建议关闭"
    new "Raise a warning if input language is not target language.\n* Suggested to enable in normal cases"

# TODO: Translation updated at 2025-12-22 18:12

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:1167
    old "退出"
    new "Quit"

# TODO: Translation updated at 2026-01-08 02:22

translate english strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:458
    old "MAICA: 已切换节点, 正在重新连接"
    new "MAICA: Provider applied, reconnecting"

