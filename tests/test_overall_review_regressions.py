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
    assert mpostal_source.index("try:") < mpostal_source.index("vista_manager.upload")
    assert "vista_info = cur_postal.get(\"vista_image_info\") or {}" in mpostal_source


def test_get_history_returns_dict_on_unavailable_service():
    ai = object.__new__(maica.MaicaAi)
    ai._MaicaAi__accessable = False

    result = ai.get_history()

    assert result["success"] is False
    assert result["content"] == []
