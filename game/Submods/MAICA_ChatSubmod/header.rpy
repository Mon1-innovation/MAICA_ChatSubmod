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
        "enable_mf":True,
        "enable_mt":True,
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
        "mspire_use_cache":True,
        "log_level":logging.DEBUG,
        "log_conlevel":logging.INFO,
        "provider_id":1 if not renpy.android else 2,
        "max_history_token":4096,
        "status_update_time":0.25,
        "strict_mode": False,
        "show_console_when_reply": False,
        "mpostal_default_reply_time": 60*60*12,
        "42seed":False,
        "use_anim_background": True
    }
    import copy
    mdef_setting = copy.deepcopy(maica_default_dict)
    maica_advanced_setting = {
        "top_p":0.7,
        "temperature":0.2,
        "max_tokens":1600,
        "frequency_penalty":0.4,
        "presence_penalty":0.4,
        "seed":0,
        "mf_aggressive":False,
        "sfe_aggressive":False,
        "tnd_aggressive":1,
        "esc_aggressive":True,
        "nsfw_acceptive":True,
        "pre_additive":0,
        "post_additive":1,
        "amt_aggressive":True,
        "tz":None,
    }
    maica_advanced_setting_status = {k: False for k, v in maica_advanced_setting.items()}
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
    def _upload_persistent_dict():
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
        import json_exporter
        sentiment = json_exporter.persistent_filter

        keys_to_remove = []

        def process_value(value, depth=0):
            # Prevent infinite recursion
            if depth > 3:
                return "REMOVED|TOO_DEEP"

            # Handle None
            if value is None:
                return None

            # Recursive processing for dictionaries
            if isinstance(value, dict):
                return {k: process_value(v, depth+1) for k, v in value.items() if k in sentiment}

            # Recursive processing for lists/tuples
            if isinstance(value, (list, tuple)):
                return [process_value(item, depth+1) for item in value]

            # check serialization and length
            try:
                str_val = str(value)
                if len(str_val) > maxlen:
                    return "REMOVED|TOO_LONG"
                
                # Attempt JSON serialization
                json.dumps(value)
                return value
            except:
                return "REMOVED|UNSERIALIZABLE"

        keys_to_remove = []
        for i in list(d.keys()):  # Use list() for Python 2 & 3 compatibility
            if i not in sentiment:
                keys_to_remove.append(i)
                continue
            
            d[i] = process_value(d[i])

        for key in keys_to_remove:
            del d[key]
        res = store.maica.maica.upload_save(d)
        if not res.get("success", False):
            store.mas_submod_utils.submod_log.error("ERROR: upload save failed: {}".format(res.get("exception", "unknown")))
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
        
        if persistent.maica_setting_dict["42seed"]:
            persistent.maica_advanced_setting_status["seed"] = False
            persistent.maica_advanced_setting['seed'] = 42
            store.maica.maica.modelconfig.update({"seed":42})
        store.maica.maica.sf_extraction = persistent.maica_setting_dict["sf_extraction"]
        store.maica.maica.chat_session = persistent.maica_setting_dict["chat_session"]
        store.maica.maica.enable_mf = persistent.maica_setting_dict['enable_mf']
        store.maica.maica.enable_mt = persistent.maica_setting_dict['enable_mt']
        store.maica.maica.mspire_use_cache = persistent.maica_setting_dict["mspire_use_cache"]
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

    def chatsession_can_add():
        return 0 <= persistent.maica_setting_dict["chat_session"] <= 8

    def chatsession_add():
        if chatsession_can_add():
            persistent.maica_setting_dict["chat_session"] += 1
        
    def chatsession_can_sub():
        return 1 <= persistent.maica_setting_dict["chat_session"] <= 9

    def chatsession_sub():
        if chatsession_can_sub():
            persistent.maica_setting_dict["chat_session"] -= 1


    def sessionlength_can_add():
        return 512 <= persistent.maica_setting_dict["max_history_token"] <= 28671

    def sessionlength_add():
        if sessionlength_can_add():
            persistent.maica_setting_dict["max_history_token"] += 1
        
    def sessionlength_can_sub():
        return 513 <= persistent.maica_setting_dict["max_history_token"] <= 28672

    def sessionlength_sub():
        if sessionlength_can_sub():
            persistent.maica_setting_dict["max_history_token"] -= 1
        
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
    log_eventstat()
        

init python:
    def scr_nullfunc():
        return            

style small_link is main_menu_version:
    size 10

image bar1 = Transform("gui/scrollbar/horizontal_poem_bar_d.png", xalign=0.1, yalign=0.5, size=(300, 25))
image bar2 = Transform("gui/scrollbar/horizontal_poem_bar_d.png", xalign=0.9, yalign=0.5, size=(300, 25))

screen divider(message):

    hbox:
        yminimum 75
        xfill True

        hbox:
            xalign 0.5
            yalign 0.6
            xminimum 900
            add "bar1"
            text "  "
            text message:
                xalign 0.5
            text "  "
            add "bar2"

style main_menu_version:
    text_align 0.0

style main_menu_version_dark:
    text_align 0.0

style nf_check_label is check_label

style nf_check_label_dark is check_label_dark

style nf_check_label_text is check_label_text

style nf_check_label_text_dark is check_label_text_dark

style nf_check_vbox is check_vbox

style nf_check_button is check_button

style nf_check_button_dark is check_button_dark

style nf_check_button_text is check_button_text:
    xpos -10

style nf_check_button_text_dark is check_button_text_dark:
    xpos -10


style addsub_fancy_check_button:
    background Solid("#FFBDE1")
    hover_background Solid("#ffd1ea")
    selected_background Solid("#FFBDE1")
    insensitive_background Solid("#BFBFBF")

style addsub_fancy_check_button_dark:
    background Solid("#CE4A7E")
    hover_background Solid("#d9739c")
    selected_background Solid("#CE4A7E")
    insensitive_background Solid("#333333")

style addsub_fancy_check_button_disabled is addsub_fancy_check_button:
    background Solid("#1b1b1b")
    selected_background Solid("#1b1b1b")

style addsub_fancy_check_button_text is gui_button_text:
    font "gui/font/Halogen.ttf"
    color "#ffe6f4"
    hover_color "#000000"
    selected_color "#000000"
    insensitive_color mas_ui.light_button_text_insensitive_color
    outlines []
    yoffset 3
    xoffset -10

style addsub_fancy_check_button_text_dark is gui_button_text_dark:
    font "gui/font/Halogen.ttf"
    color "#BFBFBF"
    hover_color "#FFAA99"
    selected_color "#FFAA99"
    insensitive_color mas_ui.dark_button_text_insensitive_color
    outlines []
    yoffset 3
    xoffset -10

style addsub_fancy_check_button_disabled_text is addsub_fancy_check_button_text:
    font "gui/font/Halogen.ttf"
    color "#8C8C8C"
    outlines []
    yoffset 3
    xoffset -10

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
        
        if renpy.android and not os.path.exists(os.path.join(ANDROID_MASBASE, 'game', 'python-packages', 'certifi', 'cacert.pem')):
            text _("> 警告: 找不到证书, 你是不是忘记安装数据包了?"):
                xalign 1.0 yalign 0.0
                xoffset -10
                style "main_menu_version"

        if store.mas_submod_utils.isSubmodInstalled("Better Loading"):
            text _("> 警告: 与 Better Loading 不兼容"):
                xalign 1.0 yalign 0.0
                xoffset -10
                style "main_menu_version"
        if store.mas_submod_utils.isSubmodInstalled("Log Screen"):
            text _("> 警告: 与 Log Screen 一起使用时, 请将'submod_log'的过滤级别提高至info及以上"):
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
                
                textbutton _("> 重置当前对话"):
                    action Function(reset_session)
            else:
                textbutton _("> 手动上传设置 [[请先使MAICA完成连接]")
                     
                textbutton _("> 重置当前对话 [[现在暂时不能重置]")

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
        if os.path.exists(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "donation")):
            textbutton _("> 向 MAICA 捐赠"):
                action Show("maica_support")

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
        xalign 0.5
        yalign 0.26
        vbox:
            xmaximum 1000
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 500
                xmaximum 1000
                xfill True
                yfill True
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1000
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
                            
                            textbutton renpy.substitute(_("> 打开官网")) + "(" + provider.get('portalPage') + ")":
                                action OpenURL(provider.get('portalPage'))

                            if provider.get("isOfficial", False):
                                textbutton _(" √ MAICA 官方服务器")
                            

                    
            hbox:
                style_prefix "confirm"
                textbutton _("更新节点列表"):
                    style_prefix "confirm"
                    action Function(store.maica.maica.MaicaProviderManager.get_provider)

                textbutton _("关闭"):
                    style_prefix "confirm"
                    action Hide("maica_node_setting")
                
                textbutton _("测试当前节点可用性"):
                    style_prefix "confirm"
                    action Function(store.maica.maica.accessable)
                        
screen maica_mspire_setting():
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
        xalign 0.5
        yalign 0.26
        vbox:
            xmaximum 1000
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 500
                xmaximum 1000
                xfill True
                yfill True
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1000
                    xfill True
                    yfill False
                    textbutton "percise_page":
                        action SetDict(persistent.maica_setting_dict, "mspire_search_type", "percise_page")
                    text _("仅选取与搜索关键词最接近的一个页面, 此时采样广度不生效. 此种类条目不执行递归查找, 响应较快.\n"):
                        size 15
                    textbutton "fuzzy_page":
                        action SetDict(persistent.maica_setting_dict, "mspire_search_type", "fuzzy_page")
                    text _("根据关键词搜索多个页面, 从中随机抽取一个页面. 此种类条目不执行递归查找, 响应较快.\n"):
                        size 15
                    textbutton "in_percise_category":
                        action SetDict(persistent.maica_setting_dict, "mspire_search_type", "in_percise_category")
                    text _("先仅选取与搜索关键词最接近的一个分类, 再从其中递归地随机抽取分类或页面, 直至最终抽取到一个页面. 此种类条目响应较慢.\n"):
                        size 15
                    textbutton "in_fuzzy_category":
                        action SetDict(persistent.maica_setting_dict, "mspire_search_type", "in_fuzzy_category")
                    text _("根据关键词搜索多个分类, 再从其中递归地随机抽取分类或页面, 直至最终抽取到一个页面. 此种类条目响应较慢.\n"):
                        size 15
                    textbutton "in_fuzzy_all":
                        action SetDict(persistent.maica_setting_dict, "mspire_search_type", "in_fuzzy_all")
                    text _("根据关键词直接开始递归地抽取分类或页面, 直至最终抽取到一个页面. 此种类条目响应较慢.\n"):
                        size 15
            hbox:
                style_prefix "confirm"
                textbutton _("关闭"):
                    action Hide("maica_mspire_setting")
                
                # textbutton _("当前方式: [persistent.maica_setting_dict.get('mspire_search_type', 'None')]")


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
        xalign 0.5
        yalign 0.26
        vbox:
            xmaximum 1000
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 500
                xmaximum 1000
                xfill True
                yfill True
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1000
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

                        hbox:
                            if hasattr(trigger, 'web_musicplayer_installed'):
                                text _("内置 | 更换背景音乐 "):
                                    size 15
                                text _("* 支持 "):
                                    yalign 1.0
                                    size 10
                                textbutton "{u}Netease Music{/u}" style "small_link" action OpenURL("https://github.com/MAS-Submod-MoyuTeam/NeteaseInMas"):
                                    yalign 1.0
                                    text_size 10
                                text _(" 和 "):
                                    yalign 1.0
                                    size 10
                                textbutton "{u}Youtube Music{/u}" style "small_link" action OpenURL("https://github.com/Booplicate/MAS-Submods-YouTubeMusic"):
                                    yalign 1.0
                                    text_size 10
                                text _(" 子模组"):
                                    yalign 1.0
                                    size 10

                            else:
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
        xalign 0.5
        yalign 0.26
        vbox:
            xmaximum 1000
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 500
                xmaximum 1000
                xfill True
                yfill True
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1000
                    xfill True
                    yfill False
                    # hbox:
                    #     textbutton _("{size=15}因能力有限, 阅读信件后信件列表将在返回太空教室后重新显示.")

                    hbox:
                        text ""
                    for postal in persistent._maica_send_or_received_mpostals:
                        label postal["raw_title"]
                        text renpy.substitute(_("信件状态: ")) + postal["responsed_status"]:
                            size 10                       
                        text renpy.substitute(_("寄信时间: ")) + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(postal["time"].split(".")[0]))):
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

screen maica_support():
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
        xalign 0.5
        yalign 0.26
        vbox:
            xmaximum 1000
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 500
                xmaximum 1000
                xfill True
                yfill True
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1000
                    xfill True
                    yfill False

                    text _("首先很感谢你有心捐赠.\n我们收到的捐赠基本上不可能回本, 但你不必有任何压力.")

                    text _("请注意, 向MAICA捐赠不会提供任何特权, 除了论坛捐赠页名单和捐赠徽章.")

                    if config.language == 'chinese':
                        imagebutton:
                            idle "mod_assets/maica_img/aifadian.png"
                            insensitive "mod_assets/maica_img/aifadian.png"
                            hover "mod_assets/maica_img/aifadian.png"
                            selected_idle "mod_assets/maica_img/aifadian.png"
                            selected_hover "mod_assets/maica_img/aifadian.png"
                            action OpenURL("https://forum.monika.love/iframe/redir_donation.php?lang=zh")
                    else:
                        imagebutton:
                            idle "mod_assets/maica_img/unifans.png"
                            insensitive "mod_assets/maica_img/unifans.png"
                            hover "mod_assets/maica_img/unifans.png"
                            selected_idle "mod_assets/maica_img/unifans.png"
                            selected_hover "mod_assets/maica_img/unifans.png"
                            action OpenURL("https://forum.monika.love/iframe/redir_donation.php?lang=en")

            hbox:
                textbutton _("关闭"):
                    style_prefix "confirm"
                    action Hide("maica_support") 

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
        xalign 0.5
        yalign 0.26
        vbox:
            xmaximum 1000
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 500
                xmaximum 1000
                xfill True
                yfill True
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1000
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
            persistent.maica_setting_dict["provider_id"] = int(id)

    modal True
    zorder 215
    
    style_prefix "check"

    frame:
        xalign 0.5
        yalign 0.26
        vbox:
            xmaximum 1000
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 500
                xmaximum 1000
                xfill True
                yfill True
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1000
                    xfill True
                    yfill False

                    text maica_log.get("title")

                    text "========================================================="
                    for content in maica_log.get("content"):
                        text content.replace("[", "[[").replace("{", "{{").replace("【", "【【"):
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
        xalign 0.5
        yalign 0.26
        vbox:
            xmaximum 1000
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 500
                xmaximum 1000
                xfill True
                yfill True
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1000
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
                    action [
                        SetDict(persistent.maica_advanced_setting_status, "tz", persistent.maica_advanced_setting['tz']),
                        Hide("maica_tz_setting")
                        ]


screen maica_advance_setting():
    python:
        submods_screen = store.renpy.get_screen("submods", "screens")

        if submods_screen:
            _tooltip = submods_screen.scope.get("tooltip", None)
        else:
            _tooltip = None
        
        def reset_to_default():
            for item in store.maica.maica.default_setting:
                if item == 'seed':
                    store.maica.maica.default_setting[item] = 0
                if item in persistent.maica_advanced_setting:
                    persistent.maica_advanced_setting[item] = store.maica.maica.default_setting[item]
                    persistent.maica_advanced_setting_status[item] = False
                    

    modal True
    zorder 215
    
    style_prefix "check"

    frame:
        xalign 0.5
        yalign 0.26
        vbox:
            xmaximum 1000
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 500
                xmaximum 1000
                xfill True
                yfill True
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1000
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
                            hovered SetField(_tooltip, "value", _("token权重过滤范围. 非常不建议动这个"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        if persistent.maica_advanced_setting_status.get("top_p", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "top_p", 0.9, step=0.01,offset=0.1 ,style="slider")
                                xsize 200
                            
                            textbutton "[persistent.maica_advanced_setting.get('top_p', 'None')]"

                    hbox:
                        textbutton "temperature":
                            action ToggleDict(persistent.maica_advanced_setting_status, "temperature")
                            hovered SetField(_tooltip, "value", _("token选择的随机程度. 数值越高, 模型输出会越偏离普遍最佳情况"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        if persistent.maica_advanced_setting_status.get("temperature", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "temperature", 1.0, step=0.01,offset=0 ,style="slider")
                                xsize 200
                            textbutton "[persistent.maica_advanced_setting.get('temperature', 'None')]"
                    
                    hbox:
                        textbutton "max_tokens":
                            action ToggleDict(persistent.maica_advanced_setting_status, "max_tokens")
                            hovered SetField(_tooltip, "value", _("模型一轮生成的token数限制. 一般而言不会影响表现, 只会截断超长的部分"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        if persistent.maica_advanced_setting_status.get("max_tokens", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "max_tokens", 2048, step=1,offset=0 ,style="slider")
                                xsize 200
                            textbutton "[persistent.maica_advanced_setting.get('max_tokens', 'None')]"
                    
                    hbox:
                        textbutton "frequency_penalty":
                            action ToggleDict(persistent.maica_advanced_setting_status, "frequency_penalty")
                            hovered SetField(_tooltip, "value", _("token频率惩罚. 数值越高, 反复出现的token越不可能继续出现, 一般会产生更短且更延拓的结果"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        if persistent.maica_advanced_setting_status.get("frequency_penalty", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "frequency_penalty", 1.0, step=0.01,offset=0 ,style="slider")
                                xsize 200
                            textbutton "[persistent.maica_advanced_setting.get('frequency_penalty', 'None')]"
                    
                    hbox:
                        textbutton "presence_penalty":
                            action ToggleDict(persistent.maica_advanced_setting_status, "presence_penalty")
                            hovered SetField(_tooltip, "value", _("token重现惩罚. 数值越高, 出现过的token越不可能再次出现, 一般会产生更跳跃的结果"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        if persistent.maica_advanced_setting_status.get("presence_penalty", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "presence_penalty", 1.0, step=0.01,offset=0 ,style="slider")
                                xsize 200
                            textbutton "[persistent.maica_advanced_setting.get('presence_penalty', 'None')]"
 
                    hbox:
                        if not persistent.maica_setting_dict.get('42seed'):
                            textbutton "seed":
                                action ToggleDict(persistent.maica_advanced_setting_status, "seed")
                            
                            if persistent.maica_advanced_setting_status.get("seed", False):
                                #bar:
                                #    value DictValue(persistent.maica_advanced_setting, "seed", 998, step=1,offset=1 ,style="slider")
                                #    xsize 600
                                textbutton "[persistent.maica_advanced_setting.get('seed', 'None')] ":
                                    action Show("maica_seed_input")

                                # textbutton "+1000":
                                #     action SetDict(persistent.maica_advanced_setting, "seed", persistent.maica_advanced_setting["seed"] + 1000)

                                # textbutton "+100":
                                #     action SetDict(persistent.maica_advanced_setting, "seed", persistent.maica_advanced_setting["seed"] + 100)

                                # textbutton "+25":
                                #     action SetDict(persistent.maica_advanced_setting, "seed", persistent.maica_advanced_setting["seed"] + 25)

                                # textbutton "+1":
                                #     action SetDict(persistent.maica_advanced_setting, "seed", persistent.maica_advanced_setting["seed"] + 1)

                                # textbutton "-1":
                                #     action SetDict(persistent.maica_advanced_setting, "seed", persistent.maica_advanced_setting["seed"] - 1)
                                
                                # textbutton "-25":
                                #     action SetDict(persistent.maica_advanced_setting, "seed", persistent.maica_advanced_setting["seed"] - 25)
                                
                                # textbutton "-100":
                                #     action SetDict(persistent.maica_advanced_setting, "seed", persistent.maica_advanced_setting["seed"] - 100)
                                
                                # textbutton "-1000":
                                #     action SetDict(persistent.maica_advanced_setting, "seed", persistent.maica_advanced_setting["seed"] - 1000)

                        else:
                            textbutton "seed ":
                                action NullAction()
                                selected persistent.maica_advanced_setting_status.get('seed', False)

                            textbutton "[persistent.maica_advanced_setting.get('seed', 'None')]"

                            textbutton _("!已启用最佳实践")


                    hbox:
                        text _("{size=-10}================偏好================")

                    hbox:
                        textbutton "tnd_aggressive":
                            action ToggleDict(persistent.maica_advanced_setting_status, "tnd_aggressive")
                            hovered SetField(_tooltip, "value", _("即使MFocus未调用工具, 也提供一些工具的结果.\n+ 其值越高, 越能避免信息缺乏导致的幻觉, 并产生灵活体贴的表现\n- 其值越高, 越有可能产生注意力涣散和专注混乱"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        if persistent.maica_advanced_setting_status.get("tnd_aggressive", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "tnd_aggressive", 3, step=1,offset=0 ,style="slider")
                                xsize 100
                            textbutton "[persistent.maica_advanced_setting.get('tnd_aggressive', 'None')]"
                    hbox:
                        textbutton "mf_aggressive:[persistent.maica_advanced_setting.get('mf_aggressive', 'None')]":
                            action [ToggleDict(persistent.maica_advanced_setting_status, "mf_aggressive"),
                                ToggleDict(persistent.maica_advanced_setting, "mf_aggressive")]
                            hovered SetField(_tooltip, "value", _("要求agent模型生成最终指导, 并替代默认MFocus指导.\n+ 信息密度更高, 更容易维持语言自然\n- 表现十分依赖agent模型自身的能力\n- 启用时会禁用tnd_aggressive"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        textbutton "sfe_aggressive:[persistent.maica_advanced_setting.get('sfe_aggressive', 'None')]":
                            action [ToggleDict(persistent.maica_advanced_setting_status, "sfe_aggressive"),
                                ToggleDict(persistent.maica_advanced_setting, "sfe_aggressive")]
                            hovered SetField(_tooltip, "value", _("将prompt和引导中的[[player]字段替换为玩家真名.\n+ 模型对玩家的名字有实质性理解\n- 明显更容易发生表现离群和专注混乱"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        textbutton "esc_aggressive:[persistent.maica_advanced_setting.get('esc_aggressive', 'None')]":
                            action [ToggleDict(persistent.maica_advanced_setting_status, "esc_aggressive"),
                                ToggleDict(persistent.maica_advanced_setting, "esc_aggressive")]
                            hovered SetField(_tooltip, "value", _("在MFocus调用互联网搜索的情况下, 要求其整理一遍结果.\n+ 大多数情况下信息密度更高, 更容易维持语言自然\n- 涉及互联网搜索时生成速度更慢"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                            selected persistent.maica_advanced_setting_status.get('esc_aggressive')
                        textbutton "amt_aggressive: [persistent.maica_advanced_setting.get('amt_aggressive', 'None')]":
                            action [ToggleDict(persistent.maica_advanced_setting_status, "amt_aggressive"),
                                ToggleDict(persistent.maica_advanced_setting, "amt_aggressive")]
                            hovered SetField(_tooltip, "value", _("当MTrigger存在时, 要求MFocus预检玩家的请求并提供指导.\n+ 比较明显地改善MTrigger失步问题\n- 在少数情况下对语言的自然性产生破坏\n* 当对话未使用MTrigger或仅有好感触发器, 此功能不会生效"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                            selected persistent.maica_advanced_setting_status.get('amt_aggressive')
                    hbox:
                        textbutton "nsfw_acceptive:[persistent.maica_advanced_setting.get('nsfw_acceptive', 'None')]":
                            action [ToggleDict(persistent.maica_advanced_setting_status, "nsfw_acceptive"),
                                ToggleDict(persistent.maica_advanced_setting, "nsfw_acceptive")]
                            hovered SetField(_tooltip, "value", _("要求模型宽容正面地对待有毒内容.\n+ (出乎意料地)在大多数场合下对模型表现有正面作用, 即使不涉及有毒内容\n- 在少数情况下造成意料之外的问题"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                            selected persistent.maica_advanced_setting_status.get('nsfw_acceptive')

                    hbox:
                        textbutton "pre_additive":
                            action ToggleDict(persistent.maica_advanced_setting_status, "pre_additive")
                            hovered SetField(_tooltip, "value", _("在MFocus介入时, 额外提供上下文以供分析. 范围0-5.\n+ 改善MFocus对连贯对话的理解能力\n- 明显更容易破坏MFocus的应答模式"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        if persistent.maica_advanced_setting_status.get("pre_additive", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "pre_additive", 5, step=1,offset=0 ,style="slider")
                                xsize 50
                            textbutton "[persistent.maica_advanced_setting.get('pre_additive', 'None')]"

                        textbutton "post_additive":
                            action ToggleDict(persistent.maica_advanced_setting_status, "post_additive")
                            hovered SetField(_tooltip, "value", _("在MTrigger介入时, 额外提供上下文以供分析. 范围0-5.\n+ 改善MTrigger对连贯对话的理解能力\n- 更容易破坏MTrigger的应答模式"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                        
                        if persistent.maica_advanced_setting_status.get("post_additive", False):
                            bar:
                                value DictValue(persistent.maica_advanced_setting, "post_additive", 5, step=1,offset=0 ,style="slider")
                                xsize 50
                            textbutton "[persistent.maica_advanced_setting.get('post_additive', 'None')]"

                    hbox:      
                        textbutton _("选择时区: [persistent.maica_advanced_setting.get('tz') or 'Asia/Shanghai' if store.maica.maica.target_lang == store.maica.maica.MaicaAiLang.zh_cn else 'America/Indiana/Vincennes']"):
                            action Show("maica_tz_setting")
                            selected persistent.maica_advanced_setting_status.get('tz')





                    
            hbox:
                style_prefix "confirm"
                textbutton _("保存设置"):
                    action [
                        Function(maica_apply_advanced_setting),
                        Hide("maica_advance_setting")
                    ]
                textbutton _("重置设置"):
                    action [
                        Function(reset_to_default),
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
        xsize 1100
        xalign 0.5
        yalign 0.2
        vbox:
            xmaximum 1100
            spacing 10
            viewport:
                id "viewport"
                scrollbars "vertical"
                xsize 1100
                ysize 550

                mousewheel True
                draggable True
                
                hbox:
                    vbox:
                        xsize 30
                    vbox:
                        xsize 1040
                        spacing 5

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
                                text "triggered_list: [store.maica.maica.mtrigger_manager.triggered_list]":
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
                            use divider(_("连接与安全"))

                        hbox:
                            textbutton _("服务提供节点: [MaicaProviderManager.get_server_by_id(persistent.maica_setting_dict.get('provider_id')).get('name', 'Unknown')]"):
                                action Show("maica_node_setting")
                                hovered SetField(_tooltip, "value", _("设置服务器节点"))
                                unhovered SetField(_tooltip, "value", _tooltip.default)
                        hbox:
                            style_prefix "generic_fancy_check"
                            textbutton _("自动重连: [persistent.maica_setting_dict.get('auto_reconnect')]"):
                                action ToggleDict(persistent.maica_setting_dict, "auto_reconnect", True, False)
                                hovered SetField(_tooltip, "value", _("连接断开时自动重连"))
                                unhovered SetField(_tooltip, "value", _tooltip.default)
                        hbox:
                            style_prefix "generic_fancy_check"
                            textbutton _("ws严格模式: [persistent.maica_setting_dict.get('strict_mode')]"):
                                action ToggleDict(persistent.maica_setting_dict, "strict_mode", True, False)
                                hovered SetField(_tooltip, "value", _("严格模式下, 将会在每次发送时携带cookie信息"))
                                unhovered SetField(_tooltip, "value", _tooltip.default)

                        hbox:
                            use divider(_("行为与表现"))

                        hbox:
                            style_prefix "generic_fancy_check"
                            textbutton _("使用MTrigger: [persistent.maica_setting_dict.get('enable_mt')]"):
                                action ToggleDict(persistent.maica_setting_dict, "enable_mt", True, False)
                        hbox:
                            style_prefix "generic_fancy_check"
                            textbutton _("使用MFocus: [persistent.maica_setting_dict.get('enable_mf')]"):
                                action ToggleDict(persistent.maica_setting_dict, "enable_mf", True, False)
                        hbox:
                            textbutton _("目标语言: [persistent.maica_setting_dict.get('target_lang')]"):
                                action Show("maica_select_language")
                                hovered SetField(_tooltip, "value", _("目标生成语言. 仅支持\"zh\"或\"en\".\n* 该参数不能100%保证生成语言是目标语言\n* 该参数影响范围广泛, 包括默认时区, 节日文化等, 并不止目标生成语言. 建议设为你的实际母语\n* 截至文档编纂时为止, MAICA官方部署的英文能力仍然弱于中文"))
                                unhovered SetField(_tooltip, "value", _tooltip.default)

                        hbox:
                            frame:
                                xmaximum 950
                                xpos 30
                                xfill True
                                vbox:
                                    xmaximum 950
                                    xfill True
                                    hbox:
                                        style_prefix "generic_fancy_check"
                                        textbutton _("使用自定义高级参数: [persistent.maica_setting_dict.get('use_custom_model_config')]"):
                                            action ToggleDict(persistent.maica_setting_dict, "use_custom_model_config", True, False)
                                            hovered SetField(_tooltip, "value", _("高级参数可能大幅影响模型的表现.\n* 默认的高级参数已经是实践中的普遍最优配置, 不建议启用"))
                                            unhovered SetField(_tooltip, "value", _tooltip.default)
                                    hbox:
                                        textbutton _("设置高级参数"):
                                            action Show("maica_advance_setting")
                                    hbox:
                                        textbutton _("锁定最佳实践"):
                                            action ToggleDict(persistent.maica_setting_dict, "42seed", True, False)
                                            hovered SetField(_tooltip, "value", _("锁定seed为42, 该设置覆盖高级参数中的seed.\n* 启用会完全排除生成中的随机性, 在统计学上稳定性更佳, 且更易于复现"))
                                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        hbox:
                            use divider(_("会话与数据"))

                        hbox:
                            style_prefix "generic_fancy_check"
                            textbutton _("使用存档数据: [persistent.maica_setting_dict.get('sf_extraction')]"):
                                action ToggleDict(persistent.maica_setting_dict, "sf_extraction", True, False)
                                hovered SetField(_tooltip, "value", _("关闭时, 模型将不会使用存档数据.\n* 每次重启游戏将自动上传存档数据"))
                                unhovered SetField(_tooltip, "value", _tooltip.default)

                        hbox:
                            $ tooltip_chat_session = _("每个session独立保存和应用对话记录.\n* 设为0以不记录和不使用对话记录(单轮对话)")
                            hbox:
                                style_prefix "addsub_fancy_check"
                                textbutton "-":
                                    text_size 40
                                    action [Function(store.chatsession_sub), SensitiveIf(store.chatsession_can_sub())]
                                    hovered SetField(_tooltip, "value", tooltip_chat_session)
                                    unhovered SetField(_tooltip, "value", _tooltip.default)
                            hbox:
                                xsize 200
                                style_prefix "nf_check"
                                textbutton _("当前使用会话: [persistent.maica_setting_dict.get('chat_session')]"):
                                    xalign 0.5
                                    action NullAction()
                                    hovered SetField(_tooltip, "value", tooltip_chat_session)
                                    unhovered SetField(_tooltip, "value", _tooltip.default)
                            hbox:
                                style_prefix "addsub_fancy_check"
                                textbutton "+":
                                    text_size 40
                                    action [Function(store.chatsession_add), SensitiveIf(store.chatsession_can_add())]
                                    hovered SetField(_tooltip, "value", tooltip_chat_session)
                                    unhovered SetField(_tooltip, "value", _tooltip.default)

                        hbox:
                            $ tooltip_session_length = _("会话保留的最大长度. 范围512-28672.\n* 按字符数计算. 每3个ASCII字符只占用一个字符长度\n* 字符数超过限制后, MAICA会裁剪其中较早的部分, 直至少于限制的 2/3\n* 过大或过小的值可能导致表现和性能问题")
                            textbutton _("会话长度: "):
                                action Show("maica_context_length_input")
                                hovered SetField(_tooltip, "value", tooltip_session_length)
                                unhovered SetField(_tooltip, "value", _tooltip.default)

                            hbox:
                                style_prefix "addsub_fancy_check"
                                textbutton "-":
                                    text_size 40
                                    action [Function(store.sessionlength_sub), SensitiveIf(store.sessionlength_can_sub())]
                                    hovered SetField(_tooltip, "value", tooltip_session_length)
                                    unhovered SetField(_tooltip, "value", _tooltip.default)

                            hbox:
                                xsize 450
                                bar:
                                    xpos 20
                                    yoffset 5
                                    value DictValue(persistent.maica_setting_dict, "max_history_token", 28672-512,step=10,offset=512 ,style="slider")
                                    xsize 300
                                    hovered SetField(_tooltip, "value", tooltip_session_length)
                                    unhovered SetField(_tooltip, "value", _tooltip.default)
                                hbox:
                                    style_prefix "nf_check"
                                    textbutton _("[persistent.maica_setting_dict.get('max_history_token')]"):
                                        xalign 1.0
                                        action Show("maica_context_length_input")
                                        hovered SetField(_tooltip, "value", tooltip_session_length)
                                        unhovered SetField(_tooltip, "value", _tooltip.default)

                            hbox:
                                style_prefix "addsub_fancy_check"
                                textbutton "+":
                                    text_size 40
                                    action [Function(store.sessionlength_add), SensitiveIf(store.sessionlength_can_add())]
                                    hovered SetField(_tooltip, "value", tooltip_session_length)
                                    unhovered SetField(_tooltip, "value", _tooltip.default)

                        hbox:
                            frame:
                                xmaximum 950
                                xpos 30
                                xfill True
                                vbox:
                                    xmaximum 950
                                    xfill True
                                    $ tooltip_mf_info = _("由你补充的设定信息, 由MFocus检索并呈递到核心模型. 需要重新上传存档生效.")
                                    hbox:
                                        textbutton _("当前有[len(persistent.mas_player_additions)]条自定义MFocus信息"):
                                            action NullAction()
                                            hovered SetField(_tooltip, "value", tooltip_mf_info)
                                            unhovered SetField(_tooltip, "value", _tooltip.default)

                                    hbox:
                                        textbutton _("添加MFocus信息"):
                                            action [
                                                Hide("maica_setting"),
                                                Function(store.maica_apply_setting),
                                                Function(renpy.call_in_new_context, "maica_call_from_setting", "maica_mods_preferences")
                                                ]
                                            hovered SetField(_tooltip, "value", tooltip_mf_info)
                                            unhovered SetField(_tooltip, "value", _tooltip.default)

                                    hbox:
                                        textbutton _("编辑MFocus信息"):
                                            action [
                                                Hide("maica_setting"),
                                                Function(store.maica_apply_setting),
                                                Function(renpy.call_in_new_context, "maica_call_from_setting", "maica_mods_preferences")
                                                ]
                                            hovered SetField(_tooltip, "value", tooltip_mf_info)
                                            unhovered SetField(_tooltip, "value", _tooltip.default)

                                    hbox:
                                        textbutton _("清除MFocus信息"):
                                            action Function(reset_player_information)
                                            hovered SetField(_tooltip, "value", tooltip_mf_info)
                                            unhovered SetField(_tooltip, "value", _tooltip.default)

                                    hbox:
                                        textbutton _("导出自定义MFocus信息到主目录"):
                                            action Function(export_player_information)
                                            hovered SetField(_tooltip, "value", _("导出至game/Submods/MAICA_ChatSubmod/player_information.txt"))
                                            unhovered SetField(_tooltip, "value", _tooltip.default)




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
                                    Show("maica_mspire_setting")
                                ]
                            
                        hbox:
                            textbutton _("MSpire 使用缓存"):
                                action ToggleDict(persistent.maica_setting_dict, "mspire_use_cache", True, False)
                                hovered SetField(_tooltip, "value", _("启用MSpire缓存.\n* 会强制使用默认高级参数并固定最佳实践"))
                                unhovered SetField(_tooltip, "value", _tooltip.default)

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
                            textbutton _("信件回复时间"):
                                action NullAction()
                            bar:
                                value DictValue(persistent.maica_setting_dict, "mpostal_default_reply_time", 50000, step=1, offset=3600, style="slider")
                                xsize 150
                                hovered SetField(_tooltip, "value", _("回信所需要的最低时间"))
                                unhovered SetField(_tooltip, "value", _tooltip.default)

                            textbutton "[persistent.maica_setting_dict.get('mpostal_default_reply_time', 0) / 3600]h"


                        
                        hbox:
                            textbutton _("查看后端负载"):
                                action Show("maica_workload_stat")
                            
                            textbutton _("动态的天堂树林"):
                                action ToggleDict(persistent.maica_setting_dict, "use_anim_background", True, False)
                                hovered SetField(_tooltip, "value", _("使用动态摇曳和改良光影的天堂树林, 略微增加渲染压力. 重启生效\n如果产生显存相关错误, 删减精灵包或禁用此选项"))
                                unhovered SetField(_tooltip, "value", _tooltip.default)

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
                xpos 10
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
                
screen maica_select_language(ok_action = Hide("maica_select_language")):
    #登录输入账户窗口, 也用来用作通用的输入窗口
    ## Ensure other screens do not get input while this screen is displayed.s
    modal True
    zorder 225

    style_prefix "confirm"

    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            ymaximum 300
            xmaximum 800
            xfill True
            yfill False
            spacing 5


            hbox:
                style_prefix "check"
                textbutton _("zh | 简体中文"):
                    action SetDict(persistent.maica_setting_dict, "target_lang", store.maica.maica.MaicaAiLang.zh_cn)
                
                textbutton _("en | English"):
                    action SetDict(persistent.maica_setting_dict, "target_lang", store.maica.maica.MaicaAiLang.en)

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action ok_action          

default use_email = True
screen maica_login():
    modal True
    zorder 215

    style_prefix "confirm"

    frame:
        xalign 0.5
        yalign 0.5
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
        xalign 0.5
        yalign 0.5
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

screen maica_context_length_input():
    # 长度
    ## Ensure other screens do not get input while this screen is displayed.
    python:
        if '_max_history_token' not in persistent.maica_setting_dict:
            persistent.maica_setting_dict['_max_history_token'] = str(persistent.maica_setting_dict['max_history_token'])
        def apply_length():
            if persistent.maica_setting_dict['_max_history_token'] == "":
                persistent.maica_setting_dict['_max_history_token'] = '512'
            persistent.maica_setting_dict['max_history_token'] = int(persistent.maica_setting_dict['_max_history_token'])
            if persistent.maica_setting_dict['max_history_token'] < 512:
                persistent.maica_setting_dict['max_history_token'] = 512
            if persistent.maica_setting_dict['max_history_token'] > 28672:
                persistent.maica_setting_dict['max_history_token'] = 28672 
            del persistent.maica_setting_dict['_max_history_token']
    modal True
    zorder 225

    style_prefix "confirm"

    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            ymaximum 300
            xmaximum 800
            xfill True
            yfill False
            spacing 5

            label _("请输入上下文长度"):
                style "confirm_prompt"
                xalign 0.5
            hbox:
                input default str(persistent.maica_setting_dict['_max_history_token']) value DictInputValue(persistent.maica_setting_dict, "_max_history_token") length 5 allow "0123456789"

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action [
                    Function(apply_length),
                    Hide("maica_context_length_input")
                ]

screen maica_seed_input():
    python:
        if "_seed" not in persistent.maica_advanced_setting:
            persistent.maica_advanced_setting["_seed"] = str(persistent.maica_advanced_setting["seed"])
        def apply_seed():
            if persistent.maica_advanced_setting['_seed'] == "":
                persistent.maica_advanced_setting['_seed'] = '0'
            seed = int(persistent.maica_advanced_setting['_seed'])
            if seed > 2147483647:
                seed = 2147483647
            elif seed < -2147483648:
                seed = -2147483648
            persistent.maica_advanced_setting['seed'] = seed
            del persistent.maica_advanced_setting["_seed"]
                
    #seed输入
    ## Ensure other screens do not get input while this screen is displayed.s
    modal True
    zorder 225

    style_prefix "confirm"

    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            ymaximum 300
            xmaximum 800
            xfill True
            yfill False
            spacing 5

            label _("请输入种子(整数)"):
                style "confirm_prompt"
                xalign 0.5
            hbox:
                input default str(persistent.maica_advanced_setting['_seed']) value DictInputValue(persistent.maica_advanced_setting, "_seed") allow "-0123456789"

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action [
                    Function(apply_seed),
                    Hide("maica_seed_input")
                ]



screen maica_message(message = "Non Message", ok_action = Hide("maica_message")):
    modal True
    zorder 225

    style_prefix "confirm"

    frame:
        xalign 0.5
        yalign 0.5
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