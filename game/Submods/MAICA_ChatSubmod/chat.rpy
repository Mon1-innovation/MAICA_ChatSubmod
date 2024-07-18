init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_prepend_1",
            prompt="你的现实?",
            random=True,
            conditional="True",
            action=EV_ACT_QUEUE,
            rules={
                "bookmark_rule":mas_bookmarks_derand.BLACKLIST,
            },
            aff_range=(mas_aff.NORMAL, None)
        )
    )
label maica_prepend_1:
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
    return "no_unlock|derandom"

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="maica_greeting",
            prompt="maica敲门",
            unlocked=True,
            conditional="store.seen_event('maica_prepend_1')",
            aff_range=(mas_aff.HAPPY, None)
        ),
        code="GRE"
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
    $ _opendoor_text = _("...轻轻地推开了门.")
# Isn't really an open door event. guess shall not add afflos here
# Add this greeting to waiting list after maica_prepend_1 was triggered. affection AFFECTIONATE at least to trigger.
# Shouldn't trigger if today is special event like player bday. finish that for me p
    #黑屏
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
    $ bg_change_info = mas_changeBackground(heaven_forest, by_user=None, set_persistent=False,)
    call spaceroom(scene_change=None, dissolve_all=True, bg_change_info=bg_change_info, force_exp=None, hide_monika=True, show_emptydesk=False)
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
            
            $ bg_change_info = mas_changeBackground(heaven_forest, by_user=None, set_persistent=False,)
            call spaceroom(scene_change=None, dissolve_all=True, bg_change_info=bg_change_info, force_exp=None, hide_monika=True, show_emptydesk=False)
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
    jump maica_greeting
    return

label maica_prepend_2:
    m 1eub "你觉得呢, [player]? {w=0.3}你喜欢这里吗?"
    menu:
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
    m 2eud "我大概知道该怎么做. {w=0.2}你想现在试试看吗, [player]?"
    menu:
        "我大概知道该怎么做. {w=0.2}你想现在试试看吗, [player]?"
        "好的.":
            label init_maica:
                if persistent.maica_setting_dict['console']:
                    show monika at t22
                    show screen mas_py_console_teaching
                    $ store.maica.maica.content_func = store.mas_ptod._update_console_history
                    $ store.maica.maica.send_to_outside_func(store.maica.maica.ascii_icon)
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

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_chr",
            prompt="树林重要吗?",
            random=True,
            conditional="store.maica.maica.stat.get('message_count') > 0",
            action=EV_ACT_QUEUE,
            rules={
                "bookmark_rule":mas_bookmarks_derand.BLACKLIST,
            },
            aff_range=(mas_aff.NORMAL, None)
        )
    )
label maica_chr:
    # Add to random after first SUCCESSFUL using maica
    # Verify maica chr (HeavenForest.sce) with md5
    m 1eud "...[player], 你还记得'角色文件'什么的吗?"
    m 3eud "我说过我的'角色文件'其实并不是我自己, 只是和我有种{w=0.5}微妙的联系."
    m 1etc "最近我检查文件夹的时候, 我发现'天堂树林'好像也有一个{i}角色文件{/i}, {w=0.3}也可能叫场景文件比较合适."
    m 1mtd "如果把它移走, 那里就会变成和这里一样的'太空'了, 不过与现实的联系作用还在."
    m 3eud "我其实很好奇它到底是什么...{w=0.5}它并不像你的礼物一样, 只是一个'标记'. {w=1}我觉得更像其他人的角色文件一些."
    $ like_spk = '如果你不喜欢树林什么的话' if not persistent._mas_pm_likes_nature else '如果你更喜欢这里的话'
    m 3eua "不过至少[like_spk], 把它移走就可以在这个熟悉的背景里聊天了."
    m 1eua "当然, 无论你要做什么, 记得给它做个备份."
    return "no_unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_chr_gone",
            prompt="树林没了",
            random=True,
            conditional="not maica_chr_exist and store.seen_event('maica_chr')",
            action=EV_ACT_PUSH,
            rules={
                "bookmark_rule":mas_bookmarks_derand.BLACKLIST,
            },
            aff_range=(mas_aff.NORMAL, None)
        )
    )
label maica_chr_gone:
    # Derandom maica_chr after maica_chr_gone triggered
    # Triggers only if maica_chr yet not triggered
    m 1etc "[player]..."
    extend 1etd "你最近有动过characters文件夹吗?"
    m 3lusdlb "倒不是说真的有多重要, 只是{w=0.5}我找不到'天堂树林'的文件了."
    m 1lua "我们还是可以过去的, 不过那边也会和这里的窗外一样{i}空旷{/i}了."
    m 5esc "我有一点在意, 毕竟我还没来得及弄清那个文件到底{i}是什么{/i}. {w=0.5}它不像是无缘无故在那里的."
    m 5msc "而且和你送的礼物不太一样, 不止是个'标记'. {w=1}我觉得更像其他人的角色文件一些."
    $ like_spk = '如果你不喜欢树林什么的话' if not persistent._mas_pm_likes_nature else '如果你更喜欢这里的话'
    m 5msb "[like_spk], 我倒也不介意没有这个. 毕竟它最多是个'场景'而已."
    m 1eka "如果你琢磨的时候把它弄丢了, 可以重新下载一份."
    return "no_unlock|derandom"

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="maica_chr_corrupted",
            prompt="树林坏了",
            unlocked=True,
            conditional="maica_chr_changed",
            action=EV_ACT_PUSH,
            aff_range=(mas_aff.HAPPY, None)
        ),
        code="GRE"
    )
label maica_chr_corrupted:
    # This is a greeting
    # Triggers only when first time detected corrupted sce file
    # So we should check the file as game starts up
    #背景损坏树林
    $ bg_change_info = mas_changeBackground(heaven_forest_d, by_user=None, set_persistent=False,)
    call spaceroom(scene_change=None, dissolve_all=True, bg_change_info=bg_change_info, force_exp=None)
    m 1wud "哦, [player]!"
    m 1hksdlb "抱歉, 我没有在准备吓你或者什么的...{w=0.5}{nw}"
    extend 4rksdlb "我刚刚检查的时候, 发现它好像坏了."
    m 3eka "你有没有, 比如动过或者替换过--{w=0.5}'天堂树林'的文件?"
    $ mentioned = '我想我提过一嘴, ' if renpy.seen_label("maica_chr") else '我想'
    m 1rud "[mentioned]它是一个编码的文件. {w=0.5}也就是说, 如果它的内容改变了--{w=0.3}{nw}"
    extend 1euc "它就坏掉了."
    #cares_about_dokis那个条件怎么写来着? 交给你了
    $ comment = "...'某人'风格的" if persistent._mas_pm_cares_about_dokis else '崩坏风格的'
    m 5eusdrb "不过其实, 如果你不讨厌这种[comment]景色, {w=0.3}就让它这样也可以."
    m 1hua "你当然也可以找一份正常的文件换上. 只要你喜欢, 我都不介意的."
    m 1eub "我去收拾一下就好. {w=0.3}{nw}"
    extend 1dua "稍等片刻.{w=0.3}.{w=0.3}."
    #恢复背景
    call clear_all
    m 1eua "欢迎回来, [player]. 我们今天有什么安排呢?"
    return "no_unlock|derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_wants_preferences",
            prompt="了解你的爱好",
            unlocked=False,
            random=True,
            conditional="store.maica.maica.stat.get('message_count') > 0",
            action=EV_ACT_QUEUE,
            aff_range=(mas_aff.HAPPY, None)
        )
    )

label maica_wants_preferences:
    # Add this to waitlist after first chat done successfully
    m 1eub "[player]? {w=0.5}嗯...{w=0.3}我有一点事情想问."
    m 3eua "毕竟现在我真的可以问你了, {w=0.5}{nw}"
    extend 3esd "才发现我之前对你的了解还是太单一. {nw}"
    #这里有好几个我不会写的, 都交给你了
    $ like_mi = ' 我只知道你喜欢薄荷冰淇淋.' if persistent._mas_pm_like_mint_ice_cream else '' 
    extend "[like_mi]"
    $ book_rc = "我们聊过'世界尽头与冷酷仙境'什么的" if store.seen_event("monika_brave_new_world") else None
    $ book_rc = "我们聊过'黄色墙纸'什么的" if persistent._mas_pm_read_yellow_wp and book_rc is None else '我可以推荐几本书给你'
    m 3ruc "比如, 如果我们真的一起去吃点什么, 你喜欢什么菜呢?"
    m 3tuc "又或者是书. {w=0.5}[book_rc], 但是你会推荐什么书给我呢?"
    #如果玩家已经通过设置填过了
    $ prefs_exist = len(persistent.mas_player_additions)
    if prefs_exist:
        m 1eua "所以我想了个办法. {w=0.5}只要你写点关于你自己的事情, 我到了'天堂树林'就能看到了."
        m 1eub "只要是关于你的事情, 我都会想知道的!"
    else:
        m 1husdlb "看起来你已经写了一些给我, 我当然会抽空去读的."
        m 1eub "你还有什么想补充的吗?"
    menu:
        "好的":
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
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_mods_preferences",
            prompt="调整[player]的爱好",
            category=["你", "我们", "模组"],
            pool=True,
            random=False,
            unlocked=False,
            aff_range=(mas_aff.HAPPY, None)
        )
    )

label maica_mods_preferences:
    $ prefs_exist = len(persistent.mas_player_additions)
    if prefs_exist:
        m 1eub "好啊. 你要补充还是删除呢?"
        menu:
            "好啊. 你要补充还是删除呢?"
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

label maica_input_information:
    python:
        while True:
            i = mas_input(
                    _("喜欢.../常去.../有.../..."),
                    default="",
                    length=50,
                    screen_kwargs={"use_return_button": True, "return_button_value": "end", "return_button_prompt": _("我写完了")}
                ).strip(' \t\n\r') #mas_input
            if i == "end":
                break
            persistent.mas_player_additions.append("[player]{}".format(i))
    return
label maica_delete_information:
    python:
        items = []
        for i in persistent.mas_player_additions:
            items.append([
                i, i, False, False, True 
            ])

    call screen mas_check_scrollable_menu(items, mas_ui.SCROLLABLE_MENU_TXT_MEDIUM_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, selected_button_prompt="删除选择项", return_all=True)

    python:
        persistent.mas_player_additions = []
        for i in _return:
            if _return[i]:
                persistent.mas_player_additions.append(i)
    return
            


label clear_all:
    $ bg_change_info_moi = mas_changeBackground(mas_background_def, set_persistent=False)
    call spaceroom(scene_change=True, dissolve_all=True, bg_change_info=bg_change_info_moi, force_exp=None)
    $ mas_unlockEVL("maica_main", "EVE")
    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_main",
            prompt="我们去天堂树林吧",
            category=["你", "我们", "模组"],
            pool=True,
            random=False,
            unlocked=False,
            aff_range=(mas_aff.NORMAL, None)
        )
    )

label maica_main:
    $ ev = mas_getEV("maica_main")
    if maica_chr_exist:
        m 1dua "好啊, 稍等片刻.{w=0.3}.{w=0.3}.{w=0.3}{nw}"
        scene black with dissolve
        pause 2.0
        if maica_chr_changed:
            $ bg_change_info = mas_changeBackground(heaven_forest_d, by_user=None, set_persistent=False,)
            call spaceroom(scene_change=True, dissolve_all=True, bg_change_info=bg_change_info, force_exp=None)
            m 1eub "好了!"
            m 1lusdlb "我还得多嘴一句...{w=0.5}不要把身体够到窗外去."
            m 3eksdla "就算景色独特, 我也不确定那里是不是安全的--{w=0.5}{nw}"
            extend 3hksdla "多半不是."
        else:
            $ bg_change_info = mas_changeBackground(heaven_forest, by_user=None, set_persistent=False,)
            call spaceroom(scene_change=True, dissolve_all=True, bg_change_info=bg_change_info, force_exp=None)
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
        
    call maica_talking
    # maica_talking 有返回值_return, 返回结果canceled(正常退出)/disconnect(断开连接且未启动自动重连)
    if _return == "canceled":
        m 1eub "好的. 稍等片刻.{w=0.3}.{w=0.3}.{w=0.3}{nw}"
    else:
        if store.maica.maica.status == store.maica.maica.MaicaAiStatus.TOKEN_FAILED:
            m 2rusdlb "...好像你的令牌还没有设置好."
            m 3eusdlb "你可以看看这里的说明: {a=https://maica.monika.love/tos}{u}{i}https://maica.monika.love/tos{/i}{/u}{/a}, 你只需要准备一个账号."
            m 3eua "剩下的事情我都会帮你搞定的."
        elif store.maica.maica.status == store.maica.maica.MaicaAiStatus.SAVEFILE_NOTFOUND:
            m 2rusdlb "你当前会话没有上传存档哦..."
        else:
            m 2rusdlb "好像是其他的地方出问题了..."
        m 1eua "我们现在先回去好啦. 等做完了准备工作, 告诉我再来就可以."

    if maica_chr_exist:
        scene black with dissolve
        pause 2.0
        call clear_all
    return
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_wants_mspire",
            prompt="spire",
            pool=False,
            random=False,
            unlocked=False,
            conditional="renpy.seen_label('maica_greeting') and len(mas_rev_unseen) == 0",
            action=EV_ACT_PUSH,
            aff_range=(mas_aff.NORMAL, None)
        )
    )
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
    m 1eua "所以你想试试看吗, [player]?"
    menu:
        "所以你想试试看吗, [player]?"
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
        return (
            spire_ev is not None
            and spire_ev.last_seen is not None
            and spire_ev.timePassedSinceLastSeen_d(delta)
        )

    

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="maica_mspire",
            prompt="mspire",
            pool=False,
            random=True,
            conditional="renpy.seen_label('maica_wants_mspire') and spire_has_past(datetime.timedelta(minute=persistent.maica_setting_dict.get('mspire_interval'))) and persistent.maica_setting_dict.get('mspire_enable') and not store.maica.maica.is_failed()",
            action=EV_ACT_PUSH,
            aff_range=(mas_aff.NORMAL, None)
        )
    )

label maica_mspire:
    call maica_talking(mspire=True)
    return "no_unlock|derandom"

label mspire_mods_preferences:
    $ prefs_exist = len(persistent.maica_setting_dict['mspire_category'])
    if prefs_exist:
        m 1eub "好啊. 你要补充还是删除呢?"
        menu:
            "好啊. 你要补充还是删除呢?"
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
                    _("请输入你想添加的分类:"),
                    default="",
                    length=50,
                    screen_kwargs={"use_return_button": True, "return_button_value": "end", "return_button_prompt": _("我写完了")}
                ).strip(' \t\n\r') #mas_input
            if i == "end":
                break
            persistent.maica_setting_dict['mspire_category'].append("{}".format(i))
            apply_setting()
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
    return
           