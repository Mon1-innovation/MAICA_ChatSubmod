init -990 python:
    store.mas_submod_utils.Submod(
        author="P",
        name="MAICA Blessland",
        description="The official Submod frontend of MAICA",
        version='0.2.5',
        settings_pane="maica_setting_pane"
    )
init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="MAICA Blessland",
            user_name="Mon1_Innovation",
            repository_name="MAICA_ChatSubmod",
            update_dir="",
            attachment_id=None
        )

default persistent.maica_setting_dict = {
    "auto_reconnect":False,
    "maica_model":None,
    "use_custom_model_config":False,
    "sf_extraction":False,
    "chat_session":1,
    "console":True
}
default persistent.mas_player_additions = []

define maica_confont = "mod_assets/font/SarasaMonoTC-SemiBold.ttf"
#define "mod_assets/font/mplus-1mn-medium.ttf" # mas_ui.MONO_FONT
init 10 python:
    import logging
    maica_default_dict = {
        "auto_reconnect":False,
        "maica_model":None,
        "use_custom_model_config":False,
        "sf_extraction":True,
        "chat_session":1,
        "console":True,
        "console_font":maica_confont,
        "target_lang":None,
        "_event_pushed":False,
        "mspire_enable":True,
        "mspire_category":[],
        "mspire_interval":60,
        "mspire_session":0,
        "log_level":logging.DEBUG,
    }
    maica_default_dict.update(persistent.maica_setting_dict)
    persistent.maica_setting_dict = maica_default_dict.copy()

    if persistent.maica_setting_dict["maica_model"] is None:
        persistent.maica_setting_dict["maica_model"] = store.maica.maica.MaicaAiModel.maica_main
    if persistent.maica_setting_dict["target_lang"] is None:
        persistent.maica_setting_dict["target_lang"] = store.maica.maica.MaicaAiLang.zh_cn
    _maica_LoginAcc = ""
    _maica_LoginPw = ""
    _maica_LoginEmail = ""
    def _maica_clear():
        store._maica_LoginAcc = ""
        store._maica_LoginPw = ""
        store._maica_LoginEmail = ""
        store.mas_api_keys.api_keys.update({"Maica_Token":store.maica.maica.ciphertext})
        store.mas_api_keys.save_keys()

    @store.mas_submod_utils.functionplugin("ch30_preloop")
    def upload_persistent_dict():
        import copy
        d = copy.deepcopy(persistent.__dict__)
        d['_seen_ever'].clear()
        d['_mas_event_init_lockdb'].clear()
        d['_changed'].clear()
        d['_mas_event_init_lockdb'].clear()
        d['event_database'].clear()
        d['farewell_database'].clear()
        d['greeting_database'].clear()
        d['_mas_apology_database'].clear()
        d['_mas_compliments_database'].clear()
        d['_mas_fun_facts_database'].clear()
        d['_mas_mood_database'].clear()
        d['_mas_songs_database'].clear()
        d['_mas_story_database'].clear()
        d['_mas_affection_backups'] = None
        d['greeting_database'].clear()
        d['greeting_database'].clear()
        d['greeting_database'].clear()
        d['greeting_database'].clear()
        d['greeting_database'].clear()
        d['greeting_database'].clear()
        d['greeting_database'].clear()
        d['mas_playername'] = store.player
        if persistent._mas_player_bday:
            d['mas_player_bday'] = [persistent._mas_player_bday.year, persistent._mas_player_bday.month, persistent._mas_player_bday.day]
        d['mas_affection'] = store._mas_getAffection()
        del d['_preferences']
        for i in d:
            try:
                json.dumps(d[i])
            except:
                try:
                    d[i] = str(d[i])
                except:
                    d[i] = "REMOVED"
        res = store.maica.maica.upload_save(d)
        renpy.notify(_("上传成功") if res.get("success", False) else _("上传失败"))

    def reset_session():
        store.maica.maica.reset_chat_session()
        renpy.notify("会话已重置, 请重新连接MAICA服务器")
    def output_chat_history():
        with open(os.path.join("game", "Submods", "MAICA_ChatSubmod", "chat_history.txt"), 'w') as f:
            f.write(store.maica.maica.get_history().get("history", {}))
        renpy.notify("已导出至game/Submods/MAICA_ChatSubmod/chat_history.txt")
    
    def maica_apply_setting(ininit=False):
        store.maica.maica.auto_reconnect = persistent.maica_setting_dict["auto_reconnect"]
        if persistent.maica_setting_dict["use_custom_model_config"]:
            update_model_setting(ininit)
        else:
            store.maica.maica.modelconfig = {}
        store.maica.maica.sf_extraction = persistent.maica_setting_dict["sf_extraction"]
        store.maica.maica.chat_session = persistent.maica_setting_dict["chat_session"]
        store.maica.maica.model = persistent.maica_setting_dict["maica_model"]
        store.mas_ptod.font = persistent.maica_setting_dict["console_font"]
        store.maica.maica.target_lang = persistent.maica_setting_dict["target_lang"]
        store.maica.maica.mspire_category = persistent.maica_setting_dict["mspire_category"]
        store.mas_submod_utils.submod_log.level = persistent.maica_setting_dict["log_level"]
        store.maica.maica.mspire_session = persistent.maica_setting_dict["mspire_session"]
        store.mas_submod_utils.getAndRunFunctions()
    
    def change_chatsession():
        persistent.maica_setting_dict["chat_session"] += 1
        if persistent.maica_setting_dict["chat_session"] not in range(0, 10):
            persistent.maica_setting_dict["chat_session"] = 0
        
    def reset_player_information():
        persistent.mas_player_additions = []
    
    def export_player_information():
        with open(os.path.join("game", "Submods", "MAICA_ChatSubmod", "player_info.txt"), 'w') as f:
            f.write(json.dumps(persistent.mas_player_additions))
        renpy.notify("已导出至game/Submods/MAICA_ChatSubmod/player_information.txt")

    def update_model_setting(ininit = False):
        import os, json
        try:
            with open(os.path.join("game", "Submods", "MAICA_ChatSubmod", "custom_modelconfig.json"), "r") as f:
                store.maica.maica.modelconfig = json.load(f)
        except Exception as e:
            if not ininit:
                renpy.notify(_("加载高级参数失败, 查看submod_log.log来获取详细原因").format(e))
            store.mas_submod_utils.submod_log.error("Failed to load custom model config: {}".format(e))
    
    def change_loglevel():
        import logging
        l = [logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        curr = l.index(persistent.maica_setting_dict["log_level"])
        persistent.maica_setting_dict["log_level"] = l[(curr + 1) % len(l)]
    
    maica_apply_setting(True)
        
            

screen maica_setting_pane():
    python:
        import store.maica as maica
        stat = _("未连接") if not maica.maica.wss_session else _("已连接") if maica.maica.wss_session.keep_running else _("已断开")
        store.maica.maica.ciphertext = store.mas_getAPIKey("Maica_Token")
    vbox:
        xmaximum 800
        xfill True
        style_prefix "check"

        text _("> MAICA通信状态: [maica.maica.status]|[maica.maica.MaicaAiStatus.get_description(maica.maica.status)]"):
            xalign 1.0 yalign 0.0
            xoffset -10
            style "main_menu_version"
        text _("> Websocket:[stat]"):
            xalign 1.0 yalign 0.0
            xoffset -10
            style "main_menu_version"
        
        if True if not maica.maica.wss_session else not maica.maica.wss_session.keep_running:
            textbutton _("> 生成令牌"):
                action Show("maica_login")
                
            textbutton _("> 使用已保存令牌连接"):
                action Function(store.maica.maica.init_connect)

            
        else:
            #textbutton _("上传存档信息"):
            #    action Function(upload_persistent_dict)

            textbutton _("重置当前对话"):
                action Function(reset_session)

            textbutton _("导出当前对话"):
                action Function(output_chat_history)

            textbutton _("退出当前DCC账号"):
                action Function(store.maica.maica.close_wss_session)
    
        textbutton _("> MAICA对话设置 *部分选项需要重新连接"):
            action Show("maica_setting")

            
screen maica_setting():
    python:
        submods_screen = store.renpy.get_screen("submods", "screens")

        if submods_screen:
            _tooltip = submods_screen.scope.get("tooltip", None)
        else:
            _tooltip = None
    modal True
    zorder 215
    
    style_prefix "check"

    frame:
        vbox:
            xmaximum 1100
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 600
                xmaximum 1100
                xfill True
                yfill False
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1100
                    xfill True
                    yfill False
                    if renpy.config.debug:
                        hbox:
                            text "=====MaicaAi()====="
                        hbox:
                            text "ai.is_responding: [store.maica.maica.is_responding()]"
                        hbox:
                            text "ai.is_failed: [store.maica.maica.is_failed()]"
                        hbox:
                            text "ai.is_connected: [store.maica.maica.is_connected()]"
                        hbox:
                            text "ai.is_ready_to_input: [store.maica.maica.is_ready_to_input()]"
                        hbox:
                            text "ai.MaicaAiStatus.is_submod_exception: [store.maica.maica.MaicaAiStatus.is_submod_exception(store.maica.maica.status)]"
                        hbox:
                            text "ai.len_message_queue(): [store.maica.maica.len_message_queue()]"
                        hbox:
                            text "maica_chr_exist: [maica_chr_exist]"
                        hbox:
                            text "maica_chr_changed: [maica_chr_changed]"
                        hbox:
                            text "len(mas_rev_unseen): [len(mas_rev_unseen)]"
                        hbox:
                            text "=====MaicaAi() Finish====="

                    hbox:
                        text _("累计对话轮次: [store.maica.maica.stat.get('message_count')]")

                    hbox:
                        text _("累计MSpire轮次: [store.maica.maica.stat.get('mspire_count')]")

                    hbox:
                        text _("累计收到Token: [store.maica.maica.stat.get('received_token')]")
                    hbox:
                        textbutton _("重置统计数据"):
                            action Function(store.maica.maica.reset_stat)


                    hbox: 
                        textbutton _("自动重连: [persistent.maica_setting_dict.get('auto_reconnect')]"):
                            action ToggleDict(persistent.maica_setting_dict, "auto_reconnect", True, False)
                            hovered SetField(_tooltip, "value", _("连接断开时自动重连"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        textbutton _("当前MAICA模型: [persistent.maica_setting_dict.get('maica_model')]"):
                            action ToggleDict(persistent.maica_setting_dict, "maica_model", store.maica.maica.MaicaAiModel.maica_main, store.maica.maica.MaicaAiModel.maica_core)
                            hovered SetField(_tooltip, "value", _("maica_main：完全能力模型，maica_core: 核心能力模型\n完全能力的前置响应延迟偏高"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        textbutton _("目标语言: [persistent.maica_setting_dict.get('target_lang')]"):
                            action ToggleDict(persistent.maica_setting_dict, "target_lang", store.maica.maica.MaicaAiLang.zh_cn, store.maica.maica.MaicaAiLang.en)
                            hovered SetField(_tooltip, "value", _("你与莫妮卡的沟通语言\n通过system prompt实现, 不能保证输出语言严格正确"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)


                    hbox:
                        textbutton _("使用高级参数: [persistent.maica_setting_dict.get('use_custom_model_config')]"):
                            action ToggleDict(persistent.maica_setting_dict, "use_custom_model_config", True, False)    
                            hovered SetField(_tooltip, "value", _("在使用前, 请务必查看子模组根目录的custom_modelconfig.json\n否则可能导致意料之外的问题\n子模组将读取该json作为对话参数"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        textbutton _("刷新参数"):
                            action Function(store.update_model_setting)

                    hbox:
                        textbutton _("使用存档数据: [persistent.maica_setting_dict.get('sf_extraction')]"):
                            action ToggleDict(persistent.maica_setting_dict, "sf_extraction", True, False)
                            hovered SetField(_tooltip, "value", _("关闭时, 模型将不会使用存档数据\n每次重启游戏将自动上传存档"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        textbutton _("当前使用会话: [persistent.maica_setting_dict.get('chat_session')]"):
                            action Function(store.change_chatsession)
                            hovered SetField(_tooltip, "value", _("chat_session为0为单轮对话模式, 不同的对话之间相互独立, 需要分别上传存档"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        textbutton _("输出到控制台: [persistent.maica_setting_dict.get('console')]"):
                            action ToggleDict(persistent.maica_setting_dict, "console", True, False)
                            hovered SetField(_tooltip, "value", _("在对话期间是否使用console显示相关信息, wzt的癖好\n说谁呢, 不觉得这很酷吗"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        textbutton _("控制台字体: [persistent.maica_setting_dict.get('console_font')]"):
                            action ToggleDict(persistent.maica_setting_dict, "console_font", store.maica_confont, store.mas_ui.MONO_FONT)
                            hovered SetField(_tooltip, "value", _("console使用的字体\nmplus-1mn-medium.ttf为默认字体\nSarasaMonoTC-SemiBold.ttf对于非英文字符有更好的显示效果"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        textbutton _("清除玩家补充信息: 当前共有[len(persistent.mas_player_additions)]条"):
                            action Function(reset_player_information)
                            hovered SetField(_tooltip, "value", _("由你补充的一些数据, 增删后需要重新上传存档"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)


                        textbutton _("编辑信息"):
                            action [
                                SetDict(persistent.maica_setting_dict, "_event_pushed", True),
                                Function(renpy.notify, _("增加信息的事件将于关闭设置后推送")),
                                Function(store.MASEventList.push, "maica_mods_preferences")
                                ]
                            hovered SetField(_tooltip, "value", _("点击后将推送相关事件"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                            sensitive not persistent.maica_setting_dict.get('_event_pushed')



                        textbutton _("导出至根目录"):
                            action Function(export_player_information)
                            hovered SetField(_tooltip, "value", _("导出至game/Submods/MAICA_ChatSubmod/player_information.txt"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        textbutton _("MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"):
                            action ToggleDict(persistent.maica_setting_dict, "mspire_enable", True, False)
                            hovered SetField(_tooltip, "value", _("是否允许由MSpire生成的对话, MSpire不受MFocus影响, 需要关闭重复对话"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)


                        textbutton _("对话范围编辑"):
                            action [
                                SetDict(persistent.maica_setting_dict, "_event_pushed", True),
                                Function(renpy.notify, _("增加信息的事件将于关闭设置后推送")),
                                Function(store.MASEventList.push, "mspire_mods_preferences")
                                ]
                            hovered SetField(_tooltip, "value", _("范围为维基百科的category页面"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        textbutton _("间隔: [persistent.maica_setting_dict.get('mspire_interval')]分钟"):
                            action NullAction()
                        bar:
                            value DictValue(persistent.maica_setting_dict, "mspire_interval", 200, step=1,offset=5 ,style="slider")
                            xsize 200
                            hovered SetField(_tooltip, "value", _("MSpire对话的最低间隔分钟"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        textbutton _("使用会话: [persistent.maica_setting_dict.get('mspire_session')]"):
                            action NullAction()
                        bar:
                            value DictValue(persistent.maica_setting_dict, "mspire_session", 9, step=1,offset=0 ,style="slider")
                            xsize 50
                            hovered SetField(_tooltip, "value", _("MSpire所使用的会话\nMSpire使用过多可能会导致模型定位混乱"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)


                    hbox:
                        textbutton _("submod_log.log 等级:[logging.getLevelName(store.mas_submod_utils.submod_log.level)]"):
                            action Function(store.change_loglevel)
                            hovered SetField(_tooltip, "value", _("这将影响submod_log.log中每条log的等级, 低于该等级的log将不会记录\n这也会影响其他子模组"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)



                    if renpy.config.debug:
                        hbox:
                            textbutton "MASEventList.push(maica_talking)":
                                action [
                                    Function(store.MASEventList.push, "maica_talking"),
                                    SetDict(persistent.maica_setting_dict, "_event_pushed", True)
                                    ]
                                sensitive not persistent.maica_setting_dict.get('_event_pushed')
                            textbutton "MASEventList.push(maica_mspire)":
                                action [
                                    Function(store.MASEventList.push, "maica_mspire"),
                                    SetDict(persistent.maica_setting_dict, "_event_pushed", True)
                                    ]
                                sensitive not persistent.maica_setting_dict.get('_event_pushed')


                    hbox:
                        style_prefix "confirm"

                        textbutton _("保存设置"):
                            action [
                                SetDict(persistent.maica_setting_dict, "_event_pushed", False),
                                Function(store.maica_apply_setting),
                                Hide("maica_setting")
                                ]
                
                 


screen maica_login():
    modal True
    zorder 215

    style_prefix "confirm"

    frame:
        vbox:
            xfill False
            yfill False
            spacing 5

            hbox:
                textbutton _("输入 DCC 账号用户名"):
                    action Show("maica_login_input",message = _("请输入DCC 账号用户名") ,returnto = "_maica_LoginAcc")
                text _("或")
                textbutton _("输入 DCC 账号邮箱"):
                    action Show("maica_login_input",message = _("请输入DCC 账号邮箱"),returnto = "_maica_LoginEmail")

            hbox:
                textbutton _("输入 DCC 账号密码"):
                    action Show("maica_login_input",message = _("请输入DCC 账号密码"),returnto = "_maica_LoginPw")
            hbox:
                text ""
            hbox:
                if renpy.version_tuple[0] < 8:
                    textbutton _("连接至服务器生成MAICA令牌"):
                        action [
                            Function(store.maica.maica._gen_token, store._maica_LoginAcc, store._maica_LoginPw, "", store._maica_LoginEmail if store._maica_LoginEmail != "" else None),
                            Function(_maica_clear), 
                            Hide("maica_login")
                            ]
                else:
                    textbutton _("生成MAICA令牌"):
                        action [
                            Function(store.maica.maica._gen_token, store._maica_LoginAcc, store._maica_LoginPw, "", store._maica_LoginEmail if store._maica_LoginEmail != "" else None),
                            Function(_maica_clear), 
                            Hide("maica_login")
                            ]
                textbutton _("取消"):
                    action [Function(_maica_clear), Hide("maica_login")]



screen maica_login_input(message, returnto, ok_action = Hide("maica_login_input")):
    #登录输入账户窗口, 也用来用作通用的输入窗口
    ## Ensure other screens do not get input while this screen is displayed.s
    modal True
    zorder 225

    style_prefix "confirm"

    frame:
        vbox:
            ymaximum 300
            xmaximum 800
            xfill True
            yfill False
            spacing 5

            label _(message):
                style "confirm_prompt"
                xalign 0.5
            hbox:
                input default "" value VariableInputValue(returnto) length 64

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action ok_action



screen maica_message(message = "Non Message", ok_action = Hide("maica_message")):
    modal True
    zorder 225

    style_prefix "confirm"

    frame:
        vbox:
            ymaximum 300
            xmaximum 800
            xfill True
            yfill False
            spacing 5

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            #input default "" value VariableInputValue("savefile") length 25

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action ok_action