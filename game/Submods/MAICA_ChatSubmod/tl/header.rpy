

translate english strings:


    old "未连接"
    new "Not connected"


    old "已连接"
    new "Connection established"


    old "已断开"
    new "Connection closed"


    old "> MAICA通信状态: [maica.maica.status]|[maica.maica.MaicaAiStatus.get_description(maica.maica.status)]"
    new "> MAICA connection status: [maica.maica.status]|[maica.maica.MaicaAiStatus.get_description(maica.maica.status)]"


    old "> Websocket:[stat]"
    new "> Websocket:[stat]"


    old "> 生成令牌"
    new "> Generate token"


    old "> 使用已保存令牌连接"
    new "> Connect with current token"


    old "上传存档信息"
    new "> Upload savefile information"


    old "重置当前对话"
    new "> Reset current session"


    old "导出当前对话"
    new "> Export current session"


    old "退出当前DCC账号"
    new "> Lougout current account"


    old "> MAICA对话设置 *部分选项需要重新连接"
    new "> MAICA chat settings *some options may need reconnection"


    old "累计对话轮次: [store.maica.maica.stat.get('message_count')]"
    new "Total conversation rounds: [store.maica.maica.stat.get('message_count')]"


    old "累计收到Token: [store.maica.maica.stat.get('received_token')]"
    new "Total tokens recieved: [store.maica.maica.stat.get('received_token')]"


    old "重置统计数据"
    new "Reset statistics"


    old "自动重连: [persistent.maica_setting_dict.get('auto_connect')]"
    new "Auto reconnect: [persistent.maica_setting_dict.get('auto_connect')]"


    old "连接断开时自动重连"
    new "Automatically reconnect on connection close"


    old "当前MAICA模型: [persistent.maica_setting_dict.get('maica_model')]"
    new "Current MAICA model: [persistent.maica_setting_dict.get('maica_model')]"


    old "maica_main：完全能力模型，maica_core: 核心能力模型\n完全能力的前置响应延迟偏高"
    new "maica_main: MAICA full functionality; maica_core: MAICA LLM functionality\nmaica_main has a higher response latency"


    old "目标语言: [persistent.maica_setting_dict.get('target_lang')]"
    new "Target language: [persistent.maica_setting_dict.get('target_lang')]"


    old "你与莫妮卡的沟通语言\n通过system prompt实现, 不能保证输出语言严格正确"
    new "The language you prefer recieving\nAchieved by modding system prompt, cannot guarantee correct output"


    old "使用高级参数: [persistent.maica_setting_dict.get('use_custom_model_config')]"
    new "Use advanced parameters: [persistent.maica_setting_dict.get('use_custom_model_config')]"


    old "在使用前, 请务必查看子模组根目录的custom_modelconfig.json\n否则可能导致意料之外的问题\n子模组将读取该json作为对话参数"
    new "Make sure config file custom_modelconfig.json makes sense before use"


    old "刷新参数"
    new "Flush options"


    old "使用存档数据: [persistent.maica_setting_dict.get('sf_extraction')]"
    new "Use persistent file: [persistent.maica_setting_dict.get('sf_extraction')]"


    old "关闭时, 模型将不会使用存档数据\n在开启前请务必先上传存档"
    new "Decides if use uploaded savefile or not\nMust have savefile uploaded if set to on"


    old "当前使用会话: [persistent.maica_setting_dict.get('chat_session')]"
    new "Session currently in use: [persistent.maica_setting_dict.get('chat_session')]"


    old "chat_session为0为单轮对话模式, 不同的对话之间相互独立, 需要分别上传存档"
    new "Disable session storage by setting chat_session 0. Sessions use savefiles individually"


    old "输出到控制台: [persistent.maica_setting_dict.get('console')]"
    new "Debugging console: [persistent.maica_setting_dict.get('console')]"


    old "在对话期间是否使用console显示相关信息, wzt的癖好\n说谁呢, 不觉得这很酷吗"
    new "Show debugging console while chatting\nI think this looks cool xd"


    old "清除玩家补充信息: 当前共有[len(persistent.mas_player_additions)]条"
    new "Purge additional player preferences: currently [len(persistent.mas_player_additions)]"


    old "由你补充的一些数据"
    new "Player complemented preferences data"


    old "导出至根目录"
    new "Export to directory"


    old "导出至game/Submods/MAICA_ChatSubmod/player_information.txt"
    new "Export to game/Submods/MAICA_ChatSubmod/player_information.txt"


    old "保存设置"
    new "Save settings"


    old "输入 DCC 账号用户名"
    new "Enter DCC username "


    old "或"
    new "or "


    old "输入 DCC 账号邮箱"
    new "Enter DCC register email"


    old "请输入DCC 账号邮箱"
    new "Enter DCC register email"


    old "输入 DCC 账号密码"
    new "Enter DCC password"


    old "请输入DCC 账号密码"
    new "Enter DCC password"


    old "连接至服务器生成MAICA令牌"
    new "Generate token online"


    old "生成MAICA令牌"
    new "Generate token"


    old "取消"
    new "Cancel"



translate english strings:


    old "上传成功"
    new "Upload success"


    old "上传失败"
    new "Upload failed"


    old "加载高级参数失败, 查看submod_log.log来获取详细原因"
    new "Failed initializing advanced params, check submod_log.log"


    old "自动重连: [persistent.maica_setting_dict.get('auto_reconnect')]"
    new "Auto reconnect: [persistent.maica_setting_dict.get('auto_reconnect')]"


    old "控制台字体: [persistent.maica_setting_dict.get('console_font')]"
    new "Console font: [persistent.maica_setting_dict.get('console_font')]"


    old "console使用的字体\nmplus-1mn-medium.ttf为默认字体\nSarasaMonoTC-SemiBold.ttf对于非英文字符有更好的显示效果"
    new "Decides what font should console display in. \nmplus-1mn-medium.ttf for default, SarasaMonoTC-SemiBold.ttf may behave better with non-ascii characters."


    old "由你补充的一些数据, 增删后需要重新上传存档"
    new "User defined preference data, needs re-uploading savefile to take effect"


    old "增加信息"
    new "Add preference"


    old "增加信息的事件将于关闭设置后推送"
    new "Preference addition will be sent on closing settings"


    old "点击后将推送相关事件"
    new "Click me to push events"


    old "请输入DCC 账号用户名"
    new "Enter DCC account username"



translate english strings:


    old "编辑信息"
    new "Edit information"


    old "MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"
    new "MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"


    old "是否允许由MSpire生成的对话, MSpire不受MFocus影响, 需要关闭重复对话"
    new "Enable or disable MSpire topics generation. Turn off repetive conversation to take effect."


    old "对话范围编辑"
    new "Edit topic range"


    old "范围为维基百科的category页面"
    new "The range should be the title of a wikipedia category page"


    old "间隔: [persistent.maica_setting_dict.get('mspire_interval')]分钟"
    new "Interval: [persistent.maica_setting_dict.get('mspire_interval')] Minute(s)"


    old "MSpire对话的最低间隔分钟"
    new "The minimum interval triggering MSpire"


    old "submod_log.log 等级:[logging.getLevelName(store.mas_submod_utils.submod_log.level)]"
    new "submod_log.log verbosity: [logging.getLevelName(store.mas_submod_utils.submod_log.level)]"


    old "这将影响submod_log.log中每条log的等级, 低于该等级的log将不会记录\n这也会影响其他子模组"
    new "Filter lower level logs\nThis affects every installed submod"



translate english strings:


    old "{a=https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Document.txt#L81}{i}{u}MAICA 官方文档{/i}{/u}{/a}"
    new "{a=https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Document.txt#L81}{i}{u}Official document of MAICA API{/i}{/u}{/a}"


    old "{a=https://www.openaidoc.com.cn/api-reference/chat}{i}{u}OPENAI 中文文档{/i}{/u}{/a}"
    new "{a=https://platform.openai.com/docs/api-reference/chat}{i}{u}OPENAI documents{/i}{/u}{/a}"


    old "模型选择的范围, 模型考虑概率质量值在前 top_p 的标记的结果, 因此，0.1 意味着仅考虑概率质量值前 10% 的标记"
    new "The token choice range in sequence of probability. Model will only choose the next token from the top_p/1 former part of all tokens."


    old "模型输出的随机性, 较高的值会使输出更随机, 而较低的值则会使其更加专注和确定"
    new "The randomness of output. Temperature was added to token weights to dilute their default probabilities, so higher temperature suggests creativity and lower suggests precision."


    old "模型输出的长度限制, 较高的值会使输出更长"
    new "The max length model can output in a single round. Model will try to fit this value but oversized responses will be chopped."


    old "频率惩罚, 正值基于新标记在文本中的现有频率对其进行惩罚, 降低模型重复相同行的可能性"
    new "Higher Frequency penalty prevents model from repeating one pattern for times. Minimum was limited to 0.2 by MAICA to avoid catastrophic repetition."


    old "正值基于新标记出现在文本中的情况对其进行惩罚, 增加模型谈论新话题的可能性"
    new "Higher Presence penalty prevents model from repeating the input, enhances the possibility of topic switching."


    old "0时只调用MFocus直接选择的工具. 当其为1时总是会调用时间与节日工具. 当其为2时还会额外调用日期工具.\n为2时, 且mas_geolocation存在, tnd_aggressive还会额外调用当前天气工具.\n可能补偿MFocus命中率低下的问题, 但也可能会干扰模型对部分问题的判断."
    new "Set 0 for no MFocus enforcing. Set 1 for enforcing time and events. Set 2 for enforcing time, date, events and weather(if possible). May offset low MFocus hit rate but may also cause misunderstanding of queries."


    old "总是尽可能使用MFocus的最终输出替代指导构型信息. 启用此功能可能提升模型的复杂信息梳理能力 \n但也可能会造成人称或格式的混乱"
    new "Set true for always using MFocus final answer instead of combined instructs if possible. May improve capability of concluding information but may also result in confusion in personality and response format."


    old "指定sfe_aggressive为true将总是以用户的真名替代prompt中的[[player]字段. \n启用此功能可能有利于模型理解玩家的姓名, 但也可能会造成总体拟合能力的下降和信息编造"
    new "Set true for always using player name in place of [[player]s in prompts. May help model understanding player's name but may also result in overall performance decline and information makeups."


    old "当esc_aggressive为true时会调用agent模型对MFocus联网搜集的信息整理一次.\n 启用此功能会改善模型对联网检索信息的专注能力, 但也会降低涉及联网搜索query的响应速度."
    new "Set true for concluding internet information gathered by AgentLM again. Helps model focusing on search results but will lag specific responses."


    old "累计MSpire轮次: [store.maica.maica.stat.get('mspire_count')]"
    new "Total MSpire rounds: [store.maica.maica.stat.get('mspire_count')]"


    old "高级参数会大幅影响模型的表现"
    new "Advanced params can impact model performance severely, use with extreme care."


    old "设置高级参数"
    new "Adjust advanced params"


    old "关闭时, 模型将不会使用存档数据\n每次重启游戏将自动上传存档"
    new "Set false for not uploading savefiles. Savefile is uploaded on game launching by default."


    old "间隔"
    new "Frequency"


    old "[persistent.maica_setting_dict.get('mspire_interval')]分钟"
    new "[persistent.maica_setting_dict.get('mspire_interval')] minutes"


    old "使用会话: [persistent.maica_setting_dict.get('mspire_session')]"
    new "Using session: [persistent.maica_setting_dict.get('mspire_session')]"


    old "MSpire所使用的会话\nMSpire使用过多可能会导致模型定位混乱"
    new "Use chat session for MSpire\nMay lead to response pattern corruption."



translate english strings:


    old "验证失败, 请检查账号密码"
    new "Authentication failed, recheck your account and password"


    old "验证成功"
    new "Authentication passed"


    old "会话已重置, 请重新连接MAICA服务器"
    new "Session reset, please reconnect to MAICA server"


    old "已导出至game/Submods/MAICA_ChatSubmod/chat_history.txt"
    new "Exported to game/Submods/MAICA_ChatSubmod/chat_history.txt"


    old "正在上传设置"
    new "Uploading settings"


    old "不能上传设置, 请等待MAICA准备好聊天\n请等待状态码改变后手动上传设置"
    new "Please ensure connection is ready first"


    old "> 警告: 与 Better Loading 不兼容"
    new "> Warning: Blessland is not compatible with Better Loading"


    old "> 手动上传设置"
    new "> Upload settings"


    old "> 手动上传设置 [[不能上传, 因为MAICA未准备好/忙碌中]"
    new "> Upload settings [[Ensure connection ready first]"


    old "> 重置当前对话"
    new "> Reset current chat session"


    old "> 导出当前对话"
    new "> Export current conversation history"


    old "> 退出当前DCC账号"
    new "> Logout"


    old " √ MAICA 官方服务器"
    new " √ Official MAICA provider"


    old "设备: "
    new "Cluster: "


    old "当前模型: "
    new "Mode: "


    old "> 使用该节点"
    new "> Switch to provider"


    old "更新节点列表"
    new "Refresh providers list"


    old "关闭"
    new "Close"


    old "当nsfw_acceptive为true时会改变system指引, 使模型对NSFW场景更为宽容.\n 启用此功能可能提高特定场合表现, 但也可能会造成模型核心能力下降和注意力混乱.\n请注意, 目前为止MAICA尚未使用任何NSFW数据集进行训练, 因此nsfw_acceptive的效果十分薄弱.\n 此后或许会有针对性的改善."
    new "Enabling may improve performance in particular occasion.\nBut also may result in overall performance decrease."


    old "服务提供节点: [MaicaProviderManager.get_server_by_id(persistent.maica_setting_dict.get('provider_id')).get('name', 'Unknown')]"
    new "Current provider: [MaicaProviderManager.get_server_by_id(persistent.maica_setting_dict.get('provider_id')).get('name', 'Unknown')]"


    old "设置服务器节点"
    new "Choose provider"


    old "范围为维基百科的category页面\n如果无法找到catrgory将会提示错误输入"
    new "Accepts existing categories of wikipedia\nWill fail if category doesn't exist"


    old "重置设置"
    new "Reset defaults"


    old "设置已重置"
    new "Reset finished"


    old "改为用户名登录"
    new "Use username instead"


    old "改为邮箱登录"
    new "Use Email instead"




translate english strings:


    old "MAICA官方前端子模组"
    new "MAICA Official Submod Frontend"


    old "> 无法验证版本号, 如果出现问题请更新至最新版"
    new "> Cannot verify version, try updating submod yourself if problems encountered"


    old "> 当前版本已不再支持, 请更新至最新版"
    new "> Support has ended for current version, please update submod"


    old "> 更新日志与服务状态"
    new "> Changelogs and serving status"


    old "※ 使用MAICA Blessland, 即认为你同意 {a=https://maica.monika.love/tos_zh}{i}{u}MAICA服务条款{/i}{/u}{/a}"
    new "※ By using MAICA Blessland, you have acknowledged and agree to obey {a=https://maica.monika.love/tos_en}{i}{u}MAICA TOS{/i}{/u}{/a}"


    old "算了"
    new "Nevermind"


    old "粘贴"
    new "Paste"



translate english strings:


    old "> 更新日志与服务状态 {size=-10}*有新更新"
    new "> Update and service status tracker {size=-10}* Update available"


    old "√ 已启用"
    new "√ Enabled"


    old "× 已禁用"
    new "× Disabled"


    old "※ 当前不满足触发条件"
    new "※ Trigger condition not satisfied"


    old "{a=https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Document.txt}{i}{u}MAICA 官方文档{/i}{/u}{/a}"
    new "{a=https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Document.txt}{i}{u}MAICA Official API references{/i}{/u}{/a}"


    old "{size=-10}注意: 只有已被勾选(标记了X)的高级设置才会被使用, 未使用的设置将使用服务端的默认设置"
    new "{size=-10}Notice: Only checked (X) advanced settings will take effect, unchecked ones will remain default"


    old "{size=-10}你当前未启用'使用高级参数', 该页的所有设置都不会生效!"
    new "{size=-10}You have not enabled advanced parameters, thus settings on this page will not take effect!"


    old "{size=-10}================超参数================"
    new "{size=-10}================Super params================"


    old "{size=-10}================偏好================"
    new "{size=-10}================Preferences================"


    old "相当于pre_additive数值轮次的历史对话将被加入MFocus.\n此功能强度越高, 越可能提高MFocus在自然对话中的触发率, 但也越可能干扰MFocus的判断或导致其表现异常."
    new "Rounds equal to pre_additive value will be added for MFocus to analyze.\nMay improve MFocus accuracy performance, but may also result in misbehavior."


    old "相当于post_additive数值轮次的历史对话将被加入MTrigger.\n此功能强度越高, 越可能提高MTrigger在自然对话中的触发率, 但也越可能干扰MTrigger的判断或导致其表现异常."
    new "Rounds equal to post_additive value will be added for MTrigger to analyze.\nMay improve MTrigger accuracy performance, but may also result in misbehavior."


    old "当amt_aggressive为true时会要求MFocus预检MTrigger内容(若存在), 以告知核心模型要求是否可以完成. \n启用此功能会改善MTrigger与核心模型的表现失步问题, 但也会降低涉及MTrigger对话的响应速度.\n当对话未使用MTrigger或仅有好感触发器, 此功能不会生效."
    new "Set to true to pre-analyze MTrigger items by MFocus(if both exists) to inform core model if request could be done. \nMay improve synchronousity of MTrigger, but also increases delay."


    old "每个会话累计Token: [store.maica.maica.stat.get('received_token_by_session')]"
    new "Overall tokens recieved: [store.maica.maica.stat.get('received_token_by_session')]"


    old "当前用户: [store.maica.maica.user_acc]"
    new "Current user: [store.maica.maica.user_acc]"


    old "会话长度: "
    new "Chat session length: "


    old "此参数意在缓解对话历史累积导致的响应速度过慢问题. 请避免将其设置得过小, 否则可能影响模型的正常语言能力."
    new "This setting is intended to reduce performance issue when history goes too long. Choose a reasonable value or model coherence may be impacted."


    old "[persistent.maica_setting_dict.get('max_history_token')]"
    new "[persistent.maica_setting_dict.get('max_history_token')]"


    old "上传对话历史到会话 '[store.maica.maica.chat_session]'"
    new "Recover history to chat session '[store.maica.maica.chat_session]'"


    old "MTrigger 列表"
    new "Mtrigger trigger list"


    old "{size=-10}※ 使用MAICA Blessland, 即认为你同意 {a=https://maica.monika.love/tos_zh}{i}{u}MAICA服务条款{/i}{/u}{/a}"
    new "{size=-10}※ By using MAICA Blessland, you agree to {a=https://maica.monika.love/tos_en}{i}{u}MAICA TOS{/i}{/u}{/a}"



translate english strings:


    old "未找到game/Submods/MAICA_ChatSubmod/chat_history.txt"
    new "game/Submods/MAICA_ChatSubmod/chat_history.txt not found"


    old "暂未上传设置, 请等待MAICA准备好聊天\n待状态码改变后手动上传设置"
    new "Please ensure connection is ready before uploading settings"


    old "> 警告: 与 Log Screen 一起使用时, 请将'submod_log'的详细程度提高至info及以上"
    new "> Warning: set 'submod_log' logger verbosity to 'info' or lower when using with Log Screen"


    old "> 手动上传设置 [[请先使MAICA完成连接]"
    new "> Manually upload settings [[Ensure connection is ready first]"


    old "> 上传对话历史到会话 '[store.maica.maica.chat_session]'"
    new "> Upload chat history to session '[store.maica.maica.chat_session]'"


    old "> MAICA对话设置 {size=-10}*部分选项重新连接生效"
    new "> MAICA chat settings {size=-10}*May need restarting to take effect"


    old "重现惩罚, 正值基于新标记出现在文本中的情况对其进行惩罚, 增加模型谈论新话题的可能性"
    new "Higher Presence penalty prevents model from repeating the input, enhances the possibility of topic switching."


    old "当其为0时只调用MFocus直接选择的工具. 为1时总是会调用时间与节日工具. 为2时还会额外调用日期工具.\n当其为2且mas_geolocation存在时, tnd_aggressive还会额外调用当前天气工具.\n越高越可能补偿MFocus命中率低下的问题, 但也越可能会干扰模型对部分问题的判断."
    new "Set 0 for no MFocus enforcing. Set 1 for enforcing time and events.\nSet 2 for enforcing time, date, events and weather(if possible).\nMay offset low MFocus hit rate but may also cause misunderstanding of queries."


    old "总是尽可能使用MFocus的最终输出替代指导构型信息.\n启用可能提升模型的复杂信息梳理能力, 但也可能会造成速度下降或专注扰乱"
    new "Set true for always using MFocus final answer instead of combined instructs if possible.\nMay improve capability of concluding information but may also result in confusion in personality and response format."


    old "总是以用户的真名替代prompt中的[[player]字段.\n启用此功能可能有利于模型理解玩家的姓名, 但也可能会造成总体拟合能力的下降和信息编造"
    new "Set true for always using player name in place of [[player]s in prompts.\nMay help model understanding player's name but may also result in overall performance decline and information makeups."


    old "调用agent模型对MFocus联网搜集的信息整理一次.\n启用此功能会改善模型对联网检索信息的专注能力, 但也会降低涉及联网搜索query的响应速度."
    new "Set true for concluding internet information gathered by AgentLM again.\nHelps model focusing on search results but will lag specific responses."


    old "要求MFocus预检MTrigger内容(若存在), 以告知核心模型要求是否可以完成. \n启用此功能会改善MTrigger与核心模型的表现失步问题, 但也会降低涉及MTrigger对话的响应速度.\n当对话未使用MTrigger或仅有好感触发器, 此功能不会生效."
    new "Set true to request MFocus pre-analyzing MTrigger triggers on query's possibility.\nMay benefit on core-trigger sync but will lag specific responses.\nWill not take effect if no trigger aside from affection is activated."


    old "改变system指引, 使模型对NSFW场景更为宽容.\n经测试启用此功能对模型总体表现(意外地)有利, 但也存在降低模型专注能力和造成混乱的风险."
    new "Set true to guide core model being more tolerant on toxic scenes.\nMay improve overall core performance (unexpectedly but proved true)\n but may also decrease attention performance and cause confusion."



translate english strings:


    old "MAICA: 存档上传成功"
    new "MAICA: Savefile uploaded successfully"


    old "MAICA: 存档上传失败"
    new "MAICA; Savefile failed to upload"


    old "MAICA: 会话已重置"
    new "MAICA: Chat session reset"


    old "MAICA: 历史已导出至game/Submods/MAICA_ChatSubmod/chat_history.txt"
    new "MAICA: History exported to game/Submods/MAICA_ChatSubmod/chat_history.txt"


    old "MAICA: 未找到历史game/Submods/MAICA_ChatSubmod/chat_history.txt"
    new "MAICA: History not found at game/Submods/MAICA_ChatSubmod/chat_history.txt"


    old "MAICA: 历史上传成功"
    new "MAICA: History uploaded"


    old "MAICA: 已上传设置"
    new "MAICA: Settings uploaded"


    old "MAICA: 请等待连接就绪后手动上传"
    new "MAICA: Do a manual upload after connection ready"


    old "MAICA: 加载高级参数失败, 查看submod_log.log获取详细原因"
    new "MAICA: Advanced settings failed to serialize, check submod_log.log"


    old "MAICA: 设置已重置"
    new "MAICA: Settings reset"



translate english strings:


    old "> Websocket:"
    new "> Websocket:"


    old "MTrigger空间使用情况: "
    new "MTrigger space usage: "


    old "空间占用: -"
    new "Space used: -"


    old "空间占用: request"
    new "Space used: request"


    old "空间占用: table"
    new "Space used: table"


    old "搜索方式: [persistent.maica_setting_dict.get('mspire_search_type')]"
    new "Search type: [persistent.maica_setting_dict.get('mspire_search_type')]"

    old "{size=-10}* 如果对话卡住了, 点我断开连接"
    new "{size=-10}* If chat is stuck, click me to disconnect"

    old "{size=-10}※ 还没有DCC账号? {a=https://forum.monika.love/signup}{i}{u}注册一个{/u}{/i}{/a}"
    new "{size=-10}※ Don't have DCC account yet? {a=https://forum.monika.love/signup}{i}{u}Sign up.{/u}{/i}{/a}"

    old "严格反劫持: [persistent.maica_setting_dict.get('strict_mode')]"
    new "Strict anti-hijack: [persistent.maica_setting_dict.get('strict_mode')]"



translate english strings:


    old "失败原因:"
    new "Reason:"


    old "> 你当前的MAS生成版本过旧, 可能影响正常运行, 请升级至最新生成版本"
    new "> Your current MAS version is below the lowest compatible version, please update"


    old "> 注意: 当空间不足时将自动关闭部分MTrigger!"
    new "> Notice: Some MTriggers will be disabled if content length exceeds!"


    old "{size=15}因能力有限, 阅读信件后信件列表将在返回太空教室后重新显示."
    new "{size=15}MPostal list will be shown after returning to the spaceroom."


    old "信件状态: "
    new "MPostal status:"


    old "寄信时间: "
    new "Last post sent at: "


    old "\n[player]: \n"
    new "\n[player]: \n"


    old "[m_name]: \n"
    new "[m_name]: \n"


    old "阅读[player]写的信"
    new "Read [player]'s letter"


    old "阅读[m_name]的回信"
    new "Read [m_name]'s reply"


    old "累计发信数: [store.maica.maica.stat.get('mpostal_count')]"
    new "MPostal sent count: [store.maica.maica.stat.get('mpostal_count')]"


    old "严格模式下, 将会在每次发送时携带cookie信息"
    new "Strict anti-hijack enables MAICA websocket cookie"


    old "状态码更新速度"
    new "Status code refreshing frequency"


    old "在Submod界面处的状态码更新频率"
    new "The refreshing frequency of status code on Submod screen"


    old "查看MPostals往来信件"
    new "Reread MPostal letters"

    old "回信时显示控制台"
    new "Show console on MPostal writing reply"



translate english strings:


    old "重新寄信"
    new "Resend mail"


    old "平均功耗: "
    new "Mean power consumption: "


    old "下次更新数据"
    new "Analytics refresh"


    old "{size=-10}如果这里没有你的时区, 请根据你当地的UTC时间选择"
    new "{size=-10}If your timezone is not listed here, decide by your local UTC timezone."


    old "根据语言自动选择"
    new "Language default"


    old "根据系统时区自动选择"
    new "System default"


    old "选择时区: [persistent.maica_advanced_setting.get('tz') or 'Asia/Shanghai' if store.maica.maica.target_lang == store.maica.maica.MaicaAiLang.zh_cn else 'America/Indiana/Vincennes']"
    new "Set timezone: [persistent.maica_advanced_setting.get('tz') or 'Asia/Shanghai' if store.maica.maica.target_lang == store.maica.maica.MaicaAiLang.zh_cn else 'America/Indiana/Vincennes']"


    old "控制台log等级: [logging.getLevelName(store.maica.maica.console_logger.level)]"
    new "Console logging verbosity: [logging.getLevelName(store.maica.maica.console_logger.level)]"


    old "这将影响控制台中每条log的等级, 低于该等级的log将不会记录"
    new "Filter lower level logs shown in console"


    old "查看后端负载"
    new "Check server load status"



translate english strings:


    old "信件回复时间"
    new "MPostal reply delay"


    old "回信所需要的最低时间"
    new "The minimum delay before MPostal replies"



translate english strings:


    old "!已启用42seed"
    new "!Seed locked to 42"


    old "锁定最佳实践"
    new "Enforce best practice"


    old "锁定seed为42, 该设置覆盖高级参数中的seed\n启用会完全排除生成中的随机性, 在统计学上稳定性更佳"
    new "Set seed to 42 and override the corresponding advanced section.\nThis removes the randomness in generation completely and performs better statistically."


    old "MSpire 使用缓存"
    new "Use cache for MSpire"


    old "启用MSpire缓存, 且使用默认高级参数并固定种子为42\n"
    new "Enable MSpire cache, disable advanced settings and set seed to 42 for MSpire.\n"



translate english strings:


    old "> 支持 MAICA"
    new "> Donate for MAICA"


    old "首先很感谢你有心捐赠.\n我们收到的捐赠基本上不可能回本, 但你不必有任何压力."
    new "We're grateful for your being willing to donate.\nThe donate will likely never cover our cost, but that's okay anyway."


    old "请注意, 向MAICA捐赠不会提供任何特权, 除了论坛捐赠页名单和捐赠徽章."
    new "Please note that donating to MAICA doesn't give you any actual privilege. It's simply donation."



translate english strings:


    old "> 向 MAICA 捐赠"
    new "> Donate to MAICA"


    old "!已启用最佳实践"
    new "!Best practice enabled"


    old "动态的天堂树林"
    new "Dynamic Heaven Forest"


    old "使用动态摇曳和改良光影的天堂树林, 略微增加渲染压力. 重启生效\n如果产生显存相关错误, 删减精灵包或禁用此选项"
    new "Use dynamic forest background with improved illumination\nIncreases render consume slightly. Restart to take effect\nRemove some spritepacks or disable this if VRAM overflows"


    old "seed范围错误, 请重新输入种子"
    new "Seed out of range, retry"


    old "请输入种子, 范围为0-99999"
    new "Choose a seed from 0-99999"



translate english strings:


    old "> 警告: 找不到证书, 你是不是忘记安装数据包了?"
    new "> Warning: no certification found, check datapack installation"


    old "> 打开官网"
    new "> Go to portal page"


    old "测试当前节点可用性"
    new "Test current node avaliability"


    old "使用MTrigger: [persistent.maica_setting_dict.get('enable_mt')]"
    new "MTrigger enabled: [persistent.maica_setting_dict.get('enable_mt')]"


    old "使用MFocus: [persistent.maica_setting_dict.get('enable_mf')]"
    new "MFocus enabled: [persistent.maica_setting_dict.get('enable_mf')]"


    old "请输入种子(整数)"
    new "Choose a seed (integer)"



translate english strings:


    old "> 警告: 与 Log Screen 一起使用时, 请将'submod_log'的过滤级别提高至info及以上"
    new "> Warning: set 'submod_log' logger verbosity to 'info' or lower when using with Log Screen"


    old "token权重过滤范围. 非常不建议动这个"
    new "Token weight filter percentage. Seriously do not touch this"


    old "token选择的随机程度. 数值越高, 模型输出会越偏离普遍最佳情况"
    new "The randomness tokens are chosen. Higher this value, larger the offset between model performance and generally best performance"


    old "模型一轮生成的token数限制. 一般而言不会影响表现, 只会截断超长的部分"
    new "The limit of tokens model can generate one round. Normally don't affect performance, but stops generating on hitting the limit"


    old "token频率惩罚. 数值越高, 反复出现的token越不可能继续出现, 一般会产生更短且更延拓的结果"
    new "Token frequency penalty. Higher this value, less likely repeatedly appeared tokens continue appearing, usually resulting in shorter and more expanding generation"


    old "token重现惩罚. 数值越高, 出现过的token越不可能再次出现, 一般会产生更跳跃的结果"
    new "Token presence penalty. Higher this value, less likely appeared tokens appear again, usually resulting in more jumping generation"


    old "即使MFocus未调用工具, 也提供一些工具的结果.\n+ 其值越高, 越能避免信息缺乏导致的幻觉, 并产生灵活体贴的表现\n- 其值越高, 越有可能产生注意力涣散和专注混乱"
    new "Acquire some information even if not called explicitly.\n+ Higher: keen and less hallucination\n- Higher: higher likeability of distraction and misfocusing"


    old "要求agent模型生成最终指导, 并替代默认MFocus指导.\n+ 信息密度更高, 更容易维持语言自然\n- 表现十分依赖agent模型自身的能力\n- 启用时会禁用tnd_aggressive"
    new "Require agent model to generate guidance instead of default MFocus mechanism.\n+ Higher information density and naturalness\n- Heavily depends on agent instruction following behavior\n- Disables tnd_aggressive"


    old "将prompt和引导中的[[player]字段替换为玩家真名.\n+ 模型对玩家的名字有实质性理解\n- 明显更容易发生表现离群和专注混乱"
    new "Replace [[player] in prompt with player's real name.\n+ Model has real understanding of player's name\n- Significantly higher likeability of performance offset and degration"


    old "在MFocus调用互联网搜索的情况下, 要求其整理一遍结果.\n+ 大多数情况下信息密度更高, 更容易维持语言自然\n- 涉及互联网搜索时生成速度更慢"
    new "Require MFocus to sort internet search results.\n+ Higher information density and naturalness in most cases\n- Higher time consumption when query involves searching internet"


    old "当MTrigger存在时, 要求MFocus预检玩家的请求并提供指导.\n+ 比较明显地改善MTrigger失步问题\n- 在少数情况下对语言的自然性产生破坏\n* 当对话未使用MTrigger或仅有好感触发器, 此功能不会生效"
    new "Require MFocus to precheck query for MTrigger.\n+ Significantly reduces MTrigger desync\n- Seldom negative impact on naturalness\n* Only works with MTrigger enabled"


    old "要求模型宽容正面地对待有毒内容.\n+ (出乎意料地)在大多数场合下对模型表现有正面作用, 即使不涉及有毒内容\n- 在少数情况下造成意料之外的问题"
    new "Require model to handle toxic content positively and pardonly.\n+ (Suprisingly) benefits overall performance in most cases\n- May lead to unexpected problems in rare cases"


    old "在MFocus介入时, 额外提供上下文以供分析. 范围0-5.\n+ 改善MFocus对连贯对话的理解能力\n- 明显更容易破坏MFocus的应答模式"
    new "Provide history context for MFocus, in range of 0-5 rounds.\n+ Improves MFocus' understanding to serial conversation\n- Significant risk of breaking MFocus reply pattern"


    old "在MTrigger介入时, 额外提供上下文以供分析. 范围0-5.\n+ 改善MTrigger对连贯对话的理解能力\n- 更容易破坏MTrigger的应答模式"
    new "Provide history context for MTrigger, in range of 0-5 rounds.\n+ Improves MTrigger's understanding to serial conversation\n- Risk of breaking MTrigger reply pattern"


    old "ws严格模式: [persistent.maica_setting_dict.get('strict_mode')]"
    new "Websocket strict mode: [persistent.maica_setting_dict.get('strict_mode')]"


    old "目标生成语言. 仅支持\"zh\"或\"en\".\n* 该参数不能100%保证生成语言是目标语言\n* 该参数影响范围广泛, 包括默认时区, 节日文化等, 并不止目标生成语言. 建议设为你的实际母语\n* 截至文档编纂时为止, MAICA官方部署的英文能力仍然弱于中文"
    new "Target generation language. Supports \"zh\" or \"en\".\n* Does not 100% guarantee generation language\n* This setting also affects default timezone, festivals, culture and more\n* Up to when this was written, MAICA official deployment's English performance is still weaker than Chinese"


    old "使用自定义高级参数: [persistent.maica_setting_dict.get('use_custom_model_config')]"
    new "Enable customized advanced parameters: [persistent.maica_setting_dict.get('use_custom_model_config')]"


    old "高级参数可能大幅影响模型的表现.\n* 默认的高级参数已经是实践中的普遍最优配置, 不建议启用"
    new "Advanced parameters could significantly affect the model's performance.\n* The default is already the best field-tested config, so it's not suggested to enable this"


    old "锁定seed为42, 该设置覆盖高级参数中的seed.\n* 启用会完全排除生成中的随机性, 在统计学上稳定性更佳, 且更易于复现"
    new "Designate seed to 42, which overrides seed in advanced parameters.\n* Removes randomness in generation, makes performance more stable and reproducable."


    old "关闭时, 模型将不会使用存档数据.\n* 每次重启游戏将自动上传存档数据"
    new "Model will ignore savefile data if this is disabled.\n* MAICA Blessland uploads savefile on each restart automatically"


    old "每个session独立保存和应用对话记录.\n* 设为0以不记录和不使用对话记录(单轮对话)"
    new "Each session stores and applies history context independently.\n* Set to 0 to disable context (single round conversation)"


    old "会话保留的最大长度. 范围512-28672.\n* 按字符数计算. 每3个ASCII字符只占用一个字符长度\n* 字符数超过限制后, MAICA会裁剪其中较早的部分, 直至少于限制的 2/3\n* 过大或过小的值可能导致表现和性能问题"
    new "Max length each session will preserve, in range of 512-28672.\n* Every 3 ASCII characters occupy one space\n* MAICA crops the former part of context on exceeding to no more than 2/3 left\n* Too high or too low value can cause performance and generation quality issues"


    old "启用MSpire缓存.\n* 会强制使用默认高级参数并固定最佳实践"
    new "Enable MSpire cache.\n* Forces default super params and best practice"
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
