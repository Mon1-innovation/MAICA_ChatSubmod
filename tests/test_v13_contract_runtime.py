import json
import logging
import math
import re
import sys
import threading
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
import maica_v13_migration
import migrations


def test_development_migration_force_current_is_repeatable():
    calls = []
    migration = migrations.migration_instance(
        "1.8.0", "1.8.0", force_current=True
    )
    migration.migration_queue = [
        ("1.7.9", lambda: calls.append("old")),
        ("1.8.0", lambda: calls.append("current")),
    ]

    migration.migrate()
    migration.migrate()

    assert calls == ["current", "current"]


def test_migration_default_and_development_upgrade_paths_do_not_duplicate():
    calls = []
    unchanged = migrations.migration_instance("1.8.0", "1.8.0")
    unchanged.migration_queue = [("1.8.0", lambda: calls.append("unchanged"))]
    assert unchanged.migrate() == (True, "Version unchanged")

    upgrading = migrations.migration_instance(
        "1.7.9", "1.8.0", force_current=True
    )
    upgrading.migration_queue = [
        ("1.8.0", lambda: calls.append("upgrade")),
    ]
    upgrading.migrate()

    assert calls == ["upgrade"]


def test_development_migration_runs_after_switching_back_from_newer_version():
    calls = []
    migration = migrations.migration_instance(
        "1.9.0", "1.8.0", force_current=True
    )
    migration.migration_queue = [
        ("1.8.0", lambda: calls.append("current")),
        ("1.9.0", lambda: calls.append("newer")),
    ]

    migration.migrate()

    assert calls == ["current"]


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


def _ws_event(taskowner, status, content="detail", code=400, event_type="error"):
    return type(
        "WsEvent",
        (),
        {
            "taskowner": taskowner,
            "event_type": maica_tasker.MAICATASKEVENT_TYPE_WS,
            "data": type(
                "Packet",
                (),
                {
                    "status": status,
                    "content": content,
                    "code": code,
                    "type": event_type,
                },
            )(),
        },
    )()


def test_task_reset_restores_ready_status(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    task = maica_tasker.MaicaTask(
        maica_tasker.MaicaTask.MAICATASK_TYPE_NORMAL,
        "reset-test",
        None,
    )
    task.status = task.MAICATASK_STATUS_ERROR

    task.reset()

    assert task.status == task.MAICATASK_STATUS_READY


def test_login_tasker_exposes_current_backend_failure_statuses(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    manager = ManagerStub()
    tasker = maica_tasker_sub.MAICALoginTasker(
        1,
        "login",
        manager,
        except_ws_status=list(maica_tasker_sub.MAICALoginTasker.LOGIN_FAILURE_STATUSES),
    )
    statuses = (
        "maica_login_token_corrupted",
        "maica_login_token_invalid",
        "maica_login_f2b",
        "maica_login_banned",
        "maica_login_email_unchecked",
        "maica_login_tos_unaccepted",
        "maica_connection_reuse_denied",
    )
    for status in statuses:
        event = type(
            "WsEvent",
            (),
            {
                "event_type": maica_tasker.MAICATASKEVENT_TYPE_WS,
                "data": type("Packet", (), {"status": status, "content": "detail", "code": 400})(),
            },
        )()
        tasker.on_event(event)
        assert manager.closed is True
        failure = manager.events[-1].data
        assert failure.name == "maica_login_failed"
        assert failure.content["status"] == status
        tasker.reset()
        manager.closed = False

    assert not hasattr(tasker, "wrong_pwd")
    assert not hasattr(tasker, "login_status")


def test_login_tasker_ignores_unified_warning_after_login(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    manager = ManagerStub()
    tasker = maica_tasker_sub.MAICALoginTasker(
        1,
        "login-success-warning",
        manager,
        except_ws_status=list(maica_tasker_sub.MAICALoginTasker.PREAUTH_FAILURE_STATUSES),
    )
    tasker.success = True

    tasker.on_event(
        _ws_event(manager, "maica_unified_warning", code=409, event_type="warn")
    )

    assert tasker.success is True
    assert tasker.status == tasker.MAICATASK_STATUS_READY
    assert manager.closed is False
    assert not any(
        getattr(getattr(event, "data", None), "name", None) == "maica_login_failed"
        for event in manager.events
    )


def test_login_tasker_treats_preauth_unified_error_as_login_failure(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    manager = ManagerStub()
    tasker = maica_tasker_sub.MAICALoginTasker(
        1,
        "login-preauth-error",
        manager,
        except_ws_status=list(maica_tasker_sub.MAICALoginTasker.PREAUTH_FAILURE_STATUSES),
    )
    results = []
    tasker.set_result_callback(lambda *args: results.append(args))

    tasker.on_event(_ws_event(manager, "maica_unified_error", code=500))

    assert tasker.success is False
    assert tasker.status == tasker.MAICATASK_STATUS_ERROR
    assert manager.closed is True
    assert results == [(False, "maica_unified_error", "detail", 500)]


def test_general_ws_error_handler_can_defer_login_failure_close(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    manager = ManagerStub()
    handler = maica_tasker_sub.GeneralWsErrorHandler(1, "ws-error", manager)
    handler.set_error_callback(lambda *args: False)

    handler.on_event(_ws_event(manager, "maica_unified_error", code=500))

    assert manager.closed is False


@pytest.mark.parametrize(
    "protocol_status, expected_status",
    [
        ("maica_login_token_corrupted", maica.MaicaAi.MaicaAiStatus.TOKEN_CORRUPTED),
        ("maica_login_token_invalid", maica.MaicaAi.MaicaAiStatus.TOKEN_INVALID),
        ("maica_login_f2b", maica.MaicaAi.MaicaAiStatus.LOGIN_BLOCKED),
        ("maica_login_banned", maica.MaicaAi.MaicaAiStatus.ACCOUNT_BANNED),
        ("maica_login_email_unchecked", maica.MaicaAi.MaicaAiStatus.EMAIL_UNVERIFIED),
        ("maica_login_tos_unaccepted", maica.MaicaAi.MaicaAiStatus.TOS_UNACCEPTED),
        ("maica_connection_reuse_denied", maica.MaicaAi.MaicaAiStatus.CONNECTION_REUSE_DENIED),
    ],
)
def test_login_result_maps_protocol_failure_to_numeric_status(
    protocol_status, expected_status
):
    ai = object.__new__(maica.MaicaAi)
    ai.status = ai.MaicaAiStatus.IDLE

    ai._handle_login_result(False, protocol_status, "detail", 400)

    assert ai.status == expected_status
    assert ai.get_error_result() == {
        "success": False,
        "status": protocol_status,
        "exception": "detail",
        "code": 400,
    }


def test_clear_error_removes_stale_numeric_error_status():
    ai = object.__new__(maica.MaicaAi)
    ai.status = ai.MaicaAiStatus.TOKEN_INVALID
    ai.error_protocol_status = "maica_login_token_invalid"
    ai.error_message = "detail"
    ai.error_protocol_code = 400

    ai.clear_error()

    assert ai.status == ai.MaicaAiStatus.IDLE
    assert ai.get_error_result() == {
        "success": False,
        "status": None,
        "exception": None,
        "code": None,
    }


def test_login_result_moves_authenticated_client_to_connected_state():
    ai = object.__new__(maica.MaicaAi)
    ai.status = ai.MaicaAiStatus.WAIT_AVAILABILITY
    ai.error_protocol_status = "old_error"
    ai.error_message = "old detail"
    ai.error_protocol_code = 500

    ai._handle_login_result(True)

    assert ai.status == ai.MaicaAiStatus.CONNECTED
    assert ai.get_error_result() == {
        "success": False,
        "status": None,
        "exception": None,
        "code": None,
    }


def test_maica_status_inventory_excludes_retired_state_machine_codes():
    status = maica.MaicaAi.MaicaAiStatus
    assert status.IDLE == 10000
    assert status.WAIT_AVAILABILITY == 10010
    assert status.WEBSOCKET_CONNECTING == 10020
    assert status.CONNECTED == 10302
    assert status.CERTIFI_RESTART_REQUIRED == 13418
    assert status.CERTIFI_RESTART_REQUIRED != status.SERVER_REJECTED

    retired_names = (
        "WAIT_AUTH",
        "WAIT_SERVER_TOKEN",
        "WAIT_USE_TOKEN",
        "SESSION_CREATED",
        "WAIT_MODEL_INFOMATION",
        "SSL_FAILED_BUT_OKAY",
        "MESSAGE_WAIT_SEND",
        "MESSAGE_WAIT_SEND_MSPIRE",
        "MESSAGE_WAIT_SEND_MPOSTAL",
        "MESSAGE_WAITING_RESPONSE",
        "MESSAGE_DONE",
        "REQUEST_RESET_SESSION",
        "SESSION_RESETED",
        "REQUEST_PING",
        "SEND_SETTING",
        "WAIT_SETTING_RESPONSE",
        "TOKEN_MAX_EXCEEDED",
        "TOKEN_WARN_EXCEEDED",
    )
    assert not [name for name in retired_names if hasattr(status, name)]
    assert not hasattr(status, "MAIKA_PREFIX")
    assert not hasattr(status, "is_1xx")

    game_root = PACKAGE_ROOT.parent
    sources = []
    for pattern in ("*.py", "*.rpy"):
        sources.extend(
            path.read_text(encoding="utf-8-sig")
            for path in game_root.rglob(pattern)
        )
    source = "\n".join(sources)
    assert not [
        name
        for name in retired_names
        if "MaicaAiStatus." + name in source
    ]


def test_connection_scripts_do_not_reference_retired_error_state_api():
    root = PACKAGE_ROOT.parent
    paths = [
        root / "Submods" / "MAICA_ChatSubmod" / "main.rpy",
        root / "Submods" / "MAICA_ChatSubmod" / "chat.rpy",
        root / "Submods" / "MAICA_ChatSubmod" / "header.rpy",
        root / "Submods" / "MAICA_ChatSubmod" / "raw_session_example.rpy",
    ]
    source = "\n".join(path.read_text(encoding="utf-8-sig") for path in paths)
    retired_names = (
        "login_failure_message",
        "TOKEN_FAILED",
        "SAVEFILE_NOTFOUND",
        "MODEL_NOT_FOUND",
        "WSS_CLOSED_UNEXCEPTED",
        "NO_INTERTENT",
    )

    assert not [name for name in retired_names if name in source]
    assert "call maica_init_connect" in paths[0].read_text(encoding="utf-8-sig")
    assert "call maica_init_connect" in paths[1].read_text(encoding="utf-8-sig")
    raw_example = paths[3].read_text(encoding="utf-8-sig")
    assert 'if _return == "disconnected":' in raw_example


def test_verify_token_preserves_backend_status_from_http_error(monkeypatch):
    class Response:
        def json(self):
            return {
                "success": False,
                "exception": "maica_login_email_unchecked: Email not verified",
            }

    class Provider:
        def get_api_url(self):
            return "https://backend.test/api"

    ai = object.__new__(maica.MaicaAi)
    ai._MaicaAi__accessable = True
    ai.ciphertext = "token-value"
    ai.provider_manager = Provider()
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: Response())

    result = ai._verify_token()

    assert result["status"] == "maica_login_email_unchecked"
    assert result["exception"] == "Email not verified"


def _make_legality_client():
    class Provider:
        def get_api_url(self):
            return "https://backend.test/api"

    ai = object.__new__(maica.MaicaAi)
    ai._MaicaAi__accessable = True
    ai.ciphertext = "token-value"
    ai.provider_manager = Provider()
    return ai


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    ((30.5928, 114.3055), (0.0, 0.0)),
)
def test_verify_legality_preserves_canonical_coordinates(
    monkeypatch, latitude, longitude
):
    calls = []
    payload = {
        "success": True,
        "exception": None,
        "content": {"latitude": latitude, "longitude": longitude},
    }

    class Response:
        status_code = 200
        text = ""

        def json(self):
            return payload

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return Response()

    monkeypatch.setattr("requests.get", fake_get)
    ai = _make_legality_client()

    result = ai.verify_legality("geolocation", "Wuhan")

    assert result == payload
    assert result["content"] == {
        "latitude": latitude,
        "longitude": longitude,
    }
    assert ai.extract_legality_coordinates(result) == (latitude, longitude)
    assert calls[0][0] == "https://backend.test/api/legality"
    assert json.loads(calls[0][1]["params"]["content"]) == {
        "object": "geolocation",
        "value": "Wuhan",
    }


@pytest.mark.parametrize(
    "content",
    (
        {"lat": 30.5928, "lng": 114.3055},
        {"lat": 30.5928, "lon": 114.3055},
        {"latitude": 30.5928},
        {"longitude": 114.3055},
        "test-user",
    ),
)
def test_verify_legality_rejects_noncanonical_coordinate_payload(
    monkeypatch, content
):
    class Response:
        status_code = 200
        text = ""

        def json(self):
            return {"success": True, "exception": None, "content": content}

    monkeypatch.setattr("requests.get", lambda *args, **kwargs: Response())
    result = _make_legality_client().verify_legality("geolocation", "Wuhan")

    assert result["success"] is False
    assert "latitude/longitude" in result["exception"]


@pytest.mark.parametrize(
    ("verification_object", "verification_value"),
    (
        ("geolocation", ""),
        ("geolocation", "   "),
        ("", "Wuhan"),
        (None, "Wuhan"),
        ("geolocation", 114),
        (114, "Wuhan"),
    ),
)
def test_verify_legality_rejects_incomplete_content_without_request(
    monkeypatch, verification_object, verification_value
):
    calls = []
    monkeypatch.setattr(
        "requests.get",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    result = _make_legality_client().verify_legality(
        verification_object, verification_value
    )

    assert result["success"] is False
    assert calls == []


def test_verify_legality_without_content_keeps_token_only_check(monkeypatch):
    calls = []

    class Response:
        status_code = 200
        text = ""

        def json(self):
            return {"success": True, "exception": None, "content": "test-user"}

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return Response()

    monkeypatch.setattr("requests.get", fake_get)

    result = _make_legality_client().verify_legality()

    assert result["success"] is True
    assert result["content"] == "test-user"
    assert calls[0][1]["params"] == {"access_token": "token-value"}


def test_general_chat_completion_resets_mood_after_final_analysis():
    calls = []

    class ProcessorStub:
        def consume_core_output(self, event):
            return []

        def reset(self):
            calls.append("processor.reset")

    class TalkSplitterStub:
        def announce_stop(self):
            return ["final"]

    class MoodStatusStub:
        def reset(self):
            calls.append("mood.reset")

    ai = type(
        "AiStub",
        (),
        {
            "_in_mspire": True,
            "pprt": False,
            "status": "connected",
            "TalkSpilter": TalkSplitterStub(),
            "MoodStatus": MoodStatusStub(),
            "add_ana": lambda self, content: calls.append(("add_ana", content)),
        },
    )()

    maica.MaicaAi.general_chat_callback(
        ai, ProcessorStub(), EventStub("maica_chat_loop_finished")
    )

    assert calls == [("add_ana", "final"), "mood.reset", "processor.reset"]
    assert ai.status == "connected"
    assert ai._in_mspire is False


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
        fixed_names = {
            maica_mtrigger.common_affection_template: "alter_affection",
        }
        if hasattr(maica_mtrigger, "memory_writeback_template"):
            fixed_names[maica_mtrigger.memory_writeback_template] = "write_memory"
        manager.add_trigger(
            _build_trigger(
                template,
                name=fixed_names.get(template, "trigger_{}".format(index)),
                exprop=_build_exprop(template),
            )
        )
    return manager.build_data(full=True)


def _last_json(manager):
    assert manager.ws_client.sent
    return json.loads(manager.ws_client.sent[-1])


def _task_event(name):
    return type(
        "TaskEvent",
        (),
        {
            "event_type": maica_tasker.MAICATASKEVENT_TYPE_TASK,
            "data": type("Data", (), {"name": name})(),
        },
    )()


def _new_mtrigger_handler(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    return maica_tasker_sub.MTriggerWsHandler(
        task_type=1,
        name="mtrigger_ws_handler",
        manager=ManagerStub(),
        except_ws_status=["maica_mtrigger"],
    )


def test_builtin_container_helpers_accept_plain_and_revertable_subclasses():
    class RevertableDict(dict):
        pass

    class RevertableList(list):
        pass

    assert maica_mtrigger.is_builtin_dict({})
    assert maica_mtrigger.is_builtin_dict(RevertableDict())
    assert not maica_mtrigger.is_builtin_dict([])
    assert maica_mtrigger.is_builtin_list([])
    assert maica_mtrigger.is_builtin_list(RevertableList())
    assert not maica_mtrigger.is_builtin_list({})


def _new_quality_handler(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    return maica_tasker_sub.QualityStatusWsHandler(
        task_type=1,
        name="quality_status_ws_handler",
        manager=ManagerStub(),
        except_ws_status=["maica_quality_status"],
    )


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


def test_mtrigger_ws_handler_dispatches_named_arguments_payload(monkeypatch):
    handler = _new_mtrigger_handler(monkeypatch)
    received = []
    handler.set_trigger_function(lambda name, arguments: received.append((name, arguments)))

    handler.on_received(
        EventStub("maica_mtrigger", {"name": "idle", "arguments": {}})
    )

    assert received == [("idle", {})]


def test_mtrigger_ws_handler_does_not_accept_legacy_mapping_payload(monkeypatch):
    handler = _new_mtrigger_handler(monkeypatch)
    received = []
    handler.set_trigger_function(lambda name, arguments: received.append((name, arguments)))

    handler.on_received(EventStub("maica_mtrigger", {"idle": {}}))

    assert received == []


@pytest.mark.parametrize(
    "content",
    [
        None,
        {"name": "idle"},
        {"name": 42, "arguments": {}},
        {"name": "idle", "arguments": []},
    ],
)
def test_mtrigger_ws_handler_rejects_malformed_payload(content, monkeypatch):
    handler = _new_mtrigger_handler(monkeypatch)
    received = []
    handler.set_trigger_function(lambda name, arguments: received.append((name, arguments)))

    handler.on_received(EventStub("maica_mtrigger", content))

    assert received == []


def test_quality_status_handler_queues_and_atomically_drains_results(monkeypatch):
    handler = _new_quality_handler(monkeypatch)

    handler.on_received(EventStub("maica_quality_status", [False, 0.9]))
    handler.on_received(EventStub("maica_quality_status", [True, 0]))

    assert handler.drain() == [(False, 0.9), (True, 0.0)]
    assert handler.drain() == []


@pytest.mark.parametrize(
    "content",
    [
        None,
        {},
        [False],
        [False, 0.5, "extra"],
        [0, 0.5],
        [False, True],
        [False, -0.1],
        [False, 1.1],
        [False, float("nan")],
        [False, float("inf")],
    ],
)
def test_quality_status_handler_rejects_malformed_payloads(content, monkeypatch):
    handler = _new_quality_handler(monkeypatch)

    handler.on_received(EventStub("maica_quality_status", content))

    assert handler.drain() == []


def test_quality_status_handler_reset_discards_stale_results(monkeypatch):
    handler = _new_quality_handler(monkeypatch)
    handler.on_received(EventStub("maica_quality_status", [False, 0.9]))

    handler.reset()

    assert handler.drain() == []


def test_common_affection_template_uses_alter_value_and_accepts_legacy_input():
    received = []
    trigger = maica_mtrigger.MTriggerBase(
        maica_mtrigger.common_affection_template,
        "alter_affection",
        callback=received.append,
    )

    assert maica_mtrigger.common_affection_template.datakey == "alter_value"
    trigger.triggered({"alter_value": 1.5})
    trigger.triggered({"affection": 0.5})
    assert received == [1.5, 0.5]


def test_fixed_name_templates_send_canonical_name_in_request_payload():
    affection = _build_trigger(
        maica_mtrigger.common_affection_template,
        name="alter_affection",
    )
    memory = _build_trigger(
        maica_mtrigger.memory_writeback_template,
        name="write_memory",
    )

    assert affection.build() == {
        "template": "common_affection_template",
        "name": "alter_affection",
    }
    assert memory.build() == {
        "template": "memory_writeback_template",
        "name": "write_memory",
    }


@pytest.mark.parametrize(
    ("template_name", "invalid_name"),
    [
        ("common_affection_template", "custom_affection"),
        ("memory_writeback_template", "custom_memory"),
    ],
)
def test_fixed_name_templates_reject_custom_names(template_name, invalid_name):
    template = getattr(maica_mtrigger, template_name)
    with pytest.raises(ValueError):
        _build_trigger(template, name=invalid_name).build()


def test_memory_template_extracts_memory_item():
    received = []
    trigger = maica_mtrigger.MTriggerBase(
        maica_mtrigger.memory_writeback_template,
        "write_memory",
        callback=received.append,
    )

    trigger.triggered({"memory_item": "{player_name} likes chocolate"})

    assert received == ["{player_name} likes chocolate"]


def test_memory_template_allows_only_one_trigger():
    assert len(_build_trigger_batch(maica_mtrigger.memory_writeback_template, 1)) == 1
    with pytest.raises(ValueError):
        _build_trigger_batch(maica_mtrigger.memory_writeback_template, 2)


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


def test_switch_allows_unknown_current_item_and_omits_curr_item():
    switch_data = _build_trigger(
        maica_mtrigger.common_switch_template,
        exprop=maica_mtrigger.MTriggerExprop(
            item_name_zh="选项", item_list=["one"], curr_value=None
        ),
    ).build()

    assert "curr_item" not in switch_data["exprop"]


def test_mtrigger_manager_skips_invalid_runtime_trigger_with_context(monkeypatch):
    messages = []

    class CaptureLogger:
        def warning(self, message):
            messages.append(message)

    monkeypatch.setattr(maica_mtrigger, "logger", CaptureLogger())
    manager = maica_mtrigger.MTriggerManager()
    manager.add_trigger(
        _build_trigger(
            maica_mtrigger.common_switch_template,
            name="bad_runtime",
            exprop=maica_mtrigger.MTriggerExprop(
                item_name_zh="选项",
                item_list=["ok", ""],
                curr_value="ok",
            ),
        )
    )
    manager.add_trigger(
        _build_trigger(
            maica_mtrigger.common_switch_template,
            name="good_runtime",
            exprop=maica_mtrigger.MTriggerExprop(
                item_name_zh="选项", item_list=["ok"], curr_value=None
            ),
        )
    )

    payload = manager.build_data(maica_mtrigger.MTriggerMethod.request, full=True)

    assert [item["name"] for item in payload] == ["good_runtime"]
    assert any(
        "name='bad_runtime'" in message
        and "phase=build" in message
        and "item_list entry at index 1" in message
        for message in messages
    )


def test_mtrigger_build_does_not_clear_queued_callbacks_or_running_state():
    manager = maica_mtrigger.MTriggerManager()
    trigger = _build_trigger(
        maica_mtrigger.customize_template,
        name="queued_build",
        exprop=maica_mtrigger.MTriggerExprop(item_name_zh="项目"),
    )
    manager.add_trigger(trigger)
    manager.triggered("queued_build", {})
    queued_before = list(manager.triggered_list)
    manager._running = True

    manager.build_data(maica_mtrigger.MTriggerMethod.request, full=True)

    assert manager.triggered_list == queued_before
    assert manager._running is True


def test_mtrigger_manager_skips_condition_failure_and_keeps_valid_trigger(monkeypatch):
    messages = []

    class CaptureLogger:
        def warning(self, message):
            messages.append(message)

    def failing_condition():
        raise RuntimeError("condition failed")

    monkeypatch.setattr(maica_mtrigger, "logger", CaptureLogger())
    manager = maica_mtrigger.MTriggerManager()
    manager.add_trigger(
        maica_mtrigger.MTriggerBase(
            maica_mtrigger.customize_template,
            "bad_condition",
            condition=failing_condition,
            exprop=maica_mtrigger.MTriggerExprop(item_name_zh="项目"),
        )
    )
    manager.add_trigger(
        _build_trigger(
            maica_mtrigger.customize_template,
            name="good_condition",
            exprop=maica_mtrigger.MTriggerExprop(item_name_zh="项目"),
        )
    )

    payload = manager.build_data(maica_mtrigger.MTriggerMethod.request, full=True)

    assert [item["name"] for item in payload] == ["good_condition"]
    assert any(
        "name='bad_condition'" in message
        and "phase=condition" in message
        and "condition failed" in message
        for message in messages
    )


def test_mtrigger_manager_skips_non_json_trigger_data_with_context(monkeypatch):
    messages = []

    class CaptureLogger:
        def warning(self, message):
            messages.append(message)

    class NonJsonTrigger(maica_mtrigger.MTriggerBase):
        def build(self):
            return {"name": self.name, "invalid": object()}

    monkeypatch.setattr(maica_mtrigger, "logger", CaptureLogger())
    manager = maica_mtrigger.MTriggerManager()
    manager.add_trigger(
        NonJsonTrigger(
            maica_mtrigger.customize_template,
            "non_json",
            exprop=maica_mtrigger.MTriggerExprop(item_name_zh="项目"),
        )
    )
    manager.add_trigger(
        _build_trigger(
            maica_mtrigger.customize_template,
            name="json_ok",
            exprop=maica_mtrigger.MTriggerExprop(item_name_zh="项目"),
        )
    )

    payload = manager.build_data(maica_mtrigger.MTriggerMethod.request, full=True)

    assert [item["name"] for item in payload] == ["json_ok"]
    assert any(
        "name='non_json'" in message
        and "phase=serialize" in message
        and "not JSON serializable" in message
        for message in messages
    )


@pytest.mark.parametrize(
    ("value", "reason"),
    [
        (None, "must be a string"),
        (False, "must be a string"),
        ("", "must not be empty"),
        ("x" * 257, "must be at most 256 characters"),
    ],
)
def test_dynamic_mtrigger_item_helper_rejects_invalid_values(value, reason):
    target = {"kept": 1}

    assert maica_mtrigger.add_valid_mtrigger_item(target, value, 2) == reason
    assert target == {"kept": 1}


def test_dynamic_mtrigger_item_helper_keeps_valid_items_and_rejects_duplicates():
    target = {}

    assert maica_mtrigger.add_valid_mtrigger_item(target, "valid", 1) is None
    assert maica_mtrigger.add_valid_mtrigger_item(target, "valid", 2) == "duplicate item name"
    assert target == {"valid": 1}


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
    data = _build_trigger(
        maica_mtrigger.customize_template,
        name="a",
        exprop=_build_exprop(maica_mtrigger.customize_template),
    ).build()
    assert data["name"] == "a"


@pytest.mark.parametrize("name", ["n" * 64, "valid_name", "valid-name"])
def test_mtrigger_accepts_valid_name_boundaries(name):
    data = _build_trigger(
        maica_mtrigger.customize_template,
        name=name,
        exprop=_build_exprop(maica_mtrigger.customize_template),
    ).build()
    assert data["name"] == name


@pytest.mark.parametrize("name", ["bad name", "n" * 65])
def test_mtrigger_rejects_invalid_names(name):
    with pytest.raises(ValueError):
        _build_trigger(
            maica_mtrigger.customize_template,
            name=name,
            exprop=_build_exprop(maica_mtrigger.customize_template),
        ).build()


def test_mtrigger_rejects_empty_name():
    with pytest.raises(ValueError):
        _build_trigger(
            maica_mtrigger.customize_template,
            name="",
            exprop=_build_exprop(maica_mtrigger.customize_template),
        ).build()


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
        maica_mtrigger.memory_writeback_template,
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
        name=maica_mtrigger.FIXED_TEMPLATE_NAMES.get(canonical.name, "trigger"),
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


def test_general_chat_preserves_unicode_until_websocket_serialization():
    root = Path(__file__).resolve().parents[1]
    maica_source = (root / "game" / "python-packages" / "maica.py").read_text(
        encoding="utf-8"
    )
    chat_block = maica_source.split("    def chat(self,", 1)[1].split(
        "    def start_raw_context", 1
    )[0]
    sender_source = (
        root
        / "game"
        / "python-packages"
        / "maica_tasker_sub_sessionsender.py"
    ).read_text(encoding="utf-8")
    process_block = sender_source.split(
        "    def process_request(self, query, session, triggers, taskowner", 1
    )[1].split("class MAICAMSpireProcessor", 1)[0]

    assert "message = str(message)" not in chat_block
    assert "decode_cp936" not in process_block


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


def test_hair_trigger_keeps_nonselectable_current_hair_out_of_choices():
    trigger_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "trigger.rpy"
    ).read_text(encoding="utf-8")
    hair_source = trigger_source.split(
        "    class HairTrigger(MTriggerBase):", 1
    )[1].split("    class AccessoryTrigger(MTriggerBase):", 1)[0]

    assert "HAIR_SEL_MAP[store.monika_chr.hair.name]" not in hair_source
    assert "HAIR_SEL_MAP.get(store.monika_chr.hair.name)" in hair_source
    assert "return None" in hair_source
    assert "if self.outfit_has_and_unlocked(key)" in hair_source
    assert "curr_value = self.current_item()" in hair_source
    assert "self.exprop.curr_value = self.current_item()" in hair_source


def test_builtin_dynamic_switch_sources_use_logged_item_filtering():
    trigger_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "trigger.rpy"
    ).read_text(encoding="utf-8")

    assert "def log_invalid_mtrigger(" in trigger_source
    assert "def _add_mtrigger_item(" in trigger_source
    assert "add_valid_mtrigger_item(target, display_name, mapped_value)" in trigger_source
    for source_name in (
        "store.mas_selspr.CLOTH_SEL_MAP",
        "store.mas_games.game_db",
        "store.mas_weather.WEATHER_MAP",
        "store.songs.music_choices",
        "store.mas_selspr.HAIR_SEL_MAP",
        "store.mas_selspr.ACS_SEL_MAP",
    ):
        assert source_name in trigger_source

    assert "trigger={} source={} key={} index={}" in trigger_source
    assert "type={} value={} reason={}" in trigger_source
    assert "reserved built-in item name" in trigger_source


def test_maica_namespace_container_guards_use_builtin_helpers():
    root = Path(__file__).resolve().parents[1]
    trigger_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "trigger.rpy"
    ).read_text(encoding="utf-8")
    api_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "api.rpy"
    ).read_text(encoding="utf-8")
    maica_block = api_source.split("init 5 python in maica:", 1)[1].split(
        "\ninit ", 1
    )[0]

    assert trigger_source.count("is_builtin_dict(data)") == 3
    assert "isinstance(data, dict)" not in trigger_source
    assert "from maica_mtrigger import is_builtin_dict, is_builtin_list" in maica_block
    assert "is_builtin_dict(store.persistent.maica_stat)" in maica_block
    assert "is_builtin_dict(store.persistent.maica_mtrigger_status)" in maica_block
    assert "is_builtin_list(store.persistent._maica_visuals)" in maica_block
    assert not re.search(r"(?<![\w.])persistent\b", maica_block)
    for legacy_guard in (
        "isinstance(postal, dict)",
        "isinstance(preview, dict)",
        "isinstance(other, dict)",
        "isinstance(other_preview, dict)",
    ):
        assert legacy_guard not in maica_block


def test_minigame_fixed_labels_take_precedence_over_mas_event_wrappers():
    trigger_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "trigger.rpy"
    ).read_text(encoding="utf-8")
    minigame_source = trigger_source.split("    def get_unlocked_games():", 1)[1].split(
        "    class MinigameTrigger(MTriggerBase):", 1
    )[0]

    dynamic_loop = minigame_source.index("for index, ev in enumerate(game_values):")
    assert minigame_source.index('"Pong", "game_pong"') < dynamic_loop
    assert minigame_source.index('"Hangman",\n                "game_hangman"') < dynamic_loop


def test_mtrigger_screen_builds_lengths_once_and_uses_cached_item_lengths():
    screen_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "screen_subs.rpy"
    ).read_text(encoding="utf-8")
    screen = screen_source.split("screen maica_triggers():", 1)[1]

    assert screen.count("maica_triggers.get_length(0)") == 1
    assert screen.count("maica_triggers.get_length(1)") == 1
    assert "len(trigger)" not in screen
    assert "get_trigger_length(trigger, use_cached=True)" in screen
    assert "get_trigger_state(trigger)" in screen
    assert "if trigger_condition_met:" in screen
    assert "trigger.condition()" not in screen


def test_mtrigger_manager_reports_condition_failures_as_inactive(monkeypatch):
    messages = []

    class CaptureLogger:
        def warning(self, message):
            messages.append(message)

    def failing_condition():
        raise RuntimeError("ui condition failed")

    monkeypatch.setattr(maica_mtrigger, "logger", CaptureLogger())
    manager = maica_mtrigger.MTriggerManager()
    trigger = maica_mtrigger.MTriggerBase(
        maica_mtrigger.customize_template,
        "ui_condition",
        condition=failing_condition,
        exprop=maica_mtrigger.MTriggerExprop(item_name_zh="项目"),
    )
    manager.add_trigger(trigger)

    assert manager.is_trigger_active(trigger) is False
    assert any(
        "name='ui_condition'" in message
        and "ui condition failed" in message
        for message in messages
    )


def test_mtrigger_manager_returns_enabled_and_condition_state_once():
    calls = []
    manager = maica_mtrigger.MTriggerManager()
    trigger = maica_mtrigger.MTriggerBase(
        maica_mtrigger.customize_template,
        "state_once",
        condition=lambda: calls.append(True) or True,
        exprop=maica_mtrigger.MTriggerExprop(item_name_zh="项目"),
    )
    manager.add_trigger(trigger)

    assert manager.get_trigger_state(trigger) == (True, True)
    assert calls == [True]


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


def test_mspire_search_type_is_forwarded():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    processor.process_request(["science"], 0, mspire_type="precise_page")
    assert _last_json(manager)["inspire"]["type"] == "precise_page"


@pytest.mark.parametrize(
    "search_type",
    ["not-a-search-mode", "percise_page", "in_percise_category"],
)
def test_mspire_rejects_unknown_search_type(search_type):
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", ManagerStub()
    )
    with pytest.raises(ValueError):
        processor.process_request(["science"], 0, mspire_type=search_type)


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


def test_mspire_cache_is_ignored_for_nonzero_session():
    manager = ManagerStub()
    processor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
        1, "mspire", manager
    )
    processor.process_request(["science"], 1, use_cache=True)
    assert _last_json(manager)["inspire"]["use_cache"] is False


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
    assert postmail["bypass_stream"] is True


def test_core_output_modes_are_explicit_and_accumulate_complete_responses():
    manager = ManagerStub()
    postal = maica_tasker_sub_sessionsender.MAICAMPostalProcessor(
        1, "mpostal", manager
    )
    assert postal.core_input_mode == maica_tasker_sub_sessionsender.CORE_INPUT_COMPLETE
    assert postal.core_output_mode == maica_tasker_sub_sessionsender.CORE_OUTPUT_COMPLETE
    assert postal.consume_core_output(EventStub("maica_core_streaming_continue", "first")) == []
    assert postal.consume_core_output(EventStub("maica_core_streaming_continue", "second")) == []
    assert postal.consume_core_output(EventStub("maica_chat_loop_finished")) == ["firstsecond"]

    chat = maica_tasker_sub_sessionsender.MAICAGeneralChatProcessor(
        1, "chat", manager
    )
    assert chat.consume_core_output(EventStub("maica_core_streaming_continue", "chunk")) == ["chunk"]


def test_maica_start_mspire_forwards_weight_and_cache_to_processor():
    class ProcessorRecorder(object):
        def __init__(self):
            self.kwargs = None

        def start_request(self, **kwargs):
            self.kwargs = kwargs

    class QualityStatusRecorder(object):
        def __init__(self):
            self.clear_count = 0

        def clear(self):
            self.clear_count += 1

    ai = object.__new__(maica.MaicaAi)
    ai._MaicaAi__accessable = True
    ai.is_ready_to_input = lambda: True
    ai.stat = {"mspire_count": 0}
    ai.MaicaAiStatus = maica.MaicaAi.MaicaAiStatus
    ai.MSpireProcessor = ProcessorRecorder()
    ai.QualityStatusTasker = QualityStatusRecorder()
    ai.mspire_category = ["science"]
    ai.mspire_session = 0
    ai.chat_session = 1
    ai.pprt = False
    ai.mspire_weight = 25
    ai.mspire_use_cache = True
    ai.mspire_type = "fuzzy_page"
    ai._in_mspire = False
    ai.status = ai.MaicaAiStatus.CONNECTED

    maica.MaicaAi.start_MSpire(ai)

    assert ai.MSpireProcessor.kwargs["ctg_weight"] == 25
    assert ai.MSpireProcessor.kwargs["use_cache"] is True
    assert ai.MSpireProcessor.kwargs["mspire_type"] == "fuzzy_page"
    assert ai.QualityStatusTasker.clear_count == 1
    assert ai.status == ai.MaicaAiStatus.CONNECTED


def test_login_payload_explicitly_identifies_auth_request(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    manager = ManagerStub()
    tasker = maica_tasker_sub.MAICALoginTasker(1, "login", manager)
    tasker.on_manual_run("token")
    assert _last_json(manager) == {"type": "auth", "access_token": "token"}


def test_maica_registers_current_websocket_status_contracts(isolated_maica_ai_globals):
    ai = maica.MaicaAi("account", "password")
    assert ai.MPostalProcessor.except_ws_status == [
        "maica_core_streaming_continue",
        "maica_chat_loop_finished",
    ]
    assert not hasattr(ai, "StreamingPacketValidator")
    assert ai.MTriggerTasker.except_ws_status == ["maica_mtrigger_trigger"]
    assert ai.QualityStatusTasker.except_ws_status == ["maica_quality_status"]
    loop_task = ai.task_manager.get_task("maicaloop_warn_handler")
    assert loop_task.except_ws_status == ["maica_loop_warn_reset"]


def test_init_connect_without_token_sets_explicit_failure(isolated_maica_ai_globals):
    ai = maica.MaicaAi("account", "password")
    ai._MaicaAi__accessable = True
    ai.status = ai.MaicaAiStatus.TOKEN_INVALID
    ai.ciphertext = ""

    assert ai.init_connect() is False
    assert ai.status == ai.MaicaAiStatus.TOKEN_MISSING
    assert ai.get_error_result()["status"] == "client_token_missing"
    assert ai.wss_thread is None


def test_init_connect_rechecks_sticky_disable_before_starting_thread(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai._MaicaAi__accessable = True
    ai.ciphertext = "token-value"

    def disable_during_token_check():
        ai.disable(ai.MaicaAiStatus.VERSION_OLD, sticky=True)
        return True

    ai.has_token = disable_during_token_check

    assert ai.init_connect() is False
    assert ai.wss_thread is None
    assert ai.status == ai.MaicaAiStatus.VERSION_OLD
    assert ai.is_accessable() is False


def test_init_connect_preserves_availability_failure_detail(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai.ciphertext = "token-value"
    ai._MaicaAi__accessable = False
    ai.set_error(
        "client_provider_unavailable",
        "provider lookup failed",
        fallback=ai.MaicaAiStatus.FAILED_GET_NODE,
    )

    assert ai.init_connect() is False
    assert ai.status == ai.MaicaAiStatus.FAILED_GET_NODE
    assert ai.error_protocol_status == "client_provider_unavailable"
    assert ai.error_message == "provider lookup failed"


def test_init_connect_without_token_preserves_availability_failure(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai.ciphertext = ""
    ai._MaicaAi__accessable = False
    ai.set_error(
        "client_provider_unavailable",
        "provider lookup failed",
        fallback=ai.MaicaAiStatus.FAILED_GET_NODE,
    )

    assert ai.init_connect() is False
    assert ai.status == ai.MaicaAiStatus.FAILED_GET_NODE
    assert ai.error_protocol_status == "client_provider_unavailable"
    assert ai.error_message == "provider lookup failed"


def test_init_connect_unknown_unavailability_is_connection_problem(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai.ciphertext = ""
    ai._MaicaAi__accessable = False
    ai.clear_error(ai.MaicaAiStatus.IDLE)

    assert ai.init_connect() is False
    assert ai.status == ai.MaicaAiStatus.CONNECT_PROBLEM
    assert ai.error_protocol_status == "client_availability_failed"


def test_init_connect_is_single_flight_and_clears_stale_state_before_start(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai.ciphertext = "token-value"
    ai._MaicaAi__accessable = True
    ai.Loginer.success = True
    ai.ChatProcessor.status = maica_tasker.MaicaTask.MAICATASK_STATUS_ERROR
    ai.ChatProcessor._request_timed_out = True
    started = threading.Event()
    release = threading.Event()

    def hold_connection_driver():
        started.set()
        release.wait(2.0)

    ai._init_connect = hold_connection_driver
    try:
        assert ai.init_connect() is True
        assert started.wait(1.0)
        connection_thread = ai.wss_thread
        assert ai.status == ai.MaicaAiStatus.WEBSOCKET_CONNECTING
        assert ai.error_protocol_status is None
        assert ai.Loginer.success is False
        assert ai.ChatProcessor.status == maica_tasker.MaicaTask.MAICATASK_STATUS_READY
        assert ai.response_timed_out() is False
        assert ai.is_connecting() is True

        assert ai.init_connect() is False
        assert ai.wss_thread is connection_thread
        assert ai.status == ai.MaicaAiStatus.WEBSOCKET_CONNECTING
        assert ai.error_protocol_status is None

        ai.set_error("client_network_error", "real connection failure")
        assert ai.is_failed() is True
        assert ai.is_connecting() is True
        assert ai.init_connect() is False
        assert ai.error_message == "real connection failure"
    finally:
        release.set()
        assert ai.wait_for_connection_shutdown(1.0)

    assert ai.wss_thread is None
    assert ai.is_connecting() is False


def test_ready_to_input_requires_transport_auth_and_idle_processor(
    isolated_maica_ai_globals, monkeypatch
):
    ai = maica.MaicaAi("account", "password")
    request_lock = threading.Lock()
    monkeypatch.setattr(
        maica_tasker_sub_sessionsender.SessionSenderAndReceiver,
        "multi_lock",
        request_lock,
    )
    ai.Loginer.success = True

    assert ai.is_ready_to_input() is False

    client = type("Client", (), {"keep_running": False})()
    ai.task_manager.ws_client = client
    assert ai.is_ready_to_input() is False

    client.keep_running = True
    assert ai.is_ready_to_input() is True

    request_lock.acquire()
    try:
        assert ai.is_ready_to_input() is False
    finally:
        request_lock.release()


def test_cancelled_connection_ignores_late_login_result(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai.status = ai.MaicaAiStatus.IDLE
    ai._connection_cancel_requested = True
    ai._connection_in_progress = True
    ai.Loginer.success = True

    ai._handle_login_result(True)

    assert ai.Loginer.success is False
    assert ai.status == ai.MaicaAiStatus.IDLE
    assert ai._connection_in_progress is True


def test_close_during_connection_is_intentional_and_does_not_set_13411(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai.ciphertext = "token-value"
    ai._MaicaAi__accessable = True
    ai.auto_reconnect = True
    started = threading.Event()
    stopped = threading.Event()

    class ConnectingClient:
        url = "wss://example.invalid/ws"

        def __init__(self):
            self.keep_running = False
            self.close_calls = 0

        def run_forever(self):
            self.keep_running = True
            started.set()
            stopped.wait(2.0)
            self.keep_running = False

        def close(self):
            self.close_calls += 1
            self.keep_running = False
            stopped.set()

    client = ConnectingClient()

    def init_ws_client():
        assert ai.multi_lock.acquire(False)
        ai.task_manager.ws_client = client
        ai.wss_session = client
        return True

    ai._init_ws_client = init_ws_client
    try:
        assert ai.init_connect() is True
        assert started.wait(1.0)
        assert ai.is_connecting() is True

        ai.close_wss_session()
        assert ai.wait_for_connection_shutdown(1.0)
    finally:
        stopped.set()
        ai.wait_for_connection_shutdown(1.0)
        if ai.multi_lock.locked():
            ai.multi_lock.release()

    assert client.close_calls == 1
    assert ai.status == ai.MaicaAiStatus.IDLE
    assert ai.error_protocol_status is None
    assert ai.Loginer.success is False
    assert ai.is_connecting() is False
    assert not ai.multi_lock.locked()


def test_init_connect_is_blocked_until_close_call_finishes(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai.ciphertext = "token-value"
    ai._MaicaAi__accessable = True
    close_started = threading.Event()
    allow_close = threading.Event()

    class ClosingClient:
        keep_running = False

        def close(self):
            close_started.set()
            allow_close.wait(2.0)

    ai.task_manager.ws_client = ClosingClient()
    close_thread = threading.Thread(target=ai.close_wss_session)
    close_thread.start()
    try:
        assert close_started.wait(1.0)
        assert ai.is_connecting() is True
        assert ai.init_connect() is False
        assert ai.wss_thread is None
        assert ai.status == ai.MaicaAiStatus.IDLE
    finally:
        allow_close.set()
        close_thread.join(1.0)

    assert not close_thread.is_alive()
    assert ai.is_connecting() is False


def test_token_generation_unavailability_survives_verification(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai._MaicaAi__accessable = False

    ai._gen_token("account", "password")
    result = ai._verify_token()

    assert ai.status == ai.MaicaAiStatus.CONNECT_PROBLEM
    assert result["status"] == "client_availability_failed"
    assert result["exception"] == "Maica server availability is unknown"


def test_ws_failure_dispatch_defers_login_errors_to_loginer(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai.Loginer.success = False

    assert (
        ai._handle_ws_failure("maica_unified_error", "pre-auth failure", 500)
        is False
    )
    assert ai.status == ai.MaicaAiStatus.WAIT_AVAILABILITY

    ai.Loginer.success = True
    assert ai._handle_ws_failure("maica_unified_error", "runtime failure", 500) is True
    assert ai.status == ai.MaicaAiStatus.SERVER_ERROR
    assert ai.error_message == "runtime failure"


def test_response_timeout_sets_unified_numeric_failure(isolated_maica_ai_globals):
    ai = maica.MaicaAi("account", "password")

    ai.ChatProcessor._timeout_callback("MAICAGeneralChatProcessor", 12.0)

    assert ai.status == ai.MaicaAiStatus.CONNECT_PROBLEM
    assert ai.get_error_result()["status"] == "client_response_timeout"
    assert "12.0 seconds" in ai.error_message


def test_intentional_close_clears_login_failure_state(isolated_maica_ai_globals):
    ai = maica.MaicaAi("account", "password")

    class Client:
        def __init__(self):
            self.close_calls = 0

        def close(self):
            self.close_calls += 1

    client = Client()
    ai.task_manager.ws_client = client
    ai.Loginer.success = True
    ai.set_error("client_network_error", "old failure")

    ai.close_wss_session()

    assert client.close_calls == 1
    assert ai.Loginer.success is False
    assert ai.status == ai.MaicaAiStatus.IDLE
    assert ai.get_error_result()["status"] is None
    assert client in ai._intentional_ws_closes


def test_close_without_transport_preserves_availability_failure(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai.set_error(
        "client_provider_unavailable",
        "provider lookup failed",
        fallback=ai.MaicaAiStatus.FAILED_GET_NODE,
    )

    ai.close_wss_session()

    assert ai.status == ai.MaicaAiStatus.FAILED_GET_NODE
    assert ai.error_protocol_status == "client_provider_unavailable"
    assert ai.error_message == "provider lookup failed"


def test_unexpected_close_sets_numeric_connection_failure(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")

    class Client:
        def close(self):
            pass

    client = Client()
    ai.Loginer.success = True
    ai.status = ai.MaicaAiStatus.CONNECTED

    ai._on_close(client, 1006, "network lost")

    assert ai.status == ai.MaicaAiStatus.CONNECT_PROBLEM
    assert ai.error_protocol_status == "client_connection_closed"
    assert ai.error_message == "network lost"


def test_maica_runtime_has_no_websocket_cookie_owner(isolated_maica_ai_globals):
    ai = maica.MaicaAi("account", "password")
    assert not hasattr(maica_tasker_sub, "MAICAWSCookiesHandler")
    assert not hasattr(ai, "WSCookiesTask")
    assert not hasattr(ai, "enable_strict_mode")


def test_savefile_access_marker_is_a_final_outbound_gate(
    isolated_maica_ai_globals, monkeypatch, tmp_path
):
    ai = maica.MaicaAi("account", "password")
    ai.savefile_access = True
    ai.modelconfig["savefile_access"] = True
    monkeypatch.setattr(maica, "basedir", str(tmp_path), raising=False)

    assert ai.build_setting_config()["chat_params"]["savefile_access"] is False
    assert ai.savefile_access is True
    assert ai.upload_save({}) == {
        "success": False,
        "exception": "savefile_access marker is missing",
    }

    (tmp_path / "savefile_access").write_text("enabled", encoding="utf-8")
    assert ai.build_setting_config()["chat_params"]["savefile_access"] is True

    ai.savefile_access = False
    assert ai.build_setting_config()["chat_params"]["savefile_access"] is False


def test_setting_payload_only_contains_allowlisted_selected_advanced_settings(
    isolated_maica_ai_globals, monkeypatch, tmp_path
):
    ai = maica.MaicaAi("account", "password")
    monkeypatch.setattr(maica, "basedir", str(tmp_path), raising=False)
    ai.modelconfig = {
        "temperature": 0.35,
        "unknown_legacy_setting": "must-not-leak",
        "mf_aggressive": True,
    }

    payload = ai.build_setting_config()
    advanced = set(payload["chat_params"]).intersection(
        maica_v13_migration.ADVANCED_SETTING_KEYS
    )

    assert payload["reset"] is True
    assert advanced == {"temperature"}
    assert payload["chat_params"]["temperature"] == 0.35
    assert "unknown_legacy_setting" not in payload["chat_params"]
    assert "mf_aggressive" not in payload["chat_params"]


def test_setting_payload_does_not_inject_advanced_defaults(
    isolated_maica_ai_globals, monkeypatch, tmp_path
):
    ai = maica.MaicaAi("account", "password")
    monkeypatch.setattr(maica, "basedir", str(tmp_path), raising=False)
    ai.modelconfig = {}

    params = ai.build_setting_config()["chat_params"]

    assert set(params).isdisjoint(maica_v13_migration.ADVANCED_SETTING_KEYS)


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


def test_auto_reconnector_deduplicates_pending_retry_and_disable_cancels_it(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    manager = ManagerStub()
    tasker = maica_tasker_sub.AutoReconnector(1, "reconnect", manager)
    reconnect_calls = []
    tasker.set_reconnect_func(lambda: reconnect_calls.append(True))
    tasker._reconnect_delay = 0.2
    tasker.enable()
    tasker.on_event(_task_event("maica_login_successful"))

    tasker.on_event(_task_event("websocket_closed"))
    pending_thread = tasker._reconnect_thread
    tasker.on_event(_task_event("websocket_closed"))

    assert tasker._reconnect_thread is pending_thread
    assert tasker._reconnect_attempts == 1
    tasker.disable()
    pending_thread.join(1.0)
    assert not pending_thread.is_alive()
    assert reconnect_calls == []


def test_auto_reconnector_stops_after_retry_limit_and_resets_on_login(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    manager = ManagerStub()
    tasker = maica_tasker_sub.AutoReconnector(1, "reconnect-limit", manager)
    reconnect_calls = []
    tasker.set_reconnect_func(lambda: reconnect_calls.append(True))
    tasker._reconnect_delay = 0.0
    tasker._max_reconnect_attempts = 2
    tasker.enable()
    tasker.on_event(_task_event("maica_login_successful"))

    for _index in range(2):
        tasker.on_event(_task_event("websocket_closed"))
        tasker._reconnect_thread.join(1.0)

    tasker.on_event(_task_event("websocket_closed"))
    assert reconnect_calls == [True, True]
    assert tasker._enabled is False
    assert any(
        getattr(getattr(event, "data", None), "name", None)
        == "auto_reconnector_give_up"
        for event in manager.events
    )

    tasker.enable()
    tasker._reconnect_attempts = 1
    tasker.on_event(_task_event("maica_login_successful"))
    assert tasker._reconnect_attempts == 0


def test_auto_reconnector_login_failure_cancels_pending_retry(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    tasker = maica_tasker_sub.AutoReconnector(1, "reconnect-auth", ManagerStub())
    reconnect_calls = []
    tasker.set_reconnect_func(lambda: reconnect_calls.append(True))
    tasker._reconnect_delay = 0.2
    tasker.enable()
    tasker.on_event(_task_event("maica_login_successful"))
    tasker.on_event(_task_event("websocket_closed"))
    pending_thread = tasker._reconnect_thread

    tasker.on_event(_task_event("maica_login_failed"))
    pending_thread.join(1.0)

    assert reconnect_calls == []
    assert tasker._enabled is False
    assert tasker._login_successful is False


def test_auto_resume_survives_error_reset_before_close(monkeypatch):
    monkeypatch.setattr(maica_tasker, "default_logger", NullLogger())
    manager = ManagerStub()
    tasker = maica_tasker_sub.AutoResumeTasker(
        1,
        "resume-error-close",
        manager,
        except_ws_status=["maica_mcore_gen_start", "maica_chat_loop_finished"],
    )
    tasker.enable()
    generation_event = type(
        "WsEvent",
        (),
        {
            "event_type": maica_tasker.MAICATASKEVENT_TYPE_WS,
            "data": type("Data", (), {"status": "maica_mcore_gen_start"})(),
        },
    )()

    tasker.on_event(generation_event)
    tasker.reset()  # MaicaTaskManager._ws_onerror
    tasker.on_event(_task_event("auto_reconnector_start_reconnect"))
    tasker.on_event(_task_event("websocket_closed"))
    tasker.reset()  # MaicaAi._init_connect
    tasker.on_event(_task_event("maica_login_successful"))

    assert [json.loads(payload) for payload in manager.ws_client.sent] == [
        {"type": "reconn"}
    ]


def test_auto_resume_has_no_redundant_predicate_api(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")

    assert not hasattr(ai, "_should_resume")
    assert not hasattr(ai.AutoResumeTasker, "set_should_resume_func")
    assert not hasattr(ai.AutoResumeTasker, "_should_resume_func")


def test_init_connect_does_not_run_or_release_an_existing_connection_lock(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai._MaicaAi__accessable = True

    class ExistingClient:
        def __init__(self, url):
            self.url = url
            self.run_calls = 0

        def run_forever(self):
            self.run_calls += 1

    existing_client = ExistingClient(ai.provider_manager.get_wssurl())
    ai.task_manager.ws_client = existing_client
    ai.multi_lock.acquire()
    try:
        ai._init_connect()
        assert existing_client.run_calls == 0
        assert ai.multi_lock.locked()
        assert ai.status != ai.MaicaAiStatus.CONNECT_PROBLEM
        assert ai.error_protocol_status is None
    finally:
        if ai.multi_lock.locked():
            ai.multi_lock.release()


def test_on_close_leaves_connection_lock_for_driver_finally(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")

    class ClosingClient:
        def __init__(self):
            self.close_calls = 0

        def close(self):
            self.close_calls += 1

    client = ClosingClient()
    ai.multi_lock.acquire()
    try:
        ai._on_close(client, 1006, "network lost")
        assert client.close_calls == 1
        assert ai.multi_lock.locked()
    finally:
        if ai.multi_lock.locked():
            ai.multi_lock.release()


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


def test_vista_delete_mutates_local_state_only_after_server_success(monkeypatch):
    manager = maica_vista_files_manager.MAICAVistaFilesManager(
        "https://example.test/api", "token"
    )
    manager.add("uuid-1")
    manager.add("uuid-2")
    manager.cloud_files = ["uuid-1", "uuid-2"]

    class ResponseStub:
        def __init__(self, payload):
            self.payload = payload

        def json(self):
            return self.payload

    responses = iter([
        ResponseStub({"success": False, "exception": "denied"}),
        ResponseStub({"success": True}),
        ResponseStub({"success": True}),
    ])
    calls = []

    def fake_delete(url, **kwargs):
        calls.append(kwargs)
        return next(responses)

    monkeypatch.setattr(maica_vista_files_manager.requests, "delete", fake_delete)
    with pytest.raises(Exception, match="denied"):
        manager.delete("uuid-1")
    assert manager.get_uuids() == ["uuid-2", "uuid-1"]
    assert manager.cloud_files == ["uuid-1", "uuid-2"]

    manager.delete(0)
    assert manager.get_uuids() == ["uuid-1"]
    assert manager.cloud_files == ["uuid-1"]
    assert calls[1]["json"]["content"] == "uuid-2"

    manager.delete()
    assert manager.get_uuids() == []
    assert manager.cloud_files == []


def test_session_sender_reraises_send_failure_and_releases_state():
    class FailingWsClient:
        def send(self, payload):
            raise IOError("send failed")

    manager = ManagerStub()
    manager.ws_client = FailingWsClient()
    processor = maica_tasker_sub_sessionsender.MAICAGeneralChatProcessor(
        1, "chat", manager
    )
    try:
        with pytest.raises(IOError, match="send failed"):
            processor.start_request(
                query="hello",
                session=0,
                triggers=[],
                taskowner=manager,
            )
        assert processor.processing is False
        assert processor.request_timed_out is False
        assert not maica_tasker_sub_sessionsender.SessionSenderAndReceiver.multi_lock.locked()
    finally:
        if maica_tasker_sub_sessionsender.SessionSenderAndReceiver.multi_lock.locked():
            maica_tasker_sub_sessionsender.SessionSenderAndReceiver.multi_lock.release()


def test_mutable_defaults_are_isolated_between_instances():
    first = maica_tasker.MaicaWSTask(1, "first")
    second = maica_tasker.MaicaWSTask(1, "second")
    first.except_ws_status.append("status")
    assert second.except_ws_status == []

    first_exprop = maica_mtrigger.MTriggerExprop()
    second_exprop = maica_mtrigger.MTriggerExprop()
    first_exprop.item_list.append("item")
    first_exprop.value_limits[0] = 10
    assert second_exprop.item_list == []
    assert second_exprop.value_limits == [0, 1]


def test_logger_sync_does_not_clear_root_handlers():
    manager = logger_manager.get_logger_manager()
    module = type("Module", (), {})()
    module.logger = manager.logger
    name = "test.root_logger_reference"
    manager.register_injected_reference(name, module, "logger")
    before = list(manager.logger.handlers)
    try:
        manager.set_log_level(logging.INFO)
        assert manager.logger.handlers == before
    finally:
        manager._injected_references.pop(name, None)
        manager.set_log_level(logging.DEBUG)


def test_logger_sync_does_not_copy_handlers_to_distinct_loggers():
    manager = logger_manager.get_logger_manager()
    if not isinstance(manager.logger, logging.Logger):
        pytest.skip("requires the stdlib fallback logger")

    child = logging.getLogger("test.distinct_logger")
    handlers_before = list(child.handlers)
    level_before = child.level
    propagate_before = child.propagate
    child_handler = logging.NullHandler()
    child.addHandler(child_handler)
    child.propagate = False
    module = type("Module", (), {})()
    module.logger = child
    name = "test.distinct_logger_reference"
    manager.register_injected_reference(name, module, "logger")
    try:
        manager.set_log_level(logging.INFO)
        assert child.handlers == handlers_before + [child_handler]
    finally:
        manager._injected_references.pop(name, None)
        for handler in list(child.handlers):
            child.removeHandler(handler)
            if handler not in handlers_before:
                handler.close()
        for handler in handlers_before:
            if handler not in child.handlers:
                child.addHandler(handler)
        child.setLevel(level_before)
        child.propagate = propagate_before
        manager.set_log_level(logging.DEBUG)


def test_accessable_preserves_sticky_version_disable_before_probe(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    provider_checks = []
    cached_version = {
        "success": True,
        "content": {"fe_blessland_version": "99.0.0"},
    }
    ai.version_info = cached_version
    ai.provider_manager.get_provider = lambda: provider_checks.append(True)
    ai.disable(ai.MaicaAiStatus.VERSION_OLD, sticky=True)

    ai.accessable()

    assert provider_checks == []
    assert ai.version_info is cached_version
    assert ai.status == ai.MaicaAiStatus.VERSION_OLD
    assert ai.is_accessable() is False


def test_accessable_rechecks_sticky_disable_before_committing_success(
    isolated_maica_ai_globals, monkeypatch
):
    ai = maica.MaicaAi("account", "password")
    ai.in_mas = False
    ai._MaicaAi__accessable = True

    class Provider:
        def get_provider(self):
            return True

        def get_api_url(self):
            return "https://backend.test/api"

    class Response:
        def json(self):
            assert ai.is_accessable() is False
            ai.disable(ai.MaicaAiStatus.VERSION_OLD, sticky=True)
            return {"success": True, "content": "serving"}

    ai.provider_manager = Provider()
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: Response())

    ai.accessable()

    assert ai.status == ai.MaicaAiStatus.VERSION_OLD
    assert ai.is_accessable() is False


def test_get_version_normalizes_server_and_invalid_response_failures(
    isolated_maica_ai_globals, monkeypatch
):
    ai = maica.MaicaAi("account", "password")

    class Provider:
        def get_api_url(self):
            return "https://backend.test/api"

    class Response:
        def __init__(self, status_code, payload):
            self.status_code = status_code
            self.payload = payload

        def json(self):
            if self.payload is None:
                raise ValueError("not JSON")
            return self.payload

    ai.provider_manager = Provider()
    responses = iter([
        Response(
            503,
            {
                "success": False,
                "exception": "maica_unified_error: maintenance",
            },
        ),
        Response(502, None),
    ])
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: next(responses))

    assert ai.get_version() == {
        "success": False,
        "status": "maica_unified_error",
        "exception": "maintenance",
        "code": 503,
    }
    assert ai.get_version() == {
        "success": False,
        "status": "client_response_invalid",
        "exception": "Version response was not valid JSON",
        "code": 502,
    }


def test_get_version_normalizes_network_failure(
    isolated_maica_ai_globals, monkeypatch
):
    ai = maica.MaicaAi("account", "password")
    monkeypatch.setattr(
        "requests.get",
        lambda *args, **kwargs: (_ for _ in ()).throw(IOError("offline")),
    )

    assert ai.get_version() == {
        "success": False,
        "status": "client_network_error",
        "exception": "Version request failed",
        "code": None,
    }


def test_accessable_caches_one_version_probe_before_defaults(
    isolated_maica_ai_globals, monkeypatch
):
    ai = maica.MaicaAi("account", "password")
    ai.in_mas = False

    class Provider:
        def get_provider(self):
            return True

        def get_api_url(self):
            return "https://backend.test/api"

    class Response:
        status_code = 200

        def __init__(self, payload):
            self.payload = payload

        def json(self):
            return self.payload

    version_info = {
        "success": True,
        "content": {"fe_blessland_version": "1.8.0"},
    }
    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        if url.endswith("/accessibility"):
            return Response({"success": True, "content": "serving"})
        if url.endswith("/version"):
            return Response(version_info)
        if url.endswith("/defaults"):
            return Response({"success": True, "content": {}})
        raise AssertionError("unexpected URL: {}".format(url))

    ai.provider_manager = Provider()
    monkeypatch.setattr("requests.get", fake_get)

    assert ai.accessable() is True
    assert ai.version_info is version_info
    assert calls == [
        "https://backend.test/api/accessibility",
        "https://backend.test/api/version",
        "https://backend.test/api/defaults",
    ]
    assert ai.error_protocol_status is None


def test_accessable_keeps_version_failure_separate_and_clears_stale_cache(
    isolated_maica_ai_globals, monkeypatch
):
    ai = maica.MaicaAi("account", "password")
    ai.in_mas = False

    class Provider:
        def get_provider(self):
            return True

        def get_api_url(self):
            return "https://backend.test/api"

    class Response:
        status_code = 200

        def __init__(self, payload):
            self.payload = payload

        def json(self):
            return self.payload

    version_failure = {
        "success": False,
        "status": "client_server_unavailable",
        "exception": "version unavailable",
    }

    def successful_access_get(url, **kwargs):
        if url.endswith("/accessibility"):
            return Response({"success": True, "content": "serving"})
        if url.endswith("/version"):
            return Response(version_failure)
        if url.endswith("/defaults"):
            return Response({"success": True, "content": {}})
        raise AssertionError("unexpected URL: {}".format(url))

    ai.provider_manager = Provider()
    monkeypatch.setattr("requests.get", successful_access_get)

    assert ai.accessable() is True
    assert ai.version_info == {
        "success": False,
        "status": "client_server_unavailable",
        "exception": "version unavailable",
        "code": 200,
    }
    assert ai.error_protocol_status is None

    monkeypatch.setattr(
        "requests.get",
        lambda *args, **kwargs: Response(
            {"success": True, "content": "maintenance"}
        ),
    )

    assert ai.accessable() is False
    assert ai.version_info == {"success": False, "content": {}}
    assert ai.status == ai.MaicaAiStatus.SERVER_MAINTAIN


def test_accessable_checks_backend_before_external_network(monkeypatch):
    ai = maica.MaicaAi.__new__(maica.MaicaAi)
    ai.in_mas = False
    ai.HTTP_TIMEOUT = (0.1, 0.1)
    ai._ignore_accessable = False
    ai._serving_status = None
    ai.status = None
    ai._MaicaAi__accessable = False

    class Provider:
        def __init__(self, available):
            self.available = available

        def get_provider(self):
            return self.available

        def set_provider_id(self, value):
            self._provider_id = value

        def get_provider_id(self):
            return self._provider_id

        def get_api_url(self):
            return "https://backend.test/api"

    checks = []
    ai.provider_manager = Provider(False)
    ai.provider_manager._provider_id = 1
    ai.can_access_internet = lambda: checks.append("network") or True
    ai.accessable()
    assert ai.status == ai.MaicaAiStatus.FAILED_GET_NODE
    assert ai.get_error_result()["status"] == "client_provider_unavailable"
    assert checks == ["network"]

    ai.provider_manager = Provider(True)
    ai.can_access_internet = lambda: False
    import requests
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: (_ for _ in ()).throw(IOError("offline")))
    ai.accessable()
    assert ai.status == ai.MaicaAiStatus.NO_INTERNET
    assert ai.get_error_result()["status"] == "client_no_internet"


def test_provider_refresh_routes_disconnected_failure_through_ai_status(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai.in_mas = False

    class Provider:
        def get_provider(self):
            assert ai.is_checking_availability() is True
            return False

        def get_provider_id(self):
            return 1

        def get_last_refresh_error(self):
            return {
                "status": "client_provider_unavailable",
                "exception": "catalog lookup failed",
                "code": None,
            }

    ai.provider_manager = Provider()
    ai.can_access_internet = lambda: True

    assert ai.refresh_provider_list() is False
    assert ai.status == ai.MaicaAiStatus.FAILED_GET_NODE
    assert ai.error_protocol_status == "client_provider_unavailable"
    assert ai.error_message == "catalog lookup failed"
    assert ai.is_checking_availability() is False


def test_provider_refresh_preserves_connected_runtime_status(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai._MaicaAi__accessable = True
    ai.status = ai.MaicaAiStatus.CONNECTED
    ai.task_manager.ws_client = type("ConnectedClient", (), {"keep_running": True})()

    class Provider:
        def get_provider(self):
            return False

        def get_last_refresh_error(self):
            return {
                "status": "client_provider_unavailable",
                "exception": "catalog refresh failed",
                "code": None,
            }

    ai.provider_manager = Provider()

    assert ai.refresh_provider_list() is False
    assert ai.status == ai.MaicaAiStatus.CONNECTED
    assert ai.is_accessable() is True
    assert ai.get_provider_refresh_error()["exception"] == "catalog refresh failed"
    assert ai.is_failed() is False


def test_provider_refresh_preserves_disconnected_authentication_error(
    isolated_maica_ai_globals,
):
    ai = maica.MaicaAi("account", "password")
    ai._MaicaAi__accessable = True
    ai.status = ai.MaicaAiStatus.TOKEN_INVALID
    ai.error_protocol_status = "maica_login_token_invalid"
    ai.error_message = "token rejected"

    class Provider:
        def get_provider(self):
            return False

        def get_last_refresh_error(self):
            return {
                "status": "client_provider_unavailable",
                "exception": "catalog refresh failed",
                "code": None,
            }

    ai.provider_manager = Provider()

    assert ai.refresh_provider_list() is False
    assert ai.status == ai.MaicaAiStatus.TOKEN_INVALID
    assert ai.error_protocol_status == "maica_login_token_invalid"
    assert ai.error_message == "token rejected"
    assert ai.get_provider_refresh_error()["exception"] == "catalog refresh failed"


def test_accessable_only_uses_maintenance_for_explicit_non_serving(monkeypatch):
    ai = maica.MaicaAi.__new__(maica.MaicaAi)
    ai.in_mas = False
    ai.HTTP_TIMEOUT = (0.1, 0.1)
    ai._ignore_accessable = False
    ai._serving_status = None
    ai.status = None
    ai._MaicaAi__accessable = False

    class Provider:
        def get_provider(self):
            return True

        def get_api_url(self):
            return "https://backend.test/api"

    class Response:
        def __init__(self, payload):
            self.payload = payload

        def json(self):
            return self.payload

    ai.provider_manager = Provider()
    payloads = iter(
        [
            {"success": True, "content": "maintenance"},
            {"success": False, "exception": "temporary gateway failure"},
        ]
    )
    import requests
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: Response(next(payloads)),
    )

    ai.accessable()
    assert ai.status == ai.MaicaAiStatus.SERVER_MAINTAIN
    assert ai.error_protocol_status == "client_server_unavailable"

    ai.accessable()
    assert ai.status == ai.MaicaAiStatus.CONNECT_PROBLEM
    assert ai.error_protocol_status == "client_availability_failed"


def test_check_certifi_loads_ca_bundle_without_network(monkeypatch):
    ai = maica.MaicaAi.__new__(maica.MaicaAi)
    ai.ping = lambda *args, **kwargs: pytest.fail(
        "certificate validation must not perform network probes"
    )

    assert ai.check_certifi() is True


def test_check_certifi_rejects_an_invalid_local_ca_bundle(monkeypatch, tmp_path):
    import certifi

    invalid_bundle = tmp_path / "cacert.pem"
    invalid_bundle.write_text("not a certificate", encoding="ascii")
    monkeypatch.setattr(certifi, "where", lambda: str(invalid_bundle))
    ai = maica.MaicaAi.__new__(maica.MaicaAi)

    assert ai.check_certifi() is False


def test_accessable_reports_network_failure_when_local_ca_bundle_is_valid(monkeypatch):
    import certifi
    import requests

    ai = maica.MaicaAi.__new__(maica.MaicaAi)
    ai.in_mas = True
    ai.HTTP_TIMEOUT = (0.1, 0.1)
    ai._ignore_accessable = False
    ai._serving_status = None
    ai.status = None
    ai._MaicaAi__accessable = False
    ai.can_access_internet = lambda: False
    monkeypatch.setattr(certifi, "set_parent_dir", lambda *args: None, raising=False)

    class Provider:
        def get_provider(self):
            return True

        def get_api_url(self):
            return "https://backend.test/api"

    ai.provider_manager = Provider()
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: (_ for _ in ()).throw(IOError("offline")),
    )

    ai.accessable()

    assert ai.status == ai.MaicaAiStatus.NO_INTERNET
    assert ai.error_protocol_status == "client_no_internet"


def test_accessable_reports_missing_certifi_module_as_certificate_failure(monkeypatch):
    ai = maica.MaicaAi.__new__(maica.MaicaAi)
    ai.in_mas = True
    ai.status = None
    ai._MaicaAi__accessable = False
    monkeypatch.setitem(sys.modules, "certifi", None)

    ai.accessable()

    assert ai.status == ai.MaicaAiStatus.CERTIFI_BROKEN
    assert ai.error_protocol_status == "client_certifi_broken"


def test_legality_ui_uses_canonical_coordinate_result_without_legacy_geocode():
    screen = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "screen_subs.rpy"
    ).read_text(encoding="utf-8")
    location_screen = screen.split("screen maica_location_input", 1)[1].split(
        "screen maica_addition_setting", 1
    )[0]
    assert "extract_legality_coordinates" in location_screen
    assert "latitude, longitude" in location_screen
    assert "format(latitude, longitude)" in location_screen
    assert "geocode" not in location_screen.lower()
    for legacy_key in ('get("lat"', 'get("lng"', 'get("lon"'):
        assert legacy_key not in location_screen


def test_setting_migration_renames_tristates_and_is_idempotent():
    values = {
        "sfe_aggressive": True,
        "prompt_pname_repl": False,
        "mf_sf_access_impl": False,
        "mf_const_sf_access": True,
        "memory_concl_arc": 2,
        "tnd_aggressive": 3,
        "mf_const_tools": 1,
        "max_length": 99999,
        "session_len_limit": 8192,
        "mspire_search_type": "percise_page",
        "ic_prep": True,
        "twk_super": True,
    }
    status = {
        "sfe_aggressive": True,
        "prompt_pname_repl": False,
        "ic_prep": True,
        "twk_super": True,
    }

    maica_v13_migration.migrate_setting_values(values, status)
    first = (dict(values), dict(status))
    maica_v13_migration.migrate_setting_values(values, status)

    assert (values, status) == first
    assert values["prompt_pname_repl"] is True
    assert status["prompt_pname_repl"] is True
    assert values["mf_sf_access_impl"] == 0
    assert values["mf_const_sf_access"] == 1
    assert values["memory_concl_arc"] == 2
    assert values["mf_const_tools"] == 2
    assert values["session_len_limit"] == 28672
    assert values["mspire_search_type"] == "precise_page"
    for old in maica_v13_migration.SETTING_RENAMES:
        assert old not in values
        assert old not in status
    for key in maica_v13_migration.RETIRED_PERSISTENT_SETTINGS:
        assert key not in values
        assert key not in status


def test_setting_migration_normalizes_legacy_mspire_search_types():
    for legacy, expected in maica_v13_migration.MSPIRE_SEARCH_TYPE_MIGRATIONS.items():
        values = {"mspire_search_type": legacy}
        maica_v13_migration.migrate_setting_values(
            values,
            fill_missing_tristates=False,
        )
        assert values == {"mspire_search_type": expected}


def test_setting_migration_defaults_invalid_and_missing_tristates_with_warnings():
    missing_values = {}
    maica_v13_migration.migrate_setting_values(missing_values)
    assert missing_values == {
        "mf_sf_access_impl": 1,
        "mf_const_sf_access": 0,
        "memory_concl_arc": 1,
    }

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
    assert values["mf_const_sf_access"] == 0
    assert values["memory_concl_arc"] == 1
    assert len(warnings) == 2
    assert "reset to 0" in warnings[1]


def test_outbound_settings_normalize_tristates_to_real_integers():
    normalized = maica.normalize_chat_params(
        {
            "mf_sf_access_impl": False,
            "mf_const_sf_access": True,
            "memory_concl_arc": "invalid",
        }
    )

    assert normalized["mf_sf_access_impl"] == 0
    assert normalized["mf_const_sf_access"] == 1
    assert normalized["memory_concl_arc"] == 1
    for key in maica_v13_migration.TRISTATE_SETTINGS:
        assert type(normalized[key]) is int


def test_outbound_settings_drop_retained_legacy_keys():
    params = {old: "legacy" for old in maica_v13_migration.SETTING_RENAMES}
    params.update(
        {
            "mf_const_tools": 1,
            "session_len_limit": 8192,
            "mt_extraction": True,
            "ic_prep": True,
            "twk_super": True,
        }
    )

    normalized = maica.normalize_chat_params(params)

    for old in maica_v13_migration.SETTING_RENAMES:
        assert old not in normalized
    assert "mt_extraction" not in normalized
    for key in maica_v13_migration.RETIRED_PERSISTENT_SETTINGS:
        assert key not in normalized


def test_outbound_normalization_does_not_create_missing_tristates():
    normalized = maica.normalize_chat_params({"temperature": 0.22})

    assert normalized == {"temperature": 0.22}


def test_advanced_setting_cleanup_removes_unknown_values_and_statuses():
    values = {
        "temperature": 0.35,
        "unknown_legacy_setting": "obsolete",
    }
    status = {
        "temperature": True,
        "unknown_legacy_setting": True,
        "orphan_status": True,
    }

    maica_v13_migration.cleanup_advanced_settings(values, status)

    assert values == {"temperature": 0.35}
    assert status == {"temperature": True}


def test_advanced_setting_filter_requires_a_local_enable_flag():
    values = {
        "temperature": 0.35,
        "top_p": 0.8,
        "unknown_legacy_setting": "obsolete",
    }
    status = {
        "temperature": False,
        "top_p": True,
        "unknown_legacy_setting": True,
    }

    filtered = maica_v13_migration.filter_advanced_settings(values, status)

    assert filtered == {"top_p": 0.8}


def test_general_setting_migration_does_not_inject_advanced_tristates():
    values = {"enable_mf": True}

    maica_v13_migration.migrate_setting_values(
        values,
        fill_missing_tristates=False,
    )

    assert values == {"enable_mf": True}


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


def test_get_message_normalizes_ellipsis_before_pause_processing():
    class MessageQueueStub:
        def __len__(self):
            return 1

        def get(self):
            return ["1eua", Ellipsis, False]

    class TalkSplitterStub:
        def add_pauses(self, value):
            if not isinstance(value, str):
                raise TypeError("message must be a string")
            return value

    ai = object.__new__(maica.MaicaAi)
    ai.message_list = MessageQueueStub()
    ai.TalkSpilter = TalkSplitterStub()

    message = ai.get_message()

    assert message[1] == "..."


def test_get_message_keeps_temperature_symbols_in_the_raw_message():
    class MessageQueueStub:
        def __len__(self):
            return 1

        def get(self):
            return ["1eua", "室温 21℃，体温 98.6℉", False]

    ai = object.__new__(maica.MaicaAi)
    ai.message_list = MessageQueueStub()

    message = ai.get_message()

    assert message[1] == "室温 21℃，体温 98.6℉"


def test_prepare_message_normalizes_values_in_raw_and_display_modes():
    class TalkSplitterStub:
        def add_pauses(self, value):
            return value + "{w=0.3}"

    ai = object.__new__(maica.MaicaAi)
    ai.TalkSpilter = TalkSplitterStub()

    assert ai.prepare_message_for_renpy(Ellipsis, escape_for_renpy=False) == "..."
    assert ai.prepare_message_for_renpy(12, escape_for_renpy=False) == "12"
    assert ai.prepare_message_for_renpy(Ellipsis) == "...{w=0.3}"
