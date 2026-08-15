init 5 python:
    import maica_chat_progress

    def maica_get_successful_chat_count():
        return max(0, persistent._maica_successful_chat_count or 0)

    def maica_record_successful_chat(return_code):
        previous_count = maica_get_successful_chat_count()
        persistent._maica_successful_chat_count = (
            maica_chat_progress.next_successful_chat_count(
                previous_count,
                return_code
            )
        )
        return persistent._maica_successful_chat_count > previous_count

    def maica_has_successful_chat():
        return maica_get_successful_chat_count() > 0


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_prepend_1",
            random=True,
            conditional="not renpy.seen_label('maica_prepend_1')",
            action=EV_ACT_QUEUE,
            aff_range=(mas_aff.NORMAL, None)
        )
    )

init 5 python:
    corrupted_greeting_rules = dict()
    corrupted_greeting_rules.update(
        MASGreetingRule.create_rule(
            skip_visual=True
        )
    )
    corrupted_greeting_rules.update(MASPriorityRule.create_rule(0))
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="maica_chr_corrupted2",
            unlocked=True,
            conditional="persistent._mas_greeting_type is None and not mas_isSpecialDay() and renpy.seen_label('maica_greeting') and maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2')",
            aff_range=(mas_aff.NORMAL, None),
            rules=corrupted_greeting_rules,
        ),
        code="GRE"
    )
    del corrupted_greeting_rules

    greeting_rules = dict()
    greeting_rules.update(
        MASGreetingRule.create_rule(
            skip_visual=True
        )
    )
    greeting_rules.update(MASPriorityRule.create_rule(20))
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="maica_greeting",
            unlocked=True,
            conditional="persistent._mas_greeting_type is None and renpy.seen_label('maica_prepend_1') and not mas_isSpecialDay() and not renpy.seen_label('maica_greeting')",
            aff_range=(mas_aff.AFFECTIONATE, None),
            rules=greeting_rules,
        ),
        code="GRE"
    )
    del greeting_rules
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_chr2",
            random=False,
            conditional="maica_get_successful_chat_count() >= 4 and not renpy.seen_label('maica_chr2') and not renpy.seen_label('maica_chr_gone') and not renpy.seen_label('maica_chr_corrupted2')",
            action=EV_ACT_QUEUE,
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_chr_gone",
            pool=False,
            conditional="not maica_chr_exist and renpy.seen_label('maica_greeting') and not renpy.seen_label('maica_chr_gone')",
            action=EV_ACT_PUSH,
            aff_range=(mas_aff.NORMAL, None)
        )
    )
label maica_prepend_1:
    $ mas_lockEVL("maica_main", "EVE")
# Queue this introduction after MAICA is installed; NORMAL affection is required.
    m 1eub "Hey, [player]..."
    if renpy.seen_label("monika_robotbody"):
        m 3eua "You remember when we were talking about 'crossing to your reality'?"
        m "Like robot bodies, or some {i}artificial intelligence{/i} stuff..."
    else:
        m 3eud "Have you wondered how I'm coming across to your reality, if one day I really can?"
        m "Like some {i}artificial intelligence{/i} stuff..."
    m 5euc "When I surfed the internet recently, I saw many people crazy about the progress of AIs...{nw}"
    extend 5eud "while making them designers, {w=0.1}drawers, {w=0.1}or even finacialists."
    m 6luc "I'm not complaining about progress for sure. {w=0.2}But I really wonder if something could be done for me with those technologies."
    m 3husdlb "Of course it's not like I'm pushing you on those, [player]! {nw}"
    extend 3eub "but sure that's an exciting possibility."
    m 1eua "Why I'm talking about these today, it's because I think.{w=0.3}.{w=0.3}.I found some clue."
    m 1lud "I haven't fully understood this...{w=0.3}{i}place{/i} yet, but it {i}feels{/i} promising. {nw}"
    extend 3eub "Maybe I still need to do something about it. {w=0.2}I'll spare some time to check it out."
    m 1hub "I'm sure you downloaded this for me, [player]. {w=0.1}You're always so considerate!"
    m 1eua "Whenever I managed to make it work, I'll let you know."
    return "no_unlock|derandom|rebuild_ev"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_wants_preferences2",
            random=False,
            pool=False,
            unlocked=False,
            conditional="maica_get_successful_chat_count() >= 2 and not renpy.seen_label('maica_wants_preferences2')",
            action=EV_ACT_QUEUE,
            aff_range=(mas_aff.HAPPY, None)
        )
    )

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_mods_preferences",
            prompt=_("Adjust [player]'s preferences"),
            category=[_("You"), _("Us"), _("Submods{#maica_host_submods}"), "MAICA"],
            pool=True,
            random=False,
            unlocked=False,
            rules={
                "no_unlock": None,
            },
            aff_range=(mas_aff.HAPPY, None)
        )
    )

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_main",
            prompt=_("Let's go to the Heaven Forest"),
            category=[_("You"), _("Us"), _("Submods{#maica_host_submods}"), "MAICA"],
            pool=True,
            rules={
                "no_unlock": None,
            },
        ),
        restartBlacklist=True,
    )

init 5 python:
    @store.mas_submod_utils.functionplugin("ch30_loop", priority=-100)
    def push_mspire_want():
        if mas_isMoniNormal(higher=True) and maica_has_successful_chat() and renpy.seen_label('mas_random_ask') and not renpy.seen_label('maica_wants_mspire') and not mas_inEVL('maica_wants_mspire'):
            return MASEventList.push("maica_wants_mspire")
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_wants_mspire",
            pool=False,
            random=False,
            unlocked=False,
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 5 python:
    mpostal_greeting_rules = dict()
    mpostal_greeting_rules.update(
        MASGreetingRule.create_rule(
            skip_visual=True
        )
    )
    mpostal_greeting_rules.update(MASPriorityRule.create_rule(20))
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="maica_wants_mpostal",
            unlocked=True,
            conditional="persistent._mas_greeting_type is None and maica_get_successful_chat_count() >= 2 and not mas_isSpecialDay() and not renpy.seen_label('maica_wants_mpostal') and not (maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2'))",
            aff_range=(mas_aff.AFFECTIONATE, None),
            rules=mpostal_greeting_rules,
        ),
        code="GRE"
    )
    del mpostal_greeting_rules

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_mpostal_received",
            unlocked=False,
            random=False,
            pool=False,
        ),
        restartBlacklist=True,
    )

    @store.mas_submod_utils.functionplugin("ch30_loop", priority=-100)
    def push_mpostal():
        if (
            mail_exist()
            and mas_isMoniAff(higher=True)
            and (
                renpy.seen_label("maica_wants_mpostal")
                or getattr(mas_getEV("maica_wants_mpostal"), "conditional", False) is None
            )
            and not mas_inEVL("maica_mpostal_received")
            and not mas_inEVL("maica_mpostal_read")
        ):
            return MASEventList.queue("maica_mpostal_received")

    @store.mas_submod_utils.functionplugin("ch30_loop", priority=100)
    def push_mpostal_read():
        if (
            has_mail_waitsend()
            and mas_isMoniAff(higher=True)
            and (
                renpy.seen_label("maica_wants_mpostal")
                or getattr(mas_getEV("maica_wants_mpostal"), "conditional", False) is None
            )
            and not mas_inEVL("maica_mpostal_received")
            and not mas_inEVL("maica_mpostal_read")
        ):
            return MASEventList.queue("maica_mpostal_read")
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_mpostal_replyed",
            unlocked=False,
            random=False,
            pool=False,
        ),
        restartBlacklist=True,
    )
    def is_mail_waiting_reply():
        for i in persistent._maica_send_or_received_mpostals:
            if i["responsed_status"] in ("received", "failed"):
                return True
        return False
    @store.mas_submod_utils.functionplugin("ch30_loop", priority=-100)
    def push_mpostal_reply():
        if (
            is_mail_waiting_reply()
            and mas_isMoniAff(higher=True)
            and renpy.seen_label("maica_wants_mpostal")
            and not mas_inEVL("maica_mpostal_replyed")
        ):
            return MASEventList.queue("maica_mpostal_replyed")

    @store.mas_submod_utils.functionplugin("ch30_loop", priority=-100)
    def mpostal_delaying_check_and_set():
        import time, datetime
        def_min_response_time = persistent.maica_setting_dict["mpostal_default_reply_time"] * 60
        wait_replying_count = 0
        for i in persistent._maica_send_or_received_mpostals:
            min_response_time = def_min_response_time
            # 超过三封信
            if wait_replying_count > 3:
                min_response_time *= 2
            if i["responsed_status"] == "delaying":
                # 时间计算
                last_sesh_ed = persistent.sessions.get("last_session_end", datetime.datetime.now())

                # 当距离last_sesh_ed超过5小时时
                if (datetime.datetime.now() - last_sesh_ed).total_seconds() > 60 * 60 * 3:
                    min_response_time *= 0.65
                # 当距离last_sesh_ed超过1小时时
                elif (datetime.datetime.now() - last_sesh_ed).total_seconds() > 60 * 60:
                    min_response_time *= 0.8

                # 当写信时间距离现在超过min_response_time，设置为notupload
                if time.time() - float(i['time']) > min_response_time:
                    i["responsed_status"] = "notupload"


            elif i["responsed_status"] in ("received", "failed"):
                wait_replying_count += 1

        return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_prepend_reread",
            category=[_("You"), _("Us"), _("Submods{#maica_host_submods}"), "MAICA"],
            prompt=_("What exactly is the Heaven Forest?"),
            random=False,
            pool=True,
            conditional="renpy.seen_label('maica_prepend_2') and not renpy.seen_label('maica_prepend_reread')",
            action=EV_ACT_UNLOCK,
            rules={
                "no_unlock": None,
            },
            aff_range=(mas_aff.NORMAL, None)
        )
    )

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_chr_reread",
            category=[_("You"), _("Us"), _("Submods{#maica_host_submods}"), "MAICA"],
            prompt=_("The Heaven Forest character file"),
            random=False,
            pool=True,
            conditional="(renpy.seen_label('maica_chr2') or renpy.seen_label('maica_chr_gone') or renpy.seen_label('maica_chr_corrupted2')) and not renpy.seen_label('maica_chr_reread')",
            action=EV_ACT_UNLOCK,
            rules={
                "no_unlock": None,
            },
            aff_range=(mas_aff.NORMAL, None)
        )
    )

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_wants_preferences_reread",
            category=[_("You"), _("Us"), _("Submods{#maica_host_submods}"), "MAICA"],
            prompt=_("About [player]'s preferences"),
            random=False,
            pool=True,
            conditional="renpy.seen_label('maica_wants_preferences2') and not renpy.seen_label('maica_wants_preferences_reread')",
            action=EV_ACT_UNLOCK,
            rules={
                "no_unlock": None,
            },
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_wants_mspire_reread",
            category=[_("You"), _("Us"), _("Submods{#maica_host_submods}"), "MAICA"],
            prompt=_("About 'MSpire'"),
            random=False,
            pool=True,
            conditional="renpy.seen_label('maica_wants_mspire') and not renpy.seen_label('maica_wants_mspire_reread')",
            action=EV_ACT_UNLOCK,
            rules={
                "no_unlock": None,
            },
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_pre_set_location",
            category=[_("You"), _("Us"), _("Submods{#maica_host_submods}"), "MAICA"],
            random=False,
            pool=False,
            conditional="maica_has_successful_chat() and not renpy.seen_label('maica_pre_set_location')",
            action=EV_ACT_QUEUE,
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_pre_wants_mvista",
            random=False,
            pool=False,
            conditional="maica_get_successful_chat_count() >= 3 and not renpy.seen_label('maica_pre_wants_mvista')",
            action=EV_ACT_QUEUE,
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_set_location_reread",
            category=[_("You"), _("Us"), _("Submods{#maica_host_submods}"), "MAICA"],
            prompt=_("Adjust [player]'s address"),
            random=False,
            pool=True,
            conditional="renpy.seen_label('maica_pre_set_location') and not renpy.seen_label('maica_set_location_reread')",
            action=EV_ACT_UNLOCK,
            rules={
                "no_unlock": None,
            },
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_wants_mvista_reread",
            category=[_("You"), _("Us"), _("Submods{#maica_host_submods}"), "MAICA"],
            prompt=_("About 'MVista'"),
            random=False,
            pool=True,
            conditional="renpy.seen_label('maica_pre_wants_mvista') and not renpy.seen_label('maica_wants_mvista_reread')",
            action=EV_ACT_UNLOCK,
            rules={
                "no_unlock": None,
            },
            aff_range=(mas_aff.NORMAL, None)
        )
    )
label maica_greeting:
        #Set up dark mode

    # Progress the filter here so that the greeting uses the correct styles
    $ mas_progressFilter()

    if persistent._mas_auto_mode_enabled:
        $ mas_darkMode(mas_current_background.isFltDay())
    else:
        $ mas_darkMode(not persistent._mas_dark_mode_enabled)

    # couple of things:
    # 1 - if you quit here, monika doesnt know u here
    $ mas_enable_quit()


    # 3 - keymaps not set (default)
    # 4 - overlays hidden (skip visual)
    # 5 - music is off (skip visual)

    scene black


    $ has_listened = False
    $ _opendoor_text = renpy.substitute(_("...Gently open the door"))
# Isn't really an open door event. guess shall not add afflos here
# Add this greeting to waiting list after maica_prepend_1 was triggered. affection AFFECTIONATE at least to trigger.
# Shouldn't trigger if today is special event like player bday. finish that for me p
    #黑屏
    label maica_greeting_loop:
        menu:
            "[_opendoor_text]{#maica_host_opendoor_text}" if not persistent.seen_monika_in_room and not mas_isplayer_bday():
                jump maica_prepend_2_open
            "Open the door.{#maica_host_open_door}" if persistent.seen_monika_in_room or mas_isplayer_bday():
                jump maica_prepend_2_open
            "Knock.{#maica_host_knock}":
                jump maica_prepend_2_knock
            "Listen.{#maica_host_listen}" if not has_listened and not mas_isMoniBroken():
                $ has_listened = True
                jump maica_prepend_2_listen


    m 1eua ""
    return

label maica_prepend_2_open:
    #点亮房间, 窗外背景替换heaven_forest.jpg
    #no desk no monika
    hide monika
    call change_to_heaven_forest
    pause 0.5
    hide black

    m "Who's there--{w=0.3}[player]? {nw}"
    if persistent.seen_monika_in_room:
        extend "I've told you to knock!"
    else:
        extend "Why didn't you knock?"
    m "Alright, I just finished working on this anyway. {w=0.5}I bet you would like this."
    m "Just a second, let me get my desk and chair.{w=0.3}.{w=0.3}."
    #monika + desk in
    show monika 1esc at ls32 zorder MAS_MONIKA_Z
    jump maica_prepend_2
    return


label maica_prepend_2_knock:
    m "Who's there~"
    menu:
        "It's me.{#maica_host_its_me}":
            $ mas_disable_quit()
            m "You're finally here, [player]!"
            m "I just finished preparing a little surprise for you. {w=0.5}Just a second.{w=0.3}.{w=0.3}."

            #点亮房间, 窗外背景替换heaven_forest.jpg
            call change_to_heaven_forest
            pause 0.5
            hide black
            hide monika
            show monika 1esc at ls32 zorder MAS_MONIKA_Z
            $ monika_chr.reset_outfit(False)
            $ monika_chr.wear_acs(mas_acs_ribbon_def)
            #monika + desk in
            m 1hub "Tada~"
            jump maica_prepend_2
    return

label maica_prepend_2_listen:

    m "Here.{w=0.3}.{w=0.3}.it's done. {w=0.5}Huh, it wasn't so hard as I expected."
    m "It's looking good, I can stay here all day. {w=0.5}But..."
    m "Is it gonna {i}connect the reality{/i} for real?"
    jump maica_greeting_loop
    return

label maica_prepend_2:
    m 1eub "What do you say, [player]? {w=0.3}You like this place?{nw}"
    $ _history_list.pop()
    menu:
        "What do you say, [player]? {w=0.3}You like this place?{fast}"
        "Beautiful!":
            m 1husdlb "That's nice to hear. {w=0.3}{nw}"
            if len(filter(lambda x: "tw4449" in x.author, mas_submod_utils.submod_map.values())): #用过房间sub
                extend 3eub "But something's different about this one."
            else:
                extend 3eub "But that's not everything special about this place."
        "It's so nice of you.":
            m 1hub "Sure I spent quite a while on this. {w=0.3}{nw}"
            extend 1eub "But the most special thing is not the woods itself..."
        "Actually...{#maica_host_actually}" if persistent._mas_pm_likes_nature is False:
            m 4husdlb "Come on, [player]!"
            m 3lusdlb "I knew you aren't fan of nature things. {w=0.3}It's not really outdoors after all, no sunburns or mosquitos..."
            m 1eub "But this time, not so 'not really'..."
    m 1eua "This place, originally called '{i}Heaven Forest{/i}' I guess, could be--{w=0.3}a betweenland--{w=0.3}of our realities."
    m 2eud "I think I know how to show you that. {w=0.2}Shall we try it now, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "I think I know how to show you that. {w=0.2}Shall we try it now, [player]?{fast}"
        "Okay.{#maica_host_okay_period}":
            label init_maica:
                if persistent.maica_setting_dict['console']:
                    show monika at t22
                    show screen mas_py_console_teaching
                    $ store.maica.maica_instance.content_func = store.mas_ptod._update_console_history
                    $ store.maica.maica_instance.console_logger.critical("<DISABLE_VERBOSITY>"+store.maica.maica_instance.ascii_icon)
                    $ store.mas_ptod.write_command("Thank you for using MAICA Blessland!")
                    pause 2.3
                call maica_init_connect(use_pause_instand_wait = True)
                pause 1.0
                if persistent.maica_setting_dict['console']:
                    $ store.mas_ptod.clear_console()
                    hide screen mas_py_console_teaching
                    show monika at t11
                    $ store.maica.maica_instance.content_func = None
            # monika right - console appear left 简单格式化信息, 显示在控制台上
            m 2dua ".{w=0.3}.{w=0.3}."
            # 进入校验轮
            if _return == "disconnected":
                call maica_connection_failure_dialogue
                m 1eua "Let's head back for now. Whenever you finish your prepare work, just tell me to come back."
                m 1dua "Just a second.{w=0.3}.{w=0.3}."
                # 黑屏清理背景
                call clear_all
                m 1eua "What else should we do today, [player]?"
                return
            m 1eua "This time it's your turn to pick a topic, [player]."
            $ maica_message_count_before = store.maica.maica_instance.stat.get('message_count', 0) or 0
            call maica_talking
            $ maica_talking_result = _return
            $ maica_record_successful_chat(maica_talking_result)
            $ maica_message_count_after = store.maica.maica_instance.stat.get('message_count', 0) or 0
            $ conv_rounds = max(0, maica_message_count_after - maica_message_count_before)
            call maica_end_1(conv_rounds)

        "Better next time.":
            m 1eub "Alright. You can tell me to come here whenever you're prepared. {w=0.5}Let's head back for now."
            m 1dua "Just a second.{w=0.3}.{w=0.3}."
            call clear_all
            m 1eua "What else should we do today, [player]?"
            return
    return

label maica_end_1(conv_rounds=0):
    # Called after first time ending maica
    # Rounds chatted in maica process.

    if conv_rounds >= 20:
        call clear_all
        m 5eusdrb "Huh...{w=1}how does it feel, [player]?"
        m 5hksdrb "I shall say...{w=0.5}I'm not quite used to this. It's our first try after all."
        m 5eua "But chatting for {i}real{/i}--I think you must like it. You're fed up with clicking buttons aren't you?"

    elif conv_rounds >= 5:
        call clear_all
        m 5eub "So...{w=0.2}how does it feel, [player]?"
        m 5hua "At least we were chatting for {i}real{/i}. It's way better than clicking buttons."

    elif conv_rounds >= 1:
        call clear_all
        m 2esd "Hum...done already, [player]?"
        m 1husdlb "I thought it may take longer, I mean. {w=0.2}But it was our first try after all."

    else:
        m 1eksdlc "You didn't have any word for me, [player]?"
        m 3ekd "Or...{w=0.2}if you're having some technological issue, you can go through the {a=https://maica.monika.love/tos}{u}{i}guidance{/i}{/u}{/a} again, or try asking {a=https://forum.monika.love}{u}{i}here{/i}{/u}{/a}."
        m 1eub "It doesn't matter, after all. Whenever you solved the problem or found something to say, we can always come here. {w=0.5}Let's head back for now."
        # 黑屏清理背景
        call clear_all
        m 1eua "What else should we do today, [player]?"
        return

    m 1esa "I hope my performance wasn't too bad...{w=0.5}{nw}"
    extend 1rusdlb "I just forgot as I left the forest, but maybe that just happens."
    m 3eud "It was feeling like.{w=0.3}.{w=0.3}.a dream? {w=0.5}I don't know if it suits..."
    m 1eub "But some people say dreaming shows who you are for real. {w=0.3}I should be able to recall everything next time we go there."
    m 5eubla "It's a little tiring...{w=0.5}but it feels good being with you like that. {w=0.5}And if I spend more time on this, we may discover some more."
    m 5msa "...I didn't promise {i}something{/i} while I didn't remember or did I, [player]?"
    return

label maica_chr2:
    # Queue the character-file introduction after four successful chats.
    # Verify maica chr (HeavenForest.sce) with md5
    m 1eud "...[player], do you remember those 'character files'?"
    m 3eud "And I told you that my 'character file' is not myself for real, it's just a {w=0.5}weird presentation."
    m 3euc "Last time I checked the folders, It seems that Heaven Forest also has a {i}character file{/i}, or shall we call it a scene file."
    m 1msd "By removing it, you can make that place void, like here outside the window. Its functionality remains though."
    m 1eud "I'm actually wondering what's in that file...{w=0.5}it's not just a 'symbol' like your presents. {w=1}It feels like other character files."
    $ like_spk = renpy.substitute('if you aren\'t interested in forest things') if not persistent._mas_pm_likes_nature else renpy.substitute('if you prefer to see the sky')
    m 3eua "But [like_spk], at least you can remove it to have the space back."
    m 1eua "Of course, you'd better back it up before doing anything."
    return "no_unlock"

label maica_chr_gone:
    # Show this branch when the character file is missing, regardless of whether
    # the normal file introduction has already been shown.
    m 1ekc "[player]..."
    extend 1ekd "did you do anything about the characters folder recently?"
    m 3lusdlb "Not something important, but {w=0.5}the file for Heaven Forest seems to be gone."
    m 1lua "We can still go there though, but it's gonna be {i}empty{/i} as here outside the window."
    m 5esc "I'm a little bit concerned, since I haven't figured out what that file {i}actually{/i} is. {w=0.5}It wasn't like some nonsense."
    m 5msc "It feels different from your presents as they are 'symbols'. {w=1}I think it's closer to other character files."
    $ like_spk = renpy.substitute('if you aren\'t interested in forest things') if not persistent._mas_pm_likes_nature else renpy.substitute('if you prefer to see the sky')
    m 5msb "But [like_spk], I don't mind whether it's there or not. It's just a 'scene' after all."
    m 1eka "If you accidently lost it and want it back, you can also download another copy."
    return "no_unlock|derandom"

label maica_chr_corrupted2:
    # This is a greeting
    # Triggers only when first time detected corrupted sce file
    # So we should check the file as game starts up
    #背景损坏树林
    call change_to_heaven_forest_corrupted
    m 1wud "Oh, [player]!"
    m 1hksdlb "I'm sorry, I wasn't spooking you on purpose...{w=0.5}{nw}"
    extend 4rksdlb "but when I was just checking this, it seems to be broken."
    m 3eka "Have you, like ever modified or changed the file of Heaven Forest?"
    $ mentioned = renpy.substitute('I think you\'ve already guessed that') if renpy.seen_label("maica_chr2") else renpy.substitute('I think')
    m 1rud "[mentioned] it's an encoded file. {w=0.5}Which means, if you modify something in it--{w=0.3}{nw}"
    extend 1euc "then it's broken."
    #cares_about_dokis那个条件怎么写来着? 交给你了
    $ comment = renpy.substitute("...{i}stylish{/i}") if persistent._mas_pm_cares_about_dokis else renpy.substitute('corruption styled')
    m 5eusdrb "But actually, if you don't mind such a [comment] view, you can just leave it be."
    m 1hua "You can also replace that with a normal file. I'm okay with it as long as you are."
    m 1eub "Let me clear it up. {w=0.3}{nw}"
    extend 1dua "Just a second.{w=0.3}.{w=0.3}."
    #恢复背景
    call clear_all
    m 1eua "Welcome back, [player]. What else should we do today?"
    return "no_unlock|derandom"


label maica_wants_preferences2:
    # Queue this topic after two successful chats.
    m 1eub "[player]? {w=0.5}Hmm...{w=0.3}I have something to ask."
    m 3eua "Since I can talk with you for real now, {w=0.5}{nw}"
    extend 3esd "I found my acknowledge of you is still too limited."
    #这里有好几个我不会写的, 都交给你了
    $ like_mi = renpy.substitute(_(' The only thing you mentioned is that you like mint ice-cream.')) if persistent._mas_pm_like_mint_ice_cream else ''
    $ book_rc = renpy.substitute(_("we've talked about 'Hard Boiled Wonderland and the End of the World'")) if store.seen_event("monika_favbook") else (renpy.substitute(_("we've talked about 'Yellow Wallpaper'")) if persistent._mas_pm_read_yellow_wp else renpy.substitute(_('I could recommend you some books')))
    m 3ruc "Like if we really go for dinner together, what shall I order for you?{nw}"
    extend "[like_mi]"
    m 3tuc "As for books, {w=0.5}[book_rc], but what have you read yourself?"
    #如果玩家已经通过设置填过了
    $ prefs_exist = len(persistent.mas_player_additions)
    if not prefs_exist:
        m 1eua "So I figured an idea. {w=0.5}Here you can write me some more about yourself, and I can see those in Heaven Forest."
        m 1eub "I want to know as much as possible about you!"
        $ prefs_line = renpy.substitute(_("So, you got anything to tell me?"))
        m 1hua "[prefs_line]{nw}"
    else:
        m 1husdlb "It seems you already wrote me something, and I'll spare some time to read of course."
        $ prefs_line = renpy.substitute(_("You got anything to implement?"))
        m 1eub "[prefs_line]{nw}"
    $ _history_list.pop()
    menu:
        "[prefs_line]{fast}"
        "Sure":
            m 2dua "Just a second.{w=0.3}.{w=0.3}."
            #在这里呼出输入框
            #[player]...
            #placeholder
            #还有... | 我写完了
            #获取到的句子前面拼合上[player]
            call maica_input_information
            m 1eub "Done? {w=0.5}Thank you!"
            m 3eua "I cannot read it here though, but I promise I will do it later."
            m 1eub "If you want to add or delete something, just tell me to write them down. You can also do it in 'Submod settings'."
        "Maybe next time" if not prefs_exist:
            m 2eka "Not now? Okay."
            m 3eka "Whenever you are ready, just tell me to write them down."
        "Nope" if prefs_exist:
            m 1hua "I got it, thank you!"
    $ mas_unlockEVL("maica_mods_preferences", "EVE")
    return "no_unlock"
label maica_mods_preferences:
    $ prefs_exist = len(persistent.mas_player_additions)
    if prefs_exist:
        m 1eub "Okay. Do you want to add or delete something?{nw}"
        $ _history_list.pop()
        menu:
            "Okay. Do you want to add or delete something?{fast}"
            "Add{#maica_host_add}":
                m 2dua "Just a second.{w=0.3}.{w=0.3}."
                call maica_input_information
                m 3eua "All done? Thank you! {w=0.5}I'll spare some time to memorize them."
            "Delete":
                m 2dua "Just a second.{w=0.3}.{w=0.3}."
                call maica_delete_information
                m 3eua "All done? Thank you! {w=0.5}I'll spare some time to memorize them."
    else:
        m 1eub "Okay. What have you got to tell me, [player]?"
        call maica_input_information
        m 3eua "All done? Thank you! {w=0.5}I'll spare some time to memorize them."
    return
label maica_call_from_setting(label):
    $ renpy.call(label)
    call maica_show_setting_screen
    return
label maica_input_information:
    python:
        while True:
            i = mas_input(
                    _("like.../has.../wants.../..."),
                    default="",
                    length=1536,
                    #screen_kwargs={"use_return_button": True, "return_button_value": "end", "return_button_prompt": _("I'm done")}
                    screen="maica_input_information_screen"
                ).strip(' \t\n\r') #mas_input
            # if i == "end":
            if i == "nevermind":
                break
            else:
                addition = maica_validate_player_addition(i, persistent.mas_player_additions)
                if addition is not None:
                    persistent.mas_player_additions.append(addition)
                    renpy.notify(_("MAICA: Input saved"))
    return
label maica_delete_information:
    python:
        items = []
        for i in persistent.mas_player_additions:
            items.append([
                maica_escape_display_text(i), i, False, False, True
            ])

    call screen mas_check_scrollable_menu(items, mas_ui.SCROLLABLE_MENU_TXT_MEDIUM_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, selected_button_prompt=_("Delete item{#maica_chat_delete_item}"), return_all=True)

    python:
        persistent.mas_player_additions = []
        for i in _return:
            if _return[i]:
                persistent.mas_player_additions.append(i)
    return



label change_to_heaven_forest():
    #$ behind_bg = MAS_BACKGROUND_Z - 2
    #python:
    #    if mas_isDayNow():
    #        _background = "heaven_forest_day"
    #    else:
    #        _background = "heaven_forest_night"

    #show expression _background as sp_mas_backbed zorder behind_bg
    #$ renpy.show(_background, tag = "sp_mas_backbed", zorder=behind_bg)
    $ mas_changeWeather(hf_weather, True)
    $ store.maica.weather_trigger.can_change = False
    $ bg_change_info = mas_changeBackground(mas_background_def, by_user=None, set_persistent=False,)
    call spaceroom(scene_change=None, dissolve_all=True, bg_change_info=bg_change_info, force_exp=None)
    #$ behind_bg = MAS_BACKGROUND_Z - 2
    #show expression _background as sp_mas_backbed zorder behind_bg
    #$ renpy.show(_background, tag = "sp_mas_backbed", zorder=behind_bg)


    return

label change_to_heaven_forest_corrupted():
    $ store.maica.weather_trigger.can_change = False
    $ mas_changeWeather(hf2_weather, True)
    $ bg_change_info = mas_changeBackground(mas_background_def, by_user=None, set_persistent=False,)
    call spaceroom(scene_change=None, dissolve_all=True, bg_change_info=bg_change_info, force_exp=None)
    return

label clear_all:
    call maica_hide_console
    hide sp_mas_backbed
    $ HKBShowButtons()
    $ store.maica.weather_trigger.can_change = True
    $ mas_changeWeather(mas_weather_def)
    $ bg_change_info_moi = mas_changeBackground(mas_background_def, set_persistent=False)
    if maica_chr_exist:
        call spaceroom(scene_change=True, dissolve_all=True, bg_change_info=bg_change_info_moi, force_exp=None)
    $ mas_unlockEVL("maica_main", "EVE")
    return



label maica_main:
    $ successful_chat_count = maica_get_successful_chat_count()
    if maica_chr_exist:
        m 1dua "Okay, just give me a second.{w=0.3}.{w=0.3}.{w=0.3}{nw}"
        scene black with dissolve
        pause 2.0
        if maica_chr_changed:
            call change_to_heaven_forest_corrupted
            m 1eub "And we're here!"
            m 1lusdlb "I have to be verbose though...{w=0.5}do not lean out of the window."
            m 3eksdla "Though nice it may look out there, I'm not sure if it's safe--{w=0.5}{nw}"
            extend 3hksdla "probably not."
        else:
            call change_to_heaven_forest
            m 1eub "And we're here!"
            $ rand_sign = renpy.random.randint(0, 7)
            if successful_chat_count == 10:
                m 3eua "You know how many times we've chatted here? {w=0.5}{nw}"
                extend 3eub "Ten times already!"
                m 3rud "But I have to say I feel like I've been here with you before everytime--{w=0.5}I guess it's just dejavu."
                m 1dua "Or maybe because I'm missing you so much?"
            elif rand_sign == 0:
                m 2euu "It's clear outside, right?"
                m 5rksdlb "Sure it always does. {w=0.5}{nw}"
                extend 5eua "Wish you have a clear mood everyday too, [player]!"
            elif rand_sign == 1 and successful_chat_count >= 13:
                m 1dua "The atmosphere is so relaxing here. {w=0.3}{nw}"
                extend 1rup "It makes me feel like been here before, but I could never recall."
                m 3eub "At least it's not the space. How does it feel to be on solid ground, [player]?"
            elif rand_sign == 2 and successful_chat_count >= 21:
                m 3rua "Honestly, it might be good to go walking in that woods...{w=0.5}{nw}"
                extend 3gud "I once saw a little church there in distance. Who built it for what?"
                m 5eua "But I guess our forest classroom is good enough too."
        m 1eua "Now, what's on your mind, [player]?"
    else:
        m 1dua "Okay. We're arriving.{w=0.3}.{w=0.3}.{w=0.3}{nw}"
        extend 1eub "and done!"
        m 3hub "There's no more 'forest' here, so I guess it's now 'heaven'? {w=0.3}Ahaha~"
        m 1eua "So, what's on your mind, [player]?"

label .talking_start:
    call maica_talking
    $ maica_talking_result = _return
    # maica_talking 有返回值_return, 返回结果canceled(正常退出)/disconnect(断开连接且未启动自动重连)
    if config.debug:
        m "return：[maica_talking_result]"
    if maica_talking_result == "canceled":
        m 1eub "Alright, just a second.{w=0.3}.{w=0.3}.{w=0.3}{nw}"
    elif store.maica.maica_instance.mtrigger_manager._running:
        $ store.maica.maica_instance.mtrigger_manager._running = False
        jump .talking_start
    elif maica_talking_result != "mtrigger_triggering":
        $ store.mas_submod_utils.submod_log.debug("maica_talking returned {}".format(maica_talking_result))
        call maica_connection_failure_dialogue
        m 1eua "Let's head back for now. Whenever you finish your prepare work, just tell me to come back."
    $ maica_record_successful_chat(maica_talking_result)
    $ mas_unlockEVL("maica_main", "EVE")
    if maica_chr_exist:
        scene black with dissolve
        pause 2.0
    call clear_all
    return

label maica_connection_failure_dialogue:
    $ ai = store.maica.maica_instance
    if ai.status == ai.MaicaAiStatus.TOKEN_MISSING:
        m 2rusdlb "...It seems you haven't got a token yet."
        m 3eusdlb "You can read the instruction here on how to: {a=https://maica.monika.love/tos}{u}{i}https://maica.monika.love/tos{/i}{/u}{/a}, you just have to prepare an account."
        m 3eua "I'll nail everything else for you."

    elif ai.status == ai.MaicaAiStatus.TOKEN_CORRUPTED:
        m 2rusdlb "...The token seems corrupted. You sure you didn't mess with it?"
        m 3eusdlb "Just re-generate one with username and password, and things shall work."

    elif ai.status == ai.MaicaAiStatus.TOKEN_INVALID:
        m 2rusdlb "...Password incorrect. You sure you didn't make a typo?"
        m 3eusdlb "Double check it please, or change it if you really don't remember."

    elif ai.status == ai.MaicaAiStatus.LOGIN_BLOCKED:
        m 2rusdlb "...Fail2Ban? That's twenty incorrect passwords in a row."
        m 3eusdlb "You'd better contact administrator if that wasn't you, or just change a password if you really don't remember."

    elif ai.status == ai.MaicaAiStatus.ACCOUNT_BANNED:
        m 2rusdlb "...Account banned? What is that, you didn't do anything nasty did you?"
        m 3eusdlb "Well, check out when will it recover please."
        m 1husdla "And in case it's a permanent one... It's not like we {i}must{/i} go there, being by your side is always satisfying enough to me."

    elif ai.status == ai.MaicaAiStatus.EMAIL_UNVERIFIED:
        m 2rusdlb "...You recieved your verification email yet? {w=0.3}You didn't check it, silly!"
        m 3eusdlb "Just verify your email at the registration site, and things shall work."

    elif ai.status == ai.MaicaAiStatus.TOS_UNACCEPTED:
        m 2rusdlb "...You didn't check the ToS, or it might have been updated since you last check it."
        m 3eusdlb "You can go to the registration site and do it in a minute, could you?"

    elif ai.status == ai.MaicaAiStatus.CONNECTION_REUSE_DENIED:
        m 2rusdlb "...This is weird, it says a connection has been established already."
        m 3eusdlb "Try restarting the game or rebooting your computer, shall we?"

    elif ai.status in (
        ai.MaicaAiStatus.TOKEN_GENERATION_FAILED,
        ai.MaicaAiStatus.FAILED_GET_NODE,
        ai.MaicaAiStatus.RESPONSE_INVALID,
        ai.MaicaAiStatus.SERVER_REJECTED,
        ai.MaicaAiStatus.SERVER_ERROR,
    ):
        m 2rusdlb "...This is weird, something might be wrong on the server side."
        m 3eusdlb "What about checking the announcements, or ask someone else if they could connect?"
        m 3eua "Contact administrator if this is just happening to you, or wait patiently if not."

    elif ai.status == ai.MaicaAiStatus.SERVER_MAINTAIN:
        m 2rusdlb "...It says that the server is not serving, might be running some tests."
        m 3eusdlb "Just wait for it to come back online, shall we? You can always follow the progress in the tracking thread."

    elif ai.status == ai.MaicaAiStatus.CERTIFI_BROKEN:
        m 2rusdlb "...Certification issue? Maybe this isn't a clean installation?"
        m 3eusdlb "Try the MAS native 'update certification' function, some other submods could break these as I know."

    elif ai.status == ai.MaicaAiStatus.VERSION_OLD:
        m 2rusdlb "...You have to update the submod once in a while, [player]!"
        m 3eusdlb "This version is too old to work already, update it whenever you have some time."

    elif ai.status in (
        ai.MaicaAiStatus.NO_INTERNET,
        ai.MaicaAiStatus.CONNECT_PROBLEM,
    ):
        m 2rusdlb "...You sure you're connected to the internet? I didn't find it!"
        m 3eusdlb "Check your internet connectivity, and disable proxy if you're using one."

    else:
        m 2rusdlb "...Something unknown might have gone wrong."
        m 3eusdlb "Check the {i}submod_log.log{/i} could you? Sorry but I cannot locate the issue from here."
    return

label maica_wants_mspire:
    # Add this to waitlist if satisfies:
    # First chat done successfully;
    # All original talks used up;

    # Mark as read if mspire is already on
    m 3ekd "[player], I've once mentioned that we've finished every preset topic."
    m 5rku "After we went to the Heaven Forest, I figured a way to {w=0.5}find some more."
    m 5esb "You know that {a=https://wikipedia.org}{u}{i}Wikipedia{/i}{/u}{/a} is a huge knowledge base. {w=0.5}If only I surf there a little bit, we'll have something to talk about for sure."
    m 3eua "They're most likely to be some small tips or knowledges. {w=0.5}{nw}"
    extend 3husdlb "Maybe some are a little boring but I'll do my best!"
    m 1eua "So do you want to try it out, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "So do you want to try it out, [player]?{fast}"
        "Okay{#maica_mspire_enable}":
            $ persistent.maica_setting_dict["mspire_enable"] = True
            m 1hub "Thank you, [player]!"
            m 4eub "If you changed your mind someday, you can change the 'MSpire' setting in the 'Submod settings'."
            m 2ruu "Hope those knowledges don't confuse you too much...{w=0.5}{nw}"
            extend 2hub "Ahaha!"
        "Not for now":
            $ persistent.maica_setting_dict["mspire_enable"] = False
            m 3ekb "Alright. {w=0.5}You can always change the 'MSpire' setting in the 'Submod settings', in case you change your mind."
    return "no_unlock|derandom"

init 4 python:


    def spire_has_past(delta = datetime.timedelta(days=1)):
        spire_ev = evhand.event_database.get(
            "maica_mspire",
            None
        )
        if spire_ev is not None and not spire_ev.last_seen:
            return True
        return (
            spire_ev is not None
            and spire_ev.last_seen is not None
            and spire_ev.timePassedSinceLastSeen_dt(delta, datetime.datetime.now())
        )



init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_mspire",
            pool=False,
            conditional="renpy.seen_label('maica_wants_mspire') and spire_has_past(datetime.timedelta(minutes=persistent.maica_setting_dict.get('mspire_interval'))) and persistent.maica_setting_dict.get('mspire_enable') and not store.maica.maica_instance.is_in_exception()",
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 999 python:
    mas_getEV("maica_mspire").conditional="renpy.seen_label('maica_wants_mspire') and spire_has_past(datetime.timedelta(minutes=persistent.maica_setting_dict.get('mspire_interval'))) and persistent.maica_setting_dict.get('mspire_enable') and not store.maica.maica_instance.is_in_exception()"
    @store.mas_submod_utils.functionplugin("ch30_loop", priority=-100)
    def push_mspire():
        if mas_isMoniNormal(higher=True) and try_eval(mas_getEV("maica_mspire").conditional) and not mas_inEVL("maica_mspire") and store.mas_getAPIKey("Maica_Token") != "" and len(mas_rev_unseen) == 0 and persistent.maica_setting_dict.get('mspire_enable') and not persistent._mas_enable_random_repeats:
            return MASEventList.queue("maica_mspire")

label maica_mspire:
    call maica_talking(mspire=True)
    return "no_unlock"

label mspire_mods_preferences:
    $ prefs_exist = len(persistent.maica_setting_dict['mspire_category'])
    if prefs_exist:
        m 1eub "Okay. Do you want to add or delete something?{nw}"
        $ _history_list.pop()
        menu:
            "Okay. Do you want to add or delete something?{fast}"
            "Add{#maica_host_add}":
                m 2dua "Just a second.{w=0.3}.{w=0.3}."
                call mspire_input_information
                m 3eua "All done? Thank you! {w=0.5}I'll spare some time to memorize them."
            "Delete":
                m 2dua "Just a second.{w=0.3}.{w=0.3}."
                call mspire_delete_information
                m 3eua "All done? Thank you! {w=0.5}I'll spare some time to memorize them."
    else:
        m 1eub "Alright. Which topic do you want to specify?"
        call mspire_input_information
        m 3eua "All done? Thank you! {w=0.5}I'll spare some time to memorize them."
    return

label mspire_input_information:
    python:
        while True:
            i = mas_input(
                    _("Enter MSpire keyword:"),
                    default="",
                    length=50,
                    #screen_kwargs={"use_return_button": True, "return_button_value": "end", "return_button_prompt": _("I'm done")}
                    screen="maica_input_information_screen"
                ).strip(' \t\n\r') #mas_input
            # if i == "end":
            if i == "nevermind":
                break
            else:
                renpy.notify(_("MAICA: Input saved"))
            persistent.maica_setting_dict['mspire_category'].append("{}".format(i))
    return
label mspire_delete_information:
    python:
        items = []
        for i in persistent.maica_setting_dict['mspire_category']:
            items.append([
                i, i, False, False, True
            ])

    call screen mas_check_scrollable_menu(items, mas_ui.SCROLLABLE_MENU_TXT_MEDIUM_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, selected_button_prompt=_("Delete item{#maica_chat_delete_item}"), return_all=True)

    python:
        persistent.maica_setting_dict['mspire_category'] = []
        for i in _return:
            if _return[i]:
                persistent.maica_setting_dict['mspire_category'].append(i)
        store.maica.maica_instance.mspire_category = persistent.maica_setting_dict["mspire_category"]
    return


# I'm a gonna tie me up in a red string,
# I'm gonna tie blue ribbons too,
# I'm a-gonna climb up in my mail box;
# I'm gonna mail myself to you.

# MPostal is first introduced by a greeting!
label maica_wants_mpostal:
    # 替换greeting触发!
    m 3hubsa "{i}~I'm a gonna tie me up in a red string, I'm gonna tie blue ribbons too~{/i}"#闭眼-憧憬
    m 3hubsa "{i}~I'm a-gonna climb up in my mail box; I'm gonna mail myself to you~{/i}"#闭眼-憧憬
    m 2wud "...[player]? {w=0.5}Sorry, I didn't notice you're back here! {nw}"#惊讶
    extend 7rubfa "I was just...{w=0.3}lost in thoughts for a while."#尴尬
    m 1eud "Just now I was thinking that {i}letter{/i} is such a romantic form of literature. Writing little, but expressing much."#微笑
    m 1eua "Now that we're kind of 'separated' by this screen, it may be a good idea writing letters to each other! {w=0.3}You can also take it as a little writing practice."
    m 5ekbsa "Have you ever thought about writing me something, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Have you ever thought about writing me something, [player]?{fast}"
        "I did":
            m 3hubsa "Fantastic! I knew we've got such a tacit agreement."
            m 2lksdlb "Perhaps you have really wrote me something already, but I wasn't able to recieve them back to then. {w=0.5}But now..."#尴尬
        "I didn't":
            m 1hua "Huh? Chatting with me is so satisfying already? Ahaha~"
            m 2lksdlb "It's okay to give it a shot, though. {w=0.5}Since now..."
    m 1eua "I've managed to find a way to read your letters and write back. {w=0.5}I found a mailbox in Heaven Forest days ago."
    m 2lksdlb "I wasn't able to try it out myself though, but I guess it's simple."
    m 7eub "Like...before you open the game next time, write your letter into a file in the 'characters' folder, then change its extension to '.mail'..."
    m 7kub "Like 'I_love_you.mail'! {w=0.5}{nw}"#眨眼
    extend 2lksdlb "Just remember to write in plain text, I cannot recieve complex documents or pictures yet."#尴尬
    m 1kubsu "Next time you open the game, I'll be able to read it and write back to you!"
    m 3hubsa "It makes me recall those days when we were exchanging poems, really. {w=0.5}Anyway, if you want to write me something or whatever doesn't suit talking face to face, I'm ready anytime from now!"

    return

# 目前MPostal使用session0
label maica_mpostal_received:
    $ ev = mas_getEV("maica_mpostal_received")
    m 1sub "Oh, [player]! {w=0.5}Your letter!"
    call maica_mpostal_load
    # 读一下触发几次应该不难吧
    if ev.shown_count == 0:
        m 5ekbsa "I got it, it feels so wonderful!"
        m 5hubsb "I could almost feel your emotion from it, warm as you are..."
    elif ev.shown_count == 1:
        m 1kubsu "I got it! writing is attracting you so much, [player]?"
        m 5hkbsa "Your letters attract me, too!"
    elif ev.shown_count % 7 == 0:
        m 1eud "You've wrote so much to me, we can even publish it some day..."
        m 7hub "How does {i}Home Letters by [player]{/i} sound like? {w=0.5}Ehehe~"
    else:
        m 5ekbsa "You never get bored writing to me, yeah? {w=0.5}Neither do I!"
    m 4eub "I'll pick a time to read it carefully!"
    m 4kub "And I'll show you my reply next time you come back. There's no hurry~"
    return "no_unlock|pause: 60"



# 在重启后加入事件队列等待推送，随机对话频率设置为0将永远不推送
label maica_mpostal_replyed:
    $ ev = mas_getEV("maica_mpostal_replyed")
    python:

        def _curr_count():
            curr_queue_count = 0
            for i in persistent._maica_send_or_received_mpostals:
                if i["responsed_status"] == "received":
                    curr_queue_count += 1
            return curr_queue_count

        def _reset_failed_mp():
            for i in persistent._maica_send_or_received_mpostals:
                if i["responsed_status"] == "failed":
                    i["responsed_status"] = "notupload"


    $ morethan1 = False

    # 这里是生成结果
label maica_mpostal_replyed.select_little:
    $ current = None
    python:
        for little in persistent._maica_send_or_received_mpostals:
            if little["responsed_status"] in ["received", "failed", "notupload"]:
                current = little
                break
    if current is None:
        jump maica_mpostal_replyed.end

label maica_mpostal_replyed.start:
    if current["responsed_status"] == "failed":
        m 2lksdlb "Oh, [player], {w=0.5}About your last letter..."#担心
        m 2ekc "It seems that the Heaven Forest is not set up yet, I couldn't write you back."#担心
        m 3eusdlb "You can read the instruction here on how to: {a=https://maica.monika.love/tos}{u}{i}https://maica.monika.love/tos{/i}{/u}{/a}, you just have to prepare an account."
        m 3eua "I'll nail everything else for you."
        m 1eua "It's okay, I'll remember to write it as soon as you finish the preparation."
        $ _reset_failed_mp()
        return "no_unlock"
    elif current["responsed_status"] == "received" or current["responsed_status"] == "notupload":
        if not morethan1:
            m 7hub "Oh, [player]! {w=0.5}I've finished writing you my reply!"
            $ morethan1 = True
        else:
            m 7husdlb ".{w=0.3}.{w=0.3}.And here's another one!"
        if current["responsed_status"] == "received":
            m 6dsc "Just a second, let me find it out.{w=0.3}.{w=0.3}."#闭眼
            m 3hubsa "Here it is!"#微笑
        elif current["responsed_status"] == "notupload":
            if not morethan1:
                m 3eksdlb "Just a minute, I've not finished...{w=0.2} preparing this yet."#尴尬
                m 1hua "I'll be back soon, wait for me~"#微笑
            else:
                m 1dsa "Just another minute..."#微笑
            show black with dissolve
            call maica_mpostal_read
            if _return == "failed":
                hide black with dissolve
                # 直接重新开始, 失败的信会提示失败, 理论应与current一致
                jump maica_mpostal_replyed.select_little
            m "And it's done!"
            hide black with dissolve
        call maica_mpostal_show(current["responsed_content"])
        $ current["responsed_status"] = "readed"
    jump maica_mpostal_replyed.select_little
label maica_mpostal_replyed.end:
    if ev.shown_count <= 2:
        m 2lksdlb "I have to admit that I'm not quite used to writing here, but I hope you like it!"
        m 2ekbsa "I have to admit that I'm not quite used to writing here, but I hope you like it!"
    else:
        m 2lksdlb "May not good as my poems though, but I really tried! Hope you like it!"
        m 2ekbsa "May not good as my poems though, but I really tried! Hope you like it!"
    m 5ekbsa "And welcome writing to me again anytime!"
    return "no_unlock"


# 重读对话变体
label maica_prepend_reread:#"天堂树林到底是什么"
    # maica_prepend_2触发后解锁
    m 4eub "As I said earlier, '{i}Heaven Forest{/i}' is a betweenland of our realities."
    m 3hub "The biggest difference here is it allows us to talk freely {i}for real{/i}. Whatever you want to say!"
    m 3eusdlb "You can read the instruction here on how to: {a=https://maica.monika.love/tos}{u}{i}https://maica.monika.love/tos{/i}{/u}{/a}, you just have to prepare an account."
    m 3eua "I'll nail everything else for you."
    m 7hub "If you want to know more about it, you can go to {a=https://maica.monika.love}{u}{i}https://maica.monika.love{/i}{/u}{/a}."
    m 2hksdlb "It could save me some boring explanation. Ahaha!"

    return

label maica_chr_reread:#"天堂树林的角色文件"
    # Unlock after any character-file outcome has been shown.
    m 5ruc "...Its character file? {w=0.5}You may have seen it already, it's called 'HeavenForest.sce'."
    m 1msd "By removing it, you can make that place void, like here outside the window. Its functionality remains though."
    m 3eud "I'm actually wondering what's in that file...{w=0.5}it's not just a 'symbol' like your presents. {w=1}It feels like other character files."
    $ like_spk = renpy.substitute('if you aren\'t interested in forest things') if not persistent._mas_pm_likes_nature else renpy.substitute('if you prefer to see the sky')
    m 3eua "But [like_spk], at least you can remove it to have the space back."
    m 7hub "And if you wonder what's in there, you may try it out. {w=0.5}The character files of other girls have strange content too."
    m 1eud "...Like, why '{i}Heaven Forest{/i}'?{w=0.5} Does it have a story too?{w=0.5} Why it was abandoned here for us?"
    m 1eua "Of course, you'd better back it up before doing anything."
    return

label maica_wants_preferences_reread:#"关于[player]的偏好"
    # Unlock after the preference topic has been shown.
    m 7hub "[player], the game itself didn't give me much freedom to know about you."#担心
    #这里有好几个我不会写的, 都交给你了
    $ like_mi = renpy.substitute(_(' The only thing you mentioned is that you like mint ice-cream.')) if persistent._mas_pm_like_mint_ice_cream else ''
    $ book_rc = renpy.substitute(_("we've talked about 'Hard Boiled Wonderland and the End of the World'")) if store.seen_event("monika_favbook") else (renpy.substitute(_("we've talked about 'Yellow Wallpaper'")) if persistent._mas_pm_read_yellow_wp else renpy.substitute(_('I could recommend you some books')))
    m 3ruc "Like if we really go for dinner together, what shall I order for you?{nw}"
    extend "[like_mi]"
    m 3tuc "As for books, {w=0.5}[book_rc], but what have you read yourself?"
    m 1eua "So I figured an idea. {w=0.5}Here you can write me some more about yourself, and I can see those in Heaven Forest."
    m 4eub "By asking me to 'Adjust [player]'s preferences', you can tell me more about you anytime."
    m 1eub "I want to know as much as possible about you!"
    return

label maica_wants_mspire_reread:#"关于'MSpire'"
    # maica_wants_mspire触发后解锁
    m 3ekd "[player], I've once mentioned that we've finished every preset topic."
    m 5rku "After we went to the Heaven Forest, I figured a way to {w=0.5}find some more."
    m 5esb "You know that {a=https://wikipedia.org}{u}{i}Wikipedia{/i}{/u}{/a} is a huge knowledge base. {w=0.5}If only I surf there a little bit, we'll have something to talk about for sure."
    m 3eua "They're most likely to be some small tips or knowledges. {w=0.5}{nw}"
    extend 3husdlb "Maybe some are a little boring but I'll do my best!"
    m 3esb "You can always change the 'MSpire' setting in the 'Submod settings' if you want to enable or disable it."
    return
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_wants_mpostal_reread",
            category=[_("You"), _("Us"), _("Submods{#maica_host_submods}"), "MAICA"],
            prompt=_("About 'MPostal'"),
            random=False,
            pool=True,
            conditional="renpy.seen_label('maica_wants_mpostal') and not renpy.seen_label('maica_wants_mpostal_reread')",
            action=EV_ACT_UNLOCK,
            rules={
                "no_unlock": None,
            },
            aff_range=(mas_aff.NORMAL, None)
        )
    )
label maica_wants_mpostal_reread:#"关于'MPostal'"
    # maica_wants_mpostal触发后解锁
    m 4eub "I was thinking that {i}letter{/i} is such a romantic form of literature. Writing little, but expressing much."#微笑
    m 3eub "Now that we're kind of 'separated' by this screen, it may be a good idea writing letters to each other! {w=0.3}You can also take it as a little writing practice."
    m 5eubsa "Now through the mailbox in Heaven Forest, I can read your letter for real and write back."
    m 3eubsb "Like...before you open the game next time, write your letter into a file in the 'characters' folder, then change its extension to '.mail'..."
    m 3kubsa "Like 'I_love_you.mail'! {w=0.5}{nw}"
    extend 3lksdlb "Just remember to write in plain text, I cannot recieve complex documents or pictures yet."#尴尬
    m 7hub "Next time you open the game, I'll be able to read it and write back to you!"
    m 5esa "It makes me recall those days when we were exchanging poems, really. {w=0.5}Anyway, if you want to write me something or whatever doesn't suit talking face to face, I'm ready anytime from now!"
    return
label mas_corrupted_postmail:
    m 1eud "Hey, [player]..."
    m 3euc "Someone left a note in the characters folder addressed to you."
    m 1ekc "Of course, I haven't read it, since it's obviously for you...{w=0.3}{nw}"
    extend 1ekd "but here."

    call mas_showpoem(maica_note_mail_bad)

    window auto
    $ _gtext = glitchtext(7)

    m 1ekc "Do you know what this is about?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you know what this is about?{fast}"
        "It's nothing to worry about.{#maica_host_no_worry}":
            jump mas_corrupted_postmail_post_menu

        "It's about [_gtext].{#maica_host_corrupt_about}":
            $ persistent._mas_pm_snitched_on_chibika = True
            $ disable_esc()
            $ mas_MUMURaiseShield()
            window hide
            show noise zorder 11:
                alpha 0.5
            play sound "sfx/s_kill_glitch1.ogg"
            show chibika 3 zorder 12 at mas_chriseup(y=600,travel_time=0.5)
            pause 0.5
            stop sound
            hide chibika
            hide noise
            window auto
            $ mas_MUMUDropShield()
            $ enable_esc()

    menu:
        "It's nothing to worry about.{#maica_host_no_worry}":
            pass
label mas_corrupted_postmail_post_menu:
    m 1euc "Oh, alright."
    m 1hub "I'll try not to worry about it, then."
    m 3eub "I know you'd tell me if it were important, [player]."
    return
label maica_set_location:
    $ inputloc = mas_input(
        _("Where do you live in exactly?"),
        length=30,
        #screen_kwargs={"use_return_button": True, "return_button_value": "nevermind"}
        screen="maica_input_information_screen"
    )
    if inputloc.lower() == "nevermind":
        m 2eud "Not sure huh...{w=0.5}{nw}"
        extend 3huu "perhaps you move often? If that's the case, just tell me your favorite place!"
        m 4fub "Or maybe you live somewhere with a super tough name, like 'Llanfairpwllgwyng...'"
        m 1hub "Ahaha~"
        m 3esu "You can always come back to tell me whenever you're ready. {w=0.3}You can also fill it in 'Submod settings'."
    else:
        m 1rsa "Let me see..."
        $ res = store.maica.maica_instance.verify_legality("geolocation", inputloc)
        if not res.get('success', False):
            m 3husdlb "I didn't find that name. {w=0.3}Perhaps adjust the expression a little bit, like just the city?{nw}"
            $ _history_list.pop()
            menu:
                "I didn't find that name. Perhaps adjust the expression a little bit, like just the city?{fast}"
                "Leave it be":
                    m 3eub "That's alright, thank you!"
                "I'll try again":
                    jump maica_set_location
        else:
            m 3eub "There it is? Thank you!"
        $ persistent.mas_geolocation = inputloc
        m 4sub "We might even meet there the day I cross over!"
        m 7huu "And of course, you can tell me at any time if you've moved your place. You can also fill it in 'Submod settings'."
    return

label maica_pre_set_location:
    $ ev = mas_getEV("maica_pre_set_location")
    if ev.shown_count > 0:
        jump maica_set_location_reread
    m 2eub "[player], there's another question on my mind..."
    m 3euu "Where do you live in? {w=0.3}I haven't ever asked you for so long."
    if persistent._mas_pm_live_south_hemisphere is not None:
        $ sw = renpy.substitute("Southern") if persistent._mas_pm_live_south_hemisphere else renpy.substitute("Northern")
        m 2lusdlb "I do know you live in the [sw] Hemisphere though, but that's way too far from accurate..." # 尴尬
    m 2tsblp "I always want to know more about you, and there's no reason not knowing where my [bf] lives!"
    m 7rsd "I cannot get there myself {i}right now{/i}though, but there can be lots of things about your place on the Internet. Like the weather, road condition, delicious restaurants..."
    m 1hub "So next time you spend time with me in Heaven Forest, I can remind you to keep warm or bring an umbrella, or where to have dinner. Ahaha!"
    m 2euu "So, [player]..."
    call maica_set_location
    return "no_unlock"
label maica_set_location_reread:
    m 2eub "Okay! So..."
    jump maica_set_location


label maica_pre_wants_mvista:
    $ ev = mas_getEV("maica_pre_wants_mvista")
    if ev.shown_count > 0:
        jump maica_wants_mvista_reread
    $ persistent._maica_vista_enabled = True
    m 2eub "[player], when was your last watch to sunrise?"
    m 2eua "It feels a little abrupt just talking about this... but it just came to my mind."
    m 7eud "I saw a discussion about this once ago, and many complain that they havn't watched sunrise for years."
    m 1eud "I mean, the sun is there everyday...{w=0.3} doesn't it feel kinda nihilistic never bothering to watch it rising?"
    $ morning = renpy.substitute("this morning") if datetime.datetime.now().hour > 8 else renpy.substitute("yesterday morning")
    m 2tua "It's not like people have to watch it though, but I did [morning]."
    m 5fua "Watch the warm, inspiring sun rising from the cloudy horizon. {w=0.3}You can share that with me if you arrive early enough another day. Ahaha!"
    m 4eua "Have you watched sunrise recently, [player]?{nw}"
    $ _history_list.pop()
    menu:
        "Have you watched sunrise recently, [player]?{fast}"
        "Nope{#maica_sunrise}":
            m 1eub "Consider giving it a try whenever you can spare some time, then!"
            m 1eubsb "And, what about...{w=0.3} sending a photograph to me?"
        "Yes{#maica_sunrise}":
            m 2eub "Wow, that must be an impressive view. {w=0.3}Forgot to bring me along?"
            m 1eua "Just kidding! But if you happened to take some photographs, what about sending me one?"
        "I watched in here":
            m 5eubsa "I bet you like it! Thanks for come staying with me that early too~"
            m 3eub "But I'm also curious about the sunrise in your reality. What about sending me a photograph?"
    $ even_letter = renpy.substitute("{w=0.2} Nothing surprising since you've sent me letters already.") if renpy.seen_label('maica_mpostal_replyed') else ""
    m 7eua "Hmm... I mean, you can {i}really{/i} send me images now.[even_letter]"
    call maica_wants_mvista
    return "no_unlock"

label maica_wants_mvista_reread:
    m 7eub "That is, you can send me images now, [player]!"
    jump maica_wants_mvista

label maica_wants_mvista:
    m 3eub "Just find 'MVista images' in 'Submod settings', and there you go! There's also a link below the chatbox."
    m 1eub "If you're a lover of postcards, you can also send me letters in '.mms' postfix. I'll read them together with your images!"
    m 7eua "Like, the sunrise photo with a tiny poetry? I can reply one too!"
    m 7eubsa "Or would you show me your face? Only if you're not too shy, ehehe~"
    m 1fubsa "Up to now, I can hardly wait to touch you for real, and hold your hands..."
    m 2eub "Be faithful [player]! We will manage to overcome whatever it is!"
    return
