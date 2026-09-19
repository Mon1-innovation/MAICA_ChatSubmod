"""Exercise trigger menus and Ren'Py call transfers without a running MAS game."""

import ast
import datetime
import re
import textwrap
from types import SimpleNamespace

import pytest

from test_mtrigger_dialogue_flow import _label_block, _source
import maica_mtrigger


YES = "Yes{#maica_host_yes}"
BRB = "Yes, I'll be right back"
CANCEL = "Nevermind{#maica_host_nevermind}"
STAY = "Not yet{#maica_host_not_yet}"
IDLE = "I'll be right back, leave the game open"
LEAVE = "I'm leaving for now, close the game please"
TAKEOUT = "I mean to take you with me"
ALONE = "I mean to go alone"


class Return(Exception):
    pass


class Jump(Exception):
    pass


class CallTransfer(Exception):
    """renpy.call abandons the current Python statement, including assignments."""


def _compile(body):
    lines = []
    options = []
    for line in body.splitlines():
        line = line[4:] if line.startswith("    ") else line
        statement = line.lstrip()
        indent = line[:len(line) - len(statement)]
        if not statement or statement.startswith("#"):
            continue
        if statement == "menu:":
            statement = "if True:"
        elif statement.startswith('"'):
            if statement.endswith(":"):
                option = ast.literal_eval(statement[:-1])
                options.append(option)
                statement = "if choice == {!r}:".format(option)
            else:
                statement = "pass"  # menu caption
        elif statement.startswith("$ "):
            statement = "_exec({!r})".format(statement[2:])
        elif statement.startswith("call "):
            match = re.fullmatch(r"call (\w+)(?:\((.*)\))?", statement)
            assert match, statement
            label, args = match.groups()
            statement = "_return = _call({!r}{})".format(
                label, ", " + args if args else ""
            )
        elif statement.startswith("jump "):
            statement = "raise Jump({!r})".format(statement[5:])
        elif statement == "return" or statement.startswith("return "):
            statement = "raise Return({})".format(statement[7:] or "None")
        elif re.match(r'(?:m|extend)(?: \w+)* "', statement):
            statement = "_say({})".format(statement[statement.index('"'):])
        elif statement.startswith("hide "):
            statement = "pass"
        else:
            assert statement.startswith(("if ", "elif ", "else:", "pass")), statement
        lines.append(indent + statement)
    return compile("\n".join(lines), "<trigger label>", "exec"), options


class Flow:
    def __init__(self, choice, takeout_result=None):
        self.calls = []
        self.queued = []
        self.console_visible = True
        self.takeout_result = takeout_result
        self.namespace = {
            "choice": choice,
            "_history_list": [],
            "persistent": SimpleNamespace(closed_self=False, _mas_idle_data={}),
            "MASEventList": SimpleNamespace(push=self.queued.append),
            "mas_clearNotifs": lambda: self.calls.append("mas_clearNotifs"),
            "mas_setupIdleMode": lambda *args: self.calls.append(("idle", args)),
            "mas_isMoniEnamored": lambda **kwargs: True,
            "mas_shouldKiss": lambda *args: True,
            "datetime": datetime,
            "renpy": SimpleNamespace(
                has_label=lambda label: True,
                random=SimpleNamespace(randint=lambda low, high: low),
            ),
            "store": SimpleNamespace(
                np_util=SimpleNamespace(
                    Music_Search=lambda keyword: self.calls.append(("search", keyword))
                )
            ),
            "weather": "rain",
            "keyword": "test song",
            "mtrigger_action": {"stop": False},
            "Return": Return,
            "Jump": Jump,
            "_call": self.host_call,
            "_say": lambda text: self.namespace["_history_list"].append(text),
            "_exec": self.execute,
        }
        labels = (
            "mtrigger_idle", "mtrigger_leave", "mtrigger_takeout",
            "mtrigger_weather(weather)", "mtrigger_location",
            "mtrigger_neteasemusic_search(keyword)", "mtrigger_backup",
            "mtrigger_kiss", "mtrigger_hold",
            "_mtrigger_start_idle", "_mtrigger_brb", "_mtrigger_idle_callback",
            "_mtrigger_leave", "_mtrigger_takeout", "_mtrigger_quit",
        )
        self.labels = {}
        for label in labels:
            block = _label_block(_source("trigger_labels.rpy"), label)
            self.labels[label.split("(")[0]] = _compile(block.split("\n", 1)[1])
        dispatcher = _label_block(_source("main.rpy"), "maica_run_mtriggers")
        self.labels[".next"] = _compile(dispatcher.split("label .next:\n")[1])

    def host_call(self, label, *args, **kwargs):
        self.calls.append(label)
        if label == "maica_hide_console":
            self.console_visible = False
        elif label == "maica_show_console":
            self.console_visible = True
        elif label == "bye_going_somewhere":
            return self.takeout_result

    def execute(self, code):
        try:
            exec(code, self.namespace)
        except CallTransfer as transfer:
            self.namespace["_return"] = self.run(transfer.args[0])

    def run(self, label):
        for _ in range(20):
            if label == "_quit":
                self.calls.append("_quit")
                return "quit"
            code, options = self.labels[label]
            if options:
                assert self.namespace["choice"] in options
            try:
                exec(code, self.namespace)
            except Jump as jump:
                label = jump.args[0]
            except Return as result:
                return result.args[0]
            else:
                pytest.fail("label fell through without returning: " + label)
        pytest.fail("trigger dialogue did not terminate")


@pytest.mark.parametrize(
    "label, choice",
    [
        ("mtrigger_idle", STAY),
        ("mtrigger_leave", CANCEL),
        ("mtrigger_takeout", CANCEL),
        ("mtrigger_weather", CANCEL),
        ("mtrigger_location", CANCEL),
        ("mtrigger_neteasemusic_search", CANCEL),
        ("mtrigger_backup", CANCEL),
    ],
)
def test_cancelling_restores_console_without_running_an_action(label, choice):
    flow = Flow(choice)
    assert flow.run(label) is None
    assert flow.console_visible
    assert flow.queued == []
    assert flow.calls == [
        "maica_pause_connection", "maica_hide_console", "maica_show_console",
    ]
    assert not flow.namespace["persistent"].closed_self


@pytest.mark.parametrize("label, choice", [("mtrigger_idle", BRB), ("mtrigger_leave", IDLE)])
def test_idle_is_queued_only_after_confirmation_and_keeps_the_return_callback(label, choice):
    flow = Flow(choice)
    assert flow.run(label) == "stop"
    assert not flow.console_visible
    assert flow.queued == ["_mtrigger_brb"]
    assert flow.namespace["persistent"]._mas_idle_data == {}

    assert flow.run(flow.queued.pop()) is None
    assert flow.namespace["persistent"]._mas_idle_data == {"mtrigger_idle": True}
    assert flow.calls[-1] == ("idle", ("mtrigger_idle", "_mtrigger_idle_callback"))
    assert flow.run("_mtrigger_idle_callback") is None
    assert flow.calls[-1] == "maica_reconnect"


@pytest.mark.parametrize(
    "label, choice",
    [("mtrigger_leave", YES), ("mtrigger_idle", LEAVE), ("mtrigger_takeout", ALONE)],
)
def test_leaving_uses_the_confirmed_quit_path(label, choice):
    flow = Flow(choice)
    assert flow.run(label) == "quit"
    assert flow.namespace["persistent"].closed_self
    assert flow.calls[-2:] == ["mas_clearNotifs", "_quit"]
    assert flow.queued == []
    assert "bye_going_somewhere" not in flow.calls


@pytest.mark.parametrize("label, choice", [("mtrigger_takeout", YES), ("mtrigger_leave", TAKEOUT)])
@pytest.mark.parametrize("host_result", [None, "quit"])
def test_takeout_respects_mas_cancellation_and_quit_results(label, choice, host_result):
    flow = Flow(choice, host_result)
    assert flow.run(label) == host_result
    assert flow.calls.count("bye_going_somewhere") == 1
    assert flow.namespace["persistent"].closed_self is (host_result == "quit")
    assert flow.console_visible is (host_result is None)
    assert flow.queued == []


@pytest.mark.parametrize(
    "label, effect",
    [
        ("mtrigger_weather", "mas_change_weather"),
        ("mtrigger_location", "monika_change_background"),
        ("mtrigger_neteasemusic_search", ("search", "test song")),
        ("mtrigger_backup", "extra_mas_backup"),
    ],
)
def test_new_confirmations_still_run_the_requested_action(label, effect):
    flow = Flow("Okay")
    assert flow.run(label) is None
    assert effect in flow.calls
    assert flow.console_visible


def _manager(callbacks):
    manager = maica_mtrigger.MTriggerManager()
    for index, callback in enumerate(callbacks):
        name = "test_{}".format(index)
        manager.add_trigger(maica_mtrigger.MTriggerBase(
            maica_mtrigger.customize_template, name, callback=callback,
            exprop=maica_mtrigger.MTriggerExprop(item_name_zh="item"),
            priority=len(callbacks) - index,
        ))
        manager.triggered(name, {})
    return manager


@pytest.mark.parametrize("choice, stopped", [(BRB, True), (STAY, False)])
def test_real_idle_callback_propagates_stop_only_when_the_menu_confirms(choice, stopped):
    flow = Flow(choice)
    source = _source("trigger.rpy")
    start = source.index("    def mtrigger_idle_callback(arg):")
    end = source.index("    idle_trigger =", start)

    def renpy_call(label):
        raise CallTransfer(label)

    callback_namespace = {
        "store": SimpleNamespace(renpy=SimpleNamespace(call=renpy_call)),
        "ai": SimpleNamespace(console_logger=SimpleNamespace(debug=lambda text: None)),
    }
    exec(textwrap.dedent(source[start:end]), callback_namespace)
    after = []
    manager = _manager([
        callback_namespace["mtrigger_idle_callback"],
        lambda _arg: after.append("next trigger"),
    ])
    flow.namespace["mtrigger_manager"] = manager
    assert flow.run(".next") == {"stop": stopped}
    assert manager.has_triggered() is stopped
    assert after == ([] if stopped else ["next trigger"])
    assert bool(flow.queued) is stopped
    assert flow.console_visible is not stopped


@pytest.mark.parametrize("callback_result", [None, "stop"])
def test_dispatcher_clears_stale_label_results_and_keeps_python_callback_results(callback_result):
    flow = Flow(CANCEL)
    flow.namespace["_return"] = "stop"
    flow.namespace["mtrigger_manager"] = _manager([lambda _arg: callback_result])
    assert flow.run(".next") == {"stop": callback_result == "stop"}


@pytest.mark.parametrize("label", ["mtrigger_kiss", "mtrigger_hold"])
@pytest.mark.parametrize("random_value", range(5))
def test_affection_cancellation_only_speaks_and_restores_console(label, random_value):
    flow = Flow(CANCEL)
    flow.namespace["renpy"].random.randint = lambda low, high: random_value
    assert flow.run(label) is None
    assert flow.console_visible
    assert flow.calls == [
        "maica_pause_connection", "maica_hide_console", "maica_show_console",
    ]


@pytest.mark.parametrize(
    "label, choice, actions",
    [
        ("mtrigger_kiss", "Kiss [m_name]", ["monika_kissing_motion_short"]),
        ("mtrigger_hold", "Hold [m_name]", [
            "monika_holdme_prep", "monika_holdme_start",
            "monika_holdme_reactions", "monika_holdme_end",
        ]),
    ],
)
def test_affection_confirmation_runs_the_action_then_restores_console(label, choice, actions):
    flow = Flow(choice)
    assert flow.run(label) is None
    assert flow.console_visible
    assert flow.calls == [
        "maica_pause_connection", "maica_hide_console",
    ] + actions + ["maica_show_console"]


def test_every_public_trigger_entry_has_a_confirmation_and_cancellation():
    source = _source("trigger_labels.rpy")
    public = re.findall(r"^label (mtrigger_\w+)(?:\([^\n]*\))?:", source, re.M)
    called = set(re.findall(r'renpy\.call\("(mtrigger_\w+)"', _source("trigger.rpy")))
    assert set(public) == called
    for name in public:
        match = re.search(r"^label " + name + r"[^:\n]*:", source, re.M)
        end = source.find("\nlabel ", match.end())
        block = source[match.end():end if end >= 0 else len(source)]
        assert "menu:" in block, name
        assert "{nw}" in block and "{fast}" in block, name
        assert CANCEL in block or STAY in block, name
    for name in re.findall(r"^\s+label \.(\w+):", source, re.M):
        assert name.startswith("_")
