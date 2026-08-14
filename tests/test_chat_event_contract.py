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


def _event_block(eventlabel):
    marker = 'eventlabel="{}"'.format(eventlabel)
    start = CHAT_SOURCE.index(marker)
    end = CHAT_SOURCE.find("\ninit ", start + len(marker))
    return CHAT_SOURCE[start:] if end == -1 else CHAT_SOURCE[start:end]


def _function_block(function_name):
    marker = "    def {}():".format(function_name)
    start = CHAT_SOURCE.index(marker)
    end = CHAT_SOURCE.find("\n    def ", start + len(marker))
    return CHAT_SOURCE[start:] if end == -1 else CHAT_SOURCE[start:end]


def _label_block(label):
    marker = "label {}:".format(label)
    start = CHAT_SOURCE.index(marker)
    end = CHAT_SOURCE.find("\nlabel ", start + len(marker))
    return CHAT_SOURCE[start:] if end == -1 else CHAT_SOURCE[start:end]


def test_chat_progression_uses_main_shown_count_without_persistent_counter():
    assert "persistent.maica_chat_success_count" not in CHAT_SOURCE
    assert "random=True" in _event_block("maica_chr2")
    assert "random=True" in _event_block("maica_wants_preferences2")
    assert "random=True" in _event_block("maica_pre_set_location")
    assert "random=True" in _event_block("maica_pre_wants_mvista")
    assert "mas_getEV('maica_main').shown_count >= 1" in _event_block(
        "maica_wants_preferences2"
    )
    assert "mas_getEV('maica_main').shown_count >= 2" in _event_block(
        "maica_pre_wants_mvista"
    )
    assert "mas_getEV('maica_main').shown_count >= 3" in _event_block(
        "maica_chr2"
    )


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
    assert 'persistent._seen_ever["maica_end_1"] = True' in MIGRATION_SOURCE
    assert '"maica_chr": "maica_chr2"' in MIGRATION_SOURCE
    assert '"maica_chr_corrupted": "maica_chr_corrupted2"' in MIGRATION_SOURCE
    assert '"maica_wants_preferences": "maica_wants_preferences2"' in MIGRATION_SOURCE
