"""Execute the MPostal script branches with mocked I/O, without a MAS install.

The small adapter below handles only the Ren'Py statements used by these labels.
Python blocks, conditions and state changes come directly from the .rpy files.
"""

import inspect
import re
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "game" / "python-packages"))
from maica import MaicaAi

SCRIPTS = ROOT / "game" / "Submods" / "MAICA_ChatSubmod"
CHAT = (SCRIPTS / "chat.rpy").read_text(encoding="utf-8")
MAIN = (SCRIPTS / "main.rpy").read_text(encoding="utf-8")
API = (SCRIPTS / "api.rpy").read_text(encoding="utf-8")


class LabelReturn(Exception):
    pass


class LabelJump(Exception):
    pass


def compile_label(body):
    output = []
    python_indent = None
    condition_open = False
    for line in body.splitlines():
        line = line[4:] if line.startswith("    ") else line
        statement = line.lstrip()
        indent = len(line) - len(statement)
        if not statement or statement.startswith("#"):
            output.append(line)
            continue
        if python_indent is not None and indent > python_indent:
            output.append(line)
            continue
        python_indent = None
        if condition_open:
            output.append(line)
            condition_open = not statement.endswith(":")
            continue
        if statement == "python:":
            python_indent = indent
            statement = "if True:"
        elif statement.startswith("$ "):
            statement = statement[2:]
        elif statement.startswith("call "):
            match = re.fullmatch(r"call ([\w.]+)(?:\((.*)\))?", statement)
            assert match, statement
            target, args = match.groups()
            statement = "_return = _call({!r}{})".format(
                target, ", " + args if args else ""
            )
        elif statement.startswith("jump "):
            statement = "raise LabelJump({!r})".format(statement[5:])
        elif statement == "return" or statement.startswith("return "):
            statement = "raise LabelReturn({})".format(statement[7:] or "None")
        elif re.match(r'm(?: \w+)* "', statement):
            literal = statement[statement.index('"'):]
            # Comments after a Say statement must stay outside the call.
            literal = re.match(r'"(?:[^"\\]|\\.)*"', literal).group()
            statement = "_say({})".format(literal)
        elif statement.startswith(("show ", "hide ", "window ")):
            statement = "_visual({!r})".format(statement)
        else:
            assert statement.startswith(("if ", "elif ", "else:")), statement
            condition_open = not statement.endswith(":")
        output.append(" " * indent + statement)
    return compile("\n".join(output), "<mpostal label>", "exec")


def load_function(source, name, namespace):
    match = re.search(r"^    def " + name + r"\(.*", source, re.M)
    assert match, name
    lines = source[match.start():].splitlines()
    end = next(
        (i for i, line in enumerate(lines[1:], 1)
         if line.strip() and len(line) - len(line.lstrip()) <= 4), len(lines)
    )
    exec(textwrap.dedent("\n".join(lines[:end])), namespace)


class Flow:
    def __init__(self, namespace, stubs):
        self.namespace = namespace
        self.stubs = stubs
        self.labels = {}
        self.steps = 0
        namespace.update(_call=self.call, LabelReturn=LabelReturn, LabelJump=LabelJump)
        for source, prefix in ((MAIN, "maica_mpostal_read"), (CHAT, "maica_mpostal_replyed"),
                               (CHAT, "maica_connection_failure_dialogue")):
            matches = list(re.finditer(r"^label ([\w.]+)(\([^\n]*\))?:.*$", source, re.M))
            for i, match in enumerate(matches):
                if not match[1].startswith(prefix):
                    continue
                end = matches[i + 1].start() if i + 1 < len(matches) else len(source)
                signature = inspect.signature(eval("lambda {}: None".format(
                    match[2][1:-1] if match[2] else ""
                )))
                self.labels[match[1]] = (
                    compile_label(source[match.end() + 1:end]), signature,
                    matches[i + 1][1] if i + 1 < len(matches) else None,
                )

    def call(self, name, *args, **kwargs):
        if name in self.stubs:
            return self.stubs[name](*args, **kwargs)
        signature = self.labels[name][1]
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        missing = object()
        saved = {key: self.namespace.get(key, missing) for key in bound.arguments}
        self.namespace.update(bound.arguments)
        try:
            while name:
                self.steps += 1
                assert self.steps < 150, "MPostal kept retrying inside one dialogue"
                code, _, next_name = self.labels[name]
                try:
                    exec(code, self.namespace)
                except LabelJump as jump:
                    name = jump.args[0]
                    continue
                name = next_name
        except LabelReturn as result:
            return result.args[0]
        finally:
            for key, value in saved.items():
                if value is missing:
                    self.namespace.pop(key, None)
                else:
                    self.namespace[key] = value


class FakeAI:
    MaicaAiStatus = MaicaAi.MaicaAiStatus
    gen_time = 0

    def __init__(self, outcomes):
        self.outcomes = outcomes
        self.started = []
        self.queue = []
        self.status = self.MaicaAiStatus.CONNECTED
        self.error_protocol_status = None
        self.error_protocol_code = None
        self.error_message = None
        self.console_logger = Mock()

    def start_MPostal(self, content, title, visions):
        self.started.append(title)
        outcome = self.outcomes.get(title, "success")
        self.status = self.MaicaAiStatus.CONNECTED
        self.error_protocol_status = self.error_message = self.error_protocol_code = None
        if outcome in ("response", "partial"):
            self.status = self.MaicaAiStatus.SERVER_REJECTED
            self.error_protocol_status = "maica_loop_warn_reset"
            self.error_protocol_code = 500
            self.error_message = "generation failed"
        if outcome in ("success", "partial"):
            self.queue = [(None, "reply:" + title)]

    def fail_connection(self):
        self.status = self.MaicaAiStatus.CONNECT_PROBLEM
        self.error_protocol_status = "client_response_timeout"
        self.error_protocol_code = 500
        self.error_message = "timed out"

    def is_responding(self):
        return False

    def is_failed(self):
        return self.MaicaAiStatus.is_submod_exception(self.status)

    def len_message_queue(self):
        return len(self.queue)

    def get_message(self):
        return self.queue.pop(0)


def postal(title="a", count=0, status="notupload", image=False):
    return dict(raw_title=title, raw_content="letter", raw_image=title if image else None,
                responsed_content="", responsed_status=status, failed_count=count, time="1")


@pytest.fixture
def harness(monkeypatch):
    clock = [100000.0]
    monkeypatch.setattr("time.time", lambda: clock[0])

    def build(postals, outcomes=None, connection="success", console=False):
        ai = FakeAI(outcomes or {})
        dialogue, visuals, shown, deleted = [], [], [], []
        persistent = SimpleNamespace(
            _maica_send_or_received_mpostals=postals,
            maica_setting_dict={"mpostal_default_reply_time": 10,
                                "show_console_when_reply": console}, sessions={},
        )

        def connect(**kwargs):
            if connection != "success":
                ai.fail_connection()
            return connection

        def upload(_path):
            raise IOError("attachment upload failed")

        namespace = dict(
            persistent=persistent,
            store=SimpleNamespace(maica=SimpleNamespace(
                maica_instance=ai, upload_vista_image=upload,
                delete_mpostal_original=lambda item: deleted.append(item["raw_title"])),
                mas_submod_utils=SimpleNamespace(submod_log=Mock()), mas_ptod=Mock()),
            renpy=SimpleNamespace(dynamic=lambda *args: None, pause=lambda *args: None,
                                  substitute=lambda text: text),
            mas_HKBRaiseShield=lambda: None,
            mas_getEV=lambda name: SimpleNamespace(shown_count=0),
            _=lambda text: text, _say=dialogue.append, _visual=visuals.append,
        )
        for source, name in ((CHAT, "maica_retry_mpostal"), (CHAT, "is_mail_waiting_reply"),
                             (CHAT, "mpostal_delaying_check_and_set"), (API, "has_mail_waitsend")):
            load_function(source, name, namespace)
        hide_console = Mock(return_value=None)
        flow = Flow(namespace, {
            "maica_init_connect": connect, "maica_mpostal_load": lambda: None,
            "maica_hide_console": hide_console, "maica_show_console": lambda: None,
            "maica_mpostal_show": shown.append,
        })
        return SimpleNamespace(flow=flow, namespace=namespace, ai=ai, clock=clock,
                               dialogue=dialogue, visuals=visuals, shown=shown,
                               deleted=deleted, hide_console=hide_console)
    return build


@pytest.mark.parametrize("failure", ["setup", "response", "empty", "partial", "disconnected"])
@pytest.mark.parametrize("count", [0, 1, 2])
def test_each_failure_is_counted_once_and_third_failure_remains_pending(harness, failure, count):
    letter = postal(count=count, image=failure == "setup")
    h = harness([letter], {"a": failure}, connection="disconnected" if failure == "disconnected" else "success")
    assert h.flow.call("maica_mpostal_read") == "failed"
    assert letter["failed_count"] == count + 1
    assert letter["responsed_status"] == ("newfatal" if count == 2 else "failed")
    assert h.namespace["is_mail_waiting_reply"]()
    assert not h.namespace["has_mail_waitsend"]()
    assert h.deleted == []
    h.hide_console.assert_called_once()


@pytest.mark.parametrize("connection", ["disconnected", None, "failed"])
@pytest.mark.parametrize("console", [False, True])
def test_connection_failure_gets_cleanup_dialogue_and_delayed_retry(harness, connection, console):
    letters = [postal("a"), postal("b")]
    h = harness(letters, connection=connection, console=console)
    assert h.flow.call("maica_mpostal_replyed") == "no_unlock"
    assert [letter["responsed_status"] for letter in letters] == ["delaying", "delaying"]
    assert [letter["failed_count"] for letter in letters] == [1, 1]
    assert all(letter["retry_after"] == h.clock[0] + 600 for letter in letters)
    assert all(letter["time"] == "1" for letter in letters)
    assert h.ai.started == [] and h.shown == []
    assert any("connected to the internet" in line for line in h.dialogue)
    assert not any("Hope you like" in line or "hope it's not too bad" in line for line in h.dialogue)
    assert "hide black with dissolve" in h.visuals
    h.hide_console.assert_called_once()
    h.namespace["mpostal_delaying_check_and_set"]()
    assert not h.namespace["has_mail_waitsend"]()
    h.clock[0] += 600
    h.namespace["mpostal_delaying_check_and_set"]()
    assert h.namespace["has_mail_waitsend"]() == 2


@pytest.mark.parametrize("order", [("a", "b"), ("b", "a")])
@pytest.mark.parametrize("failure", ["setup", "response", "partial"])
@pytest.mark.parametrize("read_first", [False, True])
def test_mixed_batch_never_reads_the_failed_letter(harness, order, failure, read_first):
    letters = [postal(name, image=name == "a" and failure == "setup") for name in order]
    h = harness(letters, {"a": failure})
    if read_first:
        assert h.flow.call("maica_mpostal_read") == "failed"
    assert h.flow.call("maica_mpostal_replyed") == "no_unlock"
    by_title = {letter["raw_title"]: letter for letter in letters}
    assert by_title["a"]["responsed_status"] == "delaying"
    assert by_title["b"]["responsed_status"] == "readed"
    assert h.shown == ["reply:b"] and h.deleted == ["b"]
    if failure == "setup":
        assert by_title["a"]["failure_status"] is None
    else:
        assert by_title["a"]["failure_status"] == h.ai.MaicaAiStatus.SERVER_REJECTED
        assert by_title["a"]["failure_message"] == "generation failed"
        assert by_title["a"]["failure_protocol_status"] == "maica_loop_warn_reset"
        assert by_title["a"]["failure_protocol_code"] == 500
        assert not any("Something unknown" in line for line in h.dialogue)


@pytest.mark.parametrize("read_first", [False, True])
def test_fatal_transition_notifies_once_and_does_not_block_other_letters(harness, read_first):
    failed, success = postal("a", count=2, image=True), postal("b")
    h = harness([failed, success])
    if read_first:
        assert h.flow.call("maica_mpostal_read") == "failed"
        assert failed["responsed_status"] == "newfatal"
        assert success["responsed_status"] == "received"
    h.flow.call("maica_mpostal_replyed")
    assert failed["responsed_status"] == "fatal"
    assert success["responsed_status"] == "readed"
    assert h.shown == ["reply:b"]
    assert sum("Resend mail" in line for line in h.dialogue) == 1
    assert not h.namespace["is_mail_waiting_reply"]()
    h.flow.call("maica_mpostal_replyed")
    assert sum("Resend mail" in line for line in h.dialogue) == 1
    h.namespace["maica_retry_mpostal"](failed, reset_count=True)
    assert failed["failed_count"] == 0 and failed["responsed_status"] == "delaying"


def test_three_failures_each_wait_for_acknowledgement_and_retry_interval(harness):
    letter = postal(image=True)
    h = harness([letter])
    for count in (1, 2, 3):
        assert h.namespace["has_mail_waitsend"]() == 1
        assert h.flow.call("maica_mpostal_read") == "failed"
        assert letter["failed_count"] == count
        assert not h.namespace["has_mail_waitsend"]()
        assert h.namespace["is_mail_waiting_reply"]()
        h.flow.call("maica_mpostal_replyed")
        assert not h.namespace["is_mail_waiting_reply"]()
        assert not h.namespace["has_mail_waitsend"]()
        h.clock[0] += 599
        h.namespace["mpostal_delaying_check_and_set"]()
        assert not h.namespace["has_mail_waitsend"]()
        h.clock[0] += 1
        h.namespace["mpostal_delaying_check_and_set"]()
        assert letter["responsed_status"] == ("fatal" if count == 3 else "notupload")
        assert "retry_after" not in letter
        assert letter["time"] == "1"
    assert sum("Resend mail" in line for line in h.dialogue) == 1
    assert h.shown == [] and h.deleted == []


def test_unacknowledged_failure_cannot_exhaust_retries(harness):
    letter = postal(image=True)
    h = harness([letter])
    h.flow.call("maica_mpostal_read")
    for _ in range(3):
        h.namespace["mpostal_delaying_check_and_set"]()
        assert not h.namespace["has_mail_waitsend"]()
        h.flow.call("maica_mpostal_read")  # Even a duplicate queued read skips failed.
    assert letter["failed_count"] == 1 and letter["responsed_status"] == "failed"


def test_local_setup_error_does_not_borrow_previous_ai_error(harness):
    letter = postal(image=True)
    h = harness([letter])
    h.ai.fail_connection()  # Previous request's error must not describe this upload.
    h.flow.call("maica_mpostal_read")
    assert letter["failure_status"] is None
    assert letter["failure_message"] == "attachment upload failed"
    h.flow.call("maica_mpostal_replyed")
    assert any("Something unknown" in line for line in h.dialogue)
    assert not any("connected to the internet" in line for line in h.dialogue)


def test_legacy_failed_letter_keeps_current_status_fallback(harness):
    letter = postal(status="failed")
    h = harness([letter])
    h.ai.fail_connection()
    h.flow.call("maica_mpostal_replyed")
    assert any("connected to the internet" in line for line in h.dialogue)


def test_success_result_survives_console_cleanup(harness):
    letter = postal()
    h = harness([letter])
    assert h.flow.call("maica_mpostal_read") == "success"
    assert letter["responsed_status"] == "received"
    assert letter["failed_count"] == 0
    h.hide_console.assert_called_once()
