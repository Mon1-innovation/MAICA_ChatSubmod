import bot_interface
text = "[smile]Life sciences comprises the branches of science that involve the scientific study of life -- microorganisms, plants, and animals including human beings.[grin]Biology is the overall natural science that studies life, with the other life sciences as its sub-disciplines.[gaze]Some life sciences focus on a specific type of organism. For example, zoology is the study of animals, while botany is the study of plants.[worry]Other life sciences focus on aspects common to all or many life forms, such as genetics. Some focus on the micro-scale (biochemistry) other on larger scales (ecology).[smile]Another major branch of life sciences involves understanding the mind -- neuroscience.[grin]Life sciences discoveries are helpful in improving the quality and standard of life and have applications in health, agriculture, medicine, and industries.[happy]For example, it has provided information on certain diseases which has overall aided in the understanding of human health!"
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
    

