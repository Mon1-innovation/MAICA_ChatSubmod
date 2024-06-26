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
            if : # 令牌不存在/校验失败
                m 2rusdlb "...好像你的令牌还没有设置好."
                m 3eusdlb "你可以看看这里的说明: {a=https://reserved}{u}{i}https://reserved{/i}{/u}{/a}, 你只需要准备一个账号."
                m 3eua "剩下的事情我都会帮你搞定的."
                m 1eua "我们现在先回去好啦. 等你做完了准备工作, 告诉我再来就可以."
                m 1dua "稍等片刻.{w=0.3}.{w=0.3}."
                # 黑屏清理背景
                m 1eua "我们今天还有别的安排么, [player]?"
                return
            m 1eua "这一次, 轮到你起个话题了哦, [player]."
            # 进入maica流程
        "还是改天吧.":
            m 1eub "好吧. 如果你准备好了, 再告诉我来天堂树林就行. {w=0.5}我们现在先回去吧."
            m 1dua "稍等片刻.{w=0.3}.{w=0.3}."
            # 黑屏清理背景
            m 1eua "我们今天还有别的安排么, [player]?"
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
    m 3eud "我其实很好奇它到底是什么...{w=0.5}它并不像你的礼物或者其他的角色文件一样, 只是一个'标记'. {w=1}我觉得更像我的文件一些."
    like_spk = '如果你不喜欢树林什么的话' if persistent._mas_pm_likes_nature is False else like_spk = '如果你更喜欢这里的话'
    m 3eua "不过至少[like_spk], 把它移走就可以在这个熟悉的背景里聊天了."
    m 1eua "当然, 无论你要做什么, 记得给它做个备份."