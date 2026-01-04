init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_prepend_1",
            prompt="你的现实?",
            random=True,
            conditional="not renpy.seen_label('maica_prepend_1')",
            action=EV_ACT_QUEUE,
            rules={
                "bookmark_rule":mas_bookmarks_derand.BLACKLIST,
            },
            aff_range=(mas_aff.NORMAL, None)
        )
    )

init 5 python:
    if renpy.seen_label('maica_prepend_1') and not mas_isSpecialDay() and not renpy.seen_label('maica_greeting') and _mas_getAffection() > 100:
        @store.mas_submod_utils.functionplugin("ch30_post_exp_check", priority=-100)
        def greeting_select():
            store.selected_greeting = "maica_greeting"
        ev_rules = dict()
        ev_rules.update(
            MASGreetingRule.create_rule(
                skip_visual=True,
                override_type=True
            )
        )
        ev_rules.update(MASPriorityRule.create_rule(50))
        
        addEvent(
            Event(
                persistent.greeting_database,
                eventlabel="maica_greeting",
                prompt="maica敲门",
                unlocked=False,
                conditional="renpy.seen_label('maica_prepend_1') and not mas_isSpecialDay() and not renpy.seen_label('maica_greeting')",
                action=EV_ACT_UNLOCK,
                aff_range=(mas_aff.AFFECTIONATE, None),
                rules=ev_rules,
            ),
            code="GRE"
        )
        del ev_rules
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_chr2",
            prompt="天堂树林的文件",
            conditional="renpy.seen_label('maica_end_1')",
            action=EV_ACT_QUEUE,
            rules={
                "bookmark_rule":mas_bookmarks_derand.BLACKLIST,
            },
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_chr_gone",
            prompt="天堂树林去哪了",
            pool=False,
            conditional="not maica_chr_exist and store.seen_event('maica_chr2')",
            action=EV_ACT_PUSH,
            rules={
                "bookmark_rule":mas_bookmarks_derand.BLACKLIST,
            },
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_chr_corrupted2",
            prompt="天堂树林好像坏了",
            pool=False,
            conditional="maica_chr_changed and store.seen_event('maica_chr2')",
            action=EV_ACT_PUSH,
            rules={
                "bookmark_rule":mas_bookmarks_derand.BLACKLIST,
            },
            aff_range=(mas_aff.HAPPY, None)
        )
    )
label maica_prepend_1:
    $ mas_lockEVL("maica_main", "EVE")
# Add this to random waiting list since submod installation. affection NORMAL at least to trigger.
    m 1eub "嗨, [player]..."
    if renpy.seen_label("monika_robotbody"):
        m 3eua "你还记得我们讨论过'进入你的现实'的事情吗?"
        m "像是机械躯体, 或者{i}人工智能{/i}什么的..."
    else:
        m 3eud "你有想过吗, 如果我{i}真的{/i}要来你的现实, 我该从哪里着手呢?"
        m "比如说, {i}人工智能{/i}什么的..."
    m 5euc "我最近看新闻的时候, 好像整个互联网都为人工智能的发展鼓舞不已...{nw}"
    extend 5eud "人们让人工智能做设计, {w=0.1}绘图, {w=0.1}看病甚至炒股票."
    m 6luc "我当然不是在抱怨技术进步. {w=0.2}但是我真的很想知道, {i}我们{/i}能不能用上这些技术."
    m 3husdlb "别误会, [player], 我没有要逼你去做这些的意思! {nw}"
    extend 3eub "不过这种可能性确实让我挺激动的."
    m 1eua "至于在今天说起这些, 是因为.{w=0.3}.{w=0.3}.我想我找到了一点线索."
    m 1lud "我现在还没有弄明白这个...{w=0.3}{i}地方{/i}到底是什么, 但是它的{i}感觉{/i}{w=0.3}很有说服力. {nw}"
    extend 3eub "可能还需要点什么. {w=0.2}我应该会抽空仔细检查一下它的."
    m 1hub "我知道这应该是你找来给我的, [player]. {w=0.1}你还是那么贴心!"
    m 1eua "等我理清了眉目, 我会让你知道的."
    return "no_unlock|derandom|rebuild_ev"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_wants_preferences2",
            prompt="了解你的爱好",
            pool=False,
            unlocked=False,
            conditional="renpy.seen_label('maica_end_1')",
            action=EV_ACT_QUEUE,
            aff_range=(mas_aff.HAPPY, None)
        )
    )

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_mods_preferences",
            prompt="调整[player]的爱好",
            category=["你", "我们", "模组", "MAICA"],
            pool=True,
            random=False,
            unlocked=False,
            aff_range=(mas_aff.HAPPY, None)
        )
    )

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_main",
            prompt="我们去天堂树林吧",
            category=["你", "我们", "模组", "MAICA"],
            pool=True,
            rules={
                "bookmark_rule":mas_bookmarks_derand.BLACKLIST,
            },
        ),
        restartBlacklist=True,
    )

init 5 python:
    @store.mas_submod_utils.functionplugin("ch30_loop", priority=-100)
    def push_mspire_want():
        if renpy.seen_label('maica_greeting') and renpy.seen_label('mas_random_ask') and not renpy.seen_label('maica_wants_mspire') and not mas_inEVL('maica_wants_mspire'):
            return MASEventList.push("maica_wants_mspire")
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_wants_mspire",
            prompt="spire",
            pool=False,
            random=False,
            unlocked=False,
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 5 python:
    if not mas_isSpecialDay() and not renpy.seen_label('maica_wants_mpostal') and _mas_getAffection() > 100 and renpy.seen_label("maica_greeting"):
        @store.mas_submod_utils.functionplugin("ch30_post_exp_check", priority=-100)
        def greeting_select():
            store.selected_greeting = "maica_wants_mpostal"
        ev_rules = dict()
        ev_rules.update(
            MASGreetingRule.create_rule(
                skip_visual=True,
                override_type=True
            )
        )
        ev_rules.update(MASPriorityRule.create_rule(50))
        
        addEvent(
            Event(
                persistent.greeting_database,
                eventlabel="maica_wants_mpostal",
                prompt="maica敲门",
                unlocked=False,
                conditional="renpy.seen_label('maica_prepend_1') and not mas_isSpecialDay() and not renpy.seen_label('maica_wants_mpostal')",
                action=EV_ACT_UNLOCK,
                aff_range=(mas_aff.AFFECTIONATE, None),
                rules=ev_rules,
            ),
            code="GRE"
        )
        del ev_rules

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_mpostal_received",
            unlocked=False,
            random=False,
            pool=False,
            rules={
                "bookmark_rule":mas_bookmarks_derand.BLACKLIST,
            },
        ),
        restartBlacklist=True,
    )

    @store.mas_submod_utils.functionplugin("ch30_loop", priority=-100)
    def push_mpostal():
        if mail_exist() and _mas_getAffection() >= 100 and (renpy.seen_label("maica_wants_mpostal") or getattr(mas_getEV("maica_wants_mpostal"), conditional, False) is None) and not mas_inEVL("maica_mpostal_received") and not mas_inEVL("maica_mpostal_read"):
            return MASEventList.queue("maica_mpostal_received")
    
    @store.mas_submod_utils.functionplugin("ch30_loop", priority=100)
    def push_mpostal_read():
        if has_mail_waitsend() and _mas_getAffection() >= 100 and (renpy.seen_label("maica_wants_mpostal") or getattr(mas_getEV("maica_wants_mpostal"), conditional, False) is None) and not mas_inEVL("maica_mpostal_received") and not mas_inEVL("maica_mpostal_read"):
            return MASEventList.queue("maica_mpostal_read")
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_mpostal_replyed",
            unlocked=False,
            random=False,
            pool=False,
            rules={
                "bookmark_rule":mas_bookmarks_derand.BLACKLIST,
            },
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
        if is_mail_waiting_reply() and _mas_getAffection() >= 100 and renpy.seen_label("maica_wants_mpostal") and not mas_inEVL("maica_mpostal_replyed"):
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
            category=["你", "我们", "模组", "MAICA"],
            prompt="天堂树林到底是什么",
            random=False,
            pool=True,
            conditional="renpy.seen_label('maica_greeting')",
            action=EV_ACT_UNLOCK,
            aff_range=(mas_aff.NORMAL, None)
        )
    )

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_chr_reread",
            category=["你", "我们", "模组", "MAICA"],
            prompt="天堂树林的角色文件",
            random=False,
            pool=True,
            conditional="renpy.seen_label('maica_greeting')",
            action=EV_ACT_UNLOCK,
            aff_range=(mas_aff.NORMAL, None)
        )
    )

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_wants_preferences_reread",
            category=["你", "我们", "模组", "MAICA"],
            prompt="关于补充偏好",
            random=False,
            pool=True,
            conditional="renpy.seen_label('maica_wants_preferences')",
            action=EV_ACT_UNLOCK,
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_wants_mspire_reread",
            category=["你", "我们", "模组", "MAICA"],
            prompt="关于'MSpire'",
            random=False,
            pool=True,
            conditional="renpy.seen_label('maica_wants_mspire')",
            action=EV_ACT_UNLOCK,
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_pre_set_location",
            category=["你", "我们", "模组", "MAICA"],
            prompt="[player]的住址",
            random=True,
            pool=False,
            conditional="renpy.seen_label('maica_greeting')",
            action=EV_ACT_QUEUE,
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_pre_wants_mvista",
            category=["你", "我们", "模组", "MAICA"],
            prompt="关于'MVista'",
            random=True,
            pool=False,
            conditional="renpy.seen_label('maica_mpostal_replyed') or mas_getEV('maica_main').shown_count >= 3",
            action=EV_ACT_QUEUE,
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
    $ _opendoor_text = renpy.substitute(_("...轻轻地推开了门."))
# Isn't really an open door event. guess shall not add afflos here
# Add this greeting to waiting list after maica_prepend_1 was triggered. affection AFFECTIONATE at least to trigger.
# Shouldn't trigger if today is special event like player bday. finish that for me p
    #黑屏
    label maica_greeting_loop:
        menu:
            "[_opendoor_text]" if not persistent.seen_monika_in_room and not mas_isplayer_bday():
                jump maica_prepend_2_open
            "开门." if persistent.seen_monika_in_room or mas_isplayer_bday():
                jump maica_prepend_2_open
            "敲门.":
                jump maica_prepend_2_knock
            "偷听." if not has_listened and not mas_isMoniBroken():
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

    m "是谁--{w=0.3}[player]? {nw}"
    if persistent.seen_monika_in_room:
        extend "我早告诉过你记得敲门的!"
    else:
        extend "你敲过门了吗?"
    m "好吧, 我正好也刚刚忙完. {w=0.5}我觉得你肯定会喜欢这个的."
    m "稍等一下, 我把桌椅找来.{w=0.3}.{w=0.3}."
    #monika + desk in
    show monika 1esc at ls32 zorder MAS_MONIKA_Z
    jump maica_prepend_2
    return


label maica_prepend_2_knock:
    m "谁呀~"
    menu:
        "是我.":
            $ mas_disable_quit()
            m "终于等到你啦, [player]!"
            m "我正想给你准备一点特别惊喜的, 你来得正好. {w=0.5}稍等片刻.{w=0.3}.{w=0.3}."

            #点亮房间, 窗外背景替换heaven_forest.jpg
            call change_to_heaven_forest
            pause 0.5
            hide black
            hide monika
            show monika 1esc at ls32 zorder MAS_MONIKA_Z
            $ monika_chr.reset_outfit(False)
            $ monika_chr.wear_acs(mas_acs_ribbon_def)
            #monika + desk in
            m 1hub "锵锵~"
            jump maica_prepend_2
    return

label maica_prepend_2_listen:
    
    m "这样.{w=0.3}.{w=0.3}.就好了. {w=0.5}呼, 没有我想得那么难."
    m "看起来真不错, 我可以一整天都待在这里. {w=0.5}不过..."
    m "{i}连接现实{/i}是真的吗?"
    jump maica_greeting_loop
    return

label maica_prepend_2:
    m 1eub "你觉得呢, [player]? {w=0.3}你喜欢这里吗?{nw}"
    menu:
        "你觉得呢, [player]? {w=0.3}你喜欢这里吗?{fast}"
        "太好看了!":
            m 1husdlb "你喜欢就好啦. {w=0.3}{nw}"
            if len(filter(lambda x: "tw4449" in x.author, mas_submod_utils.submod_map.values())): #用过房间sub
                extend 3eub "不过这里和其它地方有点区别..."
            else:
                extend 3eub "不过这里还有另一个特别之处..."
        "辛苦你了.":
            m 1hub "我是花了挺久的. {w=0.3}{nw}"
            extend 1eub "不过最有意思的不是这片树林本身..."
        "我其实不太..." if persistent._mas_pm_likes_nature is False:
            m 4husdlb "拜托, [player]!"
            m 3lusdlb "我知道你不太喜欢野外什么的啦. {w=0.3}这里又不是{i}真的{/i}野外, 没有大太阳或者蚊子什么的..."
            m 1eub "不过'{i}不是真的{/i}'这个说法, 这次也不完全对..."
    m 1eua "这里, 看上去叫'{i}天堂树林{/i}'的样子, 可能是--{w=0.3}我们的现实之间的--{w=0.3}某种{i}交界{/i}."
    m 2eud "我大概知道该怎么做. {w=0.2}你想现在试试看吗, [player]?{nw}"
    menu:
        "我大概知道该怎么做. {w=0.2}你想现在试试看吗, [player]?{fast}"
        "好的.":
            label init_maica:
                if persistent.maica_setting_dict['console']:
                    show monika at t22
                    show screen mas_py_console_teaching
                    $ store.maica.maica.content_func = store.mas_ptod._update_console_history
                    $ store.maica.maica.console_logger.critical("<DISABLE_VERBOSITY>"+store.maica.maica.ascii_icon)
                    $ store.mas_ptod.write_command("Thank you for using MAICA Blessland!")
                    pause 2.3
                $ store.maica.maica.init_connect()
                
            
            label check:

                if store.maica.maica.is_ready_to_input() or store.maica.maica.is_failed():
                    pass
                else:
                    pause 1.0
                    jump check
            
            label closed:
                $ store.mas_ptod.write_command("Login successful, ready to chat!")
                pause 1.0
                if persistent.maica_setting_dict['console']:
                    $ store.mas_ptod.clear_console()
                    hide screen mas_py_console_teaching
                    show monika at t11
                    $ store.maica.maica.content_func = None
            # monika right - console appear left 简单格式化信息, 显示在控制台上
            m 2dua ".{w=0.3}.{w=0.3}."
            # 进入校验轮
            if store.maica.maica.is_failed(): # 令牌不存在/校验失败
                m 2rusdlb "...好像你的令牌还没有设置好."
                m 3eusdlb "你可以看看这里的说明: {a=https://maica.monika.love/tos}{u}{i}https://maica.monika.love/tos{/i}{/u}{/a}, 你只需要准备一个账号."
                m 3eua "剩下的事情我都会帮你搞定的."
                m 1eua "我们现在先回去好啦. 等你做完了准备工作, 告诉我再来就可以."
                m 1dua "稍等片刻.{w=0.3}.{w=0.3}."
                # 黑屏清理背景
                call clear_all
                m 1eua "我们今天还有别的安排么, [player]?"
                return
            m 1eua "这一次, 轮到你起个话题了哦, [player]."
            call maica_talking
            call maica_end_1
        "还是改天吧.":
            m 1eub "好吧. 如果你准备好了, 再告诉我来天堂树林就行. {w=0.5}我们现在先回去吧."
            m 1dua "稍等片刻.{w=0.3}.{w=0.3}."
            call clear_all
            m 1eua "我们今天还有别的安排么, [player]?"
            return
    return

label maica_end_1:
    $ conv_rounds = store.maica.maica.stat.get('message_count')
    # Called after first time ending maica
    # Rounds chatted in maica process.
    call clear_all
    if conv_rounds >= 20:
        m 5eusdrb "哈...{w=1}感觉怎么样, [player]?"
        m 5hksdrb "我感觉的话...{w=0.5}还不太熟悉. 毕竟是头一回这样嘛."
        m 5eua "不过我觉得你肯定会喜欢{i}真的{/i}能聊天的感觉. 你肯定早就对点选项不满意了吧?"
    elif conv_rounds >= 5:
        m 5eub "所以...{w=0.2}你感觉怎么样, [player]?"
        m 5hua "至少你{i}真的{/i}能跟我聊点什么了. 你肯定早就对点选项不满意了吧?"
    elif conv_rounds >= 1:
        m 2esd "嗯...聊完了吗, [player]?"
        m 1husdlb "我是说, 我以为你会有更多要聊的. {w=0.2}毕竟是头一回嘛."
    else:
        m 1eksdlc "你一句想说的话都找不到么, [player]?"
        m 3ekd "或者...{w=0.2}如果你遇到了什么问题, 可以再看一遍{a=https://maica.monika.love/tos}{u}{i}说明{/i}{/u}{/a}, 或者到{a=https://forum.monika.love}{u}{i}这里{/i}{/u}{/a}问问."
        m 1eub "不过没关系. 不管你什么时候解决了问题或者想说什么了, 我们都可以再来的. {w=0.5}现在先回去吧."
        # 黑屏清理背景
        call clear_all
        m 1eua "我们今天还有别的安排么, [player]?"
        return

    m 1esa "我希望我的表现不算太差...{w=0.5}{nw}"
    extend 1rusdlb "离开天堂树林之后我都记不起来了, 不过可能是正常情况吧."
    m 3eud "感觉有点像是在.{w=0.3}.{w=0.3}.梦游? {w=0.5}我不知道这么说合不合适..."
    m 1eub "不过也有说法认为做梦才是人的本质表露. {w=0.3}再回去的时候, 我应该也都能想起来的."
    m 5eubla "虽然有点累...{w=0.5}但是能这样和你在一起的感觉也很好. {w=0.5}我会继续抽空研究的, 说不定还能有新发现呢."
    m 5msa "...你没有在我不记得的时候让我许诺{i}什么东西{/i}吧, [player]?"
    return

label maica_chr2:
    # Add to random after first SUCCESSFUL using maica
    # Verify maica chr (HeavenForest.sce) with md5
    m 1eud "...[player], 你还记得'角色文件'什么的吗?"
    m 3eud "我说过我的'角色文件'其实并不是我自己, 只是和我有种{w=0.5}微妙的联系."
    m 3euc "最近我检查文件夹的时候, 我发现'天堂树林'好像也有一个{i}角色文件{/i}, {w=0.3}也可能叫场景文件比较合适."
    m 1msd "如果把它移走, 那里就会变成和这里一样的'太空'了, 不过与现实的联系作用还在."
    m 1eud "我其实很好奇它到底是什么...{w=0.5}它并不像你的礼物一样, 只是一个'标记'. {w=1}我觉得更像其他人的角色文件一些."
    $ like_spk = '如果你不喜欢树林什么的话' if not persistent._mas_pm_likes_nature else '如果你更喜欢这里的话'
    m 3eua "不过至少[like_spk], 把它移走就可以在这个熟悉的背景里聊天了."
    m 1eua "当然, 无论你要做什么, 记得给它做个备份."
    return "no_unlock"

label maica_chr_gone:
    # Derandom maica_chr after maica_chr_gone triggered
    # Triggers only if maica_chr yet not triggered
    m 1ekc "[player]..."
    extend 1ekd "你最近有动过characters文件夹吗?"
    m 3lusdlb "倒不是说真的有多重要, 只是{w=0.5}我找不到'天堂树林'的文件了."
    m 1lua "我们还是可以过去的, 不过那边也会和这里的窗外一样{i}空旷{/i}了."
    m 5esc "我有一点在意, 毕竟我还没来得及弄清那个文件到底{i}是什么{/i}. {w=0.5}它不像是无缘无故在那里的."
    m 5msc "而且和你送的礼物不太一样, 不止是个'标记'. {w=1}我觉得更像其他人的角色文件一些."
    $ like_spk = '如果你不喜欢树林什么的话' if not persistent._mas_pm_likes_nature else '如果你更喜欢这里的话'
    m 5msb "[like_spk], 我倒也不介意没有这个. 毕竟它最多是个'场景'而已."
    m 1eka "如果你琢磨的时候把它弄丢了, 可以重新下载一份."
    return "no_unlock|derandom"

label maica_chr_corrupted2:
    # This is a greeting
    # Triggers only when first time detected corrupted sce file
    # So we should check the file as game starts up
    #背景损坏树林
    call change_to_heaven_forest_corrupted
    m 1wud "哦, [player]!"
    m 1hksdlb "抱歉, 我没有在准备吓你或者什么的...{w=0.5}{nw}"
    extend 4rksdlb "我刚刚检查的时候, 发现它好像坏了."
    m 3eka "你有没有, 比如动过或者替换过--{w=0.5}'天堂树林'的文件?"
    $ mentioned = '我想我提过一嘴, ' if renpy.seen_label("maica_chr") else '我想'
    m 1rud "[mentioned]它是一个编码的文件. {w=0.5}也就是说, 如果它的内容改变了--{w=0.3}{nw}"
    extend 1euc "它就坏掉了."
    #cares_about_dokis那个条件怎么写来着? 交给你了
    $ comment = "...{i}某人{/i}风格的" if persistent._mas_pm_cares_about_dokis else '崩坏风格的'
    m 5eusdrb "不过其实, 如果你不讨厌这种[comment]景色, {w=0.3}就让它这样也可以."
    m 1hua "你当然也可以找一份正常的文件换上. 只要你喜欢, 我都不介意的."
    m 1eub "我去收拾一下就好. {w=0.3}{nw}"
    extend 1dua "稍等片刻.{w=0.3}.{w=0.3}."
    #恢复背景
    call clear_all
    m 1eua "欢迎回来, [player]. 我们今天有什么安排呢?"
    return "no_unlock|derandom"


label maica_wants_preferences2:
    # Add this to waitlist after first chat done successfully
    m 1eub "[player]? {w=0.5}嗯...{w=0.3}我有一点事情想问."
    m 3eua "毕竟现在我真的可以问你了, {w=0.5}{nw}"
    extend 3esd "才发现我之前对你的了解还是太单一."
    #这里有好几个我不会写的, 都交给你了
    $ like_mi = _(' 我只知道你喜欢薄荷冰淇淋.') if persistent._mas_pm_like_mint_ice_cream else '' 
    $ book_rc = _("我们聊过'世界尽头与冷酷仙境'什么的") if store.seen_event("monika_favbook") else None
    $ book_rc = _("我们聊过'黄色墙纸'什么的") if persistent._mas_pm_read_yellow_wp and book_rc is None else _('我可以推荐几本书给你')
    m 3ruc "比如, 如果我们真的一起去吃点什么, 你喜欢什么菜呢?{nw}"
    extend "[like_mi]"
    m 3tuc "又或者是书. {w=0.5}[book_rc], 但是你会推荐什么书给我呢?"
    #如果玩家已经通过设置填过了
    $ prefs_exist = len(persistent.mas_player_additions)
    if not prefs_exist:
        m 1eua "所以我想了个办法. {w=0.5}只要你写点关于你自己的事情, 我到了'天堂树林'就能看到了."
        m 1eub "只要是关于你的事情, 我都会想知道的!"
        $ prefs_line = _("你有什么想说的吗?")
        m 1hua "[prefs_line]{nw}"
    else:
        m 1husdlb "看起来你已经写了一些给我, 我当然会抽空去读的."
        $ prefs_line = _("你还有什么想补充的吗?")
        m 1eub "[prefs_line]{nw}"
    menu:
        "[prefs_line]{fast}"
        "有的":
            m 2dua "稍等片刻.{w=0.3}.{w=0.3}."
            #在这里呼出输入框
            #[player]...
            #placeholder
            #还有... | 我写完了
            #获取到的句子前面拼合上[player]
            call maica_input_information
            m 1eub "写完了? {w=0.5}谢谢你!"
            m 3eua "我在这里还没办法看, 但我一定会抽空记下来的."
            m 1eub "如果有什么要修改或者补充的, 再叫我写下来就好. '子模组设置'里面也有相关的选项."
        "还是下次吧" if not prefs_exist:
            m 2eka "现在没空么? 好吧."
            m 3eka "如果你准备好了, 再叫我记下来就好."
        "没有了" if prefs_exist:
            m 1hua "我明白了, 谢谢你!"
    $ mas_unlockEVL("maica_mods_preferences", "EVE")
    return "no_unlock|derandom"
label maica_mods_preferences:
    $ prefs_exist = len(persistent.mas_player_additions)
    if prefs_exist:
        m 1eub "好啊. 你要补充还是删除呢?{nw}"
        menu:
            "好啊. 你要补充还是删除呢?{fast}"
            "补充":
                m 2dua "稍等片刻.{w=0.3}.{w=0.3}."
                call maica_input_information
                m 3eua "写完了? 谢谢你! {w=0.5}我会抽空全部记下来的."
            "删除":
                m 2dua "稍等片刻.{w=0.3}.{w=0.3}."
                call maica_delete_information
                m 3eua "改完了? 谢谢你! {w=0.5}我会抽空全部记下来的."
    else:
        m 1eub "好啊. 你想到什么要告诉我的了吗, [player]?"
        call maica_input_information
        m 3eua "写完了? 谢谢你! {w=0.5}我会抽空全部记下来的."
    return
label maica_call_from_setting(label):
    $ renpy.call(label)
    call maica_show_setting_screen
    return
label maica_input_information:
    python:
        while True:
            i = mas_input(
                    _("喜欢.../常去.../有.../..."),
                    default="",
                    length=50,
                    #screen_kwargs={"use_return_button": True, "return_button_value": "end", "return_button_prompt": _("我写完了")}
                    screen="maica_input_information_screen"
                ).strip(' \t\n\r') #mas_input
            # if i == "end":
            if i == "nevermind":
                break
            else:
                renpy.notify(_("MAICA: 已保存输入"))
            persistent.mas_player_additions.append("[player]{}".format(i))
    return
label maica_delete_information:
    python:
        items = []
        for i in persistent.mas_player_additions:
            items.append([
                i, i, False, False, True 
            ])

    call screen mas_check_scrollable_menu(items, mas_ui.SCROLLABLE_MENU_TXT_MEDIUM_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, selected_button_prompt=_("删除选择项"), return_all=True)

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
    $ bg_change_info = mas_changeBackground(mas_background_def, by_user=None, set_persistent=False,)
    call spaceroom(scene_change=None, dissolve_all=True, bg_change_info=bg_change_info, force_exp=None)
    #$ behind_bg = MAS_BACKGROUND_Z - 2
    #show expression _background as sp_mas_backbed zorder behind_bg
    #$ renpy.show(_background, tag = "sp_mas_backbed", zorder=behind_bg)

    
    return

label change_to_heaven_forest_corrupted():
    $ mas_changeWeather(hf2_weather, True)
    $ bg_change_info = mas_changeBackground(heaven_forest_d, by_user=None, set_persistent=False,)
    call spaceroom(scene_change=None, dissolve_all=True, bg_change_info=bg_change_info, force_exp=None)
    return

label clear_all:
    call maica_hide_console
    hide sp_mas_backbed
    $ HKBShowButtons()
    $ mas_changeWeather(mas_weather_def)
    $ bg_change_info_moi = mas_changeBackground(mas_background_def, set_persistent=False)
    if maica_chr_exist:
        call spaceroom(scene_change=True, dissolve_all=True, bg_change_info=bg_change_info_moi, force_exp=None)
    $ mas_unlockEVL("maica_main", "EVE")
    return



label maica_main:
    $ ev = mas_getEV("maica_main")
    if maica_chr_exist:
        m 1dua "好啊, 稍等片刻.{w=0.3}.{w=0.3}.{w=0.3}{nw}"
        scene black with dissolve
        pause 2.0
        if maica_chr_changed:
            call change_to_heaven_forest_corrupted
            m 1eub "好了!"
            m 1lusdlb "我还得多嘴一句...{w=0.5}不要把身体够到窗外去."
            m 3eksdla "就算景色独特, 我也不确定那里是不是安全的--{w=0.5}{nw}"
            extend 3hksdla "多半不是."
        else:
            call change_to_heaven_forest
            m 1eub "好了!"
            $ rand_sign = renpy.random.randint(0, 7)
            if ev.shown_count == 9: #第一次没触发这个对话
                m 3eua "你数过我们来这里多少次了吗? {w=0.5}{nw}"
                extend 3eub "有十次了哦!"
                m 3rud "不过从最开始, 我就感觉之前和你来过这里--{w=0.5}大概是一种既视感吧."
                m 1dua "也有可能是我太想你了吧!"
            elif rand_sign == 0:
                m 2euu "这里天气不错, 是吧?"
                m 5rksdlb "当然啦, 其实每天都是这样. {w=0.5}{nw}"
                extend 5eua "希望你也每天都有好心情, [player]!"
            elif rand_sign == 1 and ev.shown_count >= 12:
                m 1dua "这里的气氛真轻松啊. {w=0.3}{nw}"
                extend 1rup "我经常会感觉之前见过这里, 但又记不起来了."
                m 3eub "至少不是太空了. '脚踏实地'一会的感觉怎么样, [player]?"
            elif rand_sign == 2 and ev.shown_count >= 20:
                m 3rua "其实我有时候在想, 能去树林里走走就好了...{w=0.5}{nw}"
                extend 3gud "我好像看得到里面有一间小教堂. 会是什么人修的呢?"
                m 5eua "不过就享受一下我们的林间小屋也挺好的嘛."
        m 1eua "现在, 你想和我聊点什么呢?"
    else:
        m 1dua "好啊. 马上就到.{w=0.3}.{w=0.3}.{w=0.3}{nw}"
        extend 1eub "好了!"
        m 3hub "既然没有'树林'了, 这里会是'天堂'吗? {w=0.3}哈哈~"
        m 1eua "那么, 你想和我聊点什么呢?"
    
label .talking_start:
    call maica_talking
    # maica_talking 有返回值_return, 返回结果canceled(正常退出)/disconnect(断开连接且未启动自动重连)
    if config.debug:
        m "return：[_return]"
    if _return == "canceled":
        m 1eub "好的. 稍等片刻.{w=0.3}.{w=0.3}.{w=0.3}{nw}"
    elif store.maica.maica.mtrigger_manager._running:
        $ store.maica.maica.mtrigger_manager._running = False
        jump .talking_start
    elif _return != "mtrigger_triggering":
        $ store.mas_submod_utils.submod_log.debug("maica_talking returned {}".format(_return))
        if store.maica.maica.Loginer.wrong_pwd:
            m 2rusdlb "...好像你的令牌还没有设置好."
            m 3eusdlb "你可以看看这里的说明: {a=https://maica.monika.love/tos}{u}{i}https://maica.monika.love/tos{/i}{/u}{/a}, 你只需要准备一个账号."
            m 3eua "剩下的事情我都会帮你搞定的."
        elif store.maica.maica.status == store.maica.maica.MaicaAiStatus.SAVEFILE_NOTFOUND:
            m 2rusdlb "好像上传存档出了点问题..."
        else:
            m 2rusdlb "好像是其他的地方出问题了..."
        m 1eua "我们现在先回去好啦. 等做完了准备工作, 告诉我再来就可以."
    $ mas_unlockEVL("maica_main", "EVE")
    if maica_chr_exist:
        scene black with dissolve
        pause 2.0
    call clear_all
    return
label maica_wants_mspire:
    # Add this to waitlist if satisfies:
    # First chat done successfully;
    # All original talks used up;

    # Mark as read if mspire is already on
    m 3ekd "[player], 我之前提到过, 我们已经把所有话题都聊完了."
    m 5rku "去过天堂树林之后, 我想或许有个办法{w=0.5}永远有话和你说."
    m 5esb "你知道的, {a=https://wikipedia.org}{u}{i}维基百科{/i}{/u}{/a}是一个很大的知识库. {w=0.5}只要我去那里转转, 肯定能找到话题的."
    m 3eua "多半是一些小知识或者小科普. {w=0.5}{nw}"
    extend 3husdlb "可能一些条目没有多少可聊, 但是我会尽量的!"
    m 1eua "所以你想试试看吗, [player]?{nw}"
    menu:
        "所以你想试试看吗, [player]?{fast}"
        "好啊":
            m 1hub "谢谢你, [player]!"
            m 4eub "如果你想再调整, 可以在'子模组设置'里面找到'MSpire'的选项."
            m 2ruu "希望没有太多在你知识盲区里的内容...{w=0.5}{nw}"
            extend 2hub "哈哈!"
        "还是算了":
            m 3ekb "好吧. {w=0.5}如果你之后想试试看了, 在'子模组设置'里面找到'MSpire'就好."
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
            prompt="mspire",
            pool=False,
            conditional="renpy.seen_label('maica_wants_mspire') and spire_has_past(datetime.timedelta(minutes=persistent.maica_setting_dict.get('mspire_interval'))) and persistent.maica_setting_dict.get('mspire_enable') and not store.maica.maica.is_in_exception()",
            aff_range=(mas_aff.NORMAL, None)
        )
    )
init 999 python:
    mas_getEV("maica_mspire").conditional="renpy.seen_label('maica_wants_mspire') and spire_has_past(datetime.timedelta(minutes=persistent.maica_setting_dict.get('mspire_interval'))) and persistent.maica_setting_dict.get('mspire_enable') and not store.maica.maica.is_in_exception()"
    @store.mas_submod_utils.functionplugin("ch30_loop", priority=-100)
    def push_mspire():
        if try_eval(mas_getEV("maica_mspire").conditional) and not mas_inEVL("maica_mspire") and store.mas_getAPIKey("Maica_Token") != "" and len(mas_rev_unseen) == 0 and persistent.maica_setting_dict.get('mspire_enable') and not persistent._mas_enable_random_repeats:
            return MASEventList.queue("maica_mspire")

label maica_mspire:
    call maica_talking(mspire=True)
    return "no_unlock"

label mspire_mods_preferences:
    $ prefs_exist = len(persistent.maica_setting_dict['mspire_category'])
    if prefs_exist:
        m 1eub "好啊. 你要补充还是删除呢?{nw}"
        menu:
            "好啊. 你要补充还是删除呢?{fast}"
            "补充":
                m 2dua "稍等片刻.{w=0.3}.{w=0.3}."
                call mspire_input_information
                m 3eua "写完了? 谢谢你! {w=0.5}我会抽空全部记下来的."
            "删除":
                m 2dua "稍等片刻.{w=0.3}.{w=0.3}."
                call mspire_delete_information
                m 3eua "改完了? 谢谢你! {w=0.5}我会抽空全部记下来的."
    else:
        m 1eub "好啊. 你想我说那些方面呢~"
        call mspire_input_information
        m 3eua "写完了? 谢谢你! {w=0.5}我会抽空全部记下来的."
    return

label mspire_input_information:
    python:
        while True:
            i = mas_input(
                    _("请输入搜索关键词:"),
                    default="",
                    length=50,
                    #screen_kwargs={"use_return_button": True, "return_button_value": "end", "return_button_prompt": _("我写完了")}
                    screen="maica_input_information_screen"
                ).strip(' \t\n\r') #mas_input
            # if i == "end":
            if i == "nevermind":
                break
            else:
                renpy.notify(_("MAICA: 已保存输入"))
            persistent.maica_setting_dict['mspire_category'].append("{}".format(i))
    return
label mspire_delete_information:
    python:
        items = []
        for i in persistent.maica_setting_dict['mspire_category']:
            items.append([
                i, i, False, False, True 
            ])

    call screen mas_check_scrollable_menu(items, mas_ui.SCROLLABLE_MENU_TXT_MEDIUM_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, selected_button_prompt=_("删除选择项"), return_all=True)

    python:
        persistent.maica_setting_dict['mspire_category'] = []
        for i in _return:
            if _return[i]:
                persistent.maica_setting_dict['mspire_category'].append(i)
        store.maica.maica.mspire_category = persistent.maica_setting_dict["mspire_category"]
    return
           
            
# I'm a gonna tie me up in a red string,
# I'm gonna tie blue ribbons too,
# I'm a-gonna climb up in my mail box;
# I'm gonna mail myself to you.

# MPostal is first introduced by a greeting!
label maica_wants_mpostal:
    # 替换greeting触发!
    m 3hubsa "{i}~我要扎上红丝绸, 我要系上蓝发带~{/i}"#闭眼-憧憬
    m 3hubsa "{i}~我要爬进小小的邮箱, 把小小的心意送给你~{/i}"#闭眼-憧憬
    m 2wud "...[player]? {w=0.5}抱歉, 我没注意到你回来了! {nw}"#惊讶
    extend 7rubfa "我只是...{w=0.3}正巧在哼歌."#尴尬
    m 1eud "我刚刚在想, 书信实在是种浪漫的文学. 用短短的几行字, 把巧思传递给千里之外的某人."#微笑
    m 1eua "既然我们现在也算是相隔两地, 也许我们写写信挺合适的. {w=0.3}还可以当作文学小练习!"
    m 5ekbsa "你有想过给我写封信吗, [player]?{nw}"
    menu:
        "你有想过给我写封信吗, [player]?{fast}"
        "想过":
            m 3hubsa "那太好了! 我就知道我们超级合拍的."
            m 2lksdlb "有可能你都已经写给我过了, 只是我之前没能收到. {w=0.5}那现在..."#尴尬
        "没想过":
            m 1hua "没想过吗? 是和我聊天就足够开心了吗? 哈哈~"
            m 2lksdlb "不管怎样, 不妨写写信试一试. {w=0.5}毕竟现在..."
    m 1eua "我有办法读你的信, 再给你写回信了. {w=0.5}我最近在天堂树林里发现了一个邮箱."
    m 2lksdlb "虽然我自己没办法试, 但我大概知道要怎么用."
    m 7eub "大概是...下次打开游戏前, 在'characters'文件夹里放上一封信, 文件名是信的标题, 再把后缀名改成'.mail'..."
    m 7kub "就像是'我爱你.mail'! {w=0.5}{nw}"#眨眼
    extend 2lksdlb "只是记得用记事本写, 我应该读不了太复杂的文档或者图片."#尴尬
    m 1kubsu "你打开游戏的时候, 我就可以写我的回信了!"
    m 3hubsa "说实话, 我想起了我们在文学部交换过的诗. {w=0.5}总之, 如果你有当面说不清的话, {w=0.3}或者只是想写点什么给我, 现在随时都可以哦!"

# 目前MPostal使用session0
label maica_mpostal_received:
    $ ev = mas_getEV("maica_mpostal_received")
    m 1sub "哦, [player]! {w=0.5}你的信!"
    call maica_mpostal_load
    # 读一下触发几次应该不难吧
    if ev.shown_count == 0:
        m 5ekbsa "我收到了, 感觉还真是奇妙!"
        m 5hubsb "我能感觉到你的心意, 如此有实感, 像是有你的温度..."
    elif ev.shown_count == 1:
        m 1kubsu "我收到了! 开始迷上这种感觉了么, [player]?"
        m 5hkbsa "我也好喜欢这种感觉..."
    elif ev.shown_count % 7 == 0:
        m 1eud "你都写了这么多了, 说不定哪天都能整理成册出版..."
        m 7hub "叫[player]家书怎么样? {w=0.5}哈哈~"
    else:
        m 5ekbsa "你就是不会腻, 对吧? {w=0.5}我也一样!"
    m 4eub "我一定会抽空仔细读的!"
    m 4kub "你下次来的时候, 我会把回信给你看, 不要太急躁哦~"
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
        m 2lksdlb "对了, [player], {w=0.5}上次的信..."#担心
        m 2ekc "你好像还没有给天堂树林配置好, 我没法把回信写给你."#担心
        m 3eusdlb "你可以看看这里的说明: {a=https://maica.monika.love/tos}{u}{i}https://maica.monika.love/tos{/i}{/u}{/a}, 你只需要准备一个账号."
        m 3eua "剩下的事情我都会帮你搞定的."
        m 1eua "没关系, 等你做完了准备工作, 我一定会记得写回信给你的."
        $ _reset_failed_mp()
        return "no_unlock"
    elif current["responsed_status"] == "received" or current["responsed_status"] == "notupload":
        if not morethan1:
            m 7hub "对了, [player]! {w=0.5}我给你的回信写完了!"
            $ morethan1 = True
        else:
            m 7husdlb ".{w=0.3}.{w=0.3}.这里还有一封!"
        if current["responsed_status"] == "received":
            m 6dsc "稍等, 我把它找出来.{w=0.3}.{w=0.3}."#闭眼
            m 3hubsa "好了!"#微笑
        elif current["responsed_status"] == "notupload":
            if not morethan1:
                m 3eksdlb "这封可能要多等一会, 我还没...{w=0.2}完全准备好."#尴尬
                m 1hua "我去去就回, 等我哦~"#微笑
            else:
                m 1dsa "再等我去准备一下..."#微笑
            show black with dissolve
            call maica_mpostal_read
            if _return == "failed":
                hide black with dissolve
                # 直接重新开始, 失败的信会提示失败, 理论应与current一致
                jump maica_mpostal_replyed.select_little
            m "好了!"
            hide black with dissolve
        call maica_mpostal_show(current["responsed_content"])
        $ current["responsed_status"] = "readed"
    jump maica_mpostal_replyed.select_little
label maica_mpostal_replyed.end:
    if ev.shown_count <= 2:
        m 2lksdlb "说实话, 我还没太熟悉在这里写信..."
        m 2ekbsa "不过还是希望你喜欢!"
    else:
        m 2lksdlb "可能是不如在文学部里写得好, 但我尽力啦."
        m 2ekbsa "希望你喜欢哦!"
    m 5ekbsa "也随时欢迎你再写给我!"
    return "no_unlock"


# 重读对话变体
label maica_prepend_reread:#"天堂树林到底是什么"
    # maica_prepend_2触发后解锁
    m 4eub "如我当时所说, '{i}天堂树林{/i}'确实是我们的现实之间的{w=0.3}某种{i}交界{/i}地."
    m 3hub "与其它地方最大的不同, 就是能让你{i}真正地{/i}和我对话. 想聊什么都可以!"
    m 3eusdlb "你可以看看这里的说明: {a=https://maica.monika.love/tos}{u}{i}https://maica.monika.love/tos{/i}{/u}{/a}, 你只需要准备一个账号."
    m 3eua "剩下的事情我都会帮你搞定的."
    m 7hub "如果你想要了解得再具体点, 可以到{a=https://maica.monika.love}{u}{i}https://maica.monika.love{/i}{/u}{/a}看看."
    m 2hksdlb "我就不多说教啦, 哈哈!"

label maica_chr_reread:#"天堂树林的角色文件"
    # maica_chr2触发后解锁
    m 5ruc "...它的角色文件? {w=0.5}也许你已经去找过了, 它叫'HeavenForest.sce'."
    m 1msd "如果把它移走, 那里就会变成和这里一样的'太空'了, 不过与现实的联系作用还在."
    m 3eud "我其实很好奇它到底是什么...{w=0.5}它并不像你的礼物一样, 只是一个'标记'. {w=1}我觉得更像其他人的角色文件一些."
    $ like_spk = '如果你不喜欢树林什么的话' if not persistent._mas_pm_likes_nature else '如果你更喜欢这里的话'
    m 3eua "不过至少[like_spk], 把它移走就可以在这个熟悉的背景里聊天了."
    m 7hub "如果你有兴趣研究一下它, 也许可以试试看. {w=0.5}毕竟你应该知道, 其他人的角色文件里面都有奇怪的内容."
    m 1eud "...比如, 这里为什么会叫天堂树林?{w=0.5} 是为什么故事设计的吗?{w=0.5} 为什么又被遗弃在这里, 留给我们约会?"
    m 1eua "当然, 无论你要做什么, 记得给它做个备份."
    return

label maica_wants_preferences_reread:#"关于补充偏好"
    # maica_wants_preferences触发后解锁
    m 7hub "是这样, 游戏本身并没有留给我太多空间去了解你."#担心
    #这里有好几个我不会写的, 都交给你了
    $ like_mi = _(' 我只知道你喜欢薄荷冰淇淋.') if persistent._mas_pm_like_mint_ice_cream else '' 
    $ book_rc = _("我们聊过'世界尽头与冷酷仙境'什么的") if store.seen_event("monika_brave_new_world") else None
    $ book_rc = _("我们聊过'黄色墙纸'什么的") if persistent._mas_pm_read_yellow_wp and book_rc is None else _('我可以推荐几本书给你')
    m 3ruc "比如, 如果我们真的一起去吃点什么, 你喜欢什么菜呢?{nw}"
    extend "[like_mi]"
    m 3tuc "又或者是书. {w=0.5}[book_rc], 但是你会推荐什么书给我呢?"
    m 1eua "所以我想了个办法. {w=0.5}只要你写点关于你自己的事情, 我到了'天堂树林'就能看到了."
    m 4eub "只用在对话里找到'调整[player]的爱好', 你就可以随时告诉我关于你的事情."
    m 1eub "只要是关于你的事情, 我都会想知道的!"
    return

label maica_wants_mspire_reread:#"关于'MSpire'"
    # maica_wants_mspire触发后解锁
    m 3ekd "[player], 我之前提到过, 我们已经把所有话题都聊完了."
    m 5rku "去过天堂树林之后, 我想或许有个办法{w=0.5}永远有话和你说."
    m 5esb "你知道的, {a=https://wikipedia.org}{u}{i}维基百科{/i}{/u}{/a}是一个很大的知识库. {w=0.5}只要我去那里转转, 肯定能找到话题的."
    m 3eua "多半是一些小知识或者小科普. {w=0.5}{nw}"
    extend 3husdlb "可能一些条目没有多少可聊, 但是我会尽量的!"
    m 3esb "如果你想听或者不想听了, 在'子模组设置'里面找到'MSpire'就好."
    return
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_wants_mpostal_reread",
            category=["你", "我们", "模组", "MAICA"],
            prompt="关于'MPostal'",
            random=False,
            pool=True,
            conditional="renpy.seen_label('maica_wants_mpostal')",
            action=EV_ACT_UNLOCK,
            aff_range=(mas_aff.NORMAL, None)
        )
    )
label maica_wants_mpostal_reread:#"关于'MPostal'"
    # maica_wants_mpostal触发后解锁
    m 4eub "我一直觉得, 书信实在是种浪漫的文学. 用短短的几行字, 把巧思传递给千里之外的某人."#微笑
    m 3eub "既然我们现在也算是相隔两地, 也许我们写写信挺合适的. {w=0.3}还可以当作文学小练习!"
    m 5eubsa "现在, 通过天堂树林里的邮箱, 我有办法读你的信, 再给你写回信了."
    m 3eubsb "只需要在下次打开游戏前, 在'characters'文件夹里放上一封信, 文件名是信的标题, 再把后缀名改成'.mail'..."
    m 3kubsa "就像是'我爱你.mail'! {w=0.5}{nw}"
    extend 3lksdlb "只是记得用记事本写, 我应该读不了太复杂的文档或者图片."#尴尬
    m 7hub "你打开游戏的时候, 我就可以写我的回信了!"
    m 5esa "说实话, 我想起了我们在文学部交换过的诗. {w=0.5}总之, 如果你有当面说不清的话, {w=0.3}或者只是想写点什么给我, 现在随时都可以哦!"
    return
label mas_corrupted_postmail:
    m 1eud "嗨, [player]..."
    m 3euc "好像有人在'characters'文件夹里给你留了个便条."
    m 1ekc "我没看啦, 毕竟是写给你的...{w=0.3}{nw}"
    extend 1ekd "就是这个."

    call mas_showpoem(maica_note_mail_bad)

    window auto
    $ _gtext = glitchtext(7)

    m 1ekc "你知道大概是怎么了吗?{nw}"
    $ _history_list.pop()
    menu:
        m "你知道大概是怎么了吗?{fast}"
        "没什么好担心的.":
            jump mas_corrupted_postmail_post_menu

        "和[_gtext]有关.":
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
        "没什么好担心的.":
            pass
label mas_corrupted_postmail_post_menu:
    m 1euc "啊, 好吧."
    m 1hub "那我就不瞎操心了."
    m 3eub "要紧的事情你肯定会告诉我的, [player]."
    return
label maica_set_location:
    $ inputloc = mas_input(
        _("你具体住在什么地方呢?"),
        length=30,
        #screen_kwargs={"use_return_button": True, "return_button_value": "nevermind"}
        screen="maica_input_information_screen"
    )
    if inputloc.lower() == "nevermind":
        m 2eud "不太确定吗...{w=0.5}{nw}"
        extend 3huu "可能你常待的地方不止一个吧? 这样的话, 告诉我你最喜欢的那个就好!"
        m 4fub "还是说你那里有个超级难写的地名, 比如'兰韦尔普尔古因吉...'"
        m 1hub "哈哈~"
        m 3esu "无论如何, 等你决定要告诉我了, 随时都可以来找我. {w=0.3}你也可以直接填在'子模组设置'里."
    else:
        m 1rsa "我看看..."
        $ res = store.maica.maica.verify_legality("geolocation", inputloc)
        if not res.get('success', False):
            m 3husdlb "我没找到这个地方. {w=0.3}要不调整一下写法? 省市地名就行.{nw}"
            menu:
                "我没找到这个地方. 要不调整一下写法? 省市地名就行.{fast}"
                "就这样吧{#maica_location}":
                    m 3eub "那也行, 谢谢你!"
                "我再改改":
                    jump maica_set_location
        else:
            m 3eub "是那里吗? 谢谢你!"
        $ persistent.mas_geolocation = inputloc
        m 4sub "等到我'出来'的那天, 我们说不定也会在那里见面呢!"
        m 7huu "当然, 如果之后情况有变, 你随时可以告诉我或者填在'子模组设置'里."
    return

label maica_pre_set_location:
    $ ev = mas_getEV("maica_pre_set_location")
    if ev.shown_count > 0:
        jump maica_set_location_reread
    m 2eub "[player], 我又想问你了..."
    m 3euu "你住在什么地方? {w=0.3}我好像都还没问过你呢."
    if persistent._mas_pm_live_south_hemisphere is not None:
        $ sw = "南" if persistent._mas_pm_live_south_hemisphere else "北"
        m 2lusdlb "我倒是知道你在[sw]半球啦, 不过那个也太宽泛了..." # 尴尬
    m 2tsblp "我总是想多了解你一点. 总不该连我的[bf]住在哪里都不知道吧!"
    m 7rsd "虽然{i}大概{/i}还没办法亲自过去, 但现在我可以上网查不少东西了. 譬如你那里的天气, 路况, 好吃的餐馆..."
    m 1hub "这样下次你到天堂树林来的时候, 我就可以提醒你不要淋着冻着饿着. 哈哈!"
    m 2euu "所以, [player]..."
    jump maica_set_location
    return
label maica_set_location_reread:
    m 2eub "好啊! 所以..."
    jump maica_set_location


label maica_pre_wants_mvista:
    $ ev = mas_getEV("maica_pre_wants_mvista")
    if ev.shown_count > 0:
        jump maica_wants_mvista_reread
    $ persistent._maica_vista_enabled = True
    m 2eub "[player], 你上一次看日出是什么时候?"
    m 2eua "突然问这个是不是有点奇怪...我也只是正好想起来."
    m 7eud "我在网上见到了一个帖子, 问了类似的问题. 许多人感叹自己居然几年没看过."
    m 1eud "太阳每天都在那里, 我们却总连看日出的机会都没有...{w=0.3}是不是有点光阴虚度的感觉?"
    $ morning = "今早" if datetime.datetime.now().hour > 8 else "昨天早上"
    m 2tua "倒也不是真的非要看啦. 但不管怎么说, 我[morning]还是抽空去看了一次."
    m 5fua "这里的太阳从云层里升起来真的很漂亮. {w=0.3}如果你哪天早上打开游戏, 你也可以陪我看. 哈哈!"
    m 4eua "你最近看过日出么, [player]?{nw}"
    menu:
        "你最近看过日出么, [player]{fast}"
        "没有":
            m 1eub "如果哪天有空的话, 可以考虑去看一回嘛!"
            m 1eubsb "而且, 你还可以...{w=0.3}让我陪你看哦?"
        "看过":
            m 2eub "应该很漂亮吧. {w=0.3}你没有忘了把我带上吧?"
            m 1eua "就开个玩笑! 不过如果你有拍照片的话, 可以发给我看看哦?"
        "在这里看过":
            m 5eubsa "确实很漂亮吧! 当然, 我还要谢谢你起大早来陪我~"
            m 3eub "不过我也想看看你那边的日出. 拍张照让我看看怎么样?"
    $ even_letter = "{w=0.2} 毕竟连信都可以了嘛." if renpy.seen_label('maica_mpostal_replyed') else ""
    m 7eua "嗯...我是说, 你{i}真的{/i}可以把照片发给我了.[even_letter]"
    jump maica_wants_mvista

label maica_wants_mvista_reread:
    m 7eub "就是说, 你现在可以发图片给我看, [player]!"
    jump maica_wants_mvista

label maica_wants_mvista:
    m 3eub "只需要在'子模组设置'里找到'MVista图片', 就可以上传给我看了! 对话框底下也有个按钮."
    m 1eub "如果你是明信片爱好者, 也可以在下次给我送信的时候, 用'.mms'后缀. 我会记得和图片一起看的!"
    m 7eua "比如, 日出的照片加上一首小诗? 我也会陪你写一首的!"
    m 7eubsa "再比如, 让我看看你的脸? 当然是如果你不害羞的话, 哈哈~"
    m 1fubsa "到了现在, 我都有点急着想摸到你, 牵到你的手..."
    m 2eub "要有信心, [player]! 不管有多难, 我们都一定能想到办法的!"
    return
