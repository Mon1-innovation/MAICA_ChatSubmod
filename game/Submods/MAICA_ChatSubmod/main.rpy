label maica_talking:
    python:
        from store.maica import maica as ai
        while True:
            question = mas_input(
                        "想和我聊什么呢?",
                        default=""
                        allow=name_characters_only,
                        length=10,
                        screen_kwargs={"use_return_button": True, "return_button_value": "nevermind"}
                    ).strip(' \t\n\r') #mas_input
            if question == "":
                continue
            if question = "nevermind":
                break
            ai.chat(question)
            while ai.is_responding() or ai.len_message_queue() > 0:
                if ai.len_message_queue() = 0:
                    #renpy.show(monika 1eua)
                    renpy.say(m, ".{w=0.3}.{w=0.3}.{w=0.3}{nw}")
                    continue    
                mes = ai.get_message()
                renpy.show("monika {}".format(mes[0]))
                renpy.say(m, mes[1])
                


