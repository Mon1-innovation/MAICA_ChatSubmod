import re
import sys
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBMOD = ROOT / "game" / "Submods" / "MAICA_ChatSubmod"
HEADER = (SUBMOD / "header.rpy").read_text(encoding="utf-8")
API = (SUBMOD / "api.rpy").read_text(encoding="utf-8")
PACKAGE_ROOT = ROOT / "game" / "python-packages"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from maica_vista_files_manager import MAICAVistaFilesManager

EARLY_CONTAINERS = {
    "maica_setting_dict": dict,
    "maica_advanced_setting": dict,
    "maica_advanced_setting_status": dict,
    "mas_player_additions": list,
    "_maica_send_or_received_mpostals": list,
    "_maica_visuals": list,
}


def default_priority(source, name):
    match = re.search(
        r"(?m)^default(?:\s+(-?\d+))?\s+persistent\.{}\s*=".format(
            re.escape(name)
        ),
        source,
    )
    assert match, "missing persistent default: {}".format(name)
    return int(match.group(1) or 0)


def init_python_body(source, priority):
    lines = source.splitlines()
    marker = "init {} python:".format(priority)
    start = next(index for index, line in enumerate(lines) if line == marker) + 1
    body = []
    for line in lines[start:]:
        if line and not line.startswith((" ", "\t")):
            break
        body.append(line)
    return textwrap.dedent("\n".join(body))


def iter_init_python_blocks(source):
    lines = source.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^init(?:\s+(-?\d+))?\s+python(?:\s+in\s+\w+)?:$", line)
        if not match:
            continue
        body = []
        for body_line in lines[index + 1:]:
            if body_line and not body_line.startswith((" ", "\t")):
                break
            body.append(body_line)
        yield int(match.group(1) or 0), "\n".join(body)


def test_container_defaults_run_before_every_consumer():
    repair_priority = -1498
    for name in EARLY_CONTAINERS:
        owner = HEADER if "persistent.{}".format(name) in HEADER else API
        assert default_priority(owner, name) < repair_priority

    for path in SUBMOD.glob("*.rpy"):
        source = path.read_text(encoding="utf-8")
        for priority, body in iter_init_python_blocks(source):
            if path.name == "header.rpy" and priority == repair_priority:
                continue
            if priority <= repair_priority:
                for name in EARLY_CONTAINERS:
                    assert "persistent.{}".format(name) not in body

    forest = (SUBMOD / "heaven_forest.rpy").read_text(encoding="utf-8")
    assert "init -1 python:" in forest
    assert "persistent.maica_setting_dict.get" in forest
    assert repair_priority < -1


def test_early_repair_preserves_valid_containers_and_replaces_invalid_values():
    class PersistentStub(object):
        pass

    class DictSubclass(dict):
        pass

    class ListSubclass(list):
        pass

    persistent = PersistentStub()
    preserved_dict = DictSubclass({"keep": True})
    preserved_list = ListSubclass(["keep"])
    persistent.maica_setting_dict = None
    persistent.maica_advanced_setting = preserved_dict
    persistent.maica_advanced_setting_status = "invalid"
    persistent.mas_player_additions = preserved_list
    persistent._maica_send_or_received_mpostals = {"invalid": True}
    persistent._maica_visuals = None

    namespace = {"persistent": persistent}
    exec(init_python_body(HEADER, -1498), namespace)

    assert persistent.maica_setting_dict == {}
    assert persistent.maica_advanced_setting is preserved_dict
    assert persistent.maica_advanced_setting_status == {}
    assert persistent.mas_player_additions is preserved_list
    assert persistent._maica_send_or_received_mpostals == []
    assert persistent._maica_visuals == []
    assert len(namespace["_maica_repaired_persistent_containers"]) == 4

    nested_persistent = PersistentStub()
    nested_persistent.maica_setting_dict = {
        "keep": True,
        "mspire_category": "invalid",
    }
    nested_namespace = {"persistent": nested_persistent}
    exec(init_python_body(HEADER, -1498), nested_namespace)
    assert nested_persistent.maica_setting_dict == {"keep": True}
    assert any(
        item.startswith("maica_setting_dict.mspire_category")
        for item in nested_namespace["_maica_repaired_persistent_containers"]
    )


def test_early_repair_accepts_builtin_containers_when_renpy_rebinds_names():
    class PersistentStub(object):
        pass

    class RevertableDict(dict):
        pass

    class RevertableList(list):
        pass

    persistent = PersistentStub()
    setting_dict = {"mspire_category": ["keep"]}
    advanced_setting = {"keep": True}
    advanced_status = {}
    additions = ["keep"]
    postals = []
    visuals = [{"uuid": "vista-1"}]
    persistent.maica_setting_dict = setting_dict
    persistent.maica_advanced_setting = advanced_setting
    persistent.maica_advanced_setting_status = advanced_status
    persistent.mas_player_additions = additions
    persistent._maica_send_or_received_mpostals = postals
    persistent._maica_visuals = visuals

    namespace = {
        "persistent": persistent,
        "dict": RevertableDict,
        "list": RevertableList,
    }
    exec(init_python_body(HEADER, -1498), namespace)

    assert persistent.maica_setting_dict is setting_dict
    assert persistent.maica_advanced_setting is advanced_setting
    assert persistent.maica_advanced_setting_status is advanced_status
    assert persistent.mas_player_additions is additions
    assert persistent._maica_send_or_received_mpostals is postals
    assert persistent._maica_visuals is visuals
    assert namespace["_maica_repaired_persistent_containers"] == []

    persistent._maica_visuals = None
    exec(init_python_body(HEADER, -1498), namespace)
    assert type(persistent._maica_visuals) is RevertableList


def test_vista_list_survives_export_repair_and_import_with_renpy_types():
    class PersistentStub(object):
        pass

    class RevertableDict(dict):
        pass

    class RevertableList(list):
        pass

    original = MAICAVistaFilesManager("https://example.invalid", "token")
    original.add(
        "00000000-0000-0000-0000-000000000001",
        file_path="vista_cache/source.png",
        upload_time=123.0,
        width=640,
        height=480,
    )
    exported = original.export_list()

    persistent = PersistentStub()
    persistent.maica_setting_dict = {}
    persistent.maica_advanced_setting = {}
    persistent.maica_advanced_setting_status = {}
    persistent.mas_player_additions = []
    persistent._maica_send_or_received_mpostals = []
    persistent._maica_visuals = exported
    namespace = {
        "persistent": persistent,
        "dict": RevertableDict,
        "list": RevertableList,
    }
    exec(init_python_body(HEADER, -1498), namespace)

    restarted = MAICAVistaFilesManager("https://example.invalid", "token")
    restarted.import_list(persistent._maica_visuals)

    assert persistent._maica_visuals is exported
    assert restarted.export_list() == exported


def test_nested_and_runtime_generated_containers_are_type_checked():
    repair = init_python_body(HEADER, -1498)
    assert re.search(
        r"not isinstance\(mspire_category,\s*maica_builtins\.list\)",
        repair,
    )
    assert 'maica_setting_dict.pop("mspire_category", None)' in repair

    for name, helper in (
        ("maica_stat", "is_builtin_dict"),
        ("maica_mtrigger_status", "is_builtin_dict"),
        ("_maica_visuals", "is_builtin_list"),
    ):
        assert re.search(
            r"{}\(store\.persistent\.{}\)".format(
                helper, re.escape(name)
            ),
            API,
        )
