import sys
import logging
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "game" / "python-packages"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

import bot_interface
import maica


def test_key_replace_preserves_unicode_text():
    assert bot_interface.to_unicode("错误".encode("utf-8")) == "错误"
    assert bot_interface.key_replace("状态: 中文", {"状态": "错误"}) == "错误: 中文"


def test_send_to_outside_func_keeps_unicode_console_text():
    ai = maica.MaicaAi.__new__(maica.MaicaAi)
    received = []
    ai.content_func = received.append

    ai.send_to_outside_func("错误信息: 中文")

    assert received == ["错误信息: 中文"]


def test_console_handler_falls_back_to_unicode_record_formatting():
    received = []
    handler = maica.MaicaAi.ExternalLoggingHandler(received.append)

    def raise_unicode_error(record):
        raise UnicodeError("simulated Python 2 formatter failure")

    handler.format = raise_unicode_error
    handler.emit(logging.LogRecord("test", logging.ERROR, __file__, 1, "中文错误", (), None))

    assert received == ["<ERROR>|中文错误"]


def test_localized_status_does_not_use_mas_write_command():
    main_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "main.rpy"
    ).read_text(encoding="utf-8")

    assert "ai.send_to_outside_func(ai.get_status_description())" in main_source
    assert "store.mas_ptod.write_command(ai.get_status_description())" not in main_source


def test_python2_console_path_does_not_force_unicode_through_str():
    maica_source = (PACKAGE_ROOT / "maica.py").read_text(encoding="utf-8")
    output_block = maica_source[maica_source.index("    def send_to_outside_func"):]
    output_block = output_block[:output_block.index("    def update_stat")]

    assert "self.content_func(str(key_replace" not in output_block
    assert "bot_interface.to_unicode" in output_block
