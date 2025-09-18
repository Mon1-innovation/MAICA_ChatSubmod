style ed_debug_text:
    size 15

style main_menu_version_l is main_menu_version:
    text_align 0.0

style small_link is main_menu_version:
    size 10

style small_expl is main_menu_version:
    text_align 0.0
    size 15

style small_expl_hw is maica_check_nohover_button_text:
    size 15

style maica_default is default

style maica_default_small is maica_default:
    size 20






style maica_check_button is check_button:
    foreground None
    padding (4,4,4,4)
    hover_background Solid("#ffe6f4")
    # selected_background Solid("#FFBDE1")

style maica_check_button_dark is check_button_dark:
    foreground None
    padding (4,4,4,4)    
    hover_background Solid("#d9739c")
    # selected_background Solid("#CE4A7E")

style maica_check_button_text is generic_fancy_check_button_text:
    color "#AAAAAA"
    hover_color "#000000"
    selected_color "#AAAAAA"

style maica_check_button_text_dark is generic_fancy_check_button_text_dark:
    color "#BFBFBF"
    hover_color "#FFAA99"
    selected_color "#BFBFBF"






style maica_check_nohover_text is maica_check_button_text:
    color "#AAAAAA"
    hover_color "#AAAAAA"

style maica_check_nohover_button is maica_check_button:
    hover_background None

style maica_check_nohover_button_text is maica_check_button_text:
    color "#AAAAAA"
    hover_color "#AAAAAA"

style maica_check_nohover_button_dark is maica_check_button_dark:
    hover_background None

style maica_check_nohover_button_text_dark is maica_check_button_text_dark:
    color "#BFBFBF"
    hover_color "#BFBFBF"






style addsub_fancy_check_button is generic_fancy_check_button:
    padding (14,4,14,4)
    foreground None
    background Solid("#FFBDE1")
    hover_background Solid("#ffcde9")
    selected_background Solid("#FFBDE1")
    insensitive_background Solid("#ccb5c2")

style addsub_fancy_check_button_dark is generic_fancy_check_button_dark:
    padding (14,4,14,4)
    foreground None
    background Solid("#CE4A7E")
    hover_background Solid("#d9739c")
    selected_background Solid("#CE4A7E")
    insensitive_background Solid("#977985")

style addsub_fancy_check_button_disabled is generic_fancy_check_button_disabled:
    padding (14,4,14,4)
    foreground None
    background Solid("#808080")

style addsub_fancy_check_button_text is check_label_text:
    color "#e6e6e6"
    outlines []
    hover_color "#f0f0f0"
    selected_color "#e6e6e6"
    insensitive_color "#cecece"
    yoffset 1

style addsub_fancy_check_button_text_dark is check_label_text_dark:
    color "#BFBFBF"
    outlines []
    hover_color "#FFAA99"
    selected_color "#BFBFBF"
    insensitive_color "#a5a5a5"
    yoffset 1

style addsub_fancy_check_button_disabled_text is addsub_fancy_check_button_text

