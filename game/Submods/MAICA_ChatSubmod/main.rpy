label maica_talking:
    python:
        from store.maica import maica as ai
        while True:
            renpy.show("monika idle")
            question = mas_input(
                        "想和我聊什么呢?",
                        default="",
                        length=50,
                        screen_kwargs={"use_return_button": True, "return_button_value": "nevermind"}
                    ).strip(' \t\n\r') #mas_input
            if question == "":
                continue
            if question == "nevermind":
                break
            ai.chat(question)
            while ai.is_responding() or ai.len_message_queue() > 0 :
                if ai.wss_session.keep_running == False:
                    renpy.say(m, "似乎连接出了问题, 一会再试试吧~")
                    break
                if ai.len_message_queue() == 0:
                    #renpy.show(monika 1eua)
                    renpy.say(m, ".{w=0.3}.{w=0.3}.{w=0.3}{nw}")
                    continue    
                mes = ai.get_message()
                store.mas_submod_utils.submod_log.debug("label maica_talking::mes: {}".format(mes))
                renpy.show("monika {}".format(mes[0]))
                renpy.say(m, mes[1])
                
    return


