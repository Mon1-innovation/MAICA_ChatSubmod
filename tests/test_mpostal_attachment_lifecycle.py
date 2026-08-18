import struct
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "game" / "python-packages"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from maica_mpostal_files import MPostalAttachmentStore, path_is_within
from maica_vista_files_manager import MAICAVistaFilesManager


def _write_png_header(path, width, height):
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
    )


def test_mpostal_attachment_store_moves_restores_and_deletes_only_managed_files(tmp_path):
    characters = tmp_path / "characters"
    characters.mkdir()
    source = characters / "letter.mms"
    source.write_bytes(b"attachment")

    store = MPostalAttachmentStore(str(tmp_path / "vista_cache" / "mpostal_pending"))
    staged = Path(store.stage(str(source)))

    assert not source.exists()
    assert staged.read_bytes() == b"attachment"
    assert staged.suffix == ".mms"
    assert store.contains(str(staged))
    assert path_is_within(str(staged), store.root_path)
    assert store.stage(str(staged)).replace("\\", "/") == str(staged).replace("\\", "/")

    assert store.restore(str(staged), str(source)) is True
    assert source.read_bytes() == b"attachment"
    assert not staged.exists()

    staged = Path(store.stage(str(source)))
    assert store.delete(str(staged)) is True
    assert not staged.exists()


def test_mpostal_attachment_store_refuses_paths_outside_its_root(tmp_path):
    outside = tmp_path / "outside.mms"
    outside.write_bytes(b"keep")
    store = MPostalAttachmentStore(str(tmp_path / "pending"))

    assert store.contains(str(outside)) is False
    assert store.delete(str(outside)) is False
    assert outside.read_bytes() == b"keep"


def test_mpostal_attachment_store_rejects_missing_paths_inside_its_root(tmp_path):
    store = MPostalAttachmentStore(str(tmp_path / "pending"))
    store.ensure()
    missing = Path(store.root_path) / "missing.mms"

    try:
        store.stage(str(missing))
    except IOError:
        pass
    else:
        raise AssertionError("missing managed paths must not be staged")


def test_vista_manager_deletes_thumbnail_without_deleting_source(tmp_path):
    cache = tmp_path / "vista_cache"
    cache.mkdir()
    source = tmp_path / "source.mms"
    source.write_bytes(b"original")
    thumbnail = cache / "thumb_postal.png"
    _write_png_header(thumbnail, 120, 80)
    entry = {
        "path": str(source),
        "thumb_path": str(thumbnail),
        "thumb_width": 120,
        "thumb_height": 80,
        "thumb_version": MAICAVistaFilesManager.THUMBNAIL_VERSION,
    }
    manager = MAICAVistaFilesManager(
        "https://example.invalid",
        "token",
        cache_path=str(cache),
    )

    assert manager.get_thumbnail_info(entry) is not None
    assert manager.delete_thumbnail(entry) is True
    assert source.read_bytes() == b"original"
    assert not thumbnail.exists()
    assert "thumb_path" not in entry
