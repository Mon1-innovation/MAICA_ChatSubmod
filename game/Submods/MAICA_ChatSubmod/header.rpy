init -990 python:
    store.mas_submod_utils.Submod(
        author="P",
        name="MAICA 子模组",
        description="看看我们能走多远",
        version='0.0.1',
        settings_pane="maica_setting_pane"
    )
init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="Netease Music",
            user_name="MAS-Submod-MoyuTeam",
            repository_name="NeteaseInMas",
            update_dir="",
            attachment_id=None
        )

screen maica_setting_pane():
    vbox:
        xmaximum 800
        xfill True
        style_prefix "check"

        text "MAICA 服务器状态:"
        text "Websocket"

        text ("连接 MAICA 服务器"):
            xalign 1.0 yalign 0.0
            xoffset -10
            style "main_menu_version"
        


