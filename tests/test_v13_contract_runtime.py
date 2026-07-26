import json
import logging
import math
import sys
import urllib.request
from pathlib import Path

import pytest


PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "game" / "python-packages"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

import emotion_analyze_v2
import logger_manager
import maica
import maica_mtrigger
import maica_tasker
import maica_tasker_sub
import maica_tasker_sub_sessionsender
import maica_vista_files_manager


class NullLogger:
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


class WsClientStub:
    def __init__(self):
        self.sent = []

    def send(self, payload):
        self.sent.append(payload)


class ManagerStub:
    def __init__(self):
        self.ws_client = WsClientStub()
        self.events = []
        self.closed = False

    def register_task(self, task):
        self.events.append(("registered", task))

    def create_event(self, event):
        self.events.append(event)

    def close_ws(self):
        self.closed = True


class EventStub:
    def __init__(self, status, content=""):
        self.data = type("Packet", (), {"status": status, "content": content})()


def _build_trigger(template, name="trigger", exprop=None, description=""):
    if exprop is None:
        exprop = maica_mtrigger.MTriggerExprop(item_name_zh="项目")
    return maica_mtrigger.MTriggerBase(
        template,
        name,
        description=description,
        exprop=exprop,
    )


def _build_exprop(template):
    if template is maica_mtrigger.common_affection_template:
        return maica_mtrigger.MTriggerExprop()
    if template is maica_mtrigger.common_switch_template:
        return maica_mtrigger.MTriggerExprop(
            item_name_zh="项目", item_list=["item"], curr_value="item"
        )
    return maica_mtrigger.MTriggerExprop(item_name_zh="项目")


def _build_trigger_batch(template, count):
    manager = maica_mtrigger.MTriggerManager()
    for index in range(count):
        manager.add_trigger(
            _build_trigger(
                template,
                name="trigger_{}".format(index),
                exprop=_build_exprop(template),
            )
        )
    return manager.build_data(full=True)


def _last_json(manager):
    assert manager.ws_client.sent
    return json.loads(manager.ws_client.sent[-1])


def _new_validator(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    manager = ManagerStub()
    validator = maica_tasker_sub.StreamingPacketValidator(
        task_type=1,
        name="streaming_packet_validator",
        manager=manager,
        except_ws_status=[
            "maica_core_streaming_continue",
            "maica_core_complete",
        ],
    )
    return validator


def _send_streaming_packets(validator, count):
    for _index in range(count):
        validator.on_received(EventStub("maica_core_streaming_continue"))


def _copy_injected_references(registry):
    return {
        name: dict(reference) if isinstance(reference, dict) else reference
        for name, reference in registry.items()
    }


def _assert_injected_references_equal(actual, expected):
    assert list(actual) == list(expected)
    for name, expected_reference in expected.items():
        actual_reference = actual[name]
        if isinstance(expected_reference, dict):
            assert set(actual_reference) == set(expected_reference)
            for key, expected_value in expected_reference.items():
                assert actual_reference[key] is expected_value
        else:
            assert actual_reference is expected_reference


@pytest.fixture
def isolated_maica_ai_globals():
    console_logger = logging.getLogger("mas_console_logger")
    handlers_before = list(console_logger.handlers)
    level_before = console_logger.level
    propagate_before = console_logger.propagate
    disabled_before = console_logger.disabled
    mtrigger_logger_before = maica_mtrigger.logger
    manager_before = logger_manager.get_logger_manager()
    assert maica._logger_manager is manager_before
    injected_before = _copy_injected_references(
        manager_before._injected_references
    )

    yield

    for handler in list(console_logger.handlers):
        if handler not in handlers_before:
            console_logger.removeHandler(handler)
            handler.close()
    for handler in handlers_before:
        if handler not in console_logger.handlers:
            console_logger.addHandler(handler)
    console_logger.setLevel(level_before)
    console_logger.propagate = propagate_before
    console_logger.disabled = disabled_before
    maica_mtrigger.logger = mtrigger_logger_before

    registry = manager_before._injected_references
    for name in list(registry):
        if name not in injected_before:
            del registry[name]
    for name, reference in injected_before.items():
        registry[name] = dict(reference) if isinstance(reference, dict) else reference

    assert list(console_logger.handlers) == handlers_before
    assert console_logger.level == level_before
    assert console_logger.propagate is propagate_before
    assert console_logger.disabled is disabled_before
    assert maica_mtrigger.logger is mtrigger_logger_before
    assert logger_manager.get_logger_manager() is manager_before
    assert maica._logger_manager is manager_before
    _assert_injected_references_equal(registry, injected_before)


def _raw_messages_with_compact_size(target_size):
    empty_query = [{"role": "user", "content": ""}]
    overhead = len(
        json.dumps(empty_query, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
    )
    assert target_size >= overhead
    content_size = target_size - overhead
    content = "好" * (content_size // 3) + "x" * (content_size % 3)
    query = [{"role": "user", "content": content}]
    actual_size = len(
        json.dumps(query, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )
    assert actual_size == target_size
    return query


def test_common_switch_template_uses_choice_datakey():
    assert maica_mtrigger.common_switch_template.datakey == "choice"


def test_common_affection_template_uses_alter_value_and_accepts_legacy_input():
    received = []
    trigger = maica_mtrigger.MTriggerBase(
        maica_mtrigger.common_affection_template,
        "affection",
        callback=received.append,
    )

    assert maica_mtrigger.common_affection_template.datakey == "alter_value"
    trigger.triggered({"alter_value": 1.5})
    trigger.triggered({"affection": 0.5})
    assert received == [1.5, 0.5]


def test_switch_build_uses_curr_item_instead_of_curr_value():
    switch_exprop = maica_mtrigger.MTriggerExprop(
        item_name_zh="选项", item_list=["one"], curr_value="one"
    )
    switch_data = _build_trigger(
        maica_mtrigger.common_switch_template,
        exprop=switch_exprop,
    ).build()
    assert switch_data["exprop"].get("curr_item") == "one"
    assert "curr_value" not in switch_data["exprop"]


def test_meter_build_preserves_zero_curr_value():
    meter_exprop = maica_mtrigger.MTriggerExprop(
        item_name_zh="刻度", value_limits=[0, 100], curr_value=0
    )
    meter_data = _build_trigger(
        maica_mtrigger.common_meter_template,
        exprop=meter_exprop,
    ).build()
    assert meter_data["exprop"].get("curr_value") == 0


@pytest.mark.parametrize("item_list", [["ok", False], ["ok", ""]])
def test_mtrigger_rejects_invalid_switch_items_before_sending(item_list):
    with pytest.raises(ValueError):
        _build_trigger(
            maica_mtrigger.common_switch_template,
            exprop=maica_mtrigger.MTriggerExprop(
                item_name_zh="选项",
                item_list=item_list,
                curr_value="ok",
            ),
        ).build()


def test_mtrigger_accepts_one_character_name():
    data = _build_trigger(maica_mtrigger.common_affection_template, name="a").build()
    assert data["name"] == "a"


@pytest.mark.parametrize("name", ["n" * 64, "valid_name", "valid-name"])
def test_mtrigger_accepts_valid_name_boundaries(name):
    data = _build_trigger(maica_mtrigger.common_affection_template, name=name).build()
    assert data["name"] == name


@pytest.mark.parametrize("name", ["bad name", "n" * 65])
def test_mtrigger_rejects_invalid_names(name):
    with pytest.raises(ValueError):
        _build_trigger(maica_mtrigger.common_affection_template, name=name).build()


def test_mtrigger_rejects_empty_name():
    with pytest.raises(ValueError):
        _build_trigger(maica_mtrigger.common_affection_template, name="").build()


def test_mtrigger_accepts_256_character_bilingual_names_and_switch_items():
    item = "i" * 256
    data = _build_trigger(
        maica_mtrigger.common_switch_template,
        exprop=maica_mtrigger.MTriggerExprop(
            item_name_zh="中" * 256,
            item_name_en="e" * 256,
            item_list=[item, "j" * 256],
            curr_value=item,
        ),
    ).build()
    assert len(data["exprop"]["item_name"]["zh"]) == 256
    assert len(data["exprop"]["item_name"]["en"]) == 256
    assert all(len(value) == 256 for value in data["exprop"]["item_list"])


@pytest.mark.parametrize("field", ["item_name_zh", "item_name_en", "item_list"])
def test_mtrigger_rejects_item_strings_over_256_characters(field):
    kwargs = {
        "item_name_zh": "项目",
        "item_name_en": "item",
        "item_list": ["ok"],
        "curr_value": "ok",
    }
    if field == "item_list":
        kwargs[field] = ["ok", "i" * 257]
    else:
        kwargs[field] = "i" * 257
    with pytest.raises(ValueError):
        _build_trigger(
            maica_mtrigger.common_switch_template,
            exprop=maica_mtrigger.MTriggerExprop(**kwargs),
        ).build()


@pytest.mark.parametrize("limits", [[0, 100], [5, 5]])
def test_meter_accepts_two_item_non_descending_limits(limits):
    data = _build_trigger(
        maica_mtrigger.common_meter_template,
        exprop=maica_mtrigger.MTriggerExprop(
            item_name_zh="刻度", value_limits=limits, curr_value=limits[0]
        ),
    ).build()
    assert data["exprop"]["value_limits"] == limits


@pytest.mark.parametrize("limits", [[0], [0, 1, 2], [10, 1]])
def test_meter_limits_must_be_two_items_in_ascending_order(limits):
    with pytest.raises(ValueError):
        _build_trigger(
            maica_mtrigger.common_meter_template,
            exprop=maica_mtrigger.MTriggerExprop(
                item_name_zh="刻度", value_limits=limits
            ),
        ).build()


@pytest.mark.parametrize(
    ("limits", "curr_value"),
    [
        ([math.nan, 1], 0),
        ([-math.inf, math.inf], 0),
        ([0, 1], math.nan),
        ([0, 1], math.inf),
    ],
)
def test_meter_rejects_non_finite_numbers(limits, curr_value):
    with pytest.raises(ValueError):
        _build_trigger(
            maica_mtrigger.common_meter_template,
            exprop=maica_mtrigger.MTriggerExprop(
                item_name_zh="刻度",
                value_limits=limits,
                curr_value=curr_value,
            ),
        ).build()


def test_meter_number_types_are_python2_compatible_and_accept_large_integers():
    assert int in maica_mtrigger.integer_types
    assert int in maica_mtrigger.number_types
    assert float in maica_mtrigger.number_types

    large_value = 10 ** 1000
    data = _build_trigger(
        maica_mtrigger.common_meter_template,
        exprop=maica_mtrigger.MTriggerExprop(
            item_name_zh="刻度",
            value_limits=[0, large_value],
            curr_value=large_value,
        ),
    ).build()
    assert data["exprop"]["curr_value"] == large_value


@pytest.mark.parametrize(
    "canonical",
    [
        maica_mtrigger.common_affection_template,
        maica_mtrigger.common_switch_template,
        maica_mtrigger.common_meter_template,
        maica_mtrigger.customize_template,
    ],
)
def test_mtrigger_accepts_equivalent_canonical_template_clones(canonical):
    flags = canonical.exprop
    clone = maica_mtrigger.MTriggerTemplate(
        canonical.name,
        canonical.datakey,
        exprop=maica_mtrigger.MTriggerExprop(
            flags.item_name_zh,
            flags.item_name_en,
            flags.item_list,
            flags.value_limits,
            flags.curr_value,
            flags.suggestion,
        ),
    )
    assert _build_trigger(
        clone,
        exprop=_build_exprop(canonical),
    ).build()["template"] == canonical.name


def test_mtrigger_manager_rejects_spoofed_reserved_template_before_filtering():
    spoof = maica_mtrigger.MTriggerTemplate(
        maica_mtrigger.common_switch_template.name,
        maica_mtrigger.common_switch_template.datakey,
        exprop=maica_mtrigger.MTriggerExprop(False, False, False, False, False, False),
    )
    trigger = _build_trigger(
        spoof,
        exprop=maica_mtrigger.MTriggerExprop(item_name_zh="项目"),
    )
    trigger.method = maica_mtrigger.MTriggerMethod.table
    manager = maica_mtrigger.MTriggerManager()
    manager.add_trigger(trigger)

    with pytest.raises(ValueError):
        manager.build_data(maica_mtrigger.MTriggerMethod.request, full=True)


def test_mtrigger_builder_rejects_unknown_template_name():
    unknown = maica_mtrigger.MTriggerTemplate(
        "unknown_template",
        "value",
        exprop=maica_mtrigger.MTriggerExprop(True, True, False, True, True, False),
    )
    with pytest.raises(ValueError):
        _build_trigger(
            unknown,
            exprop=maica_mtrigger.MTriggerExprop(
                item_name_zh="刻度", value_limits=[0, 1], curr_value=0
            ),
        ).build()


@pytest.mark.parametrize(
    ("template", "limit"),
    [
        (maica_mtrigger.common_affection_template, 1),
        (maica_mtrigger.common_switch_template, 6),
        (maica_mtrigger.common_meter_template, 6),
        (maica_mtrigger.customize_template, 20),
    ],
)
def test_mtrigger_batch_limits_are_enforced(template, limit):
    assert len(_build_trigger_batch(template, limit)) == limit
    with pytest.raises(ValueError):
        _build_trigger_batch(template, limit + 1)


def test_switch_batch_limit_counts_triggers_across_methods():
    manager = maica_mtrigger.MTriggerManager()
    for index in range(6):
        trigger = _build_trigger(
            maica_mtrigger.common_switch_template,
            name="table_{}".format(index),
            exprop=_build_exprop(maica_mtrigger.common_switch_template),
        )
        trigger.method = maica_mtrigger.MTriggerMethod.table
        manager.add_trigger(trigger)
    request_trigger = _build_trigger(
        maica_mtrigger.common_switch_template,
        name="request_0",
        exprop=_build_exprop(maica_mtrigger.common_switch_template),
    )
    request_trigger.method = maica_mtrigger.MTriggerMethod.request
    manager.add_trigger(request_trigger)

    with pytest.raises(ValueError):
        manager.build_data(maica_mtrigger.MTriggerMethod.request, full=True)


def test_switch_batch_limit_allows_legal_total_across_methods():
    manager = maica_mtrigger.MTriggerManager()
    for index in range(5):
        trigger = _build_trigger(
            maica_mtrigger.common_switch_template,
            name="table_{}".format(index),
            exprop=_build_exprop(maica_mtrigger.common_switch_template),
        )
        trigger.method = maica_mtrigger.MTriggerMethod.table
        manager.add_trigger(trigger)
    request_trigger = _build_trigger(
        maica_mtrigger.common_switch_template,
        name="request_0",
        exprop=_build_exprop(maica_mtrigger.common_switch_template),
    )
    request_trigger.method = maica_mtrigger.MTriggerMethod.request
    manager.add_trigger(request_trigger)

    assert len(manager.build_data(maica_mtrigger.MTriggerMethod.table, full=True)) == 5
    assert len(manager.build_data(maica_mtrigger.MTriggerMethod.request, full=True)) == 1


def test_general_chat_payload_uses_triggers_key():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAGeneralChatProcessor(
        1, "general", manager
    )
    processor.process_request("hello", 1, ["trigger"], manager)
    payload = _last_json(manager)
    assert payload.get("triggers") == ["trigger"]
    assert "trigger" not in payload


def test_maica_chat_calls_general_processor_with_triggers_keyword():
    maica_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "python-packages"
        / "maica.py"
    ).read_text(encoding="utf-8")
    chat_block = maica_source.split("    def chat(self,", 1)[1].split(
        "    def start_raw_context", 1
    )[0]

    assert "triggers =" in chat_block
    assert "trigger =" not in chat_block


def test_builtin_switches_are_six_and_accessory_keeps_wear_and_unwear_actions():
    trigger_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "trigger.rpy"
    ).read_text(encoding="utf-8")

    assert trigger_source.count("common_switch_template") == 6
    assert "class AccessoryTrigger(MTriggerBase):" in trigger_source
    assert '"wear|{}"' in trigger_source
    assert '"unwear|{}"' in trigger_source
    assert 'store.renpy.call("mtrigger_change_acs"' in trigger_source
    assert 'store.renpy.call("mtrigger_unwear_acs"' in trigger_source


def test_general_query_accepts_exactly_4096_utf8_bytes():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAGeneralChatProcessor(
        1, "general", manager
    )
    query = "好" * 1365 + "x"
    assert len(query.encode("utf-8")) == 4096
    processor.process_request(query, 1, [], manager)
    assert _last_json(manager)["query"] == query


def test_general_query_rejects_4097_utf8_bytes():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAGeneralChatProcessor(
        1, "general", manager
    )
    query = "好" * 1365 + "xx"
    assert len(query.encode("utf-8")) == 4097
    with pytest.raises(ValueError):
        processor.process_request(query, 1, [], manager)


def test_general_processor_routes_minus_one_session_to_raw_context_validator():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAGeneralChatProcessor(
        1, "general", manager
    )
    query = [{"role": "user", "content": "hello"}]
    processor.process_request(query, -1, [], manager)
    assert _last_json(manager)["query"] == query


@pytest.mark.parametrize("query", ["hello", ("hello",)])
def test_general_processor_minus_one_session_rejects_non_list_query(query):
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAGeneralChatProcessor(
        1, "general", manager
    )
    with pytest.raises(ValueError):
        processor.process_request(query, -1, [], manager)


@pytest.mark.parametrize("session", [True, False, -1.0, "1", -2, 10])
def test_general_processor_rejects_invalid_session_values(session):
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAGeneralChatProcessor(
        1, "general", manager
    )
    query = [] if session == -1 else "hello"
    with pytest.raises(ValueError):
        processor.process_request(query, session, [], manager)


@pytest.mark.parametrize("session", [-1, 0, 9])
def test_general_processor_accepts_session_boundaries(session):
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAGeneralChatProcessor(
        1, "general", manager
    )
    query = [] if session == -1 else "hello"
    processor.process_request(query, session, [], manager)
    assert _last_json(manager)["chat_session"] == session


@pytest.mark.parametrize("query", [None, 123, ["hello"]])
def test_validate_query_text_rejects_non_text_values(query):
    with pytest.raises(ValueError):
        maica_tasker_sub_sessionsender.validate_query_text(query)


def test_validate_query_text_rejects_bytes_on_python3():
    if sys.version_info[0] >= 3:
        with pytest.raises(ValueError):
            maica_tasker_sub_sessionsender.validate_query_text(b"hello")
        with pytest.raises(ValueError):
            maica_tasker_sub_sessionsender.validate_query_text(b"\xff")


def test_raw_context_accepts_exactly_ten_messages():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICARawContextProcessor(
        1, "raw", manager
    )
    ten_messages = [{"role": "user", "content": "x"}] * 10
    processor.process_request(ten_messages, manager)
    assert _last_json(manager)["query"] == ten_messages


def test_raw_context_rejects_more_than_ten_messages():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICARawContextProcessor(
        1, "raw", manager
    )
    eleven_messages = [{"role": "user", "content": "x"}] * 11
    with pytest.raises(ValueError):
        processor.process_request(eleven_messages, manager)


def test_raw_context_size_validation_uses_compact_json_separators():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICARawContextProcessor(
        1, "raw", manager
    )
    content = "好" * 535 + "x"
    assert len(content.encode("utf-8")) == 1606
    compact_only_messages = [{"role": "user", "content": content}] * 10
    compact_size = len(
        json.dumps(
            compact_only_messages,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    default_size = len(
        json.dumps(compact_only_messages, ensure_ascii=False).encode("utf-8")
    )
    assert compact_size <= 16 * 1024 < default_size
    processor.process_request(compact_only_messages, manager)
    assert _last_json(manager)["query"] == compact_only_messages


def test_raw_context_accepts_compact_json_at_sixteen_kibibytes():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICARawContextProcessor(
        1, "raw", manager
    )
    query = _raw_messages_with_compact_size(16 * 1024)
    processor.process_request(query, manager)
    assert _last_json(manager)["query"] == query


def test_raw_context_rejects_compact_json_over_sixteen_kibibytes():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICARawContextProcessor(
        1, "raw", manager
    )
    query = _raw_messages_with_compact_size(16 * 1024 + 1)
    with pytest.raises(ValueError):
        processor.process_request(query, manager)


def test_validate_raw_context_reports_json_serialization_errors():
    with pytest.raises(ValueError, match="serializable"):
        maica_tasker_sub_sessionsender.validate_raw_context([object()])


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_validate_raw_context_rejects_nested_non_finite_numbers(value):
    secret = "private user body"
    with pytest.raises(ValueError) as exc_info:
        maica_tasker_sub_sessionsender.validate_raw_context(
            [{"role": "user", "content": secret, "metadata": {"value": value}}]
        )
    assert secret not in str(exc_info.value)


def test_mspire_ctg_weight_defaults_to_ten():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    processor.process_request(["science"], 1)
    payload = _last_json(manager)
    assert payload["inspire"].get("ctg_weight") == 10


def test_mspire_without_categories_sends_empty_inspire_object():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    processor.process_request([], 1)
    payload = _last_json(manager)
    assert payload.get("inspire") == {}


def test_mspire_places_use_cache_inside_inspire(monkeypatch):
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    monkeypatch.setattr(
        maica_tasker_sub_sessionsender.MAICAMSpireProcessor, "use_cache", True
    )
    processor.ctg_weight = 10
    processor.process_request(["science"], 0)
    payload = _last_json(manager)
    assert "use_cache" not in payload
    assert payload["inspire"].get("use_cache") is True


@pytest.mark.parametrize("value", [0, 101, True, 1.0, "10", None])
def test_mspire_rejects_invalid_ctg_weight(value):
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    processor.ctg_weight = value
    with pytest.raises(ValueError):
        processor.process_request(["science"], 1)


@pytest.mark.parametrize("value", [1, 100])
def test_mspire_accepts_integer_ctg_weight_boundaries(value):
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    processor.ctg_weight = value
    processor.process_request(["science"], 1)
    payload = _last_json(manager)
    assert payload["inspire"].get("ctg_weight") == value


def test_mspire_does_not_mutate_category_list():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    category = ["science", "memory", "science"]
    original = list(category)
    processor.process_request(category, 0, ctg_weight=20, use_cache=True)
    assert category == original
    assert _last_json(manager)["inspire"]["title"] == category


def test_mspire_single_category_title_remains_a_list():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    processor.process_request(["science"], 0)
    assert _last_json(manager)["inspire"]["title"] == ["science"]


@pytest.mark.parametrize("category", ["science", ("science",), None])
def test_mspire_rejects_non_list_categories(category):
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    with pytest.raises(ValueError):
        processor.process_request(category, 0)


@pytest.mark.parametrize("category", [[""], ["  "], [1], [None]])
def test_mspire_rejects_invalid_category_items(category):
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    with pytest.raises(ValueError):
        processor.process_request(category, 0)


@pytest.mark.parametrize("use_cache", [0, 1, "false", None])
def test_mspire_rejects_non_boolean_explicit_use_cache(use_cache):
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    with pytest.raises(ValueError):
        processor.process_request(["science"], 0, use_cache=use_cache)


def test_mspire_cache_is_only_allowed_for_session_zero():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    with pytest.raises(ValueError):
        processor.process_request(["science"], 1, use_cache=True)
    processor.process_request(["science"], 1, use_cache=False)


@pytest.mark.parametrize("category", [[], ["science"]])
def test_mspire_rejects_minus_one_session_before_sending(category):
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    with pytest.raises(ValueError, match="0 to 9"):
        processor.process_request(category, -1, use_cache=False)
    assert manager.ws_client.sent == []


@pytest.mark.parametrize("session", [0, 9])
def test_mspire_accepts_nonnegative_session_boundaries(session):
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    processor.process_request(["science"], session, use_cache=False)
    assert _last_json(manager)["chat_session"] == session


def test_mpostal_uses_v13_twk_super_option():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMPostalProcessor(
        1, "mpostal", manager
    )

    processor.process_request({"header": "mail", "content": "hello"})

    postmail = _last_json(manager)["postmail"]
    assert postmail["twk_super"] is True
    assert "ic_prep" not in postmail


def test_maica_start_mspire_forwards_weight_and_cache_to_processor():
    class ProcessorRecorder(object):
        def __init__(self):
            self.kwargs = None

        def start_request(self, **kwargs):
            self.kwargs = kwargs

    ai = object.__new__(maica.MaicaAi)
    ai._MaicaAi__accessable = True
    ai.is_ready_to_input = lambda: True
    ai.stat = {"mspire_count": 0}
    ai.MaicaAiStatus = maica.MaicaAi.MaicaAiStatus
    ai.MSpireProcessor = ProcessorRecorder()
    ai.mspire_category = ["science"]
    ai.mspire_session = 0
    ai.chat_session = 1
    ai.pprt = False
    ai.mspire_weight = 25
    ai.mspire_use_cache = True
    ai._in_mspire = False

    maica.MaicaAi.start_MSpire(ai)

    assert ai.MSpireProcessor.kwargs["ctg_weight"] == 25
    assert ai.MSpireProcessor.kwargs["use_cache"] is True


def test_streaming_completion_without_tracker_id_validates_and_resets(monkeypatch):
    validator = _new_validator(monkeypatch)
    _send_streaming_packets(validator, 3)
    assert validator.packet_count == 3

    validator.on_received(
        EventStub(
            "maica_core_complete",
            "Streaming finished for user, 3 packets sent",
        )
    )
    assert validator.validation_passed is True
    assert validator.packet_count == 0


def test_login_payload_explicitly_identifies_auth_request(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    manager = ManagerStub()
    tasker = maica_tasker_sub.MAICALoginTasker(1, "login", manager)
    tasker.on_manual_run("token")
    assert _last_json(manager) == {"type": "auth", "access_token": "token"}


def test_streaming_cache_completion_validates_without_tracker_id(monkeypatch):
    validator = _new_validator(monkeypatch)
    _send_streaming_packets(validator, 2)
    validator.on_received(
        EventStub("maica_core_complete", "MSpire cache finished, 2 packets sent")
    )
    assert validator.validation_passed is True
    assert validator.packet_count == 0


def test_streaming_legacy_seed_and_traceray_completion_still_validates(monkeypatch):
    validator = _new_validator(monkeypatch)
    _send_streaming_packets(validator, 2)
    validator.on_received(
        EventStub(
            "maica_core_complete",
            "Streaming finished with seed None for Monika, 2 packets sent -- your traceray ID is trace-1",
        )
    )
    assert validator.validation_passed is True
    assert validator.packet_count == 0


@pytest.mark.parametrize(
    "content",
    [
        "Streaming finished for user, -2 packets sent",
        "Streaming finished for user, 1.2 packets sent",
        "tracker 2024 packets sent",
        "Streaming finished for user, 2 packets sent malicious-tail",
    ],
)
def test_streaming_completion_rejects_ambiguous_or_extended_packet_counts(
    content, monkeypatch
):
    validator = _new_validator(monkeypatch)
    _send_streaming_packets(validator, 2)
    validator.on_received(EventStub("maica_core_complete", content))
    assert validator.validation_passed is False
    assert validator.packet_count == 0
    assert validator.manager.closed is True


@pytest.mark.parametrize("content", [None, 42, "request 99 completed without packet report"])
def test_streaming_nontext_or_unrelated_numbers_are_controlled_failures(
    content, monkeypatch
):
    validator = _new_validator(monkeypatch)
    _send_streaming_packets(validator, 1)
    validator.on_received(EventStub("maica_core_complete", content))
    assert validator.validation_passed is False
    assert validator.packet_count == 0
    assert validator.manager.closed is True


def test_streaming_disable_and_reset_clear_partial_count(monkeypatch):
    validator = _new_validator(monkeypatch)
    _send_streaming_packets(validator, 2)
    validator.disable()
    assert validator.packet_count == 0
    validator.enable()
    _send_streaming_packets(validator, 1)
    validator.reset()
    assert validator.packet_count == 0


def test_streaming_validation_resets_when_event_notification_raises(monkeypatch):
    validator = _new_validator(monkeypatch)
    _send_streaming_packets(validator, 1)

    def fail_create_event(_event):
        raise RuntimeError("notification failed")

    validator.manager.create_event = fail_create_event
    with pytest.raises(RuntimeError, match="notification failed"):
        validator.on_received(
            EventStub("maica_core_complete", "Streaming finished for user, 2 packets sent")
        )
    assert validator.validation_passed is False
    assert validator.packet_count == 0
    assert validator.manager.closed is True


def test_maica_registers_current_websocket_status_contracts(isolated_maica_ai_globals):
    ai = maica.MaicaAi("account", "password")
    assert ai.MPostalProcessor.except_ws_status == [
        "maica_core_streaming_continue",
        "maica_chat_loop_finished",
    ]
    assert "maica_quality_status" in ai.MTriggerTasker.except_ws_status
    loop_task = ai.task_manager.get_task("maicaloop_warn_handler")
    assert loop_task.except_ws_status == ["maica_loop_warn_reset"]


def test_maica_runtime_has_no_websocket_cookie_owner(isolated_maica_ai_globals):
    ai = maica.MaicaAi("account", "password")
    assert not hasattr(maica_tasker_sub, "MAICAWSCookiesHandler")
    assert not hasattr(ai, "WSCookiesTask")
    assert not hasattr(ai, "enable_strict_mode")


def test_manual_maica_example_has_no_retired_cookie_or_strict_owner():
    source = (PACKAGE_ROOT / "test_maica.py").read_text(encoding="utf-8")
    assert "enable_strict_mode" not in source
    assert "WSCookiesTask" not in source
    assert "MAICAWSCookiesHandler" not in source


def test_auto_resume_uses_generation_marker_and_clears_after_terminal_event(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    manager = ManagerStub()
    tasker = maica_tasker_sub.AutoResumeTasker(
        1,
        "resume",
        manager,
        except_ws_status=["maica_mcore_gen_start", "maica_chat_loop_finished"],
    )
    tasker.enable()
    tasker.set_should_resume_func(lambda: True)

    def ws_event(status):
        return type(
            "WsEvent",
            (),
            {
                "event_type": maica_tasker.MAICATASKEVENT_TYPE_WS,
                "data": type("Data", (), {"status": status})(),
            },
        )()

    def task_event(name):
        return type(
            "TaskEvent",
            (),
            {
                "event_type": maica_tasker.MAICATASKEVENT_TYPE_TASK,
                "data": type("Data", (), {"name": name})(),
            },
        )()

    tasker.on_event(ws_event("maica_mcore_gen_start"))
    tasker.on_event(task_event("auto_reconnector_start_reconnect"))
    tasker.on_event(task_event("maica_login_successful"))
    assert _last_json(manager) == {"type": "reconn"}

    manager.ws_client.sent[:] = []
    tasker.on_event(ws_event("maica_chat_loop_finished"))
    tasker.on_event(task_event("auto_reconnector_start_reconnect"))
    tasker.on_event(task_event("maica_login_successful"))
    assert manager.ws_client.sent == []

    tasker.on_event(ws_event("maica_mcore_gen_start"))
    tasker.on_event(task_event("auto_reconnector_start_reconnect"))
    tasker.on_event(task_event("websocket_closed"))
    tasker.on_event(task_event("maica_login_successful"))
    tasker.on_event(task_event("maica_login_successful"))
    assert [json.loads(payload) for payload in manager.ws_client.sent] == [
        {"type": "reconn"}
    ]

    manager.ws_client.sent[:] = []
    tasker.on_event(ws_event("maica_mcore_gen_start"))
    tasker._on_reconnect = False
    tasker.on_event(task_event("websocket_closed"))
    tasker.on_event(task_event("auto_reconnector_start_reconnect"))
    tasker.on_event(task_event("maica_login_successful"))
    assert manager.ws_client.sent == []


def test_auto_resume_disabled_ignores_generation_marker(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    tasker = maica_tasker_sub.AutoResumeTasker(
        1, "resume-disabled", ManagerStub(), ["maica_mcore_gen_start"]
    )
    event = type(
        "WsEvent",
        (),
        {
            "event_type": maica_tasker.MAICATASKEVENT_TYPE_WS,
            "data": type("Data", (), {"status": "maica_mcore_gen_start"})(),
        },
    )()
    tasker.on_event(event)
    tasker.enable()
    assert tasker._generation_started is False
    assert tasker._on_reconnect is False


def test_auto_resume_loop_finish_and_disable_clear_all_resume_flags(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    tasker = maica_tasker_sub.AutoResumeTasker(
        1,
        "resume-terminal",
        ManagerStub(),
        ["maica_mcore_gen_start", "maica_chat_loop_finished"],
    )
    tasker.enable()
    tasker._generation_started = True
    tasker._on_reconnect = True
    loop_event = type(
        "WsEvent",
        (),
        {
            "event_type": maica_tasker.MAICATASKEVENT_TYPE_WS,
            "data": type("Data", (), {"status": "maica_chat_loop_finished"})(),
        },
    )()
    tasker.on_event(loop_event)
    assert tasker._generation_started is False
    assert tasker._on_reconnect is False

    tasker._generation_started = True
    tasker._on_reconnect = True
    tasker.disable()
    assert tasker._generation_started is False
    assert tasker._on_reconnect is False


def test_auto_resume_send_failure_clears_resume_flags(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    manager = ManagerStub()
    tasker = maica_tasker_sub.AutoResumeTasker(1, "resume-send-failure", manager)
    tasker.enable()
    tasker.set_should_resume_func(lambda: True)
    tasker._generation_started = True
    tasker._on_reconnect = True

    def fail_send(_payload):
        raise RuntimeError("send failed")

    manager.ws_client.send = fail_send
    login_event = type(
        "TaskEvent",
        (),
        {
            "event_type": maica_tasker.MAICATASKEVENT_TYPE_TASK,
            "data": type("Data", (), {"name": "maica_login_successful"})(),
        },
    )()
    with pytest.raises(RuntimeError, match="send failed"):
        tasker.on_event(login_event)
    assert tasker._generation_started is False
    assert tasker._on_reconnect is False


def test_auto_resume_should_resume_failure_clears_flags_without_retry(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    manager = ManagerStub()
    tasker = maica_tasker_sub.AutoResumeTasker(1, "resume-check-failure", manager)
    tasker.enable()
    tasker._generation_started = True
    tasker._on_reconnect = True

    def fail_check():
        raise RuntimeError("resume check failed")

    tasker.set_should_resume_func(fail_check)
    login_event = type(
        "TaskEvent",
        (),
        {
            "event_type": maica_tasker.MAICATASKEVENT_TYPE_TASK,
            "data": type("Data", (), {"name": "maica_login_successful"})(),
        },
    )()
    with pytest.raises(RuntimeError, match="resume check failed"):
        tasker.on_event(login_event)
    assert tasker._generation_started is False
    assert tasker._on_reconnect is False
    tasker.on_event(login_event)
    assert manager.ws_client.sent == []

@pytest.mark.parametrize(
    "content",
    [
        "malformed completion",
        "Streaming finished for user, 2 packets sent",
    ],
)
def test_streaming_malformed_and_mismatched_completion_paths_reset_count(
    content, monkeypatch
):
    validator = _new_validator(monkeypatch)
    _send_streaming_packets(validator, 1)
    assert validator.packet_count == 1

    validator.on_received(EventStub("maica_core_complete", content))
    assert validator.packet_count == 0


def _emotion_selector(fallback_predictor=None):
    return emotion_analyze_v2.EmoSelector(
        selector={"微笑": {"eua": 0.5}},
        storage={"eua": 0.5},
        sentiment={"微笑": "positive"},
        fallback_predictor=fallback_predictor,
        eoc={"eua": False},
    )


def test_unknown_emotion_without_fallback_predictor_does_not_call_network(
    monkeypatch,
):
    def fail_network(*args, **kwargs):
        raise AssertionError("network fallback must not be called")

    for method_name in ("get", "post", "request"):
        monkeypatch.setattr(
            maica_vista_files_manager.requests,
            method_name,
            fail_network,
        )
    monkeypatch.setattr(urllib.request, "urlopen", fail_network)
    monkeypatch.setattr(maica.MaicaAi, "get_emotion", fail_network)
    selector = _emotion_selector(fallback_predictor=None)
    try:
        result = selector.analyze("[未知]")
    except Exception as exc:
        pytest.fail(
            "unknown emotion must be handled without fallback network call: {}".format(
                exc
            )
        )
    assert isinstance(result, list)


def test_unknown_emotion_uses_local_fallback_even_when_callback_is_configured():
    def fail_callback(*args, **kwargs):
        raise AssertionError("unknown emotion must not use remote callback")

    selector = _emotion_selector(fallback_predictor=fail_callback)
    result = selector.analyze("before[未知]after", keep_tags=True)
    assert "".join(piece for _emotion, piece in result) == "beforeafter"


def test_player_nickname_tag_is_converted_to_mas_macro():
    def fail_fallback(*args, **kwargs):
        raise AssertionError("nickname tag must not use emotion fallback")

    selector = _emotion_selector(
        fallback_predictor=fail_fallback
    )
    try:
        result = selector.analyze("[player_nickname]", keep_tags=True)
    except Exception as exc:
        pytest.fail("player nickname tag must be handled: {}".format(exc))
    rendered = "".join(piece for _emotion, piece in result)
    assert "[mas_get_player_nickname()]" in rendered
    assert "[player_nickname]" not in rendered


def test_player_nickname_conversion_preserves_mixed_text_and_repeated_placeholders():
    def fail_fallback(*args, **kwargs):
        raise AssertionError("nickname tag must not use emotion fallback")

    selector = _emotion_selector(fallback_predictor=fail_fallback)
    result = selector.analyze(
        "Hello [player_nickname], [player_nickname]!", keep_tags=True
    )
    rendered = "".join(piece for _emotion, piece in result)
    assert rendered == (
        "Hello [mas_get_player_nickname()], [mas_get_player_nickname()]!"
    )


def test_player_nickname_conversion_does_not_replace_literal_internal_text():
    selector = _emotion_selector()
    literal = "__MAICA_PLAYER_NICKNAME_PLACEHOLDER__"
    result = selector.analyze(literal + " [player_nickname]", keep_tags=True)
    rendered = "".join(piece for _emotion, piece in result)
    assert rendered == literal + " [mas_get_player_nickname()]"


def test_local_fallback_uses_the_configured_emotion_sequence():
    fallback = emotion_analyze_v2.FallBackEmo()
    fallback.last = "开心"
    assert fallback.predict() == "笑"


def test_vista_list_uses_list_endpoint_and_download_keeps_content_parameter(monkeypatch):
    manager = maica_vista_files_manager.MAICAVistaFilesManager(
        "https://example.test/api", "token"
    )
    calls = []

    class ResponseStub:
        def __init__(self, payload=None, headers=None, content=b""):
            self._payload = payload
            self.headers = headers or {}
            self.content = content

        def json(self):
            return self._payload

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        if url.endswith("/list") or "access_token" in kwargs.get("params", {}):
            return ResponseStub({"success": True, "content": ["uuid-1"]})
        return ResponseStub(headers={"content-type": "image/png"}, content=b"image")

    monkeypatch.setattr(maica_vista_files_manager.requests, "get", fake_get)
    assert manager.list_remote(force_refresh=True) == ["uuid-1"]
    assert manager.download("uuid-1") == b"image"
    assert calls[0][0] == "https://example.test/api/vista/list"
    assert calls[1][0] == "https://example.test/api/vista"
    assert calls[1][1]["params"]["content"] == "uuid-1"


def test_legality_ui_accepts_canonical_and_alias_coordinate_fields():
    screen = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "screen_subs.rpy"
    ).read_text(encoding="utf-8")
    assert 'get("latitude"' in screen and 'get("lat"' in screen
    assert 'get("longitude"' in screen
    assert 'get("lng"' in screen and 'get("lon"' in screen
    assert "latitude" in screen and "longitude" in screen


def test_setting_migration_renames_tristates_and_is_idempotent():
    import maica_v13_migration

    values = {
        "sfe_aggressive": True,
        "prompt_pname_repl": False,
        "mf_sf_access_impl": False,
        "mf_const_sf_access": True,
        "mt_concl_memory": 2,
        "tnd_aggressive": 3,
        "mf_const_tools": 1,
        "max_length": 99999,
        "session_len_limit": 8192,
    }
    status = {"sfe_aggressive": True, "prompt_pname_repl": False}

    maica_v13_migration.migrate_setting_values(values, status)
    first = (dict(values), dict(status))
    maica_v13_migration.migrate_setting_values(values, status)

    assert (values, status) == first
    assert values["prompt_pname_repl"] is True
    assert status["prompt_pname_repl"] is True
    assert values["mf_sf_access_impl"] == 0
    assert values["mf_const_sf_access"] == 1
    assert values["mt_concl_memory"] == 2
    assert values["mf_const_tools"] == 2
    assert values["session_len_limit"] == 28672


def test_setting_migration_defaults_invalid_and_missing_tristates_with_warnings():
    import maica_v13_migration

    values = {
        "mf_sf_access_impl": "invalid",
        "mf_const_sf_access": None,
    }
    warnings = []

    maica_v13_migration.migrate_setting_values(
        values,
        warning_callback=warnings.append,
    )

    assert values["mf_sf_access_impl"] == 1
    assert values["mf_const_sf_access"] == 1
    assert values["mt_concl_memory"] == 1
    assert len(warnings) == 2


def test_outbound_settings_normalize_tristates_to_real_integers():
    import maica_v13_migration

    normalized = maica.normalize_chat_params(
        {
            "mf_sf_access_impl": False,
            "mf_const_sf_access": True,
            "mt_concl_memory": "invalid",
        }
    )

    assert normalized["mf_sf_access_impl"] == 0
    assert normalized["mf_const_sf_access"] == 1
    assert normalized["mt_concl_memory"] == 1
    for key in maica_v13_migration.TRISTATE_SETTINGS:
        assert type(normalized[key]) is int


def test_outbound_settings_drop_retained_legacy_keys():
    import maica_v13_migration

    params = {old: "legacy" for old in maica_v13_migration.SETTING_RENAMES}
    params.update(
        {
            "mf_const_tools": 1,
            "session_len_limit": 8192,
            "mt_extraction": True,
        }
    )

    normalized = maica.normalize_chat_params(params)

    for old in maica_v13_migration.SETTING_RENAMES:
        assert old not in normalized
    assert "mt_extraction" not in normalized


def test_player_additions_backup_is_created_once_and_filters_utf8_boundaries():
    import maica_v13_migration

    values = ["ok", "中" * 512, "中" * 513, 7] + ["item-{}".format(i) for i in range(511)]
    backup = []

    active = maica_v13_migration.backup_and_filter_player_additions(values, backup)
    original_backup = list(backup)
    active_again = maica_v13_migration.backup_and_filter_player_additions(values, backup)

    assert backup == original_backup == values
    assert active == active_again
    assert len(active) == 512
    assert active[:2] == ["ok", "中" * 512]
    assert "中" * 513 not in active
    assert 7 not in active


def test_player_additions_backup_preserves_but_filters_unencodable_text():
    import maica_v13_migration

    invalid = "\udcff"
    backup = []
    active = maica_v13_migration.backup_and_filter_player_additions(
        ["ok", invalid],
        backup,
    )

    assert backup == ["ok", invalid]
    assert active == ["ok"]


def test_player_additions_does_not_replace_an_initialized_empty_backup():
    import maica_v13_migration

    backup = []
    active = maica_v13_migration.backup_and_filter_player_additions(
        ["added-after-migration"],
        backup,
        backup_initialized=True,
    )

    assert active == ["added-after-migration"]
    assert backup == []


def test_maica_ai_constructs_version_info(isolated_maica_ai_globals):
    ai = maica.MaicaAi("account", "password")
    assert hasattr(ai, "version_info")


def test_maica_ai_disable_accepts_and_saves_status(isolated_maica_ai_globals):
    ai = maica.MaicaAi("account", "password")
    marker = ai.MaicaAiStatus.SERVER_MAINTAIN
    try:
        ai.disable(marker)
    except TypeError as exc:
        pytest.fail("disable(status) must accept and save status: {}".format(exc))
    assert ai.status == marker
