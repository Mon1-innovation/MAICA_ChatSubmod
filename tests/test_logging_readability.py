from pathlib import Path
import sys


PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "game" / "python-packages"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

import maica
import maica_provider_manager
import maica_tasker
import maica_tasker_sub
import requests


class CaptureLogger(object):
    def __init__(self):
        self.records = []

    def _record(self, level, message, *args):
        if args:
            message = message % args
        self.records.append((level, message))

    def debug(self, message, *args, **kwargs):
        self._record("debug", message, *args)

    def info(self, message, *args, **kwargs):
        self._record("info", message, *args)

    def warning(self, message, *args, **kwargs):
        self._record("warning", message, *args)

    def error(self, message, *args, **kwargs):
        self._record("error", message, *args)


def ws_event(status, content, event_type="debug", code=200):
    return type(
        "WsEvent",
        (),
        {
            "event_type": maica_tasker.MAICATASKEVENT_TYPE_WS,
            "data": type(
                "Packet",
                (),
                {
                    "status": status,
                    "content": content,
                    "type": event_type,
                    "code": code,
                },
            )(),
        },
    )()


def test_general_websocket_logger_keeps_full_payload(monkeypatch):
    capture = CaptureLogger()
    monkeypatch.setattr(maica_tasker, "default_logger", capture)
    handler = maica_tasker_sub.GeneralWsLogger(1, "ws-log", None)

    handler.on_received(
        ws_event(
            "maica_core_streaming_continue",
            "diagnostic payload that must remain complete",
        )
    )

    assert capture.records == [
        (
            "debug",
            "[GeneralWsLogger] <maica_core_streaming_continue(200)> "
            "diagnostic payload that must remain complete",
        )
    ]


def test_connection_initiated_message_is_written_to_console():
    capture = CaptureLogger()
    handler = maica_tasker_sub.GeneralWsConsoleLogger(
        1,
        "ws-console",
        None,
        console_logger=capture,
    )

    handler.on_received(
        ws_event("maica_connection_initiated", "Chinese welcome|English welcome", "info")
    )

    assert capture.records == [
        ("info", "<maica_connection_initiated> English welcome")
    ]


def test_feature_switches_only_log_real_state_transitions(monkeypatch):
    capture = CaptureLogger()
    monkeypatch.setattr(maica_tasker, "default_logger", capture)
    taskers = (
        maica_tasker_sub.AutoReconnector(1, "reconnect", None),
        maica_tasker_sub.AutoResumeTasker(1, "resume", None),
        maica_tasker_sub.KeepWsAliveTasker(1, "keepalive", None),
    )

    for tasker in taskers:
        tasker.enable()
        tasker.enable()
        tasker.disable()
        tasker.disable()

    info_messages = [message for level, message in capture.records if level == "info"]
    assert info_messages == [
        "[AutoReconnector] auto-reconnect enabled",
        "[AutoReconnector] auto-reconnect disabled",
        "[AutoResumeTasker] auto-resume enabled",
        "[AutoResumeTasker] auto-resume disabled",
        "[KeepWsAliveTasker] keep-alive enabled",
        "[KeepWsAliveTasker] keep-alive disabled",
    ]


def test_unavailable_workload_refresh_is_silent(monkeypatch):
    capture = CaptureLogger()
    monkeypatch.setattr(maica, "logger", capture)
    ai = object.__new__(maica.MaicaAi)
    ai._MaicaAi__accessable = False

    assert ai.update_workload() is None
    assert capture.records == []


def test_repeated_workload_failure_logs_once(monkeypatch):
    capture = CaptureLogger()
    monkeypatch.setattr(maica, "logger", capture)

    def fail_get(*_args, **_kwargs):
        raise IOError("offline")

    monkeypatch.setattr(requests, "get", fail_get)
    ai = object.__new__(maica.MaicaAi)
    ai._MaicaAi__accessable = True
    ai._workload_failure_state = None
    ai.provider_manager = type(
        "ProviderManager", (), {"get_api_url": lambda self: "https://example.invalid"}
    )()

    for _index in range(2):
        thread = ai.update_workload()
        thread.join(1.0)

    warnings = [message for level, message in capture.records if level == "warning"]
    assert warnings == ["update_workload: GET /workload failed: offline"]


def test_unavailable_history_result_reports_client_state(monkeypatch):
    capture = CaptureLogger()
    monkeypatch.setattr(maica, "logger", capture)
    ai = object.__new__(maica.MaicaAi)
    ai._MaicaAi__accessable = False
    ai.status = ai.MaicaAiStatus.WAIT_AVAILABILITY
    ai.error_protocol_status = "availability_pending"
    ai.error_message = None
    ai.error_protocol_code = None

    result = ai.get_history()

    assert result == {
        "success": False,
        "content": [],
        "exception": "Checking service availability",
    }
    assert all(level != "error" for level, _message in capture.records)
    assert "not serving" not in " ".join(message for _level, message in capture.records).lower()
    assert "protocol_status=availability_pending" in capture.records[0][1]


def test_send_settings_can_skip_mtrigger_without_changing_default(monkeypatch):
    capture = CaptureLogger()
    monkeypatch.setattr(maica, "logger", capture)

    class Sender(object):
        def __init__(self):
            self.requests = []

        def start_event(self, request):
            self.requests.append(request)

    ai = object.__new__(maica.MaicaAi)
    ai.Loginer = type("Loginer", (), {"success": True})()
    ai.SettingSender = Sender()
    ai.is_connected = lambda: True
    ai.build_setting_config = lambda: {"type": "params", "reset": True}
    mtrigger_calls = []
    ai.send_mtrigger = lambda: mtrigger_calls.append(True)

    assert ai.send_settings(send_mtrigger=False) == {"type": "params", "reset": True}
    assert ai.SettingSender.requests == [{"type": "params", "reset": True}]
    assert mtrigger_calls == []

    assert ai.send_settings() == {"type": "params", "reset": True}
    assert ai.SettingSender.requests == [
        {"type": "params", "reset": True},
        {"type": "params", "reset": True},
    ]
    assert mtrigger_calls == [True]


def test_missing_provider_warning_is_not_repeated(monkeypatch):
    capture = CaptureLogger()
    monkeypatch.setattr(maica_provider_manager, "logger", capture)
    manager = maica_provider_manager.MaicaProviderManager(pid=404)

    first_url = manager.get_api_url()
    second_url = manager.get_api_url()

    assert first_url == second_url
    warnings = [message for level, message in capture.records if level == "warning"]
    assert len(warnings) == 1
    assert "404" in warnings[0]
    assert "fallback" in warnings[0].lower()


def test_provider_refresh_failure_preserves_last_good_catalog(monkeypatch):
    advertised_servers = [
        {
            "id": 1,
            "name": "Primary",
            "description": "Primary provider",
            "isOfficial": True,
            "portalPage": "https://example.invalid",
            "servingModel": "test-model",
            "modelLink": "",
            "wsInterface": "wss://example.invalid/websocket",
            "httpInterface": "https://example.invalid/api",
        }
    ]

    class Response:
        status_code = 200
        content = b""

        def json(self):
            return {
                "success": True,
                "content": {
                    "isMaicaNameServer": True,
                    "servers": advertised_servers,
                },
            }

    responses = iter(
        (Response(), requests.ConnectionError("catalog offline"), Response())
    )

    def get(*args, **kwargs):
        response = next(responses)
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(requests, "get", get)
    manager = maica_provider_manager.MaicaProviderManager(pid=1)

    assert manager.get_provider() is True
    catalog_before_failure = list(manager._servers)
    assert advertised_servers == [catalog_before_failure[0]]

    assert manager.get_provider() is False
    assert manager._servers == catalog_before_failure
    assert manager.is_refreshing() is False
    assert manager.get_last_refresh_error() == {
        "status": "client_provider_unavailable",
        "exception": "catalog offline",
        "code": None,
    }

    assert manager.get_provider() is True
    assert manager.get_last_refresh_error() is None
    assert manager._servers[0]["id"] == 1


def test_readability_cleanup_keeps_diagnostic_logging_boundary_documented():
    root = Path(__file__).resolve().parents[1]
    runtime = (root / "game" / "python-packages" / "maica.py").read_text(
        encoding="utf-8"
    )
    tasker = (root / "game" / "python-packages" / "maica_tasker_sub.py").read_text(
        encoding="utf-8"
    )
    sender = (
        root / "game" / "python-packages" / "maica_tasker_sub_sessionsender.py"
    ).read_text(encoding="utf-8")
    main = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "main.rpy"
    ).read_text(encoding="utf-8")
    raw_session = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "raw_session_example.rpy"
    ).read_text(encoding="utf-8")
    report = (root / "docs" / "codex" / "logging-privacy-risk.md").read_text(
        encoding="utf-8"
    )

    assert "Maica is not serving" not in runtime
    assert "Maica server not serving" not in runtime
    assert "You should connected" not in runtime
    assert "sended" not in tasker
    assert "start_request error" not in sender
    assert "current triggers:" not in main
    assert "label maica_talking::message:" not in main
    assert "label maica_mpostal_read::message:" not in main
    assert "label maica_raw_session::message:" not in raw_session
    assert "完整 WebSocket" in report
    assert "不脱敏" in report
