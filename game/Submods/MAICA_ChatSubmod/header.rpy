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
        "max_history_token":8192,
        "status_update_time":1,
        "strict_mode": False,
        "show_console_when_reply": False,
        "mpostal_default_reply_time": 360,
        "42seed":False,
        "use_anim_background": True
    }
    import copy
    mdef_setting = copy.deepcopy(maica_default_dict)
    maica_advanced_setting = {
        "top_p":0.7,
        "temperature":0.22,
        "max_tokens":1600,
        "frequency_penalty":0.44,
        "presence_penalty":0.34,
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

    import time
    class ThrottleReturnNone(object):
        """This is a wrapper."""
        
        def __init__(self, wait):
            self.wait = wait
            self.last_called = 0.0
            self.remain = 0
            self.result = None
        
        def __call__(self, func):
            def wrapper(*args, **kwargs):
                now = time.time()
                elapsed = now - self.last_called
                
                if elapsed < self.wait:
                    pass
                else:
                    self.last_called = now
                    self.result = func(*args, **kwargs)

                self.remain = self.wait - elapsed
                if self.remain < 0.0:
                    self.remain = 0.0

                return None
            
            return wrapper

    store.workload_throttle = ThrottleReturnNone(15.0)
    store.nvw_folded = True
    store.stat_folded = True

    from bot_interface import PY2, PY3
    def iterize(dict):
        if PY2:
            return dict.iteritems()
        elif PY3:
            return dict.items()

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

    def run_migrations():
        if persistent.maica_setting_dict["mspire_interval"] <= 10:
            persistent.maica_setting_dict["mspire_interval"] = 10

    def maica_apply_setting(ininit=False):
        import copy
        run_migrations()
            
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
        store.persistent.maica_mtrigger_status = copy.deepcopy(store.maica.maica.mtrigger_manager.output_settings())
        store.mas_submod_utils.getAndRunFunctions()
        if store.maica.maica.target_lang == store.maica.maica.MaicaAiLang.zh_cn:
            store.maica.maica.MoodStatus.emote_translate = {}
        elif store.maica.maica.target_lang == store.maica.maica.MaicaAiLang.en:
            import json_exporter
            store.maica.maica.MoodStatus.emote_translate = json_exporter.emotion_etz
        
        if not ininit:
            renpy.notify(_("MAICA: 已上传设置") if store.maica.maica.send_settings() else _("MAICA: 请等待连接就绪后手动上传"))
            
    def maica_discard_setting():
        persistent.maica_setting_dict["auto_reconnect"] = store.maica.maica.auto_reconnect 

        # 没开42 但是相关设置改变了 证明之前开了42
        if not persistent.maica_setting_dict["42seed"] and (not persistent.maica_advanced_setting_status["seed"] and 'seed' in store.maica.maica.modelconfig):
            persistent.maica_setting_dict["42seed"] = True
        # 正常情况
        elif persistent.maica_setting_dict["42seed"] and (not persistent.maica_advanced_setting_status["seed"] and 'seed' in store.maica.maica.modelconfig):
            persistent.maica_setting_dict["42seed"] = True
        else:
            persistent.maica_setting_dict["42seed"] = False
        # maica_discard_advanced_setting()
        persistent.maica_setting_dict["sf_extraction"] = store.maica.maica.sf_extraction
        persistent.maica_setting_dict["chat_session"] = store.maica.maica.chat_session
        persistent.maica_setting_dict['enable_mf'] = store.maica.maica.enable_mf
        persistent.maica_setting_dict['enable_mt'] = store.maica.maica.enable_mt
        persistent.maica_setting_dict["mspire_use_cache"] = store.maica.maica.mspire_use_cache
        persistent.maica_setting_dict["console_font"] = store.mas_ptod.font
        persistent.maica_setting_dict["target_lang"] = store.maica.maica.target_lang
        persistent.maica_setting_dict["mspire_category"] = store.maica.maica.mspire_category
        persistent.maica_setting_dict["mspire_search_type"] = store.maica.maica.mspire_type
        persistent.maica_setting_dict["log_level"] = store.mas_submod_utils.submod_log.level
        persistent.maica_setting_dict["log_conlevel"] = store.maica.maica.console_logger.level
        # persistent.maica_setting_dict["mspire_session"] = store.maica.maica.mspire_session
        persistent.maica_setting_dict["provider_id"] = store.maica.maica.provider_id
        persistent.maica_setting_dict["max_history_token"] = store.maica.maica.max_history_token
        persistent.maica_setting_dict["strict_mode"] = store.maica.maica.enable_strict_mode
        store.maica.maica.mtrigger_manager.enable_map = store.persistent.maica_mtrigger_status

        renpy.notify(_("MAICA: 已放弃设置修改"))

    
    def maica_apply_advanced_setting():
        settings_dict = {}
        for k, v in persistent.maica_advanced_setting_status.items():
            if v:
                settings_dict[k] = persistent.maica_advanced_setting[k]
        store.maica.maica.modelconfig.update(settings_dict)
        store.mas_submod_utils.submod_log.info("Applying advanced settings: {}".format(settings_dict))
            
    def maica_discard_advanced_setting():
        settings_dict = {}
        for k, v in persistent.maica_advanced_setting_status.items():
            persistent.maica_advanced_setting_status[k] = k in store.maica.maica.modelconfig
            if k in store.maica.maica.modelconfig:
                persistent.maica_advanced_setting[k] = store.maica.maica.modelconfig[k]
            elif k in store.maica.maica.default_setting:
                persistent.maica_advanced_setting[k] = store.maica.maica.default_setting[k]

    def common_can_add(var, min, max, sdict):
        if isinstance(max, float):
            unit = 0.01
        else:
            unit = 1
        s_dict = getattr(persistent, sdict)
        return min <= s_dict[var] < max

    def common_add(var, min, max, sdict):
        if isinstance(max, float):
            unit = 0.01
        else:
            unit = 1
        s_dict = getattr(persistent, sdict)
        if common_can_add(var, min, max, sdict):
            s_dict[var] += unit
            if s_dict[var] > max:
                s_dict[var] = max

    def common_can_sub(var, min, max, sdict):
        if isinstance(max, float):
            unit = 0.01
        else:
            unit = 1
        s_dict = getattr(persistent, sdict)
        return min < s_dict[var] <= max

    def common_sub(var, min, max, sdict):
        if isinstance(max, float):
            unit = 0.01
        else:
            unit = 1
        s_dict = getattr(persistent, sdict)
        if common_can_sub(var, min, max, sdict):
            s_dict[var] -= unit
            if s_dict[var] < min:
                s_dict[var] = min



    def toggle_var(var):
        if getattr(store, var, None):
            setattr(store, var, False)
        else:
            setattr(store, var, True)


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

        use intro_tooltip()
        timer persistent.maica_setting_dict.get('status_update_time', 1.0) repeat True action Function(scr_nullfunc, _update_screens=True)
        vbox:
            xpos 400
            xsize 500
        
            if get_build_timescamp() < cn_mas_mobile_min_timescamp and renpy.android:
                hbox:

                    text _("> 你当前的MAS生成版本过旧, 可能影响正常运行, 请升级至最新生成版本"):
                        style "main_menu_version_l"

            if store.maica.maica.is_outdated is None:
                hbox:

                    text _("> 未能联网验证版本信息, 如果出现问题请尝试更新"):
                        style "main_menu_version_l"

            elif store.maica.maica.is_outdated is True:
                hbox:
         
                    text _("> 当前版本支持已终止, 请更新至最新版"):
                        style "main_menu_version_l"
            
            if renpy.android and not os.path.exists(os.path.join(ANDROID_MASBASE, 'game', 'python-packages', 'certifi', 'cacert.pem')):
                hbox:

                    text _("> 警告: 找不到证书, 你是不是忘记安装数据包了?"):
                        style "main_menu_version_l"

            if store.mas_submod_utils.isSubmodInstalled("Better Loading"):
                hbox:

                    text _("> 警告: 与 Better Loading 不兼容"):
                        style "main_menu_version_l"

            if store.mas_submod_utils.isSubmodInstalled("Log Screen"):
                hbox:

                    text _("> 警告: 与 Log Screen 一起使用时, 请将'submod_log'的过滤级别提高至info及以上"):
                        style "main_menu_version_l"

            hbox:

                text _("> MAICA通信状态: [maica.maica.status]|[maica.maica.MaicaAiStatus.get_description(maica.maica.status)]"):
                    style "main_menu_version_l"

            hbox:
   
                text renpy.substitute(_("> Websocket:")) + renpy.substitute(stat):
                    style "main_menu_version_l"

        if not maica.maica.is_accessable():
            textbutton _("> 使用账号生成令牌")
                # action Show("maica_login")
            
        elif not maica.maica.is_connected():
            textbutton _("> 使用账号生成令牌"):
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
                textbutton _("> 手动上传设置 [[请先等待连接建立]")
                     
                textbutton _("> 重置当前对话 [[现在暂时不能重置]")

            textbutton _("> 导出当前对话"):
                action Function(output_chat_history)
            
            textbutton _("> 上传对话历史到会话 '[store.maica.maica.chat_session]'"):
                action Function(upload_chat_history)

            textbutton renpy.substitute(_("> 退出当前DCC账号")) + " " + renpy.substitute(_("{size=-10}* 如果对话卡住, 退出以断开连接")):
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


screen maica_setting():
    
    python:
        store.len = len


    default tooltip = Tooltip("")
    
    python:
        submods_screen = store.renpy.get_screen("maica_setting", "screens")

        if submods_screen:
            store._tooltip = submods_screen.scope.get("tooltip", None)
        else:
            store._tooltip = None

        def reset_adv_to_default():
            for item in store.maica.maica.default_setting:
                if item == 'seed':
                    store.maica.maica.default_setting[item] = 0
                if item in persistent.maica_advanced_setting:
                    persistent.maica_advanced_setting[item] = store.maica.maica.default_setting[item]
                    persistent.maica_advanced_setting_status[item] = False

    $ _tooltip = store._tooltip

    $ w = 1100
    $ h = 640
    $ x = 0.5
    $ y = 0.5

    modal True
    zorder 215

    style_prefix "maica_check"

    use maica_common_outer_frame(w, h, x, y):
        use maica_common_inner_frame(w, h, x, y):

            if renpy.config.debug:

                text "=====MaicaAi()====="

                text "ai.is_responding: [store.maica.maica.is_responding()]"

                text "ai.is_failed: [store.maica.maica.is_failed()]"

                text "ai.is_connected: [store.maica.maica.is_connected()]"

                text "ai.is_ready_to_input: [store.maica.maica.is_ready_to_input()]"

                text "ai.MaicaAiStatus.is_submod_exception: [store.maica.maica.MaicaAiStatus.is_submod_exception(store.maica.maica.status)]"

                text "ai.len_message_queue(): [store.maica.maica.len_message_queue()]"

                text "maica_chr_exist: [maica_chr_exist]"

                text "maica_chr_changed: [maica_chr_changed]"

                text "len(mas_rev_unseen): [len(mas_rev_unseen)] | [mas_rev_unseen]"

                text "push_mpostal_read: [has_mail_waitsend() and _mas_getAffection() >= 100 and renpy.seen_label('maica_wants_mspire') and renpy.seen_label('maica_wants_mpostal') and not mas_inEVL('maica_mpostal_received') and not mas_inEVL('maica_mpostal_read')]"

                text "push_mspire_want: [renpy.seen_label('maica_greeting') and not renpy.seen_label('maica_wants_mspire') and renpy.seen_label('mas_random_ask')]"

                text "triggered_list: [store.maica.maica.mtrigger_manager.triggered_list]"

                textbutton "输出Event信息到日志":
                    action Function(log_eventstat)

                textbutton "推送分句测试":
                    action [
                                Hide("maica_setting"),
                                Function(store.maica_apply_setting),
                                Function(store.MASEventList.push, "text_split")
                            ]

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
                style_prefix "maica_check"
                textbutton _("服务提供节点: [MaicaProviderManager.get_server_by_id(persistent.maica_setting_dict.get('provider_id')).get('name', 'Unknown')]"):
                    action Show("maica_node_setting")
                    hovered SetField(_tooltip, "value", _("设置服务器节点"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                style_prefix "maica_check_nohover"
                $ user_disp = store.maica.maica.user_acc or _("未登录")
                textbutton _("当前用户: [user_disp]"):
                    action NullAction()
                    hovered SetField(_tooltip, "value", _("如需更换或退出账号, 请在Submods界面退出登录.\n* 要修改账号信息或密码, 请前往DCC论坛"))
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
                textbutton _("使用MFocus: [persistent.maica_setting_dict.get('enable_mf')]"):
                    action ToggleDict(persistent.maica_setting_dict, "enable_mf", True, False)
                    hovered SetField(_tooltip, "value", _("一个agent模型先于核心模型接收相同或相似的输入内容, 并调用工具以获取信息. 这些信息会被提供给核心模型.\n* MFocus是MAICA的重要功能之一, 一般不建议禁用"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("使用MTrigger: [persistent.maica_setting_dict.get('enable_mt')]"):
                    action ToggleDict(persistent.maica_setting_dict, "enable_mt", True, False)
                    hovered SetField(_tooltip, "value", _("一个agent模型后于核心模型接收本轮的输入输出, 并调用工具以指示前端作出角色行为.\n* MTrigger是MAICA的重要功能之一, 一般不建议禁用"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "maica_check"
                textbutton _("目标语言: [persistent.maica_setting_dict.get('target_lang')]"):
                    action Show("maica_select_language")
                    hovered SetField(_tooltip, "value", _("目标生成语言. 仅支持\"zh\"或\"en\".\n* 该参数不能100%保证生成语言是目标语言\n* 该参数影响范围广泛, 包括默认时区, 节日文化等, 并不止目标生成语言. 建议设为你的实际母语\n* 截至文档编纂时为止, MAICA官方部署的英文能力仍然弱于中文"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "maica_check"
                textbutton _("时区设置: [persistent.maica_advanced_setting.get('tz') or 'Asia/Shanghai' if store.maica.maica.target_lang == store.maica.maica.MaicaAiLang.zh_cn else 'America/Indiana/Vincennes']"):
                    action Show("maica_tz_setting")
            hbox:
                frame:
                    xmaximum 950
                    xpos 30
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("使用自定义高级参数: [persistent.maica_setting_dict.get('use_custom_model_config')]"):
                            action ToggleDict(persistent.maica_setting_dict, "use_custom_model_config", True, False)
                            hovered SetField(_tooltip, "value", _("高级参数可能大幅影响模型的表现.\n* 默认的高级参数已经是实践中的普遍最优配置, 不建议启用"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        style_prefix "maica_check"
                        if persistent.maica_setting_dict.get('use_custom_model_config'):
                            textbutton _("设置高级参数"):
                                style "maica_check_button"
                                action Show("maica_advance_setting")
                        else:
                            textbutton _("设置高级参数"):
                                style "maica_check_button_disabled"
                                action Show("maica_advance_setting")
                    hbox:
                        style_prefix "generic_fancy_check"
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

            $ tooltip_chat_session = _("每个session独立保存和应用对话记录.\n* 设为0以不记录和不使用对话记录(单轮对话)")
            use num_bar(_("当前会话"), 200, tooltip_chat_session, "chat_session", 0, 9)


            $ tooltip_session_length = _("会话保留的最大长度. 范围512-28672.\n* 按字符数计算. 每3个ASCII字符只占用一个字符长度\n* 字符数超过限制后, MAICA会裁剪其中较早的部分, 直至少于限制的 2/3\n* 过大或过小的值可能导致表现和性能问题")
            use prog_bar(_("会话长度"), 400, tooltip_session_length, "max_history_token", 512, 28672)


            hbox:
                frame:
                    xmaximum 950
                    xpos 30
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True
                    $ tooltip_mf_info = _("由你补充的设定信息, 由MFocus检索并呈递到核心模型. 需要重新上传存档生效.")
                    hbox:
                        style_prefix "maica_check_nohover"
                        textbutton _("当前有[len(persistent.mas_player_additions)]条自定义MFocus信息"):
                            action NullAction()
                            hovered SetField(_tooltip, "value", tooltip_mf_info)
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        #hbox:
                        #    style_prefix "maica_check"
                        #    textbutton _("添加MFocus信息"):
                        #        action [
                        #                        Hide("maica_setting"),
                        #                        Function(store.maica_apply_setting),
                        #                        Function(renpy.call_in_new_context, "maica_call_from_setting", "maica_mods_preferences")
                        #                        ]
                        #        hovered SetField(_tooltip, "value", tooltip_mf_info)
                        #        unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("编辑MFocus信息"):
                            #action [
                            #                Hide("maica_setting"),
                            #                Function(store.maica_apply_setting),
                            #                Function(renpy.call_in_new_context, "maica_call_from_setting", "maica_mods_preferences")
                            #                ]
                            action Show("maica_addition_setting")
                            hovered SetField(_tooltip, "value", tooltip_mf_info)
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                        #hbox:
                        #    style_prefix "maica_check"
                        #    textbutton _("清除MFocus信息"):
                        #        action Function(reset_player_information)
                        #        hovered SetField(_tooltip, "value", tooltip_mf_info)
                        #        unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("导出自定义MFocus信息到主目录"):
                            action Function(export_player_information)
                            hovered SetField(_tooltip, "value", _("导出至game/Submods/MAICA_ChatSubmod/player_information.txt"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                use divider(_("工具与功能"))

            if not persistent._mas_enable_random_repeats:
                hbox:
                    style_prefix "generic_fancy_check"
                    textbutton _("启用MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"):
                        action ToggleDict(persistent.maica_setting_dict, "mspire_enable", True, False)
                        hovered SetField(_tooltip, "value", _("是否允许由MSpire生成的对话.\n* 必须关闭复述话题才能启用\n* MSpire话题默认不使用MFocus"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)
            else:
                hbox:
                    textbutton _("启用MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"):
                        style "generic_fancy_check_button_disabled"
                        action ToggleDict(persistent.maica_setting_dict, "mspire_enable", True, False)
                        hovered SetField(_tooltip, "value", _("是否允许由MSpire生成的对话.\n! 复述话题已启用, MSpire不会生效"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                frame:
                    xpos 30
                    has vbox:
                        xsize 950
                    hbox:
                        style_prefix "maica_check"
                        textbutton _("MSpire话题"):
                            action Show("maica_mspire_category_setting")


                    $ tooltip_ms_time = _("MSpire对话的最小时间间隔")
                    use prog_bar(_("MSpire最小间隔"), 250, tooltip_ms_time, "mspire_interval", 10, 180, "m")


                    hbox:
                        style_prefix "maica_check"
                        textbutton _("MSpire搜索方式: [persistent.maica_setting_dict.get('mspire_search_type')]"):
                            action [
                                    Show("maica_mspire_setting")
                                        ]
                            hovered SetField(_tooltip, "value", _("MSpire搜索话题的模式"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("MSpire 使用缓存"):
                            action ToggleDict(persistent.maica_setting_dict, "mspire_use_cache", True, False)
                            hovered SetField(_tooltip, "value", _("启用MSpire缓存.\n* 会强制使用默认高级参数并固定最佳实践"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "maica_check"
                textbutton _("MTrigger 列表"):
                    action Show("maica_triggers")
                    hovered SetField(_tooltip, "value", _("查看和配置MTrigger条目"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)


            hbox:
                frame:
                    xmaximum 950
                    xpos 30
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True
                    hbox:
                        style_prefix "maica_check"
                        textbutton _("查看MPostals往来信件"):
                            action Show("maica_mpostals")
                            hovered SetField(_tooltip, "value", _("查看MPostal历史信件"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    $ tooltip_mp_time = _("MPostal回信的最小时间间隔")
                    use prog_bar(_("MPostal最小间隔"), 250, tooltip_mp_time, "mpostal_default_reply_time", 10, 720, "m")
            
            hbox:
                use divider(_("界面与日志"))

            hbox:
                style_prefix "maica_check"
                textbutton _("submod_log.log 等级:[logging.getLevelName(store.mas_submod_utils.submod_log.level)]"):
                    action Function(store.change_loglevel)
                    hovered SetField(_tooltip, "value", _("重要性低于设置等级的log将不会被记录在submod_log.log中.\n* 这也会影响其他子模组"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:

                use prog_bar(expl=_("状态码更新频率"), len=250, tooltip="在Submod界面处的状态码更新频率", var="status_update_time", min=1, max=60, istime="s")

            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("动态的天堂树林"):
                    action ToggleDict(persistent.maica_setting_dict, "use_anim_background", True, False)
                    hovered SetField(_tooltip, "value", _("使用动态摇曳和改良光影的天堂树林, 略微增加渲染压力. 重启生效\n* 如果产生显存相关错误, 删减精灵包或禁用此选项"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                frame:
                    xmaximum 950
                    xpos 30
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("输出到控制台: [persistent.maica_setting_dict.get('console')]"):
                            action ToggleDict(persistent.maica_setting_dict, "console", True, False)
                            hovered SetField(_tooltip, "value", _("在对话期间是否使用console显示相关信息, wzt的癖好\n说谁呢, 不觉得这很酷吗"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        style_prefix "maica_check"
                        textbutton _("控制台字体: [persistent.maica_setting_dict.get('console_font')]"):
                            action ToggleDict(persistent.maica_setting_dict, "console_font", store.maica_confont, store.mas_ui.MONO_FONT)
                            hovered SetField(_tooltip, "value", _("console使用的字体\nmplus-1mn-medium.ttf为默认字体\nSarasaMonoTC-SemiBold.ttf对于非英文字符有更好的显示效果"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("控制台log等级: [logging.getLevelName(store.maica.maica.console_logger.level)]"):
                            action Function(store.change_conloglevel)
                            hovered SetField(_tooltip, "value", _("重要性低于设置等级的log将不会显示在控制台中"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("回信时显示控制台"):
                            action ToggleDict(persistent.maica_setting_dict, "show_console_when_reply", True, False)

            hbox:
                use divider(_("统计与信息"))

            hbox:
                style_prefix "maica_check"
                textbutton (_("展开性能监控") if store.nvw_folded else _("收起性能监控")):
                    action [
                        Function(toggle_var, "nvw_folded")
                        ]
                    hovered SetField(_tooltip, "value", _("显示/收起服务器的性能状态指标"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            if not store.nvw_folded:
                hbox:
                    xpos 30
                    use maica_workload_stat()

            hbox:
                style_prefix "maica_check"
                textbutton (_("展开统计数据") if store.stat_folded else _("收起统计数据")):
                    action [
                        Function(toggle_var, "stat_folded")
                        ]
                    hovered SetField(_tooltip, "value", _("显示/收起你的使用统计数据"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            if not store.stat_folded:
                hbox:
                    xpos 30
                    use maica_statics()


        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("保存设置"):
                action [
                        Function(store.maica_apply_setting),
                        Hide("maica_setting")
                        ]
            textbutton _("放弃修改"):
                action [
                        Function(store.maica_discard_setting),
                        Hide("maica_setting")
                        ]
            textbutton _("重置设置"):
                action [
                        Function(reset_adv_to_default),
                        Function(store.maica_reset_setting),
                        Function(store.maica_apply_setting, ininit = True),
                        Function(renpy.notify, _("MAICA: 已重置设置")),
                        Hide("maica_setting")
                    ]

    if tooltip.value:
        frame:
            xalign 0 yalign 1.0
            xoffset 475 yoffset -25
            text tooltip.value:
                style "main_menu_version"


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