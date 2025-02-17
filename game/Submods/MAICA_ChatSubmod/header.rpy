init -990 python:
    store.mas_submod_utils.Submod(
        author="P",
        name="MAICA Blessland",
        description=_("MAICA官方前端子模组"),
        version=maica_ver,
        settings_pane="maica_setting_pane",
    )
init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="MAICA Blessland",
            user_name="Mon1-innovation",
            repository_name="MAICA_ChatSubmod",
            update_dir="",
            attachment_id=None
        )

default persistent.maica_setting_dict = {
    "auto_reconnect":False,
    "maica_model":None,
    "use_custom_model_config":False,
    "sf_extraction":False,
    "chat_session":1,
    "console":True
}
default persistent.maica_advanced_setting = {}
default persistent.maica_advanced_setting_status = {}
default persistent.maica_player_additions_status = {}
default persistent.mas_player_additions = []
default persistent._maica_reseted = False

define maica_confont = "mod_assets/font/SarasaMonoTC-SemiBold.ttf"
#define "mod_assets/font/mplus-1mn-medium.ttf" # mas_ui.MONO_FONT
init 10 python:
    import logging
    maica_default_dict = {
        "auto_reconnect":False,
        "maica_model":store.maica.maica.MaicaAiModel.maica_main,
        "use_custom_model_config":False,
        "sf_extraction":True,
        "chat_session":1,
        "console":True,
        "console_font":maica_confont,
        "target_lang":store.maica.maica.MaicaAiLang.zh_cn if config.language == "chinese" else store.maica.maica.MaicaAiLang.en,
        "mspire_enable":True,
        "mspire_category":[],
        "mspire_interval":60,
        "mspire_search_type":"in_fuzzy_all",
        "mspire_session":0,
        "log_level":logging.DEBUG,
        "log_conlevel":logging.INFO,
        "provider_id":1 if not renpy.android else 2,
        "max_history_token":4096,
        "status_update_time":0.25,
        "strict_mode": False,
        "show_console_when_reply": False
    }
    import copy
    mdef_setting = copy.deepcopy(maica_default_dict)
    maica_advanced_setting = {
        "top_p":0.7,
        "temperature":0.2,
        "max_tokens":1600,
        "frequency_penalty":0.4,
        "presence_penalty":0.4,
        "seed":0.0,
        "mf_aggressive":False,
        "sfe_aggressive":False,
        "tnd_aggressive":1,
        "esc_aggressive":True,
        "nsfw_acceptive":True,
        "pre_additive":0,
        "post_additive":1,
        "amt_aggressive":True,
        "tz":None
    }
    maica_advanced_setting_status = {k: bool(v) for k, v in maica_advanced_setting.items()}
    maica_default_dict.update(persistent.maica_setting_dict)
    maica_advanced_setting.update(persistent.maica_advanced_setting)
    maica_advanced_setting_status.update(persistent.maica_advanced_setting_status)

    persistent.maica_setting_dict = maica_default_dict.copy()
    persistent.maica_advanced_setting = maica_advanced_setting.copy()
    persistent.maica_advanced_setting_status = maica_advanced_setting_status.copy()
    MaicaProviderManager = store.maica.maica.MaicaProviderManager

    _maica_LoginAcc = ""
    _maica_LoginPw = ""
    _maica_LoginEmail = ""
    def _maica_clear():
        store._maica_LoginAcc = ""
        store._maica_LoginPw = ""
        store._maica_LoginEmail = ""
        store.mas_api_keys.api_keys.update({"Maica_Token":store.maica.maica.ciphertext})
        store.mas_api_keys.save_keys()
    
    def maica_reset_setting():
        persistent.maica_setting_dict = mdef_setting.copy()

    def _maica_verify_token():
        res = store.maica.maica._verify_token()
        if res.get("success"):
            renpy.show_screen("maica_message", message=_("验证成功"))
        else:
            store.mas_api_keys.api_keys.update({"Maica_Token":""})
            store.maica.maica.ciphertext = ""
            renpy.show_screen("maica_message", message=renpy.substitute(_("验证失败, 请检查账号密码")) + "\n" + renpy.substitute(_("失败原因:")) + res.get("exception"))
            

    @store.mas_submod_utils.functionplugin("ch30_preloop")
    def upload_persistent_dict():
        maxlen = 1000
        import copy
        d = copy.deepcopy(persistent.__dict__)
        d['_seen_ever'].clear()
        d['_mas_event_init_lockdb'].clear()
        d['_changed'].clear()
        d['_mas_event_init_lockdb'].clear()
        d['event_database'].clear()
        d['farewell_database'].clear()
        d['greeting_database'].clear()
        d['_mas_apology_database'].clear()
        d['_mas_compliments_database'].clear()
        d['_mas_fun_facts_database'].clear()
        d['_mas_mood_database'].clear()
        d['_mas_songs_database'].clear()
        d['_mas_story_database'].clear()
        d['_mas_affection_backups'] = None
        d['greeting_database'].clear()
        d['greeting_database'].clear()
        d['greeting_database'].clear()
        d['greeting_database'].clear()
        d['greeting_database'].clear()
        d['greeting_database'].clear()
        d['greeting_database'].clear()
        d['mas_playername'] = store.player
        if persistent._mas_player_bday:
            d['mas_player_bday'] = [persistent._mas_player_bday.year, persistent._mas_player_bday.month, persistent._mas_player_bday.day]
        d['mas_affection'] = store._mas_getAffection()
        del d['_preferences']
        try:
            with open(os.path.normpath(os.path.join(maica.maica_basedir, "game", "Submods", "MAICA_ChatSubmod", "persistent_filter.json")), "r") as keys:
                sentiment = json.loads(keys.read())
        except:
            import json_exporter
            sentiment = json_exporter.persistent_filter

        keys_to_remove = []

        for i in d.keys():  # 使用 d.keys() 以兼容 Python 2
            if i not in sentiment:
                keys_to_remove.append(i)
                continue
            try:
                json.dumps(d[i])
                if len(d[i]) > maxlen:
                    d[i] = "REMOVED|TOO_LONG"
            except:
                try:
                    d[i] = str(d[i])
                    if len(d[i]) > maxlen:
                        d[i] = "REMOVED|TOO_LONG"
                except:
                    d[i] = "REMOVED"

        for key in keys_to_remove:
            del d[key]
        res = store.maica.maica.upload_save(d)
        if not res.get("success", False):
            store.mas_submod_utils.submod_log.info("ERROR: upload save failed: {}".format(res.get("exception", "unknown")))
        renpy.notify(_("MAICA: 存档上传成功") if res.get("success", False) else _("MAICA: 存档上传失败"))

    def reset_session():
        store.maica.maica.reset_chat_session()
        renpy.notify(_("MAICA: 会话已重置"))
    def output_chat_history():
        import json
        with open(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "chat_history.txt"), 'w') as f:
            f.write(json.dumps(store.maica.maica.get_history().get("history"), []))
        renpy.notify(_("MAICA: 历史已导出至game/Submods/MAICA_ChatSubmod/chat_history.txt"))
    
    def upload_chat_history():
        import json
        if not os.path.exists(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "chat_history.txt")):
            renpy.notify(_("MAICA: 未找到历史game/Submods/MAICA_ChatSubmod/chat_history.txt"))
            return
        with open(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "chat_history.txt"), 'r') as f:
            history = json.load(f)
        res = store.maica.maica.upload_history(history)
        renpy.notify(_("MAICA: 历史上传成功") if res.get("success", False) else _("MAICA: 历史上传失败, {}".format(res.get("exception", "未知错误"))))

    
    def maica_apply_setting(ininit=False):
        if persistent.maica_setting_dict["mspire_interval"] <= 10:
            persistent.maica_setting_dict["mspire_interval"] = 10
            
        store.maica.maica.auto_reconnect = persistent.maica_setting_dict["auto_reconnect"]
        if persistent.maica_setting_dict["use_custom_model_config"]:
            maica_apply_advanced_setting()
        else:
            store.maica.maica.modelconfig = {}
        store.maica.maica.sf_extraction = persistent.maica_setting_dict["sf_extraction"]
        store.maica.maica.chat_session = persistent.maica_setting_dict["chat_session"]
        store.maica.maica.model = persistent.maica_setting_dict["maica_model"]
        store.mas_ptod.font = persistent.maica_setting_dict["console_font"]
        store.maica.maica.target_lang = persistent.maica_setting_dict["target_lang"]
        store.maica.maica.mspire_category = persistent.maica_setting_dict["mspire_category"]
        store.maica.maica.mspire_type = persistent.maica_setting_dict["mspire_search_type"]
        store.mas_submod_utils.submod_log.level = persistent.maica_setting_dict["log_level"]
        store.maica.maica.console_logger.level = persistent.maica_setting_dict["log_conlevel"]
        store.maica.maica.mspire_session = 0#persistent.maica_setting_dict["mspire_session"]
        store.maica.maica.provider_id = persistent.maica_setting_dict["provider_id"]
        store.maica.maica.max_history_token = persistent.maica_setting_dict["max_history_token"]
        store.maica.maica.enable_strict_mode = persistent.maica_setting_dict["strict_mode"]
        store.persistent.maica_mtrigger_status = store.maica.maica.mtrigger_manager.output_settings()
        store.mas_submod_utils.getAndRunFunctions()
        if store.maica.maica.target_lang == store.maica.maica.MaicaAiLang.zh_cn:
            store.maica.maica.MoodStatus.emote_translate = {}
        elif store.maica.maica.target_lang == store.maica.maica.MaicaAiLang.en:
            try:
                with open(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "emotion_etz.json"), 'r') as f:
                    store.maica.maica.MoodStatus.emote_translate = json.load(f)
            except:
                import json_exporter
                store.maica.maica.MoodStatus.emote_translate = json_exporter.emotion_etz
        
        if not ininit:
            renpy.notify(_("MAICA: 已上传设置") if store.maica.maica.send_settings() else _("MAICA: 请等待连接就绪后手动上传"))
            
            
    
    def maica_apply_advanced_setting():
        settings_dict = {}
        for k, v in persistent.maica_advanced_setting_status.items():
            if v:
                settings_dict[k] = persistent.maica_advanced_setting[k]
        store.maica.maica.modelconfig.update(settings_dict)
        store.mas_submod_utils.submod_log.info("Applying advanced settings: {}".format(settings_dict))
            
    
    def change_chatsession():
        persistent.maica_setting_dict["chat_session"] += 1
        if persistent.maica_setting_dict["chat_session"] not in range(0, 10):
            persistent.maica_setting_dict["chat_session"] = 0
        
    def reset_player_information():
        persistent.mas_player_additions = []
    
    def export_player_information():
        with open(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "player_info.txt"), 'w') as f:
            f.write(json.dumps(persistent.mas_player_additions))
        renpy.notify("MAICA: 信息已导出至game/Submods/MAICA_ChatSubmod/player_information.txt")

    def update_model_setting(ininit = False):
        import os, json
        try:
            with open(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "custom_modelconfig.json"), "r") as f:
                store.maica.maica.modelconfig = json.load(f)
        except Exception as e:
            if not ininit:
                renpy.notify(_("MAICA: 加载高级参数失败, 查看submod_log.log获取详细原因").format(e))
            store.mas_submod_utils.submod_log.error("Failed to load custom model config: {}".format(e))
    
    def change_loglevel():
        import logging
        l = [logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        curr = l.index(persistent.maica_setting_dict["log_level"])
        persistent.maica_setting_dict["log_level"] = l[(curr + 1) % len(l)]
        store.mas_submod_utils.submod_log.level = persistent.maica_setting_dict["log_level"]

    def change_conloglevel():
        import logging
        l = [logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        curr = l.index(persistent.maica_setting_dict["log_conlevel"])
        persistent.maica_setting_dict["log_conlevel"] = l[(curr + 1) % len(l)]
        store.maica.maica.console_logger.level = persistent.maica_setting_dict["log_conlevel"]
    def try_eval(str):
        try:
            return eval(str)
        except Exception as e:
            store.mas_submod_utils.submod_log.error("Failed to eval: {}|param: '{}'".format(e, str))
            return None
    def log_eventstat():
        try:
            #hbox:
            #    text "Event status"
            #hbox:
            #    text "maica_greeting.conditional:[try_eval(mas_getEV('maica_greeting').conditional)]|seen:[renpy.seen_label('maica_greeting')]"
            #hbox:
            #    text "maica_chr2.conditional: [try_eval(mas_getEV('maica_chr2').conditional)]|seen:[renpy.seen_label('maica_chr2')]"
            #hbox:
            #    text "maica_chr_gone.conditional:[try_eval(mas_getEV('maica_chr_gone').conditional)]|seen:[renpy.seen_label('maica_chr_gone')]"
            #hbox:
            #    text "maica_chr_corrupted2.conditional:[try_eval(mas_getEV('maica_chr_corrupted2').conditional)]|seen:[renpy.seen_label('maica_chr_corrupted2')]"
            #hbox:
            #    text "maica_wants_preferences2.conditional: [try_eval(mas_getEV('maica_wants_preferences2').conditional)]|seen:[renpy.seen_label('maica_wants_preferences2')]"
            #hbox:
            #    text "maica_wants_mspire.conditional:[try_eval(mas_getEV('maica_wants_mspire').conditional)]|seen:[renpy.seen_label('maica_wants_mspire')]"
            #hbox:
            #    text "maica_mspire.conditional:[try_eval(mas_getEV('maica_mspire').conditional)]|seen:[renpy.seen_label('maica_mspire')]"
            #hbox:
            #    text "maica_mspire.last_seen:[evhand.event_database.get('maica_mspire',None).last_seen]"
            #hbox:
            #    text "=====MaicaAi() Finish====="

            def get_conditional(name):
                try:
                    if mas_getEV(name):
                        return mas_getEV(name).conditional
                except Exception as e:
                    store.mas_submod_utils.submod_log.error("Failed to get conditional: {}".format(e))
                    return None
            store.mas_submod_utils.submod_log.info("maica_greeting.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_greeting')), renpy.seen_label('maica_greeting')))
            store.mas_submod_utils.submod_log.info("maica_chr2.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_chr2')), renpy.seen_label('maica_chr2')))
            store.mas_submod_utils.submod_log.info("maica_chr_gone.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_chr_gone')), renpy.seen_label('maica_chr_gone')))
            store.mas_submod_utils.submod_log.info("maica_chr_corrupted2.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_chr_corrupted2')), renpy.seen_label('maica_chr_corrupted2')))
            store.mas_submod_utils.submod_log.info("maica_wants_preferences2.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_wants_preferences2')), renpy.seen_label('maica_wants_preferences2')))
            store.mas_submod_utils.submod_log.info("maica_wants_mspire.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_wants_mspire')), renpy.seen_label('maica_wants_mspire')))
            store.mas_submod_utils.submod_log.info("maica_mspire.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_mspire')), renpy.seen_label('maica_mspire')))
            store.mas_submod_utils.submod_log.info("maica_mspire.last_seen:{}".format(evhand.event_database.get('maica_mspire',None).last_seen))
            store.mas_submod_utils.submod_log.info("maica_wants_mpostal.conditional:{}|seen: {}".format(try_eval(get_conditional('maica_wants_mpostal')), renpy.seen_label('maica_wants_mpostal')) )



        except Exception as e:
            store.mas_submod_utils.submod_log.error("Failed to get event stat: {}".format(e))

    maica_apply_setting(True)
        

init python:
    def scr_nullfunc():
        return            

screen maica_setting_pane():
    python:
        import store.maica as maica
        stat = _("未连接") if not maica.maica.wss_session else _("已连接") if maica.maica.is_connected() else _("已断开")
        store.maica.maica.ciphertext = store.mas_getAPIKey("Maica_Token")
        log_hasupdate = persistent._maica_updatelog_version_seen < store.maica.update_info.get("version", 0)


    vbox:
        xmaximum 800
        xfill True
        style_prefix "check"

        timer persistent.maica_setting_dict.get('status_update_time', 1.0) repeat True action Function(scr_nullfunc, _update_screens=True)
        
        if get_build_timescamp() < cn_mas_mobile_min_timescamp and renpy.android:
            text _("> 你当前的MAS生成版本过旧, 可能影响正常运行, 请升级至最新生成版本"):
                xalign 1.0 yalign 0.0
                xoffset -10
                style "main_menu_version"
        if store.maica.maica.is_outdated is None:
            text _("> 无法验证版本号, 如果出现问题请更新至最新版"):
                xalign 1.0 yalign 0.0
                xoffset -10
                style "main_menu_version"
        elif store.maica.maica.is_outdated is True:
            text _("> 当前版本已不再支持, 请更新至最新版"):
                xalign 1.0 yalign 0.0
                xoffset -10
                style "main_menu_version"

        if store.mas_submod_utils.isSubmodInstalled("Better Loading"):
            text _("> 警告: 与 Better Loading 不兼容"):
                xalign 1.0 yalign 0.0
                xoffset -10
                style "main_menu_version"
        if store.mas_submod_utils.isSubmodInstalled("Log Screen"):
            text _("> 警告: 与 Log Screen 一起使用时, 请将'submod_log'的详细程度提高至info及以上"):
                xalign 1.0 yalign 0.0
                xoffset -10
                style "main_menu_version"
        text _("> MAICA通信状态: [maica.maica.status]|[maica.maica.MaicaAiStatus.get_description(maica.maica.status)]"):
            xalign 1.0 yalign 0.0
            xoffset -10
            style "main_menu_version"

        text renpy.substitute(_("> Websocket:")) + renpy.substitute(stat):
            xalign 1.0 yalign 0.0
            xoffset -10
            style "main_menu_version"
        if not maica.maica.is_accessable():
            textbutton _("> 生成令牌")  
        elif not maica.maica.is_connected():
            textbutton _("> 生成令牌"):
                action Show("maica_login")
            
        if maica.maica.has_token() and not maica.maica.is_connected():
            textbutton _("> 使用已保存令牌连接"):
                action Function(store.maica.maica.init_connect)

            
        elif maica.maica.is_connected():
            if maica.maica.is_ready_to_input():
                textbutton _("> 手动上传设置"):
                    action Function(maica_apply_setting)
            else:
                textbutton _("> 手动上传设置 [[请先使MAICA完成连接]")
                    

            textbutton _("> 重置当前对话"):
                action Function(reset_session)

            textbutton _("> 导出当前对话"):
                action Function(output_chat_history)
            
            textbutton _("> 上传对话历史到会话 '[store.maica.maica.chat_session]'"):
                action Function(upload_chat_history)

            textbutton renpy.substitute(_("> 退出当前DCC账号")) + " " + renpy.substitute(_("{size=-10}* 如果对话卡住了, 点我断开连接")):
                action Function(store.maica.maica.close_wss_session)

        else:
            textbutton _("> 使用已保存令牌连接")
    
        textbutton _("> MAICA对话设置 {size=-10}*部分选项重新连接生效"):
            action Show("maica_setting")
        
        if log_hasupdate:
            textbutton _("> 更新日志与服务状态 {size=-10}*有新更新"):
                action Show("maica_log")
        else:
            textbutton _("> 更新日志与服务状态"):
                action Show("maica_log")

screen maica_node_setting():
    python:
        submods_screen = store.renpy.get_screen("submods", "screens")

        if submods_screen:
            _tooltip = submods_screen.scope.get("tooltip", None)
        else:
            _tooltip = None
        def set_provider(id):
            persistent.maica_setting_dict["provider_id"] = id

    modal True
    zorder 215
    
    style_prefix "check"

    frame:
        vbox:
            xmaximum 1100
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 600
                xmaximum 1100
                xfill True
                yfill False
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1100
                    xfill True
                    yfill False



                    for provider in MaicaProviderManager.servers:
                        text str(provider.get('id')) + ' | ' + provider.get('name')
                        

                        hbox:
                            text renpy.substitute(_("设备: ")) + provider.get('deviceName', 'Device not provided')
                        hbox:
                            text renpy.substitute(_("当前模型: ")) + provider.get('servingModel', 'No model provided')


                        hbox:
                            textbutton _("> 使用该节点"):
                                action [
                                    Function(set_provider, provider.get('id')),
                                    Hide("maica_node_setting")
                                ]
                            
                            if provider.get("isOfficial", False):
                                textbutton _(" √ MAICA 官方服务器")
                    
                    hbox:
                        textbutton _("更新节点列表"):
                            style_prefix "confirm"
                            action Function(store.maica.maica.MaicaProviderManager.get_provider)

                        textbutton _("关闭"):
                            style_prefix "confirm"
                            action Hide("maica_node_setting")

screen maica_triggers():
    python:
        submods_screen = store.renpy.get_screen("submods", "screens")
        maica_triggers = store.maica.maica.mtrigger_manager
        if submods_screen:
            _tooltip = submods_screen.scope.get("tooltip", None)
        else:
            _tooltip = None

    modal True
    zorder 215
    
    style_prefix "check"

    frame:
        vbox:
            xmaximum 1100
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 600
                xmaximum 1100
                xfill True
                yfill False
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1100
                    xfill True
                    yfill False

                    text _("MTrigger空间使用情况: ")
                    text "request: " + str(maica_triggers.get_length(0)) + " / " + str(maica_triggers.MAX_LENGTH_REQUEST):
                        color ("#FF0000" if maica_triggers.get_length(0) > maica_triggers.MAX_LENGTH_REQUEST * 0.75 else gui.interface_text_color)
                    text "table: " + str(maica_triggers.get_length(1)) + " / " + str(maica_triggers.MAX_LENGTH_TABLE):
                        color ("#FF0000" if maica_triggers.get_length(1) > maica_triggers.MAX_LENGTH_TABLE * 0.9 else gui.interface_text_color)
                    if maica_triggers.get_length(0) > maica_triggers.MAX_LENGTH_REQUEST * 0.75 or maica_triggers.get_length(1) > maica_triggers.MAX_LENGTH_TABLE * 0.9:
                        text _("> 注意: 当空间不足时将自动关闭部分MTrigger!"):
                            color "#ff0000"
                            size 15

                    for trigger in maica_triggers.triggers:
                        label trigger.name
                        if not maica_triggers.trigger_status(trigger.name) or not trigger.condition():
                            hbox:
                                text _("空间占用: -"):
                                    size 15
                        elif trigger.method == 0:
                            hbox:
                                text _("空间占用: request"):
                                    size 15
                                text str(len(trigger)):
                                    size 15
                        elif trigger.method == 1:
                            hbox:
                                text _("空间占用: table"):
                                    size 15
                                text str(len(trigger)):
                                    size 15
                        text trigger.description:
                            size 15
                        
                        
                        
                        hbox:
                            if maica_triggers.trigger_status(trigger.name):
                                textbutton _("√ 已启用"):
                                    action Function(maica_triggers.disable_trigger, trigger.name)
                                    selected maica_triggers.trigger_status(trigger.name)
                            else:
                                textbutton _("× 已禁用"):
                                    action Function(maica_triggers.enable_trigger, trigger.name)
                                    selected maica_triggers.trigger_status(trigger.name)
                            
                            if not trigger.condition():
                                textbutton _("※ 当前不满足触发条件")

            hbox:
                style_prefix "confirm"
                textbutton _("关闭"):
                    action Hide("maica_triggers")

screen maica_mpostals():
    python:
        import time
        submods_screen = store.renpy.get_screen("submods", "screens")
        maica_triggers = store.maica.maica.mtrigger_manager
        preview_len = 200
        if submods_screen:
            _tooltip = submods_screen.scope.get("tooltip", None)
        else:
            _tooltip = None

        def _delect_portal(title):
            for item in persistent._maica_send_or_received_mpostals:
                if title == item["raw_title"]:
                    persistent._maica_send_or_received_mpostals.remove(item)
                    break

    modal True
    zorder 215
    
    style_prefix "check"

    frame:
        vbox:
            xmaximum 1100
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 600
                xmaximum 1100
                xfill True
                yfill False
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1100
                    xfill True
                    yfill False
                    hbox:
                        textbutton _("{size=15}因能力有限, 阅读信件后信件列表将在返回太空教室后重新显示.")
                            

                    hbox:
                        text ""
                    for postal in persistent._maica_send_or_received_mpostals:
                        label postal["raw_title"]
                        text renpy.substitute(_("信件状态: ")) + postal["responsed_status"]:
                            size 10                       
                        text renpy.substitute(_("寄信时间: ")) + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(postal["time"][:-3]))):
                            size 10
                        text renpy.substitute(_("\n[player]: \n")) + postal["raw_content"][:preview_len].replace("\n", "") + ("..." if len(postal["raw_content"]) > preview_len else  "") + "\n":
                            size 15
                        if postal["responsed_content"] != "":
                            text renpy.substitute(_("[m_name]: \n")) + postal["responsed_content"][:preview_len].replace("\n", "")  + ("..." if len(postal["responsed_content"]) > preview_len else  ""):
                                size 15
                        hbox:
                            textbutton _("阅读[player]写的信"):
                                action [
                                        Hide("maica_mpostals"),
                                        Hide("maica_setting"),
                                        Function(store.maica_apply_setting),
                                        Function(renpy.call, "maica_mpostal_show_backtoscreen", content = postal["raw_content"])
                                ]
                            if postal["responsed_content"] != "":
                                textbutton _("阅读[m_name]的回信"):
                                    action [
                                            Hide("maica_mpostals"),
                                            Hide("maica_setting"),
                                            Function(store.maica_apply_setting),
                                            Function(renpy.call, "maica_mpostal_show_backtoscreen", content = postal["responsed_content"])
                                    ]
                            
                            if postal["responsed_status"] in ("fatal"):
                                textbutton _("重新寄信"):
                                    action SetDict(postal, "responsed_status", "delaying")
                            hbox:
                                textbutton _("删除"):
                                    action Function(_delect_portal, postal["raw_title"])
                            
            hbox:
                style_prefix "confirm"
                textbutton _("关闭"):
                    action Hide("maica_mpostals")

screen maica_workload_stat():
    python:
        submods_screen = store.renpy.get_screen("submods", "screens")
        stat = store.maica.maica.workload_raw
        if submods_screen:
            _tooltip = submods_screen.scope.get("tooltip", None)
        else:
            _tooltip = None
        store.update_interval = 15
        def check_and_update(use_none = False):
            import time
            last = store.maica.last_workload_update + update_interval - time.time()
            if last < 0:
                store.maica.last_workload_update = time.time()
                store.maica.maica.update_workload()
            return last if not use_none else None # 返回的是剩余时间

    modal True
    zorder 215
    
    style_prefix "check"

    frame:
        vbox:
            xmaximum 1100
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 600
                xmaximum 1100
                xfill True
                yfill False
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1100
                    xfill True
                    yfill False

                    for server in stat:
                        text server:
                            size 20
                        text "========================================"
                        for card in stat[server]:
                            hbox:
                                text stat[server][card]["name"]:
                                    size 15
                                text store.maica.progress_bar(stat[server][card]["mean_utilization"]):
                                    size 10
                                    #font maica_confont

                                text "VRAM: " + str(stat[server][card]["mean_memory"]) + " / " + str(stat[server][card]["vram"]):
                                    size 10
                                text renpy.substitute(_("平均功耗: ")) + str(stat[server][card]["mean_consumption"]) + "W":
                                    size 10
                        text ""

            hbox:
                text renpy.substitute(_("下次更新数据")) + store.maica.progress_bar(((check_and_update() / store.update_interval)) * 100, bar_length = 90):
                    size 15
                timer 0.15 repeat True action Function(check_and_update, use_none = True)

            hbox:
                textbutton _("关闭"):
                    style_prefix "confirm"
                    action Hide("maica_workload_stat") 


screen maica_log():
    python:
        submods_screen = store.renpy.get_screen("submods", "screens")
        maica_log = store.maica.update_info
        persistent._maica_updatelog_version_seen = maica_log.get("version", persistent._maica_updatelog_version_seen)
        if submods_screen:
            _tooltip = submods_screen.scope.get("tooltip", None)
        else:
            _tooltip = None
        def set_provider(id):
            persistent.maica_setting_dict["provider_id"] = id

    modal True
    zorder 215
    
    style_prefix "check"

    frame:
        vbox:
            xmaximum 1100
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 600
                xmaximum 1100
                xfill True
                yfill False
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1100
                    xfill True
                    yfill False

                    text maica_log.get("title")

                    text "========================================================="
                    for content in maica_log.get("content"):
                        text content:
                            size 18
                        text "================================"
            hbox:
                textbutton _("关闭"):
                    style_prefix "confirm"
                    action Hide("maica_log")

screen maica_tz_setting():
    python:
        submods_screen = store.renpy.get_screen("submods", "screens")
        if submods_screen:
            _tooltip = submods_screen.scope.get("tooltip", None)
        else:
            _tooltip = None

        def get_gmt_offset_timezone():
            import time
            # 获取当前本地时间的 UTC 偏移量（以秒为单位）
            if time.localtime().tm_isdst:
                offset_sec = -time.altzone
            else:
                offset_sec = -time.timezone

            # 将偏移量转换为小时
            offset_hours = offset_sec // 3600

            # 生成 Etc/GMT± 的时区名称
            if offset_hours == 0:
                return "Etc/GMT"
            elif offset_hours > 0:
                return "Etc/GMT-{}".format(offset_hours)
            else:
                return "Etc/GMT+{}".format(-offset_hours)

        current_tz = get_gmt_offset_timezone()

    modal True
    zorder 215
    
    style_prefix "check"

    frame:
        vbox:
            xmaximum 1100
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 600
                xmaximum 1100
                xfill True
                yfill False
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1100
                    xfill True
                    yfill False
                    text _("{size=-10}如果这里没有你的时区, 请根据你当地的UTC时间选择")

                    hbox:
                        textbutton _("根据语言自动选择"):
                            action SetDict(persistent.maica_advanced_setting, "tz", None)
                    
                    hbox:
                        textbutton _("根据系统时区自动选择"):
                            action SetDict(persistent.maica_advanced_setting, "tz", current_tz)

                    hbox:
                        textbutton "UTC-12|Etc/GMT+12":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Etc/GMT+12")

                    hbox:
                        textbutton "UTC-11|Pacific/Midway":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Pacific/Midway")

                    hbox:
                        textbutton "UTC-10|Pacific/Honolulu":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Pacific/Honolulu")

                    hbox:
                        textbutton "UTC-9|America/Anchorage":
                            action SetDict(persistent.maica_advanced_setting, "tz", "America/Anchorage")

                    hbox:
                        textbutton "UTC-8|America/Los_Angeles":
                            action SetDict(persistent.maica_advanced_setting, "tz", "America/Los_Angeles")

                    hbox:
                        textbutton "UTC-7|America/Denver":
                            action SetDict(persistent.maica_advanced_setting, "tz", "America/Denver")

                    hbox:
                        textbutton "UTC-6|America/Chicago":
                            action SetDict(persistent.maica_advanced_setting, "tz", "America/Chicago")

                    hbox:
                        textbutton "UTC-5|America/New_York":
                            action SetDict(persistent.maica_advanced_setting, "tz", "America/New_York")

                    hbox:
                        textbutton "UTC-4|America/Santiago":
                            action SetDict(persistent.maica_advanced_setting, "tz", "America/Santiago")

                    hbox:
                        textbutton "UTC-3|America/Argentina/Buenos_Aires":
                            action SetDict(persistent.maica_advanced_setting, "tz", "America/Argentina/Buenos_Aires")

                    hbox:
                        textbutton "UTC-2|Atlantic/South_Georgia":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Atlantic/South_Georgia")

                    hbox:
                        textbutton "UTC-1|Atlantic/Azores":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Atlantic/Azores")

                    hbox:
                        textbutton "UTC+0|Europe/London":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Europe/London")

                    hbox:
                        textbutton "UTC+1|Europe/Berlin":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Europe/Berlin")

                    hbox:
                        textbutton "UTC+2|Europe/Kaliningrad":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Europe/Kaliningrad")

                    hbox:
                        textbutton "UTC+3|Europe/Moscow":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Europe/Moscow")

                    hbox:
                        textbutton "UTC+4|Asia/Dubai":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Asia/Dubai")

                    hbox:
                        textbutton "UTC+5|Asia/Karachi":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Asia/Karachi")

                    hbox:
                        textbutton "UTC+6|Asia/Dhaka":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Asia/Dhaka")

                    hbox:
                        textbutton "UTC+7|Asia/Bangkok":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Asia/Bangkok")

                    hbox:
                        textbutton "UTC+8|Asia/Shanghai":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Asia/Shanghai")

                    hbox:
                        textbutton "UTC+9|Asia/Tokyo":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Asia/Tokyo")

                    hbox:
                        textbutton "UTC+10|Australia/Sydney":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Australia/Sydney")

                    hbox:
                        textbutton "UTC+11|Pacific/Noumea":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Pacific/Noumea")

                    hbox:
                        textbutton "UTC+12|Pacific/Auckland":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Pacific/Auckland")

                    hbox:
                        textbutton "UTC+13|Pacific/Tongatapu":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Pacific/Tongatapu")

                    hbox:
                        textbutton "UTC+14|Pacific/Kiritimati":
                            action SetDict(persistent.maica_advanced_setting, "tz", "Pacific/Kiritimati")
            hbox:
                textbutton _("关闭"):
                    style_prefix "confirm"
                    action Hide("maica_tz_setting")


screen maica_advance_setting():
    python:
        submods_screen = store.renpy.get_screen("submods", "screens")

        if submods_screen:
            _tooltip = submods_screen.scope.get("tooltip", None)
        else:
            _tooltip = None
    modal True
    zorder 215
    
    style_prefix "check"

    frame:
        vbox:
            xmaximum 1100
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 600
                xmaximum 1100
                xfill True
                yfill False
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1100
                    xfill True
                    yfill False
                    hbox:
                        text _("{a=https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Document.txt}{i}{u}MAICA 官方文档{/i}{/u}{/a}")
                    hbox:
                        text _("{a=https://www.openaidoc.com.cn/api-reference/chat}{i}{u}OPENAI 中文文档{/i}{/u}{/a}")
                    hbox:
                        text _("{size=-10}注意: 只有已被勾选(标记了X)的高级设置才会被使用, 未使用的设置将使用服务端的默认设置")
                    hbox:
                        if not persistent.maica_setting_dict.get('use_custom_model_config'):
                            text _("{size=-10}你当前未启用'使用高级参数', 该页的所有设置都不会生效!")

                    hbox:
                        text ""
                    hbox:
                        text _("{size=-10}================超参数================")

                    hbox:
                        textbutton "top_p":
                            action ToggleDict(persistent.maica_advanced_setting_status, "top_p")
                            hovered SetField(_tooltip, "value", _("模型选择的范围, 模型考虑概率质量值在前 top_p 的标记的结果, 因此，0.1 意味着仅考虑概率质量值前 10% 的标记"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        if persistent.maica_advanced_setting_status.get("top_p", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "top_p", 0.9, step=0.01,offset=0.1 ,style="slider")
                                xsize 200
                            
                            textbutton "[persistent.maica_advanced_setting.get('top_p', 'None')]"

                    hbox:
                        textbutton "temperature":
                            action ToggleDict(persistent.maica_advanced_setting_status, "temperature")
                            hovered SetField(_tooltip, "value", _("模型输出的随机性, 较高的值会使输出更随机, 而较低的值则会使其更加专注和确定"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        if persistent.maica_advanced_setting_status.get("temperature", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "temperature", 1.0, step=0.01,offset=0 ,style="slider")
                                xsize 200
                            textbutton "[persistent.maica_advanced_setting.get('temperature', 'None')]"
                    
                    hbox:
                        textbutton "max_tokens":
                            action ToggleDict(persistent.maica_advanced_setting_status, "max_tokens")
                            hovered SetField(_tooltip, "value", _("模型输出的长度限制, 较高的值会使输出更长"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        if persistent.maica_advanced_setting_status.get("max_tokens", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "max_tokens", 2048, step=1,offset=0 ,style="slider")
                                xsize 200
                            textbutton "[persistent.maica_advanced_setting.get('max_tokens', 'None')]"
                    
                    hbox:
                        textbutton "frequency_penalty":
                            action ToggleDict(persistent.maica_advanced_setting_status, "frequency_penalty")
                            hovered SetField(_tooltip, "value", _("频率惩罚, 正值基于新标记在文本中的现有频率对其进行惩罚, 降低模型重复相同行的可能性"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        if persistent.maica_advanced_setting_status.get("frequency_penalty", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "frequency_penalty", 1.0, step=0.01,offset=0 ,style="slider")
                                xsize 200
                            textbutton "[persistent.maica_advanced_setting.get('frequency_penalty', 'None')]"
                    
                    hbox:
                        textbutton "presence_penalty":
                            action ToggleDict(persistent.maica_advanced_setting_status, "presence_penalty")
                            hovered SetField(_tooltip, "value", _("重现惩罚, 正值基于新标记出现在文本中的情况对其进行惩罚, 增加模型谈论新话题的可能性"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        if persistent.maica_advanced_setting_status.get("presence_penalty", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "presence_penalty", 1.0, step=0.01,offset=0 ,style="slider")
                                xsize 200
                            textbutton "[persistent.maica_advanced_setting.get('presence_penalty', 'None')]"
 
                    hbox:
                        textbutton "seed":
                            action ToggleDict(persistent.maica_advanced_setting_status, "seed")
                        
                        if persistent.maica_advanced_setting_status.get("seed", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "seed", 998, step=1,offset=1 ,style="slider")
                                xsize 600
                            textbutton "[persistent.maica_advanced_setting.get('seed', 'None')]"

                    hbox:
                        text _("{size=-10}================偏好================")

                    hbox:
                        textbutton "tnd_aggressive":
                            action ToggleDict(persistent.maica_advanced_setting_status, "tnd_aggressive")
                            hovered SetField(_tooltip, "value", _("当其为0时只调用MFocus直接选择的工具. 为1时总是会调用时间与节日工具. 为2时还会额外调用日期工具.\n当其为2且mas_geolocation存在时, tnd_aggressive还会额外调用当前天气工具.\n越高越可能补偿MFocus命中率低下的问题, 但也越可能会干扰模型对部分问题的判断."))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        if persistent.maica_advanced_setting_status.get("tnd_aggressive", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "tnd_aggressive", 2, step=1,offset=0 ,style="slider")
                                xsize 100
                            textbutton "[persistent.maica_advanced_setting.get('tnd_aggressive', 'None')]"
                    hbox:
                        textbutton "mf_aggressive:[persistent.maica_advanced_setting.get('mf_aggressive', 'None')]":
                            action [ToggleDict(persistent.maica_advanced_setting_status, "mf_aggressive"),
                                ToggleDict(persistent.maica_advanced_setting, "mf_aggressive")]
                            hovered SetField(_tooltip, "value", _("总是尽可能使用MFocus的最终输出替代指导构型信息.\n启用可能提升模型的复杂信息梳理能力, 但也可能会造成速度下降或专注扰乱"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        textbutton "sfe_aggressive:[persistent.maica_advanced_setting.get('sfe_aggressive', 'None')]":
                            action [ToggleDict(persistent.maica_advanced_setting_status, "sfe_aggressive"),
                                ToggleDict(persistent.maica_advanced_setting, "sfe_aggressive")]
                            hovered SetField(_tooltip, "value", _("总是以用户的真名替代prompt中的[[player]字段.\n启用此功能可能有利于模型理解玩家的姓名, 但也可能会造成总体拟合能力的下降和信息编造"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        textbutton "esc_aggressive:[persistent.maica_advanced_setting.get('esc_aggressive', 'None')]":
                            action [ToggleDict(persistent.maica_advanced_setting_status, "esc_aggressive"),
                                ToggleDict(persistent.maica_advanced_setting, "esc_aggressive")]
                            hovered SetField(_tooltip, "value", _("调用agent模型对MFocus联网搜集的信息整理一次.\n启用此功能会改善模型对联网检索信息的专注能力, 但也会降低涉及联网搜索query的响应速度."))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        textbutton "amt_aggressive: [persistent.maica_advanced_setting.get('amt_aggressive', 'None')]":
                            action [ToggleDict(persistent.maica_advanced_setting_status, "amt_aggressive"),
                                ToggleDict(persistent.maica_advanced_setting, "amt_aggressive")]
                            hovered SetField(_tooltip, "value", _("要求MFocus预检MTrigger内容(若存在), 以告知核心模型要求是否可以完成. \n启用此功能会改善MTrigger与核心模型的表现失步问题, 但也会降低涉及MTrigger对话的响应速度.\n当对话未使用MTrigger或仅有好感触发器, 此功能不会生效."))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        textbutton "nsfw_acceptive:[persistent.maica_advanced_setting.get('nsfw_acceptive', 'None')]":
                            action [ToggleDict(persistent.maica_advanced_setting_status, "nsfw_acceptive"),
                                ToggleDict(persistent.maica_advanced_setting, "nsfw_acceptive")]
                            hovered SetField(_tooltip, "value", _("改变system指引, 使模型对NSFW场景更为宽容.\n经测试启用此功能对模型总体表现(意外地)有利, 但也存在降低模型专注能力和造成混乱的风险."))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        textbutton "pre_additive":
                            action ToggleDict(persistent.maica_advanced_setting_status, "pre_additive")
                            hovered SetField(_tooltip, "value", _("相当于pre_additive数值轮次的历史对话将被加入MFocus.\n此功能强度越高, 越可能提高MFocus在自然对话中的触发率, 但也越可能干扰MFocus的判断或导致其表现异常."))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        if persistent.maica_advanced_setting_status.get("pre_additive", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "pre_additive", 5, step=1,offset=0 ,style="slider")
                                xsize 50
                            textbutton "[persistent.maica_advanced_setting.get('pre_additive', 'None')]"

                        textbutton "post_additive":
                            action ToggleDict(persistent.maica_advanced_setting_status, "post_additive")
                            hovered SetField(_tooltip, "value", _("相当于post_additive数值轮次的历史对话将被加入MTrigger.\n此功能强度越高, 越可能提高MTrigger在自然对话中的触发率, 但也越可能干扰MTrigger的判断或导致其表现异常."))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        if persistent.maica_advanced_setting_status.get("post_additive", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "post_additive", 5, step=1,offset=0 ,style="slider")
                                xsize 50
                            textbutton "[persistent.maica_advanced_setting.get('post_additive', 'None')]"

                    hbox:      
                        textbutton _("选择时区: [persistent.maica_advanced_setting.get('tz') or 'Asia/Shanghai' if store.maica.maica.target_lang == store.maica.maica.MaicaAiLang.zh_cn else 'America/Indiana/Vincennes']"):
                            action Show("maica_tz_setting")





                    
            hbox:
                style_prefix "confirm"
                textbutton _("保存设置"):
                    action [
                        Function(maica_apply_advanced_setting),
                        Hide("maica_advance_setting")
                    ]
                        
                        
            
screen maica_setting():
    python:
        submods_screen = store.renpy.get_screen("submods", "screens")

        if submods_screen:
            _tooltip = submods_screen.scope.get("tooltip", None)
        else:
            _tooltip = None
        store.len = len
        
    modal True
    zorder 215
    
    style_prefix "check"

    frame:
        vbox:
            xmaximum 1100
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 600
                xmaximum 1100
                xfill True
                yfill False
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1100
                    xfill True
                    yfill False
                    if renpy.config.debug:
                        hbox:
                            text "=====MaicaAi()====="
                        hbox:
                            text "ai.is_responding: [store.maica.maica.is_responding()]":
                                size 15
                        hbox:
                            text "ai.is_failed: [store.maica.maica.is_failed()]":
                                size 15
                        hbox:
                            text "ai.is_connected: [store.maica.maica.is_connected()]":
                                size 15
                        hbox:
                            text "ai.is_ready_to_input: [store.maica.maica.is_ready_to_input()]":
                                size 15
                        hbox:
                            text "ai.MaicaAiStatus.is_submod_exception: [store.maica.maica.MaicaAiStatus.is_submod_exception(store.maica.maica.status)]":
                                size 15
                        hbox:
                            text "ai.len_message_queue(): [store.maica.maica.len_message_queue()]":
                                size 15
                        hbox:
                            text "maica_chr_exist: [maica_chr_exist]":
                                size 15
                        hbox:
                            text "maica_chr_changed: [maica_chr_changed]":
                                size 15
                        hbox:
                            text "len(mas_rev_unseen): [len(mas_rev_unseen)] | [mas_rev_unseen]":
                                size 15
                        hbox:
                            text "push_mpostal_read: [has_mail_waitsend() and _mas_getAffection() >= 100 and renpy.seen_label('maica_wants_mspire') and renpy.seen_label('maica_wants_mpostal') and not mas_inEVL('maica_mpostal_received') and not mas_inEVL('maica_mpostal_read')]":
                                size 15
                        hbox:
                            text "push_mspire_want: [renpy.seen_label('maica_greeting') and not renpy.seen_label('maica_wants_mspire') and renpy.seen_label('mas_random_ask')]":
                                size 15
                        hbox:
                            textbutton "输出Event信息到日志":
                                action Function(log_eventstat)
                        hbox:
                            textbutton "推送分句测试":
                                action [
                                    Hide("maica_setting"),
                                    Function(store.maica_apply_setting),
                                    Function(store.MASEventList.push, "text_split")
                                ]
                        hbox:
                            textbutton "推送聊天loop":
                                action [
                                    Hide("maica_setting"),
                                    Function(store.maica_apply_setting),
                                    Function(store.MASEventList.push, "maica_main.talking_start")
                                    ]
                            textbutton "推送MSpire":
                                action [
                                    Hide("maica_setting"),
                                    Function(store.maica_apply_setting),
                                    Function(store.MASEventList.push, "maica_mspire")
                                    ]
                            textbutton "推送maica_mpostal_read":
                                action [
                                        Hide("maica_setting"),
                                        Function(store.maica_apply_setting),
                                        Function(store.MASEventList.push, "maica_mpostal_read")
                                    ]
                            textbutton "推送maica_mpostal_load":
                                action [
                                        Hide("maica_setting"),
                                        Function(store.maica_apply_setting),
                                        Function(store.MASEventList.push, "maica_mpostal_load")
                                    ]
                            
                            

                    hbox:
                        text _("累计对话轮次: [store.maica.maica.stat.get('message_count')]")

                    hbox:
                        text _("累计MSpire轮次: [store.maica.maica.stat.get('mspire_count')]")

                    hbox:
                        text _("累计收到Token: [store.maica.maica.stat.get('received_token')]")
                    
                    hbox:
                        text _("每个会话累计Token: [store.maica.maica.stat.get('received_token_by_session')]")
                    
                    hbox:
                        text _("累计发信数: [store.maica.maica.stat.get('mpostal_count')]")

                    hbox:
                        text _("当前用户: [store.maica.maica.user_acc]")

                    hbox:
                    
                        textbutton _("重置统计数据"):
                            action Function(store.maica.maica.reset_stat)

                    hbox:
                        textbutton _("服务提供节点: [MaicaProviderManager.get_server_by_id(persistent.maica_setting_dict.get('provider_id')).get('name', 'Unknown')]"):
                            action Show("maica_node_setting")
                            hovered SetField(_tooltip, "value", _("设置服务器节点"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox: 
                        textbutton _("自动重连: [persistent.maica_setting_dict.get('auto_reconnect')]"):
                            action ToggleDict(persistent.maica_setting_dict, "auto_reconnect", True, False)
                            hovered SetField(_tooltip, "value", _("连接断开时自动重连"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        textbutton _("严格反劫持: [persistent.maica_setting_dict.get('strict_mode')]"):
                            action ToggleDict(persistent.maica_setting_dict, "strict_mode", True, False)
                            hovered SetField(_tooltip, "value", _("严格模式下, 将会在每次发送时携带cookie信息"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        textbutton _("当前MAICA模型: [persistent.maica_setting_dict.get('maica_model')]"):
                            action ToggleDict(persistent.maica_setting_dict, "maica_model", store.maica.maica.MaicaAiModel.maica_main, store.maica.maica.MaicaAiModel.maica_core)
                            hovered SetField(_tooltip, "value", _("maica_main：完全能力模型，maica_core: 核心能力模型\n完全能力的前置响应延迟偏高"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        textbutton _("目标语言: [persistent.maica_setting_dict.get('target_lang')]"):
                            action ToggleDict(persistent.maica_setting_dict, "target_lang", store.maica.maica.MaicaAiLang.zh_cn, store.maica.maica.MaicaAiLang.en)
                            hovered SetField(_tooltip, "value", _("你与莫妮卡的沟通语言\n通过system prompt实现, 不能保证输出语言严格正确"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)


                    hbox:
                        textbutton _("使用高级参数: [persistent.maica_setting_dict.get('use_custom_model_config')]"):
                            action ToggleDict(persistent.maica_setting_dict, "use_custom_model_config", True, False)    
                            hovered SetField(_tooltip, "value", _("高级参数会大幅影响模型的表现"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        textbutton _("设置高级参数"):
                            action Show("maica_advance_setting")

                    hbox:
                        textbutton _("使用存档数据: [persistent.maica_setting_dict.get('sf_extraction')]"):
                            action ToggleDict(persistent.maica_setting_dict, "sf_extraction", True, False)
                            hovered SetField(_tooltip, "value", _("关闭时, 模型将不会使用存档数据\n每次重启游戏将自动上传存档"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        textbutton _("当前使用会话: [persistent.maica_setting_dict.get('chat_session')]"):
                            action Function(store.change_chatsession)
                            hovered SetField(_tooltip, "value", _("chat_session为0为单轮对话模式, 不同的对话之间相互独立, 需要分别上传存档"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        textbutton _("会话长度: "):
                            action NullAction()
                        bar:
                            value DictValue(persistent.maica_setting_dict, "max_history_token", 28672-512,step=10,offset=512 ,style="slider")
                            xsize 375
                            hovered SetField(_tooltip, "value", _("此参数意在缓解对话历史累积导致的响应速度过慢问题. 请避免将其设置得过小, 否则可能影响模型的正常语言能力."))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        textbutton _("[persistent.maica_setting_dict.get('max_history_token')]")


                    hbox:
                        textbutton _("输出到控制台: [persistent.maica_setting_dict.get('console')]"):
                            action ToggleDict(persistent.maica_setting_dict, "console", True, False)
                            hovered SetField(_tooltip, "value", _("在对话期间是否使用console显示相关信息, wzt的癖好\n说谁呢, 不觉得这很酷吗"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        textbutton _("控制台字体: [persistent.maica_setting_dict.get('console_font')]"):
                            action ToggleDict(persistent.maica_setting_dict, "console_font", store.maica_confont, store.mas_ui.MONO_FONT)
                            hovered SetField(_tooltip, "value", _("console使用的字体\nmplus-1mn-medium.ttf为默认字体\nSarasaMonoTC-SemiBold.ttf对于非英文字符有更好的显示效果"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        textbutton _("清除玩家补充信息: 当前共有[len(persistent.mas_player_additions)]条"):
                            action Function(reset_player_information)
                            hovered SetField(_tooltip, "value", _("由你补充的一些数据, 增删后需要重新上传存档"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        textbutton _("编辑信息"):
                            action [
                                Hide("maica_setting"),
                                Function(store.maica_apply_setting),
                                Function(renpy.jump, "maica_mods_preferences")
                                ]


                        textbutton _("导出至根目录"):
                            action Function(export_player_information)
                            hovered SetField(_tooltip, "value", _("导出至game/Submods/MAICA_ChatSubmod/player_information.txt"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        textbutton _("MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"):
                            action ToggleDict(persistent.maica_setting_dict, "mspire_enable", True, False)
                            hovered SetField(_tooltip, "value", _("是否允许由MSpire生成的对话, MSpire不受MFocus影响, 需要关闭重复对话"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        textbutton _("对话范围编辑"):
                            action [
                                Hide("maica_setting"),
                                Function(store.maica_apply_setting),
                                Function(renpy.jump, "mspire_mods_preferences")
                                ]
                        textbutton _("间隔"):
                            action NullAction()
                        bar:
                            value DictValue(persistent.maica_setting_dict, "mspire_interval", 200, step=1,offset=10 ,style="slider")
                            xsize 150
                            hovered SetField(_tooltip, "value", _("MSpire对话的最低间隔分钟"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        textbutton _("[persistent.maica_setting_dict.get('mspire_interval')]分钟")

                        textbutton _("搜索方式: [persistent.maica_setting_dict.get('mspire_search_type')]"):
                            action [
                                Hide("maica_setting"),
                                Function(store.maica_apply_setting),
                                Function(renpy.jump, "mspire_type")
                            ]

                    hbox:
                        textbutton _("submod_log.log 等级:[logging.getLevelName(store.mas_submod_utils.submod_log.level)]"):
                            action Function(store.change_loglevel)
                            hovered SetField(_tooltip, "value", _("这将影响submod_log.log中每条log的等级, 低于该等级的log将不会记录\n这也会影响其他子模组"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)


                        textbutton _("控制台log等级: [logging.getLevelName(store.maica.maica.console_logger.level)]"):
                            action Function(store.change_conloglevel)
                            hovered SetField(_tooltip, "value", _("这将影响控制台中每条log的等级, 低于该等级的log将不会记录"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        textbutton _("状态码更新速度"):
                            action NullAction()
                        bar:
                            value DictValue(persistent.maica_setting_dict, "status_update_time", 3.0, step=0.1, offset=0.1,style="slider")
                            xsize 150
                            hovered SetField(_tooltip, "value", _("在Submod界面处的状态码更新频率"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        textbutton "[persistent.maica_setting_dict.get('status_update_time')]s"


                    hbox:
                        textbutton _("MTrigger 列表"):
                            action Show("maica_triggers")
                        
                        textbutton _("查看MPostals往来信件"):
                            action Show("maica_mpostals")
                        
                        textbutton _("回信时显示控制台"):
                            action ToggleDict(persistent.maica_setting_dict, "show_console_when_reply", True, False)
                    
                    hbox:
                        textbutton _("查看后端负载"):
                            action Show("maica_workload_stat")




            hbox:
                style_prefix "confirm"
                textbutton _("保存设置"):
                    action [
                        Function(store.maica_apply_setting),
                        Hide("maica_setting")
                        ]
                textbutton _("重置设置"):
                    action [
                        Function(store.maica_reset_setting),
                        Function(store.maica_apply_setting, ininit = True),
                        Function(renpy.notify, _("MAICA: 设置已重置")),
                        Hide("maica_setting")
                    ]
                
                 

default use_email = True
screen maica_login():
    modal True
    zorder 215

    style_prefix "confirm"

    frame:
        vbox:
            xfill False
            yfill False
            spacing 5

            hbox:
                style_prefix "check"
                if use_email:
                    textbutton _("改为用户名登录"):
                        action [ToggleVariable("use_email"), Function(_maica_clear)]
                        selected False

                else:
                    textbutton _("改为邮箱登录"):
                        action [ToggleVariable("use_email"), Function(_maica_clear)]
                        selected False
                        

                    
            hbox:
                if use_email:
                    textbutton _("输入 DCC 账号邮箱"):
                        action Show("maica_login_input",message = _("请输入DCC 账号邮箱"),returnto = "_maica_LoginEmail")
                else:
                    textbutton _("输入 DCC 账号用户名"):
                        action Show("maica_login_input",message = _("请输入DCC 账号用户名") ,returnto = "_maica_LoginAcc")

            hbox:
                textbutton _("输入 DCC 账号密码"):
                    action Show("maica_login_input",message = _("请输入DCC 账号密码"),returnto = "_maica_LoginPw")
            hbox:
                text ""
            hbox:
                textbutton _("连接至服务器生成MAICA令牌"):
                    action [
                        Function(store.maica.maica._gen_token, store._maica_LoginAcc, store._maica_LoginPw, "", store._maica_LoginEmail if store._maica_LoginEmail != "" else None),
                        Function(_maica_verify_token),
                        Function(_maica_clear), 
                        Hide("maica_login")
                        ]
                textbutton _("取消"):
                    action [Function(_maica_clear), Hide("maica_login")]
            hbox:
                text _("{size=-10}※ 使用MAICA Blessland, 即认为你同意 {a=https://maica.monika.love/tos_zh}{i}{u}MAICA服务条款{/i}{/u}{/a}")
            hbox:
                text _("{size=-10}※ 还没有DCC账号? {a=https://forum.monika.love/signup}{i}{u}注册一个{/u}{/i}{/a}")



screen maica_login_input(message, returnto, ok_action = Hide("maica_login_input")):
    #登录输入账户窗口, 也用来用作通用的输入窗口
    ## Ensure other screens do not get input while this screen is displayed.s
    modal True
    zorder 225

    style_prefix "confirm"

    frame:
        vbox:
            ymaximum 300
            xmaximum 800
            xfill True
            yfill False
            spacing 5

            label _(message):
                style "confirm_prompt"
                xalign 0.5
            hbox:
                input default "" value VariableInputValue(returnto) length 64

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action ok_action



screen maica_message(message = "Non Message", ok_action = Hide("maica_message")):
    modal True
    zorder 225

    style_prefix "confirm"

    frame:
        vbox:
            ymaximum 300
            xmaximum 800
            xfill True
            yfill False
            spacing 5

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            #input default "" value VariableInputValue("savefile") length 25

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action ok_action

screen maica_input_screen(prompt):
    default maica_input = store.maica.MaicaInputValue()
    style_prefix "input"

    window:
        hbox:
            style_prefix "quick"
            #xfill True
            #xmaximum 0#(None if not has_history else 232)
            xalign 0.5
            yalign 0.995

            textbutton _("就这样吧"):
                selected False
                action Return("nevermind")

            textbutton _("粘贴"):
                selected False
                action [Function(maica_input.set_text, pygame.scrap.get(pygame.SCRAP_TEXT).strip()),Function(maica_input.set_text, pygame.scrap.get(pygame.SCRAP_TEXT).strip())]
            
            #extbutton _("清空"):
            #   selected False
            #   action Function(maica_input.set_text, "")

#            有一点点想实现搜索历史的想法，不过摸了
#            if has_history:
#                if renpy.get_screen("ytm_history_submenu") is None:
#                    textbutton _("Show previous tracks"):
#                        selected False
#                        action ShowTransient("ytm_history_submenu")
#
#                else:
#                    textbutton _("Hide previous tracks"):
#                        selected False
#                        action Hide("ytm_history_submenu")
#
        vbox:
            align (0.5, 0.5)
            spacing 30

            text prompt style "input_prompt"
            input:
                id "input"
                value maica_input