text = "[凝视]你有没有想过艺术自由的问题? [凝视]我的意思是, 我知道它存在, 但是当我开始思考时, 我意识到它并不像看起来那么简单. [担心]为了说明我的意思, 我问你...[担心]你会怎样描述艺术表达的自由? [凝视]...你可能认为艺术自由就是政府不审查你, 政府不压制你, 或者其他人不压制你. 这当然是正确的! [担心]但是当你深入一点去想一想, 就会发现还有更多没有被考虑到的'自由'. 比如, 仅仅因为你的作品没有被禁就说明你是自由的吗? [担心]如果你的作品不受追捧或者被认为是低俗的呢? 如果这发生的话, 那么你就有可能受到骚扰甚至恐吓...[沉重]如果这对你造成了很大的影响以至于你想放弃表达自己的想法呢? 这算不算是对你的压制? 或者如果有人为了阻止你的工作而威胁要破坏你的生活呢? 又或者有人试图通过利用社会对你的看法来阻止你做你想做的事呢? ...我想说这都是对自由的侵犯. [思考]我认为我们所说的艺术自由不仅包括可以创造什么...[思考]还包括人们是否愿意创造它以及是否愿意让它存在. 毕竟, 如果连想都不敢想的话, 那还有什么希望可言呢. [笑]我希望你知道我真的很关心你的感受和想法. 如果有什么事让你觉得不能做某事或必须做某事...[笑]请先和我谈谈吧! 我会尽我所能帮助你的."
import bot_interface
text = "[smile]Video game addiction, or VGA, is defined as a psychological addiction that results in significant impairment to an individual's ability to function in various life domains over a prolonged period of time.[grin]This and associated concepts have been the subject of considerable research, debate, and discussion among experts in several disciplines and has generated controversy within the medical, scientific, and gaming communities.[worry]Such disorders can be diagnosed when an individual engages in gaming activities at the cost of fulfilling daily responsibilities or pursuing other interests without regard for the negative consequences.[think]As defined by the ICD-11, the main criterion for this disorder is a lack of self control over gaming.[smile]The World Health Organization included gaming disorder in the 11th revision of its International Classification of Diseases (ICD).[think]Controversy around the diagnosis includes whether the disorder is a separate clinical entity or a manifestation of underlying psychiatric disorders.[worry]Research has approached the question from a variety of viewpoints, with no universally standardized or agreed definitions, leading to difficulties in developing evidence-based recommendations."
pos = 0
text_length = len(text)

while pos < text_length:
    for i in range(pos + 1, text_length + 1):
        sub_text = text[pos:i]
        res = bot_interface.is_precisely_a_talk(sub_text)
        if res != 0:
            print(f"res{res} pos{pos} {sub_text[:res]}")
            pos += res  # 跳跃已识别的段落
            break
    else:
        pos += 1  # 如果没有任何匹配，在当前位置后继续
    
