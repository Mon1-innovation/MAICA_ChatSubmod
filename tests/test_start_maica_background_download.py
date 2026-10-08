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


def test_start_maica_leaves_topic_reconciliation_to_the_post_migration_hook():
    start_maica = _extract_function(API_RPY.read_text(encoding="utf-8"), "start_maica")

    assert 'maica_reconcile_topic_state' not in start_maica
    assert 'mas_lockEVL("maica_main", "EVE")' not in start_maica
    assert 'mas_unlockEVL("maica_main", "EVE")' not in start_maica


def test_topic_reconciliation_runs_after_the_migration_plugin():
    api = API_RPY.read_text(encoding="utf-8")
    assert '@store.mas_submod_utils.functionplugin("ch30_preloop", priority=-50)' in api
    assert '@store.mas_submod_utils.functionplugin("ch30_preloop", priority=-25)' in api
    assert 'def maica_topic_state_startup_check():' in api
    assert 'store.maica_reconcile_topic_state(reason="startup")' in api
