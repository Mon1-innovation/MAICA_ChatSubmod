import textwrap
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
HEADER_SOURCE = (
    Path(__file__).resolve().parents[1]
    / "game"
    / "Submods"
    / "MAICA_ChatSubmod"
    / "header.rpy"
).read_text(encoding="utf-8")
VISTA_SCREEN_SOURCE = (
    Path(__file__).resolve().parents[1]
    / "game"
    / "Submods"
    / "MAICA_ChatSubmod"
    / "screen_subs_vista.rpy"
).read_text(encoding="utf-8")
HEAVEN_FOREST_SOURCE = (
    Path(__file__).resolve().parents[1]
    / "game"
    / "Submods"
    / "MAICA_ChatSubmod"
    / "heaven_forest.rpy"
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

INTERNAL_EVENTLABELS = (
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

DISPATCH_EVENTLABELS = (
    "maica_prepend_1",
    "maica_wants_location2",
    "maica_wants_preferences2",
    "maica_pre_wants_mvista",
    "maica_chr2",
    "maica_chr_gone",
)


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


def test_one_shot_dispatch_events_are_not_random_and_guard_the_event_list():
    for eventlabel in DISPATCH_EVENTLABELS:
        registration = _registration_block(eventlabel)
        assert "random=False" in registration
        assert "not mas_inEVL('{}')".format(eventlabel) in registration

    assert "random=True" not in _registration_block("maica_prepend_1")
    for eventlabel in DISPATCH_EVENTLABELS:
        assert "not mas_inEVL('{}')".format(eventlabel) in MIGRATION_SOURCE


def test_mvista_unlock_is_derived_from_its_intro_seen_state():
    assert "default persistent._maica_vista_enabled" not in API_SOURCE
    assert "persistent._maica_vista_enabled" not in CHAT_SOURCE
    assert "persistent._maica_vista_enabled" not in HEADER_SOURCE
    assert "persistent._maica_vista_enabled" not in VISTA_SCREEN_SOURCE
    assert HEADER_SOURCE.count('maica_topic_ready("mvista")') == 2
    assert 'store.maica_topic_ready("mvista")' in VISTA_SCREEN_SOURCE


def test_internal_events_are_explicitly_locked_out_of_talk_menus():
    for eventlabel in INTERNAL_EVENTLABELS:
        assert "unlocked=False" in _event_block(eventlabel)


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
    assert "maica_topic_main_ready()" in corruption
    assert "renpy.seen_label('maica_prepend_2')" not in corruption
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
        "location": "maica_wants_location_reread",
        "preferences": "maica_wants_preferences_reread",
        "mspire": "maica_wants_mspire_reread",
        "mpostal": "maica_wants_mpostal_reread",
        "mvista": "maica_wants_mvista_reread",
    }
    for source, reread in source_to_reread.items():
        block = _event_block(reread)
        assert "maica_topic_ready('{}')".format(source) in block
        assert "not renpy.seen_label('{}')".format(reread) in block
        assert "action=EV_ACT_UNLOCK" in block

    heaven = _event_block("maica_prepend_reread")
    assert "maica_topic_main_ready()" in heaven
    assert "renpy.seen_label('maica_prepend_2')" not in heaven

    chr_reread = _event_block("maica_chr_reread")
    assert "maica_topic_ready('character')" in chr_reread
    for source in ("maica_chr2", "maica_chr_gone", "maica_chr_corrupted2"):
        assert "renpy.seen_label('{}')".format(source) not in chr_reread
    assert "not renpy.seen_label('maica_chr_reread')" in chr_reread
    assert "action=EV_ACT_UNLOCK" in chr_reread

    for reread in tuple(source_to_reread.values()) + (
            "maica_prepend_reread", "maica_chr_reread"):
        assert 'eventlabel="{}"'.format(reread) in CHAT_SOURCE


def test_mpostal_conditional_attribute_is_looked_up_by_name():
    assert CHAT_SOURCE.count('maica_topic_ready("mpostal")') == 3
    assert 'getattr(mas_getEV("maica_wants_mpostal"), "conditional", False)' not in CHAT_SOURCE


def test_mspire_choices_and_dispatch_respect_the_registered_state():
    intro = _label_block("maica_wants_mspire")
    assert 'persistent.maica_setting_dict["mspire_enable"] = True' in intro
    assert 'persistent.maica_setting_dict["mspire_enable"] = False' in intro
    assert "mas_isMoniNormal(higher=True)" in _function_block("push_mspire_want")
    assert "mas_isMoniNormal(higher=True)" in _function_block("push_mspire")


def test_internal_events_do_not_define_user_facing_prompts():
    for eventlabel in INTERNAL_EVENTLABELS:
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
    assert '("1.8.12", migration_1_8_12)' in MIGRATION_SOURCE
    assert '("1.8.13", migration_1_8_13)' in MIGRATION_SOURCE
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
    assert '("1.8.17", migration_1_8_17)' in MIGRATION_SOURCE


def test_v1817_migration_and_startup_share_the_complete_topic_reconciler():
    assert 'def maica_reconcile_topic_state(reason="startup", repair_contracts=False):' in MIGRATION_SOURCE
    assert 'reason="migration_1_8_17"' in MIGRATION_SOURCE
    assert 'maica_reconcile_topic_state(reason="startup")' in API_SOURCE
    assert "_MAICA_SOURCE_DEFINITIONS" in MIGRATION_SOURCE
    assert "_maica_topic_contract_specs" in MIGRATION_SOURCE
    assert '("maica_main", "main_ready", "main_evidence"' in MIGRATION_SOURCE
    assert '("maica_prepend_reread", "heaven_reread_ready", "heaven_reread_evidence"' in MIGRATION_SOURCE
    assert '("maica_wants_location_reread", "location_seen", "location_evidence"' in MIGRATION_SOURCE
    assert '("maica_chr_reread", "character_seen", "character_evidence"' in MIGRATION_SOURCE
    assert 'fields["clear_unlock_date"] = not expected' in MIGRATION_SOURCE
    assert "legacy_changed" in MIGRATION_SOURCE
    assert "maica_topic_ready" in MIGRATION_SOURCE
    assert "topic state corrected" in MIGRATION_SOURCE
    assert "topic state check" in MIGRATION_SOURCE
    assert '"maica_pre_set_location"' in MIGRATION_SOURCE
    assert '"maica_set_location_reread"' in MIGRATION_SOURCE
    assert '"maica_chr_corrupted"' in MIGRATION_SOURCE


def _load_topic_reconciler(
        events,
        seen=(),
        seen_ever=(),
        successful_count=0,
        aggregate=None,
        db_map=None,
    ):
    start = MIGRATION_SOURCE.index("    _MAICA_UNSET = object()")
    end = MIGRATION_SOURCE.index("\n    def migration_1_8_0()", start)
    source = textwrap.dedent(MIGRATION_SOURCE[start:end])

    class PersistentStub(object):
        def __init__(self):
            self._seen_ever = dict.fromkeys(seen_ever, True)
            self._maica_vista_enabled = False
            self.event_database = {}

    class RenpyStub(object):
        def __init__(self):
            self.seen = set(seen)

        def seen_label(self, eventlabel):
            return eventlabel in self.seen

    class LoggerStub(object):
        def __init__(self):
            self.messages = []

        def debug(self, message):
            self.messages.append(("debug", message))

        def info(self, message):
            self.messages.append(("info", message))

        def warning(self, message):
            self.messages.append(("warning", message))

    class GreetingRuleStub(object):
        @staticmethod
        def create_rule(**kwargs):
            return kwargs

    class PriorityRuleStub(object):
        @staticmethod
        def create_rule(priority):
            return {"priority": priority}

    persistent = PersistentStub()
    renpy = RenpyStub()
    logger = LoggerStub()
    store = type(
        "StoreStub",
        (),
        {
            "mas_submod_utils": type(
                "SubmodUtilsStub",
                (),
                {"submod_log": logger},
            )(),
            "evhand": type("EventHandlerStub", (), {"event_database": {}})(),
        },
    )()
    rebuild_calls = []
    def get_event(eventlabel):
        if aggregate is not None:
            return aggregate.get(eventlabel, events.get(eventlabel))
        return events.get(eventlabel)

    namespace = {
        "mas_getEV": get_event,
        "mas_rebuildEventLists": lambda: rebuild_calls.append(True),
        "maica_has_successful_chat": lambda: successful_count > 0,
        "maica_get_successful_chat_count": lambda: successful_count,
        "persistent": persistent,
        "renpy": renpy,
        "store": store,
        "MASGreetingRule": GreetingRuleStub,
        "MASPriorityRule": PriorityRuleStub,
        "maica_chr_exist": True,
        "maica_chr_changed": False,
    }
    if aggregate is not None:
        namespace["mas_all_ev_db"] = aggregate
    if db_map is not None:
        namespace["mas_all_ev_db_map"] = db_map
    exec(source, namespace)
    return namespace, persistent, renpy, logger, rebuild_calls


def test_dispatch_contracts_block_repeat_actions_after_startup_repair():
    class EventStub(object):
        def __init__(self):
            self.unlocked = True
            self.shown_count = 0
            self.unlock_date = "legacy"
            self.pool = True
            self.random = True
            self.conditional = "legacy"
            self.action = "legacy"
            self.rules = {}

    events = {eventlabel: EventStub() for eventlabel in DISPATCH_EVENTLABELS}
    namespace, persistent, renpy, _, _ = _load_topic_reconciler(events)

    namespace["maica_reconcile_topic_state"](reason="dispatch-runtime")
    persistent.event_list = []

    def in_event_list(eventlabel):
        return any(
            (item[0] if isinstance(item, (tuple, list)) else item) == eventlabel
            for item in persistent.event_list
        )

    runtime_globals = dict(namespace)
    runtime_globals.update({
        "maica_topic_main_ready": lambda: True,
        "maica_has_successful_chat": lambda: True,
        "maica_get_successful_chat_count": lambda: 10,
        "maica_chr_exist": False,
        "mas_inEVL": in_event_list,
        "renpy": renpy,
    })

    # MAS random selection does not consult a conditional or action. None of
    # these one-shot dispatchers may therefore remain a random candidate.
    assert [
        eventlabel
        for eventlabel, event in events.items()
        if event.random
    ] == []

    for eventlabel in DISPATCH_EVENTLABELS:
        event = events[eventlabel]
        assert eval(event.conditional, runtime_globals) is True

        if event.action == "queue":
            persistent.event_list.insert(0, (eventlabel, False, None))
        else:
            assert event.action == "push"
            persistent.event_list.append((eventlabel, False, None))

        # On a later startup the reconciler restores action/conditional. The
        # EVL guard must still prevent MAS from dispatching a second copy.
        assert eval(event.conditional, runtime_globals) is False
        persistent.event_list[:] = []


def test_dispatch_queue_cleanup_preserves_interrupted_event_and_drops_completed_entries():
    class EventStub(object):
        def __init__(self, shown_count=0):
            self.unlocked = False
            self.shown_count = shown_count
            self.unlock_date = None
            self.pool = False
            self.random = False
            self.conditional = None
            self.action = None
            self.rules = {}

    events = {eventlabel: EventStub() for eventlabel in DISPATCH_EVENTLABELS}
    events["maica_wants_preferences2"].shown_count = 1
    namespace, persistent, _, logger, _ = _load_topic_reconciler(
        events,
        seen=("maica_prepend_1", "maica_wants_preferences2"),
    )
    persistent.current_monikatopic = "maica_prepend_1"
    persistent.event_list = [
        ("maica_prepend_1", False, "older-copy"),
        ("keep", False, None),
        ["maica_prepend_1", False, "restart-copy"],
        "maica_wants_preferences2",
        ("continue_event", False, None),
    ]

    result = namespace["maica_reconcile_topic_state"](reason="queue-cleanup")

    # seen_label alone is not completion evidence: a label becomes seen as soon
    # as it starts. Keep the highest-priority copy while shown_count is zero.
    assert persistent.event_list == [
        ("keep", False, None),
        ["maica_prepend_1", False, "restart-copy"],
        ("continue_event", False, None),
    ]
    assert persistent.current_monikatopic == "maica_prepend_1"
    assert result["queue_changed"] is True
    assert result["queue_removed"] == 2
    assert any(
        level == "warning" and "dispatch queue normalized" in message
        for level, message in logger.messages
    )


def test_dispatch_diagnostics_include_scheduler_state_and_survive_bad_condition():
    class EventStub(object):
        def __init__(self, eventlabel):
            self.eventlabel = eventlabel
            self.unlocked = False
            self.shown_count = 0
            self.unlock_date = None
            self.pool = False
            self.random = False
            self.conditional = "True"
            self.action = "queue"
            self.rules = {}

        def checkConditional(self):
            if self.eventlabel == "maica_chr2":
                raise ValueError("bad condition")
            return True

        def checkAffection(self, affection):
            return affection == 42

    events = {
        eventlabel: EventStub(eventlabel)
        for eventlabel in DISPATCH_EVENTLABELS
    }
    namespace, persistent, renpy, logger, _ = _load_topic_reconciler(
        events,
        successful_count=4,
    )
    renpy.has_label = lambda unused_label: True
    persistent.event_list = [("maica_prepend_1", False, None)]
    persistent.current_monikatopic = "maica_chr2"
    namespace["store"].mas_globals = type(
        "GlobalsStub",
        (),
        {"in_idle_mode": False, "event_unpause_dt": "pause-marker"},
    )()
    namespace["mas_curr_affection"] = 42

    namespace["_maica_log_dispatch_diagnostics"]("diagnostic-test")

    info_messages = [
        message for level, message in logger.messages if level == "info"
    ]
    debug_messages = [
        message for level, message in logger.messages if level == "debug"
    ]
    assert any(
        "queue_total=1" in message
        and "pause_until='pause-marker'" in message
        and "affection=42" in message
        and "successful_chats=4" in message
        for message in info_messages
    )
    assert len(debug_messages) == len(DISPATCH_EVENTLABELS)
    for field in (
            "seen_label=", "seen_ever=", "shown_count=", "unlocked=",
            "random=", "pool=", "action=", "conditional=",
            "condition_result=", "affection_ok=", "queue_positions=",
            "current=",
        ):
        assert all(field in message for message in debug_messages)
    assert any(
        "label=maica_chr2" in message
        and "error:ValueError:bad condition" in message
        for message in debug_messages
    )


def test_topic_reconciler_enforces_one_way_gate_and_restores_later_progression():
    class EventStub(object):
        def __init__(self):
            self.unlocked = True
            self.shown_count = 0
            self.unlock_date = "legacy"
            self.pool = True
            self.random = True
            self.conditional = "legacy"
            self.action = "legacy"
            self.rules = {}

    labels = (
        "maica_prepend_1", "maica_greeting", "maica_main",
        "maica_wants_location2", "maica_mods_location",
        "maica_wants_preferences2", "maica_mods_preferences",
        "maica_wants_mspire", "maica_wants_mpostal",
        "maica_pre_wants_mvista", "maica_chr_corrupted2",
        "maica_chr_gone", "maica_chr2", "maica_mspire",
        "maica_mpostal_received", "maica_mpostal_replyed",
        "maica_prepend_reread", "maica_wants_location_reread",
        "maica_wants_preferences_reread", "maica_wants_mspire_reread",
        "maica_wants_mpostal_reread", "maica_wants_mvista_reread",
        "maica_chr_reread",
    )
    events = {label: EventStub() for label in labels}
    namespace, _, renpy, logger, rebuild_calls = _load_topic_reconciler(events)

    result = namespace["maica_reconcile_topic_state"](reason="test")

    assert events["maica_main"].unlocked is False
    assert events["maica_wants_location_reread"].unlocked is False
    assert events["maica_chr_reread"].unlocked is False
    assert events["maica_prepend_reread"].unlocked is False
    assert events["maica_greeting"].unlocked is True
    assert result["progress"]["main_evidence"] == "not-seen"
    assert result["changed"] is True
    assert any(level == "warning" for level, _ in logger.messages)

    # Downstream history is retained as evidence, but it cannot promote the
    # main gate or any child unlock while the Heaven Forest flow is absent.
    renpy.seen.update(("maica_wants_location2", "maica_chr2"))
    result = namespace["maica_reconcile_topic_state"](reason="test-later")

    assert events["maica_main"].unlocked is False
    assert events["maica_prepend_reread"].unlocked is False
    assert events["maica_mods_location"].unlocked is False
    assert events["maica_wants_location_reread"].unlocked is False
    assert events["maica_chr_reread"].unlocked is False
    assert result["progress"]["main_evidence"] == "not-seen"
    assert result["progress"]["location_evidence"].startswith("blocked-by:main")
    assert result["progress"]["character_evidence"].startswith("blocked-by:main")
    assert any("evidence=" in message for level, message in logger.messages if level == "info")
    assert rebuild_calls

    # Once the main history appears, the earlier source evidence can restore
    # the children. The Heaven Forest reread follows the main gate even when
    # its own intro label is absent from the old save.
    renpy.seen.add("maica_main")
    result = namespace["maica_reconcile_topic_state"](reason="test-main-only")
    assert events["maica_main"].unlocked is True
    assert events["maica_prepend_reread"].unlocked is True
    assert events["maica_mods_location"].unlocked is True
    assert events["maica_wants_location_reread"].unlocked is True
    assert events["maica_chr_reread"].unlocked is True
    assert result["progress"]["heaven_reread_evidence"].startswith("implied-by:maica_main")

    rebuild_count = len(rebuild_calls)
    repeat = namespace["maica_reconcile_topic_state"](reason="test-repeat")
    assert repeat["changed"] is False
    assert len(rebuild_calls) == rebuild_count


def test_topic_reconciler_does_not_use_stale_main_unlock_as_evidence():
    class EventStub(object):
        def __init__(self):
            self.unlocked = True
            self.shown_count = 0
            self.unlock_date = "legacy"
            self.pool = True
            self.random = True
            self.conditional = "legacy"
            self.action = "legacy"
            self.rules = {}

    labels = (
        "maica_prepend_1", "maica_greeting", "maica_main",
        "maica_wants_location2", "maica_mods_location",
        "maica_wants_preferences2", "maica_mods_preferences",
        "maica_wants_mspire", "maica_wants_mpostal",
        "maica_pre_wants_mvista", "maica_chr_corrupted2",
        "maica_chr_gone", "maica_chr2", "maica_mspire",
        "maica_mpostal_received", "maica_mpostal_replyed",
        "maica_prepend_reread", "maica_wants_location_reread",
        "maica_wants_preferences_reread", "maica_wants_mspire_reread",
        "maica_wants_mpostal_reread", "maica_wants_mvista_reread",
        "maica_chr_reread",
    )
    events = {label: EventStub() for label in labels}
    namespace, _, _, _, _ = _load_topic_reconciler(events)

    result = namespace["maica_reconcile_topic_state"](reason="stale-main")

    assert result["progress"]["main_evidence"] == "not-seen"
    assert events["maica_main"].unlocked is False
    assert events["maica_prepend_reread"].unlocked is False


def test_topic_progress_reads_legacy_tuple_shown_count_as_source_evidence():
    class EventStub(object):
        def __init__(self):
            self.unlocked = False
            self.shown_count = 0
            self.unlock_date = None
            self.pool = False
            self.random = False
            self.conditional = None
            self.action = None
            self.rules = {}

    labels = (
        "maica_prepend_1", "maica_greeting", "maica_main",
        "maica_wants_location2", "maica_mods_location",
        "maica_wants_preferences2", "maica_mods_preferences",
        "maica_wants_mspire", "maica_wants_mpostal",
        "maica_pre_wants_mvista", "maica_chr_corrupted2",
        "maica_chr_gone", "maica_chr2", "maica_mspire",
        "maica_mpostal_received", "maica_mpostal_replyed",
        "maica_prepend_reread", "maica_wants_location_reread",
        "maica_wants_preferences_reread", "maica_wants_mspire_reread",
        "maica_wants_mpostal_reread", "maica_wants_mvista_reread",
        "maica_chr_reread",
    )
    events = {label: EventStub() for label in labels}
    # MAS persistent Event rows store shown_count at tuple index 12.
    legacy_row = [None] * 13
    legacy_row[0] = "maica_pre_set_location"
    legacy_row[12] = 1
    events["maica_pre_set_location"] = legacy_row
    namespace, persistent, _, _, _ = _load_topic_reconciler(
        events,
        seen=("maica_prepend_2",),
    )

    progress = namespace["maica_get_topic_progress"]()

    assert progress["main_ready"] is True
    assert progress["location_seen"] is True
    assert progress["location_evidence"] == "shown_count:maica_pre_set_location"
    assert persistent._seen_ever["maica_wants_location2"] is True


def test_v1817_migration_cleans_legacy_records_and_rebuilds_once():
    class EventStub(object):
        def __init__(self, shown_count=0):
            self.unlocked = True
            self.shown_count = shown_count
            self.unlock_date = "legacy"
            self.pool = True
            self.random = True
            self.conditional = "legacy"
            self.action = "legacy"
            self.rules = {}

    labels = (
        "maica_prepend_1", "maica_greeting", "maica_main",
        "maica_wants_location2", "maica_mods_location",
        "maica_wants_preferences2", "maica_mods_preferences",
        "maica_wants_mspire", "maica_wants_mpostal",
        "maica_pre_wants_mvista", "maica_chr_corrupted2",
        "maica_chr_gone", "maica_chr2", "maica_mspire",
        "maica_mpostal_received", "maica_mpostal_replyed",
        "maica_prepend_reread", "maica_wants_location_reread",
        "maica_wants_preferences_reread", "maica_wants_mspire_reread",
        "maica_wants_mpostal_reread", "maica_wants_mvista_reread",
        "maica_chr_reread",
    )
    events = {label: EventStub() for label in labels}
    namespace, persistent, _, _, rebuild_calls = _load_topic_reconciler(
        events,
        seen=("maica_prepend_2",),
    )
    legacy_event = EventStub(shown_count=1)
    persistent.event_database["maica_pre_set_location"] = legacy_event
    namespace["store"].evhand.event_database["maica_chr"] = EventStub(shown_count=1)

    namespace["migration_1_8_17"]()

    assert "maica_pre_set_location" not in persistent.event_database
    assert "maica_chr" not in namespace["store"].evhand.event_database
    assert persistent._seen_ever["maica_wants_location2"] is True
    assert persistent._seen_ever["maica_chr2"] is True
    assert events["maica_mods_location"].unlocked is True
    assert events["maica_chr_reread"].unlocked is True
    assert len(rebuild_calls) == 1


def test_v1817_cleanup_refreshes_mas_aggregate_after_eve_label_removal():
    class EventStub(object):
        def __init__(self, shown_count=0):
            self.unlocked = True
            self.shown_count = shown_count
            self.unlock_date = "legacy"
            self.pool = True
            self.random = True
            self.conditional = "legacy"
            self.action = "legacy"
            self.rules = {}

    labels = (
        "maica_prepend_1", "maica_greeting", "maica_main",
        "maica_wants_location2", "maica_mods_location",
        "maica_wants_preferences2", "maica_mods_preferences",
        "maica_wants_mspire", "maica_wants_mpostal",
        "maica_pre_wants_mvista", "maica_chr_corrupted2",
        "maica_chr_gone", "maica_chr2", "maica_mspire",
        "maica_mpostal_received", "maica_mpostal_replyed",
        "maica_prepend_reread", "maica_wants_location_reread",
        "maica_wants_preferences_reread", "maica_wants_mspire_reread",
        "maica_wants_mpostal_reread", "maica_wants_mvista_reread",
        "maica_chr_reread",
    )
    events = {label: EventStub() for label in labels}
    aggregate = dict(events)
    db_map = {"EVE": {}, "GRE": {}}
    namespace, persistent, _, logger, rebuild_calls = _load_topic_reconciler(
        events,
        seen=("maica_prepend_2",),
        aggregate=aggregate,
        db_map=db_map,
    )

    eve_db = namespace["store"].evhand.event_database
    db_map["EVE"] = eve_db
    old_location = EventStub(shown_count=1)
    old_eve_corrupted = EventStub(shown_count=1)
    current_greeting = EventStub()
    persistent.event_database["maica_pre_set_location"] = old_location
    eve_db["maica_pre_set_location"] = old_location
    eve_db["maica_chr_corrupted2"] = old_eve_corrupted
    db_map["GRE"]["maica_chr_corrupted2"] = current_greeting
    aggregate["maica_pre_set_location"] = old_location
    aggregate["maica_chr_corrupted2"] = old_eve_corrupted

    namespace["migration_1_8_17"]()

    assert "maica_pre_set_location" not in aggregate
    assert aggregate["maica_chr_corrupted2"] is current_greeting
    assert "maica_pre_set_location" not in eve_db
    assert "maica_chr_corrupted2" not in eve_db
    assert len(rebuild_calls) == 1
    assert any(
        level == "info" and "legacy topic records normalized" in message
        for level, message in logger.messages
    )

    # A second audit must not read a detached Event left in the old snapshot.
    result = namespace["maica_reconcile_topic_state"](reason="aggregate-repeat")
    assert result["changed"] is False


def test_v1817_cleanup_migrates_legacy_queue_and_topic_references():
    class EventStub(object):
        def __init__(self):
            self.unlocked = False
            self.shown_count = 0
            self.unlock_date = None
            self.pool = False
            self.random = False
            self.conditional = None
            self.action = None
            self.rules = {}

    labels = (
        "maica_prepend_1", "maica_greeting", "maica_main",
        "maica_wants_location2", "maica_mods_location",
        "maica_wants_preferences2", "maica_mods_preferences",
        "maica_wants_mspire", "maica_wants_mpostal",
        "maica_pre_wants_mvista", "maica_chr_corrupted2",
        "maica_chr_gone", "maica_chr2", "maica_mspire",
        "maica_mpostal_received", "maica_mpostal_replyed",
        "maica_prepend_reread", "maica_wants_location_reread",
        "maica_wants_preferences_reread", "maica_wants_mspire_reread",
        "maica_wants_mpostal_reread", "maica_wants_mvista_reread",
        "maica_chr_reread",
    )
    events = {label: EventStub() for label in labels}
    namespace, persistent, _, _, _ = _load_topic_reconciler(
        events,
        seen=("maica_prepend_2",),
    )
    persistent.event_list = [
        ("maica_pre_set_location", False, None),
        "maica_chr",
        ("keep", False, None),
    ]
    persistent._mas_player_bookmarked = ["maica_set_location_reread", "keep"]
    persistent._mas_player_derandomed = ["maica_wants_preferences", "keep"]
    persistent.flagged_monikatopic = "maica_chr"

    namespace["migration_1_8_17"]()

    assert persistent.event_list == [
        ("maica_wants_location2", False, None),
        "maica_chr2",
        ("keep", False, None),
    ]
    assert persistent._mas_player_bookmarked == ["maica_mods_location", "keep"]
    assert persistent._mas_player_derandomed == ["maica_wants_preferences2", "keep"]
    assert persistent.flagged_monikatopic == "maica_chr2"


def test_latest_migration_repairs_internal_and_mvista_reread_state():
    start = MIGRATION_SOURCE.index("    def migration_1_8_12():")
    end = MIGRATION_SOURCE.index("\n    migration_queue =", start)
    migration = MIGRATION_SOURCE[start:end]

    for eventlabel in INTERNAL_EVENTLABELS:
        assert '"{}"'.format(eventlabel) in migration

    assert "ev.unlocked = False" in migration
    assert "ev.unlock_date = None" in migration
    assert "ev.pool = False" in migration
    assert 'mvista_ev = mas_getEV("maica_pre_wants_mvista")' in migration
    assert (
        'mvista_reread_ev = mas_getEV("maica_wants_mvista_reread")'
        in migration
    )
    assert 'renpy.seen_label("maica_pre_wants_mvista")' in migration
    assert 'renpy.seen_label("maica_wants_mvista_reread")' in migration
    assert "mvista_reread_ev.unlocked = (" in migration
    assert "mas_rebuildEventLists()" in migration


def test_latest_migration_repairs_persistent_event_objects_at_runtime():
    start = MIGRATION_SOURCE.index("    def migration_1_8_12():")
    end = MIGRATION_SOURCE.index("\n    migration_queue =", start)
    migration = textwrap.dedent(MIGRATION_SOURCE[start:end])

    class EventStub(object):
        def __init__(self, shown_count=0):
            self.shown_count = shown_count
            self.unlocked = True
            self.unlock_date = "legacy"
            self.pool = True

    class RenpyStub(object):
        def __init__(self):
            self.seen = set()

        def seen_label(self, eventlabel):
            return eventlabel in self.seen

    events = {
        eventlabel: EventStub()
        for eventlabel in INTERNAL_EVENTLABELS
    }
    events["maica_pre_wants_mvista"].shown_count = 1
    events["maica_wants_mvista_reread"] = EventStub()
    renpy = RenpyStub()
    rebuild_calls = []
    namespace = {
        "mas_getEV": events.get,
        "mas_rebuildEventLists": lambda: rebuild_calls.append(True),
        "renpy": renpy,
    }
    exec(migration, namespace)

    migrate = namespace["migration_1_8_12"]
    migrate()

    for eventlabel in INTERNAL_EVENTLABELS:
        event = events[eventlabel]
        assert event.unlocked is False
        assert event.unlock_date is None
        assert event.pool is False
    assert events["maica_wants_mvista_reread"].unlocked is True

    events["maica_pre_wants_mvista"].shown_count = 0
    events["maica_wants_mvista_reread"].shown_count = 0
    migrate()
    assert events["maica_wants_mvista_reread"].unlocked is False

    renpy.seen.add("maica_pre_wants_mvista")
    migrate()
    assert events["maica_wants_mvista_reread"].unlocked is True
    assert len(rebuild_calls) == 3


def test_mvista_seen_migration_preserves_legacy_unlock_state():
    start = MIGRATION_SOURCE.index("    def migration_1_8_13():")
    end = MIGRATION_SOURCE.index("\n    migration_queue =", start)
    migration = textwrap.dedent(MIGRATION_SOURCE[start:end])

    class EventStub(object):
        def __init__(self, shown_count=0):
            self.shown_count = shown_count
            self.unlocked = False

    class PersistentStub(object):
        def __init__(self):
            self._maica_vista_enabled = True
            self._seen_ever = {}

    class RenpyStub(object):
        def __init__(self):
            self.seen = set()

        def seen_label(self, eventlabel):
            return eventlabel in self.seen

    events = {
        "maica_pre_wants_mvista": EventStub(),
        "maica_wants_mvista_reread": EventStub(),
    }
    persistent = PersistentStub()
    rebuild_calls = []
    namespace = {
        "mas_getEV": events.get,
        "mas_rebuildEventLists": lambda: rebuild_calls.append(True),
        "persistent": persistent,
        "renpy": RenpyStub(),
    }
    exec(migration, namespace)

    namespace["migration_1_8_13"]()

    assert persistent._seen_ever["maica_pre_wants_mvista"] is True
    assert events["maica_wants_mvista_reread"].unlocked is True
    assert rebuild_calls == [True]


def test_greeting_retries_until_the_post_door_flow_starts():
    greeting = _registration_block("maica_greeting")
    gone = _event_block("maica_chr_gone")
    label = _label_block("maica_greeting")

    assert "not renpy.seen_label('maica_prepend_2')" in greeting
    assert "not renpy.seen_label('maica_greeting')" not in greeting
    assert "maica_topic_main_ready()" in gone
    assert "renpy.seen_label('maica_prepend_2')" not in gone
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
        assert 'evhand.greeting_database.get("{}")'.format(eventlabel) in registration
        assert 'persistent.greeting_database.get("{}")'.format(eventlabel) not in registration
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


def test_heaven_forest_animation_setting_controls_the_weather_mask():
    assert 'img_tag="hf_weather_fb"' in HEAVEN_FOREST_SOURCE
    assert '"hf_weather"\n            if persistent.maica_setting_dict.get(' in HEAVEN_FOREST_SOURCE
    assert '"use_anim_background", True)\n            else None' in HEAVEN_FOREST_SOURCE


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
