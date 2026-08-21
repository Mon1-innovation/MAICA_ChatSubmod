import struct
import sys
from pathlib import Path

import pytest


PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "game" / "python-packages"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

import maica
import maica_mtrigger
import maica_tasker
import maica_vista_files_manager
from maica_vista_files_manager import MAICAVistaFilesManager


def test_mtrigger_build_refreshes_dynamic_values_before_validation():
    class DynamicTrigger(maica_mtrigger.MTriggerBase):
        def __init__(self):
            self.build_calls = 0
            super(DynamicTrigger, self).__init__(
                maica_mtrigger.common_switch_template,
                "dynamic",
                exprop=maica_mtrigger.MTriggerExprop(
                    item_name_zh="item",
                    item_name_en="item",
                    item_list=["old"],
                    curr_value="old",
                ),
            )

        def on_build_pre(self):
            self.exprop.item_list = ["new"]
            self.exprop.curr_value = "new"

        def build(self):
            self.build_calls += 1
            return super(DynamicTrigger, self).build()

    manager = maica_mtrigger.MTriggerManager()
    trigger = DynamicTrigger()
    manager.add_trigger(trigger)

    assert manager.build_data(full=True)[0]["exprop"]["curr_item"] == "new"
    assert trigger.build_calls == 1


def test_mtrigger_running_flag_is_cleared_when_callback_fails():
    class FailingTrigger(maica_mtrigger.MTriggerBase):
        def triggered(self, data=None):
            raise RuntimeError("boom")

    manager = maica_mtrigger.MTriggerManager()
    manager.add_trigger(
        FailingTrigger(
            maica_mtrigger.customize_template,
            "failing",
            exprop=maica_mtrigger.MTriggerExprop(item_name_zh="item"),
        )
    )
    manager.triggered("failing", {})

    with pytest.raises(RuntimeError):
        manager.run_trigger()

    assert manager._running is False


def test_task_failure_sets_error_and_preserves_integer_task_type():
    class FailingTask(maica_tasker.MaicaTask):
        def on_manual_run(self):
            raise RuntimeError("boom")

    task = FailingTask(maica_tasker.MaicaTask.MAICATASK_TYPE_NORMAL, "failing", None)

    with pytest.raises(RuntimeError):
        task.start_event()

    assert task.status == maica_tasker.MaicaTask.MAICATASK_STATUS_ERROR
    assert task.task_type == maica_tasker.MaicaTask.MAICATASK_TYPE_NORMAL


def test_vista_reupload_keeps_record_when_upload_fails(monkeypatch):
    manager = MAICAVistaFilesManager("https://example.invalid", "token")
    entry = {"uuid": "old", "path": "cached.png"}
    manager.files = [entry]

    def fail_upload(_path):
        raise RuntimeError("network down")

    monkeypatch.setattr(manager, "upload", fail_upload)
    with pytest.raises(RuntimeError):
        manager.reupload("old")

    assert manager.files == [entry]


def test_vista_cache_cleanup_removes_only_unreferenced_managed_files(tmp_path):
    cache = tmp_path / "cache"
    manager = MAICAVistaFilesManager(
        "https://example.invalid", "token", cache_path=str(cache)
    )
    active_uuid = "00000000-0000-0000-0000-000000000001"
    postal_uuid = "00000000-0000-0000-0000-000000000002"
    orphan_uuid = "00000000-0000-0000-0000-000000000003"

    active_source = cache / (active_uuid + ".png")
    active_thumb = Path(manager._thumbnail_output_path(active_uuid))
    postal_source = cache / (postal_uuid + ".jpg")
    postal_thumb = Path(manager._thumbnail_output_path(postal_uuid))
    orphan_source = cache / (orphan_uuid + ".webp")
    orphan_thumb = Path(manager._thumbnail_output_path(orphan_uuid))
    legacy_orphan = cache / "old-upload-name.jpeg"
    unknown_file = cache / "notes.txt"
    pending_dir = cache / "mpostal_pending"
    pending_dir.mkdir()
    pending_file = pending_dir / (orphan_uuid + ".mms")

    for path in (
        active_source,
        active_thumb,
        postal_source,
        postal_thumb,
        orphan_source,
        orphan_thumb,
        legacy_orphan,
        unknown_file,
        pending_file,
    ):
        path.write_bytes(b"cached")

    active = manager.add(active_uuid, file_path=str(active_source))
    active["thumb_path"] = str(active_thumb)
    postal_thumb_display_path = (
        "Submods/MAICA_ChatSubmod/vista_cache/" + postal_thumb.name
    )

    assert manager.cleanup_cache(
        [str(postal_source), postal_thumb_display_path]
    ) == 3
    assert active_source.exists()
    assert active_thumb.exists()
    assert postal_source.exists()
    assert postal_thumb.exists()
    assert not orphan_source.exists()
    assert not orphan_thumb.exists()
    assert not legacy_orphan.exists()
    assert unknown_file.exists()
    assert pending_file.exists()

    manager.remove(active_uuid)
    assert manager.cleanup_cache(
        [str(postal_source), postal_thumb_display_path]
    ) == 2
    assert not active_source.exists()
    assert not active_thumb.exists()
    assert postal_source.exists()
    assert postal_thumb.exists()


def test_vista_cache_uuid_filename_check_needs_no_uuid_module():
    source = Path(maica_vista_files_manager.__file__).read_text(encoding="utf-8")

    assert "import uuid" not in source
    assert MAICAVistaFilesManager._is_uuid_filename(
        "00000000-0000-0000-0000-000000000001"
    )
    assert MAICAVistaFilesManager._is_uuid_filename(
        "ABCDEF12-3456-7890-ABCD-EF1234567890.png"
    )
    assert not MAICAVistaFilesManager._is_uuid_filename(
        "000000000000-0000-0000-0000-000000000001"
    )
    assert not MAICAVistaFilesManager._is_uuid_filename(
        "00000000-0000-0000-0000-00000000000g"
    )


def test_vista_ui_mutations_sync_and_save_the_cached_file_list():
    root = Path(__file__).resolve().parents[1]
    submod = root / "game" / "Submods" / "MAICA_ChatSubmod"
    api_source = (submod / "api.rpy").read_text(encoding="utf-8")
    vista_screen = (submod / "screen_subs_vista.rpy").read_text(encoding="utf-8")
    main_source = (submod / "main.rpy").read_text(encoding="utf-8")

    sync_block = api_source.split("    def sync_vista_files():", 1)[1].split(
        "\n    def upload_vista_image", 1
    )[0]
    assert "store.persistent._maica_visuals =" in sync_block
    assert "store.renpy.save_persistent()" in sync_block
    assert sync_block.index("store.renpy.save_persistent()") < sync_block.index(
        "cleanup_vista_cache()"
    )

    for function_name, mutation in (
        ("upload_vista_image", "vista_manager.upload"),
        ("reupload_vista_image", "vista_manager.reupload"),
        ("delete_vista_image", "vista_manager.delete"),
        ("remove_vista_image", "vista_manager.remove"),
    ):
        block = api_source.split("    def {}(".format(function_name), 1)[1].split(
            "\n    def ", 1
        )[0]
        assert mutation in block
        assert block.index(mutation) < block.index("sync_vista_files()")

    assert "store.maica.upload_vista_image" in vista_screen
    assert "store.maica.reupload_vista_image" in vista_screen
    assert "store.maica.delete_vista_image" in vista_screen
    assert "store.maica.remove_vista_image" in vista_screen
    assert "vista_manager.upload(" not in vista_screen
    assert "vista_manager.reupload(" not in vista_screen
    assert "vista_manager.delete(" not in vista_screen
    assert "vista_manager.remove(" not in vista_screen
    assert "store.maica.upload_vista_image(image_source)" in main_source


def test_vista_image_size_parsers_handle_bmp_and_webp(tmp_path):
    bmp = tmp_path / "sample.bmp"
    bmp_data = bytearray(26)
    bmp_data[0:2] = b"BM"
    bmp_data[18:26] = struct.pack("<II", 640, 480)
    bmp.write_bytes(bmp_data)

    webp = tmp_path / "sample.webp"
    webp_data = bytearray(30)
    webp_data[0:4] = b"RIFF"
    webp_data[8:12] = b"WEBP"
    webp_data[12:16] = b"VP8X"
    webp_data[24:27] = (299).to_bytes(3, "little")
    webp_data[27:30] = (199).to_bytes(3, "little")
    webp.write_bytes(webp_data)

    assert MAICAVistaFilesManager._get_image_size(str(bmp)) == (640, 480)
    assert MAICAVistaFilesManager._get_image_size(str(webp)) == (300, 200)


def _write_png_header(path, width, height):
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
    )


def test_vista_thumbnail_generation_is_external_bounded_and_png(monkeypatch, tmp_path):
    source = tmp_path / "letter.mms"
    source.write_bytes(b"unrecognized source format")
    manager = MAICAVistaFilesManager(
        "https://example.invalid", "token", cache_path=str(tmp_path / "cache")
    )
    manager.magick_path = "magick"
    calls = []

    def fake_call(command, **kwargs):
        calls.append((command, kwargs))
        _write_png_header(Path(command[-1]), 533, 300)
        return 0

    monkeypatch.setattr(maica_vista_files_manager.subprocess, "call", fake_call)
    entry = {"uuid": "vista-1", "path": str(source)}

    assert manager.ensure_thumbnail(entry) is True
    assert manager.get_thumbnail_info(entry) == (
        entry["thumb_path"],
        533,
        300,
    )
    assert entry["thumb_path"].endswith(".png")
    assert entry["thumb_version"] == manager.THUMBNAIL_VERSION
    assert calls[0][0][1] == str(source) + "[0]"
    assert "-auto-orient" in calls[0][0]
    assert calls[0][0][calls[0][0].index("-thumbnail") + 1] == "600x300>"


def test_vista_upload_generates_thumbnail_when_source_dimensions_are_unknown(
    monkeypatch, tmp_path
):
    source = tmp_path / "attachment.mms"
    source.write_bytes(b"format recognized only by ImageMagick")
    manager = MAICAVistaFilesManager(
        "https://example.invalid", "token", cache_path=str(tmp_path / "cache")
    )
    manager.magick_path = "magick"
    calls = []

    class ResponseStub(object):
        def json(self):
            return {"success": True, "content": "vista-upload"}

    def fake_call(command, **kwargs):
        calls.append(command)
        _write_png_header(Path(command[-1]), 450, 300)
        return 0

    monkeypatch.setattr(
        maica_vista_files_manager.requests,
        "post",
        lambda *args, **kwargs: ResponseStub(),
    )
    monkeypatch.setattr(maica_vista_files_manager.subprocess, "call", fake_call)

    assert manager.upload(str(source)) == "vista-upload"
    entry = manager.get_info("vista-upload")
    assert calls
    assert entry["thumb_width"] == 450
    assert entry["thumb_height"] == 300
    assert manager.get_thumbnail_info(entry) is not None


def test_vista_thumbnail_failure_never_falls_back_to_original(monkeypatch, tmp_path):
    source = tmp_path / "large-source.mms"
    _write_png_header(source, 200, 200)
    manager = MAICAVistaFilesManager(
        "https://example.invalid", "token", cache_path=str(tmp_path / "cache")
    )
    manager.magick_path = "magick"
    entry = {
        "uuid": "vista-2",
        "path": str(source),
        "thumb_path": str(source),
        "thumb_width": 200,
        "thumb_height": 200,
        "thumb_version": manager.THUMBNAIL_VERSION,
    }

    monkeypatch.setattr(
        maica_vista_files_manager.subprocess,
        "call",
        lambda *args, **kwargs: 1,
    )

    assert manager.ensure_thumbnail(entry) is False
    assert manager.get_thumbnail_info(entry) is None
    assert "thumb_path" not in entry
    assert entry["path"] == str(source)


def test_vista_rejects_oversized_generated_thumbnail(monkeypatch, tmp_path):
    source = tmp_path / "source.png"
    _write_png_header(source, 1200, 600)
    manager = MAICAVistaFilesManager(
        "https://example.invalid", "token", cache_path=str(tmp_path / "cache")
    )
    manager.magick_path = "magick"

    def fake_call(command, **kwargs):
        _write_png_header(Path(command[-1]), 601, 300)
        return 0

    monkeypatch.setattr(maica_vista_files_manager.subprocess, "call", fake_call)
    entry = {"uuid": "vista-3", "path": str(source)}

    assert manager.ensure_thumbnail(entry) is False
    assert manager.get_thumbnail_info(entry) is None
    assert not list((tmp_path / "cache").glob("thumb_*.png"))


def test_vista_screens_only_render_validated_thumbnails():
    root = Path(__file__).resolve().parents[1]
    vista_screen = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "screen_subs_vista.rpy"
    ).read_text(encoding="utf-8")
    postal_screen = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "screen_subs.rpy"
    ).read_text(encoding="utf-8")
    combined = vista_screen + postal_screen

    assert "get_thumbnail_info" in vista_screen
    assert "get_thumbnail_info" in postal_screen
    assert "return vista_manager.get_thumbnail_info(item)" not in combined
    assert "add Transform(img_path" not in combined
    assert "add Transform(postal['raw_image']" not in combined
    assert "return (path, True)" not in combined
    assert "renpy.image_size" not in combined


def test_reviewed_source_contracts_are_kept_in_sync():
    trigger_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "trigger.rpy"
    ).read_text(encoding="utf-8")
    label_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "trigger_labels.rpy"
    ).read_text(encoding="utf-8")
    api_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "api.rpy"
    ).read_text(encoding="utf-8")

    assert 'store.renpy.call("mtrigger_youtubemusic_search", selection)' in trigger_source
    assert "label mtrigger_youtubemusic_search(keyword):" in label_source
    assert "def maica_set_plain_provider():" in api_source
    assert "store.maica.maica_instance.provider_id = 2" in api_source

    main_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "main.rpy"
    ).read_text(encoding="utf-8")
    mpostal_source = main_source[
        main_source.index("label maica_mpostal_read:"):
        main_source.index("label maica_mpostal_read.failed:")
    ]
    assert mpostal_source.index("try:") < mpostal_source.index(
        "store.maica.upload_vista_image"
    )
    assert "vista_info = cur_postal.get(\"vista_image_info\") or {}" in mpostal_source


def test_get_history_returns_dict_on_unavailable_service():
    ai = object.__new__(maica.MaicaAi)
    ai._MaicaAi__accessable = False

    result = ai.get_history()

    assert result["success"] is False
    assert result["content"] == []
