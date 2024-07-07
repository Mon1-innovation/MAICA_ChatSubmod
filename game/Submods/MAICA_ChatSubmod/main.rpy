label maica_talking:
    if persistent.maica_setting_dict['console']:
        show monika at t22
        show screen mas_py_console_teaching
    python:
        import time
        from store.maica import maica as ai
        ai.content_func = store.mas_ptod._update_console_history
        while True:
            renpy.show("monika {}".format(ai.MoodStatus.get_emote(True)))
            question = mas_input(
                        "想和我聊什么呢?",
                        default="",
                        length=50,
                        screen_kwargs={"use_return_button": True, "return_button_value": "nevermind"}
                    ).strip(' \t\n\r') #mas_input
            if question == "":
                continue
            if question == "nevermind":
                _return = "canceled"
                ai.content_func = None
                break
            start_time = time.time()
            start_token = ai.stat.get("received_token", 0)
            ai.chat(question)
            while ai.is_responding() or ai.len_message_queue() > 0 :
                gentime = 0.0
                if ai.is_responding():
                    gentime = time.time() - start_time
                store.mas_ptod.write_command("Maica.status:{} | message_queue: {}/{}token | time: {}".format(
                    ai.status, ai.len_message_queue(), ai.stat.get("received_token", 0) - start_token,
                    round(gentime)
                    ))
                if ai.wss_session.keep_running == False and ai.len_message_queue() == 0:
                    renpy.say(m, "似乎连接出了问题, 一会再试试吧~")
                    _return = "disconnected"
                    
                if ai.len_message_queue() == 0:
                    #renpy.show(monika 1eua)
                    renpy.say(m, ".{w=0.3}.{w=0.3}.{w=0.3}{nw}")
                    continue    
                mes = ai.get_message()
                store.mas_submod_utils.submod_log.debug("label maica_talking::mes: {}".format(mes))
                renpy.show("monika {}".format(mes[0]))
                renpy.say(m, mes[1])
            
    # store.mas_ptod.write_command()

    # store.mas_ptod._update_console_history([])

    
    if persistent.maica_setting_dict['console']:
        
        $ store.mas_ptod.clear_console()
        hide screen mas_py_console_teaching
        show monika at t11
    return _return

