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
    assert "random=True" in _event_block("maica_chr2")
    assert "random=True" in _event_block("maica_wants_preferences2")
    assert "random=True" in _event_block("maica_pre_set_location")
    assert "random=True" in _event_block("maica_pre_wants_mvista")
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
    assert "maica_get_successful_chat_count() >= 2" in _function_block(
        "mpostal_greeting_select"
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


def test_chat_progression_keeps_special_day_greetings_dynamic():
    greeting = _event_block("maica_greeting")
    mpostal = _event_block("maica_wants_mpostal")

    assert "not mas_isSpecialDay()" in greeting
    assert "not mas_isSpecialDay()" in mpostal
    assert "@store.mas_submod_utils.functionplugin(\"ch30_post_exp_check\"" in CHAT_SOURCE
    assert "if not mas_isSpecialDay()" not in CHAT_SOURCE[: CHAT_SOURCE.index(greeting)]


def test_corruption_greeting_cannot_bypass_the_primary_greeting():
    primary_selector = _function_block("greeting_select")
    corruption_selector = _function_block("corrupted_greeting_select")
    corruption_greeting = _event_block("maica_chr_corrupted2")
    mpostal_selector = _function_block("mpostal_greeting_select")

    assert "not maica_chr_changed" not in primary_selector
    assert 'renpy.seen_label("maica_greeting")' in corruption_selector
    assert "renpy.seen_label('maica_greeting')" in corruption_greeting
    assert (
        'not (maica_chr_changed and not renpy.seen_label("maica_chr_corrupted2"))'
        in mpostal_selector
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
        "maica_prepend_1": "maica_prepend_reread",
        "maica_chr2": "maica_chr_reread",
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

    for reread in source_to_reread.values():
        assert 'eventlabel="{}"'.format(reread) in CHAT_SOURCE


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
    assert "maica_ver = '1.8.8'" in API_SOURCE
    assert "maica_has_successful_chat()" in MIGRATION_SOURCE
    assert "persistent._maica_successful_chat_count" in MIGRATION_SOURCE
    assert 'getattr(main_ev, "shown_count", 0)' in MIGRATION_SOURCE
    assert 'persistent._seen_ever["maica_end_1"] = True' in MIGRATION_SOURCE
    assert '"maica_chr": "maica_chr2"' in MIGRATION_SOURCE
    assert '"maica_chr_corrupted": "maica_chr_corrupted2"' in MIGRATION_SOURCE
    assert '"maica_wants_preferences": "maica_wants_preferences2"' in MIGRATION_SOURCE
