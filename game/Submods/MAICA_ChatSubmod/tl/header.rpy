# TODO: Translation updated at 2024-07-07 20:52

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:140
    old "Not connected"
    new "未连接"
    # game/Submods/MAICA_ChatSubmod/header.rpy:140
    old "Connection established"
    new "已连接"
    # game/Submods/MAICA_ChatSubmod/header.rpy:140
    old "Connection closed"
    new "已断开"
    # game/Submods/MAICA_ChatSubmod/header.rpy:147
    old "> MAICA connection status: [maica.maica_instance.status]|[maica.maica_instance.MaicaAiStatus.get_description(maica.maica_instance.status)]"
    new "> MAICA通信状态: [maica.maica_instance.status]|[maica.maica_instance.MaicaAiStatus.get_description(maica.maica_instance.status)]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:151
    old "> Websocket: [stat]"
    new "> Websocket: [stat]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:157
    old "> Generate token"
    new "> 生成令牌"
    # game/Submods/MAICA_ChatSubmod/header.rpy:160
    old "> Connect with current token"
    new "> 使用已保存令牌连接"
    # game/Submods/MAICA_ChatSubmod/header.rpy:165
    old "> Upload savefile information"
    new "上传存档信息"
    # game/Submods/MAICA_ChatSubmod/header.rpy:168
    old "> Reset current session"
    new "重置当前对话"
    # game/Submods/MAICA_ChatSubmod/header.rpy:171
    old "> Export current session"
    new "导出当前对话"
    # game/Submods/MAICA_ChatSubmod/header.rpy:174
    old "> Lougout current account"
    new "退出当前DCC账号"
    # game/Submods/MAICA_ChatSubmod/header.rpy:177
    old "> MAICA params and settings *some options may need reconnection"
    new "> MAICA参数与设置 *部分选项需要重新连接"
    # game/Submods/MAICA_ChatSubmod/header.rpy:201
    old "Total conversation rounds: [store.maica.maica_instance.stat.get('message_count')]"
    new "累计对话轮次: [store.maica.maica_instance.stat.get('message_count')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:204
    old "Total chunks recieved: [store.maica.maica_instance.stat.get('received_token')]"
    new "累计收到Chunks: [store.maica.maica_instance.stat.get('received_token')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:206
    old "Reset statistics"
    new "重置统计数据"
    # game/Submods/MAICA_ChatSubmod/header.rpy:211
    old "Auto reconnect: [persistent.maica_setting_dict.get('auto_connect')]"
    new "自动重连: [persistent.maica_setting_dict.get('auto_connect')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:213
    old "Automatically reconnect on connection close"
    new "连接断开时自动重连"
    # game/Submods/MAICA_ChatSubmod/header.rpy:216
    old "Current MAICA model: [persistent.maica_setting_dict.get('maica_model')]"
    new "当前MAICA模型: [persistent.maica_setting_dict.get('maica_model')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:218
    old "maica_main: MAICA full functionality; maica_core: MAICA LLM functionality\nmaica_main has a higher response latency"
    new "maica_main：完全能力模型，maica_core: 核心能力模型\n完全能力的前置响应延迟偏高"
    # game/Submods/MAICA_ChatSubmod/header.rpy:222
    old "Target language: [persistent.maica_setting_dict.get('target_lang')]"
    new "目标语言: [persistent.maica_setting_dict.get('target_lang')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:224
    old "The language you prefer recieving\nAchieved by modding system prompt, cannot guarantee correct output"
    new "你与莫妮卡的沟通语言\n通过system prompt实现, 不能保证输出语言严格正确"
    # game/Submods/MAICA_ChatSubmod/header.rpy:229
    old "Use advanced parameters: [persistent.maica_setting_dict.get('use_custom_model_config')]"
    new "使用高级参数: [persistent.maica_setting_dict.get('use_custom_model_config')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:231
    old "Make sure config file custom_modelconfig.json makes sense before use"
    new "在使用前, 请务必查看子模组根目录的custom_modelconfig.json\n否则可能导致意料之外的问题\n子模组将读取该json作为对话参数"
    # game/Submods/MAICA_ChatSubmod/header.rpy:234
    old "Flush options"
    new "刷新参数"
    # game/Submods/MAICA_ChatSubmod/header.rpy:238
    old "Use persistent file: [persistent.maica_setting_dict.get('savefile_access')]"
    new "使用存档数据: [persistent.maica_setting_dict.get('savefile_access')]"
    old "Model will ignore savefile data if this is disabled.\n! savefile_access marker does not exist, savefile will not be uploaded or applied"
    new "关闭时, 模型将不会使用存档数据.\n! savefile_access标记文件不存在, 存档数据不会上传或应用"
    # game/Submods/MAICA_ChatSubmod/header.rpy:240
    old "Decides if use uploaded savefile or not\nMust have savefile uploaded if set to on"
    new "关闭时, 模型将不会使用存档数据\n在开启前请务必先上传存档"
    # game/Submods/MAICA_ChatSubmod/header.rpy:244
    old "Session currently in use: [persistent.maica_setting_dict.get('chat_session')]"
    new "当前使用会话: [persistent.maica_setting_dict.get('chat_session')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:246
    old "Disable session storage by setting chat_session 0. Sessions use savefiles individually"
    new "chat_session为0为单轮对话模式, 不同的对话之间相互独立, 需要分别上传存档"
    # game/Submods/MAICA_ChatSubmod/header.rpy:250
    old "Debugging console: [persistent.maica_setting_dict.get('console')]"
    new "输出到控制台: [persistent.maica_setting_dict.get('console')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:252
    old "Show debugging console while chatting\nI think this looks cool xd"
    new "在对话期间是否使用console显示相关信息, wzt的癖好\n说谁呢, 不觉得这很酷吗"
    # game/Submods/MAICA_ChatSubmod/header.rpy:256
    old "Purge additional player preferences: currently [len(persistent.mas_player_additions)]"
    new "清除玩家补充信息: 当前共有[len(persistent.mas_player_additions)]条"
    # game/Submods/MAICA_ChatSubmod/header.rpy:258
    old "Player complemented preferences data"
    new "由你补充的一些数据"
    # game/Submods/MAICA_ChatSubmod/header.rpy:261
    old "Export to directory"
    new "导出至根目录"
    # game/Submods/MAICA_ChatSubmod/header.rpy:263
    old "Export to game/Submods/MAICA_ChatSubmod/player_information.txt"
    new "导出至game/Submods/MAICA_ChatSubmod/player_information.txt"
    # game/Submods/MAICA_ChatSubmod/header.rpy:270
    old "Save settings"
    new "保存设置"
    # game/Submods/MAICA_ChatSubmod/header.rpy:292
    old "Enter DCC username "
    new "输入 DCC 账号用户名"
    # game/Submods/MAICA_ChatSubmod/header.rpy:294
    old "or "
    new "或"
    # game/Submods/MAICA_ChatSubmod/header.rpy:295
    old "Enter DCC register email{#maica_register_prompt}"
    new "输入 DCC 账号邮箱"
    # game/Submods/MAICA_ChatSubmod/header.rpy:296
    old "Enter DCC register email"
    new "请输入DCC 账号邮箱"
    # game/Submods/MAICA_ChatSubmod/header.rpy:299
    old "Enter DCC password{#maica_register_prompt}"
    new "输入 DCC 账号密码"
    # game/Submods/MAICA_ChatSubmod/header.rpy:300
    old "Enter DCC password"
    new "请输入DCC 账号密码"
    # game/Submods/MAICA_ChatSubmod/header.rpy:305
    old "Generate token online"
    new "连接至服务器生成MAICA令牌"
    # game/Submods/MAICA_ChatSubmod/header.rpy:312
    old "Generate token"
    new "生成MAICA令牌"
    # game/Submods/MAICA_ChatSubmod/header.rpy:318
    old "Cancel"
    new "取消"
# TODO: Translation updated at 2024-07-09 18:46

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:99
    old "Upload success"
    new "上传成功"
    # game/Submods/MAICA_ChatSubmod/header.rpy:99
    old "Upload failed"
    new "上传失败"
    # game/Submods/MAICA_ChatSubmod/header.rpy:140
    old "Failed initializing advanced params, check submod_log.log"
    new "加载高级参数失败, 查看submod_log.log来获取详细原因"
    # game/Submods/MAICA_ChatSubmod/header.rpy:220
    old "Auto reconnect: [persistent.maica_setting_dict.get('auto_reconnect')]"
    new "自动重连: [persistent.maica_setting_dict.get('auto_reconnect')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:264
    old "Console font: [persistent.maica_setting_dict.get('console_font')]"
    new "控制台字体: [persistent.maica_setting_dict.get('console_font')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:266
    old "Decides what font should console display in. \nmplus-1mn-medium.ttf for default, SarasaMonoTC-SemiBold.ttf may behave better with non-ascii characters."
    new "console使用的字体\nmplus-1mn-medium.ttf为默认字体\nSarasaMonoTC-SemiBold.ttf对于非英文字符有更好的显示效果"
    # game/Submods/MAICA_ChatSubmod/header.rpy:272
    old "User defined preference data, needs re-uploading savefile to take effect"
    new "由你补充的一些数据, 增删后需要重新上传存档"
    # game/Submods/MAICA_ChatSubmod/header.rpy:276
    old "Add preference"
    new "增加信息"
    # game/Submods/MAICA_ChatSubmod/header.rpy:277
    old "Preference addition will be sent on closing settings"
    new "增加信息的事件将于关闭设置后推送"
    # game/Submods/MAICA_ChatSubmod/header.rpy:282
    old "Click me to push events"
    new "点击后将推送相关事件"
    # game/Submods/MAICA_ChatSubmod/header.rpy:329
    old "Enter DCC account username{#maica_legacy_header}"
    new "请输入DCC 账号用户名"
# TODO: Translation updated at 2024-07-11 22:18

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:289
    old "Edit information"
    new "编辑信息"
    # game/Submods/MAICA_ChatSubmod/header.rpy:306
    old "MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"
    new "MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:308
    old "Enable or disable MSpire topics generation. Turn off repetive conversation to take effect."
    new "是否允许由MSpire生成的对话, MSpire不受MFocus影响, 需要关闭重复对话"
    # game/Submods/MAICA_ChatSubmod/header.rpy:311
    old "Edit topic range"
    new "对话范围编辑"
    # game/Submods/MAICA_ChatSubmod/header.rpy:317
    old "The range should be the title of a wikipedia category page"
    new "范围为维基百科的category页面"
    # game/Submods/MAICA_ChatSubmod/header.rpy:320
    old "Interval: [persistent.maica_setting_dict.get('mspire_interval')] Minute(s)"
    new "间隔: [persistent.maica_setting_dict.get('mspire_interval')]分钟"
    # game/Submods/MAICA_ChatSubmod/header.rpy:325
    old "The minimum interval triggering MSpire"
    new "MSpire对话的最低间隔分钟"
    # game/Submods/MAICA_ChatSubmod/header.rpy:330
    old "submod_log.log verbosity: [logging.getLevelName(store.mas_submod_utils.submod_log.level)]"
    new "submod_log.log 等级:[logging.getLevelName(store.mas_submod_utils.submod_log.level)]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:332
    old "Filter lower level logs\nThis affects every installed submod"
    new "这将影响submod_log.log中每条log的等级, 低于该等级的log将不会记录\n这也会影响其他子模组"
# TODO: Translation updated at 2024-08-04 13:15

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:280
    old "{a=https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Documents.md#调整设置}{i}{u}Official document of MAICA API{/i}{/u}{/a}"
    new "{a=https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Documents.md#调整设置}{i}{u}MAICA 官方文档{/i}{/u}{/a}"
    # game/Submods/MAICA_ChatSubmod/header.rpy:282
    old "{a=https://platform.openai.com/docs/api-reference/chat}{i}{u}OPENAI documents{/i}{/u}{/a}"
    new "{a=https://www.openaidoc.com.cn/api-reference/chat}{i}{u}OPENAI 中文文档{/i}{/u}{/a}"
    # game/Submods/MAICA_ChatSubmod/header.rpy:287
    old "The token choice range in sequence of probability. Model will only choose the next token from the top_p/1 former part of all tokens."
    new "模型选择的范围, 模型考虑概率质量值在前 top_p 的标记的结果, 因此，0.1 意味着仅考虑概率质量值前 10% 的标记"
    # game/Submods/MAICA_ChatSubmod/header.rpy:301
    old "The randomness of output. Temperature was added to token weights to dilute their default probabilities, so higher temperature suggests creativity and lower suggests precision."
    new "模型输出的随机性, 较高的值会使输出更随机, 而较低的值则会使其更加专注和确定"
    # game/Submods/MAICA_ChatSubmod/header.rpy:312
    old "The max length model can output in a single round. Model will try to fit this value but oversized responses will be chopped."
    new "模型输出的长度限制, 较高的值会使输出更长"
    # game/Submods/MAICA_ChatSubmod/header.rpy:324
    old "Higher Frequency penalty prevents model from repeating one pattern for times. Minimum was limited to 0.2 by MAICA to avoid catastrophic repetition."
    new "频率惩罚, 正值基于新标记在文本中的现有频率对其进行惩罚, 降低模型重复相同行的可能性"
    # game/Submods/MAICA_ChatSubmod/header.rpy:336
    old "Higher Presence penalty prevents model from repeating the input, enhances the possibility of topic switching.{#maica_legacy_header}"
    new "正值基于新标记出现在文本中的情况对其进行惩罚, 增加模型谈论新话题的可能性"
    # game/Submods/MAICA_ChatSubmod/header.rpy:358
    old "Set 0 for no MFocus enforcing. Set 1 for enforcing time and events. Set 2 for enforcing time, date, events and weather(if possible). May offset low MFocus hit rate but may also cause misunderstanding of queries."
    new "0时只调用MFocus直接选择的工具. 当其为1时总是会调用时间与节日工具. 当其为2时还会额外调用日期工具.\n为2时, 且mas_geolocation存在, mf_const_tools还会额外调用当前天气工具.\n可能补偿MFocus命中率低下的问题, 但也可能会干扰模型对部分问题的判断."
    # game/Submods/MAICA_ChatSubmod/header.rpy:372
    old "Set true for always using MFocus final answer instead of combined instructs if possible. May improve capability of concluding information but may also result in confusion in personality and response format."
    new "总是尽可能使用MFocus的最终输出替代指导构型信息. 启用此功能可能提升模型的复杂信息梳理能力 \n但也可能会造成人称或格式的混乱"
    # game/Submods/MAICA_ChatSubmod/header.rpy:377
    old "Set true for always using player name in place of [[player]s in prompts. May help model understanding player's name but may also result in overall performance decline and information makeups."
    new "指定prompt_pname_repl为true将总是以用户的真名替代prompt中的[[player]字段. \n启用此功能可能有利于模型理解玩家的姓名, 但也可能会造成总体拟合能力的下降和信息编造"
    # game/Submods/MAICA_ChatSubmod/header.rpy:382
    old "Set true for concluding internet information gathered by AgentLM again. Helps model focusing on search results but will lag specific responses."
    new "当esearch_llm_concl为true时会调用agent模型对MFocus联网搜集的信息整理一次.\n 启用此功能会改善模型对联网检索信息的专注能力, 但也会降低涉及联网搜索query的响应速度."
    # game/Submods/MAICA_ChatSubmod/header.rpy:470
    old "Total MSpire rounds: [store.maica.maica_instance.stat.get('mspire_count')]"
    new "累计MSpire轮次: [store.maica.maica_instance.stat.get('mspire_count')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:501
    old "Advanced params can impact model performance severely, use with extreme care."
    new "高级参数会大幅影响模型的表现"
    # game/Submods/MAICA_ChatSubmod/header.rpy:504
    old "Adjust advanced params"
    new "设置高级参数"
    # game/Submods/MAICA_ChatSubmod/header.rpy:510
    old "Set false for not uploading savefiles. Savefile is uploaded on game launching by default."
    new "关闭时, 模型将不会使用存档数据\n每次重启游戏将自动上传存档"
    # game/Submods/MAICA_ChatSubmod/header.rpy:569
    old "Frequency"
    new "间隔"
    # game/Submods/MAICA_ChatSubmod/header.rpy:577
    old "[persistent.maica_setting_dict.get('mspire_interval')] minutes"
    new "[persistent.maica_setting_dict.get('mspire_interval')]分钟"
    # game/Submods/MAICA_ChatSubmod/header.rpy:579
    old "Using session: [persistent.maica_setting_dict.get('mspire_session')]"
    new "使用会话: [persistent.maica_setting_dict.get('mspire_session')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:584
    old "Use chat session for MSpire\nMay lead to response pattern corruption."
    new "MSpire所使用的会话\nMSpire使用过多可能会导致模型定位混乱"
# TODO: Translation updated at 2024-09-30 08:15

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:96
    old "Authentication failed, recheck your account and password"
    new "验证失败, 请检查账号密码"
    # game/Submods/MAICA_ChatSubmod/header.rpy:98
    old "Authentication passed"
    new "验证成功"
    # game/Submods/MAICA_ChatSubmod/header.rpy:143
    old "Verification passed"
    new "验证成功{#maica_location}"
    # game/Submods/MAICA_ChatSubmod/header.rpy:147
    old "Exported to game/Submods/MAICA_ChatSubmod/chat_history.txt"
    new "已导出至game/Submods/MAICA_ChatSubmod/chat_history.txt"
    # game/Submods/MAICA_ChatSubmod/header.rpy:175
    old "Uploading settings"
    new "正在上传设置"
    # game/Submods/MAICA_ChatSubmod/header.rpy:175
    old "Please ensure connection is ready first"
    new "不能上传设置, 请等待MAICA准备好聊天\n请等待状态码改变后手动上传设置"
    # game/Submods/MAICA_ChatSubmod/header.rpy:275
    old "> Warning: Blessland is {color=#ff0000}NOT compatible with Better Loading{/color}"
    new "> 警告: {color=#ff0000}与 Better Loading 不兼容{/color}"
    # game/Submods/MAICA_ChatSubmod/header.rpy:298
    old "> Upload settings"
    new "> 手动上传设置"
    # game/Submods/MAICA_ChatSubmod/header.rpy:301
    old "> Upload settings [[Ensure connection ready first]"
    new "> 手动上传设置 [[不能上传, 因为MAICA未准备好/忙碌中]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:304
    old "> Reset current chat session"
    new "> 重置当前对话"
    # game/Submods/MAICA_ChatSubmod/header.rpy:307
    old "> Export current conversation history"
    new "> 导出当前对话"
    # game/Submods/MAICA_ChatSubmod/header.rpy:310
    old "> Logout"
    new "> 退出当前DCC账号"
    # game/Submods/MAICA_ChatSubmod/header.rpy:356
    old " <Official>"
    new " <官方服务>"
    # game/Submods/MAICA_ChatSubmod/header.rpy:359
    old "Intro: "
    new "说明: "
    # game/Submods/MAICA_ChatSubmod/header.rpy:361
    old "Model: "
    new "当前模型: "
    # game/Submods/MAICA_ChatSubmod/header.rpy:365
    old "> Switch to provider"
    new "> 使用该节点"
    # game/Submods/MAICA_ChatSubmod/header.rpy:372
    old "Refresh providers list"
    new "更新节点列表"
    # game/Submods/MAICA_ChatSubmod/header.rpy:376
    old "Close"
    new "关闭"
    # game/Submods/MAICA_ChatSubmod/header.rpy:520
    old "Enabling may improve performance in particular occasion.\nBut also may result in overall performance decrease."
    new "当nsfw_acceptive为true时会改变system指引, 使模型对NSFW场景更为宽容.\n 启用此功能可能提高特定场合表现, 但也可能会造成模型核心能力下降和注意力混乱.\n请注意, 目前为止MAICA尚未使用任何NSFW数据集进行训练, 因此nsfw_acceptive的效果十分薄弱.\n 此后或许会有针对性的改善."
    # game/Submods/MAICA_ChatSubmod/header.rpy:605
    old "Current provider: [store.maica.maica_instance.provider_manager.get_server_info().get('name', 'Unknown')]"
    new "服务提供节点: [store.maica.maica_instance.provider_manager.get_server_info().get('name', 'Unknown')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:607
    old "Choose provider"
    new "设置服务器节点"
    # game/Submods/MAICA_ChatSubmod/header.rpy:695
    old "Accepts existing categories of wikipedia\nWill fail if category doesn't exist"
    new "范围为维基百科的category页面\n如果无法找到catrgory将会提示错误输入"
    # game/Submods/MAICA_ChatSubmod/header.rpy:750
    old "Reset defaults"
    new "重置设置"
    # game/Submods/MAICA_ChatSubmod/header.rpy:751
    old "Reset finished"
    new "设置已重置"
    # game/Submods/MAICA_ChatSubmod/header.rpy:776
    old "Use username instead"
    new "改为用户名登录"
    # game/Submods/MAICA_ChatSubmod/header.rpy:781
    old "Use Email instead"
    new "改为邮箱登录"
# TODO: Translation updated at 2024-11-14 17:15

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:2
    old "MAICA Official Submod Frontend"
    new "MAICA官方前端子模组"
    # game/Submods/MAICA_ChatSubmod/header.rpy:275
    old "> Cannot verify version, try updating submod yourself if problems encountered"
    new "> 无法验证版本号, 如果出现问题请更新至最新版"
    # game/Submods/MAICA_ChatSubmod/header.rpy:280
    old "> Support has ended for current version, please update submod"
    new "> 当前版本已不再支持, 请更新至最新版"
    # game/Submods/MAICA_ChatSubmod/header.rpy:331
    old "> Changelogs and serving status"
    new "> 更新日志与服务状态"
    # game/Submods/MAICA_ChatSubmod/header.rpy:878
    old "※ By using MAICA Blessland, you have acknowledged and agree to obey {a=https://maica.monika.love/tos_en}{i}{u}MAICA TOS{/i}{/u}{/a}"
    new "※ 使用MAICA Blessland, 即认为你同意 {a=https://maica.monika.love/tos_zh}{i}{u}MAICA服务条款{/i}{/u}{/a}"
    # game/Submods/MAICA_ChatSubmod/header.rpy:950
    old "Nevermind"
    new "算了"
    # game/Submods/MAICA_ChatSubmod/header.rpy:954
    old "Paste"
    new "粘贴"
# TODO: Translation updated at 2024-11-22 18:00

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:349
    old "> Update and service status tracker {size=-10}* Update available"
    new "> 更新日志与服务状态 {size=-10}*有新更新"
    # game/Submods/MAICA_ChatSubmod/header.rpy:459
    old "√ Enabled"
    new "√ 已启用"
    # game/Submods/MAICA_ChatSubmod/header.rpy:462
    old "× Disabled"
    new "× 已禁用"
    # game/Submods/MAICA_ChatSubmod/header.rpy:466
    old "※ Trigger condition not satisfied"
    new "※ 当前不满足触发条件"
    # game/Submods/MAICA_ChatSubmod/header.rpy:555
    old "{a=https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Documents.md}{i}{u}MAICA Official API references{/i}{/u}{/a}"
    new "{a=https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Documents.md}{i}{u}MAICA 官方文档{/i}{/u}{/a}"
    # game/Submods/MAICA_ChatSubmod/header.rpy:559
    old "{size=-10}Notice: Only checked (X) advanced settings will take effect, unchecked ones will remain default"
    new "{size=-10}注意: 只有已被勾选(标记了X)的高级设置才会被使用, 未使用的设置将使用服务端的默认设置"
    # game/Submods/MAICA_ChatSubmod/header.rpy:562
    old "{size=-10}You have not enabled advanced parameters, thus settings on this page will not take effect!"
    new "{size=-10}你当前未启用'使用高级参数', 该页的所有设置都不会生效!"
    # game/Submods/MAICA_ChatSubmod/header.rpy:567
    old "{size=-10}================Super params================"
    new "{size=-10}================超参数================"
    # game/Submods/MAICA_ChatSubmod/header.rpy:640
    old "{size=-10}================Preferences================"
    new "{size=-10}================偏好================"
    # game/Submods/MAICA_ChatSubmod/header.rpy:678
    old "Rounds equal to mf_context_rnds value will be added for MFocus to analyze.\nMay improve MFocus accuracy performance, but may also result in misbehavior."
    new "相当于mf_context_rnds数值轮次的历史对话将被加入MFocus.\n此功能强度越高, 越可能提高MFocus在自然对话中的触发率, 但也越可能干扰MFocus的判断或导致其表现异常."
    # game/Submods/MAICA_ChatSubmod/header.rpy:689
    old "Rounds equal to mt_context_rnds value will be added for MTrigger to analyze.\nMay improve MTrigger accuracy performance, but may also result in misbehavior."
    new "相当于mt_context_rnds数值轮次的历史对话将被加入MTrigger.\n此功能强度越高, 越可能提高MTrigger在自然对话中的触发率, 但也越可能干扰MTrigger的判断或导致其表现异常."
    # game/Submods/MAICA_ChatSubmod/header.rpy:701
    old "Set to true to pre-analyze MTrigger items by MFocus(if both exists) to inform core model if request could be done. \nMay improve synchronousity of MTrigger, but also increases delay."
    new "当mf_precheck_mt为true时会要求MFocus预检MTrigger内容(若存在), 以告知核心模型要求是否可以完成. \n启用此功能会改善MTrigger与核心模型的表现失步问题, 但也会降低涉及MTrigger对话的响应速度.\n当对话未使用MTrigger或仅有好感触发器, 此功能不会生效."
    # game/Submods/MAICA_ChatSubmod/header.rpy:786
    old "Overall chunks recieved: [store.maica.maica_instance.stat.get('received_token_by_session')]"
    new "每个会话累计Chunks: [store.maica.maica_instance.stat.get('received_token_by_session')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:789
    old "Current user: [store.maica.maica_instance.user_acc]"
    new "当前用户: [store.maica.maica_instance.user_acc]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:840
    old "Chat session length: "
    new "会话长度: "
    # game/Submods/MAICA_ChatSubmod/header.rpy:845
    old "This setting is intended to reduce performance issue when history goes too long. Choose a reasonable value or model coherence may be impacted."
    new "此参数意在缓解对话历史累积导致的响应速度过慢问题. 请避免将其设置得过小, 否则可能影响模型的正常语言能力."
    # game/Submods/MAICA_ChatSubmod/header.rpy:847
    old "[persistent.maica_setting_dict.get('max_history_token')]"
    new "[persistent.maica_setting_dict.get('max_history_token')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:850
    old "Recover history to chat session [store.maica.maica_instance.chat_session]"
    new "上传对话历史到会话 [store.maica.maica_instance.chat_session]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:930
    old "Mtrigger triggers list"
    new "MTrigger列表"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1019
    old "{size=-10}※ By using MAICA Blessland, you agree to {a=https://maica.monika.love/tos_en}{i}{u}MAICA TOS{/i}{/u}{/a}"
    new "{size=-10}※ 使用MAICA Blessland, 即认为你同意 {a=https://maica.monika.love/tos_zh}{i}{u}MAICA服务条款{/i}{/u}{/a}"
# TODO: Translation updated at 2024-11-28 07:51

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:155
    old "game/Submods/MAICA_ChatSubmod/chat_history.txt not found"
    new "未找到game/Submods/MAICA_ChatSubmod/chat_history.txt"
    # game/Submods/MAICA_ChatSubmod/header.rpy:190
    old "Please ensure connection is ready before uploading settings"
    new "暂未上传设置, 请等待MAICA准备好聊天\n待状态码改变后手动上传设置"
    # game/Submods/MAICA_ChatSubmod/header.rpy:308
    old "> Warning: set 'submod_log' logger verbosity to 'info' or lower when using with Log Screen{#maica_legacy_header}"
    new "> 警告: 与 Log Screen 一起使用时, 请将'submod_log'的详细程度提高至info及以上"
    # game/Submods/MAICA_ChatSubmod/header.rpy:336
    old "> Manually upload settings [[Ensure connection is ready first]"
    new "> 手动上传设置 [[请先使MAICA完成连接]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:345
    old "> Upload chat history to session [store.maica.maica_instance.chat_session]"
    new "> 上传对话历史到会话 [store.maica.maica_instance.chat_session]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:353
    old "> MAICA params and settings {size=-10}*May need restarting to take effect"
    new "> MAICA参数与设置 {size=-10}*部分选项重新连接生效"
    # game/Submods/MAICA_ChatSubmod/header.rpy:628
    old "Higher Presence penalty prevents model from repeating the input, enhances the possibility of topic switching."
    new "重现惩罚, 正值基于新标记出现在文本中的情况对其进行惩罚, 增加模型谈论新话题的可能性"
    # game/Submods/MAICA_ChatSubmod/header.rpy:653
    old "Set 0 for no MFocus enforcing. Set 1 for enforcing time and events.\nSet 2 for enforcing time, date, events and weather(if possible).\nMay offset low MFocus hit rate but may also cause misunderstanding of queries."
    new "当其为0时只调用MFocus直接选择的工具. 为1时总是会调用时间与节日工具. 为2时还会额外调用日期工具.\n当其为2且mas_geolocation存在时, mf_const_tools还会额外调用当前天气工具.\n越高越可能补偿MFocus命中率低下的问题, 但也越可能会干扰模型对部分问题的判断."
    # game/Submods/MAICA_ChatSubmod/header.rpy:665
    old "Set true for always using MFocus final answer instead of combined instructs if possible.\nMay improve capability of concluding information but may also result in confusion in personality and response format."
    new "总是尽可能使用MFocus的最终输出替代指导构型信息.\n启用可能提升模型的复杂信息梳理能力, 但也可能会造成速度下降或专注扰乱"
    # game/Submods/MAICA_ChatSubmod/header.rpy:670
    old "Set true for always using player name in place of [[player]s in prompts.\nMay help model understanding player's name but may also result in overall performance decline and information makeups."
    new "总是以用户的真名替代prompt中的[[player]字段.\n启用此功能可能有利于模型理解玩家的姓名, 但也可能会造成总体拟合能力的下降和信息编造"
    # game/Submods/MAICA_ChatSubmod/header.rpy:675
    old "Set true for concluding internet information gathered by AgentLM again.\nHelps model focusing on search results but will lag specific responses."
    new "调用agent模型对MFocus联网搜集的信息整理一次.\n启用此功能会改善模型对联网检索信息的专注能力, 但也会降低涉及联网搜索query的响应速度."
    # game/Submods/MAICA_ChatSubmod/header.rpy:680
    old "Set true to request MFocus pre-analyzing MTrigger triggers on query's possibility.\nMay benefit on core-trigger sync but will lag specific responses.\nWill not take effect if no trigger aside from affection is activated."
    new "要求MFocus预检MTrigger内容(若存在), 以告知核心模型要求是否可以完成. \n启用此功能会改善MTrigger与核心模型的表现失步问题, 但也会降低涉及MTrigger对话的响应速度.\n当对话未使用MTrigger或仅有好感触发器, 此功能不会生效."
    # game/Submods/MAICA_ChatSubmod/header.rpy:685
    old "Set true to guide core model being more tolerant on toxic scenes.\nMay improve overall core performance (unexpectedly but proved true)\n but may also decrease attention performance and cause confusion."
    new "改变system指引, 使模型对NSFW场景更为宽容.\n经测试启用此功能对模型总体表现(意外地)有利, 但也存在降低模型专注能力和造成混乱的风险."
# TODO: Translation updated at 2024-11-29 20:06

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:141
    old "MAICA: Savefile uploaded successfully"
    new "MAICA: 存档上传成功"
    # game/Submods/MAICA_ChatSubmod/header.rpy:141
    old "MAICA; Savefile failed to upload"
    new "MAICA: 存档上传失败"
    # game/Submods/MAICA_ChatSubmod/header.rpy:145
    old "MAICA: Chat session reset"
    new "MAICA: 会话已重置"
    # game/Submods/MAICA_ChatSubmod/header.rpy:150
    old "MAICA: History exported to game/Submods/MAICA_ChatSubmod/chat_history.txt"
    new "MAICA: 历史已导出至game/Submods/MAICA_ChatSubmod/chat_history.txt"
    # game/Submods/MAICA_ChatSubmod/header.rpy:155
    old "MAICA: History not found at game/Submods/MAICA_ChatSubmod/chat_history.txt"
    new "MAICA: 未找到历史game/Submods/MAICA_ChatSubmod/chat_history.txt"
    # game/Submods/MAICA_ChatSubmod/header.rpy:160
    old "MAICA: History uploaded"
    new "MAICA: 历史上传成功"
    old "MAICA: Failed to upload history, check submod_log.log for details."
    new "MAICA: 历史上传失败, 查看submod_log获取详细原因."
    # game/Submods/MAICA_ChatSubmod/header.rpy:190
    old "MAICA: Settings uploaded"
    new "MAICA: 已上传设置"
    # game/Submods/MAICA_ChatSubmod/header.rpy:190
    old "MAICA: Do a manual upload after connection ready"
    new "MAICA: 请等待连接就绪后手动上传"
    # game/Submods/MAICA_ChatSubmod/header.rpy:223
    old "MAICA: Advanced settings failed to serialize, check submod_log.log"
    new "MAICA: 加载高级参数失败, 查看submod_log.log获取详细原因"
    # game/Submods/MAICA_ChatSubmod/header.rpy:960
    old "MAICA: Settings reset{#maica_legacy_header}"
    new "MAICA: 设置已重置"
# TODO: Translation updated at 2024-12-02 17:16

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:319
    old "> Websocket: "
    new "> Websocket: "
    # game/Submods/MAICA_ChatSubmod/header.rpy:463
    old "MTrigger space usage: "
    new "MTrigger空间使用情况: "
    # game/Submods/MAICA_ChatSubmod/header.rpy:473
    old "Space used: -"
    new "空间占用: -"
    # game/Submods/MAICA_ChatSubmod/header.rpy:477
    old "Space used: request"
    new "空间占用: request"
    # game/Submods/MAICA_ChatSubmod/header.rpy:483
    old "Space used: table"
    new "空间占用: table"
    # game/Submods/MAICA_ChatSubmod/header.rpy:960
    old "Search type: [persistent.maica_setting_dict.get('mspire_search_type')]"
    new "搜索方式: [persistent.maica_setting_dict.get('mspire_search_type')]"
    old "{size=-10}* If chat is stuck, click me to disconnect"
    new "{size=-10}* 如果对话卡住了, 点我断开连接"
    old "{size=-10}※ Don't have DCC account yet? {a=https://forum.monika.love/signup}{i}{u}Sign up.{/u}{/i}{/a}"
    new "{size=-10}※ 还没有DCC账号? {a=https://forum.monika.love/signup}{i}{u}注册一个{/u}{/i}{/a}"
# TODO: Translation updated at 2025-02-01 08:24

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:105
    old "Reason: "
    new "失败原因: "
    # game/Submods/MAICA_ChatSubmod/header.rpy:330
    old "> Your current MAS version is below the lowest compatible version, please update"
    new "> 你当前的MAS构建版本过旧, 可能影响正常运行, 请升级至最新版本"
    # game/Submods/MAICA_ChatSubmod/header.rpy:513
    old "> Notice: Some MTriggers will be disabled if content length exceeds!"
    new "> 注意: 当空间不足时将自动关闭部分MTrigger!"
    # game/Submods/MAICA_ChatSubmod/header.rpy:599
    old "{size=15}MPostal list will be shown after returning to the spaceroom."
    new "{size=15}因能力有限, 阅读信件后信件列表将在返回太空教室后重新显示."
    # game/Submods/MAICA_ChatSubmod/header.rpy:606
    old "MPostal status:"
    new "信件状态: "
    # game/Submods/MAICA_ChatSubmod/header.rpy:608
    old "Last post sent at: "
    new "寄信时间: "
    # game/Submods/MAICA_ChatSubmod/header.rpy:610
    old "\n[player]: \n"
    new "\n[player]: \n"
    # game/Submods/MAICA_ChatSubmod/header.rpy:613
    old "[m_name]: \n"
    new "[m_name]: \n"
    # game/Submods/MAICA_ChatSubmod/header.rpy:616
    old "Read [player]'s letter"
    new "阅读[player]写的信"
    # game/Submods/MAICA_ChatSubmod/header.rpy:624
    old "Read [m_name]'s reply"
    new "阅读[m_name]的回信"
    # game/Submods/MAICA_ChatSubmod/header.rpy:992
    old "MPostal sent count: [store.maica.maica_instance.stat.get('mpostal_count')]"
    new "累计发信数: [store.maica.maica_instance.stat.get('mpostal_count')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1015

    # game/Submods/MAICA_ChatSubmod/header.rpy:1125
    old "Status code refreshing frequency"
    new "状态码更新速度"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1130
    old "The refreshing frequency of status code on Submod screen"
    new "在Submod界面处的状态码更新频率"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1140
    old "Reread MPostal letters"
    new "MPostal历史信件"
    old "Show console on MPostal writing reply"
    new "回信时显示控制台"
# TODO: Translation updated at 2025-02-17 12:47

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:655
    old "Resend mail"
    new "重新寄信"
    # game/Submods/MAICA_ChatSubmod/header.rpy:721
    old "Mean power consumption: "
    new "平均功耗: "
    # game/Submods/MAICA_ChatSubmod/header.rpy:726
    old "Analytics refresh"
    new "下次更新数据"
    # game/Submods/MAICA_ChatSubmod/header.rpy:836
    old "{size=-10}If your timezone is not listed here, decide by your local UTC timezone."
    new "{size=-10}如果这里没有你的时区, 请根据你当地的UTC时间选择"
    # game/Submods/MAICA_ChatSubmod/header.rpy:839
    old "Language default"
    new "根据语言自动选择"
    # game/Submods/MAICA_ChatSubmod/header.rpy:843
    old "System default"
    new "根据系统时区自动选择"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1141
    old "Set timezone: [persistent.maica_advanced_setting.get('tz') or 'Asia/Shanghai' if store.maica.maica_instance.target_lang == store.maica.maica_instance.MaicaAiLang.zh_cn else 'America/Indiana/Vincennes']"
    new "选择时区: [persistent.maica_advanced_setting.get('tz') or 'Asia/Shanghai' if store.maica.maica_instance.target_lang == store.maica.maica_instance.MaicaAiLang.zh_cn else 'America/Indiana/Vincennes']"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1413
    old "Console logging verbosity: [logging.getLevelName(store.maica.maica_instance.console_logger.level)]"
    new "控制台log等级: [logging.getLevelName(store.maica.maica_instance.console_logger.level)]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1415
    old "Filter lower level logs shown in console"
    new "这将影响控制台中每条log的等级, 低于该等级的log将不会记录"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1440
    old "Check server load status"
    new "查看后端负载"
# TODO: Translation updated at 2025-02-23 15:54

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:1445
    old "MPostal reply delay"
    new "信件回复时间"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1450
    old "The minimum delay before MPostal replies"
    new "回信所需要的最低时间"
# TODO: Translation updated at 2025-04-08 11:52

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:1426
    old "Use cache for MSpire"
    new "MSpire使用缓存"
# TODO: Translation updated at 2025-05-04 21:00

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:430
    old "> Donate for MAICA"
    new "> 支持 MAICA"
    # game/Submods/MAICA_ChatSubmod/header.rpy:700
    old "We're grateful for your being willing to donate.\nThe donate will likely never cover our cost, but that's okay anyway."
    new "首先很感谢你有心捐赠.\n我们收到的捐赠基本上不可能回本, 但你不必有任何压力."
    # game/Submods/MAICA_ChatSubmod/header.rpy:702
    old "Please note that donating to MAICA doesn't give you any actual privilege. It's simply donation."
    new "请注意, 向MAICA捐赠不会提供任何特权, 除了论坛捐赠页名单和捐赠徽章."
# TODO: Translation updated at 2025-05-09 10:13

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:432
    old "> Donate to MAICA"
    new "> 向 MAICA 捐赠"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1568
    old "Dynamic Heaven Forest"
    new "动态的天堂树林"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1570
    old "Use dynamic forest background with improved illumination\nIncreases render consume slightly. Restart to take effect\nRemove some spritepacks or disable this if VRAM overflows"
    new "使用动态摇曳和改良光影的天堂树林, 略微增加渲染压力. 重启生效\n如果产生显存相关错误, 删减精灵包或禁用此选项"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1684
    old "Seed out of range, retry"
    new "seed范围错误, 请重新输入种子"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1704
    old "Choose a seed from 0-99999"
    new "请输入种子, 范围为0-99999"
# TODO: Translation updated at 2025-09-09 08:20

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:395
    old "> Warning: {color=#ff0000}no certification found{/color}, check datapack installation"
    new "> 警告: {color=#ff0000}找不到证书{/color}, 你是不是忘记安装数据包了?"
    # game/Submods/MAICA_ChatSubmod/header.rpy:520
    old "> Go to portal page"
    new "> 打开官网"
    # game/Submods/MAICA_ChatSubmod/header.rpy:537
    old "Test current node avaliability"
    new "测试当前节点可用性"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1451
    old "MTrigger enabled: [persistent.maica_setting_dict.get('enable_mt')]"
    new "使用MTrigger: [persistent.maica_setting_dict.get('enable_mt')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1454
    old "MFocus enabled: [persistent.maica_setting_dict.get('enable_mf')]"
    new "使用MFocus: [persistent.maica_setting_dict.get('enable_mf')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1746
    old "Choose a seed (integer)"
    new "请输入种子(整数)"
# TODO: Translation updated at 2025-09-15 16:02

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:406
    old "> Warning: set 'submod_log' logger verbosity to 'info' or lower when using with Log Screen"
    new "> 警告: 与 Log Screen 一起使用时, 请将'submod_log'的过滤级别提高至info及以上"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1124
    old "Token weight filter percentage. Seriously do not touch this"
    new "token权重过滤范围. 非常不建议动这个"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1137
    old "The randomness tokens are chosen. Higher this value, larger the offset between model performance and generally best performance"
    new "token选择的随机程度. 数值越高, 模型输出会越偏离普遍最佳情况"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1148
    old "The limit of tokens model can generate one round. Normally don't affect performance, but stops generating on hitting the limit"
    new "模型一轮生成的token数限制. 一般而言不会影响表现, 只会截断超长的部分"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1160
    old "Token frequency penalty. Higher this value, less likely repeatedly appeared tokens continue appearing, usually resulting in shorter and more expanding generation"
    new "token频率惩罚. 数值越高, 反复出现的token越不可能继续出现, 一般会产生更短且更延拓的结果"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1172
    old "Token presence penalty. Higher this value, less likely appeared tokens appear again, usually resulting in more jumping generation"
    new "token重现惩罚. 数值越高, 出现过的token越不可能再次出现, 一般会产生更跳跃的结果"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1233
    old "Provide some tool results even when MFocus does not call a tool.\n* 0: Disabled\n* 1: Provide the current time and holidays\n* 2: Also provide the current date and attempt to provide local weather\n+ Mitigates hallucinations caused by missing information and enables more flexible, considerate responses\n- May cause distraction and confusion"
    new "即使MFocus未调用工具, 也提供一些工具的结果.\n* 0: 关闭\n* 1: 提供当前时间和节日\n* 2: 还提供当前日期, 还尝试提供本地天气\n+ 能缓解信息缺乏导致的幻觉, 产生更灵活体贴的表现\n- 有可能产生注意力涣散和混乱"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1245
    old "Require the agent model to generate final guidance instead of the default MFocus guidance.\n+ Higher information density and more natural language\n- Depends heavily on the agent model's instruction-following ability and can be counterproductive\n- Usually neutralizes mf_const_tools when enabled"
    new "要求agent模型生成最终指导, 并替代默认MFocus指导.\n+ 信息密度更高, 更容易维持语言自然\n- 表现十分依赖agent模型的指令服从能力, 容易起反作用\n- 启用时一般会无效化mf_const_tools"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1250
    old "Replace [[player] in prompts and guidance with the player's real name.\n+ Gives the model a concrete understanding of the player's name\n- Increases the risk of inconsistent or confused behavior"
    new "将prompt和引导中的[[player]字段替换为玩家真名.\n+ 模型对玩家的名字有实质性理解\n- 更容易发生表现离群和混乱"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1255
    old "Require MFocus to reorganize Internet search results.\n+ Higher information density and more stable behavior in most cases\n- Slower generation when Internet search is involved\n- May mislead the core model's response style"
    new "在MFocus调用互联网搜索的情况下, 要求其整理一遍结果.\n+ 大多数情况下信息密度更高, 表现更稳定\n- 涉及互联网搜索时生成速度更慢\n- 可能会对核心模型的回答方式产生误导"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1261
    old "Require MFocus to precheck the player's request and provide guidance when MTrigger is present.\n+ Mitigates MTrigger desynchronization in principle\n- May make the language less natural in rare cases"
    new "当MTrigger存在时, 要求MFocus预检玩家的请求并提供指导.\n+ 从原理上缓解MTrigger失步问题\n- 在少数情况下对语言的自然性产生破坏"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1268
    old "Ask the model to treat toxic content tolerantly and positively.\n+ Surprisingly improves model behavior in most situations, even without toxic content\n- May cause unexpected issues, although none have been observed so far"
    new "要求模型宽容正面地对待有毒内容.\n+ (出乎意料地)在大多数场合下对模型表现有正面作用, 即使不涉及有毒内容\n- 这可能会造成意料之外的问题, 虽然目前为止没见过"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1275
    old "Provide extra context for analysis when MFocus intervenes. Range: 0-5.\n+ Improves MFocus's understanding of coherent conversations\n- Increases the risk of disrupting MFocus's response pattern"
    new "在MFocus介入时, 额外提供上下文以供分析. 范围0-5.\n+ 改善MFocus对连贯对话的理解能力\n- 更容易破坏MFocus的应答模式"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1286
    old "Provide history context for MTrigger, in range of 0-5 rounds.\n+ Improves MTrigger's understanding to serial conversation\n- Risk of breaking MTrigger reply pattern"
    new "在MTrigger介入时, 额外提供上下文以供分析. 范围0-5.\n+ 改善MTrigger对连贯对话的理解能力\n- 更容易破坏MTrigger的应答模式"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1464

    # game/Submods/MAICA_ChatSubmod/header.rpy:1479
    old "Target generation language. Supports \"zh\", \"en\", and \"auto\".\n* This setting cannot guarantee the generated language\n* It also affects the default timezone, holidays, culture, and more; using your actual native language is recommended\n* auto asks the model to choose a response language through the prompt and is not equivalent to selecting that language explicitly\n* At the time of writing, MAICA's official deployment remains less capable in English than in Chinese"
    new "目标生成语言. 支持\"zh\", \"en\"或\"auto\".\n* 该参数不能100%保证生成语言是目标语言\n* 该参数影响范围广泛, 包括默认时区, 节日文化等, 并不止目标生成语言. 建议设为你的实际母语\n* auto代表通过prompt让模型自行选择语言回答, 效果不等同于指定对应语言\n* 截至文档编纂时为止, MAICA官方部署的英文能力仍然弱于中文"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1484
    old "Enable customized advanced parameters: [persistent.maica_setting_dict.get('use_custom_model_config')]"
    new "使用自定义高级参数: [persistent.maica_setting_dict.get('use_custom_model_config')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1486
    old "Advanced parameters could significantly affect the model's performance.\n* The default is already the best field-tested config, so it's not suggested to enable this"
    new "高级参数可能大幅影响模型的表现.\n* 默认的高级参数已经是实践中的普遍最优配置, 不建议启用"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1500
    old "Model will ignore savefile data if this is disabled.\n* MAICA Blessland uploads savefile on each restart automatically"
    new "关闭时, 模型将不会使用存档数据.\n* 每次重启游戏将自动上传存档数据"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1506
    old "Each session stores and applies history context independently.\n* Set to 0 to disable context (single round conversation)"
    new "每个session独立保存和应用对话记录.\n* 设为0以不记录和不使用对话记录(单轮对话)"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1514
    old "Max length each session will preserve, in range of 512-28672.\n* Every 3 ASCII characters occupy one space\n* MAICA crops the former part of context on exceeding to no more than 2/3 left\n* Too high or too low value can cause performance and generation quality issues"
    new "会话保留的最大长度. 范围512-28672.\n* 按字符数计算. 每3个ASCII字符只占用一个字符长度\n* 字符数超过限制后, MAICA会裁剪其中较早的部分, 直至少于限制的 2/3\n* 过大或过小的值可能导致表现和性能问题"
# TODO: Translation updated at 2025-09-23 23:29

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:329
    old "MAICA: Settings discarded"
    new "MAICA: 已放弃设置修改"
    # game/Submods/MAICA_ChatSubmod/header.rpy:503
    old "> Couldn't acquire online version stream, please check updates manually"
    new "> 未能联网验证版本信息, 如果出现问题请尝试更新"
    # game/Submods/MAICA_ChatSubmod/header.rpy:509
    old "> {color=#ff0000}Support for current version has ended{/color}, an update is required"
    new "> {color=#ff0000}当前版本支持已终止{/color}, 请更新至最新版"
    # game/Submods/MAICA_ChatSubmod/header.rpy:541
    old "> Generate token from account"
    new "> 使用账号生成令牌"
    # game/Submods/MAICA_ChatSubmod/header.rpy:561
    old "> Upload settings manually [[wait for connection establishment first]"
    new "> 手动上传设置 [[请先等待连接建立]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:563
    old "> Reset current chat session [[wait for connection establishment first]"
    new "> 重置当前对话 [[请先等待连接建立]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:571
    old "{size=-10}* If conversation hangs, logout to interrupt"
    new "{size=-10}* 如果对话卡住, 退出以断开连接"
    # game/Submods/MAICA_ChatSubmod/header.rpy:694
    old "Connection and Safety"
    new "连接与安全"
    # game/Submods/MAICA_ChatSubmod/header.rpy:704
    old "Not logged in"
    new "未登录"
    # game/Submods/MAICA_ChatSubmod/header.rpy:705
    old "Current user: [user_disp]"
    new "当前用户: [user_disp]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:707
    old "To change account or logout, navigate to Submods menu.\n* To change account properties or password, navigate to registration site"
    new "如需更换或退出账号, 请在Submods界面退出登录.\n* 要修改账号信息或密码, 请前往注册网站"
    # game/Submods/MAICA_ChatSubmod/header.rpy:723
    old "Performance and Behavior"
    new "行为与表现"
    # game/Submods/MAICA_ChatSubmod/header.rpy:729
    old "An agent model will recieve input prior to the core model, and acquire information with tools.\n* MFocus is a major mechanism of MAICA, suggested to enable"
    new "一个agent模型先于核心模型接收相同或相似的输入内容, 并调用工具以获取信息. 这些信息会被提供给核心模型.\n* MFocus是MAICA的重要功能之一, 一般不建议禁用"
    # game/Submods/MAICA_ChatSubmod/header.rpy:736
    old "An agent model will recieve input subsequent to the core model, and guide character's action.\n* MTrigger is a major mechanism of MAICA, suggested to enable"
    new "一个agent模型后于核心模型接收本轮的输入输出, 并调用工具以指示前端作出角色行为.\n* MTrigger是MAICA的重要功能之一, 一般不建议禁用"
    # game/Submods/MAICA_ChatSubmod/header.rpy:748
    old "Timezone: [persistent.maica_setting_dict.get('tz')]"
    new "时区设置: [persistent.maica_setting_dict.get('tz')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:782
    old "Sessions and Data"
    new "会话与数据"
    # game/Submods/MAICA_ChatSubmod/header.rpy:792
    old "Current chat session"
    new "当前会话"
    # game/Submods/MAICA_ChatSubmod/header.rpy:796
    old "Chat session length"
    new "会话长度"
    # game/Submods/MAICA_ChatSubmod/header.rpy:807
    old "User-provided implementations, handled and sent to core model by MFocus.\n* May need a restart for changes to take effect"
    new "由你补充的设定信息, 由MFocus检索并呈递到核心模型.\n* 需要重新上传存档生效"
    # game/Submods/MAICA_ChatSubmod/header.rpy:810
    old "[len(persistent.mas_player_additions)] MFocus info present"
    new "当前有[len(persistent.mas_player_additions)]条自定义MFocus信息"
    # game/Submods/MAICA_ChatSubmod/header.rpy:828
    old "Edit MFocus info"
    new "编辑MFocus信息"
    # game/Submods/MAICA_ChatSubmod/header.rpy:847
    old "Export MFocus info to main directory"
    new "导出自定义MFocus信息到主目录"
    # game/Submods/MAICA_ChatSubmod/header.rpy:853
    old "Tools and Functions"
    new "工具与功能"
    # game/Submods/MAICA_ChatSubmod/header.rpy:858
    old "Enable MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"
    new "启用MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:860
    old "Enable MSpire to generate vanilla-like conversations.\n* Repeat topics must be disabled to take effect\n* MSpire doesn't use MF/MT"
    new "是否允许由MSpire生成的对话.\n* 必须关闭复述话题才能启用\n* MSpire话题不使用MFocus和MTrigger"
    # game/Submods/MAICA_ChatSubmod/header.rpy:867
    old "Enable MSpire to generate vanilla-like conversations.\n! Repeat topice enabled, with which MSpire conflicts"
    new "是否允许由MSpire生成的对话.\n! 复述话题已启用, MSpire不会生效"
    # game/Submods/MAICA_ChatSubmod/header.rpy:877
    old "MSpire topics"
    new "MSpire话题"
    # game/Submods/MAICA_ChatSubmod/header.rpy:881
    old "Minimal interval of MSpire conversations"
    new "MSpire对话的最小时间间隔"
    # game/Submods/MAICA_ChatSubmod/header.rpy:882
    old "MSpire minimal interval"
    new "MSpire最小间隔"
    # game/Submods/MAICA_ChatSubmod/header.rpy:887
    old "MSpire searching method: [persistent.maica_setting_dict.get('mspire_search_type')]"
    new "MSpire搜索方式: [persistent.maica_setting_dict.get('mspire_search_type')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:891
    old "Way of MSpire searching for topics"
    new "MSpire搜索话题的模式"
    # game/Submods/MAICA_ChatSubmod/header.rpy:905
    old "Configure MTrigger triggers"
    new "查看和配置MTrigger条目"
    # game/Submods/MAICA_ChatSubmod/header.rpy:921
    old "Reread MPostal history letters"
    new "查看MPostal历史信件"
    # game/Submods/MAICA_ChatSubmod/header.rpy:924
    old "Minimal interval of MPostal replies"
    new "MPostal回信的最小时间间隔"
    # game/Submods/MAICA_ChatSubmod/header.rpy:925
    old "MPostal minimal interval"
    new "MPostal最小间隔"
    # game/Submods/MAICA_ChatSubmod/header.rpy:928
    old "Interfaces and Log"
    new "界面与日志"
    # game/Submods/MAICA_ChatSubmod/header.rpy:932
    old "submod_log.log verbosity: [logging.getLevelName(persistent.maica_setting_dict['log_level'])]"
    new "submod_log.log 等级: [logging.getLevelName(persistent.maica_setting_dict['log_level'])]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:934
    old "Lower level logs will not appear in submod_log.log.\n* This effect is global"
    new "重要性低于设置等级的log将不会被记录在submod_log.log中.\n* 这也会影响其他子模组"
    # game/Submods/MAICA_ChatSubmod/header.rpy:938
    old "Status code update interval"
    new "状态码更新频率"
    # game/Submods/MAICA_ChatSubmod/header.rpy:944
    old "Use dynamic forest background with improved illumination, may increase render consumation. Restart to take effect.\n* Remove some spritepacks or disable this if VRAM overflows"
    new "使用动态摇曳和改良光影的天堂树林, 略微增加渲染压力. 重启生效.\n* 如果产生显存相关错误, 删减精灵包或禁用此选项"
    # game/Submods/MAICA_ChatSubmod/header.rpy:970
    old "Console logging verbosity: [logging.getLevelName(persistent.maica_setting_dict['log_conlevel'])]"
    new "控制台log等级: [logging.getLevelName(persistent.maica_setting_dict['log_conlevel'])]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:972
    old "Lower level logs will not appear in console"
    new "重要性低于设置等级的log将不会显示在控制台中"
    # game/Submods/MAICA_ChatSubmod/header.rpy:980
    old "Statics and Information"
    new "统计与信息"
    # game/Submods/MAICA_ChatSubmod/header.rpy:984
    old "Expand performance monitor"
    new "展开性能监控"
    # game/Submods/MAICA_ChatSubmod/header.rpy:984
    old "Retract performance monitor"
    new "收起性能监控"
    # game/Submods/MAICA_ChatSubmod/header.rpy:988
    old "Expand/retract server performance monitor"
    new "显示/收起服务器的性能状态指标"
    # game/Submods/MAICA_ChatSubmod/header.rpy:998
    old "Expand statics"
    new "展开统计数据"
    # game/Submods/MAICA_ChatSubmod/header.rpy:998
    old "Retract statics"
    new "收起统计数据"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1002
    old "Expand/retract client-side statics"
    new "显示/收起你的使用统计数据"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1019
    old "Discard modifications"
    new "放弃修改"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1025
    old "MAICA: Settings reset"
    new "MAICA: 已重置设置"
# TODO: Translation updated at 2025-09-24 16:28

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:402
    old "MAICA: Exported to game/Submods/MAICA_ChatSubmod/player_information.txt"
    new "MAICA: 信息已导出至game/Submods/MAICA_ChatSubmod/player_information.txt"
# TODO: Translation updated at 2025-09-28 16:56

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:759
    old "Geolocation: [persistent.mas_geolocation]"
    new "地理位置: [persistent.mas_geolocation]"
# TODO: Translation updated at 2025-10-06 22:29

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:543
    old "> Warning: MAICA Libs version not found. Please install from Release, {color=#ff0000}NOT source code{/color}"
    new "> 警告: 未检测到MAICA库版本信息. 请从Release下载安装MAICA, {color=#ff0000}而不是源代码{/color}"
    # game/Submods/MAICA_ChatSubmod/header.rpy:548
    old "> Warning: MAICA Libs v[libv] mismatch with UI v[uiv]. Please fully update {color=#ff0000}from Release{/color}"
    new "> 警告: MAICA库版本[libv]与UI版本[uiv]不符. 请{color=#ff0000}从Release{/color}完整地更新MAICA"
# TODO: Translation updated at 2025-11-14 17:16

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:788
    old "Generation resume: [persistent.maica_setting_dict.get('auto_resume')]"
    new "断点续传: [persistent.maica_setting_dict.get('auto_resume')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:790
    old "Resume streaming on reconnection to recover lost chunks"
    new "若生成回复时网络中断, 重连后续传丢失的部分"
    # game/Submods/MAICA_ChatSubmod/header.rpy:794
    old "Keep connection active: [persistent.maica_setting_dict.get('keep_alive')]"
    new "保持连接活跃: [persistent.maica_setting_dict.get('keep_alive')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:796
    old "Send ping packets timely to keep connection alive and calculate lag"
    new "定期发送心跳包保持长连接活跃, 并检测网络延迟"
    # game/Submods/MAICA_ChatSubmod/header.rpy:841
    old "Session quality review: [persistent.maica_setting_dict.get('gen_quality_chk')]"
    new "会话质量检测: [persistent.maica_setting_dict.get('gen_quality_chk')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:843
    old "Require MNerve to check generation quality after session exceeds 3 rounds.\n+ Quantitatively evaluate generation quality\n- Extra consumation of MNerve"
    new "对话长度超过3轮后, 在每轮对话结束时, 要求MNerve介入检查输出合理性.\n+ 量化地检测判断会话劣化情况, 以免用户注意不到\n- 产生额外的MNerve开销"
    # game/Submods/MAICA_ChatSubmod/header.rpy:985
    old "MVista images"
    new "MVista图片"
    # game/Submods/MAICA_ChatSubmod/header.rpy:987
    old "View and manage MVista images.\n* Please read TOS carefully and be responsible for your own privacy"
    new "查看和管理用于MVista的图片.\n* 请仔细阅读TOS, 对你自己的隐私负责"
    # game/Submods/MAICA_ChatSubmod/header.rpy:995
    old "View and manage MVista images.\n! MVista not unlocked, please continue chatting with Monika patiently or send her letters"
    new "查看和管理用于MVista的图片.\n! MVista尚未解锁, 请继续和莫妮卡交互或送信, 并耐心等待"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1150
    old "Choose images | "
    new "选择图片 | 当前已选择 "
    # game/Submods/MAICA_ChatSubmod/header.rpy:1150
    old " chosen"
    new " 张"
# TODO: Translation updated at 2025-12-05 19:39

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:581
    old "> Warning: current system 'non-unicode language' is not Chinese, expect possible encoding issues"
    new "> 警告: {color=#ff0000}当前系统非Unicode语言不是简体中文{/color}, 可能导致包含中文的响应出现问题"
# TODO: Translation updated at 2025-12-07 15:44

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:856
    old "Realtime post proceeding: [persistent.maica_setting_dict.get('pprt')]"
    new "实时后处理: [persistent.maica_setting_dict.get('pprt')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:858
    old "Enable backend sentence breaking and realtime post proceeding.\n* Suggested to enable in normal cases"
    new "启用后端自动断句和实时后处理功能.\n* 非特殊情况不建议关闭"
# TODO: Translation updated at 2025-12-19 17:00

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:860
    old "Input language detection: [persistent.maica_setting_dict.get('input_lang_detect')]"
    new "输入语言检测: [persistent.maica_setting_dict.get('input_lang_detect')]"
    # game/Submods/MAICA_ChatSubmod/header.rpy:862
    old "Raise a warning if input language is not target language.\n* Suggested to enable in normal cases"
    new "检测输入语言与目标生成语言是否相符.\n* 非特殊情况不建议关闭"
# TODO: Translation updated at 2025-12-22 18:12

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:1167
    old "Quit"
    new "退出"
# TODO: Translation updated at 2026-01-08 02:22

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:458
    old "MAICA: Provider applied, reconnecting"
    new "MAICA: 已切换节点, 正在重新连接"
# TODO: Translation updated at 2026-01-30 23:25

translate chinese strings:

    # game/Submods/MAICA_ChatSubmod/header.rpy:979
    old "Each session stores and applies history context independently.\n* Set to 0 to disable context (single round conversation)\n! Current session same as MSpire session, may cause confusing behaviour"
    new "每个session独立保存和应用对话记录.\n* 设为0以不记录和不使用对话记录(单轮对话)\n! 当前session与MSpire会话相同, 可能导致迷惑性的表现"
    # game/Submods/MAICA_ChatSubmod/header.rpy:982
    old "! Current main session is set to same as MSpire session which may cause unexpected issues.\n! Please avoid setting these the same value (except 0) unless you literally understand what you're doing."
    new "! 当前主会话与MSpire共用会话, 这可能导致行为和表现上的问题.\n! 如果你不清楚这意味着什么, 请不要将二者设为相同非0值."
    # game/Submods/MAICA_ChatSubmod/header.rpy:1069
    old "Enable MSpire cache.\n* Does not take effect if MSpire session not 0\n* Enforces default super params"
    new "启用MSpire缓存.\n* MSpire会话不为0时不生效\n* 会强制使用默认高级参数"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1076
    old "Enable MSpire cache.\n! MSpire session not 0, with which MSpire cache conflicts"
    new "启用MSpire缓存.\n! MSpire会话不为0, MSpire缓存不会生效"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1080
    old "Session MSpire uses.\n* Set to 0 to disable context (single round conversation)\n* MSpire will offer choice to continue if not 0\n! Currently same as main session, auto resetting disabled"
    new "MSpire使用的session.\n* 设为0以不记录MSpire(单轮对话)\n* 如果不设为0, MSpire对话将提供接续选项\n! 当前session与主会话相同, 自动清空已禁用"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1086
    old "Session MSpire uses.\n* Set to 0 to disable context (single round conversation)\n* MSpire will offer choice to continue if not 0\n! This session resets before MSpire generation every time"
    new "MSpire使用的session.\n* 设为0以不记录MSpire(单轮对话)\n* 如果不设为0, MSpire对话将提供接续选项\n! MSpire每次生成前将自动清空该session"
    # game/Submods/MAICA_ChatSubmod/header.rpy:1087
    old "MSpire session"
    new "MSpire会话"translate chinese strings:

    old "Behavior preset: [maica_get_preset_name('behavior')]"
    new "行为预设: [maica_get_preset_name('behavior')]"
    old "Hyperparameter preset: [maica_get_preset_name('hyperparameter')]"
    new "超参数预设: [maica_get_preset_name('hyperparameter')]"
    old "These settings affect model and tool co-working behavior of MAICA.\n* Changing this preset will affect tools, enhancements and prompts around core model, together with time consumation\n! Do not modify unless you know what they exactly mean"
    new "这些设置影响MAICA的模型与工具协作行为.\n* 你选择的预设会影响模型的工具, 辅助, 提示词, 以及这些环节消耗的时间\n! 如果你不清楚其具体作用, 请不要修改"
    old "These settings affect core model's performance.\n* Changing this preset will directly affect core model's inference and sampling procedure\n! Do not modify unless you know what they exactly mean"
    new "这些设置影响MAICA核心模型的推理表现.\n* 你选择的预设直接影响核心模型的推理和采样\n! 如果你不清楚其具体作用, 请不要修改"
    old "The remaining settings in this section are managed by presets.\n! Do not modify manually unless you know what they exactly mean"
    new "本节中的剩余条目均由预设管理.\n! 如果你不清楚这些条目的具体作用, 请不要手动修改"
    old "Custom"
    new "自定义"
    old "Pure"
    new "纯粹"
    old "Reduce prompt text to minimum, use almost no tool, only retain critical correction.\n+ Fastest, nearly shortest TTFT\n- Almost no external sense, no in-game action ability"
    new "最大程度缩减prompt, 几乎不启用任何工具, 只保留核心纠错.\n+ 速度最快, TTFT接近最短\n- 几乎没有感知能力, 不能调用游戏内操作"
    old "Fluent"
    new "流利"
    old "No LLM intervention in pre-generation phase, use constant tools instead to reduce TTFT. Also reduced other tools.\n+ Relatively fast, nearly shortest TTFT\n* Limited external sense, has in-game action ability"
    new "不让常规LLM介入前生成阶段, 仅依靠常态工具, 优先压低TTFT. 适当减少其余工具.\n+ 速度较快, TTFT接近最短\n* 有较弱感知能力, 能调用游戏内操作"
    old "Dexterous"
    new "灵活"
    old "Aggressive tending calibration based on default, exchanges stability and rarely used functions for average speed.\n+ Relatively fast, relatively short TTFT\n+ Normal external sense, has in-game action ability"
    new "在默认行为基础上采用偏激进的调校, 牺牲稳定性和不常用的功能, 换取平均速度.\n+ 速度较快, TTFT较短\n+ 有正常感知能力, 能调用游戏内操作"
    old "Balanced (default)"
    new "均衡(默认)"
    old "Default behavior of MAICA. Field-tested balanced calibration, performs best overall in most cases.\n* Decent speed, decent TTFT\n+ Normal external sense, has in-game action ability"
    new "MAICA的默认行为. 久经考验的平衡调校, 在绝大多数情况下表现最佳.\n* 速度中等, TTFT中等\n+ 有正常感知能力, 能调用游戏内操作"
    old "Complete"
    new "完全"
    old "Almost complete feature set of generation assistance enabled. May perform better under extreme circumstances, but normally just wasting time.\n- Slowest, longest TTFT\n+ Normal external sense, has in-game action ability"
    new "几乎完整启用生成辅助功能集. 在极端情况下可能表现更好, 但一般都是浪费时间.\n- 速度最慢, TTFT最长\n+ 有正常感知能力, 能调用游戏内操作"
    old "Eager"
    new "贪婪"
    old "Fixed seed, eager sampling.\n! Not recommended for normal cases"
    new "固定种子, 贪婪采样.\n! 非特殊情况不推荐"
    old "Cautious"
    new "胆怯"
    old "Lower temperature.\n! Not recommended for normal cases"
    new "较低的温度.\n! 非特殊情况不推荐"
    old "Standard (default)"
    new "标准(默认)"
    old "Default super params of MAICA. Field-tested balanced calibration, performs best overall in most cases."
    new "MAICA的默认超参数. 久经考验的平衡调校, 在绝大多数情况下表现最佳."
    old "Aggressive"
    new "冒进"
    old "Higher temperature.\n! Not recommended for normal cases"
    new "较高的温度和采样范围.\n! 非特殊情况不推荐"
translate chinese strings:

    old "MAICA: Input is empty"
    new "MAICA: 输入为空"

    old "MAICA: Custom MFocus information has reached the 512-item limit"
    new "MAICA: 自定义MFocus信息已达512条上限"

    old "MAICA: A custom MFocus information item cannot exceed 1536 bytes"
    new "MAICA: 单条自定义MFocus信息不能超过1536字节"

    old "MAICA: Identical content already exists"
    new "MAICA: 已存在相同内容"

    old "Reset chat session length"
    new "重置会话长度"

    old "Write Event information to the log"
    new "输出Event信息到日志"

    old "Push sentence-splitting test"
    new "推送分句测试"

    old "Push chat loop"
    new "推送聊天loop"

    old "Push MSpire"
    new "推送MSpire"

    old "Push maica_mpostal_read"
    new "推送maica_mpostal_read"

    old "Push maica_mpostal_load"
    new "推送maica_mpostal_load"

    old "Push maica_raw_context_example"
    new "推送maica_raw_context_example"

    old "Show maica_gen_quality_chk_notify 0.3"
    new "显示maica_gen_quality_chk_notify 0.3"

    old "Show maica_gen_quality_chk_notify 0.6"
    new "显示maica_gen_quality_chk_notify 0.6"

    old "Show maica_gen_quality_chk_notify 0.9"
    new "显示maica_gen_quality_chk_notify 0.9"
