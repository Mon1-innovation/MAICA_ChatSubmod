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
            submod="MAICA ChatSubmod",
            user_name="Mon1_Innovation",
            repository_name="MAICA_ChatSubmod",
            update_dir="",
            attachment_id=None
        )
init -5 python:
    _maica_LoginPhone = ""
    _maica_LoginPw = ""
    def maica_login_ok():
        if _maica_LoginPhone == "" or _maica_LoginPw == "":
            return renpy.show_screen("maica_message", message = "账号/密码为空")
        if not result:
            renpy.show_screen("maica_message", message = "登录失败! 请检查账号密码是否正确!")
        renpy.hide_screen("maica_login")
screen maica_setting_pane():
    python:
        from store.maica_sub import maica as ai
        stat = "未连接" if not ai.wss_session else "已连接" if ai.wss_session.keep_running else "已断开"
    vbox:
        xmaximum 800
        xfill True
        style_prefix "check"

        text "> MAICA 通信状态:[ai.status]|[ai.MaicaAiStatus.get_description(ai.status)]"
        text "> Websocket:[stat]"
        
        if ai.status == ai.MaicaAiStatus.NOT_READY:
            text ("输入账号密码"):
                xalign 1.0 yalign 0.0
                xoffset -10
                style "main_menu_version"
            text ("使用令牌连接")
        else:
            text ("重置当前对话")

            text ("注销当前DCC账号")

            text ("设置")
        


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
                    action Show("maica_login_input",message = "请输入DCC 账号用户名",returnto = "_maica_LoginPhone")
            hbox:
                textbutton "输入 DCC 账号密码":
                    action Show("maica_login_input",message = "请输入DCC 账号密码",returnto = "_maica_LoginPw")
            hbox:
                text ""
            hbox:
                textbutton "保存信息":
                    action Function()

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