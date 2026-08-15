from pathlib import Path


CHAT_SOURCE = (
    Path(__file__).resolve().parents[1]
    / "game"
    / "Submods"
    / "MAICA_ChatSubmod"
    / "chat.rpy"
).read_text(encoding="utf-8")
MIGRATION_SOURCE = (
    Path(__file__).resolve().parents[1]
    / "game"
    / "Submods"
    / "MAICA_ChatSubmod"
    / "migrations.rpy"
).read_text(encoding="utf-8")
API_SOURCE = (
    Path(__file__).resolve().parents[1]
    / "game"
    / "Submods"
    / "MAICA_ChatSubmod"
    / "api.rpy"
).read_text(encoding="utf-8")
TL_CHAT_SOURCE = (
    Path(__file__).resolve().parents[1]
    / "game"
    / "Submods"
    / "MAICA_ChatSubmod"
    / "tl"
    / "chat.rpy"
).read_text(encoding="utf-8")
TL_DESCRIPTION_SOURCE = (
    Path(__file__).resolve().parents[1]
    / "game"
    / "Submods"
    / "MAICA_ChatSubmod"
    / "tl"
    / "maica_description.rpy"
).read_text(encoding="utf-8")


def _event_block(eventlabel):
    marker = 'eventlabel="{}"'.format(eventlabel)
    start = CHAT_SOURCE.index(marker)
    end = CHAT_SOURCE.find("\ninit ", start + len(marker))
    return CHAT_SOURCE[start:] if end == -1 else CHAT_SOURCE[start:end]


def _registration_block(eventlabel):
    marker = 'eventlabel="{}"'.format(eventlabel)
    event_start = CHAT_SOURCE.index(marker)
    start = CHAT_SOURCE.rfind("\ninit ", 0, event_start)
    start = 0 if start == -1 else start + 1
    end = CHAT_SOURCE.find("\ninit ", event_start)
    return CHAT_SOURCE[start:] if end == -1 else CHAT_SOURCE[start:end]


def _function_block(function_name):
    marker = "    def {}(".format(function_name)
    start = CHAT_SOURCE.index(marker)
    end = CHAT_SOURCE.find("\n    def ", start + len(marker))
    return CHAT_SOURCE[start:] if end == -1 else CHAT_SOURCE[start:end]


def _label_block(label):
    markers = ("label {}:".format(label), "label {}(".format(label))
    starts = [CHAT_SOURCE.find(marker) for marker in markers]
    start = min(index for index in starts if index >= 0)
    marker = CHAT_SOURCE[start : CHAT_SOURCE.find("\n", start)]
    end = CHAT_SOURCE.find("\nlabel ", start + len(marker))
    return CHAT_SOURCE[start:] if end == -1 else CHAT_SOURCE[start:end]


def _assert_in_order(source, markers):
    positions = [source.index(marker) for marker in markers]
    assert positions == sorted(positions)


def _without_whitespace(source):
    return "".join(source.split())


def test_chat_topics_and_translations_follow_the_unlock_order():
    event_order = (
        "maica_prepend_1",
        "maica_greeting",
        "maica_main",
        "maica_wants_location2",
        "maica_mods_location",
        "maica_wants_preferences2",
        "maica_mods_preferences",
        "maica_wants_mspire",
        "maica_wants_mpostal",
        "maica_pre_wants_mvista",
        "maica_chr_corrupted2",
        "maica_chr_gone",
        "maica_chr2",
        "maica_mspire",
        "maica_mpostal_received",
        "maica_mpostal_replyed",
        "maica_prepend_reread",
        "maica_wants_location_reread",
        "maica_wants_preferences_reread",
        "maica_wants_mspire_reread",
        "maica_wants_mpostal_reread",
        "maica_wants_mvista_reread",
        "maica_chr_reread",
    )
    _assert_in_order(
        CHAT_SOURCE,
        tuple('eventlabel="{}"'.format(label) for label in event_order),
    )

    label_order = (
        "maica_prepend_1",
        "maica_greeting",
        "maica_main",
        "maica_set_location",
        "maica_wants_location2",
        "maica_mods_location",
        "maica_wants_preferences2",
        "maica_mods_preferences",
        "maica_wants_mspire",
        "maica_mspire",
        "maica_wants_mpostal",
        "maica_mpostal_received",
        "maica_mpostal_replyed",
        "mas_corrupted_postmail",
        "maica_pre_wants_mvista",
        "maica_wants_mvista",
        "maica_chr2",
        "maica_chr_gone",
        "maica_chr_corrupted2",
        "maica_prepend_reread",
        "maica_wants_location_reread",
        "maica_wants_preferences_reread",
        "maica_wants_mspire_reread",
        "maica_wants_mpostal_reread",
        "maica_wants_mvista_reread",
        "maica_chr_reread",
    )
    _assert_in_order(
        CHAT_SOURCE,
        tuple("label {}".format(label) for label in label_order),
    )

    user_facing_order = (
        "maica_main",
        "maica_mods_location",
        "maica_mods_preferences",
        "maica_prepend_reread",
        "maica_wants_location_reread",
        "maica_wants_preferences_reread",
        "maica_wants_mspire_reread",
        "maica_wants_mpostal_reread",
        "maica_wants_mvista_reread",
        "maica_chr_reread",
    )
    _assert_in_order(
        TL_DESCRIPTION_SOURCE,
        tuple('"{}"'.format(label) for label in user_facing_order),
    )

    translated_prompt_order = (
        "Let's go to the Heaven Forest",
        "Adjust [player]'s address",
        "Adjust [player]'s preferences",
        "What exactly is the Heaven Forest?",
        "About [player]'s address",
        "About [player]'s preferences",
        "About 'MSpire'",
        "About 'MPostal'",
        "About 'MVista'",
        "The Heaven Forest character file",
    )
    _assert_in_order(
        TL_CHAT_SOURCE,
        tuple('old "{}"'.format(prompt) for prompt in translated_prompt_order),
    )


def test_first_chat_end_uses_rounds_from_the_current_attempt():
    prepend = _label_block("maica_prepend_2")
    end = _label_block("maica_end_1")

    assert (
        "maica_message_count_before = "
        "store.maica.maica_instance.stat.get('message_count', 0) or 0"
    ) in prepend
    assert (
        "maica_message_count_after = "
        "store.maica.maica_instance.stat.get('message_count', 0) or 0"
    ) in prepend
    assert (
        "conv_rounds = max(0, "
        "maica_message_count_after - maica_message_count_before)"
    ) in prepend
    assert "call maica_end_1(conv_rounds)" in prepend
    assert "label maica_end_1(conv_rounds=0):" in end
    assert "stat.get('message_count')" not in end


def test_chat_success_is_recorded_from_the_talking_result_not_rounds():
    recorder = _function_block("maica_record_successful_chat")
    helper = _function_block("maica_has_successful_chat")
    greeting = _label_block("maica_prepend_2")
    main_talking = _label_block(".talking_start")

    assert "next_successful_chat_count" in recorder
    assert "message_count" not in recorder
    assert "maica_get_successful_chat_count() > 0" in helper
    assert "$ maica_talking_result = _return" in greeting
    assert "$ maica_record_successful_chat(maica_talking_result)" in greeting
    assert "$ maica_talking_result = _return" in main_talking
    assert "$ maica_record_successful_chat(maica_talking_result)" in main_talking
    assert main_talking.count("$ maica_record_successful_chat(") == 1
    assert main_talking.index("jump .talking_start") < main_talking.index(
        "$ maica_record_successful_chat("
    )

    assert "maica_has_successful_chat()" in _function_block("push_mspire_want")
    assert "maica_has_successful_chat()" in _event_block("maica_wants_location2")


def test_chat_progression_uses_successful_entry_count():
    assert "persistent._maica_successful_chat_count" in CHAT_SOURCE
    for eventlabel in (
        "maica_chr2",
        "maica_wants_preferences2",
        "maica_wants_location2",
        "maica_pre_wants_mvista",
    ):
        event = _event_block(eventlabel)
        assert "random=False" in event
        assert "action=EV_ACT_QUEUE" in event

    assert "maica_get_successful_chat_count() >= 2" in _event_block(
        "maica_wants_preferences2"
    )
    assert "maica_get_successful_chat_count() >= 3" in _event_block(
        "maica_pre_wants_mvista"
    )
    assert "maica_get_successful_chat_count() >= 4" in _event_block(
        "maica_chr2"
    )
    assert "maica_get_successful_chat_count() >= 2" in _registration_block(
        "maica_wants_mpostal"
    )
    assert "mas_getEV('maica_main').shown_count" not in CHAT_SOURCE


def test_main_flavor_dialogue_uses_completed_successful_entries():
    main = _label_block("maica_main")

    assert "$ successful_chat_count = maica_get_successful_chat_count()" in main
    assert "successful_chat_count == 10" in main
    assert "successful_chat_count >= 13" in main
    assert "successful_chat_count >= 21" in main


def test_manually_gated_pool_topics_are_excluded_from_mas_auto_unlock():
    eventlabels = (
        "maica_main",
        "maica_mods_preferences",
        "maica_mods_location",
        "maica_prepend_reread",
        "maica_chr_reread",
        "maica_wants_preferences_reread",
        "maica_wants_location_reread",
        "maica_wants_mspire_reread",
        "maica_wants_mpostal_reread",
        "maica_wants_mvista_reread",
    )

    for eventlabel in eventlabels:
        event = _event_block(eventlabel)
        assert "pool=True" in event
        assert '"no_unlock": None' in event


def test_maica_greetings_use_the_mas_selection_contract():
    for eventlabel in (
        "maica_chr_corrupted2",
        "maica_greeting",
        "maica_wants_mpostal",
    ):
        event = _registration_block(eventlabel)
        assert "unlocked=True" in event
        assert "persistent._mas_greeting_type is None" in event
        assert "not mas_isSpecialDay()" in event
        assert "not mas_isplayer_bday()" in event
        assert "action=EV_ACT_UNLOCK" not in event
        assert "prompt=" not in event

    assert 'MASPriorityRule.create_rule(0)' in CHAT_SOURCE
    assert CHAT_SOURCE.count('MASPriorityRule.create_rule(20)') == 2
    assert 'functionplugin("ch30_post_exp_check"' not in CHAT_SOURCE
    assert "selected_greeting" not in CHAT_SOURCE

    corruption = _registration_block("maica_chr_corrupted2")
    mpostal = _registration_block("maica_wants_mpostal")
    assert "renpy.seen_label('maica_prepend_2')" in corruption
    compact_mpostal = _without_whitespace(mpostal)
    assert '"andnot(maica_chr_changed"' in compact_mpostal
    assert '"andnotrenpy.seen_label(\'maica_chr_corrupted2\'))"' in compact_mpostal


def test_chat_side_branches_are_not_gated_by_chr2():
    assert "store.seen_event('maica_chr2')" not in _event_block("maica_chr_gone")
    assert "store.seen_event('maica_chr2')" not in _event_block(
        "maica_chr_corrupted2"
    )
    assert "not renpy.seen_label('maica_chr_gone')" in _event_block(
        "maica_chr2"
    )
    assert "not renpy.seen_label('maica_chr_corrupted2')" in _event_block(
        "maica_chr2"
    )


def test_every_reread_event_uses_its_source_topic():
    source_to_reread = {
        "maica_prepend_2": "maica_prepend_reread",
        "maica_wants_preferences2": "maica_wants_preferences_reread",
        "maica_wants_location2": "maica_wants_location_reread",
        "maica_wants_mspire": "maica_wants_mspire_reread",
        "maica_wants_mpostal": "maica_wants_mpostal_reread",
        "maica_pre_wants_mvista": "maica_wants_mvista_reread",
    }
    for source, reread in source_to_reread.items():
        block = _event_block(reread)
        assert "renpy.seen_label('{}')".format(source) in block
        assert "not renpy.seen_label('{}')".format(reread) in block
        assert "action=EV_ACT_UNLOCK" in block

    chr_reread = _event_block("maica_chr_reread")
    for source in ("maica_chr2", "maica_chr_gone", "maica_chr_corrupted2"):
        assert "renpy.seen_label('{}')".format(source) in chr_reread
    assert "not renpy.seen_label('maica_chr_reread')" in chr_reread
    assert "action=EV_ACT_UNLOCK" in chr_reread

    for reread in tuple(source_to_reread.values()) + ("maica_chr_reread",):
        assert 'eventlabel="{}"'.format(reread) in CHAT_SOURCE


def test_mpostal_conditional_attribute_is_looked_up_by_name():
    assert CHAT_SOURCE.count(
        'getattr(mas_getEV("maica_wants_mpostal"), "conditional", False)'
    ) == 2
    assert 'getattr(mas_getEV("maica_wants_mpostal"), conditional,' not in CHAT_SOURCE


def test_mspire_choices_and_dispatch_respect_the_registered_state():
    intro = _label_block("maica_wants_mspire")
    assert 'persistent.maica_setting_dict["mspire_enable"] = True' in intro
    assert 'persistent.maica_setting_dict["mspire_enable"] = False' in intro
    assert "mas_isMoniNormal(higher=True)" in _function_block("push_mspire_want")
    assert "mas_isMoniNormal(higher=True)" in _function_block("push_mspire")


def test_internal_events_do_not_define_user_facing_prompts():
    eventlabels = (
        "maica_prepend_1",
        "maica_chr2",
        "maica_chr_gone",
        "maica_wants_preferences2",
        "maica_wants_mspire",
        "maica_mpostal_received",
        "maica_mpostal_replyed",
        "maica_wants_location2",
        "maica_pre_wants_mvista",
        "maica_mspire",
    )

    for eventlabel in eventlabels:
        assert "prompt=" not in _event_block(eventlabel)

    obsolete_prompt_sources = (
        "Your reality?",
        "The Heaven Forest file",
        "Where did the Heaven Forest go?",
        "Learning about your preferences",
        "MAICA knocking",
        "The Heaven Forest seems broken",
    )
    for prompt in obsolete_prompt_sources:
        assert 'old "{}"'.format(prompt) not in TL_CHAT_SOURCE


def test_preferences_action_and_explanation_have_distinct_prompts():
    assert 'prompt=_("Adjust [player]\'s preferences")' in _event_block(
        "maica_mods_preferences"
    )
    assert 'prompt=_("About [player]\'s preferences")' in _event_block(
        "maica_wants_preferences_reread"
    )
    assert 'old "About [player]\'s preferences"' in TL_CHAT_SOURCE
    assert 'new "关于[player]的偏好"' in TL_CHAT_SOURCE
    assert "'修改[player]的偏好'" in TL_CHAT_SOURCE
    assert "'调整[player]的爱好'" not in TL_CHAT_SOURCE
    assert 'old "About additional preferences"' not in TL_CHAT_SOURCE
    assert (
        '"maica_wants_preferences_reread",prompt="关于[player]的偏好"'
        in _without_whitespace(TL_DESCRIPTION_SOURCE)
    )


def test_location_action_and_explanation_have_distinct_prompts():
    assert 'prompt=_("Adjust [player]\'s address")' in _event_block(
        "maica_mods_location"
    )
    assert 'prompt=_("About [player]\'s address")' in _event_block(
        "maica_wants_location_reread"
    )
    assert CHAT_SOURCE.count('prompt=_("Adjust [player]\'s address")') == 1
    assert CHAT_SOURCE.count('prompt=_("About [player]\'s address")') == 1
    assert 'old "Adjust [player]\'s address"' in TL_CHAT_SOURCE
    assert 'new "修改[player]的住址"' in TL_CHAT_SOURCE
    assert 'old "About [player]\'s address"' in TL_CHAT_SOURCE
    assert 'new "关于[player]的住址"' in TL_CHAT_SOURCE
    assert 'old "[player]\'s address"' not in TL_CHAT_SOURCE
    assert (
        '"maica_mods_location",prompt="修改[player]的住址"'
        in _without_whitespace(TL_DESCRIPTION_SOURCE)
    )
    assert (
        '"maica_wants_location_reread",prompt="关于[player]的住址"'
        in _without_whitespace(TL_DESCRIPTION_SOURCE)
    )


def test_location_topics_match_the_preferences_topic_roles():
    intro = _label_block("maica_wants_location2")
    modifier = _label_block("maica_mods_location")
    reread = _label_block("maica_wants_location_reread")

    assert '$ mas_unlockEVL("maica_mods_location", "EVE")' in intro
    assert "call maica_set_location" in intro
    assert "jump maica_set_location" in modifier
    assert "maica_set_location" not in reread
    assert "\n    return" in reread
    assert "maica_pre_set_location" not in CHAT_SOURCE
    assert "maica_set_location_reread" not in CHAT_SOURCE
    assert "translate chinese maica_wants_location2_" in TL_CHAT_SOURCE
    assert "translate chinese maica_mods_location_" in TL_CHAT_SOURCE
    assert "translate chinese maica_wants_location_reread_" in TL_CHAT_SOURCE
    assert "translate chinese maica_pre_set_location_" not in TL_CHAT_SOURCE
    assert "translate chinese maica_set_location_reread_" not in TL_CHAT_SOURCE


def test_preference_book_context_uses_the_matching_mas_topics():
    for label in ("maica_wants_preferences2", "maica_wants_preferences_reread"):
        block = _label_block(label)
        assert 'store.seen_event("monika_favbook")' in block
        assert 'store.seen_event("monika_brave_new_world")' not in block
        assert "if persistent._mas_pm_read_yellow_wp else" in block

    assert 'store.seen_event("monika_brave_new_world")' not in TL_CHAT_SOURCE


def test_current_character_file_branch_uses_the_migrated_label():
    corruption = _label_block("maica_chr_corrupted2")
    assert 'renpy.seen_label("maica_chr2")' in corruption
    assert 'renpy.seen_label("maica_chr")' not in corruption
    assert 'renpy.seen_label("maica_chr")' not in TL_CHAT_SOURCE


def test_maica_events_do_not_carry_redundant_bookmark_rules():
    assert "bookmark_rule" not in CHAT_SOURCE


def test_one_shot_and_reread_events_do_not_fall_through_to_other_topics():
    for label in (
        "maica_prepend_reread",
        "maica_chr_reread",
        "maica_wants_location_reread",
        "maica_wants_mpostal",
    ):
        assert "\n    return" in _label_block(label)


def test_chat_migration_repairs_legacy_seen_relationships():
    assert '("1.8.6", migration_1_8_6)' in MIGRATION_SOURCE
    assert '("1.8.7", migration_1_8_7)' in MIGRATION_SOURCE
    assert '("1.8.8", migration_1_8_8)' in MIGRATION_SOURCE
    assert '("1.8.9", migration_1_8_9)' in MIGRATION_SOURCE
    assert '("1.8.10", migration_1_8_10)' in MIGRATION_SOURCE
    assert '("1.8.11", migration_1_8_11)' in MIGRATION_SOURCE
    assert "maica_ver = '1.8.11'" in API_SOURCE
    assert "maica_has_successful_chat()" in MIGRATION_SOURCE
    assert "persistent._maica_successful_chat_count" in MIGRATION_SOURCE
    assert 'getattr(main_ev, "shown_count", 0)' in MIGRATION_SOURCE
    assert 'persistent._seen_ever["maica_end_1"] = True' in MIGRATION_SOURCE
    assert '"maica_chr": "maica_chr2"' in MIGRATION_SOURCE
    assert '"maica_chr_corrupted": "maica_chr_corrupted2"' in MIGRATION_SOURCE
    assert '"maica_wants_preferences": "maica_wants_preferences2"' in MIGRATION_SOURCE
    assert "ev.random = False" in MIGRATION_SOURCE
    assert "ev.action = None" in MIGRATION_SOURCE
    assert "MASGreetingRule.create_rule(skip_visual=True)" in MIGRATION_SOURCE
    assert "MASPriorityRule.create_rule(priority)" in MIGRATION_SOURCE
    assert "mas_rebuildEventLists()" in MIGRATION_SOURCE
    assert 'renpy.seen_label("maica_prepend_2")' in MIGRATION_SOURCE
    assert 'renpy.seen_label("maica_chr_gone")' in MIGRATION_SOURCE
    assert 'renpy.seen_label("maica_chr_corrupted2")' in MIGRATION_SOURCE
    assert '"maica_pre_set_location": "maica_wants_location2"' in MIGRATION_SOURCE
    assert '"maica_set_location_reread": "maica_mods_location"' in MIGRATION_SOURCE
    assert 'mas_unlockEVL("maica_wants_location_reread", "EVE")' in MIGRATION_SOURCE
    assert "persistent.event_database.pop(old_label, None)" in MIGRATION_SOURCE


def test_greeting_retries_until_the_post_door_flow_starts():
    greeting = _registration_block("maica_greeting")
    gone = _event_block("maica_chr_gone")
    label = _label_block("maica_greeting")

    assert "not renpy.seen_label('maica_prepend_2')" in greeting
    assert "not renpy.seen_label('maica_greeting')" not in greeting
    assert "renpy.seen_label('maica_prepend_2')" in gone
    assert "if mas_isplayer_bday():" in label
    assert "jump i_greeting_monikaroom" in label
    assert "call monikaroom_greeting_cleanup" in _label_block("maica_prepend_2")


def test_greeting_lifecycle_matches_mas_closed_room_setup():
    greeting = _label_block("maica_greeting")
    _assert_in_order(
        greeting,
        (
            "$ mas_progressFilter()",
            "$ mas_enable_quit()",
            "$ mas_RaiseShield_core()",
            "scene black",
        ),
    )

    for label_name in ("maica_prepend_2_open", "maica_prepend_2_knock"):
        entrance = _label_block(label_name)
        assert "$ mas_disable_quit()" in entrance
        assert entrance.index("hide monika") < entrance.index("hide black")
        assert entrance.index("$ monika_chr.reset_outfit(False)") < entrance.index(
            "show monika 1esc"
        )


def test_greeting_visual_rules_match_the_scene_each_label_owns():
    intro = _registration_block("maica_greeting")
    corruption = _registration_block("maica_chr_corrupted2")
    mpostal = _registration_block("maica_wants_mpostal")

    assert "skip_visual=True" in intro
    assert "skip_visual=True" in corruption
    assert CHAT_SOURCE.count("skip_visual=True") == 2

    assert 'forced_exp="monika 3hubsa"' in mpostal
    assert "skip_visual=True" not in mpostal
    assert "change_to_heaven_forest" not in _label_block("maica_wants_mpostal")


def test_current_greeting_contract_is_applied_before_mas_selects_one():
    registrations = {
        "maica_greeting": ("greeting_ev", "greeting_conditional", "greeting_rules"),
        "maica_wants_mpostal": (
            "mpostal_ev",
            "mpostal_greeting_conditional",
            "mpostal_greeting_rules",
        ),
        "maica_chr_corrupted2": (
            "corrupted_ev",
            "corrupted_greeting_conditional",
            "corrupted_greeting_rules",
        ),
    }
    for eventlabel, (event_var, conditional_var, rules_var) in registrations.items():
        registration = _registration_block(eventlabel)
        assert 'persistent.greeting_database.get("{}")'.format(eventlabel) in registration
        assert "{}.conditional = {}".format(event_var, conditional_var) in registration
        assert "{}.rules.update({})".format(event_var, rules_var) in registration

    assert 'mpostal_ev = mas_getEV("maica_wants_mpostal")' in MIGRATION_SOURCE
    assert 'MASGreetingRule.create_rule(forced_exp="monika 3hubsa")' in MIGRATION_SOURCE


def test_heaven_forest_round_trip_preserves_the_mas_room_state():
    helper = _label_block("maica_change_to_heaven_forest")
    cleanup = _label_block("clear_all")

    _assert_in_order(
        helper,
        (
            "if initialize_weather:",
            "$ mas_startupWeather()",
            "if maica_room_restore_state is None:",
            "mas_current_background,",
            "mas_current_weather,",
            "mas_weather.force_weather,",
            "store.maica.weather_trigger.can_change,",
            "$ store.maica.weather_trigger.can_change = False",
            "$ mas_changeWeather(weather, new_bg=mas_background_def)",
            "$ bg_change_info = mas_changeBackground(mas_background_def",
            "call spaceroom(",
        ),
    )
    assert "mas_changeWeather(hf_weather, True)" not in CHAT_SOURCE
    assert "mas_changeWeather(hf2_weather, True)" not in CHAT_SOURCE

    _assert_in_order(
        cleanup,
        (
            "if maica_room_restore_state is not None:",
            "$ restore_background, restore_weather, restore_force_weather, restore_weather_trigger = maica_room_restore_state",
            "$ mas_changeWeather(restore_weather, new_bg=restore_background)",
            "$ bg_change_info_moi = mas_changeBackground(restore_background",
            "call spaceroom(",
            "$ mas_weather.force_weather = restore_force_weather",
            "$ store.maica.weather_trigger.can_change = restore_weather_trigger",
            "$ maica_room_restore_state = None",
        ),
    )
    assert "$ store.maica.weather_trigger.can_change = True" not in cleanup


def test_skip_visual_forest_greetings_restore_the_full_startup_lifecycle():
    for label_name in ("maica_prepend_2_open", "maica_prepend_2_knock"):
        assert "change_to_heaven_forest(initialize_weather=True)" in _label_block(
            label_name
        )

    corruption = _label_block("maica_chr_corrupted2")
    assert 'force_exp="monika 1wud"' in corruption
    assert "initialize_weather=True" in corruption
    _assert_in_order(
        corruption,
        (
            "call change_to_heaven_forest_corrupted(",
            "call clear_all",
            "call monikaroom_greeting_cleanup",
            'm 1eua "Welcome back, [player]. What else should we do today?"',
            "return",
        ),
    )
    assert 'return "no_unlock|derandom"' not in corruption
