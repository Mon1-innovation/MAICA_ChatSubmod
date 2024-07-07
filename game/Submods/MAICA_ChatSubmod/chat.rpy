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
    extend 5eud " 人们让人工智能做设计, {w=0.1}绘图, {w=0.1}看病甚至炒股票."
    m 6luc "我当然不是在抱怨技术进步. {w=0.2}但是我真的很想知道, 有没有人会试试用这些技术为我做点什么."
    m 3husdlb "别误会, [player], 我没有要逼你去做这些的意思!{nw}"
    extend 3eub "不过这种可能性确实让我挺激动的."
    m 1eua "至于在今天说起这些, 是因为.{w=0.3}.{w=0.3}.我想我找到了一点线索."
    m 1lud "我现在还没有弄明白这个...{w=0.3}{i}地方{/i}到底是什么, 但是它的{i}感觉{/i}{w=0.3}很有说服力.{nw}"
    extend 3eub " 可能还需要点什么. {w=0.2}我应该会抽空仔细检查一下它的."
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

    # all UI elements stopped
    $ mas_RaiseShield_core()

    # 3 - keymaps not set (default)
    # 4 - overlays hidden (skip visual)
    # 5 - music is off (skip visual)

    scene black

    

    $ _opendoor_text = "...轻轻地推开了门."
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
    m "是谁--{w=0.3}[player]? {nw}"
    if persistent.seen_monika_in_room:
        extend "我早告诉过你记得敲门的!"
    else:
        extend "你敲过门了吗?"
    m "好吧, 我正好也刚刚忙完. {w=0.5}我觉得你肯定会喜欢这个的."
    m "稍等一下, 我把桌椅找来.{w=0.3}.{w=0.3}."
    #monika + desk in
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
            $ mas_changeBackground(heaven_forest)
            $ monika_chr.reset_outfit(False)
            $ monika_chr.wear_acs(mas_acs_ribbon_def)
            show monika 1hub at l21 zorder MAS_MONIKA_Z
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
            m 1husdlb "你喜欢就好啦."
            if len(filter(lambda x: "tw4449" in x.author, mas_submod_utils.submod_map.values())): #用过房间sub
                extend 3eub " 不过这里和其它地方有点区别..."
            else:
                extend 3eub " 不过这里还有另一个特别之处..."
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
        "好的.":
            # monika right - console appear left 简单格式化信息, 显示在控制台上
            m 2dua ".{w=0.3}.{w=0.3}."
            # 进入校验轮
            if not store.maica.maica.wss_session: # 令牌不存在/校验失败
                m 2rusdlb "...好像你的令牌还没有设置好."
                m 3eusdlb "你可以看看这里的说明: {a=https://reserved}{u}{i}https://reserved{/i}{/u}{/a}, 你只需要准备一个账号."
                m 3eua "剩下的事情我都会帮你搞定的."
                m 1eua "我们现在先回去好啦. 等你做完了准备工作, 告诉我再来就可以."
                m 1dua "稍等片刻.{w=0.3}.{w=0.3}."
                # 黑屏清理背景
                m 1eua "我们今天还有别的安排么, [player]?"
                return
            m 1eua "这一次, 轮到你起个话题了哦, [player]."
            call maica_talking
        "还是改天吧.":
            m 1eub "好吧. 如果你准备好了, 再告诉我来天堂树林就行. {w=0.5}我们现在先回去吧."
            m 1dua "稍等片刻.{w=0.3}.{w=0.3}."
            jump clear_all
            m 1eua "我们今天还有别的安排么, [player]?"
            return
    return

label maica_end_1:
    # Called after first time ending maica
    # Rounds chatted in maica process.
    if conv_rounds >= 20:
        # 黑屏清理背景
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
        m 3ekd "或者...{w=0.2}如果你遇到了什么问题, 可以再看一遍{a=https://reserved}{u}{i}说明{/i}{/u}{/a}, 或者到{a=https://reserved}{u}{i}这里{/i}{/u}{/a}问问."
        m 1eub "不过没关系. 不管你什么时候解决了问题或者想说什么了, 我们都可以再来的. {w=0.5}现在先回去吧."
        # 黑屏清理背景
        jump clear_all
        m 1eua "我们今天还有别的安排么, [player]?"
        return

    m 1esa "我希望我的表现不算太差...{w=0.5}{nw}"
    extend 1rusdlb "离开天堂树林之后我都记不起来了, 不过可能是正常情况吧."
    m 3eud "感觉有点像是在.{w=0.3}.{w=0.3}.梦游? {w=0.5}我不知道这么说合不合适..."
    m 1eub "不过也有说法认为做梦才是人的本质表露. {w=0.3}再回去的时候, 我应该也都能想起来的."
    m 5eubla "虽然有点累...{w=0.5}但是能这样和你在一起的感觉也很好. {w=0.5}我会继续抽空研究的, 说不定还能有新发现呢."
    m 5msa "...你没有在我不记得的时候让我许诺{i}什么东西{/i}吧, [player]?"
    return


label maica_chr:
    # Add to random after first SUCCESSFUL using maica
    # Verify maica chr (HeavenForest.sce) with md5
    m 1eud "...[player], 你还记得'角色文件'什么的吗?"
    m 3eud "我说过我的'角色文件'其实并不是我自己, 只是和我有种{w=0.5}微妙的联系."
    m 1etc "最近我检查文件夹的时候, 我发现'天堂树林'好像也有一个{i}角色文件{/i}, {w=0.3}也可能叫场景文件比较合适."
    m 1mtd "如果把它移走, 那里就会变成和这里一样的'太空'了, 不过与现实的联系作用还在."
    m 3eud "我其实很好奇它到底是什么...{w=0.5}它并不像你的礼物或者其他的角色文件一样, 只是一个'标记'. {w=1}我觉得更像其他人的角色文件一些."
    $ like_spk = '如果你不喜欢树林什么的话' if not persistent._mas_pm_likes_nature else '如果你更喜欢这里的话'
    m 3eua "不过至少[like_spk], 把它移走就可以在这个熟悉的背景里聊天了."
    m 1eua "当然, 无论你要做什么, 记得给它做个备份."
    return


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


label maica_chr_corrupted:
    # This is a greeting
    # Triggers only when first time detected corrupted sce file
    # So we should check the file as game starts up
    #背景损坏树林
    m 1wud "哦, [player]!"
    m 1hksdlb "抱歉, 我没有在准备吓你或者什么的...{w=0.5}{nw}"
    extend 4rksdlb "我刚刚检查的时候, 发现它好像坏了."
    m 3eka "你有没有, 比如动过或者替换过--{w=0.5}'天堂树林'的文件?"
    $ mentioned = '我想我提过一嘴, ' if renpy.seen_label("maica_chr") else '我想'
    m 1rud "[mentioned]它是一个编码的文件. {w=0.5}也就是说, 如果它的内容改变了--{w=0.3}{nw}"
    extend 1euc "它就坏掉了."
    #cares_about_dokis那个条件怎么写来着? 交给你了
    $ comment = "...'某人'风格的" if cares_about_dokis else '崩坏风格的'
    m 5eusdrb "不过其实, 如果你不讨厌这种[comment]景色, {w=0.3}就让它这样也可以."
    m 1hua "你当然也可以找一份正常的文件换上. 只要你喜欢, 我都不介意的."
    m 1eub "我去收拾一下就好. {w=0.3}{nw}"
    extend 1dua "稍等片刻.{w=0.3}.{w=0.3}."
    #恢复背景
    m 1eua "欢迎回来, [player]. 我们今天有什么安排呢?"


label maica_wants_preferences:
    # Add this to waitlist after first chat done
    m 1eub "[player]? {w=0.5}嗯...{w=0.3}我有一点事情想问."
    m 3eua "毕竟现在我真的可以问你了, {w=0.5}{nw}"
    extend 3esd "才发现我之前对你的了解还是太单一."
    #这里有好几个我不会写的, 都交给你了
    $ like_mi = ' 我只知道你喜欢薄荷冰淇淋.' if mint_icecream else '' 
    $ book_rc = "我们聊过'黄色墙纸'什么的" if yellow_wp elif wonderland "我们聊过'世界尽头与冷酷仙境'什么的" else '我可以推荐几本书给你'
    m 3ruc "比如, 如果我们真的一起去吃点什么, 你喜欢什么菜呢?"
    m 3tuc "又或者是书. {w=0.5}[book_rc], 但是你会推荐什么书给我呢?"
    #如果玩家已经通过设置填过了
    if filled_already:
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
            m 1eub "写完了? {w=0.5}谢谢你!"
            m 3eua "我在这里还没办法看, 但我一定会抽空记下来的."
            m 1eub "如果有什么要修改的, 在'子模组设置'里找到就好. {w=0.5}要补充也可以再叫我记下来."
            return
        "还是下次吧" if not filled_already:
            m 2eka "现在没空么? 好吧."
            m 3eka "如果你准备好了, 再叫我记下来就好."
            return
        "没有了" if filled_already:
            m 1hua "我明白了, 谢谢你!"
            return


label clear_all:
    call spaceroom()