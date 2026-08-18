init python:

    def maica_hide_quality_chibi():
        renpy.hide("chibi_peek")
        renpy.transition(moveoutleft, layer="master")

    def maica_handle_quality_status(reasonable, confidence):
        if reasonable or not store.maica.maica_instance.gen_quality_chk:
            return
        if confidence < 0.5:
            return
        if confidence < 0.8:
            renpy.notify(_("MAICA: Please reset session if quality decreases notably"))
            return

        renpy.show_screen("maica_gen_quality_chk_notify", confidence)
        renpy.show(
            "chibi_peek",
            zorder=MAS_BACKGROUND_Z - 1,
            at_list=[],
            layer="master",
            what=None,
            tag=None
        )
        renpy.transition(moveinleft, layer="master")


screen maica_gen_quality_chk_notify(prob = 1.0):
    modal False
    zorder 100
    on "show" action If(not persistent.maica_setting_dict["gen_quality_chk"], Hide("maica_gen_quality_chk_notify"))
    on "hide" action Function(maica_hide_quality_chibi)

    default countdown = 10

    frame:
        xalign 1.0
        yalign 0.0
        xoffset -5
        yoffset 5
        xsize 400
        ysize 300
        background "mod_assets/console/gen_quality_chk.png"
        padding (15, 15)

        vbox:
            spacing 5
            xfill True

            text _("Generation quality warning"):
                style "confirm_prompt"
                color "#ff6666"
                size 22
                xalign 0.5

            text _("Confidence: {color=#ff6666}[prob:.0%]{/color}"):
                size 10
                xalign 0.5

            text _("[player], is she behaving inappropriate in some way?"):
                size 15
                color "#ffffff"
                xalign 0.0

            text _("Reality here is not stable. Resetting session may allow her to rethink a bit."):
                size 15
                color "#ffffff"
                xalign 0.0

            text _("You decide, but things may go worse if you don't."):
                size 15
                color "#ffffff"
                xalign 0.0

            text _("Don't embarrass her... nor let her look at the window!"):
                size 15
                color "#ffffff"
                xalign 0.0

        vbox:
            spacing 5
            yalign 1.0
            xfill True

            hbox:
                xalign 0.5
                spacing 10
                style_prefix "confirm"

                textbutton _("Reset session"):
                    action [Function(reset_session), Hide("maica_gen_quality_chk_notify")]

                textbutton _("Ignore{#maica_host_ignore}"):
                    action Hide("maica_gen_quality_chk_notify")

            text _("Dismissing in [countdown] seconds..."):
                size 10
                color "#aaaaaa"
                xalign 0.5

    timer 1.0 repeat True action If(countdown > 0, SetScreenVariable("countdown", countdown - 1), Hide("maica_gen_quality_chk_notify"))
    timer 5.0 action Function(maica_hide_quality_chibi)

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
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "console_font"

            use divider_small(maica_log.get("title"))

            for content in maica_log.get("content"):
                text content.replace("[", "[[").replace("{", "{{").replace("【", "【【"):
                    size 18
                use divider_plain_small()
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Close{#maica_host_close}"):
                action Hide("maica_log")

screen maica_tz_setting():
    python:
        store.timezone_dict = store.maica_timezone_dict
        store.timezone_list = sorted(list(store.timezone_dict.keys()))
        current_tz = store.maica_get_system_timezone()

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "generic_fancy_check"

            text _("{size=-10}If your timezone is not listed here, decide by your local UTC timezone.")

            hbox:
                style_prefix "maica_check"
                textbutton _("Language default"):
                    action [
                        SetDict(persistent.maica_setting_dict, "tz", 'Asia/Shanghai' if store.maica.maica_instance.target_lang == store.maica.maica_instance.MaicaAiLang.zh_cn else 'America/Indiana/Vincennes'),
                        SetField(persistent, "_maica_tz_mode", "manual")
                    ]

            hbox:
                style_prefix "maica_check"
                textbutton _("System default"):
                    action [
                        SetDict(persistent.maica_setting_dict, "tz", current_tz),
                        SetField(persistent, "_maica_tz_mode", "system")
                    ]

            for item in timezone_list:
                hbox:
                    textbutton "UTC" + "{}".format("+" if item >= 0 else "") + str(item) + "|" + timezone_dict[item]:
                        action [
                            SetDict(persistent.maica_setting_dict, "tz", timezone_dict[item]),
                            SetField(persistent, "_maica_tz_mode", "manual")
                        ]
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Close{#maica_host_close}"):
                action Hide("maica_tz_setting")


screen maica_advance_setting():
    $ _tooltip = store._tooltip

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "generic_fancy_check"
            hbox:
                style_prefix "maica_check"
                text _("For detailed explainations of these params, refer to "):
                    size 20
                textbutton _("{u}MAICA official documents{/u}"):
                    action OpenURL("https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Documents.md")
                    text_size 20
                text _(" and "):
                    size 20
                textbutton _("{u}OpenAI documents{/u}"):
                    action OpenURL("https://www.openaidoc.com.cn/api-reference/chat" if config.language == "chinese" else "https://platform.openai.com/docs/api-reference/completions/create#completions_create")
                    text_size 20
            hbox:
                text _("{size=-10}Caution: only checked params will take effect, others will remain server default")
            hbox:
                if not persistent.maica_setting_dict.get('use_custom_model_config'):
                    text _("{size=-10}You have not enabled advanced parameters, thus settings on this page will not take effect!")

            use divider_small(_("Super params"))
            $ sdict = "maica_advanced_setting"

            hbox:
                $ tooltip_max_tokens = _("The limit of tokens model can generate one round. Normally don't affect performance, but stops generating on hitting the limit")
                spacing 5
                textbutton "max_tokens":
                    action ToggleDict(persistent.maica_advanced_setting_status, "max_tokens")
                    hovered SetField(_tooltip, "value", tooltip_max_tokens)
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.maica_advanced_setting_status.get("max_tokens", False):
                    use prog_bar("max_tokens", 250, tooltip_max_tokens, "max_tokens", 1, 2048, sdict=sdict)

            hbox:
                $ tooltip_seed = _("Generation seed. Normally a minor and random factor")
                spacing 5
                textbutton "seed":
                    action ToggleDict(persistent.maica_advanced_setting_status, "seed")
                    hovered SetField(_tooltip, "value", tooltip_seed)
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("seed", False):
                    use num_bar("seed", 200, tooltip_seed, "seed", -2147483648, 2147483647, sdict=sdict)

            hbox:
                $ tooltip_top_p = _("Token weight filter percentage. Seriously do not touch this")
                spacing 5
                textbutton "top_p":
                    action ToggleDict(persistent.maica_advanced_setting_status, "top_p")
                    hovered SetField(_tooltip, "value", tooltip_top_p)
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.maica_advanced_setting_status.get("top_p", False):
                    use prog_bar("top_p", 250, tooltip_top_p, "top_p", 0.1, 1.0, sdict=sdict)

            hbox:
                $ tooltip_temperature = _("The randomness tokens are chosen. Higher this value, larger the offset between model performance and generally best performance")
                spacing 5
                textbutton "temperature":
                    action ToggleDict(persistent.maica_advanced_setting_status, "temperature")
                    hovered SetField(_tooltip, "value", tooltip_temperature)
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("temperature", False):
                    use prog_bar("temperature", 250, tooltip_temperature, "temperature", 0.0, 1.0, sdict=sdict)

            hbox:
                $ tooltip_frequency_penalty = _("Token frequency penalty. Higher this value, less likely repeatedly appeared tokens continue appearing, usually resulting in shorter and more expanding generation")
                spacing 5
                textbutton "frequency_penalty":
                    action ToggleDict(persistent.maica_advanced_setting_status, "frequency_penalty")
                    hovered SetField(_tooltip, "value", tooltip_frequency_penalty)
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("frequency_penalty", False):
                    use prog_bar("frequency_penalty", 250, tooltip_frequency_penalty, "frequency_penalty", 0.0, 1.0, sdict=sdict)

            hbox:
                $ tooltip_presence_penalty = _("Token presence penalty. Higher this value, less likely appeared tokens appear again, usually resulting in more jumping generation")
                spacing 5
                textbutton "presence_penalty":
                    action ToggleDict(persistent.maica_advanced_setting_status, "presence_penalty")
                    hovered SetField(_tooltip, "value", tooltip_presence_penalty)
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("presence_penalty", False):
                    use prog_bar("presence_penalty", 250, tooltip_presence_penalty, "presence_penalty", 0.0, 1.0, sdict=sdict)

            use divider_small(_("Advanced settings"))

            hbox:
                spacing 5
                textbutton "prompt_pname_repl":
                    action ToggleDict(persistent.maica_advanced_setting_status, "prompt_pname_repl")
                    hovered SetField(_tooltip, "value", _("Replace [[player] in prompts and guidance with the player's real name.\n+ Gives the model a concrete understanding of the player's name\n- Increases the risk of inconsistent or confused behavior"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('prompt_pname_repl')
                if persistent.maica_advanced_setting_status.get("prompt_pname_repl", False):
                    textbutton "[persistent.maica_advanced_setting.get('prompt_pname_repl', False)]":
                        action ToggleDict(persistent.maica_advanced_setting, "prompt_pname_repl")
            hbox:
                spacing 5
                textbutton "prompt_allow_nickname":
                    action ToggleDict(persistent.maica_advanced_setting_status, "prompt_allow_nickname")
                    hovered SetField(_tooltip, "value", _("Experimental: allow model to generate [[player_nickname] placeholder in prompts.\n+ Fits MAS-style better\n- Requires additional frontend handling\n- May cause unexpected issues"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('prompt_allow_nickname')
                if persistent.maica_advanced_setting_status.get("prompt_allow_nickname", False):
                    textbutton "[persistent.maica_advanced_setting.get('prompt_allow_nickname', True)]":
                        action ToggleDict(persistent.maica_advanced_setting, "prompt_allow_nickname")
            hbox:
                spacing 5
                textbutton "mf_llm_concl":
                    action ToggleDict(persistent.maica_advanced_setting_status, "mf_llm_concl")
                    hovered SetField(_tooltip, "value", _("Require the agent model to generate final guidance instead of the default MFocus guidance.\n+ Higher information density and more natural language\n- Depends heavily on the agent model's instruction-following ability and can be counterproductive\n- Usually neutralizes mf_const_tools when enabled"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('mf_llm_concl')
                if persistent.maica_advanced_setting_status.get("mf_llm_concl", False):
                    textbutton "[persistent.maica_advanced_setting.get('mf_llm_concl', False)]":
                        action ToggleDict(persistent.maica_advanced_setting, "mf_llm_concl")

            hbox:
                $ tooltip_mf_sf_access_impl = _("Experimental: implementation of possibly faster savefile access, replacing traditional MFocus implementation.\n* 0: (Traditional) LLM-only implementation\n* 1: RAG + reranker implementation\n* 2: RAG-only implementation\n+ Could be a lot, lot faster\n+ mf_const_sf_access can be enabled only if this is nonzero\n- RAG-only mode does not search from per-query savefile\n- Significantly less precise than traditional implementation, demanding core model's distraction resistance\n- Falls back to 0 if backend does not implement optional requirements")
                spacing 5
                textbutton "mf_sf_access_impl":
                    action [ToggleDict(persistent.maica_advanced_setting_status, "mf_sf_access_impl"), Function(maica_clamp_advanced_setting, "mf_sf_access_impl", 0, 2)]
                    hovered SetField(_tooltip, "value", tooltip_mf_sf_access_impl)
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("mf_sf_access_impl", False):
                    use num_bar("mf_sf_access_impl", 200, tooltip_mf_sf_access_impl, "mf_sf_access_impl", 0, 2, sdict=sdict)

            hbox:
                $ tooltip_const_sfa = _("Experimental: provide extracted information even when MFocus does not call savefile access.\n* 0: (Traditional) MFocus tool only\n* 1: Pre-retrieval + tool\n* 2: Pre-retrieval only\n+ Significantly increases interventionality of savefile data\n- Can introduce distractions and demands core model's distraction resistance\n- Just wasting time in more than half cases")
                spacing 5
                textbutton "mf_const_sf_access":
                    action [ToggleDict(persistent.maica_advanced_setting_status, "mf_const_sf_access"), Function(maica_clamp_advanced_setting, "mf_const_sf_access", 0, 2)]
                    hovered SetField(_tooltip, "value", tooltip_const_sfa)
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("mf_const_sf_access", False):
                    use num_bar("mf_const_sf_access", 200, tooltip_const_sfa, "mf_const_sf_access", 0, 2, sdict=sdict)

            hbox:
                $ tooltip_const_tools = _("Provide some tool results even when MFocus does not call a tool.\n* 0: Disabled\n* 1: Provide the current time and holidays\n* 2: Also provide the current date and attempt to provide local weather\n+ Mitigates hallucinations caused by missing information and enables more flexible, considerate responses\n- May cause distraction and confusion")
                spacing 5
                textbutton "mf_const_tools":
                    action [ToggleDict(persistent.maica_advanced_setting_status, "mf_const_tools"), Function(maica_clamp_advanced_setting, "mf_const_tools", 0, 2)]
                    hovered SetField(_tooltip, "value", tooltip_const_tools)
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("mf_const_tools", False):
                    use num_bar("mf_const_tools", 200, tooltip_const_tools, "mf_const_tools", 0, 2, sdict=sdict)

            hbox:
                spacing 5
                textbutton "esearch_llm_concl":
                    action ToggleDict(persistent.maica_advanced_setting_status, "esearch_llm_concl")
                    hovered SetField(_tooltip, "value", _("Require MFocus to reorganize Internet search results.\n+ Higher information density and more stable behavior in most cases\n+ Force enabled if backend using responses SERP implementation\n- Slower generation when Internet search is involved\n- May mislead the core model's response style"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('esearch_llm_concl')
                if persistent.maica_advanced_setting_status.get("esearch_llm_concl", False):
                    textbutton "[persistent.maica_advanced_setting.get('esearch_llm_concl', True)]":
                        action ToggleDict(persistent.maica_advanced_setting, "esearch_llm_concl")
            hbox:
                spacing 5
                textbutton "mf_precheck_mt":
                    action ToggleDict(persistent.maica_advanced_setting_status, "mf_precheck_mt")
                    hovered SetField(_tooltip, "value", _("Require MFocus to precheck the player's request and provide guidance when MTrigger is present.\n+ Mitigates MTrigger desynchronization in principle\n- May make the language less natural in rare cases"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('mf_precheck_mt')
                if persistent.maica_advanced_setting_status.get("mf_precheck_mt", False):
                    textbutton "[persistent.maica_advanced_setting.get('mf_precheck_mt', True)]":
                        action ToggleDict(persistent.maica_advanced_setting, "mf_precheck_mt")

            hbox:
                $ tooltip_memory_concl_arc = _("Experimental: generate memory summary when session trimmed or cleared to preserve information.\n* 0: Disabled\n* 1: Rotate on trimming only\n* 2: Rotate on both trimming and clearing\n+ Generates conclusion for rounds leaving context window, as short-term memory\n- Operations triggering summarizing could be much slower\n- May cause distraction and demands core model's distraction resistance")
                spacing 5
                textbutton "memory_concl_arc":
                    action [ToggleDict(persistent.maica_advanced_setting_status, "memory_concl_arc"), Function(maica_clamp_advanced_setting, "memory_concl_arc", 0, 2)]
                    hovered SetField(_tooltip, "value", tooltip_memory_concl_arc)
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("memory_concl_arc", False):
                    use num_bar("memory_concl_arc", 200, tooltip_memory_concl_arc, "memory_concl_arc", 0, 2, sdict=sdict)

            hbox:
                spacing 5
                textbutton "nsfw_acceptive":
                    action ToggleDict(persistent.maica_advanced_setting_status, "nsfw_acceptive")
                    hovered SetField(_tooltip, "value", _("Ask the model to treat toxic content tolerantly and positively.\n+ Surprisingly improves model behavior in most situations, even without toxic content\n- May cause unexpected issues, although none have been observed so far"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('nsfw_acceptive')
                if persistent.maica_advanced_setting_status.get("nsfw_acceptive", False):
                    textbutton "[persistent.maica_advanced_setting.get('nsfw_acceptive', True)]":
                        action ToggleDict(persistent.maica_advanced_setting, "nsfw_acceptive")

            hbox:
                $ tooltip_mf_context_rnds = _("Provide extra context for analysis when MFocus intervenes. Range: 0-5.\n+ Improves MFocus's understanding of coherent conversations\n- Increases the risk of disrupting MFocus's response pattern")
                spacing 5
                textbutton "mf_context_rnds":
                    action ToggleDict(persistent.maica_advanced_setting_status, "mf_context_rnds")
                    hovered SetField(_tooltip, "value", tooltip_mf_context_rnds)
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("mf_context_rnds", False):
                    use num_bar("mf_context_rnds", 200, tooltip_mf_context_rnds, "mf_context_rnds", 0, 5, sdict=sdict)

            hbox:
                $ tooltip_mt_context_rnds = _("Provide history context for MTrigger, in range of 0-5 rounds.\n+ Improves MTrigger's understanding to serial conversation\n- Risk of breaking MTrigger reply pattern")
                spacing 5
                textbutton "mt_context_rnds":
                    action ToggleDict(persistent.maica_advanced_setting_status, "mt_context_rnds")
                    hovered SetField(_tooltip, "value", tooltip_mt_context_rnds)
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("mt_context_rnds", False):
                    use num_bar("mt_context_rnds", 200, tooltip_mt_context_rnds, "mt_context_rnds", 0, 5, sdict=sdict)

            hbox:
                spacing 5
                textbutton "mf_disable_loop":
                    action ToggleDict(persistent.maica_advanced_setting_status, "mf_disable_loop")
                    hovered SetField(_tooltip, "value", _("Disable MFocus sequential toolchain to save time.\n+ Saves time for most toolcalls, lowers TTFT\n- Risk of missing information\n- Will neutralize mf_llm_concl"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('mf_disable_loop')
                if persistent.maica_advanced_setting_status.get("mf_disable_loop", False):
                    textbutton "[persistent.maica_advanced_setting.get('mf_disable_loop', True)]":
                        action ToggleDict(persistent.maica_advanced_setting, "mf_disable_loop")
            hbox:
                spacing 5
                textbutton "mt_disable_loop":
                    action ToggleDict(persistent.maica_advanced_setting_status, "mt_disable_loop")
                    hovered SetField(_tooltip, "value", _("Disable the MTrigger toolchain loop to save time.\n+ Saves time for most trigger calls\n- May miss calls"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('mt_disable_loop')
                if persistent.maica_advanced_setting_status.get("mt_disable_loop", False):
                    textbutton "[persistent.maica_advanced_setting.get('mt_disable_loop', True)]":
                        action ToggleDict(persistent.maica_advanced_setting, "mt_disable_loop")

            hbox:
                spacing 5
                textbutton "gen_enforce_lang":
                    action ToggleDict(persistent.maica_advanced_setting_status, "gen_enforce_lang")
                    hovered SetField(_tooltip, "value", _("Experimental: enforce the target output language through LLM guided decoding (guided_regex).\n* At the time of writing, this is only effective for target language en\n* Regex guidance support varies by decoding backend and may fail or behave incorrectly\n* Enabling this may affect model behavior or cause other unexpected issues"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('gen_enforce_lang')
                if persistent.maica_advanced_setting_status.get("gen_enforce_lang", False):
                    textbutton "[persistent.maica_advanced_setting.get('gen_enforce_lang', True)]":
                        action ToggleDict(persistent.maica_advanced_setting, "gen_enforce_lang")

        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Save settings"):
                action [
                    Hide("maica_advance_setting"),
                    Function(renpy.notify, _("MAICA: Advanced settings saved"))
                ]
            textbutton _("Discard changes"):
                action [
                    Function(store.maica_discard_advanced_setting),
                    Hide("maica_advance_setting"),
                    Function(renpy.notify, _("MAICA: Advanced setting changes discarded"))
                ]
            textbutton _("Reset defaults"):
                action [
                    Function(store.maica_reset_advanced_setting),
                    Hide("maica_advance_setting"),
                    Function(renpy.notify, _("MAICA: Advanced settings reset") if store.maica.maica_instance.is_accessable() else _("MAICA: Advanced settings reset (local default)"))
                ]


screen maica_select_language():
    modal True
    zorder 92

    use maica_setter_small_frame(ok_action=Hide("maica_select_language")):
        style_prefix "generic_fancy_check"
        hbox:
            textbutton _("zh | Chinese simplified"):
                action [
                    SetDict(persistent.maica_setting_dict, "target_lang", store.maica.maica_instance.MaicaAiLang.zh_cn),
                    SetField(persistent, "_maica_target_lang_mode", "manual")
                ]
        hbox:
            textbutton _("en | English"):
                action [
                    SetDict(persistent.maica_setting_dict, "target_lang", store.maica.maica_instance.MaicaAiLang.en),
                    SetField(persistent, "_maica_target_lang_mode", "manual")
                ]
        hbox:
            textbutton _("auto | Auto"):
                action [
                    SetDict(persistent.maica_setting_dict, "target_lang", store.maica.maica_instance.MaicaAiLang.auto),
                    SetField(persistent, "_maica_target_lang_mode", "manual")
                ]


screen maica_select_preset(preset_type):
    modal True
    zorder 92

    $ presets, setting_keys, advanced_keys = store._maica_preset_definition(preset_type)
    $ preset_title = _("Behavior preset") if preset_type == "behavior" else _("Hyperparameter preset")
    $ _tooltip = store._tooltip

    use maica_setter_small_frame(title=preset_title, ok_action=Hide("maica_select_preset")):
        style_prefix "generic_fancy_check"
        for preset in presets:
            hbox:
                textbutton _(preset["name"]):
                    action Function(store.maica_apply_preset, preset_type, preset)
                    hovered SetField(_tooltip, "value", _(preset["description"]))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected store.maica_preset_matches(preset_type, preset)


default use_email = True
screen maica_login():
    modal True
    zorder 92

    $ ok_action = [
                    Function(store.maica.maica_instance._gen_token, store._maica_LoginAcc, store._maica_LoginPw, "", store._maica_LoginEmail if store._maica_LoginEmail != "" else None),
                    Function(_maica_verify_token),
                    Function(_maica_clear),
                    Hide("maica_login")
                    ]
    $ cancel_action = [Function(_maica_clear), Hide("maica_login")]

    use maica_setter_medium_frame(ok_action=ok_action, cancel_action=cancel_action):

        hbox:
            if use_email:
                textbutton _("Enter DCC account email"):
                    style "confirm_button"
                    action Show("maica_login_input",message = _("Enter DCC account email{#maica_login_prompt}"),returnto = "_maica_LoginEmail")
            else:
                textbutton _("Enter DCC account username"):
                    style "confirm_button"
                    action Show("maica_login_input",message = _("Enter DCC account username{#maica_login_prompt}") ,returnto = "_maica_LoginAcc")

        hbox:
            style_prefix "maica_check"
            if use_email:
                textbutton _("> Use username instead"):
                    text_size 15
                    action [ToggleVariable("use_email"), Function(_maica_clear)]
                    selected False

            else:
                textbutton _("> Use email instead"):
                    text_size 15
                    action [ToggleVariable("use_email"), Function(_maica_clear)]
                    selected False

        hbox:
            textbutton _("Enter password"):
                style "confirm_button"
                action Show("maica_login_input",message = _("Enter password{#maica_login_prompt}"),returnto = "_maica_LoginPw")
        hbox:
            text ""
        # hbox:
        #     textbutton _("Generate token online"):
        #         action [
        #             Function(store.maica.maica_instance._gen_token, store._maica_LoginAcc, store._maica_LoginPw, "", store._maica_LoginEmail if store._maica_LoginEmail != "" else None),
        #             Function(_maica_verify_token),
        #             Function(_maica_clear),
        #             Hide("maica_login")
        #             ]
        #     textbutton _("Cancel"):
        #         action [Function(_maica_clear), Hide("maica_login")]
        hbox:
            style_prefix "small_expl"
            text _("※ By using MAICA Blessland, you agree to "):
                size 15
            textbutton _("{u}MAICA ToS{/u}"):
                action OpenURL("https://maica.monika.love/tos")
                yalign 1.0

        hbox:
            style_prefix "small_expl"
            text _("※ No DCC account yet? "):
                size 15
            textbutton _("{u}Register now{/u}"):
                action OpenURL("https://maica.monika.love/tos")
                yalign 1.0


screen maica_login_input(message, returnto, ok_action = Hide("maica_login_input")):
    ## Ensure other screens do not get input while this screen is displayed.s
    modal True
    zorder 92

    use maica_setter_small_frame(message, ok_action):
        input default "" value VariableInputValue(returnto) length 64

screen maica_addition_input(addition="", edittarget=None):
    python:
        if persistent._mas_player_addition is None:
            persistent._mas_player_addition = addition
        def apply(edittarget):
            addition = maica_validate_player_addition(
                persistent._mas_player_addition,
                persistent.mas_player_additions,
                edittarget,
                prefix_player=edittarget is None
            )
            if addition is None:
                return
            if edittarget in persistent.mas_player_additions:
                persistent.mas_player_additions[persistent.mas_player_additions.index(edittarget)] = addition
            else:
                persistent.mas_player_additions.append(addition)
            renpy.notify(_("MAICA: Input saved"))
            del persistent._mas_player_addition
        def paste(content=None):
            if not content:
                content = (pygame.scrap.get(pygame.SCRAP_TEXT).strip() or pygame.scrap.get(pygame.SCRAP_TEXT).strip())
            if content:
                persistent._mas_player_addition = content
        def clear():
            persistent._mas_player_addition = ''

    modal True
    zorder 92

    use maica_setter_medium_frame(title=renpy.substitute(_("Enter MFocus info")), ok_action=[Function(apply, edittarget), Hide("maica_addition_input")], cancel_action=[SetField(persistent, "_mas_player_addition", None), Hide("maica_addition_input")]):
        hbox:
            xfill True
            hbox:
                xalign 0.0
                input default addition value FieldInputValue(persistent, "_mas_player_addition")
            hbox:
                xalign 0.9
                yalign 0.5
                if not persistent._mas_player_addition:
                    textbutton _("Paste{#maica_host_paste}"):
                        style "mas_button_simple"
                        action Function(paste)
                else:
                    textbutton _("Clear{#mas_apikeys}"):
                        style "mas_button_simple"
                        action Function(clear)

screen maica_mspire_input(addition="", edittarget=None):
    python:
        if persistent._mas_player_addition is None:
            persistent._mas_player_addition = addition
        def apply(edittarget):
            addition = persistent._mas_player_addition
            if not persistent._mas_player_addition.strip:
                return
            if addition in persistent.maica_setting_dict["mspire_category"]:
                return
            if edittarget:
                persistent.maica_setting_dict["mspire_category"][persistent.maica_setting_dict["mspire_category"].index(edittarget)] = addition
            else:
                persistent.maica_setting_dict["mspire_category"].append(addition)
            del persistent._mas_player_addition
        def paste(content=None):
            if not content:
                content = (pygame.scrap.get(pygame.SCRAP_TEXT).strip() or pygame.scrap.get(pygame.SCRAP_TEXT).strip())
            if content:
                persistent._mas_player_addition = content
        def clear():
            persistent._mas_player_addition = ''

    modal True
    zorder 92

    use maica_setter_medium_frame(title=_("Enter MSpire topic"), ok_action=[Function(apply, edittarget), Hide("maica_mspire_input")], cancel_action=[SetField(persistent, "_mas_player_addition", None), Hide("maica_mspire_input")]):
        hbox:
            xfill True
            hbox:
                xalign 0.0
                input default addition value FieldInputValue(persistent, "_mas_player_addition")
            hbox:
                xalign 0.9
                yalign 0.5
                if not persistent._mas_player_addition:
                    textbutton _("Paste{#maica_host_paste}"):
                        style "mas_button_simple"
                        action Function(paste)
                else:
                    textbutton _("Clear{#mas_apikeys}"):
                        style "mas_button_simple"
                        action Function(clear)

screen maica_location_input(addition="", edittarget=None):
    python:
        if persistent.mas_geolocation == None:
            persistent.mas_geolocation = ""
        if persistent._mas_geolocation == None:
            persistent._mas_geolocation = persistent.mas_geolocation
        def cancel():
            persistent.mas_geolocation = persistent._mas_geolocation
        def verify(position):
            res = store.maica.maica_instance.verify_legality("geolocation", position)
            coordinates = store.maica.maica_instance.extract_legality_coordinates(res)
            if res.get("success", False) and coordinates is not None:
                latitude, longitude = coordinates
                coordinate_text = renpy.substitute(_("Latitude: {0}\nLongitude: {1}")).format(latitude, longitude)
                renpy.show_screen("maica_message", message=renpy.substitute(_("Verification passed")) + "\n" + coordinate_text)
            else:
                reason = res.get("exception") or renpy.substitute(_("Coordinates unavailable"))
                renpy.show_screen("maica_message", message=renpy.substitute(_("Verification failed")) + "\n" + renpy.substitute(_("Reason: ")) + reason)


    modal True
    zorder 92

    use maica_setter_medium_frame(title=_("Please input your geolocation"), ok_action=[SetField(persistent ,"_mas_geolocation", None), Hide("maica_location_input")], cancel_action=[Function(cancel), SetField(persistent ,"_mas_geolocation", None), Hide("maica_location_input")]):
        hbox:
            xfill True
            hbox:
                xalign 0.0
                input default addition value FieldInputValue(persistent, "mas_geolocation")
            hbox:
                xalign 0.9
                yalign 0.5
                textbutton _("Verify"):
                    style "mas_button_simple"
                    action Function(verify, persistent.mas_geolocation)

screen maica_addition_setting():
    default selected_indices = set()
    $ additions = persistent.mas_player_additions
    $ selected_item = maica_selected_item(additions, selected_indices)

    modal True
    zorder 92
    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "generic_fancy_check"
            for index, item in enumerate(additions):
                hbox:
                    textbutton maica_escape_display_text(item):
                        action ToggleSetMembership(selected_indices, index)

        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Delete item"):
                action [
                    SensitiveIf(bool(selected_indices)),
                    Function(maica_delete_selected_items, additions, selected_indices)
                ]

            textbutton _("Edit item"):
                action [
                    SensitiveIf(selected_item is not None),
                    SetScreenVariable("selected_indices", set()),
                    Show("maica_addition_input", addition=selected_item, edittarget=selected_item)
                ]

            textbutton _("Add item"):
                action [SetScreenVariable("selected_indices", set()), Show("maica_addition_input")]

            textbutton _("Close{#maica_host_close}"):
                action Hide("maica_addition_setting")


screen maica_mspire_category_setting():
    default selected_indices = set()
    $ categories = persistent.maica_setting_dict["mspire_category"]
    $ selected_item = maica_selected_item(categories, selected_indices)

    modal True
    zorder 92
    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "generic_fancy_check"
            for index, item in enumerate(categories):
                hbox:
                    textbutton maica_escape_display_text(item):
                        action ToggleSetMembership(selected_indices, index)

        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Delete item"):
                action [
                    SensitiveIf(bool(selected_indices)),
                    Function(maica_delete_selected_items, categories, selected_indices)
                ]

            textbutton _("Edit item"):
                action [
                    SensitiveIf(selected_item is not None),
                    SetScreenVariable("selected_indices", set()),
                    Show("maica_mspire_input", addition=selected_item, edittarget=selected_item)
                ]

            textbutton _("Add item"):
                action [SetScreenVariable("selected_indices", set()), Show("maica_mspire_input")]

            textbutton _("Close{#maica_host_close}"):
                action Hide("maica_mspire_category_setting")


screen maica_node_setting():
    $ _tooltip = store._tooltip
    python:
        def set_provider(id):
            persistent.maica_setting_dict["provider_id"] = id

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():

            for provider in store.maica.maica_instance.provider_manager._servers:
                use maica_l2_subframe():
                    text str(provider.get('id')) + ' | ' + provider.get('name')


                    hbox:
                        text renpy.substitute(_("Intro: ")) + provider.get('description', 'Device not provided')
                    hbox:
                        text renpy.substitute(_("Model: ")) + provider.get('servingModel', 'No model provided')


                hbox:
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("Use this server"):
                            action [
                                # Function(set_provider, provider.get('id')),
                                Function(sync_provider_id, provider.get('id')),
                                Hide("maica_node_setting")
                            ]
                            selected persistent.maica_setting_dict["provider_id"] == provider.get('id')
                    hbox:
                        style_prefix "maica_check"
                        textbutton renpy.substitute(_("> Go to portal page")) + "(" + provider.get('portalPage') + ")":
                            action OpenURL(provider.get('portalPage'))

                    if provider.get("isOfficial", False):
                        hbox:
                            style_prefix "maica_check_nohover"
                            textbutton _(" <Official>")

        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Refresh servers list"):
                action Function(store.maica.maica_instance.provider_manager.get_provider)

            textbutton _("Close{#maica_host_close}"):
                action Hide("maica_node_setting")

            textbutton _("Test current node avaliability"):
                action Function(store.maica.maica_instance.accessable)

screen maica_mspire_setting():
    $ _tooltip = store._tooltip

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():

            style_prefix "generic_fancy_check"
            textbutton "precise_page":
                action SetDict(persistent.maica_setting_dict, "mspire_search_type", "precise_page")
            text _("Select the single most related page, ignoring sample range. Relatively fast since no recursive search performed.\n"):
                style "small_expl_hw"
                size 15
            textbutton "fuzzy_page":
                action SetDict(persistent.maica_setting_dict, "mspire_search_type", "fuzzy_page")
            text _("Select one random from multiple related pages. Relatively fast since no recursive search performed.\n"):
                style "small_expl_hw"
                size 15
            textbutton "in_precise_category":
                action SetDict(persistent.maica_setting_dict, "mspire_search_type", "in_precise_category")
            text _("Select the single most related category, then recursively search pages and subcategories. Relatively slow.\n"):
                style "small_expl_hw"
                size 15
            textbutton "in_fuzzy_category":
                action SetDict(persistent.maica_setting_dict, "mspire_search_type", "in_fuzzy_category")
            text _("Select one random from multiple related categories, then recursively search pages and subcategories. Relatively slow.\n"):
                style "small_expl_hw"
                size 15
            textbutton "in_fuzzy_all":
                action SetDict(persistent.maica_setting_dict, "mspire_search_type", "in_fuzzy_all")
            text _("Select related pages, categories and subcategories recursively. Relatively slow.\n"):
                style "small_expl_hw"
                size 15

        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Close{#maica_host_close}"):
                action Hide("maica_mspire_setting")

                # textbutton _("当前方式: [persistent.maica_setting_dict.get('mspire_search_type', 'None')]")


screen maica_triggers():
    $ _tooltip = store._tooltip
    python:
        maica_triggers = store.maica.maica_instance.mtrigger_manager

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():

            style_prefix "generic_fancy_check"
            text _("MTrigger space usage: ")

            if maica_triggers.get_length(0) > maica_triggers.MAX_LENGTH_REQUEST * 0.75:
                text "request: " + str(maica_triggers.get_length(0)) + " / " + str(maica_triggers.MAX_LENGTH_REQUEST):
                    color "#FF0000"
            else:
                text "request: " + str(maica_triggers.get_length(0)) + " / " + str(maica_triggers.MAX_LENGTH_REQUEST)

            if maica_triggers.get_length(1) > maica_triggers.MAX_LENGTH_TABLE * 0.9:
                text "table: " + str(maica_triggers.get_length(1)) + " / " + str(maica_triggers.MAX_LENGTH_TABLE):
                    color "#FF0000"
            else:
                text "table: " + str(maica_triggers.get_length(1)) + " / " + str(maica_triggers.MAX_LENGTH_TABLE)

            if maica_triggers.get_length(0) > maica_triggers.MAX_LENGTH_REQUEST * 0.75 or maica_triggers.get_length(1) > maica_triggers.MAX_LENGTH_TABLE * 0.9:
                text _("> Notice: Some MTriggers will be disabled if content length exceeds!"):
                    color "#ff0000"
                    size 15

            for trigger in maica_triggers.triggers:
                use maica_l2_subframe():
                    label trigger.name
                    if not maica_triggers.trigger_status(trigger.name) or not trigger.condition():
                        hbox:
                            text _("Space used: -"):
                                size 15
                    elif trigger.method == 0:
                        hbox:
                            text _("Space used: request"):
                                size 15
                            text str(len(trigger)):
                                size 15
                    elif trigger.method == 1:
                        hbox:
                            text _("Space used: table"):
                                size 15
                            text str(len(trigger)):
                                size 15

                    hbox:
                        if hasattr(trigger, 'web_musicplayer_installed'):
                            text _("Integrated | Change BGM{#maica_trigger_screen}"):
                                size 15
                            hbox:
                                style_prefix "small_expl_hw"
                                text _("* Supports "):
                                    size 15
                                textbutton "{u}Netease Music{/u}":
                                    action OpenURL("https://github.com/MAS-Submod-MoyuTeam/NeteaseInMas")
                                text _(" and "):
                                    size 15
                                textbutton "{u}Youtube Music{/u}":
                                    action OpenURL("https://github.com/Booplicate/MAS-Submods-YouTubeMusic")
                                text _(" Submods"):
                                    size 15

                        else:
                            text trigger.description:
                                size 15



                    hbox:
                        if trigger.condition():
                            if maica_triggers.trigger_status(trigger.name):
                                textbutton _("Enabled"):
                                    action Function(maica_triggers.disable_trigger, trigger.name)
                                    selected maica_triggers.trigger_status(trigger.name)
                            else:
                                textbutton _("Disabled"):
                                    action Function(maica_triggers.enable_trigger, trigger.name)
                                    selected maica_triggers.trigger_status(trigger.name)

                        elif trigger.condition() == False:
                            if maica_triggers.trigger_status(trigger.name):
                                textbutton _("Requirements not satisfied"):
                                    style "generic_fancy_check_button_disabled"
                                    action Function(maica_triggers.disable_trigger, trigger.name)
                                    selected maica_triggers.trigger_status(trigger.name)
                            else:
                                textbutton _("Requirements not satisfied"):
                                    style "generic_fancy_check_button_disabled"
                                    action Function(maica_triggers.enable_trigger, trigger.name)
                                    selected maica_triggers.trigger_status(trigger.name)

                        # elif trigger.condition() == None:
                        #     if maica_triggers.trigger_status(trigger.name):
                        #         textbutton _("Requirements not satisfied"):
                        #             style "generic_fancy_check_button_disabled"
                        #             action Function(maica_triggers.disable_trigger, trigger.name)
                        #             selected maica_triggers.trigger_status(trigger.name)
                        #     else:
                        #         textbutton _("Requirements not satisfied"):
                        #             style "generic_fancy_check_button_disabled"
                        #             action Function(maica_triggers.enable_trigger, trigger.name)
                        #             selected maica_triggers.trigger_status(trigger.name)

        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Close{#maica_host_close}"):
                action Hide("maica_triggers")

screen maica_mpostals():
    python:
        import time
        maica_triggers = store.maica.maica_instance.mtrigger_manager
        preview_len = 200

        def _delete_postal(postal):
            for index, item in enumerate(persistent._maica_send_or_received_mpostals):
                if item is postal:
                    persistent._maica_send_or_received_mpostals.pop(index)
                    store.maica.delete_mpostal_record_files(postal)
                    break

    $ _tooltip = store._tooltip

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():

            style_prefix "maica_check"
            hbox:
                text ""
            for postal in persistent._maica_send_or_received_mpostals:
                use maica_l2_subframe():
                    label postal["raw_title"]:
                        style "maica_check_nohover_label"
                    text "":
                        style "small_link"
                    text renpy.substitute(_("MPostal status:")) + postal["responsed_status"]:
                        xalign 0.0
                        style "small_link"
                    text renpy.substitute(_("Last post sent at: ")) + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(postal["time"].split(".")[0]))):
                        xalign 0.0
                        style "small_link"
                    text renpy.substitute(_("\n[player]: \n")) + postal["raw_content"][:preview_len].replace("\n", "") + ("..." if len(postal["raw_content"]) > preview_len else  ""):
                        xalign 0.0
                        style "small_expl_hw"
                    if postal["responsed_content"] != "":
                        python:
                            preview_text = postal["responsed_content"][:preview_len].replace("\n", "")
                            for pair in [(r'[', r']'), (r'{', r'}')]:
                                while preview_text.count(pair[0]) > preview_text.count(pair[1]):
                                    preview_text = preview_text[:preview_text.rfind(pair[0])]
                        text renpy.substitute(_("[m_name]: \n")) + preview_text  + ("..." if len(postal["responsed_content"]) > preview_len else  "") + "\n":
                            xalign 0.0
                            style "small_expl_hw"
                    python:
                        preview_info = None
                        for preview_source in (
                            postal.get('raw_image_preview'),
                            postal.get('vista_image_info'),
                        ):
                            preview_info = store.maica.maica_instance.vista_manager.get_thumbnail_info(preview_source)
                            if preview_info:
                                break
                    if preview_info:
                        $ img_path = preview_info[0]
                        add img_path
                    elif postal.get('vista_image_info') or postal.get('raw_image'):
                        text _("Image preview unavailable")
                    hbox:
                        style_prefix "confirm"
                        textbutton _("Read [player]'s letter"):
                            action [
                                    Function(store.maica_apply_setting),
                                    Function(_maica_call_in_new_context_preserve_layers, "maica_mpostal_show_backtoscreen", postal["raw_content"])
                            ]
                        if postal["responsed_content"] != "":
                            textbutton _("Read [m_name]'s reply"):
                                action [
                                        Function(store.maica_apply_setting),
                                        Function(_maica_call_in_new_context_preserve_layers, "maica_mpostal_show_backtoscreen", postal["responsed_content"])
                                ]

                        if postal["responsed_status"] in ("fatal"):
                            textbutton _("Resend mail"):
                                action SetDict(postal, "responsed_status", "delaying")
                        hbox:
                            textbutton _("Delete"):
                                action Function(_delete_postal, postal)

        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Close{#maica_host_close}"):
                action Hide("maica_mpostals")

screen maica_support():

    modal True
    zorder 92

    use maica_setter_medium_frame(title=_("Donate to MAICA"), ok_action=Hide("maica_support")):
        hbox:
            text _("We're grateful for your being willing to donate.\nThe donate will likely never cover our cost, but that's okay anyway."):
                size 20
        hbox:
            style_prefix "maica_check_nohover"
            text _("Please note that donating to MAICA doesn't give you any actual privilege. It's simply donation."):
                size 15
            text "\n":
                size 15
        hbox:
            xalign 0.5
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

screen maica_workload_stat_lite():
    python:
        onliners = store.maica.maica_instance.workload_raw.get("onliners")
        ai = store.maica.maica_instance
        data = ai.get_workload_lite()
        store.update_interval = 15

        @store.workload_throttle
        def check_and_update():
            store.maica.maica_instance.update_workload()

    zorder 90
    fixed:
        frame:
            xsize 619
            xoffset 5 yoffset 450
            background "mod_assets/console/cn_frame_stats.png"
            has vbox:
                xoffset 5
            hbox:
                text renpy.substitute(_("Current onliners: ")) + str(onliners):
                    size 15
                hbox:
                    text "  ":
                        size 15
                    text renpy.substitute(_("Analytics refresh")):
                        size 15
                    text store.maica.progress_bar(((store.workload_throttle.remain / store.update_interval)) * 100, bar_length = 10, total=store.update_interval, unit="s"):
                        size 15
                        font maica_confont
                    timer 1.0 repeat True action Function(check_and_update)

            hbox:
                text "VRAM " + (maica.progress_bar(data["total_inuse_vmem"]  * 100 / data["total_vmem"], total=int(data["total_vmem"]), unit="MiB", bar_length = 35) if data["total_vmem"] != 0 else "No memory information"):
                    size 14
                    font maica_confont
            hbox:
                text "UTIL " + maica.progress_bar(data["avg_usage"], total=int(data["max_tflops"]), unit="TFlops", bar_length = 35):
                    size 14
                    font maica_confont




screen maica_workload_stat():
    $ _tooltip = store._tooltip
    python:
        stat = {k: v for k, v in iterize(store.maica.maica_instance.workload_raw) if k != "onliners"}
        onliners = store.maica.maica_instance.workload_raw.get("onliners")
    python:
        store.update_interval = 15

        @store.workload_throttle
        def check_and_update():
            store.maica.maica_instance.update_workload()

    modal True
    zorder 90

    style_prefix "check"

    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            style_prefix "maica_default_small"
            xsize 942
            spacing 5

            text renpy.substitute(_("Current onliners: ")) + str(onliners)

            for server in stat:

                use divider_small(server)

                for card in stat[server]:
                    hbox:
                        text stat[server][card]["name"]:
                            size 15
                        text store.maica.progress_bar(stat[server][card]["mean_utilization"], total=int(stat[server][card]["tflops"]), unit="TFlops"):
                            size 10
                            font maica_confont

                        text "VRAM: " + str(stat[server][card]["mean_memory"]) + " / " + str(stat[server][card]["vram"]):
                            size 10
                        text renpy.substitute(_("Mean power consumption: ")) + str(stat[server][card]["mean_consumption"]) + "W":
                            size 10
                text ""

            hbox:
                text renpy.substitute(_("Analytics refresh")):
                    size 15
                text store.maica.progress_bar(((store.workload_throttle.remain / store.update_interval)) * 100, bar_length = 78, total=store.update_interval, unit="s"):
                    size 15
                    font maica_confont
                timer 1.0 repeat True action Function(check_and_update)

screen maica_select_console_font():
    modal True
    zorder 92

    use maica_setter_small_frame(ok_action=Hide("maica_select_console_font")):
        style_prefix "generic_fancy_check"
        hbox:
            textbutton _("SarasaMonoTC | monospaced"):
                action SetDict(persistent.maica_setting_dict, "console_font", store.maica_confont)
        hbox:
            textbutton _("mplus-1mn | monospaced {size=-10}*Has issue with Chinese characters{/size}"):
                action SetDict(persistent.maica_setting_dict, "console_font", store.mas_ui.MONO_FONT)

screen maica_select_log_level(log = "log_level"):
    modal True
    zorder 92
    python:
        import logging
        log_levels = [
            (logging.NOTSET, _("NOTSET")),
            (logging.DEBUG, _("DEBUG")),
            (logging.INFO, _("INFO")),
            (logging.WARNING, _("WARNING")),
            (logging.ERROR, _("ERROR")),
            (logging.CRITICAL, _("CRITICAL"))
        ]

    use maica_setter_small_frame(ok_action=Hide("maica_select_log_level")):
        style_prefix "generic_fancy_check"
        for level, name in log_levels:
            hbox:
                textbutton "{} | {}".format(level, name):
                    action SetDict(persistent.maica_setting_dict, log, level)
                    selected level == persistent.maica_setting_dict[log]

screen maica_statics():
    $ _tooltip = store._tooltip

    modal True
    zorder 90

    style_prefix "check"

    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            style_prefix "maica_default_small"
            xsize 942
            spacing 5
            hbox:
                text _("Total conversation rounds: [store.maica.maica_instance.stat.get('message_count')]"):
                    size 20
            hbox:
                text _("Total MSpire rounds: [store.maica.maica_instance.stat.get('mspire_count')]"):
                    size 20
            hbox:
                text _("Total chunks received: [store.maica.maica_instance.stat.get('received_token')]"):
                    size 20
            hbox:
                text _("Overall chunks received: [store.maica.maica_instance.stat.get('received_token_by_session')]"):
                    size 20
            hbox:
                text _("MPostal sent count: [store.maica.maica_instance.stat.get('mpostal_count')]"):
                    size 20
            hbox:
                $ user_disp = store.maica.maica_instance.user_acc or renpy.substitute(_("Not logged in"))
                text _("Current user: [user_disp]"):
                    size 20

            hbox:
                xpos 10
                style_prefix "confirm"
                textbutton _("Reset statistics"):
                    action Function(store.maica.maica_instance.reset_stat)

screen maica_input_lang_warning():

    modal True
    zorder 99

    use maica_setter_small_frame(title=_("Input language warning"), ok_action=Hide("maica_input_lang_warning")):
        $ current_lang = store.maica.maica_instance.target_lang
        hbox:
            text _("Your input language seemingly differs from target language."):
                size 20
        hbox:
            text _("Your current MAICA target language is '[current_lang]'. Please adjust your setting to chat in another language."):
                size 20
        hbox:
            style_prefix "maica_check_nohover"
            text _("Language mismatch could impact performance or lead to unexpected issues, please avoid mismatched input or session context.\nIf you want to force proceed, please disable 'Input language detection' in settings."):
                size 15
