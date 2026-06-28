from pathlib import Path


API_RPY = Path(__file__).resolve().parents[1] / "game" / "Submods" / "MAICA_ChatSubmod" / "api.rpy"


def _extract_function(source, function_name):
    marker = "    def {}():".format(function_name)
    start = source.index(marker)
    next_def = source.find("\n    def ", start + len(marker))
    if next_def == -1:
        return source[start:]
    return source[start:next_def]


def test_start_maica_schedules_certifi_download_without_direct_network_io():
    start_maica = _extract_function(API_RPY.read_text(encoding="utf-8"), "start_maica")

    assert "requests.get(" not in start_maica
    assert "maica_start_certifi_download_in_background(" in start_maica
