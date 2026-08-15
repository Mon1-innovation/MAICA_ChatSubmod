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
    assert "maica_has_successful_chat()" in _event_block("maica_pre_set_location")


def test_chat_progression_uses_successful_entry_count():
    assert "persistent._maica_successful_chat_count" in CHAT_SOURCE
    for eventlabel in (
        "maica_chr2",
        "maica_wants_preferences2",
        "maica_pre_set_location",
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
    assert "maica_get_successful_chat_count() >= 2" in _event_block(
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
        "maica_prepend_reread",
        "maica_chr_reread",
        "maica_wants_preferences_reread",
        "maica_wants_mspire_reread",
        "maica_wants_mpostal_reread",
        "maica_set_location_reread",
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
        event = _event_block(eventlabel)
        assert "unlocked=True" in event
        assert "persistent._mas_greeting_type is None" in event
        assert "not mas_isSpecialDay()" in event
        assert "action=EV_ACT_UNLOCK" not in event

    assert 'MASPriorityRule.create_rule(0)' in CHAT_SOURCE
    assert CHAT_SOURCE.count('MASPriorityRule.create_rule(20)') == 2
    assert 'functionplugin("ch30_post_exp_check"' not in CHAT_SOURCE
    assert "selected_greeting" not in CHAT_SOURCE

    corruption = _event_block("maica_chr_corrupted2")
    mpostal = _event_block("maica_wants_mpostal")
    assert "renpy.seen_label('maica_greeting')" in corruption
    assert (
        "not (maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2'))"
        in mpostal
    )


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
        "maica_wants_mspire": "maica_wants_mspire_reread",
        "maica_wants_mpostal": "maica_wants_mpostal_reread",
        "maica_pre_set_location": "maica_set_location_reread",
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


def test_preferences_action_and_explanation_have_distinct_prompts():
    assert 'prompt=_("Adjust [player]\'s preferences")' in _event_block(
        "maica_mods_preferences"
    )
    assert 'prompt=_("About [player]\'s preferences")' in _event_block(
        "maica_wants_preferences_reread"
    )
    assert 'old "About [player]\'s preferences"' in TL_CHAT_SOURCE
    assert 'new "关于[player]的偏好"' in TL_CHAT_SOURCE
    assert 'new "了解你的偏好"' in TL_CHAT_SOURCE
    assert 'new "了解你的爱好"' not in TL_CHAT_SOURCE
    assert "'修改[player]的偏好'" in TL_CHAT_SOURCE
    assert "'调整[player]的爱好'" not in TL_CHAT_SOURCE
    assert 'old "About additional preferences"' not in TL_CHAT_SOURCE
    assert (
        'mas_setEVLPropValues("maica_wants_preferences_reread", '
        'prompt="关于[player]的偏好"'
    ) in TL_DESCRIPTION_SOURCE


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
        "maica_wants_mpostal",
    ):
        assert "\n    return" in _label_block(label)


def test_chat_migration_repairs_legacy_seen_relationships():
    assert '("1.8.6", migration_1_8_6)' in MIGRATION_SOURCE
    assert '("1.8.7", migration_1_8_7)' in MIGRATION_SOURCE
    assert '("1.8.8", migration_1_8_8)' in MIGRATION_SOURCE
    assert '("1.8.9", migration_1_8_9)' in MIGRATION_SOURCE
    assert "maica_ver = '1.8.9'" in API_SOURCE
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
