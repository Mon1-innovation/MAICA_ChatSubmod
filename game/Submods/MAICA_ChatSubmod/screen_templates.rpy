init -1:

    screen sbar(a, w):
        add Transform("gui/scrollbar/horizontal_poem_bar_d.png", xalign=a, yalign=0.5, size=(w, 25))

    image bar1 = Transform("gui/scrollbar/horizontal_poem_bar_d.png", xalign=0.0, yalign=0.5, size=(300, 25))
    image bar2 = Transform("gui/scrollbar/horizontal_poem_bar_d.png", xalign=1.0, yalign=0.5, size=(300, 25))
    image bar3 = Transform("gui/scrollbar/horizontal_poem_bar_d.png", xalign=0.5, yalign=0.5, size=(750, 25))

    screen divider(message):

        hbox:
            ysize 75
            xfill True

            hbox:
                xalign 0.5
                yalign 0.6
                xsize 900
                add "bar1"
                text "  "
                text message:
                    xalign 0.5
                    size 25
                text "  "
                add "bar2"

    screen divider_plain():

        hbox:
            ysize 75
            xfill True

            hbox:
                xalign 0.5
                yalign 0.6
                xsize 900
                add "bar3"

    screen divider_small(message):

        hbox:
            ysize 50
            xfill True

            hbox:
                xalign 0.5
                yalign 0.6
                xsize 600
                add "bar1"
                text "  "
                text message:
                    xalign 0.5
                    size 20
                text "  "
                add "bar2"

    screen divider_plain_small():

        hbox:
            ysize 50
            xfill True

            hbox:
                xalign 0.5
                yalign 0.6
                xsize 600
                add "bar3"

    screen intro_tooltip():
        python:
            submods_screen = store.renpy.get_screen("submods", "screens")

            if submods_screen:
                store._fore_tooltip = submods_screen.scope.get("tooltip", None)
            else:
                store._fore_tooltip = None

    screen sub_button(tooltip, var, min, max, sdict):
        $ _tooltip = store._tooltip
        python:
            if isinstance(max, float):
                isfloat = True
            else:
                isfloat = False
        hbox:
            style_prefix "addsub_fancy_check"
            textbutton "-":
                action [Function(store.common_sub, var, min, max, sdict), SensitiveIf(store.common_can_sub(var, min, max, sdict))]
                hovered SetField(_tooltip, "value", tooltip)
                unhovered SetField(_tooltip, "value", _tooltip.default)

    screen add_button(tooltip, var, min, max, sdict):
        $ _tooltip = store._tooltip
        python:
            if isinstance(max, float):
                isfloat = True
            else:
                isfloat = False
        hbox:
            style_prefix "addsub_fancy_check"
            textbutton "+":
                action [Function(store.common_add, var, min, max, sdict), SensitiveIf(store.common_can_add(var, min, max, sdict))]
                hovered SetField(_tooltip, "value", tooltip)
                unhovered SetField(_tooltip, "value", _tooltip.default)

    screen prog_bar(expl, len, tooltip, var, min, max, istime=False, sdict="maica_setting_dict"):
        $ _tooltip = store._tooltip
        $ expl = renpy.substitute(expl)
        python:
            s_dict = getattr(persistent, sdict)
            if isinstance(max, float):
                isfloat = True
            else:
                isfloat = False
            if not istime:
                if not isfloat:
                    disp_v = str(s_dict[var])
                else:
                    disp_v = "{:.{}f}".format(s_dict[var], 2)
            elif istime == "m":
                disp_v = str(int(s_dict[var] / 60)) + "h" + str(int(s_dict[var] % 60)) + "m"
            else:
                disp_v = str(int(s_dict[var] / 60)) + "m" + str(int(s_dict[var] % 60)) + "s"
        hbox:
            if sdict == "maica_setting_dict":
                hbox:
                    style_prefix "maica_check"
                    textbutton "{}: ".format(expl):
                        action Show("maica_common_setter", expl=expl, var=var, min=min, max=max, sdict=sdict)
                        hovered SetField(_tooltip, "value", tooltip)
                        unhovered SetField(_tooltip, "value", _tooltip.default)

            use sub_button(tooltip, var, min, max, sdict)

            hbox:
                xsize len
                bar:
                    xpos 20
                    yoffset 10
                    value DictValue(s_dict, var, (max - min), offset=min ,style="slider")
                    xsize (len - 100)
                    hovered SetField(_tooltip, "value", tooltip)
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                hbox:
                    style_prefix "maica_check"
                    textbutton disp_v:
                        xalign 1.0
                        xoffset 10
                        action Show("maica_common_setter", expl=expl, var=var, min=min, max=max, istime=istime, sdict=sdict)
                        hovered SetField(_tooltip, "value", tooltip)
                        unhovered SetField(_tooltip, "value", _tooltip.default)

            use add_button(tooltip, var, min, max, sdict)

    screen num_bar(expl, len, tooltip, var, min, max, sdict="maica_setting_dict"):
        $ _tooltip = store._tooltip
        $ expl = renpy.substitute(expl)
        python:
            s_dict = getattr(persistent, sdict)
        hbox:
            use sub_button(tooltip, var, min, max, sdict)

            hbox:
                xsize len
                style_prefix "maica_check"
                textbutton (expl + ": " + str(s_dict[var])):
                    xalign 0.5
                    action Show("maica_common_setter", expl=expl, var=var, min=min, max=max, sdict=sdict)
                    hovered SetField(_tooltip, "value", tooltip)
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            use add_button(tooltip, var, min, max, sdict)

    screen maica_common_setter(expl, var, min, max, istime=False, sdict="maica_setting_dict"):
        $ _tooltip = store._tooltip
        python:
            s_dict = getattr(persistent, sdict)
            if not istime:
                minutes = ""
            elif istime == "m":
                minutes = _("分钟")
            else:
                minutes = _("秒")
            
            str_var = '_' + var
            if str_var not in s_dict:
                s_dict[str_var] = str(s_dict[var])
            if isinstance(max, float):
                isfloat = True
            else:
                isfloat = False
            def apply_var(var, min, max, isfloat, s_dict):
                str_var = '_' + var
                if s_dict[str_var] == "":
                    renpy.hide_screen("maica_common_setter")
                    return
                try:
                    if isfloat:
                        value_var = float(s_dict[str_var])
                    else:
                        value_var = int(s_dict[str_var])
                    if not min <= value_var <= max:
                        # renpy.call_screen("maica_common_debugger", str(min)+str(value_var)+str(max))
                        raise Exception("Value out of bound")

                    s_dict[var] = value_var
                    renpy.hide_screen("maica_common_setter")
                except Exception:
                    renpy.show_screen("maica_common_warn")
                finally:
                    
                    del s_dict[str_var]
                    
        modal True
        zorder 95

        style_prefix "confirm"

        use maica_setter_small_frame(title=_("请输入{}({}~{}{}):".format(expl, min, max, minutes)), ok_action=Function(apply_var, var, min, max, isfloat, s_dict), cancel_action=Hide("maica_common_setter")):
            hbox:
                input:
                    default str(s_dict[str_var])
                    value DictInputValue(s_dict, str_var)
                    length 9
                    allow ("0123456789" + "." if isfloat else "")

    screen maica_common_warn(text=_("请输入正确的数值!")):

        modal True
        zorder 100

        use maica_setter_xsmall_frame(text, Hide("maica_common_warn"))

    screen maica_setter_xsmall_frame(title=None, ok_action=None, cancel_action=None):
        frame:
            style_prefix "confirm"
            xalign 0.5
            yalign 0.5
            vbox:
                xsize 300
                ymaximum 200

                spacing 5
                if title:
                    label title:
                        style "confirm_prompt"
                        xalign 0.5
                transclude
                hbox:
                    xalign 0.5
                    spacing 100
                    if ok_action:
                        textbutton _("OK") action ok_action
                    if cancel_action:
                        textbutton _("取消") action cancel_action   

    screen maica_setter_small_frame(title=None, ok_action=None, cancel_action=None):
        frame:
            style_prefix "confirm"
            xalign 0.5
            yalign 0.5
            vbox:
                xsize 500
                ymaximum 300

                spacing 5
                if title:
                    label title:
                        style "confirm_prompt"
                        xalign 0.5
                transclude
                hbox:
                    xalign 0.5
                    spacing 100
                    if ok_action:
                        textbutton _("OK") action ok_action
                    if cancel_action:
                        textbutton _("取消") action cancel_action

    screen maica_setter_medium_frame(title=None, ok_action=None, cancel_action=None):
        frame:
            style_prefix "confirm"
            xalign 0.5
            yalign 0.5
            vbox:
                xsize 800
                ymaximum 350

                spacing 5
                if title:
                    label title:
                        style "confirm_prompt"
                        xalign 0.5
                vbox:
                    xsize 600
                    xalign 0.5
                    transclude
                hbox:
                    xalign 0.5
                    spacing 100
                    if ok_action:
                        textbutton _("OK") action ok_action
                    if cancel_action:
                        textbutton _("取消") action cancel_action
                        
    screen maica_common_outer_frame(w=1000, h=500, x=0.5, y=0.3):
        frame:
            xsize w
            xalign x
            yalign y
            vbox:
                xsize w
                spacing 5
                transclude

    screen maica_common_inner_frame(w=1000, h=500, x=0.5, y=0.3):

        viewport:
            id "viewport"
            scrollbars "vertical"
            xsize w - 40
            ysize h

            mousewheel True
            draggable True

            has hbox

            vbox:
                xsize 30
            vbox:
                xsize w - 70
                spacing 5
                transclude

    screen maica_l1_subframe():
        hbox:
            frame:
                xsize 950
                xpos 30
                has vbox:
                    xsize 950
                transclude

    screen maica_l2_subframe():
        hbox:
            frame:
                xsize 850
                xpos 30
                has vbox:
                    xsize 850
                transclude

    screen maica_message(message = "Non Message", ok_action = Hide("maica_message")):
        modal True
        zorder 100

        style_prefix "confirm"

        frame:
            xalign 0.5
            yalign 0.5
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
