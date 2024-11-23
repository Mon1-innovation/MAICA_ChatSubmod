label text_split:
    call maica_show_console
    m "你想让我说什么呢?"
    $ text = mas_input("说吧, [player]",default="",length=9999,screen="maica_input_screen").strip(' \t\n\r')
    python:
        import bot_interface
        text = bot_interface.key_replace(text, bot_interface.renpy_symbol)
        pos = 0
        text_length = len(text)

        while pos < text_length:
            for i in range(pos + 1, text_length + 1):
                sub_text = text[pos:i]
                res = bot_interface.is_precisely_a_talk(sub_text, store.mas_ptod._update_console_history)
                if res != 0:
                    renpy.say(m, sub_text[:res])
                    pos += res  # 跳跃已识别的段落
                    break
            else:
                pos += 1  # 如果没有任何匹配，在当前位置后继续
    call maica_hide_console
    return
