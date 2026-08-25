init -990 python:
    # dependencies - dictionary in the following structure: {"name": ("minimum_version", "maximum_version")}
    store.mas_submod_utils.Submod(
        author="P",
        name="MAICA Blessland",
        description=_("MAICA Official Submod Frontend"),
        version=maica_ver,
        dependencies={"Ignore Translation Conflicts": (None, None)},
        settings_pane="maica_setting_pane"
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

default -1499 persistent.maica_setting_dict = {
    "auto_reconnect":True,
    "auto_resume":True,
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
default -1499 persistent.maica_advanced_setting = {}
default -1499 persistent.maica_advanced_setting_status = {}
default -1499 persistent.mas_player_additions = []
default persistent._maica_reseted = False
default persistent._maica_target_lang_mode = None
default persistent._maica_tz_mode = None

init -1498 python:
    try:
        import __builtin__ as maica_builtins
    except ImportError:
        import builtins as maica_builtins

    def maica_repair_persistent_containers():
        repaired = []
        container_types = (
            ("maica_setting_dict", maica_builtins.dict, dict),
            ("maica_advanced_setting", maica_builtins.dict, dict),
            ("maica_advanced_setting_status", maica_builtins.dict, dict),
            ("mas_player_additions", maica_builtins.list, list),
            ("_maica_send_or_received_mpostals", maica_builtins.list, list),
            ("_maica_visuals", maica_builtins.list, list),
        )
        for name, expected_type, factory in container_types:
            value = getattr(persistent, name, None)
            if not isinstance(value, expected_type):
                setattr(persistent, name, factory())
                repaired.append("{} ({})".format(name, type(value).__name__))

        mspire_category = persistent.maica_setting_dict.get("mspire_category", [])
        if not isinstance(mspire_category, maica_builtins.list):
            persistent.maica_setting_dict.pop("mspire_category", None)
            repaired.append(
                "maica_setting_dict.mspire_category ({})".format(
                    type(mspire_category).__name__
                )
            )
        return repaired

    _maica_repaired_persistent_containers = maica_repair_persistent_containers()

define maica_confont = "mod_assets/font/SarasaMonoTC-SemiBold.ttf"
#define "mod_assets/font/mplus-1mn-medium.ttf" # mas_ui.MONO_FONT
init 10 python:
    import logging
    import bot_interface
    import maica_v13_migration

    if _maica_repaired_persistent_containers:
        store.mas_submod_utils.submod_log.warning(
            "MAICA: repaired invalid persistent containers: {}".format(
                ", ".join(_maica_repaired_persistent_containers)
            )
        )

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

    def maica_get_language_default_timezone(target_lang=None):
        if target_lang is None:
            target_lang = persistent.maica_setting_dict.get(
                "target_lang",
                maica_get_default_target_lang()
            )
        if target_lang == "zh":
            return "Asia/Shanghai"
        return "America/Indiana/Vincennes"

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

    def maica_refresh_automatic_settings(settings):
        if persistent._maica_target_lang_mode == "renpy":
            settings["target_lang"] = maica_get_default_target_lang()
        if persistent._maica_tz_mode == "system":
            settings["tz"] = maica_get_system_timezone()
        elif persistent._maica_tz_mode == "language":
            settings["tz"] = maica_get_language_default_timezone(
                settings["target_lang"]
            )

    def maica_select_target_lang(target_lang, mode):
        persistent.maica_setting_dict["target_lang"] = target_lang
        persistent._maica_target_lang_mode = mode
        if persistent._maica_tz_mode == "language":
            persistent.maica_setting_dict["tz"] = (
                maica_get_language_default_timezone(target_lang)
            )

    def maica_select_timezone(timezone, mode):
        persistent.maica_setting_dict["tz"] = timezone
        persistent._maica_tz_mode = mode

    maica_default_dict = {
        "auto_reconnect":True,
        "auto_resume":True,
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
        "mf_context_rnds":1,
        "mt_context_rnds":1,
        "mf_precheck_mt":True,
        "mf_disable_loop":True,
        "mt_disable_loop":True,
        "gen_enforce_lang":True,
        "mf_sf_access_impl":1,
        "mf_const_sf_access":0,
        "memory_concl_arc":1,
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
        # "mf_context_rnds":1,
        # "mt_context_rnds":1,
        # "mf_precheck_mt":True,
        # "mf_disable_loop":True,
        # "mt_disable_loop":True,
        # "gen_enforce_lang":True,
        # "mf_sf_access_impl":1,
        # "mf_const_sf_access":0,
        # "memory_concl_arc":1,
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
            "name": "Pure",
            "description": "Reduce prompt text to minimum, use almost no tool, only retain critical correction.\n+ Fastest, nearly shortest TTFT\n- Almost no external sense, no in-game action ability",
            "settings": {
                "enable_mf": False,
                "enable_mt": False,
                "gen_quality_chk": False,
                "use_custom_model_config": True,
                "mf_const_tools": 0,
                "nsfw_acceptive": False,
                "gen_enforce_lang": False,
                "memory_concl_arc": 0,
                "prompt_allow_nickname": False,
            },
        },
        {
            "name": "Fluent",
            "description": "No LLM intervention in pre-generation phase, use constant tools instead to reduce TTFT. Also reduced other tools.\n+ Relatively fast, nearly shortest TTFT\n* Limited external sense, has in-game action ability",
            "settings": {
                "enable_mf": False,
                "use_custom_model_config": True,
                "mt_context_rnds": 0,
                "mf_precheck_mt": False,
                "mf_sf_access_impl": 2,
                "mf_const_sf_access": 1,
            },
        },
        {
            "name": "Dexterous",
            "description": "Aggressive tending calibration based on default, exchanges stability and rarely used functions for average speed.\n+ Relatively fast, relatively short TTFT\n+ Normal external sense, has in-game action ability",
            "settings": {
                "gen_quality_chk": False,
                "use_custom_model_config": True,
                "mf_const_tools": 2,
                "esearch_llm_concl": False,
                "mf_context_rnds": 0,
                "mt_context_rnds": 0,
                "mf_precheck_mt": False,
                "mf_sf_access_impl": 2,
                "mf_const_sf_access": 1,
            },
        },
        {
            "name": "Balanced (default)",
            "description": "Default behavior of MAICA. Field-tested balanced calibration, performs best overall in most cases.\n* Decent speed, decent TTFT\n+ Normal external sense, has in-game action ability",
            "settings": {},
        },
        {
            "name": "Complete",
            "description": "Almost complete feature set of generation assistance enabled. May perform better under extreme circumstances, but normally just wasting time.\n- Slowest, longest TTFT\n+ Normal external sense, has in-game action ability",
            "settings": {
                "use_custom_model_config": True,
                "mf_llm_concl": True,
                "mf_disable_loop": False,
                "mt_disable_loop": False,
                "mf_const_sf_access": 1,
            },
        },
    ]
    maica_hyperparameter_presets = [
        {
            "name": "Eager",
            "description": "Fixed seed, eager sampling.\n! Not recommended for normal cases",
            "settings": {
                "temperature": 0.0,
                "seed": 42,
            },
        },
        {
            "name": "Cautious",
            "description": "Lower temperature.\n! Not recommended for normal cases",
            "settings": {
                "temperature": 0.10,
            },
        },
        {
            "name": "Standard (default)",
            "description": "Default super params of MAICA. Field-tested balanced calibration, performs best overall in most cases.",
            "settings": {},
        },
        {
            "name": "Aggressive",
            "description": "Higher temperature.\n! Not recommended for normal cases",
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
        name = preset["name"] if preset else "Custom"
        return renpy.substitute(_(name))

    _maica_validate_presets()
    if set(maica_advanced_default_setting) != set(maica_v13_migration.ADVANCED_SETTING_KEYS):
        raise ValueError("MAICA advanced setting defaults do not match the outbound allowlist")
    maica_advanced_setting_status = {k: False for k, v in maica_advanced_setting.items()}
    persistent.maica_setting_dict.pop("42seed", None)
    maica_default_dict.update(persistent.maica_setting_dict)
    maica_advanced_setting.update(persistent.maica_advanced_setting)
    maica_advanced_setting_status.update(persistent.maica_advanced_setting_status)
    maica_refresh_automatic_settings(maica_default_dict)

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
        persistent._maica_target_lang_mode = "renpy"
        persistent._maica_tz_mode = "system"
        maica_refresh_automatic_settings(persistent.maica_setting_dict)
        sync_provider_id(persistent.maica_setting_dict["provider_id"])
        persistent.mas_geolocation = ''
        persistent.mas_player_additions = []
        persistent.maica_setting_dict["mspire_category"] = []

    def maica_clamp_advanced_setting(key, lower, upper):
        value = int(persistent.maica_advanced_setting.get(key, lower))
        persistent.maica_advanced_setting[key] = max(lower, min(value, upper))

    def maica_get_advanced_default(key):
        value = store.maica.maica_instance.default_setting.get(
            key,
            maica_advanced_default_setting[key]
        )
        if key == "seed" and value is None:
            value = 0
        return copy.deepcopy(value)

    def maica_reset_advanced_setting():
        maica_v13_migration.cleanup_advanced_settings(
            persistent.maica_advanced_setting,
            persistent.maica_advanced_setting_status
        )
        for key in maica_v13_migration.ADVANCED_SETTING_KEYS:
            persistent.maica_advanced_setting[key] = maica_get_advanced_default(key)
            persistent.maica_advanced_setting_status[key] = False

    def maica_escape_display_text(text):
        return bot_interface.escape_renpy_text(text)

    def maica_escape_dialogue_text(text, interpolation_passes=1):
        return bot_interface.escape_renpy_text(
            text,
            bot_interface.RENPY_DIALOGUE_SUBSTITUTIONS,
            interpolation_passes
        )

    def maica_build_display_preview(text, limit):
        return bot_interface.build_renpy_text_preview(
            text,
            limit,
            bot_interface.RENPY_DIALOGUE_SUBSTITUTIONS
        )

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
            renpy.notify(_("MAICA: Input is empty"))
            return None
        addition = ("{player_name}" + raw_addition.strip() if prefix_player else raw_addition.strip())
        replacing = edittarget in additions
        if len(additions) >= 512:
            if not replacing:
                renpy.notify(_("MAICA: Custom MFocus information has reached the 512-item limit"))
                return None
        if len(addition.encode("utf-8")) > 1536:
            renpy.notify(_("MAICA: A custom MFocus information item cannot exceed 1536 bytes"))
            return None
        if addition in additions and addition != edittarget:
            renpy.notify(_("MAICA: Identical content already exists"))
            return None
        return addition

    def _maica_verify_token():
        res = store.maica.maica_instance._verify_token()
        if res.get("success"):
            renpy.show_screen("maica_message", message=_("Authentication passed"))
        else:
            ai = store.maica.maica_instance
            if ai.status in (ai.MaicaAiStatus.TOKEN_CORRUPTED, ai.MaicaAiStatus.TOKEN_INVALID):
                store.mas_api_keys.api_keys.update({"Maica_Token":""})
                ai.ciphertext = ""
                store.mas_api_keys.save_keys()
            status_text = renpy.substitute(_("Authentication failed: ")) + ai.get_status_description()
            detail = u"{}".format(res.get("exception") or "")
            if detail:
                status_text += "\n" + renpy.substitute(_("Reason: ")) + detail
            renpy.show_screen("maica_message", message=status_text)


    @store.mas_submod_utils.functionplugin("ch30_preloop")
    def _upload_persistent_dict():
        if not store.maica.savefile_access_marker_exists():
            store.mas_submod_utils.submod_log.debug("MAICA: Skip savefile upload because savefile_access marker is missing")
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
        d['target_lang'] = store.maica.maica_instance.target_lang
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
        renpy.notify(_("MAICA: Savefile uploaded successfully") if res.get("success", False) else _("MAICA; Savefile failed to upload"))

    def reset_session():
        store.maica.maica_instance.reset_chat_session()
        renpy.notify(_("MAICA: Chat session reset"))
    def output_chat_history():
        import json
        with open(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "chat_history.txt"), 'w') as f:
            f.write(json.dumps(store.maica.maica_instance.get_history().get("content") or []))
        renpy.notify(_("MAICA: History exported to game/Submods/MAICA_ChatSubmod/chat_history.txt"))

    def upload_chat_history():
        import json
        if not os.path.exists(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "chat_history.txt")):
            renpy.notify(_("MAICA: History not found at game/Submods/MAICA_ChatSubmod/chat_history.txt"))
            return
        try:
            with open(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "chat_history.txt"), 'r') as f:
                history = json.load(f)
        except Exception as e:
            store.mas_submod_utils.submod_log.error("upload_chat_history: failed to read history file: {}".format(e))
            renpy.notify(_("MAICA: Failed to read history, check submod_log.log for details."))
            return
        res = store.maica.maica_instance.upload_history(history)
        if not res.get("success", False):
            renpy.notify(_("MAICA: Failed to upload history, check submod_log.log for details."))
            return
        renpy.notify(_("MAICA: History uploaded"))

    def run_migrations():
        if persistent.maica_setting_dict["mspire_interval"] <= 10:
            persistent.maica_setting_dict["mspire_interval"] = 10

    def maica_apply_setting(ininit=False):
        import copy
        run_migrations()
        maica_refresh_automatic_settings(persistent.maica_setting_dict)

        # Apply user-selected levels before initialization actions emit logs.
        store.mas_submod_utils.submod_log.level = persistent.maica_setting_dict["log_level"]
        store.maica.maica_instance.console_logger.level = persistent.maica_setting_dict["log_conlevel"]

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
        send_success = False
        if store.maica.maica_instance.is_ready_to_input():
            send_success = bool(store.maica.maica_instance.send_settings())
        if not ininit:
            renpy.notify(_("MAICA: Settings uploaded") if send_success else _("MAICA: Do a manual upload after connection ready"))

    def maica_discard_setting(target_lang_mode=None, tz_mode=None):
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

        if target_lang_mode is not None:
            persistent._maica_target_lang_mode = target_lang_mode
        if tz_mode is not None:
            persistent._maica_tz_mode = tz_mode

        renpy.notify(_("MAICA: Settings discarded"))


    def maica_apply_advanced_setting():
        settings_dict = maica_v13_migration.filter_advanced_settings(
            persistent.maica_advanced_setting,
            persistent.maica_advanced_setting_status
        )
        store.maica.maica_instance.modelconfig = settings_dict
        store.mas_submod_utils.submod_log.debug("Applied custom advanced settings")

    def maica_discard_advanced_setting():
        settings_dict = maica_v13_migration.filter_advanced_settings(
            store.maica.maica_instance.modelconfig
        )
        maica_v13_migration.cleanup_advanced_settings(
            persistent.maica_advanced_setting,
            persistent.maica_advanced_setting_status
        )
        for key in maica_v13_migration.ADVANCED_SETTING_KEYS:
            persistent.maica_advanced_setting_status[key] = key in settings_dict
            if key in settings_dict:
                persistent.maica_advanced_setting[key] = copy.deepcopy(settings_dict[key])
            else:
                persistent.maica_advanced_setting[key] = maica_get_advanced_default(key)


    def sync_provider_id(pid, reconnect=True):
        """
        切换服务提供节点并, 立刻生效.
        - 写入 persistent.maica_setting_dict["provider_id"]
        - 更新 provider_manager.provider_id
        - 断开当前已连接的 websocket (如有), 重新 accessable() 并重连
        """
        import threading
        ai = store.maica.maica_instance
        try:
            pid = int(pid)
        except Exception:
            pid = 0
        persistent.maica_setting_dict["provider_id"] = pid
        ai.provider_id = pid
        # ai.provider_manager.set_provider_id(pid)

        # 断开旧连接，并取消可能仍在等待的自动重连
        if reconnect:
            ai.close_wss_session()
        ai.disable()


        # 后台处理的东西 (刷新节点列表、重新 accessable()、再重连) 走threading (避免卡住 UI)
        def _bg():
            try:
                if reconnect and not ai.wait_for_connection_shutdown(6.0):
                    store.mas_submod_utils.submod_log.error(
                        "Failed to sync provider id: previous websocket did not stop"
                    )
                    return
                availability_ready = store.maica.check_accessibility()

                if reconnect and availability_ready and ai.has_token():
                    ai.init_connect()

            except Exception as e:
                store.mas_submod_utils.submod_log.error("Failed to sync provider id: {}".format(e))

        try:
            threading.Thread(target=_bg).start()
        except Exception:
            pass


        renpy.notify(_("MAICA: Provider applied, reconnecting"))
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
        renpy.notify(_("MAICA: Exported to game/Submods/MAICA_ChatSubmod/player_info.txt"))

    def update_model_setting(ininit = False):
        import os, json
        try:
            with open(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "custom_modelconfig.json"), "r") as f:
                store.maica.maica_instance.modelconfig = json.load(f)
        except Exception as e:
            if not ininit:
                renpy.notify(_("MAICA: Advanced settings failed to serialize, check submod_log.log").format(e))
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
            store.mas_submod_utils.submod_log.debug("maica_greeting.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_greeting')), renpy.seen_label('maica_greeting')))
            store.mas_submod_utils.submod_log.debug("maica_chr2.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_chr2')), renpy.seen_label('maica_chr2')))
            store.mas_submod_utils.submod_log.debug("maica_chr_gone.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_chr_gone')), renpy.seen_label('maica_chr_gone')))
            store.mas_submod_utils.submod_log.debug("maica_chr_corrupted2.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_chr_corrupted2')), renpy.seen_label('maica_chr_corrupted2')))
            store.mas_submod_utils.submod_log.debug("maica_wants_preferences2.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_wants_preferences2')), renpy.seen_label('maica_wants_preferences2')))
            store.mas_submod_utils.submod_log.debug("maica_wants_mspire.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_wants_mspire')), renpy.seen_label('maica_wants_mspire')))
            store.mas_submod_utils.submod_log.debug("maica_mspire.conditional:{}|seen:{}".format(try_eval(get_conditional('maica_mspire')), renpy.seen_label('maica_mspire')))
            store.mas_submod_utils.submod_log.debug("maica_mspire.last_seen:{}".format(evhand.event_database.get('maica_mspire',None).last_seen))
            store.mas_submod_utils.submod_log.debug("maica_wants_mpostal.conditional:{}|seen: {}".format(try_eval(get_conditional('maica_wants_mpostal')), renpy.seen_label('maica_wants_mpostal')) )



        except Exception as e:
            store.mas_submod_utils.submod_log.error("Failed to get event stat: {}".format(e))

    maica_apply_setting(True)
    #log_eventstat()


init python:
    _maica_settings_connect_context_active = False

    def _maica_call_in_new_context_preserve_layers(label, *args):
        """Call a label in a new context without clearing layers."""
        version = tuple(renpy.version_tuple[:2])

        # `_clear_layers` was added in the paired Ren'Py 7.8/8.3 releases.
        if version >= (8, 3) or (7, 8) <= version < (8, 0):
            if not args:
                return renpy.call_in_new_context(label, _clear_layers=False)
            call_kwargs = {"_clear_layers": False}
            return renpy.call_in_new_context(label, *args, **call_kwargs)

        # Older SDKs hard-code clear=True, so mirror their call path here.
        contexts = renpy.game.contexts
        uses_modern_context_lifecycle = hasattr(renpy, "revertable")
        if uses_modern_context_lifecycle:
            if renpy.game.log.current is not None:
                renpy.game.log.complete()
            renpy.display.focus.clear_focus()

        context = renpy.execution.Context(False, contexts[-1], clear=False)
        contexts.append(context)
        interface = renpy.display.interface
        if interface is not None:
            interface.enter_context()

        renpy.store._args = args or None
        renpy.store._kwargs = None

        try:
            context.goto_label(label)
            return renpy.execution.run_context(False)

        except renpy.game.JumpOutException as exception:
            outer_context = contexts[-2]
            outer_context.force_checkpoint = True
            if version >= (7, 0):
                outer_context.abnormal = True
            raise renpy.game.JumpException(exception.args[0])

        finally:
            contexts.pop()
            contexts[-1].do_deferred_rollback()
            if interface and interface.restart_interaction and contexts:
                contexts[-1].scene_lists.focused = None

    def _maica_connect_from_settings_once():
        """Open one settings connection context at a time."""
        global _maica_settings_connect_context_active
        ai = store.maica.maica_instance
        if (
            _maica_settings_connect_context_active
            or not ai.is_accessable()
            or not ai.has_token()
            or ai.is_connected()
            or ai.is_connecting()
        ):
            return False

        _maica_settings_connect_context_active = True
        try:
            return _maica_call_in_new_context_preserve_layers(
                "maica_connect_from_settings"
            )
        finally:
            _maica_settings_connect_context_active = False

    def scr_nullfunc():
        return

    def maica_start_provider_task(task):
        """Start one provider-related network task without blocking the UI."""
        ai = store.maica.maica_instance
        if ai.is_provider_refreshing() or ai.is_checking_availability():
            return False
        renpy.invoke_in_thread(task)
        return True


screen maica_setting_pane():

    on "show" action Function(store.maica.refresh_setting_pane_cache)

    python:
        import store.maica as maica
        pane_cache = maica.maica_setting_pane_cache
        ai = maica.maica_instance
        connection_busy = ai.is_connecting()
        availability_busy = ai.is_checking_availability()
        provider_refresh_error = ai.get_provider_refresh_error()
        provider_refresh_error_text = ""
        if provider_refresh_error:
            provider_refresh_error_text = maica_build_display_preview(
                provider_refresh_error.get("exception") or "",
                160,
            )
        if connection_busy and not ai.is_failed():
            stat = ai.get_status_description()
        else:
            stat = _("Not connected") if not ai.wss_session else _("Connection established") if ai.is_connected() else _("Connection closed")
        ai.ciphertext = store.mas_getAPIKey("Maica_Token")
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

            if store.maica_is_dev:
                hbox:

                    text _("> Warning: this is a {color=#ff0000}development build{/color} copy. {color=#ff0000}Stop using immediately{/color} if you're not MAICA official staff"):
                        style "main_menu_version_l"

            if get_build_timestamp() < cn_mas_mobile_min_timestamp and renpy.android:
                hbox:

                    text _("> Your current MAS version is below the lowest compatible version, please update"):
                        style "main_menu_version_l"

            elif maica.is_frontend_version_outdated():
                hbox:

                    text _("> {color=#ff0000}Support for current version has ended{/color}, an update is required"):
                        style "main_menu_version_l"

            if pane_cache.get("cacert_missing", False):
                hbox:

                    text _("> Warning: {color=#ff0000}no certification found{/color}, check datapack installation"):
                        style "main_menu_version_l"

            if ai.status == ai.MaicaAiStatus.CERTIFI_BROKEN:
                hbox:

                    text _("> Warning: {color=#ff0000}certification corrupted{/color}, remove problematic extensions or clean install"):
                        style "main_menu_version_l"

            if pane_cache.get("better_loading_installed", False):
                hbox:

                    text _("> Warning: Blessland is {color=#ff0000}NOT compatible with Better Loading{/color}"):
                        style "main_menu_version_l"

            if pane_cache.get("log_screen_installed", False):
                hbox:

                    text _("> Warning: set 'submod_log' logger verbosity to 'info' or lower when using with Log Screen"):
                        style "main_menu_version_l"

            if version_check is not None:
                $ res, libv, uiv = version_check
                if res is None:
                    hbox:

                        text _("> Warning: MAICA Libs version not found. Please install from Release, {color=#ff0000}NOT source code{/color}"):
                            style "main_menu_version_l"
                elif res != 0:
                    hbox:

                        text _("> Warning: MAICA Libs v[libv] mismatch with UI v[uiv]. Please fully update {color=#ff0000}from Release{/color}"):
                            style "main_menu_version_l"

            if renpy.windows and not pane_cache.get("is_zhcn", True):
                hbox:

                    text _("> Warning: current system 'non-unicode language' is not Chinese, expect possible encoding issues"):
                        style "main_menu_version_l"

            if availability_busy or maica.maica_instance.status == maica.maica_instance.MaicaAiStatus.WAIT_AVAILABILITY or maica.maica_instance.is_connecting() or maica.maica_instance.MaicaAiStatus.is_submod_exception(maica.maica_instance.status):
                hbox:
                    text _("> MAICA connection status: [maica.maica_instance.status]|[maica.maica_instance.MaicaAiStatus.get_description(maica.maica_instance.status)]"):
                        style "main_menu_version_l"

            if provider_refresh_error and ai.status not in (ai.MaicaAiStatus.FAILED_GET_NODE, ai.MaicaAiStatus.NO_INTERNET):
                hbox:
                    text renpy.substitute(_("> Provider list refresh failed: ")) + provider_refresh_error_text:
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

            if not maica.maica_instance.is_accessable() or connection_busy:
                # Intentionally disabled until provider availability is confirmed.
                textbutton _("> Generate token from account")

            elif not maica.maica_instance.is_connected():
                textbutton _("> Generate token from account"):
                    action Show("maica_login")

            if connection_busy:
                textbutton _("> Connect with current token")

            elif maica.maica_instance.has_token() and maica.maica_instance.is_accessable() and not maica.maica_instance.is_connected():
                textbutton _("> Connect with current token"):
                    action Function(_maica_connect_from_settings_once)


            elif maica.maica_instance.is_connected():
                if maica.maica_instance.is_ready_to_input():
                    textbutton _("> Upload settings"):
                        action Function(maica_apply_setting)

                    textbutton _("> Reset current chat session"):
                        action Function(reset_session)
                else:
                    textbutton _("> Upload settings manually [[wait for connection establishment first]")

                    textbutton _("> Reset current chat session [[wait for connection establishment first]")

                textbutton _("> Export current conversation history"):
                    action Function(output_chat_history)

                textbutton _("> Upload chat history to session [store.maica.maica_instance.chat_session]"):
                    action Function(upload_chat_history)

                textbutton renpy.substitute(_("> Logout")) + " " + renpy.substitute(_("{size=-10}* If conversation hangs, logout to interrupt")):
                    action Function(store.maica.maica_instance.close_wss_session)

            else:
                # Intentionally disabled until a usable saved token exists.
                textbutton _("> Connect with current token")

            textbutton _("> MAICA params and settings {size=-10}*May need restarting to take effect"):
                action Show("maica_setting")

            if log_hasupdate:
                textbutton _("> Update and service status tracker {size=-10}* Update available"):
                    action Show("maica_log")
            else:
                textbutton _("> Changelogs and serving status"):
                    action Show("maica_log")
            if pane_cache.get("donation_exists", False):
                textbutton _("> Donate to MAICA"):
                    action Show("maica_support")


screen maica_setting():

    python:
        store.len = len


    default tooltip = Tooltip("")
    default target_lang_mode_before_edit = persistent._maica_target_lang_mode
    default tz_mode_before_edit = persistent._maica_tz_mode

    on "show" action Show("maica_setting_tooltip", tooltip=tooltip)
    on "hide" action Hide("maica_setting_tooltip")

    python:
        submods_screen = store.renpy.get_screen("maica_setting", "screens")

        if submods_screen:
            store._tooltip = submods_screen.scope.get("tooltip", None)
        else:
            store._tooltip = None

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

                text "push_mpostal_read: [has_mail_waitsend() and mas_isMoniAff(higher=True) and renpy.seen_label('maica_wants_mspire') and renpy.seen_label('maica_wants_mpostal') and not mas_inEVL('maica_mpostal_received') and not mas_inEVL('maica_mpostal_read')]"

                text "push_mspire_want: [renpy.seen_label('maica_greeting') and not renpy.seen_label('maica_wants_mspire') and renpy.seen_label('mas_random_ask')]"

                $ triggered_list = maica_escape_display_text(store.maica.maica_instance.mtrigger_manager.triggered_list)
                text "triggered_list: [triggered_list]"

                textbutton _("Write Event information to the log"):
                    action Function(log_eventstat)

                textbutton _("Push sentence-splitting test"):
                    action [
                                Hide("maica_setting"),
                                Function(store.maica_apply_setting),
                                Function(store.MASEventList.push, "text_split")
                            ]

                textbutton _("Push chat loop"):
                    action [
                                Hide("maica_setting"),
                                Function(store.maica_apply_setting),
                                Function(store.MASEventList.push, "maica_main.talking_start")
                                ]
                textbutton _("Push MSpire"):
                    action [
                                Hide("maica_setting"),
                                Function(store.maica_apply_setting),
                                Function(store.MASEventList.push, "maica_mspire")
                                ]
                textbutton _("Push maica_mpostal_read"):
                    action [
                                    Hide("maica_setting"),
                                    Function(store.maica_apply_setting),
                                    Function(store.MASEventList.push, "maica_mpostal_read")
                                ]
                textbutton _("Push maica_mpostal_load"):
                    action [
                                    Hide("maica_setting"),
                                    Function(store.maica_apply_setting),
                                    Function(store.MASEventList.push, "maica_mpostal_load")
                                ]
                textbutton _("Push maica_raw_context_example"):
                    action [
                                    Hide("maica_setting"),
                                    Function(store.maica_apply_setting),
                                    Function(store.MASEventList.push, "maica_raw_context_example")
                                ]

                textbutton _("Show maica_gen_quality_chk_notify 0.3"):
                    action Function(store.maica_handle_quality_status, False, 0.3)

                textbutton _("Show maica_gen_quality_chk_notify 0.6"):
                    action Function(store.maica_handle_quality_status, False, 0.6)

                textbutton _("Show maica_gen_quality_chk_notify 0.9"):
                    action Function(store.maica_handle_quality_status, False, 0.9)

            hbox:
                use divider(_("Connection and Safety"))

            hbox:
                style_prefix "maica_check"
                textbutton maica_escape_display_text(renpy.substitute(_("Current provider: [store.maica.maica_instance.provider_manager.get_server_info().get('name', 'Unknown')]"))):
                    action Show("maica_node_setting")
                    hovered SetField(_tooltip, "value", _("Choose provider"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                style_prefix "maica_check_nohover"
                $ user_disp = store.maica.maica_instance.user_acc or renpy.substitute(_("Not logged in"))
                textbutton maica_escape_display_text(renpy.substitute(
                    _("Current user: [user_disp]"),
                    scope={"user_disp": user_disp}
                )):
                    action NullAction()
                    hovered SetField(_tooltip, "value", _("To change account or logout, navigate to Submods menu.\n* To change account properties or password, navigate to registration site"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("Auto reconnect: [persistent.maica_setting_dict.get('auto_reconnect')]"):
                    action ToggleDict(persistent.maica_setting_dict, "auto_reconnect", True, False)
                    hovered SetField(_tooltip, "value", _("Automatically reconnect on connection close"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("Generation resume: [persistent.maica_setting_dict.get('auto_resume')]"):
                    action ToggleDict(persistent.maica_setting_dict, "auto_resume", True, False)
                    hovered SetField(_tooltip, "value", _("Resume streaming on reconnection to recover lost chunks"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("Keep connection active: [persistent.maica_setting_dict.get('keep_alive')]"):
                    action ToggleDict(persistent.maica_setting_dict, "keep_alive", True, False)
                    hovered SetField(_tooltip, "value", _("Send ping packets timely to keep connection alive and calculate lag"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                use divider(_("Performance and Behavior"))

            hbox:
                style_prefix "maica_check"
                textbutton _("Target language: [persistent.maica_setting_dict.get('target_lang')]"):
                    action Show("maica_select_language")
                    hovered SetField(_tooltip, "value", _("Target generation language. Supports \"zh\", \"en\", and \"auto\".\n* This setting cannot guarantee the generated language\n* It also affects the default timezone, holidays, culture, and more; using your actual native language is recommended\n* auto asks the model to choose a response language through the prompt and is not equivalent to selecting that language explicitly\n* At the time of writing, MAICA's official deployment remains less capable in English than in Chinese"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "maica_check"
                textbutton _("Behavior preset: [maica_get_preset_name('behavior')]"):
                    action Show("maica_select_preset", preset_type="behavior")
                    hovered SetField(_tooltip, "value", _("These settings affect model and tool co-working behavior of MAICA.\n* Changing this preset will affect tools, enhancements and prompts around core model, together with time consumation\n! Do not modify unless you know what they exactly mean"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "maica_check"
                textbutton _("Hyperparameter preset: [maica_get_preset_name('hyperparameter')]"):
                    action Show("maica_select_preset", preset_type="hyperparameter")
                    hovered SetField(_tooltip, "value", _("These settings affect core model's performance.\n* Changing this preset will directly affect core model's inference and sampling procedure\n! Do not modify unless you know what they exactly mean"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "maica_check_nohover"
                text _("* The remaining settings in this section are managed by presets.\n* Do not modify manually unless you know what they exactly mean")

            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("MFocus enabled: [persistent.maica_setting_dict.get('enable_mf')]"):
                    action ToggleDict(persistent.maica_setting_dict, "enable_mf", True, False)
                    hovered SetField(_tooltip, "value", _("An agent model will recieve input prior to the core model, and acquire information with tools.\n* MFocus is a major mechanism of MAICA, suggested to enable"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("MTrigger enabled: [persistent.maica_setting_dict.get('enable_mt')]"):
                    action ToggleDict(persistent.maica_setting_dict, "enable_mt", True, False)
                    hovered SetField(_tooltip, "value", _("An agent model will recieve input subsequent to the core model, and guide character's action.\n* MTrigger is a major mechanism of MAICA, suggested to enable"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("Session quality review: [persistent.maica_setting_dict.get('gen_quality_chk')]"):
                    action ToggleDict(persistent.maica_setting_dict, "gen_quality_chk", True, False)
                    hovered SetField(_tooltip, "value", _("Require MNerve to check generation quality after session exceeds 3 rounds.\n+ Quantitatively evaluate generation quality\n- Extra consumation of MNerve"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("Input language detection: [persistent.maica_setting_dict.get('input_lang_detect')]"):
                    action ToggleDict(persistent.maica_setting_dict, "input_lang_detect", True, False)
                    hovered SetField(_tooltip, "value", _("Raise a warning if input language is not target language.\n* Suggested to enable in normal cases"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("Realtime post proceeding: [persistent.maica_setting_dict.get('pprt')]"):
                    action ToggleDict(persistent.maica_setting_dict, "pprt", True, False)
                    hovered SetField(_tooltip, "value", _("Enable backend sentence breaking and realtime post proceeding.\n* Suggested to enable in normal cases"))
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
                        textbutton _("Enable customized advanced parameters: [persistent.maica_setting_dict.get('use_custom_model_config')]"):
                            action ToggleDict(persistent.maica_setting_dict, "use_custom_model_config", True, False)
                            hovered SetField(_tooltip, "value", _("Advanced parameters could significantly affect the model's performance.\n* The default is already the best field-tested config, so it's not suggested to enable this"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        style_prefix "maica_check"
                        if persistent.maica_setting_dict.get('use_custom_model_config'):
                            textbutton _("Adjust advanced params"):
                                style "maica_check_button"
                                action Show("maica_advance_setting")
                        else:
                            textbutton _("Adjust advanced params"):
                                style "maica_check_button_disabled"
                                action Show("maica_advance_setting")
            hbox:
                use divider(_("Sessions and Data"))

            hbox:
                style_prefix "generic_fancy_check"
                if store.maica.savefile_access_marker_exists():
                    textbutton _("Use persistent file: [persistent.maica_setting_dict.get('savefile_access')]"):
                        action ToggleDict(persistent.maica_setting_dict, "savefile_access", True, False)
                        hovered SetField(_tooltip, "value", _("Model will ignore savefile data if this is disabled.\n* MAICA Blessland uploads savefile on each restart automatically"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)
                else:
                    textbutton _("Use persistent file: [persistent.maica_setting_dict.get('savefile_access')]"):
                        style "generic_fancy_check_button_disabled"
                        action ToggleDict(persistent.maica_setting_dict, "savefile_access", True, False)
                        hovered SetField(_tooltip, "value", _("Model will ignore savefile data if this is disabled.\n! savefile_access marker does not exist, savefile will not be uploaded or applied"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)

            if persistent.maica_setting_dict['mspire_session'] != 0 and persistent.maica_setting_dict['chat_session'] == persistent.maica_setting_dict['mspire_session']:
                $ tooltip_chat_session = _("Each session stores and applies history context independently.\n* Set to 0 to disable context (single round conversation)\n! Current session same as MSpire session, may cause confusing behaviour")
                hbox:
                    style_prefix "maica_check_nohover"
                    text _("! Current main session is set to same as MSpire session which may cause unexpected issues.\n! Please avoid setting these the same value (except 0) unless you literally understand what you're doing."):
                        color "#FF0000"
            else:
                $ tooltip_chat_session = _("Each session stores and applies history context independently.\n* Set to 0 to disable context (single round conversation)")
            use num_bar(_("Current chat session"), 200 if config.language == "chinese" else 350, tooltip_chat_session, "chat_session", 0, 9)


            $ tooltip_session_length = _("Max length each session will preserve, in range of 512-28672.\n* Every 3 ASCII characters occupy one space\n* MAICA crops the former part of context on exceeding to no more than 2/3 left\n* Too high or too low value can cause performance and generation quality issues")
            use prog_bar(_("Chat session length"), 400 if config.language == "chinese" else 450, tooltip_session_length, "session_len_limit", 512, 28672)
            textbutton _("Reset chat session length"):
                action SetDict(persistent.maica_setting_dict, "session_len_limit", 8192)

            hbox:
                style_prefix "maica_check"
                textbutton _("Timezone: [persistent.maica_setting_dict.get('tz')]"):
                    action Show("maica_tz_setting")

            hbox:
                style_prefix "maica_check"
                textbutton maica_escape_display_text(renpy.substitute(_("Geolocation: [persistent.mas_geolocation]"))):
                    action Show("maica_location_input", addition = persistent.mas_geolocation)

            hbox:
                frame:
                    xmaximum 950
                    xpos 4
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True
                    $ tooltip_mf_info = _("User-provided implementations, handled and sent to core model by MFocus.\n* May need a restart for changes to take effect")
                    hbox:
                        style_prefix "maica_check_nohover"
                        textbutton _("[len(persistent.mas_player_additions)] MFocus info present"):
                            action NullAction()
                            hovered SetField(_tooltip, "value", tooltip_mf_info)
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("Edit MFocus info"):
                            action Show("maica_addition_setting")
                            hovered SetField(_tooltip, "value", tooltip_mf_info)
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("Export MFocus info to main directory"):
                            action Function(export_player_information)
                            hovered SetField(_tooltip, "value", _("Export to game/Submods/MAICA_ChatSubmod/player_info.txt"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                use divider(_("Tools and Functions"))

            if not persistent._mas_enable_random_repeats:
                hbox:
                    style_prefix "generic_fancy_check"
                    textbutton _("Enable MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"):
                        action ToggleDict(persistent.maica_setting_dict, "mspire_enable", True, False)
                        hovered SetField(_tooltip, "value", _("Enable MSpire to generate vanilla-like conversations.\n* Repeat topics must be disabled to take effect\n* MSpire doesn't use MF/MT"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)
            else:
                hbox:
                    textbutton _("Enable MSpire: [persistent.maica_setting_dict.get('mspire_enable')]"):
                        style "generic_fancy_check_button_disabled"
                        action ToggleDict(persistent.maica_setting_dict, "mspire_enable", True, False)
                        hovered SetField(_tooltip, "value", _("Enable MSpire to generate vanilla-like conversations.\n! Repeat topice enabled, with which MSpire conflicts"))
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
                        textbutton _("MSpire topics"):
                            action Show("maica_mspire_category_setting")


                    $ tooltip_ms_time = _("Minimal interval of MSpire conversations")
                    use prog_bar(_("MSpire minimal interval"), 250 if config.language == "chinese" else 400, tooltip_ms_time, "mspire_interval", 10, 180, "m")

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("MSpire searching method: [persistent.maica_setting_dict.get('mspire_search_type')]"):
                            action [
                                    Show("maica_mspire_setting")
                                        ]
                            hovered SetField(_tooltip, "value", _("Way of MSpire searching for topics"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    if persistent.maica_setting_dict['mspire_session'] == 0:
                        hbox:
                            style_prefix "generic_fancy_check"
                            textbutton _("Use cache for MSpire"):
                                action ToggleDict(persistent.maica_setting_dict, "mspire_use_cache", True, False)
                                hovered SetField(_tooltip, "value", _("Enable MSpire cache.\n* Does not take effect if MSpire session not 0\n* Enforces default super params"))
                                unhovered SetField(_tooltip, "value", _tooltip.default)
                    else:
                        hbox:
                            textbutton _("Use cache for MSpire"):
                                style "generic_fancy_check_button_disabled"
                                action ToggleDict(persistent.maica_setting_dict, "mspire_use_cache", True, False)
                                hovered SetField(_tooltip, "value", _("Enable MSpire cache.\n! MSpire session not 0, with which MSpire cache conflicts"))
                                unhovered SetField(_tooltip, "value", _tooltip.default)

                    if persistent.maica_setting_dict['mspire_session'] != 0 and persistent.maica_setting_dict['chat_session'] == persistent.maica_setting_dict['mspire_session']:
                        $ tooltip_ms_session = _("Session MSpire uses.\n* Set to 0 to disable context (single round conversation)\n* MSpire will offer choice to continue if not 0\n! Currently same as main session, auto resetting disabled")
                        hbox:
                            style_prefix "maica_check_nohover"
                            text _("! Current main session is set to same as MSpire session which may cause unexpected issues.\n! Please avoid setting these the same value (except 0) unless you literally understand what you're doing."):
                                color "#FF0000"
                    else:
                        $ tooltip_ms_session = _("Session MSpire uses.\n* Set to 0 to disable context (single round conversation)\n* MSpire will offer choice to continue if not 0\n! This session resets before MSpire generation every time")
                    use num_bar(_("MSpire session"), 200 if config.language == "chinese" else 350, tooltip_ms_session, "mspire_session", 0, 9)

            hbox:
                style_prefix "maica_check"
                textbutton _("Mtrigger triggers list"):
                    action Show("maica_triggers")
                    hovered SetField(_tooltip, "value", _("Configure MTrigger triggers"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            if maica_topic_ready("mvista"):
                hbox:
                    style_prefix "maica_check"
                    textbutton _("MVista images"):
                        action Show("maica_vista_filelist")
                        hovered SetField(_tooltip, "value", _("View and manage MVista images.\n* Please read TOS carefully and be responsible for your own privacy"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)

            else:
                hbox:
                    textbutton _("MVista images"):
                        style "maica_check_button_disabled"
                        action Show("maica_vista_filelist")
                        hovered SetField(_tooltip, "value", _("View and manage MVista images.\n! MVista not unlocked, please continue chatting with Monika patiently or send her letters"))
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
                        textbutton _("Reread MPostal letters"):
                            action Show("maica_mpostals")
                            hovered SetField(_tooltip, "value", _("Reread MPostal history letters"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    $ tooltip_mp_time = _("Minimal interval of MPostal replies")
                    use prog_bar(_("MPostal minimal interval"), 250 if config.language == "chinese" else 400, tooltip_mp_time, "mpostal_default_reply_time", 10, 720, "m")

            hbox:
                use divider(_("Interfaces and Log"))

            hbox:
                style_prefix "maica_check"
                textbutton _("submod_log.log verbosity: [logging.getLevelName(persistent.maica_setting_dict['log_level'])]"):
                    action Show("maica_select_log_level", log = "log_level")#Function(store.change_loglevel)
                    hovered SetField(_tooltip, "value", _("Lower level logs will not appear in submod_log.log.\n* This effect is global"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:

                use prog_bar(expl=_("Status code update interval"), len=250 if config.language == "chinese" else 400, tooltip="The refreshing frequency of status code on Submod screen", var="status_update_time", min=1, max=60, istime="s")

            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("Dynamic Heaven Forest"):
                    action ToggleDict(persistent.maica_setting_dict, "use_anim_background", True, False)
                    hovered SetField(_tooltip, "value", _("Use dynamic forest background with improved illumination, may increase render consumation. Restart to take effect.\n* Remove some spritepacks or disable this if VRAM overflows"))
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
                        textbutton _("Debugging console: [persistent.maica_setting_dict.get('console')]"):
                            action ToggleDict(persistent.maica_setting_dict, "console", True, False)
                            hovered SetField(_tooltip, "value", _("Show debugging console while chatting\nI think this looks cool xd"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        style_prefix "maica_check"
                        textbutton _("Console font: [persistent.maica_setting_dict.get('console_font')]"):
                            action Show("maica_select_console_font")#ToggleDict(persistent.maica_setting_dict, "console_font", store.maica_confont, store.mas_ui.MONO_FONT)
                            hovered SetField(_tooltip, "value", _("Decides what font should console display in. \nmplus-1mn-medium.ttf for default, SarasaMonoTC-SemiBold.ttf may behave better with non-ascii characters."))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("Console logging verbosity: [logging.getLevelName(persistent.maica_setting_dict['log_conlevel'])]"):
                            action Show("maica_select_log_level", log = "log_conlevel")
                            hovered SetField(_tooltip, "value", _("Lower level logs will not appear in console"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("Show console on MPostal writing reply"):
                            action ToggleDict(persistent.maica_setting_dict, "show_console_when_reply", True, False)

            hbox:
                use divider(_("Statics and Information"))

            hbox:
                style_prefix "maica_check"
                textbutton (_("Expand performance monitor") if store.nvw_folded else _("Retract performance monitor")):
                    action [
                        Function(toggle_var, "nvw_folded")
                        ]
                    hovered SetField(_tooltip, "value", _("Expand/retract server performance monitor"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            if not store.nvw_folded:
                hbox:
                    xpos 30
                    use maica_workload_stat()

            hbox:
                style_prefix "maica_check"
                textbutton (_("Expand statics") if store.stat_folded else _("Retract statics")):
                    action [
                        Function(toggle_var, "stat_folded")
                        ]
                    hovered SetField(_tooltip, "value", _("Expand/retract client-side statics"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            if not store.stat_folded:
                hbox:
                    xpos 30
                    use maica_statics()


        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Save settings"):
                action [
                        Function(store.maica_apply_setting),
                        Hide("maica_setting")
                        ]
            textbutton _("Discard modifications"):
                action [
                        Function(
                            store.maica_discard_setting,
                            target_lang_mode_before_edit,
                            tz_mode_before_edit
                        ),
                        Hide("maica_setting")
                        ]
            textbutton _("Reset defaults"):
                action [
                        Function(store.maica_reset_advanced_setting),
                        Function(store.maica_reset_setting),
                        Function(store.maica_apply_setting, ininit = True),
                        Function(renpy.notify, _("MAICA: Settings reset")),
                        Hide("maica_setting")
                    ]

screen maica_setting_tooltip(tooltip):
    zorder 95

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

            textbutton _("Quit{#maica_host_quit}"):
                selected False
                action Return("nevermind")

            textbutton _("Paste{#maica_host_paste}"):
                selected False
                action [Function(maica_input.set_text, pygame.scrap.get(pygame.SCRAP_TEXT).strip()),Function(maica_input.set_text, pygame.scrap.get(pygame.SCRAP_TEXT).strip())]
            if maica_topic_ready("mvista"):
                textbutton renpy.substitute(_("Choose images | ")) + str(len(store._maica_selected_visuals)) + renpy.substitute(_(" chosen")):
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

            textbutton _("Quit{#maica_host_quit}"):
                selected False
                action Return("nevermind")

            textbutton _("Paste{#maica_host_paste}"):
                selected False
                action [Function(maica_input_information.set_text, pygame.scrap.get(pygame.SCRAP_TEXT).strip()),Function(maica_input_information.set_text, pygame.scrap.get(pygame.SCRAP_TEXT).strip())]


        vbox:
            align (0.5, 0.5)
            spacing 30

            text prompt style "input_prompt"
            input:
                id "input"
                value maica_input_information
