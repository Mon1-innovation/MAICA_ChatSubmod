label mtrigger_change_clothes(outfit_name):
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
    return

label mtrigger_kiss:
    if mas_shouldKiss(1):
        call monika_kissing_motion_short
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