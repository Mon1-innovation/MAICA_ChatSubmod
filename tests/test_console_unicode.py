import sys
import logging
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "game" / "python-packages"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

import bot_interface
import logger_manager
import maica_provider_manager
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


def test_console_logger_reuses_one_handler_and_isolated_propagation():
    console_logger = logging.getLogger("mas_console_logger")
    handlers_before = list(console_logger.handlers)
    callbacks_before = [
        (handler, getattr(handler, "maica_console_log_func", None))
        for handler in handlers_before
    ]
    level_before = console_logger.level
    propagate_before = console_logger.propagate
    mtrigger_logger_before = maica.maica_mtrigger.logger
    manager = logger_manager.get_logger_manager()
    reference_name = "maica_mtrigger.logger"
    missing_reference = object()
    reference_before = manager._injected_references.get(
        reference_name, missing_reference
    )

    try:
        first = maica.MaicaAi("account", "password")
        second = maica.MaicaAi("account", "password")
        owned_handlers = [
            handler for handler in console_logger.handlers
            if getattr(handler, "_maica_console_handler", False)
        ]

        assert len(owned_handlers) == 1
        assert console_logger.propagate is False

        first_output = []
        second_output = []
        first.content_func = first_output.append
        second.content_func = second_output.append
        second.console_logger.error("handler probe")

        assert first_output == []
        assert second_output == ["<ERROR>|handler probe"]
    finally:
        for handler in list(console_logger.handlers):
            if handler not in handlers_before:
                console_logger.removeHandler(handler)
                handler.close()
        for handler in handlers_before:
            if handler not in console_logger.handlers:
                console_logger.addHandler(handler)
        for handler, callback in callbacks_before:
            if hasattr(handler, "maica_console_log_func"):
                handler.maica_console_log_func = callback
        console_logger.setLevel(level_before)
        console_logger.propagate = propagate_before
        maica.maica_mtrigger.logger = mtrigger_logger_before
        if reference_before is missing_reference:
            manager._injected_references.pop(reference_name, None)
        else:
            manager._injected_references[reference_name] = reference_before


def test_logger_manager_fallback_and_provider_logger_are_centralized():
    manager = logger_manager.get_logger_manager()

    assert manager.logger.name == "maica_logger_manager"
    assert manager.logger.propagate is False
    assert manager._stream_handler in manager.logger.handlers
    assert manager._stream_handler not in logging.getLogger().handlers
    assert maica_provider_manager.logger is bot_interface.logger


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


def test_ascii_console_output_is_raw_and_welcome_flow_is_single_pass():
    root = Path(__file__).resolve().parents[1] / "game" / "Submods" / "MAICA_ChatSubmod"
    main_source = (root / "main.rpy").read_text(encoding="utf-8")
    chat_source = (root / "chat.rpy").read_text(encoding="utf-8")

    connect_start = main_source.index("label maica_init_connect")
    connect_end = main_source.index("\nlabel maica_connect_from_settings", connect_start)
    connect = main_source[connect_start:connect_end]
    intro_start = chat_source.index("label init_maica:")
    intro_end = chat_source.index('        "Better next time.":', intro_start)
    intro = chat_source[intro_start:intro_end]
    talking_start = main_source.index("label maica_talking")
    talking_setup_end = main_source.index("    $ return_code = None", talking_start)
    talking_setup = main_source[talking_start:talking_setup_end]
    show_console_start = main_source.index("label maica_show_console:")
    show_console_end = main_source.index("\nlabel maica_hide_console:", show_console_start)
    show_console = main_source[show_console_start:show_console_end]
    hide_console_start = show_console_end + 1
    hide_console_end = main_source.index("\nlabel maica_reconnect:", hide_console_start)
    hide_console = main_source[hide_console_start:hide_console_end]

    assert connect.count("ai.send_to_outside_func(ai.ascii_icon)") == 1
    assert connect.count('write_command("Thank you for using MAICA Blessland!")') == 1
    assert "persistent.maica_setting_dict['console']" in connect
    assert "and (force_welcome or should_connect)" in connect
    assert "if should_show_welcome:" in connect
    assert "renpy.pause(2.3)" in connect
    assert "ai.console_logger.critical" not in connect
    assert "maica_connect_result = \"disconnected\"" in connect
    assert "maica_connect_result = \"success\"" in connect
    assert "return maica_connect_result" in connect
    assert "return _return" not in connect
    assert "console_logger.critical(\"<DISABLE_VERBOSITY>\"+store.maica.maica_instance.ascii_icon)" not in chat_source
    assert "send_to_outside_func(store.maica.maica_instance.ascii_icon)" not in chat_source
    assert 'write_command("Thank you for using MAICA Blessland!")' not in chat_source

    assert "if persistent.maica_setting_dict['console']:" in show_console
    assert show_console.index("if persistent.maica_setting_dict['console']:") < show_console.index("show screen mas_py_console_teaching")
    assert 'if renpy.showing("monika"):' in hide_console
    assert hide_console.index('if renpy.showing("monika"):') < hide_console.index("show monika at t11")

    assert intro.count("call maica_show_console") == 1
    assert intro.count("call maica_init_connect(") == 1
    assert "force_welcome = True" in intro
    assert "show screen mas_py_console_teaching" not in intro
    assert "hide screen mas_py_console_teaching" not in intro
    assert "call maica_talking(prepared = True)" in intro
    assert intro.index("call maica_show_console") < intro.index("call maica_init_connect(")
    assert intro.index("call maica_init_connect(") < intro.index("call maica_talking(prepared = True)")
    assert intro.count('if _return == "disconnected":') == 1
    assert intro.index('if _return == "disconnected":') < intro.index("call maica_hide_console")
    assert intro.index("call maica_connection_failure_dialogue") < intro.index("call maica_hide_console")

    assert "label maica_talking(mspire = False, prepared = False):" in talking_setup
    assert "if not prepared:" in talking_setup
    assert talking_setup.index("if not prepared:") < talking_setup.index("call maica_show_console")
    assert talking_setup.index("call maica_show_console") < talking_setup.index("call maica_init_connect")


def test_python2_console_path_does_not_force_unicode_through_str():
    maica_source = (PACKAGE_ROOT / "maica.py").read_text(encoding="utf-8")
    output_block = maica_source[maica_source.index("    def send_to_outside_func"):]
    output_block = output_block[:output_block.index("    def update_stat")]

    assert "self.content_func(str(key_replace" not in output_block
    assert "bot_interface.to_unicode" in output_block
