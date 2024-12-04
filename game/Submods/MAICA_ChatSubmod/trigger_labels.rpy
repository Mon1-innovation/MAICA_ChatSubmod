label mtrigger_change_clothes(outfit_name):
    call maica_reconnect
    call maica_hide_console
    if outfit_name == "mas_pick_a_clothes":
        call monika_clothes_select 
        call maica_show_console
        return 
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

label mtrigger_change_hair(outfit_name):
    call maica_reconnect
    call maica_hide_console
    if outfit_name == "mas_pick_a_clothes":
        call monika_hair_select 
        call maica_show_console
        return 
    call mas_transition_to_emptydesk
    python:
        renpy.pause(1.0, hard=True)

        outfit_to_wear = store.mas_sprites.get_sprite(
            store.mas_sprites.SP_HAIR,
            outfit_name
        )
        if outfit_to_wear is not None and store.mas_SELisUnlocked(outfit_to_wear):
            store.monika_chr.change_hair(outfit_to_wear, by_user=True)

        renpy.pause(4.0, hard=True)

    call mas_transition_from_emptydesk("monika 1eua")
    call maica_show_console
    return

label mtrigger_change_acs(outfit_name):
    call maica_reconnect
    call maica_hide_console
    if outfit_name == "mas_pick_a_clothes":
        call mtrigger_acs_select 
        call maica_show_console
        return 
    call mas_transition_to_emptydesk
    python:
        renpy.pause(1.0, hard=True)

        outfit_to_wear = store.mas_sprites.get_sprite(
            store.mas_sprites.SP_ACS,
            outfit_name
        )
        if outfit_to_wear is not None and store.mas_SELisUnlocked(outfit_to_wear):
            store.monika_chr.wear_acs(outfit_to_wear)

        renpy.pause(4.0, hard=True)

    call mas_transition_from_emptydesk("monika 1eua")
    call maica_show_console
    return
label mtrigger_acs_select:

    menu:
        "[renpy.substitute(store.mas_selspr.get_prompt('choker'))]" if 'choker' in store.mas_selspr.PROMPT_MAP:
            $ renpy.call(store.mas_selspr.PROMPT_MAP['choker']['_ev'])
        "[renpy.substitute(store.mas_selspr.get_prompt('clothes'))]" if 'clothes' in store.mas_selspr.PROMPT_MAP:
            $ renpy.call(store.mas_selspr.PROMPT_MAP['clothes']['_ev'])
        "[renpy.substitute(store.mas_selspr.get_prompt('earrings'))]" if 'earrings' in store.mas_selspr.PROMPT_MAP:
            $ renpy.call(store.mas_selspr.PROMPT_MAP['earrings']['_ev'])
        "[renpy.substitute(store.mas_selspr.get_prompt('hair'))]" if 'hair' in store.mas_selspr.PROMPT_MAP:
            $ renpy.call(store.mas_selspr.PROMPT_MAP['hair']['_ev'])
        "[renpy.substitute(store.mas_selspr.get_prompt('hat'))]" if 'hat' in store.mas_selspr.PROMPT_MAP:
            $ renpy.call(store.mas_selspr.PROMPT_MAP['hat']['_ev'])
        "[renpy.substitute(store.mas_selspr.get_prompt('left-hair-clip'))]" if 'left-hair-clip' in store.mas_selspr.PROMPT_MAP:
            $ renpy.call(store.mas_selspr.PROMPT_MAP['left-hair-clip']['_ev'])
        "[renpy.substitute(store.mas_selspr.get_prompt('left-hair-flower'))]" if 'left-hair-flower' in store.mas_selspr.PROMPT_MAP:
            $ renpy.call(store.mas_selspr.PROMPT_MAP['left-hair-flower']['_ev'])
        "[renpy.substitute(store.mas_selspr.get_prompt('necklace'))]" if 'necklace' in store.mas_selspr.PROMPT_MAP:
            $ renpy.call(store.mas_selspr.PROMPT_MAP['necklace']['_ev'])
        "[renpy.substitute(store.mas_selspr.get_prompt('ribbon'))]" if 'ribbon' in store.mas_selspr.PROMPT_MAP:
            $ renpy.call(store.mas_selspr.PROMPT_MAP['ribbon']['_ev'])
    return

label mtrigger_kiss:
    call maica_reconnect
    if mas_shouldKiss(1):
        call maica_hide_console
        call monika_kissing_motion_short
        call maica_show_console
    return 
label mttrigger_minigame(game):
    call maica_reconnect
    call maica_hide_console
    $ renpy.call(game)
    call maica_show_console
    return


label mtrigger_leave: 
    call maica_reconnect
    m "要走了吗, [player]?"
    menu:
        "要走了吗, [player]?{nw}{fast}"
        "是的":
            m 1eka "一会见, [player]!"
            jump mtrigger_quit
            return
        "还没呢":
            m 1eka "谢谢你多陪我一会, [player]."
            return
    return
    
label mtrigger_quit:
    $ persistent.closed_self = True #Monika happily closes herself
    $ mas_clearNotifs()
    jump _quit
    return

label mtrigger_location: 
    call maica_reconnect
    if mas_isMoniEnamored(higher=True):
        call monika_change_background
    else:
        m 1eua "我们好像还没别的地方可去..."
        m 1eksdlb "抱歉啦, [player]."
    return

label mtrigger_idle:
    return "idle"

label mtrigger_idle_callback:
    call maica_reconnect
    m 1eka "你回来啦, [player]!"
    m 1eka "我都要想你了."
    jump maica_main.talking_start

label mtrigger_brb:
    call maica_hide_console
    hide screen mas_background_timed_jump
    $ _history_list.pop()
    $ persistent._mas_idle_data["mtrigger_idle"] = True
    $ mas_setupIdleMode("mtrigger_idle", "mtrigger_idle_callback")
    return

label mtrigger_hold:
    call maica_reconnect
    call maica_hide_console
    call monika_holdme_prep
    call monika_holdme_start
    call monika_holdme_reactions
    call monika_holdme_end
    call maica_show_console
    return

label mtrigger_music_menu:
    call maica_reconnect
    call maica_hide_console
    call display_music_menu
    call maica_show_console
    return

label mtrigger_neteasemusic_search(keyword):
    call maica_reconnect
    call maica_hide_console
    $ store.np_util.Music_Search(np_globals.Search_Word)
    call np_menu_display
    call maica_show_console
    return

label mtrigger_youtubemusic_search(keyword):
    if ytm_utils.is_online():
        if not ytm_globals.is_playing:
            m 1eub "Of course!"
    else:
        m 1rksdla "..."
        m 1rksdlb "We need an internet connection to listen to music online, [player]..."
        return

    python:
        ready = False


    label .input_loop:
        show monika 1eua at t11
        $ raw_search_request = keyword
        $ lower_search_request = raw_search_request.lower()

        if lower_search_request == "":
            if not ytm_globals.is_playing or renpy.music.get_pause():
                m 1eka "Oh...{w=0.2}I really would like to listen to music with you!"
                m 1eub "Let me know when you have time~"

            else:
                m 1eka "Oh, okay."

        else:
            if ytm_utils.is_youtube_url(raw_search_request):
                pass
            else:
                $ ytm_utils.add_search_history(
                    lower_search_request,
                    lower_search_request
                )

                # Since I don't have plans to expand this, I'll leave it as is
                if (
                    not renpy.seen_label("ytm_monika_find_music.reaction_your_reality")
                    and "your reality" in lower_search_request
                ):
                    label .reaction_your_reality:
                        m 3hua "Good choice, [player]~"

                elif (
                    not renpy.seen_label("ytm_monika_find_music.reaction_ily")
                    and "i love you" in lower_search_request
                ):
                    label .reaction_ily:
                        m 1hubsa "I love you too! Ehehe~"

                m 1dsa "Let me see what I can find.{w=0.5}{nw}"

                $ ytm_threading.update_thread_args(ytm_threading.search_music, [raw_search_request])
                call ytm_search_loop
                $ menu_list = _return

                label .menu_display:
                    if menu_list:
                        m 1eub "Alright! Look what I've found!"
                        show monika 1eua at t21
                        call screen mas_gen_scrollable_menu(menu_list, ytm_globals.SCR_MENU_AREA, ytm_globals.SCR_MENU_XALIGN, *ytm_globals.SCR_MENU_LAST_ITEMS)
                        show monika at t11

                        if isinstance(_return, ytm_utils.VideoInfo):
                            call .ytm_process_audio_info(_return.url, add_to_search_hist=False, add_to_audio_hist=True)
                            if not _return:
                                jump .menu_display

                        elif _return == ytm_globals.SCR_MENU_CHANGED_MIND:
                            if not ytm_globals.is_playing:
                                m 1eka "Oh...{w=0.2}{nw}"
                                extend 3ekb "I really love to listen to music with you!"
                                m 1eua "Let me know when you have time~"
                            else:
                                m 1eka "Oh, okay."

                        elif _return == ytm_globals.SCR_MENU_ANOTHER_SING:
                            m 1eub "Alright!"
                            jump .input_loop

                        else:
                            # aka the part you will never get to
                            m 2tfu "{cps=*2}Reading this doesn't seem like the best use of your time, [player].{/cps}{nw}"
                            $ _history_list.pop()

                    else:
                        m 1eud "Sorry, [mas_get_player_nickname(regex_replace_with_nullstr='my ')]...{w=0.5}I couldn't find anything."

                    $ del menu_list

    $ del response_quips, response_quip, raw_search_request, lower_search_request
    return