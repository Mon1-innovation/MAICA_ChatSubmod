style ed_debug_text:
    size 15
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


translate chinese style generic_fancy_check_text is gui_button_text:
    font "gui/font/npy.ttf"

translate chinese style generic_fancy_check_text_dark is gui_button_text_dark:
    font "gui/font/npy.ttf"
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
