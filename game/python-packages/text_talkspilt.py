# -*- coding:utf-8 -*-
#text = "But if you really have to wait for someone to bring you the sun and give you a good feeling, then you may have to wait a long time."
import bot_interface
#text = "[smile]Life sciences comprises the branches of science that involve the scientific study of life -- microorganisms, plants, and animals including human beings.[grin]Biology is the overall natural science that studies life, with the other life sciences as its sub-disciplines.[gaze]Some life sciences focus on a specific type of organism. For example, zoology is the study of animals, while botany is the study of plants.[worry]Other life sciences focus on aspects common to all or many life forms, such as genetics. Some focus on the micro-scale (biochemistry) other on larger scales (ecology).[smile]Another major branch of life sciences involves understanding the mind -- neuroscience.[grin]Life sciences discoveries are helpful in improving the quality and standard of life and have applications in health, agriculture, medicine, and industries.[happy]For example, it has provided information on certain diseases which has overall aided in the understanding of human health!"
text = "你知道世界音乐奖吗, [player]? 这是一个每年评选出来的国际重要音乐奖. 它成立于1989年, 由摩纳哥王子阿尔贝二世和约翰·马丁内蒂联合创办. 这个奖项的独特之处在于它不购买网络会员, 也不收取投票费用. 而是根据国际唱片协会的销售报表和全球粉丝的即时票选支持度来决定获奖者. 每年都有超过160个国家的电视台直播或转播颁奖典礼, 观众人数超过10亿. 世界音乐奖还致力于慈善事业, 在非洲、亚洲和南美洲建立了23个慈善组织. 所以除了表彰音乐成就之外, 它还在做些有意义的事情哦!"

import bot_interface

spilter = bot_interface.TalkSplitV2(print)
for i in range(len(text)):
    spilter.add_part(text[i])
    #res = spilter.split_present_sentence()
    #if not res is None:
    #    print(res)
fin = spilter.announce_stop()
for i in fin:
    print(i)
