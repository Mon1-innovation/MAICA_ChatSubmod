import os
import sys
from pathlib import Path
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


def test_linux_and_mac_bundled_magick_has_executable_permission():
    bundled_magick = ROOT / "game" / "Submods" / "MAICA_ChatSubmod" / "magick"
    assert bundled_magick.is_file()
    assert os.access(str(bundled_magick), os.X_OK)
