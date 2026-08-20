default return_code = None

init python:
    class ExtendSayer(object):
        def __init__(self):
            self._history = ""

        def say(self, text):
            if self._history:
                new_text = self._history + "{fast}" + text
                if len(_history_list):
                    _history_list.pop()
            else:
                new_text = text
            renpy.say(m, new_text)
            self._history += text

label maica_talking(mspire = False, prepared = False):
    $ return_code = None
    if not prepared:
        call maica_show_console
        call maica_init_connect(use_pause_instand_wait = True)
        if _return == "disconnected":
            $ return_code = "disconnected"
            jump maica_talking.end
    python:
        import time
        import copy
        from store.maica import maica_instance as ai
        import bot_interface
        import traceback
        ai.content_func = store.mas_ptod._update_console_history
        store.action = {}
        if mspire:
            ai.console_logger.info("<Function> MSpire init...")
            renpy.pause(2.3)
        printed = False
        is_retry_before_sendmessage = False
        question = False
        mspire_is_started = False # MSpire已开启开场白
        mspire_user_responsed = False # 玩家想继续ms

        extend_sayer = ExtendSayer()
label maica_talking.asking:
    python:
        while True:
            if is_retry_before_sendmessage:
                try:
                    ai.chat(is_retry_before_sendmessage)
                except Exception:
                    store.mas_submod_utils.submod_log.error("label maica_talking: retry request send failed: {}".format(traceback.format_exc()))
                    return_code = "disconnected"
                    break
                question = is_retry_before_sendmessage
                is_retry_before_sendmessage = False
            idle_emo = ai.MoodStatus.get_emote(True)
            store.mas_submod_utils.submod_log.debug("idle emo: {}".format(idle_emo))
            renpy.show("monika {}".format(idle_emo))
            if ai.is_ready_to_input():
                if mspire is False:
                    if "stop" in store.action:
                        if store.action["stop"]:
                            store.action = {}
                            return_code = "canceled"
                            break

                    question = mas_input(
                                _("Go on, [player]"),
                                default="",
                                length=75 if not config.language == "english" else 375,
                                screen="maica_input_screen"
                                #screen_kwargs={"use_return_button": True, "return_button_value": "nevermind", "return_button_prompt": _("I'm done")}
                            ).strip(' \t\n\r') #mas_input

                    if store.maica.maica_instance.input_lang_detect and not bot_interface.is_correct_lang(question, target_lang=store.maica.maica_instance.target_lang):
                        renpy.show_screen("maica_input_lang_warning")
                        continue
                    if question == "":
                        continue
                    if question == "nevermind":
                        return_code = "canceled"
                        ai.content_func = None
                        break
                    to_history = copy.deepcopy(_history_list[-1])
                    to_history.who = persistent.playername
                    to_history.what = question
                    _history_list.append(to_history)
                    try:
                        if store._maica_selected_visuals:
                            images = []
                            for item in store._maica_selected_visuals:
                                images.append(ai.generate_vista_url(item['uuid']))
                            ai.chat(question, images, session = None if not mspire_is_started else ai.mspire_session)
                            store._maica_selected_visuals = []
                        else:
                            ai.chat(question, session = None if not mspire_is_started else ai.mspire_session)
                    except Exception:
                        store.mas_submod_utils.submod_log.error("label maica_talking: request send failed: {}".format(traceback.format_exc()))
                        return_code = "disconnected"
                        break
                    is_retry_before_sendmessage = False
                else:
                    try:
                        ai.start_MSpire()
                    except Exception:
                        store.mas_submod_utils.submod_log.error("label maica_talking: MSpire request send failed: {}".format(traceback.format_exc()))
                        return_code = "disconnected"
                        break
                    mspire_is_started = True
            else:
                return_code = "disconnected"
                store.mas_submod_utils.submod_log.warning(
                    "label maica_talking: input loop stopped because the connection is not ready "
                    "(status={} / {})".format(ai.status, ai.get_status_description())
                )
                break


            start_time = time.time()
            start_token = ai.stat.get("received_token", 0)
            received_message = ""
            gen_time = 0
            while ai.is_responding() or ai.len_message_queue() > 0 :
                if ai.gen_time > gen_time:
                    gen_time = ai.gen_time

                store.mas_ptod.write_command("message_queue: {} | token: {} | time: {:.2f}".format(
                    ai.len_message_queue(), ai.stat.get("received_token", 0) - start_token,
                    gen_time
                    ))
                if ai.is_failed():
                    if ai.len_message_queue() == 0:
                        # This is already spoken at label .talking_start
                        # renpy.say(m, _("Something may went wrong..."))
                        return_code = "disconnected"
                        break
                if ai.len_message_queue() == 0:
                    #renpy.show(monika 1eua)
                    store.mas_ptod.write_command("Wait message...")
                    renpy.say(m, ".{w=0.3}.{w=0.3}.{w=0.3}{nw}")
                    if len(_history_list):
                        _history_list.pop()
                    continue
                message = ai.get_message()
                received_message += message[1]
                renpy.show(u"monika {}".format(message[0]))
                try:
                    is_extend = message[2] if len(message) >= 3 else False

                    if not is_extend:
                        extend_sayer = ExtendSayer()
                    extend_sayer.say(ai.prepare_message_for_renpy(message[1]))

                except Exception as e:
                    store.mas_submod_utils.submod_log.error("label maica_talking::renpy.say error:{}".format(traceback.format_exc()))
                    ai.console_logger.error("!!SUBMOD ERROR when chatting: {}".format(e))
            if ai.response_timed_out():
                # renpy.say(m, _("Something may went wrong..."))
                return_code = "disconnected"
            if return_code == "disconnected":
                break
            store.mas_submod_utils.submod_log.debug("label maica_talking::RESPONSE :'{}'".format(received_message))
            return_code = "mtrigger_triggering"

            # MTrigger callbacks can transfer control to Ren'Py labels.
            # Leave the Python loop so the script-level dispatcher can resume them.
            break

    if return_code == "mtrigger_triggering":
        # This means we're in "mtrigger processing status", not necessarily have any trigger.
        # So we ALWAYS enter this while main dialogues finished.

        call maica_run_mtriggers
        $ store.action = _return
        python:
            for quality_reasonable, quality_confidence in ai.consume_quality_statuses():
                store.maica_handle_quality_status(quality_reasonable, quality_confidence)
            ai.console_logger.debug("<chat_action> {}".format(store.action))

        if store.action['stop']:
            $ return_code = "canceled"
            jump maica_talking.end

        if not ai.is_connected() or not ai.is_ready_to_input():
            call maica_init_connect(use_pause_instand_wait = True)
            if _return == "disconnected":
                $ return_code = "disconnected"
                jump maica_talking.end

        if mspire:
            if ai.mspire_session == 0:
                $ afm_pref = renpy.game.preferences.afm_enable
                $ renpy.game.preferences.afm_enable = False
                $ return_code = "canceled"
                jump maica_talking.end
            else:
                $ mspire = False
                jump maica_talking.ask_mspire_continue

        $ return_code = None
        jump maica_talking.asking

    # store.mas_ptod.write_command()

    # store.mas_ptod._update_console_history([])

label maica_talking.end:
    call maica_hide_console
    if persistent.maica_setting_dict['console']:
        $ store.mas_ptod.clear_console()
    # if mspire_user_responsed:
    #     $ maica_apply_setting(True)
    return return_code
label maica_talking.ask_mspire_continue:
    m 1eub "Hmm...{w=0.3}shall we go further on this topic?{nw}"
    $ _history_list.pop()
    menu:
        "Hmm...shall we go further on this topic?{fast}"
        "Okay":
            $ mspire_user_responsed = True
            jump maica_talking.asking

        "Nevermind{#maica_host_nevermind}":
            $ return_code = "canceled"
            jump maica_talking.end
    return

label maica_run_mtriggers:
    python:
        renpy.dynamic("mtrigger_manager", "mtrigger_action", "mtrigger_step_action")
        # Ren'Py 6.99 requires every declared dynamic name to exist before return.
        mtrigger_manager = None
        mtrigger_action = {"stop": False}
        mtrigger_step_action = {"stop": False}
        mtrigger_manager = store.maica.maica_instance.mtrigger_manager
label .next:
    if not mtrigger_manager.has_triggered():
        return mtrigger_action
    $ mtrigger_step_action = {"stop": False}
    $ mtrigger_step_action = mtrigger_manager.run_trigger()
    if mtrigger_step_action.get("stop"):
        $ mtrigger_action["stop"] = True
        return mtrigger_action
    jump .next

label maica_show_console:
    if persistent.maica_setting_dict['console']:
        $ maica_enableWorkLoadScreen()
        show screen mas_py_console_teaching
        show monika at t22
    return
label maica_hide_console:
    if renpy.get_screen("mas_py_console_teaching") is not None:
        $ maica_disableWorkLoadScreen()
        hide screen mas_py_console_teaching
        if renpy.showing("monika"):
            show monika at t11
    return

label maica_pause_connection:
    python:
        ai = store.maica.maica_instance
        if ai.is_connected():
            ai.close_wss_session()
    return

label maica_reconnect:
    call maica_pause_connection
    call maica_init_connect(use_pause_instand_wait = True)
    return _return

label maica_mpostal_load:
    python:
        if mail_exist():
            import time
            _postals = find_mail_files()
            for item in _postals:
                postal = {
                    "raw_title": item["title"],
                    "raw_content": item["content"],
                    "raw_image": item.get("image"),
                    "mpostal_attachment_path": item.get("attachment_path"),
                    "vista_image_info":None,
                    "time": str(time.time()),
                    "responsed_content": "",
                    "responsed_status":"delaying",
                    "failed_count":0,
                }
                store.maica.prepare_mpostal_preview(postal)
                persistent._maica_send_or_received_mpostals.append(postal)
    return

label maica_init_connect(use_pause_instand_wait = False, force_welcome = False):
    python:
        maica_connect_result = None
        ai = store.maica.maica_instance
        ai.content_func = store.mas_ptod._update_console_history
        should_connect = not ai.is_connected() and not ai.is_connecting()
        should_show_welcome = (
            persistent.maica_setting_dict['console']
            and (force_welcome or should_connect)
        )
        if should_connect:
            ai.init_connect()
        if should_show_welcome:
            store.mas_ptod.clear_console()
            ai.send_to_outside_func(ai.ascii_icon)
            store.mas_ptod.write_command("Thank you for using MAICA Blessland!")
            renpy.pause(2.3)
        while True:
            if ai.is_failed():
                store.mas_submod_utils.submod_log.error(
                    "maica_init_connect failed: status={}, protocol_status={}, detail={}".format(
                        ai.status,
                        ai.error_protocol_status,
                        ai.error_message,
                    )
                )
                ai.send_to_outside_func(ai.get_status_description())
                renpy.pause(2.0)
                maica_connect_result = "disconnected"
                break
            if not ai.is_connected() or not ai.is_ready_to_input():
                if not ai.is_connected() and not ai.is_connecting():
                    ai.init_connect()
                store.mas_ptod.write_command("Init Connecting...")
                if use_pause_instand_wait:
                    renpy.pause(0.3, True)
                else:
                    renpy.say(m, ".{w=0.3}.{w=0.3}.{w=0.3}{nw}")
                    if len(_history_list):
                        _history_list.pop()
                continue
            if ai.is_ready_to_input():
                ai.send_mtrigger()
                store.mas_ptod.write_command("Login successful, ready to chat!")
                maica_connect_result = "success"
                break
    call show_workload
    return maica_connect_result

label maica_connect_from_settings:
    call maica_init_connect(use_pause_instand_wait = True)
    if _return == "disconnected":
        $ renpy.notify(renpy.substitute(_("MAICA: Connection failed: ")) + store.maica.maica_instance.get_status_description())
    else:
        $ renpy.notify(_("MAICA: Connection established"))
    return

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
        ai = store.maica.maica_instance
        import time
        import traceback
        pending_postals = [
            postal
            for postal in persistent._maica_send_or_received_mpostals
            if postal["responsed_status"] == "notupload"
        ]
        total_pending = len(pending_postals)
        for current_index, cur_postal in enumerate(pending_postals, 1):
            start_time = time.time()
            try:
                vista_info = cur_postal.get("vista_image_info") or {}
                uuid = vista_info.get("uuid")
                image_source = cur_postal.get("mpostal_attachment_path") or cur_postal.get("raw_image")
                if image_source:
                    if not uuid:
                        uuid = ai.vista_manager.upload(image_source)
                        cur_postal['vista_image_info'] = ai.vista_manager.get_info(uuid)
                ai.start_MPostal(cur_postal["raw_content"], title=cur_postal["raw_title"], visions = [ai.generate_vista_url(uuid)] if uuid else None)
            except Exception:
                cur_postal["responsed_status"] = "failed"
                cur_postal["failed_count"] = cur_postal.get("failed_count", 0) + 1
                _return = "failed"
                store.mas_submod_utils.submod_log.error("label maica_mpostal_read: request setup failed: {}".format(traceback.format_exc()))
                if cur_postal["failed_count"] >= 3:
                    cur_postal["responsed_status"] = "fatal"
                    cur_postal["responsed_content"] = renpy.substitute(_("Failed replying mail. Not retrying because failure count limit reached")) + "\n" + cur_postal["responsed_content"]
                    store.mas_submod_utils.submod_log.error("label maica_mpostal_read: retry limit reached for '{}'".format(cur_postal["raw_title"]))
                    break
                continue

            ai.console_logger.info("<Function> Processing mpostal {} ({}/{})".format(cur_postal["raw_title"], current_index, total_pending))
            cur_postal["responsed_status"] = "failed"
            gen_time = 0
            while ai.is_responding() or ai.len_message_queue() > 0 :
                if ai.gen_time > gen_time:
                    gen_time = ai.gen_time

                store.mas_ptod.write_command("time: {:.2f}".format(
                    gen_time
                    ))
                if ai.is_failed():
                    if ai.len_message_queue() == 0:
                        cur_postal["responsed_status"] = "failed"
                        cur_postal["responsed_content"] = cur_postal["responsed_content"] + renpy.substitute(_("Failed replying mail, check submod_log.log for details\nError code: [ai.status] | [ai.MaicaAiStatus.get_description(ai.status)]" + "\nt{}".format(time.time()))) + ("\n" if len(cur_postal["responsed_content"]) else "")

                        _return = "failed"
                        break
                if ai.len_message_queue() == 0:
                    store.mas_ptod.write_command("Wait message...")
                    renpy.pause(1.0)
                    continue
                message = ai.get_message()
                cur_postal["responsed_content"] = message[1]
                cur_postal["responsed_status"] = "received"
                _return = "success"

            if ai.response_timed_out():
                cur_postal["responsed_status"] = "failed"
                cur_postal["responsed_content"] += renpy.substitute(_("Failed replying mail, check submod_log.log for details\nError code: [ai.status] | [ai.MaicaAiStatus.get_description(ai.status)]"))
                _return = "failed"

            if _return == "success" and cur_postal["responsed_status"] == "received":
                store.maica.delete_mpostal_original(cur_postal)

            if _return != 'success':
                if cur_postal.get("failed_count", 0) >= 3:
                    cur_postal["responsed_status"] = "fatal"
                    cur_postal["responsed_content"] = renpy.substitute(_("Failed replying mail. Not retrying because failure count limit reached")) + "\n" +cur_postal["responsed_content"]
                    store.mas_submod_utils.submod_log.error("label maica_mpostal_read: retry limit reached for '{}'".format(cur_postal["raw_title"]))
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
            text = maica_escape_dialogue_text(content, interpolation_passes=2),
        )
    call mas_showpoem(store._MP, "mod_assets/poem_assets/mail_maica_bg.png")
    $ store.mas_poems.poem_map.pop(store._MP.poem_id, None)
    $ persistent._mas_poems_seen.pop(store._MP.poem_id, None)
    return

label maica_mpostal_show_backtoscreen(content = "no content"):
    # Hide the copied menu screens so the poem is shown over the game scene.
    hide screen maica_mpostals
    hide screen maica_setting
    hide screen maica_setting_tooltip
    hide screen submods
    with None
    call maica_mpostal_show(content)
    return

label _maica_return_game_menu(*args, **kwargs):
    call _enter_game_menu from _call__enter_game_menu_1

    if renpy.has_label("game_menu"):
        jump expression "game_menu"

    if renpy.has_screen("submods"):
        $ renpy.show_screen("submods")
        $ renpy.show_screen("maica_setting")
        # $ renpy.show_screen("maica_mpostals")
        $ ui.interact()
        jump _noisy_return

    jump expression "submods"

label maica_show_setting_screen:

    python:
        if not _windows_hidden:

            temp_space = {}
            _mas_game_menu_start(temp_space)

            renpy.call_in_new_context(
                "_maica_return_game_menu",
            )

            _mas_game_menu_end(temp_space)

    return
init 999 python:
    @store.mas_submod_utils.functionplugin("maica_call_from_setting")
    def _backtomenu():
        if not mas_inEVL("maica_show_setting_screen") and not renpy.get_screen("maica_setting"):
            MASEventList.push("maica_show_setting_screen")
        return

label show_workload:
    # python hide:
        # ai = store.maica.maica_instance
        # data = ai.get_workload_lite()
        # if data["total_inuse_vmem"] and data["total_vmem"] and data["avg_usage"]:
        #     ai.console_logger.info("<DISABLE_VERBOSITY><MAICA LLM Server> Current Workload ({} users online)".format(data["onliners"]))
        #     ai.console_logger.info("<DISABLE_VERBOSITY>VRAM " + maica.progress_bar(data["total_inuse_vmem"]  * 100 / data["total_vmem"], total=int(data["total_vmem"]), unit="MiB"))
        #     ai.console_logger.info("<DISABLE_VERBOSITY>UTIL " + maica.progress_bar(data["avg_usage"], total=int(data["max_tflops"]), unit="TFlops"))
        # else:
        #     ai.console_logger.debug("workload data not intact: '{}'".format(str(data)))
    return


init -1 python:

    # quick functions to enable disable the mouse tracker
    def maica_enableWorkLoadScreen():
        if not maica_isWorkLoadScreenVisible():
            config.overlay_screens.append("maica_workload_stat_lite")


    def maica_disableWorkLoadScreen():
        if maica_isWorkLoadScreenVisible():
            config.overlay_screens.remove("maica_workload_stat_lite")
            renpy.hide_screen("maica_workload_stat_lite")

    def maica_isWorkLoadScreenVisible():
        return "maica_workload_stat_lite" in config.overlay_screens
