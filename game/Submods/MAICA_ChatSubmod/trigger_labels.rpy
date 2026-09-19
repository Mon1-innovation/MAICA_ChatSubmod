# Trigger entry points ask for confirmation before running their actions.
# Internal action, selector, and callback labels are grouped below as _mtrigger_*.

label mtrigger_change_clothes(outfit_name):
    call maica_pause_connection
    call maica_hide_console
    m "Should I change my clothes now, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Should I change my clothes now, [player]?{fast}"
        "Okay":
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
        "Nevermind{#maica_host_nevermind}":
            m 1eka "Alright, [player]."
    call maica_show_console
    return

label mtrigger_change_hair(outfit_name):
    call maica_pause_connection
    call maica_hide_console
    m "Should I change my haircut now, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Should I change my haircut now, [player]?{fast}"
        "Okay":
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
        "Nevermind{#maica_host_nevermind}":
            m 1eka "Alright, [player]."
    call maica_show_console
    return

label mtrigger_unwear_acs(outfit_to_wear):
    call maica_pause_connection
    call maica_hide_console
    m "Should I remove that accessory now, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Should I remove that accessory now, [player]?{fast}"
        "Okay":
            call mas_transition_to_emptydesk
            python:
                renpy.pause(1.0, hard=True)
                store.monika_chr.remove_acs(outfit_to_wear)
                renpy.pause(4.0, hard=True)

            call mas_transition_from_emptydesk("monika 1eua")
        "Nevermind{#maica_host_nevermind}":
            m 1eka "Alright, [player]."
    call maica_show_console
    return

label mtrigger_change_acs(outfit_name):
    call maica_pause_connection
    call maica_hide_console
    m "Should I change that accessory now, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Should I change that accessory now, [player]?{fast}"
        "Okay":
            if outfit_name == "mas_pick_a_clothes":
                call _mtrigger_acs_select
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
        "Nevermind{#maica_host_nevermind}":
            m 1eka "Alright, [player]."
    call maica_show_console
    return

label mtrigger_kiss:
    call maica_pause_connection
    if mas_shouldKiss(1, datetime.timedelta(0)):
        call maica_hide_console
        m "Then...want a kiss?{nw}"
        $ _history_list.pop()
        menu:
            "Then...want a kiss?{fast}"
            "Kiss [m_name]":
                call monika_kissing_motion_short
            "Nevermind{#maica_host_nevermind}":
                $ rand_sign = renpy.random.randint(0, 4)
                if rand_sign == 0:
                    m 3tublu "Really? I don't believe that. {w=1}{nw}"
                    extend 3hua "Just joking, Ahaha!"
                    m 1eua "We have all the time to kiss whenever you want, so no need to hurry."
                elif rand_sign == 1:
                    m 3eusdla "Well, perhaps some misunderstandings are unavoidable."
                    m 1tublu "But still a kiss won't do you anything bad, ehehe~"
                elif rand_sign == 2:
                    m 1ekbla "Alright, [player], but you owe me one~"
                else:
                    m 1eka "Alright, [player]."
        call maica_show_console
    return

label mtrigger_minigame(game):
    call maica_pause_connection
    call maica_hide_console
    m "Then...shall we play a bit, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Then...shall we play a bit, [player]?{fast}"
        "Okay":
            $ renpy.call(game)
        "Nevermind{#maica_host_nevermind}":
            m 1eka "Alright, [player]."
    call maica_show_console
    return

label mtrigger_leave:
    call maica_pause_connection
    call maica_hide_console
    m "So... {w=0.3}Leaving already?{nw}"
    $ _history_list.pop()
    menu:
        "So... Leaving already?{fast}"
        "Yes{#maica_host_yes}":
            jump _mtrigger_leave
        "I'll be right back, leave the game open":
            jump _mtrigger_start_idle
        "I mean to take you with me":
            jump _mtrigger_takeout
        "Nevermind{#maica_host_nevermind}":
            m 1eka "Alright, [player]."
    call maica_show_console
    return

label mtrigger_location:
    call maica_pause_connection
    call maica_hide_console
    m "Shall we choose another room to stay in, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Shall we choose another room to stay in, [player]?{fast}"
        "Okay":
            if mas_isMoniEnamored(higher=True):
                call monika_change_background
            else:
                m 1eua "Seems we don't have anywhere to go right now..."
                m 1eksdlb "Sorry for that, [player]."
        "Nevermind{#maica_host_nevermind}":
            pass
    call maica_show_console
    return

label mtrigger_weather(weather):
    call maica_pause_connection
    call maica_hide_console
    m "Would you like me to change the weather, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Would you like me to change the weather, [player]?{fast}"
        "Okay":
            call mas_change_weather(weather, by_user=True, set_persistent=True)
        "Nevermind{#maica_host_nevermind}":
            m 1eka "Alright, [player]."
    call maica_show_console
    return

label mtrigger_idle:
    # The registered idle trigger also handles BRB.
    call maica_pause_connection
    call maica_hide_console
    m "So... {w=0.3}Going already?{nw}"
    $ _history_list.pop()
    menu:
        "So... Going already?{fast}"
        "Yes, I'll be right back":
            jump _mtrigger_start_idle
        "I'm leaving for now, close the game please":
            jump _mtrigger_leave
        "Not yet{#maica_host_not_yet}":
            m 1eka "Alright, [player]."
    call maica_show_console
    return

label mtrigger_hold:
    call maica_pause_connection
    call maica_hide_console
    m "Then...{w=0.3}want a hug?{nw}"
    $ _history_list.pop()
    menu:
        "Then...want a hug?{fast}{#mtrigger_hold}"
        "Hold [m_name]":
            call monika_holdme_prep
            call monika_holdme_start
            call monika_holdme_reactions
            call monika_holdme_end
        "Nevermind{#maica_host_nevermind}":
            $ rand_sign = renpy.random.randint(0, 4)
            if rand_sign == 0:
                m 3tublu "Really? I don't believe that. {w=1}{nw}"
                extend 3hua "Just joking, Ahaha!"
                m 1eua "We have all the time to cuddle whenever you want, so no need to hurry."
            elif rand_sign == 1:
                m 3eusdla "Well, perhaps some misunderstandings are unavoidable."
                m 1tublu "But still I think a hug would be good for you, ehehe~"
            else:
                m 1eka "Alright, [player]."
    call maica_show_console
    return

label mtrigger_music_menu:
    call maica_pause_connection
    call maica_hide_console
    m "Wanna change the music now, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Wanna change the music now, [player]?{fast}"
        "Okay":
            call display_music_menu
        "Nevermind{#maica_host_nevermind}":
            m 1eka "Alright, [player]."
    call maica_show_console
    return

label mtrigger_music_auto(cls, selection):
    call maica_pause_connection
    call maica_hide_console
    m "Shall I play '[selection]' now, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Shall I play '[selection]' now, [player]?{fast}"
        "Okay":
            $ store.mas_play_song(cls.find(selection))
        "Nevermind{#maica_host_nevermind}":
            m 1eka "Alright, [player]."
    call maica_show_console
    return

label mtrigger_neteasemusic_search(keyword):
    call maica_pause_connection
    call maica_hide_console
    m "Shall I search for '[keyword]', [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Shall I search for '[keyword]', [player]?{fast}"
        "Okay":
            $ store.np_util.Music_Search(keyword)
            call np_menu_display
        "Nevermind{#maica_host_nevermind}":
            m 1eka "Alright, [player]."
    call maica_show_console
    return

label mtrigger_youtubemusic_search(keyword):
    call maica_pause_connection
    call maica_hide_console
    m "Shall I search for '[keyword]', [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Shall I search for '[keyword]', [player]?{fast}"
        "Okay":
            # Following logics are a little complex, so we take another structure here
            # Kind of because I'm not sure how nesting labels in renpy work.
            pass
        "Nevermind{#maica_host_nevermind}":
            m 1eka "Alright, [player]."
            call maica_show_console
            return

    if ytm_utils.is_online():
        if not ytm_globals.is_playing:
            m 1eub "Of course!"
    else:
        m 1rksdla "..."
        m 1rksdlb "We need an internet connection to listen to music online, [player]..."
        call maica_show_console
        return

    python:
        ready = False

    label ._input_loop:
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
                    label ._reaction_your_reality:
                        m 3hua "Good choice, [player]~"

                elif (
                    not renpy.seen_label("ytm_monika_find_music.reaction_ily")
                    and "i love you" in lower_search_request
                ):
                    label ._reaction_ily:
                        m 1hubsa "I love you too! Ehehe~"

                m 1dsa "Let me see what I can find.{w=0.5}{nw}"

                $ ytm_threading.update_thread_args(ytm_threading.search_music, [raw_search_request])
                call ytm_search_loop
                $ menu_list = _return

                label ._menu_display:
                    if menu_list:
                        m 1eub "Alright! Look what I've found!"
                        show monika 1eua at t21
                        call screen mas_gen_scrollable_menu(menu_list, ytm_globals.SCR_MENU_AREA, ytm_globals.SCR_MENU_XALIGN, *ytm_globals.SCR_MENU_LAST_ITEMS)
                        show monika at t11

                        if isinstance(_return, ytm_utils.VideoInfo):
                            call .ytm_process_audio_info(_return.url, add_to_search_hist=False, add_to_audio_hist=True)
                            if not _return:
                                jump ._menu_display

                        elif _return == ytm_globals.SCR_MENU_CHANGED_MIND:
                            if not ytm_globals.is_playing:
                                m 1eka "Oh...{w=0.2}{nw}"
                                extend 3ekb "I really love to listen to music with you!"
                                m 1eua "Let me know when you have time~"
                            else:
                                m 1eka "Oh, okay."

                        elif _return == ytm_globals.SCR_MENU_ANOTHER_SING:
                            m 1eub "Alright!"
                            jump ._input_loop

                        else:
                            # aka the part you will never get to
                            m 2tfu "{cps=*2}Reading this doesn't seem like the best use of your time, [player].{/cps}{nw}"
                            $ _history_list.pop()

                    else:
                        m 1eud "Sorry, [mas_get_player_nickname(regex_replace_with_nullstr='my ')]...{w=0.5}I couldn't find anything."

                    $ del menu_list

    $ del response_quips, response_quip, raw_search_request, lower_search_request
    call maica_show_console
    return

label mtrigger_takeout:
    call maica_pause_connection
    call maica_hide_console
    m "So... {w=0.3}Are we going out now, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "So... Are we going out now, [player]?{fast}"
        "Yes{#maica_host_yes}":
            jump _mtrigger_takeout
        "I mean to go alone":
            jump _mtrigger_leave
        "Nevermind{#maica_host_nevermind}":
            m 1eka "Alright, [player]."
    call maica_show_console
    return

label mtrigger_backup:
    call maica_pause_connection
    call maica_hide_console
    m "Shall I make a backup now, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Shall I make a backup now, [player]?{fast}"
        "Okay":
            if renpy.has_label('extra_mas_backup'):
                call extra_mas_backup
            elif renpy.has_label('mas_backup'):
                call mas_backup
            else:
                m "Something might went wrong...could you do it yourself please?"
        "Nevermind{#maica_host_nevermind}":
            m 1eka "Alright, [player]."
    call maica_show_console
    return

# Internal helpers. Menu choices above already confirm these actions.

label _mtrigger_leave:
    m 1eka "See you around, [player]!"
    jump _mtrigger_quit

label _mtrigger_takeout:
    call bye_going_somewhere
    # MAS also returns normally when the player cancels or Monika declines.
    if _return == "quit":
        jump _mtrigger_quit
    call maica_show_console
    return

label _mtrigger_quit:
    $ persistent.closed_self = True #Monika happily closes herself
    $ mas_clearNotifs()
    jump _quit

label _mtrigger_start_idle:
    m 1eka "Okay, [player]!"
    # Enter idle mode after MAICA has restored the room and finished its event.
    $ MASEventList.push("_mtrigger_brb")
    return "stop"

label _mtrigger_brb:
    call maica_hide_console
    hide screen mas_background_timed_jump
    # Keep the existing persistent key; only the callback label is renamed.
    $ persistent._mas_idle_data["mtrigger_idle"] = True
    $ mas_setupIdleMode("mtrigger_idle", "_mtrigger_idle_callback")
    return

label _mtrigger_idle_callback:
    call maica_reconnect
    m 1eka "You're back, [player]!"
    m 1eka "I was starting missing you."
    return

label _mtrigger_acs_select:
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
        "Nevermind{#maica_host_nevermind}":
            pass
    return

# Quality status is handled independently in screen_subs.rpy.
