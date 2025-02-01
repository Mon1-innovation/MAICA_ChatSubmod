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
    new "> MAICA chat settings *some options may need reconnection"

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
    old "会话已重置, 请重新连接MAICA服务器"
    new "Session reset, please reconnect to MAICA server"

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
    new "> Warning: is not compatible with Better Loading"

    # game/Submods/MAICA_ChatSubmod/header.rpy:298
    old "> 手动上传设置"
    new "> Upload settings"

    # game/Submods/MAICA_ChatSubmod/header.rpy:301
    old "> 手动上传设置 [[不能上传, 因为MAICA未准备好/忙碌中]"
    new "> Upload settings [[Ensure connection ready first]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:304
    old "> 重置当前对话"
    new "> Purge current chat session"

    # game/Submods/MAICA_ChatSubmod/header.rpy:307
    old "> 导出当前对话"
    new "> Export current conversation history"

    # game/Submods/MAICA_ChatSubmod/header.rpy:310
    old "> 退出当前DCC账号"
    new "> Logout"

    # game/Submods/MAICA_ChatSubmod/header.rpy:356
    old " √ MAICA 官方服务器"
    new " √ Official MAICA provider"

    # game/Submods/MAICA_ChatSubmod/header.rpy:359
    old "设备: "
    new "Cluster: "

    # game/Submods/MAICA_ChatSubmod/header.rpy:361
    old "当前模型: "
    new "Mode: "

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
    old "服务提供节点: [MaicaProviderManager.get_server_by_id(persistent.maica_setting_dict.get('provider_id')).get('name', 'Unknown')]"
    new "Current provider: [MaicaProviderManager.get_server_by_id(persistent.maica_setting_dict.get('provider_id')).get('name', 'Unknown')]"

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
    old "上传对话历史到会话 '[store.maica.maica.chat_session]'"
    new "Recover history to chat session '[store.maica.maica.chat_session]'"

    # game/Submods/MAICA_ChatSubmod/header.rpy:930
    old "MTrigger 列表"
    new "Mtrigger trigger list"

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
    old "> 上传对话历史到会话 '[store.maica.maica.chat_session]'"
    new "> Upload chat history to session '[store.maica.maica.chat_session]'"

    # game/Submods/MAICA_ChatSubmod/header.rpy:353
    old "> MAICA对话设置 {size=-10}*部分选项重新连接生效"
    new "> MAICA chat settings {size=-10}*May need restarting to take effect"

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
    new "MAICA: Chat session purged"

    # game/Submods/MAICA_ChatSubmod/header.rpy:150
    old "MAICA: 历史已导出至game/Submods/MAICA_ChatSubmod/chat_history.txt"
    new "MAICA: History exported to game/Submods/MAICA_ChatSubmod/chat_history.txt"

    # game/Submods/MAICA_ChatSubmod/header.rpy:155
    old "MAICA: 未找到历史game/Submods/MAICA_ChatSubmod/chat_history.txt"
    new "MAICA: History not found at game/Submods/MAICA_ChatSubmod/chat_history.txt"

    # game/Submods/MAICA_ChatSubmod/header.rpy:160
    old "MAICA: 历史上传成功"
    new "MAICA: History uploaded"

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
    old "> Websocket:"
    new "> Websocket:"

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
    old "失败原因:"
    new "Reason:"

    # game/Submods/MAICA_ChatSubmod/header.rpy:330
    old "> 你当前的MAS生成版本过旧, 可能影响正常运行, 请升级至最新生成版本"
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
    old "查看MPostals往来信件"
    new "Reread MPostal letters"

    old "回信时显示控制台"
    new "Show console on MPostal writing reply"