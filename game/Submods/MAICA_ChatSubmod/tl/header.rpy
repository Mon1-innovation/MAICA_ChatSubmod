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
    new "Export to submod root directory"

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
    new "Log level of submod_log.log: [logging.getLevelName(store.mas_submod_utils.submod_log.level)]"

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
    new "Using chat session: [persistent.maica_setting_dict.get('mspire_session')]"

    # game/Submods/MAICA_ChatSubmod/header.rpy:584
    old "MSpire所使用的会话\nMSpire使用过多可能会导致模型定位混乱"
    new "Use chat session for MSpire\nMay lead to response pattern corruption."

