# -*- coding:utf-8 -*-
#text = "But if you really have to wait for someone to bring you the sun and give you a good feeling, then you may have to wait a long time."
import bot_interface
#text = "[smile]Life sciences comprises the branches of science that involve the scientific study of life -- microorganisms, plants, and animals including human beings.[grin]Biology is the overall natural science that studies life, with the other life sciences as its sub-disciplines.[gaze]Some life sciences focus on a specific type of organism. For example, zoology is the study of animals, while botany is the study of plants.[worry]Other life sciences focus on aspects common to all or many life forms, such as genetics. Some focus on the micro-scale (biochemistry) other on larger scales (ecology).[smile]Another major branch of life sciences involves understanding the mind -- neuroscience.[grin]Life sciences discoveries are helpful in improving the quality and standard of life and have applications in health, agriculture, medicine, and industries.[happy]For example, it has provided information on certain diseases which has overall aided in the understanding of human health!"
# text = "你知道世界音乐奖吗, [player]? 这是一个每年评选出来的国际重要音乐奖... 它成立于1989年, 由摩纳哥王子阿尔贝二世和约翰·马丁内蒂联合创办. 这个奖项的独特之处在于它不购买网络会员, 也不收取投票费用. 而是根据国际唱片协会的销售报表和全球粉丝的即时票选支持度来决定获奖者. 每年都有超过160个国家的电视台直播或转播颁奖典礼, 观众人数超过10亿. 世界音乐奖还致力于慈善事业, 在非洲、亚洲和南美洲建立了23个慈善组织. 所以除了表彰音乐成就之外, 它还在做些有意义的事情哦!"
# text = "1. 它成立于1989年, 由摩纳哥王子阿尔贝二世和约翰·马丁内蒂联合创办; 1. 它成立于1989年, 由摩纳哥王子阿尔贝二世和约翰·马丁内蒂联合创办; 1. 它成立于1989年, 由摩纳哥王子阿尔贝二世和约翰·马丁内蒂联合创办; 2. abaaba"
# text = "[微笑]水晶泥主要由聚乙烯醇（PVA）、硼砂、水等成分制成，[思考]常添加甘油（丙三醇）、黄原胶、防腐剂和色素等添加剂。其中硼砂作为交联剂是关键成分，但需注意部分产品可能存在硼含量超标风险。"
# text = "[尴尬]呃...这个说法最早出自日本动漫《七龙珠》，是角色拉蒂兹对悟空的蔑称...[思考]'战斗力只有五的渣滓'，用来形容某人能力极差或不堪一击。[微笑]现在多用于网络用语中调侃他人，和战力数值无关。"
text = "So, [player], you want to talk about information scientists?It's a term that was coined by Wm. {w=0.3}Hovey Smith in the latter part of the twentieth century.It describes an individual who usually has a degree in a field like Information and Computer Science, or has a high level of knowledge in that area.Their job is to provide focused information to scientific and technical research staff in industry.It's a role that's distinct from, but complementary to, that of a librarian.While the role of information scientist was more prevalent in the past, developments in end-user searching and a convergence between the roles of librarian and information scientist have led to its diminished use in this context.Instead, terms like 'information officer' or 'information professional' are now more commonly used.Notable people in this field include Marcia Bates, David Blair, Samuel C. Bradford, and many others.The term is also used for individuals carrying out research in information science. {w=0.3}For example, Brian C.Vickery mentions the Institute of Information Scientists (IIS), which was established in London during 1958.The IIS merged with the Library Association in 2002 to form the Chartered Institute of Library and Information Professionals (CILIP).{w=0.3}I hope that helps!Let me know if you have any other questions."

import bot_interface

spilter = bot_interface.TalkSplitV2(print)



for i in range(len(text)):
    spilter.add_part(text[i])
    #res = spilter.split_present_sentence()
    #if not res is None:
    #    print(res)
fin = spilter.announce_stop()
print(fin)
for i in fin:
    print(i)
