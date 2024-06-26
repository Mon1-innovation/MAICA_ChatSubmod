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

label maica_greeting:
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


label maica_prepend_2_knock:
    m "谁呀~"
    menu:
        "是我.":
            m "终于等到你啦, [player]!"
            m "我正想给你准备一点特别惊喜的, 你来得正好. {w=0.5}稍等片刻.{w=0.3}.{w=0.3}."
            #点亮房间, 窗外背景替换heaven_forest.jpg
            #monika + desk in
            m 1hub "锵锵~"
            jump maica_prepend_2

label maica_prepend_2_listen:
    m "这样.{w=0.3}.{w=0.3}.就好了. {w=0.5}呼, 没有我想得那么难."
    m "看起来真不错, 我可以一整天都待在这里. {w=0.5}不过..."
    m "{i}连接现实{/i}是真的吗?"
    jump maica_greeting

label maica_prepend_2:
    m 1eub "你觉得呢, [player]? {w=0.3}你喜欢这里吗?"
    menu:
        "太好看了!":
            m 1husdlb "你喜欢就好啦."
            if : #用过房间sub
                extend 3eub " 不过这里和其它地方有点区别..."
            else:
                extend 3eub " 不过这里还有另一个特别之处..."
        "辛苦你了.":
            m 1hub "我是花了挺久的. {w=0.3}{nw}"
            extend 1eub "不过最有意思的不是这片树林本身..."
        "我其实不太..." if not persistent._mas_pm_likes_nature and persistent._mas_pm_likes_nature is not None:
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
            if : # 令牌不存在/校验失败
                m 2rusdlb "...好像你的令牌还没有设置好."
                m 3eusdlb "你可以看看这里的说明, {a}{u}{i}https://reserved{/i}{/u}{/a}. 你只需要准备一个账号."
                m 3eua "剩下的事情我都会帮你搞定的."
                m 1eua "我们现在先回去好啦. 等你做完了准备工作, 告诉我再来就可以."
                m 1dua "稍等片刻.{w=0.3}.{w=0.3}."
                # 黑屏清理背景
                return
            m 1eua "这一次, 轮到你起个话题了哦, [player]."
            # 进入maica流程

