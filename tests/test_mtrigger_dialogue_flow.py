import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "game" / "python-packages"
SUBMOD_ROOT = ROOT / "game" / "Submods" / "MAICA_ChatSubmod"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

import maica_mtrigger


def _source(name):
    return (SUBMOD_ROOT / name).read_text(encoding="utf-8")


def _label_block(source, label):
    start = source.index("label {}:".format(label))
    end = source.find("\nlabel ", start + 1)
    while end >= 0 and source.startswith("\nlabel .", end):
        end = source.find("\nlabel ", end + 1)
    return source[start:] if end < 0 else source[start:end]


def _music_trigger_runtime(music_choices, playing_name, current_track=None):
    source = _source("trigger.rpy")
    start = source.index("    class MusicTrigger(MTriggerBase):")
    end = source.index("    music_trigger = MusicTrigger()", start)
    class_source = textwrap.dedent(source[start:end])
    invalid = []
    songs = SimpleNamespace(
        current_track=current_track,
        music_choices=music_choices,
        getPlayingMusicName=lambda: playing_name,
    )

    def mas_play_song(song):
        songs.current_track = song

    store = SimpleNamespace(
        mas_play_song=mas_play_song,
        mas_submod_utils=SimpleNamespace(isSubmodInstalled=lambda _name: False),
        songs=songs,
    )
    namespace = {
        "MTriggerBase": object,
        "basestring": str,
        "log_invalid_mtrigger": lambda *args, **kwargs: invalid.append(
            (args, kwargs)
        ),
        "mtrigger_item_error": maica_mtrigger.mtrigger_item_error,
        "store": store,
    }
    exec(compile(class_source, "trigger.rpy:MusicTrigger", "exec"), namespace)
    trigger = object.__new__(namespace["MusicTrigger"])
    trigger.musics = ["__none__"] + [choice[0] for choice in music_choices]
    return trigger, store, invalid


def test_mtrigger_queue_survives_renpy_style_control_transfer():
    events = []

    class ControlTransfer(Exception):
        pass

    class RecordingTrigger(maica_mtrigger.MTriggerBase):
        def __init__(self, name, callback, priority):
            super(RecordingTrigger, self).__init__(
                maica_mtrigger.customize_template,
                name,
                callback=callback,
                exprop=maica_mtrigger.MTriggerExprop(item_name_zh="item"),
                priority=priority,
            )

    def transfer(_value):
        events.append("transfer")
        raise ControlTransfer()

    def finish(_value):
        events.append("finish")

    manager = maica_mtrigger.MTriggerManager()
    manager.add_trigger(RecordingTrigger("transfer", transfer, priority=10))
    manager.add_trigger(RecordingTrigger("finish", finish, priority=0))
    manager.triggered("transfer", {})
    manager.triggered("finish", {})

    with pytest.raises(ControlTransfer):
        manager.run_trigger()

    assert manager._running is False
    assert manager.has_triggered() is True
    assert events == ["transfer"]

    assert manager.run_trigger() == {"stop": False}
    assert manager.has_triggered() is False
    assert events == ["transfer", "finish"]


def test_maica_talking_owns_mtrigger_dispatch_and_post_processing():
    source = _source("main.rpy")
    talking = source[
        source.index("label maica_talking("):
        source.index("label maica_show_console:")
    ]

    assert "label maica_run_mtriggers:" in talking
    assert "store.action = ai.mtrigger_manager.run_trigger" not in talking

    dispatch = talking.index("call maica_run_mtriggers")
    quality = talking.index("ai.consume_quality_statuses()")
    reconnect = talking.index(
        "call maica_init_connect(use_pause_instand_wait = True)",
        quality,
    )
    resume = talking.index("jump maica_talking.asking", quality)
    assert dispatch < quality < reconnect < resume

    dispatcher = _label_block(source, "maica_run_mtriggers")
    dynamic = dispatcher.index(
        'renpy.dynamic("mtrigger_manager", "mtrigger_action", "mtrigger_step_action")'
    )
    manager_default = dispatcher.index("        mtrigger_manager = None")
    action_default = dispatcher.index(
        '        mtrigger_action = {"stop": False}'
    )
    step_default = dispatcher.index(
        '        mtrigger_step_action = {"stop": False}'
    )
    manager_binding = dispatcher.index(
        "mtrigger_manager = store.maica.maica_instance.mtrigger_manager"
    )
    empty_check = dispatcher.index("if not mtrigger_manager.has_triggered()")
    per_run_default = dispatcher.index(
        '$ mtrigger_step_action = {"stop": False}'
    )
    run_action = dispatcher.index(
        "$ mtrigger_step_action = mtrigger_manager.run_trigger()"
    )
    assert all(
        dynamic < default < manager_binding
        for default in (manager_default, action_default, step_default)
    )
    assert manager_binding < empty_check < per_run_default < run_action


def test_mtrigger_early_returns_restore_console():
    source = _source("trigger_labels.rpy")

    hold = _label_block(source, "mtrigger_hold")
    hold_reject = hold[hold.index('"Nevermind{#maica_host_nevermind}":'):]
    assert hold_reject.index("call maica_show_console") < hold_reject.index("return")

    youtube = _label_block(source, "mtrigger_youtubemusic_search(keyword)")
    offline = youtube[youtube.index("else:"):youtube.index("python:")]
    assert offline.index("call maica_show_console") < offline.index("return")

    backup = _label_block(source, "mtrigger_backup")
    assert backup.count("call maica_show_console") == 1
    assert backup.index("call maica_show_console") < backup.rindex("return")


def test_music_trigger_keeps_protocol_titles_and_mas_playback_paths_separate():
    title = "Your Reality"
    path = "bgm/credits.ogg"
    legacy_track = (title, path)
    trigger, store, invalid = _music_trigger_runtime(
        [(title, path)],
        playing_name=title,
        current_track=legacy_track,
    )

    assert trigger.current_item() == title
    assert trigger.find(title) == path
    assert trigger.find(path) is None

    music_label = _label_block(
        _source("trigger_labels.rpy"), "mtrigger_music_auto(cls, selection)"
    )
    assert "store.mas_play_song(cls.find(selection))" in music_label
    store.mas_play_song(trigger.find(title))

    assert store.songs.current_track == path
    assert not isinstance(store.songs.current_track, tuple)
    assert invalid == []


def test_weather_trigger_uses_the_common_mtrigger_lifecycle():
    trigger_source = _source("trigger.rpy")
    label_source = _source("trigger_labels.rpy")

    weather_callback = trigger_source[
        trigger_source.index("        def callback(self, selection):"):
        trigger_source.index("    weather_trigger = WeatherTrigger()")
    ]
    assert 'store.renpy.call("mtrigger_weather", weather)' in weather_callback
    assert 'store.renpy.call("mas_change_weather"' not in weather_callback

    weather_label = _label_block(label_source, "mtrigger_weather(weather)")
    expected_calls = (
        "call maica_pause_connection",
        "call maica_hide_console",
        "call mas_change_weather(weather, by_user=True, set_persistent=True)",
        "call maica_show_console",
    )
    positions = [weather_label.index(call) for call in expected_calls]
    assert positions == sorted(positions)


def test_standalone_idle_callback_uses_the_full_reconnect_lifecycle():
    main_source = _source("main.rpy")
    label_source = _source("trigger_labels.rpy")

    pause = _label_block(main_source, "maica_pause_connection")
    reconnect = _label_block(main_source, "maica_reconnect")
    idle_callback = _label_block(label_source, "mtrigger_idle_callback")

    assert "ai.close_wss_session()" in pause
    assert "call maica_pause_connection" in reconnect
    assert "call maica_init_connect(use_pause_instand_wait = True)" in reconnect
    assert "call maica_reconnect" in idle_callback
    assert label_source.count("call maica_reconnect") == 1
