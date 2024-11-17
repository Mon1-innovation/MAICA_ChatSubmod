label maica_talking(mspire = False):
    if persistent.maica_setting_dict['console']:
        show monika at t22
        show screen mas_py_console_teaching
    python:
        import time
        import copy
        from store.maica import maica as ai
        from maica_mtrigger import MTriggerAction 
        ai.content_func = store.mas_ptod._update_console_history
        ai.send_to_outside_func(ai.ascii_icon)
        if mspire:
            ai.send_to_outside_func("<submod> MSpire init...")
        if persistent.maica_setting_dict['console']:
            store.mas_ptod.write_command("Thank you for using MAICA Blessland!")
            renpy.pause(2.3)
        if not ai.is_connected():
            ai.init_connect()
        printed = False
        is_retry_before_sendmessage = False
        while True:
            if not ai.is_connected():
                store.mas_ptod.write_command("Init Connecting...")
                renpy.pause(0.3, True)
                if not ai.is_connected() and not ai.is_failed():
                    continue
            if not ai.is_connected() and persistent.maica_setting_dict['auto_reconnect']:
                ai.init_connect()
                renpy.pause(0.3, True)
                store.mas_ptod._update_console_history("Websocket is closed, reconnecting...")
            if not ai.is_ready_to_input() and not ai.is_failed():
                store.mas_ptod.write_command("Wait login...")
                renpy.say(m, ".{w=0.3}.{w=0.3}.{w=0.3}{nw}")
                _history_list.pop()
                continue
            if ai.is_ready_to_input() and not printed:
                store.mas_ptod.write_command("Login successful, ready to chat!")
                printed = True
            elif ai.is_failed():
                if ai.status == ai.MaicaAiStatus.TOKEN_FAILED:
                    store.mas_ptod.write_command("Login failed, please check your token.")
                elif ai.status == ai.MaicaAiStatus.SAVEFILE_NOTFOUND:
                    store.mas_ptod.write_command("Savedata not found, please check your setting.")
                else:
                    store.mas_ptod.write_command("An error occurred, please check your submog_log.log")
                renpy.pause(2.0)
                renpy.say(m, _("似乎连接出了问题, 一会再试试吧~"))
                _return = "disconnected"
                break
            if is_retry_before_sendmessage:
                ai.chat(is_retry_before_sendmessage)
                question = is_retry_before_sendmessage
                is_retry_before_sendmessage = False
            renpy.show("monika {}".format(ai.MoodStatus.get_emote(True)))
            if ai.is_ready_to_input():
                if mspire is False:
                    question = mas_input(
                                _("说吧, [player]"),
                                default="",
                                length=75,
                                screen="maica_input_screen"
                                #screen_kwargs={"use_return_button": True, "return_button_value": "nevermind", "return_button_prompt": _("就这样吧")}
                            ).strip(' \t\n\r') #mas_input
                    if question == "":
                        continue
                    if question == "nevermind":
                        _return = "canceled"
                        ai.content_func = None
                        break
                    to_history = copy.deepcopy(_history_list[-1])
                    to_history.who = persistent.playername
                    to_history.what = question
                    _history_list.append(to_history)
                    ai.chat(question)
                    is_retry_before_sendmessage = False
                else:
                    ai.start_MSpire()
            if not ai.is_connected() and persistent.maica_setting_dict['auto_reconnect']:
                ai.init_connect()
                renpy.pause(0.3, True)
                store.mas_ptod._update_console_history("Websocket is closed, reconnecting...")
                is_retry_before_sendmessage = question
                continue

            start_time = time.time()
            start_token = ai.stat.get("received_token", 0)
                        
            gentime = 0.0
            while ai.is_responding() or ai.len_message_queue() > 0 :
                if ai.is_responding():
                    gentime = time.time()
                else:
                    gentime = ai._gen_time
                if not ai.is_connected() and persistent.maica_setting_dict['auto_reconnect']:
                    ai.init_connect()
                    store.mas_ptod._update_console_history("Websocket is closed, reconnecting...")

                store.mas_ptod.write_command("Maica.status:{} | message_queue: {}/{}token | time: {}".format(
                    ai.status, ai.len_message_queue(), ai.stat.get("received_token", 0) - start_token,
                    round(gentime - start_time)
                    ))
                if ai.is_failed():
                    if ai.len_message_queue() == 0:
                        renpy.say(m, _("好像出了什么问题..."))
                        _return = "disconnected"
                        break
                if ai.len_message_queue() == 0:
                    #renpy.show(monika 1eua)
                    store.mas_ptod.write_command("Wait message...")
                    renpy.say(m, ".{w=0.3}.{w=0.3}.{w=0.3}{nw}")
                    _history_list.pop()
                    continue    
                message = ai.get_message()
                store.mas_submod_utils.submod_log.debug("label maica_talking::message:'{}', '{}'".format(message[0], message[1]))
                renpy.show(u"monika {}".format(message[0]))
                try:
                    renpy.say(m, message[1])
                except Exception as e:
                    store.mas_submod_utils.submod_log.error("label maica_talking::renpy.say error:{}".format(e))
                    ai.send_to_outside_func("!!SUBMOD ERROR when chatting: {}".format(e))
            _return = "mtrigger_triggering"

            ai.mtrigger_manager.run_trigger(MTriggerAction.post)
            if mspire:
                _return = "canceled"
                afm_pref = renpy.game.preferences.afm_enable
                renpy.game.preferences.afm_enable = False
                break
            
    # store.mas_ptod.write_command()

    # store.mas_ptod._update_console_history([])

    
    if persistent.maica_setting_dict['console']:    
        $ store.mas_ptod.clear_console()
        hide screen mas_py_console_teaching
        show monika at t11
    return _return

