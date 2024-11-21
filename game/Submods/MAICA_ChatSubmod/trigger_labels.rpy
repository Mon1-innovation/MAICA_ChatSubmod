label mtrigger_change_clothes(outfit_name):
    call maica_hide_console
    call mas_transition_to_emptydesk

    python:
        renpy.pause(1.0, hard=True)

        outfit_to_wear = store.mas_sprites.get_sprite(
            store.mas_sprites.SP_CLOTHES,
            outfit_name
        )
        if outfit_to_wear is not None and store.mas_SELisUnlocked(outfit_to_wear):
            store.monika_chr.change_clothes(outfit_to_wear, by_user=True, outfit_mode=True)

        renpy.pause(4.0, hard=True)

    call mas_transition_from_emptydesk("monika 1eua")
    call maica_show_console
    return

label mtrigger_kiss:
    if mas_shouldKiss(1):
        call maica_hide_console
        call monika_kissing_motion_short
        call maica_show_console
    return 
label mttrigger_minigame(game):
    call maica_hide_console
    $ renpy.call(game)
    call maica_show_console
    return


label mtrigger_leave: 
    m "你要离开了吗, [player]?"
    menu:
        "你要离开了吗, [player]?{nw}{fast}"
        "是的.":
            m 1eka "一会见, [player]!"
            jump mtrigger_quit
            return
        "再过一会吧":
            m 1eka "谢谢你多陪我一会, [player]."
            return
    return
    
label mtrigger_quit:
    $ persistent.closed_self = True #Monika happily closes herself
    $ mas_clearNotifs()
    jump _quit
    return

label mtrigger_location: 
    if mas_isMoniEnamored(higher=True):
        call monika_change_background
    else:
        m 1eua "我们似乎没别的地方可去呢..."
        m 1eka "抱歉喽, [player]."
    return

label mtrigger_idle:
    return "idle"

label mtrigger_idle_callback:
    m 1eka "你回来啦, [player]!"
    m 1eka "我都要想你了."
    jump maica_main.talking_start

label mtrigger_idle:
    call maica_hide_console
    hide screen mas_background_timed_jump
    $ _history_list.pop()
    $ persistent._mas_idle_data["mtrigger_idle"] = True
    $ mas_setupIdleMode("mtrigger_idle", "mtrigger_idle_callback")
    return

label mtrigger_idle_callback:
    m 1eka "You're back, [player]!"
    m 1eka "I missed you."
    jump monika_chatting_text

label monikai_brb:
    hide screen mas_background_timed_jump
    $ _history_list.pop()
    $ persistent._mas_idle_data["monikai_be_right_back"] = True
    $ mas_setupIdleMode("monikai_be_right_back", "monikai_be_right_back_callback")
    return
