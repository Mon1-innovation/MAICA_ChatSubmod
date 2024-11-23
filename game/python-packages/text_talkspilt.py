# -*- coding:utf-8 -*-
#text = "But if you really have to wait for someone to bring you the sun and give you a good feeling, then you may have to wait a long time."
import bot_interface
#text = "[smile]Life sciences comprises the branches of science that involve the scientific study of life -- microorganisms, plants, and animals including human beings.[grin]Biology is the overall natural science that studies life, with the other life sciences as its sub-disciplines.[gaze]Some life sciences focus on a specific type of organism. For example, zoology is the study of animals, while botany is the study of plants.[worry]Other life sciences focus on aspects common to all or many life forms, such as genetics. Some focus on the micro-scale (biochemistry) other on larger scales (ecology).[smile]Another major branch of life sciences involves understanding the mind -- neuroscience.[grin]Life sciences discoveries are helpful in improving the quality and standard of life and have applications in health, agriculture, medicine, and industries.[happy]For example, it has provided information on certain diseases which has overall aided in the understanding of human health!"
text = "[思考]室扑（心室扑动）和室颤（心室颤动）都是严重的心律失常，但它们之间存在一些关键的区别。[微笑] 室扑是一种快速而规则的心室节律，频率通常在150-300次/分钟，心电图上表现为连续的大振幅波形。而室颤则是无序且不规则的心室活动，频率可高达250-600次/分钟，心电图上表现为杂乱无章的波形。[开心] 希望这些信息对你有帮助！如果你有任何其他问题，请随时告诉我。"

import bot_interface

spilter = bot_interface.TalkSplitV2()
for i in range(len(text)):
    spilter.add_part(text[i])
    res = spilter.split_present_sentence()
    if not res is None:
        print(res)
fin = spilter.announce_stop()
for i in fin:
    print(i)
