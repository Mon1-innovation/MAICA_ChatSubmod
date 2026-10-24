import os
import sys
import textwrap
from importlib.machinery import PathFinder
from pathlib import Path
from types import SimpleNamespace
import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "game" / "python-packages"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

import file_selector


def test_file_selector_imports_without_requiring_windows_ctypes():
    assert hasattr(file_selector, "select_file")
    assert hasattr(file_selector, "_select_file_macos")
    assert hasattr(file_selector, "_select_file_windows")
    assert hasattr(file_selector, "_select_file_linux")


def test_select_file_macos_generates_correct_applescript_command(monkeypatch):
    recorded_commands = []

    class DummyProc(object):
        def __init__(self, returncode, stdout_data):
            self.returncode = returncode
            self.stdout_data = stdout_data

        def communicate(self):
            return (self.stdout_data, b"")

    def fake_popen(cmd, stdout=None, stderr=None):
        recorded_commands.append(cmd)
        return DummyProc(0, b"/Users/test/image.png\n")

    monkeypatch.setattr(file_selector.subprocess, "Popen", fake_popen)

    res = file_selector._select_file_macos(
        title=u"Choose Your Image",
        file_types=[(u"Images", "*.png;*.jpg")]
    )
    assert res == "/Users/test/image.png"
    assert len(recorded_commands) == 1
    script_arg = recorded_commands[0][2]
    if isinstance(script_arg, bytes):
        script_arg = script_arg.decode("utf-8")
    assert 'choose file of type {"png", "jpg"}' in script_arg
    assert 'with prompt "Choose Your Image"' in script_arg


def test_select_file_macos_handles_cancellation(monkeypatch):
    class DummyProc(object):
        returncode = 1

        def communicate(self):
            return (b"", b"User canceled. (-128)")

    monkeypatch.setattr(
        file_selector.subprocess,
        "Popen",
        lambda *args, **kwargs: DummyProc()
    )

    res = file_selector._select_file_macos(title=u"Choose")
    assert res == u""


def test_api_rpy_contains_macos_magick_detection():
    api_source = (ROOT / "game" / "Submods" / "MAICA_ChatSubmod" / "api.rpy").read_text(encoding="utf-8")
    assert 'getattr(renpy, "macintosh", False) or getattr(renpy, "mac", False)' in api_source
    assert "/opt/homebrew/bin/magick" in api_source
    assert "/usr/local/bin/magick" in api_source
    assert "find_executable(\"magick\")" in api_source


def test_macos_lib_directories_exist_and_contain_stdlib_shims():
    expected_files = {
        "Queue.py",
        "Cookie.py",
        "cgi.py",
        "hmac.py",
        "htmlentitydefs.py",
        "markupbase.py",
        "_markupbase.py",
    }
    for subpath in ("osx-x86_64/lib/python2.7", "darwin-x86_64/lib/python2.7"):
        target_dir = ROOT / "lib" / subpath
        assert target_dir.is_dir()
        actual_files = {f.name for f in target_dir.glob("*.py")}
        assert expected_files.issubset(actual_files)


def run_early_api_init(monkeypatch, basedir, search_path, platform="darwin", major=2):
    source = (ROOT / "game" / "Submods" / "MAICA_ChatSubmod" / "api.rpy").read_text(encoding="utf-8")
    body = source.split("init -1500 python:\n", 1)[1].split("\ndefault ", 1)[0]
    runtime_sys = SimpleNamespace(platform=platform, version_info=(major, 7, 10), path=search_path)
    renpy_exports = SimpleNamespace(Displayable=object(), save_persistent=object())
    namespace = {
        "config": SimpleNamespace(basedir=str(basedir), language="english"),
        "_preferences": SimpleNamespace(language=None),
        "renpy": renpy_exports,
    }
    with monkeypatch.context() as context:
        context.setitem(sys.modules, "sys", runtime_sys)
        context.setitem(sys.modules, "renpy", SimpleNamespace())
        exec(textwrap.dedent(body), namespace)
    assert namespace["renpy"] is renpy_exports
    return search_path


def test_macos_python2_can_find_packaged_hmac_without_native_copy(monkeypatch, tmp_path):
    search_path = run_early_api_init(monkeypatch, ROOT, [str(tmp_path)])
    spec = PathFinder.find_spec("hmac", search_path)
    assert Path(spec.origin) == ROOT / "lib/darwin-x86_64/lib/python2.7/hmac.py"
    assert run_early_api_init(monkeypatch, ROOT, search_path) == search_path
    assert len(search_path) == len(set(search_path))


def test_macos_stdlib_fallback_preserves_native_module_priority(monkeypatch, tmp_path):
    native_hmac = tmp_path / "hmac.py"
    native_hmac.write_text("native = True\n", encoding="utf-8")
    search_path = run_early_api_init(monkeypatch, ROOT, [str(tmp_path)])
    assert Path(PathFinder.find_spec("hmac", search_path).origin) == native_hmac


def test_macos_stdlib_fallback_supports_osx_directory_only(monkeypatch, tmp_path):
    fallback = tmp_path / "lib/osx-x86_64/lib/python2.7"
    fallback.mkdir(parents=True)
    (fallback / "hmac.py").write_text("fallback = True\n", encoding="utf-8")
    search_path = run_early_api_init(monkeypatch, tmp_path, [])
    assert Path(PathFinder.find_spec("hmac", search_path).origin) == fallback / "hmac.py"


@pytest.mark.parametrize("platform,major", [("darwin", 3), ("win32", 2), ("linux", 2)])
def test_stdlib_fallback_does_not_affect_other_runtimes(monkeypatch, tmp_path, platform, major):
    original = [str(tmp_path)]
    assert run_early_api_init(monkeypatch, ROOT, original[:], platform, major) == original


def test_linux_and_mac_bundled_magick_has_executable_permission():
    bundled_magick = ROOT / "game" / "Submods" / "MAICA_ChatSubmod" / "magick"
    assert bundled_magick.is_file()
    assert os.access(str(bundled_magick), os.X_OK)
