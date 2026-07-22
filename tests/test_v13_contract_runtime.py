import json
import sys
from pathlib import Path

import pytest


PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "game" / "python-packages"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

import emotion_analyze_v2
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
    return maica_mtrigger.MTriggerExprop(item_name_zh="项目")


def _last_json(manager):
    assert manager.ws_client.sent
    return json.loads(manager.ws_client.sent[-1])


def _new_validator(monkeypatch, packet_count=1):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    validator = object.__new__(maica_tasker_sub.StreamingPacketValidator)
    validator.manager = ManagerStub()
    validator._enabled = True
    validator._packet_count = packet_count
    validator._validation_passed = True
    return validator


def test_common_switch_template_uses_choice_datakey():
    assert maica_mtrigger.common_switch_template.datakey == "choice"


def test_switch_build_uses_curr_item_instead_of_curr_value():
    switch_exprop = maica_mtrigger.MTriggerExprop(
        item_name_zh="选项", item_list=["one"], curr_value="one"
    )
    switch_exprop.curr_item = "one"
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


def test_mtrigger_rejects_false_switch_item():
    exprop = maica_mtrigger.MTriggerExprop(
        item_name_zh="选项", item_list=["one"], curr_value=False
    )
    exprop.curr_item = False
    with pytest.raises(ValueError):
        _build_trigger(
            maica_mtrigger.common_switch_template,
            exprop=exprop,
        ).build()


@pytest.mark.parametrize("name", ["bad name", "n" * 65])
def test_mtrigger_rejects_invalid_names(name):
    with pytest.raises(ValueError):
        _build_trigger(maica_mtrigger.common_affection_template, name=name)


def test_mtrigger_rejects_strings_over_256_characters():
    with pytest.raises(ValueError):
        _build_trigger(
            maica_mtrigger.common_affection_template,
            description="d" * 257,
        )


@pytest.mark.parametrize("limits", [[0], [10, 1]])
def test_meter_limits_must_be_two_items_in_ascending_order(limits):
    with pytest.raises(ValueError):
        _build_trigger(
            maica_mtrigger.common_meter_template,
            exprop=maica_mtrigger.MTriggerExprop(
                item_name_zh="刻度", value_limits=limits
            ),
        )


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
    manager = maica_mtrigger.MTriggerManager()
    for index in range(limit):
        manager.add_trigger(
            _build_trigger(
                template,
                name="trigger_{}".format(index),
                exprop=_build_exprop(template),
            )
        )
    with pytest.raises(ValueError):
        manager.add_trigger(
            _build_trigger(
                template,
                name="trigger_over",
                exprop=_build_exprop(template),
            )
        )


def test_general_chat_payload_uses_triggers_key():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAGeneralChatProcessor(
        1, "general", manager
    )
    processor.process_request("hello", 1, ["trigger"], manager)
    payload = _last_json(manager)
    assert payload.get("triggers") == ["trigger"]
    assert "trigger" not in payload


def test_general_query_rejects_utf8_payload_over_four_kibibytes():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAGeneralChatProcessor(
        1, "general", manager
    )
    with pytest.raises(ValueError):
        processor.process_request("好" * 1366, 1, [], manager)


def test_raw_context_rejects_more_than_ten_messages():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICARawContextProcessor(
        1, "raw", manager
    )
    eleven_messages = [{"role": "user", "content": "x"}] * 11
    with pytest.raises(ValueError):
        processor.process_request(eleven_messages, manager)


def test_raw_context_rejects_compact_json_over_sixteen_kibibytes():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICARawContextProcessor(
        1, "raw", manager
    )
    oversized_messages = [{"role": "user", "content": "好" * 1800}] * 10
    compact_size = len(
        json.dumps(oversized_messages, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
    )
    assert compact_size > 16 * 1024
    with pytest.raises(ValueError):
        processor.process_request(oversized_messages, manager)


def test_mspire_ctg_weight_defaults_to_ten():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    assert getattr(processor, "ctg_weight", None) == 10


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


@pytest.mark.parametrize("value", [0, 101, True, 1.0])
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


def test_streaming_completion_without_tracker_id_validates_and_resets(monkeypatch):
    validator = _new_validator(monkeypatch, packet_count=3)

    validator.on_received(
        EventStub(
            "maica_core_complete",
            "Streaming finished for user, 3 packets sent",
        )
    )
    assert validator.validation_passed is True
    assert validator.packet_count == 0


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


def test_unknown_emotion_without_fallback_predictor_does_not_crash_or_call_network():
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


def test_player_nickname_tag_is_preserved_or_converted_to_mas_macro():
    selector = _emotion_selector(
        fallback_predictor=lambda _mode, _label: {"success": False}
    )
    try:
        result = selector.analyze("[player_nickname]", keep_tags=True)
    except Exception as exc:
        pytest.fail("player nickname tag must be handled: {}".format(exc))
    rendered = "".join(piece for _emotion, piece in result)
    assert "[player_nickname]" in rendered or "[mas_get_player_nickname()]" in rendered


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


def test_maica_ai_constructs_version_info():
    ai = maica.MaicaAi("account", "password")
    assert hasattr(ai, "version_info")


def test_maica_ai_disable_accepts_and_saves_status():
    ai = maica.MaicaAi("account", "password")
    marker = ai.MaicaAiStatus.SERVER_MAINTAIN
    try:
        ai.disable(marker)
    except TypeError as exc:
        pytest.fail("disable(status) must accept and save status: {}".format(exc))
    assert ai.status == marker
