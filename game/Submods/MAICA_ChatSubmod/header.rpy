init -990 python:
    store.mas_submod_utils.Submod(
        author="P",
        name="MAICA-Blessland",
        description="The official Submod frontend of MAICA",
        version='0.0.1',
        settings_pane="maica_setting_pane"
    )
init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="MAICA-Blessland",
            user_name="Mon1_Innovation",
            repository_name="MAICA_ChatSubmod",
            update_dir="",
            attachment_id=None
        )

default persistent.maica_setting_dict = {
    "auto_connect":False,
    "maica_model":None,
    "use_custom_model_config":False,
    "sf_extraction":False,
    "chat_session":1,
    "console":True
}
default persistent.mas_player_additions = []
init 10 python:
    default_dict = {
        "auto_connect":False,
        "maica_model":None,
        "use_custom_model_config":False,
        "sf_extraction":False,
        "chat_session":1,
        "console":True
    }
    default_dict.update(persistent.maica_setting_dict)
    persistent.maica_setting_dict = default_dict.copy()

    if persistent.maica_setting_dict["maica_model"] is None:
        persistent.maica_setting_dict["maica_model"] = store.maica.maica.MaicaAiModel.maica_main
    _maica_LoginAcc = ""
    _maica_LoginPw = ""
    _maica_LoginEmail = None
    def _maica_clear():
        store._maica_LoginAcc = ""
        store._maica_LoginPw = ""
        store._maica_LoginEmail = None
        store.mas_api_keys.api_keys.update({"Maica_Token":store.maica.maica.ciphertext})


    def upload_persistent_dict():
        d = persistent.__dict__.copy()
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
        renpy.notify(res.get("success", "上传失败"))

    def reset_session():
        store.maica.maica.reset_chat_session()
        renpy.notify("会话已重置, 请重新连接MAICA服务器")
    def output_chat_history():
        with open(os.path.join("game", "Submods", "MAICA_ChatSubmod", "chat_history.txt"), 'w') as f:
            f.write(store.maica.maica.get_history().get("history", {}))
        renpy.notify("已导出至game/Submods/MAICA_ChatSubmod/chat_history.txt")
    
    def apply_setting():
        store.maica.maica.auto_reconnect = persistent.maica_setting_dict["auto_connect"]
        if persistent.maica_setting_dict["use_custom_model_config"]:
            update_model_setting()
        store.maica.maica.sf_extraction = persistent.maica_setting_dict["sf_extraction"]
        store.maica.maica.chat_session = persistent.maica_setting_dict["chat_session"]
        store.maica.maica.model = persistent.maica_setting_dict["maica_model"]
    
    def change_chatsession():
        persistent.maica_setting_dict["chat_session"] += 1
        if persistent.maica_setting_dict["chat_session"] not in range(0, 9):
            persistent.maica_setting_dict["chat_session"] = 0
        
    def reset_player_information():
        persistent.mas_player_additions = []
    
    def export_player_information():
        with open(os.path.join("game", "Submods", "MAICA_ChatSubmod", "player_info.txt"), 'w') as f:
            f.write(json.dumps(persistent.mas_player_additions))
        renpy.notify("已导出至game/Submods/MAICA_ChatSubmod/player_information.txt")

    def update_model_setting():
        import os, json
        try:
            with open(os.path.join(store.maica.basedir, "custom_model_config.json"), "r") as f:
                store.maica.maica.modelconfig = json.load(f)
        except Exception as e:
            if not renpy.is_init_phase():
                renpy.notify("加载自定义模型配置失败:\n {}".format(e))
            store.mas_submod_utils.submod_log("Failed to load custom model config: {}".format(e))
    
    apply_setting()
        
            

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
            textbutton _("上传存档信息"):
                action Function(upload_persistent_dict)

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
            xmaximum 1200
            spacing 5

            hbox:
                text _("累计对话轮次: [store.maica.maica.stat.get('message_count')]")
                
            hbox:
                text _("累计收到Token: [store.maica.maica.stat.get('received_token')]")
            hbox:
                textbutton _("重置统计数据"):
                    action Function(store.maica.maica.reset_stat)


            hbox: 
                textbutton _("自动重连: [persistent.maica_setting_dict.get('auto_connect')]"):
                    action ToggleDict(persistent.maica_setting_dict, "auto_connect", True, False)
                    hovered SetField(_tooltip, "value", _("连接断开时自动重连"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                textbutton _("当前MAICA模型: [persistent.maica_setting_dict.get('maica_model')]"):
                    action ToggleDict(persistent.maica_setting_dict, "maica_model", store.maica.maica.MaicaAiModel.maica_main, store.maica.maica.MaicaAiModel.maica_core)
                    hovered SetField(_tooltip, "value", _("maica_main：完全能力模型，maica_core: 核心能力模型\n完全能力的前置响应延迟偏高"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            
            hbox:
                textbutton _("使用高级参数: [persistent.maica_setting_dict.get('use_custom_model_config')]"):
                    action ToggleDict(persistent.maica_setting_dict, "use_custom_model_config", True, False)    
                    hovered SetField(_tooltip, "value", _("在使用前，请务必查看子模组根目录的custom_modelconfig.json\n否则可能导致意料之外的问题\n子模组将读取该json作为对话参数"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                textbutton _("刷新参数"):
                    action Function(store.update_model_setting)
                    
            hbox:
                textbutton _("使用存档数据: [persistent.maica_setting_dict.get('sf_extraction')]"):
                    action ToggleDict(persistent.maica_setting_dict, "sf_extraction", True, False)
                    hovered SetField(_tooltip, "value", _("关闭时, 模型将不会使用存档数据\n在开启前请务必先上传存档"))
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
                      
            hbox:
                textbutton _("清除玩家补充信息: 当前共有[len(persistent.maica_setting_dict)]条"):
                    action Function(reset_player_information)
                    hovered SetField(_tooltip, "value", _("由你补充的一些数据"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                
                textbutton _("导出至根目录"):
                    action Function(export_player_information)
                    hovered SetField(_tooltip, "value", _("导出至game/Submods/MAICA_ChatSubmod/player_information.txt"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)


            hbox:
                style_prefix "confirm"

                textbutton _("保存设置"):
                    action [
                        Function(store.apply_setting),
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
                textbutton "输入 DCC 账号用户名":
                    action Show("maica_login_input",message = "请输入DCC 账号用户名",returnto = "_maica_LoginAcc")
                text "或"
                textbutton "输入 DCC 账号邮箱":
                    action Show("maica_login_input",message = "请输入DCC 账号邮箱",returnto = "_maica_LoginEmail")

            hbox:
                textbutton "输入 DCC 账号密码":
                    action Show("maica_login_input",message = "请输入DCC 账号密码",returnto = "_maica_LoginPw")
            hbox:
                text ""
            hbox:
                if renpy.version_tuple[0] < 8:
                    textbutton "连接至Maica生成令牌":
                        action [
                            Function(store.maica.maica._gen_token, store._maica_LoginAcc, store._maica_LoginPw, "", store._maica_LoginEmail),
                            Function(_maica_clear), 
                            Hide("maica_login")
                            ]
                else:
                    textbutton "生成令牌":
                        action [
                            Function(store.maica.maica._gen_token, store._maica_LoginAcc, store._maica_LoginPw, ""),
                            Function(_maica_clear), 
                            Hide("maica_login")
                            ]
                textbutton "取消":
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