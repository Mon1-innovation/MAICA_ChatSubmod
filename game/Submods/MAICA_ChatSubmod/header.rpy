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
            attachment_id=0
        )

default persistent.maica_setting_dict = {
    "auto_reconnect":False,
    "auto_resume":False,
    "keep_alive":True,
    "maica_model":None,
    "use_custom_model_config":False,
    "savefile_access":True,
    "chat_session":1,
    "console":True,
    "gen_quality_chk":True,
    "input_lang_detect":True,
    "pprt":True
}
default persistent.maica_advanced_setting = {}
default persistent.maica_advanced_setting_status = {}
default persistent.mas_player_additions = []
default persistent._maica_reseted = False
default persistent._maica_target_lang_mode = None
default persistent._maica_tz_mode = None

define maica_confont = "mod_assets/font/SarasaMonoTC-SemiBold.ttf"
#define "mod_assets/font/mplus-1mn-medium.ttf" # mas_ui.MONO_FONT
init 10 python:
    import logging

    maica_timezone_dict = {
        -12: "Etc/GMT+12",
        -11: "Pacific/Midway",
        -10: "Pacific/Honolulu",
        -9: "America/Anchorage",
        -8: "America/Los_Angeles",
        -7: "America/Denver",
        -6: "America/Chicago",
        -5: "America/New_York",
        -4: "America/Indiana/Vincennes",
        -3: "America/Argentina/Buenos_Aires",
        -2: "Atlantic/South_Georgia",
        -1: "Atlantic/Azores",
        0: "Europe/London",
        1: "Europe/Berlin",
        2: "Europe/Kaliningrad",
        3: "Europe/Moscow",
        4: "Asia/Dubai",
        5: "Asia/Karachi",
        6: "Asia/Dhaka",
        7: "Asia/Bangkok",
        8: "Asia/Shanghai",
        9: "Asia/Tokyo",
        10: "Australia/Sydney",
        11: "Pacific/Noumea",
        12: "Pacific/Auckland",
        13: "Pacific/Tongatapu",
        14: "Pacific/Kiritimati",
    }

    def maica_get_default_target_lang():
        return {
            "chinese": "zh",
            "english": "en",
        }.get(config.language, "auto")

    def maica_get_system_timezone():
        import os
        import time

        timezone = os.environ.get("TZ")
        if timezone and "/" in timezone and not timezone.startswith(":"):
            return timezone

        for timezone_file in ("/etc/timezone", "/etc/TZ"):
            try:
                with open(timezone_file, "r") as timezone_stream:
                    timezone = timezone_stream.read().strip()
                if timezone and "/" in timezone:
                    return timezone
            except (IOError, OSError):
                pass

        try:
            localtime_path = os.path.realpath("/etc/localtime")
            marker = "zoneinfo" + os.sep
            if marker in localtime_path:
                return localtime_path.split(marker, 1)[1].replace(os.sep, "/")
        except (AttributeError, OSError):
            pass

        is_dst = time.localtime().tm_isdst > 0
        offset_seconds = -(time.altzone if is_dst and time.daylight else time.timezone)
        offset_minutes = int(offset_seconds // 60)
        # Python 2 has no cross-platform IANA lookup, so use representative zones by offset.
        fractional_timezones = {
            -570: "Pacific/Marquesas",
            -210: "America/St_Johns",
            -150: "America/St_Johns",
            210: "Asia/Tehran",
            270: "Asia/Kabul",
            330: "Asia/Kolkata",
            345: "Asia/Kathmandu",
            390: "Asia/Yangon",
            525: "Australia/Eucla",
            570: "Australia/Darwin",
            630: "Australia/Adelaide",
            765: "Pacific/Chatham",
            825: "Pacific/Chatham",
        }
        if offset_minutes in fractional_timezones:
            return fractional_timezones[offset_minutes]
        if offset_minutes % 60 == 0:
            return maica_timezone_dict.get(offset_minutes // 60)
        return None

    if persistent._maica_target_lang_mode is None:
        persistent._maica_target_lang_mode = (
            "manual" if "target_lang" in persistent.maica_setting_dict else "renpy"
        )
    if persistent._maica_tz_mode is None:
        persistent._maica_tz_mode = (
            "manual" if "tz" in persistent.maica_setting_dict else "system"
        )

    maica_default_dict = {
        "auto_reconnect":False,
        "auto_resume":False,
        "keep_alive":True,
        "enable_mf":True,
        "enable_mt":True,
        "use_custom_model_config":False,
        "savefile_access":True,
        "chat_session":1,
        "console":True,
        "console_font":maica_confont,
        "target_lang":maica_get_default_target_lang(),
        "mspire_enable":True,
        "mspire_category":[],
        "mspire_interval":60,
        "mspire_search_type":"in_fuzzy_all",
        "mspire_session":0,
        "mspire_use_cache":True,
        "log_level":logging.DEBUG,
        "log_conlevel":logging.INFO,
        "provider_id":1 if renpy.windows else 2,
        "session_len_limit":8192,
        "status_update_time":1,
        "strict_mode": False,
        "show_console_when_reply": False,
        "mpostal_default_reply_time": 360,
        "use_anim_background": True,
        "tz":maica_get_system_timezone(),
        "gen_quality_chk":True,
        "input_lang_detect":True,
        "pprt":True
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
        "mf_llm_concl":False,
        "prompt_pname_repl":False,
        "mf_const_tools":1,
        "esearch_llm_concl":True,
        "nsfw_acceptive":True,
        "mf_context_rnds":0,
        "mt_context_rnds":1,
        "mf_precheck_mt":True,
        "mf_disable_loop":True,
        "mt_disable_loop":True,
        "gen_enforce_lang":True,
        "mf_sf_access_impl":1,
        "mf_const_sf_access":0,
        "mt_concl_memory":1,
        "prompt_allow_nickname":True,
    }
    maica_advanced_default_setting = copy.deepcopy(maica_advanced_setting)

    maica_hyperparameter_setting_keys = (
        "max_tokens",
        "seed",
        "top_p",
        "temperature",
        "frequency_penalty",
        "presence_penalty",
    )
    maica_behavior_setting_keys = (
        "enable_mf",
        "enable_mt",
        "gen_quality_chk",
        "input_lang_detect",
        "pprt",
        "use_custom_model_config",
    )
    maica_behavior_advanced_setting_keys = tuple(
        key for key in maica_advanced_default_setting
        if key not in maica_hyperparameter_setting_keys
    )

    # behavior:
        # "enable_mf",
        # "enable_mt",
        # "gen_quality_chk",
        # "input_lang_detect",
        # "pprt",
        # "use_custom_model_config",
        # "mf_llm_concl":False,
        # "prompt_pname_repl":False,
        # "mf_const_tools":1,
        # "esearch_llm_concl":True,
        # "nsfw_acceptive":True,
        # "mf_context_rnds":0,
        # "mt_context_rnds":1,
        # "mf_precheck_mt":True,
        # "mf_disable_loop":True,
        # "mt_disable_loop":True,
        # "gen_enforce_lang":True,
        # "mf_sf_access_impl":1,
        # "mf_const_sf_access":0,
        # "mt_concl_memory":1,
        # "prompt_allow_nickname":True,

    # super:
        # "top_p":0.7,
        # "temperature":0.22,
        # "max_tokens":1600,
        # "frequency_penalty":0.44,
        # "presence_penalty":0.34,
        # "seed":0,

    # Preset settings use the existing flat setting names. Advanced entries are
    # enabled when declared; omitted entries are reset to their defaults.
    maica_behavior_presets = [
        {
            "name": "纯粹",
            "description": "最大程度缩减prompt, 几乎不启用任何工具, 只保留核心纠错.\n+ 速度最快, TTFT接近最短\n- 几乎没有感知能力, 不能调用游戏内操作",
            "settings": {
                "enable_mf": False,
                "enable_mt": False,
                "gen_quality_chk": False,
                "use_custom_model_config": True,
                "mf_const_tools": 0,
                "nsfw_acceptive": False,
                "gen_enforce_lang": False,
                "mf_const_sf_access": 0,
                "mt_concl_memory": 0,
                "prompt_allow_nickname": False,
            },
        },
        {
            "name": "流利",
            "description": "不让常规LLM介入前生成阶段, 仅依靠常态工具, 优先压低TTFT. 适当减少其余工具.\n+ 速度较快, TTFT接近最短\n* 有较弱感知能力, 能调用游戏内操作",
            "settings": {
                "enable_mf": False,
                "use_custom_model_config": True,
                "mt_context_rnds": 0,
                "mf_precheck_mt": False,
                "mf_sf_access_impl": 2,
            },
        },
        {
            "name": "灵活",
            "description": "在默认行为基础上采用偏激进的调校, 牺牲稳定性和不常用的功能, 换取平均速度.\n+ 速度较快, TTFT较短\n+ 有正常感知能力, 能调用游戏内操作",
            "settings": {
                "gen_quality_chk": False,
                "use_custom_model_config": True,
                "mf_const_tools": 2,
                "esearch_llm_concl": False,
                "mt_context_rnds": 0,
                "mf_precheck_mt": False,
                "mf_sf_access_impl": 2,
            },
        },
        {
            "name": "均衡(默认)",
            "description": "MAICA的默认行为. 久经考验的平衡调校, 在绝大多数情况下表现最佳.\n* 速度中等, TTFT中等\n+ 有正常感知能力, 能调用游戏内操作",
            "settings": {},
        },
        {
            "name": "完全",
            "description": "几乎完整启用生成辅助功能集. 在极端情况下可能表现更好, 但一般都是浪费时间.\n- 速度最慢, TTFT最长\n+ 有正常感知能力, 能调用游戏内操作",
            "settings": {
                "use_custom_model_config": True,
                "mf_llm_concl": True,
                "mf_context_rnds": 1,
                "mf_disable_loop": False,
                "mt_disable_loop": False,
            },
        },
    ]
    maica_hyperparameter_presets = [
        {
            "name": "贪婪",
            "description": "固定种子, 贪婪采样.\n! 非特殊情况不推荐",
            "settings": {
                "temperature": 0.0,
                "seed": 42,
            },
        },
        {
            "name": "胆怯",
            "description": "较低的温度.\n! 非特殊情况不推荐",
            "settings": {
                "temperature": 0.10,
            },
        },
        {
            "name": "标准(默认)",
            "description": "MAICA的默认超参数. 久经考验的平衡调校, 在绝大多数情况下表现最佳.",
            "settings": {},
        },
        {
            "name": "冒进",
            "description": "较高的温度和采样范围.\n! 非特殊情况不推荐",
            "settings": {
                "temperature": 0.35,
                "top_p": 0.8,
            },
        },
    ]

    def _maica_preset_definition(preset_type):
        if preset_type == "behavior":
            return (
                maica_behavior_presets,
                maica_behavior_setting_keys,
                maica_behavior_advanced_setting_keys,
            )
        if preset_type == "hyperparameter":
            return (
                maica_hyperparameter_presets,
                (),
                maica_hyperparameter_setting_keys,
            )
        raise ValueError("Unknown MAICA preset type: {}".format(preset_type))

    def _maica_validate_presets():
        for preset_type in ("behavior", "hyperparameter"):
            presets, setting_keys, advanced_keys = _maica_preset_definition(preset_type)
            allowed_keys = set(setting_keys + advanced_keys)
            for preset in presets:
                missing_fields = set(("name", "description", "settings")) - set(preset)
                if missing_fields:
                    raise ValueError("MAICA preset is missing fields: {}".format(sorted(missing_fields)))
                if not isinstance(preset["settings"], dict):
                    raise ValueError("MAICA preset settings must be a dictionary")
                unknown_keys = set(preset["settings"]) - allowed_keys
                if unknown_keys:
                    raise ValueError("MAICA preset contains unsupported settings: {}".format(sorted(unknown_keys)))

    def maica_apply_preset(preset_type, preset):
        presets, setting_keys, advanced_keys = _maica_preset_definition(preset_type)
        preset_settings = preset["settings"]

        for key in setting_keys:
            persistent.maica_setting_dict[key] = copy.deepcopy(mdef_setting[key])
        for key in advanced_keys:
            persistent.maica_advanced_setting[key] = copy.deepcopy(maica_advanced_default_setting[key])
            persistent.maica_advanced_setting_status[key] = False

        for key, value in preset_settings.items():
            if key in setting_keys:
                persistent.maica_setting_dict[key] = copy.deepcopy(value)
            else:
                persistent.maica_advanced_setting[key] = copy.deepcopy(value)
                persistent.maica_advanced_setting_status[key] = True

    def maica_preset_matches(preset_type, preset):
        presets, setting_keys, advanced_keys = _maica_preset_definition(preset_type)
        preset_settings = preset["settings"]

        for key in setting_keys:
            expected = preset_settings.get(key, mdef_setting[key])
            if persistent.maica_setting_dict.get(key) != expected:
                return False
        for key in advanced_keys:
            expected = preset_settings.get(key, maica_advanced_default_setting[key])
            expected_enabled = key in preset_settings
            if persistent.maica_advanced_setting.get(key) != expected:
                return False
            if persistent.maica_advanced_setting_status.get(key, False) != expected_enabled:
                return False
        return True

    def maica_get_matching_preset(preset_type):
        presets, setting_keys, advanced_keys = _maica_preset_definition(preset_type)
        for preset in presets:
            if maica_preset_matches(preset_type, preset):
                return preset
        return None

    def maica_get_preset_name(preset_type):
        preset = maica_get_matching_preset(preset_type)
        return _(preset["name"]) if preset else _("自定义")

    _maica_validate_presets()
    maica_advanced_setting_status = {k: False for k, v in maica_advanced_setting.items()}
    persistent.maica_setting_dict.pop("42seed", None)
    maica_default_dict.update(persistent.maica_setting_dict)
    maica_advanced_setting.update(persistent.maica_advanced_setting)
    maica_advanced_setting_status.update(persistent.maica_advanced_setting_status)
    if persistent._maica_target_lang_mode == "renpy":
        maica_default_dict["target_lang"] = maica_get_default_target_lang()
    if persistent._maica_tz_mode == "system":
        maica_default_dict["tz"] = maica_get_system_timezone()

    persistent.maica_setting_dict = maica_default_dict.copy()
    persistent.maica_advanced_setting = maica_advanced_setting.copy()
    persistent.maica_advanced_setting_status = maica_advanced_setting_status.copy()

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
        store.mas_api_keys.api_keys.update({"Maica_Token":store.maica.maica_instance.ciphertext})
        store.mas_api_keys.save_keys()
    
    def maica_reset_setting():
        persistent.maica_setting_dict = mdef_setting.copy()
        sync_provider_id(persistent.maica_setting_dict["provider_id"])
        persistent.mas_geolocation = ''
        persistent.mas_player_additions = []
        persistent.maica_setting_dict["mspire_category"] = []

    def maica_clamp_advanced_setting(key, lower, upper):
        value = int(persistent.maica_advanced_setting.get(key, lower))
        persistent.maica_advanced_setting[key] = max(lower, min(value, upper))

    def maica_escape_display_text(text):
        return text.replace("[", "[[").replace("{", "{{")

    def maica_selected_item(items, selected_indices):
        if len(selected_indices) != 1:
            return None
        index = next(iter(selected_indices))
        if index < 0 or index >= len(items):
            return None
        return items[index]

    def maica_delete_selected_items(items, selected_indices):
        items[:] = [item for index, item in enumerate(items) if index not in selected_indices]
        selected_indices.clear()

    def maica_validate_player_addition(raw_addition, additions, edittarget=None, prefix_player=True):
        if not isinstance(raw_addition, (str, unicode)) or not raw_addition.strip():
            renpy.notify(_("MAICA: 输入为空"))
            return None
        addition = ("{player_name}" + raw_addition.strip() if prefix_player else raw_addition.strip())
        replacing = edittarget in additions
        if len(additions) >= 512:
            if not replacing:
                renpy.notify(_("MAICA: 自定义MFocus信息已达512条上限"))
                return None
        if len(addition.encode("utf-8")) > 1536:
            renpy.notify(_("MAICA: 单条自定义MFocus信息不能超过1536字节"))
            return None
        if addition in additions and addition != edittarget:
            renpy.notify(_("MAICA: 已存在相同内容"))
            return None
        return addition

    def _maica_verify_token():
        res = store.maica.maica_instance._verify_token()
        if res.get("success"):
            renpy.show_screen("maica_message", message=_("验证成功"))
        else:
            store.mas_api_keys.api_keys.update({"Maica_Token":""})
            store.maica.maica_instance.ciphertext = ""
            renpy.show_screen("maica_message", message=renpy.substitute(_("验证失败, 请检查账号密码")) + "\n" + renpy.substitute(_("失败原因: ")) + res.get("exception"))
            

    @store.mas_submod_utils.functionplugin("ch30_preloop")
    def _upload_persistent_dict():
        if not store.maica.savefile_access_marker_exists():
            store.mas_submod_utils.submod_log.info("MAICA: Skip savefile upload because savefile_access marker is missing")
            return

        max_bytes = 1536
        import copy, maica_v13_migration
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
                if maica_v13_migration.utf8_byte_length(value) > max_bytes:
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
        res = store.maica.maica_instance.upload_save(d)
        if not res.get("success", False):
            store.mas_submod_utils.submod_log.error("ERROR: upload save failed: {}".format(res.get("exception", "unknown")))
        renpy.notify(_("MAICA: 存档上传成功") if res.get("success", False) else _("MAICA: 存档上传失败"))

    def reset_session():
        store.maica.maica_instance.reset_chat_session()
        renpy.notify(_("MAICA: 会话已重置"))
    def output_chat_history():
        import json
        with open(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "chat_history.txt"), 'w') as f:
            f.write(json.dumps(store.maica.maica_instance.get_history().get("content") or []))
        renpy.notify(_("MAICA: 历史已导出至game/Submods/MAICA_ChatSubmod/chat_history.txt"))
    
    def upload_chat_history():
        import json
        if not os.path.exists(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "chat_history.txt")):
            renpy.notify(_("MAICA: 未找到历史game/Submods/MAICA_ChatSubmod/chat_history.txt"))
            return
        with open(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "chat_history.txt"), 'r') as f:
            #history = json.load(f)
            try:
                history = json.load(f)
                res = store.maica.maica_instance.upload_history(history)
                if not res.get("success", False):
                    raise Exception(str(res))
            except Exception as e:
                store.mas_submod_utils.submod_log.error("upload_chat_history failed: {}".format(e))
                renpy.notify(_("MAICA: 历史上传失败, 查看submod_log获取详细原因."))
                return
        renpy.notify(_("MAICA: 历史上传成功"))

    def run_migrations():
        if persistent.maica_setting_dict["mspire_interval"] <= 10:
            persistent.maica_setting_dict["mspire_interval"] = 10

    def maica_apply_setting(ininit=False):
        import copy
        run_migrations()

        store.maica.maica_instance.auto_reconnect = persistent.maica_setting_dict["auto_reconnect"]
        if store.maica.maica_instance.auto_reconnect:
            store.maica.maica_instance.AutoReconnector.enable()
        else:
            store.maica.maica_instance.AutoReconnector.disable()
        store.maica.maica_instance.auto_resume = persistent.maica_setting_dict["auto_resume"]
        if store.maica.maica_instance.auto_resume:
            store.maica.maica_instance.AutoResumeTasker.enable()
        else:
            store.maica.maica_instance.AutoResumeTasker.disable()
        store.maica.maica_instance.keep_alive = persistent.maica_setting_dict["keep_alive"]
        if store.maica.maica_instance.keep_alive:
            store.maica.maica_instance.KeepAliveTasker.enable()
        else:
            store.maica.maica_instance.KeepAliveTasker.disable()
        if persistent.maica_setting_dict["use_custom_model_config"]:
            maica_apply_advanced_setting()
        else:
            store.maica.maica_instance.modelconfig = {}
        
        store.maica.maica_instance.savefile_access = persistent.maica_setting_dict["savefile_access"]
        store.maica.maica_instance.chat_session = persistent.maica_setting_dict["chat_session"]
        store.maica.maica_instance.enable_mf = persistent.maica_setting_dict['enable_mf']
        store.maica.maica_instance.enable_mt = persistent.maica_setting_dict['enable_mt']
        store.maica.maica_instance.mspire_use_cache = persistent.maica_setting_dict["mspire_use_cache"]
        store.mas_ptod.font = persistent.maica_setting_dict["console_font"]
        store.maica.maica_instance.target_lang = persistent.maica_setting_dict["target_lang"]
        store.maica.maica_instance.mspire_category = persistent.maica_setting_dict["mspire_category"]
        store.maica.maica_instance.mspire_type = persistent.maica_setting_dict["mspire_search_type"]
        store.mas_submod_utils.submod_log.level = persistent.maica_setting_dict["log_level"]
        store.maica.maica_instance.console_logger.level = persistent.maica_setting_dict["log_conlevel"]
        store.maica.maica_instance.mspire_session = persistent.maica_setting_dict["mspire_session"]
        store.maica.maica_instance.provider_id = persistent.maica_setting_dict["provider_id"]
        store.maica.maica_instance.max_history_token = min(persistent.maica_setting_dict["session_len_limit"], 28672)
        store.maica.maica_instance.tz = persistent.maica_setting_dict["tz"]
        store.maica.maica_instance.gen_quality_chk = persistent.maica_setting_dict["gen_quality_chk"]
        store.maica.maica_instance.input_lang_detect = persistent.maica_setting_dict["input_lang_detect"]
        store.maica.maica_instance.pprt = persistent.maica_setting_dict["pprt"]
        store.persistent.maica_mtrigger_status = copy.deepcopy(store.maica.maica_instance.mtrigger_manager.output_settings())
        store.mas_submod_utils.getAndRunFunctions()
        if store.maica.maica_instance.target_lang == store.maica.maica_instance.MaicaAiLang.zh_cn:
            store.maica.maica_instance.MoodStatus.emote_translate = {}
        elif store.maica.maica_instance.target_lang == store.maica.maica_instance.MaicaAiLang.en:
            import json_exporter
            store.maica.maica_instance.MoodStatus.emote_translate = json_exporter.emotion_etz
        if not persistent.maica_setting_dict.get('mspire_enable') and mas_inEVL("maica_mspire"):
            store.MASEventList.clean()
        send_success = store.maica.maica_instance.send_settings()
        if not ininit:
            renpy.notify(_("MAICA: 已上传设置") if send_success else _("MAICA: 请等待连接就绪后手动上传"))
            
    def maica_discard_setting():
        persistent.maica_setting_dict["auto_reconnect"] = store.maica.maica_instance.auto_reconnect
        persistent.maica_setting_dict["auto_resume"] = store.maica.maica_instance.auto_resume
        persistent.maica_setting_dict["keep_alive"] = store.maica.maica_instance.keep_alive

        persistent.maica_setting_dict["savefile_access"] = store.maica.maica_instance.savefile_access
        persistent.maica_setting_dict["chat_session"] = store.maica.maica_instance.chat_session
        persistent.maica_setting_dict['enable_mf'] = store.maica.maica_instance.enable_mf
        persistent.maica_setting_dict['enable_mt'] = store.maica.maica_instance.enable_mt
        persistent.maica_setting_dict["mspire_use_cache"] = store.maica.maica_instance.mspire_use_cache
        persistent.maica_setting_dict["console_font"] = store.mas_ptod.font
        persistent.maica_setting_dict["target_lang"] = store.maica.maica_instance.target_lang
        persistent.maica_setting_dict["mspire_category"] = store.maica.maica_instance.mspire_category
        persistent.maica_setting_dict["mspire_search_type"] = store.maica.maica_instance.mspire_type
        persistent.maica_setting_dict["log_level"] = store.mas_submod_utils.submod_log.level
        persistent.maica_setting_dict["log_conlevel"] = store.maica.maica_instance.console_logger.level
        persistent.maica_setting_dict["mspire_session"] = store.maica.maica_instance.mspire_session
        persistent.maica_setting_dict["provider_id"] = store.maica.maica_instance.provider_manager._provider_id
        persistent.maica_setting_dict["session_len_limit"] = min(store.maica.maica_instance.max_history_token, 28672)
        persistent.maica_setting_dict["tz"] = store.maica.maica_instance.tz
        persistent.maica_setting_dict["gen_quality_chk"] = store.maica.maica_instance.gen_quality_chk
        persistent.maica_setting_dict["input_lang_detect"] = store.maica.maica_instance.input_lang_detect
        persistent.maica_setting_dict["pprt"] = store.maica.maica_instance.pprt
        store.maica.maica_instance.mtrigger_manager.enable_map = store.persistent.maica_mtrigger_status

        renpy.notify(_("MAICA: 已放弃设置修改"))

    
    def maica_apply_advanced_setting():
        settings_dict = {}
        for k, v in persistent.maica_advanced_setting_status.items():
            if v:
                settings_dict[k] = persistent.maica_advanced_setting[k]
        store.maica.maica_instance.modelconfig.update(settings_dict)
        store.mas_submod_utils.submod_log.info("Applying advanced settings: {}".format(settings_dict))
            
    def maica_discard_advanced_setting():
        settings_dict = {}
        for k, v in persistent.maica_advanced_setting_status.items():
            persistent.maica_advanced_setting_status[k] = k in store.maica.maica_instance.modelconfig
            if k in store.maica.maica_instance.modelconfig:
                persistent.maica_advanced_setting[k] = store.maica.maica_instance.modelconfig[k]
            elif k in store.maica.maica_instance.default_setting:
                persistent.maica_advanced_setting[k] = store.maica.maica_instance.default_setting[k]


    def sync_provider_id(pid, reconnect=True):
        """
        切换服务提供节点并, 立刻生效.
        - 写入 persistent.maica_setting_dict["provider_id"]
        - 更新 provider_manager.provider_id
        - 断开当前已连接的 websocket (如有), 重新 accessable() 并重连
        """
        import threading, time
        ai = store.maica.maica_instance
        try:
            pid = int(pid)
        except Exception:
            pid = 0
        persistent.maica_setting_dict["provider_id"] = pid
        ai.provider_id = pid 
        # ai.provider_manager.set_provider_id(pid)

        # 刷新 vista_manager 缓存的 base_url
        ai.vista_manager.base_url = ai.provider_manager.get_api_url()

        # 如果已连接 websocket：先断开旧连接
        if reconnect:
            if ai.is_connected():
                ai.close_wss_session()
            

        # 后台处理的东西 (刷新节点列表、重新 accessable()、再重连) 走threading (避免卡住 UI)
        def _bg():
            try:
                ai.provider_manager.get_provider()
                ai.disable()
                ai.status = ai.MaicaAiStatus.WAIT_AVAILABILITY
                ai.accessable()

                if reconnect and ai.has_token():
                    # 等待旧 ws loop 释放 multi_lock，再启动新连接（一次性短轮询，不是永久时钟循环）
                    for _ in range(60):  # ~6s
                        try:
                            if not ai.multi_lock.locked():
                                break
                        except Exception:
                            break
                        time.sleep(0.1)

                    ai.init_connect()

            except Exception as e:
                store.mas_submod_utils.submod_log.error("Failed to sync provider id: {}".format(e))

        try:
            threading.Thread(target=_bg).start()
        except Exception:
            pass

        
        renpy.notify(_("MAICA: 已切换节点, 正在重新连接"))
        renpy.restart_interaction()
        

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
        renpy.notify(_("MAICA: 信息已导出至game/Submods/MAICA_ChatSubmod/player_information.txt"))

    def update_model_setting(ininit = False):
        import os, json
        try:
            with open(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "custom_modelconfig.json"), "r") as f:
                store.maica.maica_instance.modelconfig = json.load(f)
        except Exception as e:
            if not ininit:
                renpy.notify(_("MAICA: 加载高级参数失败, 查看submod_log.log获取详细原因").format(e))
            store.mas_submod_utils.submod_log.error("Failed to load custom model config: {}".format(e))
    
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
    #log_eventstat()
        

init python:
    def scr_nullfunc():
        return            


screen maica_setting_pane():

    on "show" action Function(store.maica.refresh_setting_pane_cache)

    python:
        import store.maica as maica
        pane_cache = maica.maica_setting_pane_cache
        stat = _("未连接") if not maica.maica_instance.wss_session else _("已连接") if maica.maica_instance.is_connected() else _("已断开")
        store.maica.maica_instance.ciphertext = store.mas_getAPIKey("Maica_Token")
        log_hasupdate = persistent._maica_updatelog_version_seen < store.maica.update_info.get("version", 0)
        version_check = pane_cache.get("version_check", None)

    vbox:
        # background None
        # has vbox:
            # yfit True

        vbox:
            spacing 5
            xpos 45
            xsize 900

            text "":
                size 0

            if get_build_timescamp() < cn_mas_mobile_min_timescamp and renpy.android:
                hbox:

                    text _("> 你当前的MAS构建版本过旧, 可能影响正常运行, 请升级至最新版本"):
                        style "main_menu_version_l"

            elif store.maica.maica_instance.is_outdated is True:
                hbox:
            
                    text _("> {color=#ff0000}当前版本支持已终止{/color}, 请更新至最新版"):
                        style "main_menu_version_l"
            
            if pane_cache.get("cacert_missing", False):
                hbox:

                    text _("> 警告: {color=#ff0000}找不到证书{/color}, 你是不是忘记安装数据包了?"):
                        style "main_menu_version_l"

            if pane_cache.get("better_loading_installed", False):
                hbox:

                    text _("> 警告: {color=#ff0000}与 Better Loading 不兼容{/color}"):
                        style "main_menu_version_l"

            if pane_cache.get("log_screen_installed", False):
                hbox:

                    text _("> 警告: 与 Log Screen 一起使用时, 请将'submod_log'的过滤级别提高至info及以上"):
                        style "main_menu_version_l"

            if version_check is not None:
                $ res, libv, uiv = version_check
                if res is None:
                    hbox:

                        text _("> 警告: 未检测到MAICA库版本信息. 请从Release下载安装MAICA, {color=#ff0000}而不是源代码{/color}"):
                            style "main_menu_version_l"
                elif res != 0:
                    hbox:

                        text _("> 警告: MAICA库版本[libv]与UI版本[uiv]不符. 请{color=#ff0000}从Release{/color}完整地更新MAICA"):
                            style "main_menu_version_l"

            if renpy.windows and not pane_cache.get("is_zhcn", True):
                hbox:

                    text _("> 警告: {color=#ff0000}当前系统非Unicode语言不是简体中文{/color}, 可能导致包含中文的响应出现问题"):
                        style "main_menu_version_l"

            if 13400 <= maica.maica_instance.status <= 13499:
                hbox:
                    text _("> MAICA通信状态: [maica.maica_instance.status]|[maica.maica_instance.MaicaAiStatus.get_description(maica.maica_instance.status)]"):
                        style "main_menu_version_l"

            hbox:

                text renpy.substitute(_("> Websocket: ")) + renpy.substitute(stat):
                    style "main_menu_version_l"

            text "":
                size 0

        vbox:
            xmaximum 800
            xfill True
            style_prefix "check"

            use intro_tooltip()
            timer persistent.maica_setting_dict.get('status_update_time', 1.0) repeat True action Function(scr_nullfunc, _update_screens=True)

            if not maica.maica_instance.is_accessable():
                textbutton _("> 使用账号生成令牌")
                    # action Show("maica_login")
                
            elif not maica.maica_instance.is_connected():
                textbutton _("> 使用账号生成令牌"):
                    action Show("maica_login")
                
            if maica.maica_instance.has_token() and not maica.maica_instance.is_connected():
                textbutton _("> 使用已保存令牌连接"):
                    action Function(store.maica.maica_instance.init_connect)

                
            elif maica.maica_instance.is_connected():
                if maica.maica_instance.is_ready_to_input():
                    textbutton _("> 手动上传设置"):
                        action Function(maica_apply_setting)
                    
                    textbutton _("> 重置当前对话"):
                        action Function(reset_session)
                else:
                    textbutton _("> 手动上传设置 [[请先等待连接建立]")
                        
                    textbutton _("> 重置当前对话 [[请先等待连接建立]")

                textbutton _("> 导出当前对话"):
                    action Function(output_chat_history)
                
                textbutton _("> 上传对话历史到会话 [store.maica.maica_instance.chat_session]"):
                    action Function(upload_chat_history)

                textbutton renpy.substitute(_("> 退出当前DCC账号")) + " " + renpy.substitute(_("{size=-10}* 如果对话卡住, 退出以断开连接")):
                    action Function(store.maica.maica_instance.close_wss_session)

            else:
                textbutton _("> 使用已保存令牌连接")
        
            textbutton _("> MAICA参数与设置 {size=-10}*部分选项重新连接生效"):
                action Show("maica_setting")
            
            if log_hasupdate:
                textbutton _("> 更新日志与服务状态 {size=-10}*有新更新"):
                    action Show("maica_log")
            else:
                textbutton _("> 更新日志与服务状态"):
                    action Show("maica_log")
            if pane_cache.get("donation_exists", False):
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
            for item in store.maica.maica_instance.default_setting:
                if item == 'seed':
                    store.maica.maica_instance.default_setting[item] = 0
                if item in persistent.maica_advanced_setting:
                    persistent.maica_advanced_setting[item] = store.maica.maica_instance.default_setting[item]
                    persistent.maica_advanced_setting_status[item] = False

    $ _tooltip = store._tooltip

    $ w = 1100
    $ h = 640
    $ x = 0.5
    $ y = 0.5

    modal True
    zorder 90

    style_prefix "maica_check"

    use maica_common_outer_frame(w, h, x, y):
        use maica_common_inner_frame(w, h, x, y):

            if renpy.config.debug:

                text "=====MaicaAi()====="

                text "ai.is_responding: [store.maica.maica_instance.is_responding()]"

                text "ai.is_failed: [store.maica.maica_instance.is_failed()]"

                text "ai.is_connected: [store.maica.maica_instance.is_connected()]"

                text "ai.is_ready_to_input: [store.maica.maica_instance.is_ready_to_input()]"

                text "ai.MaicaAiStatus.is_submod_exception: [store.maica.maica_instance.MaicaAiStatus.is_submod_exception(store.maica.maica_instance.status)]"

                text "ai.len_message_queue(): [store.maica.maica_instance.len_message_queue()]"

                text "maica_chr_exist: [maica_chr_exist]"

                text "maica_chr_changed: [maica_chr_changed]"

                text "len(mas_rev_unseen): [len(mas_rev_unseen)]"

                text "push_mpostal_read: [has_mail_waitsend() and _mas_getAffection() >= 100 and renpy.seen_label('maica_wants_mspire') and renpy.seen_label('maica_wants_mpostal') and not mas_inEVL('maica_mpostal_received') and not mas_inEVL('maica_mpostal_read')]"

                text "push_mspire_want: [renpy.seen_label('maica_greeting') and not renpy.seen_label('maica_wants_mspire') and renpy.seen_label('mas_random_ask')]"

                $ triggered_list = str(store.maica.maica_instance.mtrigger_manager.triggered_list).replace("[", "[[").replace("{", "{{").replace("【", "【【")
                text "triggered_list: [triggered_list]"

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
                textbutton "推送maica_raw_context_example":
                    action [
                                    Hide("maica_setting"),
                                    Function(store.maica_apply_setting),
                                    Function(store.MASEventList.push, "maica_raw_context_example")
                                ]
                
                textbutton "显示maica_gen_quality_chk_notify 0.3":
                    action Function(store.maica_handle_quality_status, False, 0.3)

                textbutton "显示maica_gen_quality_chk_notify 0.6":
                    action Function(store.maica_handle_quality_status, False, 0.6)

                textbutton "显示maica_gen_quality_chk_notify 0.9":
                    action Function(store.maica_handle_quality_status, False, 0.9)

            hbox:
                use divider(_("连接与安全"))

            hbox:
                style_prefix "maica_check"
                textbutton _("服务提供节点: [store.maica.maica_instance.provider_manager.get_server_info().get('name', 'Unknown')]"):
                    action Show("maica_node_setting")
                    hovered SetField(_tooltip, "value", _("设置服务器节点"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                style_prefix "maica_check_nohover"
                $ user_disp = store.maica.maica_instance.user_acc or renpy.substitute(_("未登录"))
                textbutton _("当前用户: [user_disp]"):
                    action NullAction()
                    hovered SetField(_tooltip, "value", _("如需更换或退出账号, 请在Submods界面退出登录.\n* 要修改账号信息或密码, 请前往注册网站"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("自动重连: [persistent.maica_setting_dict.get('auto_reconnect')]"):
                    action ToggleDict(persistent.maica_setting_dict, "auto_reconnect", True, False)
                    hovered SetField(_tooltip, "value", _("连接断开时自动重连"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("断点续传: [persistent.maica_setting_dict.get('auto_resume')]"):
                    action ToggleDict(persistent.maica_setting_dict, "auto_resume", True, False)
                    hovered SetField(_tooltip, "value", _("若生成回复时网络中断, 重连后续传丢失的部分"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("保持连接活跃: [persistent.maica_setting_dict.get('keep_alive')]"):
                    action ToggleDict(persistent.maica_setting_dict, "keep_alive", True, False)
                    hovered SetField(_tooltip, "value", _("定期发送心跳包保持长连接活跃, 并检测网络延迟"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                use divider(_("行为与表现"))

            hbox:
                style_prefix "maica_check"
                textbutton _("目标语言: [persistent.maica_setting_dict.get('target_lang')]"):
                    action Show("maica_select_language")
                    hovered SetField(_tooltip, "value", _("目标生成语言. 支持\"zh\", \"en\"或\"auto\".\n* 该参数不能100%保证生成语言是目标语言\n* 该参数影响范围广泛, 包括默认时区, 节日文化等, 并不止目标生成语言. 建议设为你的实际母语\n* auto代表通过prompt让模型自行选择语言回答, 效果不等同于指定对应语言\n* 截至文档编纂时为止, MAICA官方部署的英文能力仍然弱于中文"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "maica_check"
                textbutton _("行为预设: [maica_get_preset_name('behavior')]"):
                    action Show("maica_select_preset", preset_type="behavior")
                    hovered SetField(_tooltip, "value", _("这些设置影响MAICA的模型与工具协作行为.\n* 你选择的预设会影响模型的工具, 辅助, 提示词, 以及这些环节消耗的时间\n! 如果你不清楚其具体作用, 请不要修改"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "maica_check"
                textbutton _("超参数预设: [maica_get_preset_name('hyperparameter')]"):
                    action Show("maica_select_preset", preset_type="hyperparameter")
                    hovered SetField(_tooltip, "value", _("这些设置影响MAICA核心模型的推理表现.\n* 你选择的预设直接影响核心模型的推理和采样\n! 如果你不清楚其具体作用, 请不要修改"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "maica_check_nohover"
                text _("本节中的剩余条目均由预设管理.\n! 如果你不清楚这些条目的具体作用, 请不要手动修改")

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
                style_prefix "generic_fancy_check"
                textbutton _("会话质量检测: [persistent.maica_setting_dict.get('gen_quality_chk')]"):
                    action ToggleDict(persistent.maica_setting_dict, "gen_quality_chk", True, False)
                    hovered SetField(_tooltip, "value", _("对话长度超过3轮后, 在每轮对话结束时, 要求MNerve介入检查输出合理性.\n+ 量化地检测判断会话劣化情况, 以免用户注意不到\n- 产生额外的MNerve开销"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("输入语言检测: [persistent.maica_setting_dict.get('input_lang_detect')]"):
                    action ToggleDict(persistent.maica_setting_dict, "input_lang_detect", True, False)
                    hovered SetField(_tooltip, "value", _("检测输入语言与目标生成语言是否相符.\n* 非特殊情况不建议关闭"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("实时后处理: [persistent.maica_setting_dict.get('pprt')]"):
                    action ToggleDict(persistent.maica_setting_dict, "pprt", True, False)
                    hovered SetField(_tooltip, "value", _("启用后端自动断句和实时后处理功能.\n* 非特殊情况不建议关闭"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                frame:
                    xmaximum 950
                    xpos 4
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
                use divider(_("会话与数据"))

            hbox:
                style_prefix "generic_fancy_check"
                if store.maica.savefile_access_marker_exists():
                    textbutton _("使用存档数据: [persistent.maica_setting_dict.get('savefile_access')]"):
                        action ToggleDict(persistent.maica_setting_dict, "savefile_access", True, False)
                        hovered SetField(_tooltip, "value", _("关闭时, 模型将不会使用存档数据.\n* 每次重启游戏将自动上传存档数据"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)
                else:
                    textbutton _("使用存档数据: [persistent.maica_setting_dict.get('savefile_access')]"):
                        style "generic_fancy_check_button_disabled"
                        action ToggleDict(persistent.maica_setting_dict, "savefile_access", True, False)
                        hovered SetField(_tooltip, "value", _("关闭时, 模型将不会使用存档数据.\n! savefile_access标记文件不存在, 存档数据不会上传或应用"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)

            if persistent.maica_setting_dict['mspire_session'] != 0 and persistent.maica_setting_dict['chat_session'] == persistent.maica_setting_dict['mspire_session']:
                $ tooltip_chat_session = _("每个session独立保存和应用对话记录.\n* 设为0以不记录和不使用对话记录(单轮对话)\n! 当前session与MSpire会话相同, 可能导致迷惑性的表现")
                hbox:
                    style_prefix "maica_check_nohover"
                    text _("! 当前主会话与MSpire共用会话, 这可能导致行为和表现上的问题.\n! 如果你不清楚这意味着什么, 请不要将二者设为相同非0值."):
                        color "#FF0000"
            else:
                $ tooltip_chat_session = _("每个session独立保存和应用对话记录.\n* 设为0以不记录和不使用对话记录(单轮对话)")
            use num_bar(_("当前会话"), 200 if config.language == "chinese" else 350, tooltip_chat_session, "chat_session", 0, 9)


            $ tooltip_session_length = _("会话保留的最大长度. 范围512-28672.\n* 按字符数计算. 每3个ASCII字符只占用一个字符长度\n* 字符数超过限制后, MAICA会裁剪其中较早的部分, 直至少于限制的 2/3\n* 过大或过小的值可能导致表现和性能问题")
            use prog_bar(_("会话长度"), 400 if config.language == "chinese" else 450, tooltip_session_length, "session_len_limit", 512, 28672)
            textbutton _("重置会话长度"):
                action SetDict(persistent.maica_setting_dict, "session_len_limit", 8192)

            hbox:
                style_prefix "maica_check"
                textbutton _("时区设置: [persistent.maica_setting_dict.get('tz')]"):
                    action Show("maica_tz_setting")
            
            hbox:
                style_prefix "maica_check"
                textbutton _("地理位置: [persistent.mas_geolocation]"):
                    action Show("maica_location_input", addition = persistent.mas_geolocation)

            hbox:
                frame:
                    xmaximum 950
                    xpos 4
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True
                    $ tooltip_mf_info = _("由你补充的设定信息, 由MFocus检索并呈递到核心模型.\n* 需要重新上传存档生效")
                    hbox:
                        style_prefix "maica_check_nohover"
                        textbutton _("当前有[len(persistent.mas_player_additions)]条自定义MFocus信息"):
                            action NullAction()
                            hovered SetField(_tooltip, "value", tooltip_mf_info)
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("编辑MFocus信息"):
                            action Show("maica_addition_setting")
                            hovered SetField(_tooltip, "value", tooltip_mf_info)
                            unhovered SetField(_tooltip, "value", _tooltip.default)

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
                        hovered SetField(_tooltip, "value", _("是否允许由MSpire生成的对话.\n* 必须关闭复述话题才能启用\n* MSpire话题不使用MFocus和MTrigger"))
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
                    xmaximum 950
                    xpos 4
                    xfill True
                    has vbox:
                        xsize 950
                        xfill True
                    hbox:
                        style_prefix "maica_check"
                        textbutton _("MSpire话题"):
                            action Show("maica_mspire_category_setting")


                    $ tooltip_ms_time = _("MSpire对话的最小时间间隔")
                    use prog_bar(_("MSpire最小间隔"), 250 if config.language == "chinese" else 400, tooltip_ms_time, "mspire_interval", 10, 180, "m")

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("MSpire搜索方式: [persistent.maica_setting_dict.get('mspire_search_type')]"):
                            action [
                                    Show("maica_mspire_setting")
                                        ]
                            hovered SetField(_tooltip, "value", _("MSpire搜索话题的模式"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    if persistent.maica_setting_dict['mspire_session'] == 0:
                        hbox:
                            style_prefix "generic_fancy_check"
                            textbutton _("MSpire使用缓存"):
                                action ToggleDict(persistent.maica_setting_dict, "mspire_use_cache", True, False)
                                hovered SetField(_tooltip, "value", _("启用MSpire缓存.\n* MSpire会话不为0时不生效\n* 会强制使用默认高级参数"))
                                unhovered SetField(_tooltip, "value", _tooltip.default)
                    else:
                        hbox:
                            textbutton _("MSpire使用缓存"):
                                style "generic_fancy_check_button_disabled"
                                action ToggleDict(persistent.maica_setting_dict, "mspire_use_cache", True, False)
                                hovered SetField(_tooltip, "value", _("启用MSpire缓存.\n! MSpire会话不为0, MSpire缓存不会生效"))
                                unhovered SetField(_tooltip, "value", _tooltip.default)

                    if persistent.maica_setting_dict['mspire_session'] != 0 and persistent.maica_setting_dict['chat_session'] == persistent.maica_setting_dict['mspire_session']:
                        $ tooltip_ms_session = _("MSpire使用的session.\n* 设为0以不记录MSpire(单轮对话)\n* 如果不设为0, MSpire对话将提供接续选项\n! 当前session与主会话相同, 自动清空已禁用")
                        hbox:
                            style_prefix "maica_check_nohover"
                            text _("! 当前主会话与MSpire共用会话, 这可能导致行为和表现上的问题.\n! 如果你不清楚这意味着什么, 请不要将二者设为相同非0值."):
                                color "#FF0000"
                    else:
                        $ tooltip_ms_session = _("MSpire使用的session.\n* 设为0以不记录MSpire(单轮对话)\n* 如果不设为0, MSpire对话将提供接续选项\n! MSpire每次生成前将自动清空该session")
                    use num_bar(_("MSpire会话"), 200 if config.language == "chinese" else 350, tooltip_ms_session, "mspire_session", 0, 9)

            hbox:
                style_prefix "maica_check"
                textbutton _("MTrigger列表"):
                    action Show("maica_triggers")
                    hovered SetField(_tooltip, "value", _("查看和配置MTrigger条目"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            if persistent._maica_vista_enabled:
                hbox:
                    style_prefix "maica_check"
                    textbutton _("MVista图片"):
                        action Show("maica_vista_filelist")
                        hovered SetField(_tooltip, "value", _("查看和管理用于MVista的图片.\n* 请仔细阅读TOS, 对你自己的隐私负责"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)
            
            else:
                hbox:
                    textbutton _("MVista图片"):
                        style "maica_check_button_disabled"
                        action Show("maica_vista_filelist")
                        hovered SetField(_tooltip, "value", _("查看和管理用于MVista的图片.\n! MVista尚未解锁, 请继续和莫妮卡交互或送信, 并耐心等待"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                frame:
                    xmaximum 950
                    xpos 4
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True
                    hbox:
                        style_prefix "maica_check"
                        textbutton _("MPostal历史信件"):
                            action Show("maica_mpostals")
                            hovered SetField(_tooltip, "value", _("查看MPostal历史信件"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    $ tooltip_mp_time = _("MPostal回信的最小时间间隔")
                    use prog_bar(_("MPostal最小间隔"), 250 if config.language == "chinese" else 400, tooltip_mp_time, "mpostal_default_reply_time", 10, 720, "m")
            
            hbox:
                use divider(_("界面与日志"))

            hbox:
                style_prefix "maica_check"
                textbutton _("submod_log.log 等级: [logging.getLevelName(persistent.maica_setting_dict['log_level'])]"):
                    action Show("maica_select_log_level", log = "log_level")#Function(store.change_loglevel)
                    hovered SetField(_tooltip, "value", _("重要性低于设置等级的log将不会被记录在submod_log.log中.\n* 这也会影响其他子模组"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:

                use prog_bar(expl=_("状态码更新频率"), len=250 if config.language == "chinese" else 400, tooltip="在Submod界面处的状态码更新频率", var="status_update_time", min=1, max=60, istime="s")

            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("动态的天堂树林"):
                    action ToggleDict(persistent.maica_setting_dict, "use_anim_background", True, False)
                    hovered SetField(_tooltip, "value", _("使用动态摇曳和改良光影的天堂树林, 略微增加渲染压力. 重启生效.\n* 如果产生显存相关错误, 删减精灵包或禁用此选项"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                frame:
                    xmaximum 950
                    xpos 4
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
                            action Show("maica_select_console_font")#ToggleDict(persistent.maica_setting_dict, "console_font", store.maica_confont, store.mas_ui.MONO_FONT)
                            hovered SetField(_tooltip, "value", _("console使用的字体\nmplus-1mn-medium.ttf为默认字体\nSarasaMonoTC-SemiBold.ttf对于非英文字符有更好的显示效果"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("控制台log等级: [logging.getLevelName(persistent.maica_setting_dict['log_conlevel'])]"):
                            action Show("maica_select_log_level", log = "log_conlevel")
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
            xalign 0.5 yalign 1.0
            yoffset -25
            text tooltip.value:
                style "main_menu_version"


screen maica_input_screen(prompt):
    modal True
    default maica_input = store.maica.MaicaInputValue()
    style_prefix "input"

    window:
        hbox:
            style_prefix "quick"
            #xfill True
            #xmaximum 0#(None if not has_history else 232)
            xalign 0.5
            yalign 0.995

            textbutton _("退出"):
                selected False
                action Return("nevermind")

            textbutton _("粘贴"):
                selected False
                action [Function(maica_input.set_text, pygame.scrap.get(pygame.SCRAP_TEXT).strip()),Function(maica_input.set_text, pygame.scrap.get(pygame.SCRAP_TEXT).strip())]
            if persistent._maica_vista_enabled:
                textbutton renpy.substitute(_("选择图片 | 当前已选择 ")) + str(len(store._maica_selected_visuals)) + renpy.substitute(_(" 张")):
                    selected False
                    action [Show("maica_vista_filelist", selecting=True), NullAction()]
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

screen maica_input_information_screen(prompt):
    default maica_input_information = store.maica.MaicaInputValue()
    style_prefix "input"

    window:
        hbox:
            style_prefix "quick"
            #xfill True
            #xmaximum 0#(None if not has_history else 232)
            xalign 0.5
            yalign 0.995

            textbutton _("退出"):
                selected False
                action Return("nevermind")

            textbutton _("粘贴"):
                selected False
                action [Function(maica_input_information.set_text, pygame.scrap.get(pygame.SCRAP_TEXT).strip()),Function(maica_input_information.set_text, pygame.scrap.get(pygame.SCRAP_TEXT).strip())]


        vbox:
            align (0.5, 0.5)
            spacing 30

            text prompt style "input_prompt"
            input:
                id "input"
                value maica_input_information
