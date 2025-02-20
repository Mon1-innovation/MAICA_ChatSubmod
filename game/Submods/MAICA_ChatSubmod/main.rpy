label maica_talking(mspire = False):
    if persistent.maica_setting_dict['console']:
        show monika at t22
        show screen mas_py_console_teaching
    call maica_init_connect(use_pause_instand_wait = True)
    if _return == "disconnected":
        return "disconnected"
    python:
        import time
        import copy
        from store.maica import maica as ai
        from maica_mtrigger import MTriggerAction 
        import traceback
        ai.content_func = store.mas_ptod._update_console_history
        store.action = {}
        if mspire:
            ai.console_logger.info("<submod> MSpire init...")
            renpy.pause(2.3)
        printed = False
        is_retry_before_sendmessage = False
        while True:
            if is_retry_before_sendmessage:
                ai.chat(is_retry_before_sendmessage)
                question = is_retry_before_sendmessage
                is_retry_before_sendmessage = False
            renpy.show("monika {}".format(ai.MoodStatus.get_emote(True)))
            if ai.is_ready_to_input():
                if mspire is False:
                    if "stop" in store.action:
                        if store.action["stop"]:
                            store.action = {}
                            _return = "canceled"
                            break

                    question = mas_input(
                                _("说吧, [player]"),
                                default="",
                                length=75 if not config.language == "english" else 375,
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
            received_message = ""
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
                    if len(_history_list):
                        _history_list.pop()
                    continue    
                message = ai.get_message()
                store.mas_submod_utils.submod_log.debug("label maica_talking::message:'{}', '{}'".format(message[0], message[1]))
                received_message += message[1]
                renpy.show(u"monika {}".format(message[0]))
                try:
                    renpy.say(m, message[1])
                except Exception as e:
                    store.mas_submod_utils.submod_log.error("label maica_talking::renpy.say error:{}".format(traceback.format_exc()))
                    ai.console_logger.error("!!SUBMOD ERROR when chatting: {}".format(e))
            store.mas_submod_utils.submod_log.debug("label maica_talking::RESPONSE :'{}'".format(received_message))
            _return = "mtrigger_triggering"
            store.action = ai.mtrigger_manager.run_trigger(MTriggerAction.post)
            ai.console_logger.debug("<chat_action> {}".format(store.action))
            if store.action['stop']:
                _return = "canceled"
            if mspire:
                _return = "canceled"
                afm_pref = renpy.game.preferences.afm_enable
                renpy.game.preferences.afm_enable = False
            break
    # store.mas_ptod.write_command()

    # store.mas_ptod._update_console_history([])

label maica_talking.end:
    if persistent.maica_setting_dict['console']:    
        $ store.mas_ptod.clear_console()
        hide screen mas_py_console_teaching
        show monika at t11
    return _return

label maica_show_console:
    if persistent.maica_setting_dict['console']:
        show screen mas_py_console_teaching
        show monika at t22
    return
label maica_hide_console:
    if persistent.maica_setting_dict['console']:
        hide screen mas_py_console_teaching
        show monika at t11
    return

label maica_reconnect:
    python:
        store.maica.maica.close_wss_session()
    return

label maica_mpostal_load:
    python:
        if mail_exist(): 
            import time
            _postals = find_mail_files()
            for item in _postals:
                persistent._maica_send_or_received_mpostals.append(
                    {
                        "raw_title": item[0],
                        "raw_content":item[1],
                        "time": str(time.time()),
                        "responsed_content": "",
                        "responsed_status":"delaying",
                        "failed_count":0,
                    }
                )
    return

label maica_init_connect(use_pause_instand_wait = False):
    python:
        ai = store.maica.maica
        ai.content_func = store.mas_ptod._update_console_history
        ai.console_logger.critical("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n" + ai.ascii_icon)
        if not ai.is_connected():
            ai.init_connect()
        while True:
            if not ai.is_connected():
                store.mas_ptod.write_command("Init Connecting...")
                renpy.pause(0.3, True)
                if not ai.is_failed():
                    continue
            if not ai.is_ready_to_input() and not ai.is_failed():
                store.mas_ptod.write_command("Wait login...")
                if use_pause_instand_wait:
                    renpy.pause(1.0)
                else:
                    renpy.say(m, ".{w=0.3}.{w=0.3}.{w=0.3}{nw}")
                    if len(_history_list):
                        _history_list.pop()
                continue
            if ai.is_ready_to_input():
                store.mas_ptod.write_command("Login successful, ready to chat!")
                _return = "success"
                break
            elif ai.is_failed():
                if ai.status == ai.MaicaAiStatus.TOKEN_FAILED:
                    store.mas_ptod.write_command("Login failed, please check your token.")
                elif ai.status == ai.MaicaAiStatus.SAVEFILE_NOTFOUND:
                    store.mas_ptod.write_command("Savedata not found, please check your setting.")
                else:
                    store.mas_submod_utils.submod_log.error("maica_talking:: Unknown Error: ai.is_failed() = {}, ai.status = {}, ai.is_connected() = {}".format(ai.is_failed(), ai.status, ai.is_connected()))
                    store.mas_ptod.write_command("An error occurred, please check your submog_log.log")
                renpy.pause(2.0)
                _return = "disconnected"
                break
    call show_workload
    return _return

label maica_mpostal_read:
    $ mas_HKBRaiseShield()
    if persistent.maica_setting_dict.get("show_console_when_reply", False):
        call maica_show_console
    else:
        window hide
    call maica_mpostal_load
    call maica_init_connect(use_pause_instand_wait = True)
    if _return == "disconnected":
        jump maica_mpostal_read.failed

    python:
        ai = store.maica.maica
        import time
        for cur_postal in persistent._maica_send_or_received_mpostals:
            if cur_postal["responsed_status"] != "notupload":
                continue
            start_time = time.time()
            ai.start_MPostal(cur_postal["raw_content"], title=cur_postal["raw_title"])
            not_uploaded_count = sum(1 for postal in persistent._maica_send_or_received_mpostals if postal["responsed_status"] == "notupload")
            current_index = persistent._maica_send_or_received_mpostals.index(cur_postal) + 1  # Convert to 1-based index

            ai.console_logger.info("<submod> Processing mpostal {} ({}/{})".format(cur_postal["raw_title"], current_index, not_uploaded_count))
            cur_postal["responsed_status"] = "failed"            
            while ai.is_responding() or ai.len_message_queue() > 0 :
                if ai.is_responding():
                    gentime = time.time()
                else:
                    gentime = ai._gen_time


                store.mas_ptod.write_command("Maica.status:{} | time: {}".format(
                    ai.status, ai.len_message_queue(),
                    round(gentime - start_time)
                    ))
                if ai.is_failed():
                    if ai.len_message_queue() == 0:
                        cur_postal["responsed_status"] = "failed"
                        cur_postal["responsed_content"] = renpy.substitute(_("无法回复信件, 查看submod_log以获取详细原因\n错误码: [ai.status] | [ai.MaicaAiStatus.get_description(ai.status)]"))

                        _return = "failed"
                        store.mas_submod_utils.submod_log.error("label maica_mpostal_read: failed!")
                        break
                if ai.len_message_queue() == 0:
                    store.mas_ptod.write_command("Wait message...")
                    renpy.pause(1.0)
                    continue    
                message = ai.get_message()
                store.mas_submod_utils.submod_log.debug("label maica_mpostal_read::message:'{}', '{}'".format(message[0], message[1]))
                cur_postal["responsed_content"] = message[1]
                cur_postal["responsed_status"] = "received"
                _return = "success"   

            if cur_postal.get("failed_count", 0) >= 3:
                cur_postal["responsed_status"] = "fatal"
                cur_postal["responsed_content"] = renpy.substitute(_("无法回复信件, 因失败次数过多, 该信件将不会再回复"))
                store.mas_submod_utils.submod_log.error("label maica_mpostal_read: failed after 3 times!!!")
                break
            else:
                if "failed_count" not in cur_postal:
                    cur_postal["failed_count"] = 0
                cur_postal["failed_count"] += 1


label maica_mpostal_read.failed:
    call maica_hide_console
    if not persistent.maica_setting_dict.get("show_console_when_reply", False):
        window show
    $ mas_HKBRaiseShield()
    return _return
    

label maica_mpostal_show(content = "no content"):
    python:
        import time
        store._MP = MASPoem(
            poem_id = "mpostal_response_{}".format(time.time()),
            category = "mpostal",
            prompt = "mpostal",
            text = content,
        )
    call mas_showpoem(store._MP, "mod_assets/poem_assets/mail_maica_bg.png")
    return
        
label maica_mpostal_show_backtoscreen(content = "no content"):
    call maica_mpostal_show(content)
    return

label maica_mpostal_show_mpscreen:
    show screen maica_mpostals
    return

init 999 python:
    @store.mas_submod_utils.functionplugin("maica_mpostal_show_backtoscreen")
    def _backtompmenu():
        if not mas_inEVL("maica_mpostal_show_mpscreen") and not renpy.get_screen("maica_mpostals"):
            MASEventList.push("maica_mpostal_show_mpscreen")
        return

label show_workload:
    python hide:
        ai = store.maica.maica
        ai.console_logger.info("<DISABLE_VERBOSITY><MAICA LLM Server> Current Workload")
        data = ai.get_workload_lite()
        ai.console_logger.info("<DISABLE_VERBOSITY>VRAM " + maica.progress_bar(data["total_inuse_vmem"]  * 100 / data["total_vmem"], str(data["total_inuse_vmem"]) + "MiB" , str(data["total_vmem"]) + "MiB"))
        ai.console_logger.info("<DISABLE_VERBOSITY>UTIL " + maica.progress_bar(data["avg_usage"], str(data["avg_usage"] * 3600 / 100) + "TFlops"))
    return

