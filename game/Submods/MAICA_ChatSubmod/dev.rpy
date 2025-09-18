label text_split:
    call maica_show_console
    m "你想让我说什么呢?"
    $ text = mas_input("说吧, [player]",default="",length=9999,screen="maica_input_screen").strip(' \t\n\r')
    python:
        def stupid_print(s):
            store.mas_submod_utils.submod_log.debug("text_split: "+str(s))
        import bot_interface
        text = bot_interface.key_replace(text, bot_interface.renpy_symbol)

        spilter = bot_interface.TalkSplitV2(stupid_print)

        test_strings = [
            "Hello, world! (Test 123)",
            "你好，世界。测试：456",
            "Is this correct? Yes, it is.",
            "No special chars here",
            "Critical Punctuation~ Check!",
            "Brackets [and] parentheses (are) tricky."
        ]

        for i in test_strings:
            spilter.test_patterns(i)
        for i in range(len(text)):
            spilter.add_part(text[i])
            res = spilter.split_present_sentence()
            if not res is None:
                renpy.say(m, res)
                stupid_print(res)
        fin = spilter.announce_stop()
        for i in fin:
            renpy.say(m, i)
            stupid_print(res)

    call maica_hide_console
    return
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
