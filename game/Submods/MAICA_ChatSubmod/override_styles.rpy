init 999:
    style generic_fancy_check_text is gui_button_text:
        properties gui.button_text_properties("generic_fancy_check_button")
        font "gui/font/Halogen.ttf"
        color "#BFBFBF"
        insensitive_color mas_ui.light_button_text_insensitive_color
        outlines []
        yoffset 3

    style generic_fancy_check_text_dark is gui_button_text_dark:
        properties gui.button_text_properties("generic_fancy_check_button_dark")
        font "gui/font/Halogen.ttf"
        color "#BFBFBF"
        insensitive_color mas_ui.dark_button_text_insensitive_color
        outlines []
        yoffset 3

    style main_menu_version:
        text_align 0.0

    style main_menu_version_dark:
        color "#e4c0cf"
        text_align 0.0

    style generic_fancy_check_button_disabled:
        foreground "generic_fancy_check_button_fg_insensitive"
        selected_foreground "generic_fancy_check_button_fg_selected_insensitive"
        selected_background Solid("#504549")

    style generic_fancy_check_button_text:
        color "#AAAAAA"
        hover_color "#000000"
        selected_color "#000000"
        insensitive_color mas_ui.light_button_text_insensitive_color

    style generic_fancy_check_button_text_dark:
        color "#BFBFBF"
        hover_color "#FFAA99"
        selected_color "#FFAA99"
        insensitive_color mas_ui.dark_button_text_insensitive_color

    style generic_fancy_check_button_disabled_text:
        color "#8C8C8C"
        yoffset 0

    style check_button_text_dark:
        color "#8C8C8C"
        hover_color "#FF80B7"
        selected_color "#DE367E"
        insensitive_color "#5a5a5a"
