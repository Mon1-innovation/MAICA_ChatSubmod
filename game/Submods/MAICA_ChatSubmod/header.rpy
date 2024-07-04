init -990 python:
    store.mas_submod_utils.Submod(
        author="P",
        name="MAICA Chat",
        description="看看我们能走多远",
        version='0.0.1',
        settings_pane="maica_setting_pane"
    )
init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="MAICA Chat",
            user_name="Mon1_Innovation",
            repository_name="MAICA_ChatSubmod",
            update_dir="",
            attachment_id=None
        )
init 10 python:
    _maica_LoginAcc = ""
    _maica_LoginPw = ""
    def _maica_clear():
        store._maica_LoginAcc = ""
        store._maica_LoginPw = ""
        store.mas_api_keys.api_keys.update({"Maica_Token":store.maica.maica.ciphertext})

    def maica_login_ok():
        if _maica_LoginAcc == "" or _maica_LoginPw == "":
            return renpy.show_screen("maica_message", message = "账号/密码为空")
        if not result:
            renpy.show_screen("maica_message", message = "登录失败! 请检查账号密码是否正确!")
        renpy.hide_screen("maica_login")

    def upload_persistent_dict():
        persistent2 = persistent
        persistent2.__dict__['_seen_ever'].clear()
        persistent2.__dict__['_mas_event_init_lockdb'].clear()
        persistent2.__dict__['_changed'].clear()
        persistent2.__dict__['_mas_event_init_lockdb'].clear()
        persistent2.__dict__['event_database'].clear()
        persistent2.__dict__['farewell_database'].clear()
        persistent2.__dict__['greeting_database'].clear()
        persistent2.__dict__['_mas_apology_database'].clear()
        persistent2.__dict__['_mas_compliments_database'].clear()
        persistent2.__dict__['_mas_fun_facts_database'].clear()
        persistent2.__dict__['_mas_mood_database'].clear()
        persistent2.__dict__['_mas_songs_database'].clear()
        persistent2.__dict__['_mas_story_database'].clear()
        persistent2.__dict__['_mas_affection_backups'] = None
        persistent2.__dict__['greeting_database'].clear()
        persistent2.__dict__['greeting_database'].clear()
        persistent2.__dict__['greeting_database'].clear()
        persistent2.__dict__['greeting_database'].clear()
        persistent2.__dict__['greeting_database'].clear()
        persistent2.__dict__['greeting_database'].clear()
        persistent2.__dict__['greeting_database'].clear()
        persistent2.__dict__['mas_playername'] = store.player
        if persistent._mas_player_bday:
            persistent2.__dict__['mas_player_bday'] = [persistent._mas_player_bday.year, persistent._mas_player_bday.month, persistent._mas_player_bday.day]
        persistent2.__dict__['mas_affection'] = store._mas_getAffection()
        del persistent2.__dict__['_preferences']
        for i in persistent2.__dict__:
            try:
                json.dumps(persistent2.__dict__[i])
            except:
                try:
                    persistent2.__dict__[i] = str(persistent2.__dict__[i])
                except:
                    persistent2.__dict__[i] = "REMOVED"
        res = store.maica.maica.upload_save(persistent2.__dict__[i])
        renpy.notify(res.get("success", "上传失败!"))

    def reset_session():
        store.maica.maica.reset_chat_session()
        renpy.notify("已重置，请重新连接MAICA服务器")
    def output_chat_history():
        with open(os.path.join("game", "Submods", "MAICA_ChatSubmod", "chat_history.txt"), 'w') as f:
            f.write(store.maica.maica.get_history())
        renpy.notify("已导出至game/Submods/MAICA_ChatSubmod/chat_history.txt")
            

screen maica_setting_pane():
    python:
        import store.maica as maica
        stat = "未连接" if not maica.maica.wss_session else "已连接" if maica.maica.wss_session.keep_running else "已断开"
        store.maica.maica.ciphertext = store.mas_getAPIKey("Maica_Token")
    vbox:
        xmaximum 800
        xfill True
        style_prefix "check"

        text "> MAICA 通信状态:[maica.maica.status]|[maica.maica.MaicaAiStatus.get_description(maica.maica.status)]":
            xalign 1.0 yalign 0.0
            xoffset -10
            style "main_menu_version"
        text "> Websocket:[stat]":
            xalign 1.0 yalign 0.0
            xoffset -10
            style "main_menu_version"
        
        if True if not maica.maica.wss_session else not maica.maica.wss_session.keep_running:
            textbutton ("> 生成令牌"):
                action Show("maica_login")
                
            textbutton ("> 使用已保存令牌连接"):
                action Function(store.maica.maica.init_connect)

            
        else:
            textbutton ("上传存档信息"):
                action Function(upload_persistent_dict)

            textbutton ("重置当前对话"):
                action Function(reset_session)

            textbutton ("导出当前对话")

            textbutton ("退出当前DCC账号"):
                action Function(store.maica.maica.close_wss_session)
    
        textbutton ("> MAICA Chat设置 *部分选项需要重新连接")

            
        


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
                textbutton "输入 DCC 账号邮箱"

            hbox:
                textbutton "输入 DCC 账号密码":
                    action Show("maica_login_input",message = "请输入DCC 账号密码",returnto = "_maica_LoginPw")
            hbox:
                text ""
            hbox:
                if renpy.version_tuple[0] < 8:
                    textbutton "连接至Maica生成令牌":
                        action [
                            Function(store.maica.maica._gen_token, store._maica_LoginAcc, store._maica_LoginPw, ""),
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