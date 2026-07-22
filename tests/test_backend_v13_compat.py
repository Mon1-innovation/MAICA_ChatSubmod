"""Static release contracts for the MAICA backend-v1.3 migration.

These tests intentionally parse source instead of importing Ren'Py modules.  They are
the release-side complement to the behavioural protocol tests.
"""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBMOD = ROOT / "game" / "Submods" / "MAICA_ChatSubmod"
PYTHON = ROOT / "game" / "python-packages"
ASSETS = ROOT / "game" / "mod_assets" / "console"


def source(relative):
    path = ROOT / relative
    assert path.is_file(), "required contract source is missing: {}".format(relative)
    return path.read_text(encoding="utf-8")


def sources(paths):
    return "\n".join(source(path) for path in paths)


def production_sources():
    paths = [path for path in SUBMOD.rglob("*.rpy") if path.name != "migrations.rpy"]
    paths += list(PYTHON.glob("*.py"))
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def executable_lines(text):
    return "\n".join(
        line for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "old ", "new "))
    )


def assert_owner_renamed(text, old, new):
    """Require the canonical owner and reject the old owner outside migration code."""
    assert new in text, "canonical owner {!r} is missing".format(new)
    assert old not in text, "retired runtime owner {!r} remains".format(old)


RENAMES = {
    "sfe_aggressive": "prompt_pname_repl",
    "mf_aggressive": "mf_llm_concl",
    "tnd_aggressive": "mf_const_tools",
    "esc_aggressive": "esearch_llm_concl",
    "amt_aggressive": "mf_precheck_mt",
    "pre_additive": "mf_context_rnds",
    "post_additive": "mt_context_rnds",
    "dscl_pvn": "gen_quality_chk",
    "pre_astp": "mf_disable_loop",
    "post_astp": "mt_disable_loop",
    "enforce_lang": "gen_enforce_lang",
    "sf_extraction": "savefile_access",
    "max_length": "session_len_limit",
    "ic_prep": "twk_super",
}


def test_a_release_version_migration_and_local_override_contract():
    maica = source("game/python-packages/maica.py")
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    migration_path = SUBMOD / "migrations.rpy"
    assert re.search(r"SUPPORT_BACKEND\s*=\s*['\"]1\.3\.000['\"]", maica)
    assert migration_path.is_file()
    migration = migration_path.read_text(encoding="utf-8")
    assert "1.8.0" in migration
    assert re.search(r"(?:register|migration).{0,100}1\.8\.0|1\.8\.0.{0,100}(?:register|migration)", migration, re.S)
    assert re.search(r"maica_ver\s*=\s*['\"]1\.8\.0['\"]", api)
    assert "migrations.migration_instance" in api
    assert "dev_enable.rpy" in source(".gitignore")


def test_b_retired_setting_owners_have_canonical_runtime_owners():
    runtime = executable_lines(sources([
        "game/Submods/MAICA_ChatSubmod/header.rpy",
        "game/Submods/MAICA_ChatSubmod/screen_subs.rpy",
        "game/python-packages/maica.py",
        "game/python-packages/maica_tasker_sub.py",
        "game/python-packages/maica_tasker_sub_sessionsender.py",
    ]))
    for old, new in RENAMES.items():
        assert_owner_renamed(runtime, old, new)


def test_c_setting_defaults_ranges_and_outbound_retirements():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    screens = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    outbound = sources(["game/Submods/MAICA_ChatSubmod/header.rpy", "game/python-packages/maica.py"])
    assert re.search(r"['\"]tz['\"]\s*:", header)
    assert re.search(r"(?:target_lang|language)['\"]?\s*:\s*['\"]auto['\"]", header)
    assert re.search(r"['\"]prompt_allow_nickname['\"]\s*:\s*True", header)
    for key in ("mf_sf_access_impl", "mf_const_sf_access", "mt_concl_memory"):
        assert re.search(r"['\"]{}['\"]\s*:\s*1\b".format(key), header)
        control = re.search(r".{0,180}%s.{0,240}" % key, screens, re.S)
        assert control and re.search(r"\b0\s*,\s*2\b", control.group(0))
        assert "ToggleDict" not in control.group(0)
    assert re.search(r"['\"]mt_disable_loop['\"]\s*:\s*True", header)
    assert re.search(r"mf_const_tools.{0,160}\b(?:0\s*,\s*2|2\b)", screens, re.S)
    assert re.search(r"session_len_limit.{0,200}28672", screens, re.S)
    assert "mt_extraction" not in executable_lines(outbound)
    assert "mas_sf_hcb" not in source("game/Submods/MAICA_ChatSubmod/persistent_filter.json")
    assert "mas_sf_hcb" not in source("game/python-packages/json_exporter.py")


def test_d_websocket_auth_resume_and_retired_cookie_protocol():
    maica = source("game/python-packages/maica.py")
    tasker = source("game/python-packages/maica_tasker_sub.py")
    sender = source("game/python-packages/maica_tasker_sub_sessionsender.py")
    screens = sources(["game/Submods/MAICA_ChatSubmod/header.rpy", "game/Submods/MAICA_ChatSubmod/screen_subs.rpy"])
    runtime = executable_lines("\n".join((maica, tasker, sender, screens)))
    assert re.search(r"['\"]type['\"]\s*:\s*['\"]auth['\"]", tasker)
    assert "maica_mcore_gen_start" in runtime
    for retired in ("MAICAWSCookiesHandler", "WSCookiesTask", "strict_mode"):
        assert retired not in runtime
    assert not re.search(r"['\"]cookie['\"]\s*:", runtime)
    for current in ("maica_quality_status", "maica_loop_warn_reset", "maica_core_streaming_continue"):
        assert current in runtime
    for retired in ("maica_dscl_status", "maica_loop_warn_finished", "maica_core_nostream_reply"):
        assert retired not in runtime


def test_e_mtrigger_mspire_and_mpostal_payload_owners():
    trigger = source("game/python-packages/maica_mtrigger.py")
    sender = source("game/python-packages/maica_tasker_sub_sessionsender.py")
    assert "alter_value" in trigger
    assert "alter_affection" not in executable_lines(trigger)
    assert re.search(r"['\"]inspire['\"]\s*:\s*\{[^}]*ctg_weight", sender, re.S)
    assert re.search(r"['\"]inspire['\"]\s*:\s*\{[^}]*use_cache", sender, re.S)
    assert re.search(r"['\"]inspire['\"]\s*:\s*\{\s*\}", sender)
    assert re.search(r"['\"]twk_super['\"]", sender)
    assert not re.search(r"['\"]ic_prep['\"]", sender)
    assert re.search(r"['\"]triggers['\"]\s*:", sender)
    assert not re.search(r"['\"]trigger['\"]\s*:", sender)


def test_f_rest_nickname_and_legality_contracts():
    vista = source("game/python-packages/maica_vista_files_manager.py")
    runtime = executable_lines(production_sources())
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    assert "/vista/list" in vista
    assert not re.search(r"['\"]/emotion(?:['\"/?]|$)", runtime)
    assert re.search(r"prompt_allow_nickname.{0,120}(?:True|1)", runtime, re.S)
    assert "prompt_allow_nickname" in header
    assert re.search(r"legality.{0,300}(?:latitude|longitude).{0,300}(?:latitude|longitude)", runtime, re.S)


def test_g_player_additions_byte_limits_shared_validation_and_backup():
    chat = source("game/Submods/MAICA_ChatSubmod/chat.rpy")
    screens = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    migration = source("game/Submods/MAICA_ChatSubmod/migrations.rpy")
    combined = chat + "\n" + screens + "\n" + migration
    assert re.search(r"\b512\b", combined)
    assert re.search(r"\b1536\b", combined)
    assert re.search(r"encode\s*\(\s*['\"]utf-8['\"]\s*\)", combined)
    helper_names = set(re.findall(r"def\s+(_?maica_\w*addition\w*)\s*\(", combined))
    assert helper_names
    assert any(name in chat and name in screens for name in helper_names)
    assert "_maica_v18_player_additions_backup" in migration
    assert "_maica_v18_player_additions_notice_seen" in migration
    assert not re.search(r"(?:mas_player_additions|player_additions).{0,240}(?:\[:1000\]|>\s*1000|1000\s*character)", executable_lines(combined), re.S)


def test_h_quality_asset_and_references_are_renamed():
    assert not (ASSETS / "dscl_pvn.png").exists()
    assert (ASSETS / "gen_quality_chk.png").is_file()
    refs = executable_lines(sources([
        "game/Submods/MAICA_ChatSubmod/screen_subs.rpy",
        "game/Submods/MAICA_ChatSubmod/trigger.rpy",
        "game/Submods/MAICA_ChatSubmod/trigger_labels.rpy",
        "game/Submods/MAICA_ChatSubmod/tl/screen_subs.rpy",
        "game/Submods/MAICA_ChatSubmod/tl/trigger.rpy",
        "game/Submods/MAICA_ChatSubmod/tl/trigger_labels.rpy",
    ]))
    assert "gen_quality_chk" in refs
    assert "dscl_pvn" not in refs


def test_retired_protocol_names_are_absent_from_production_runtime():
    runtime = executable_lines(production_sources())
    # Migration mappings are the sole compatibility boundary for renamed settings.
    retired = list(RENAMES) + [
        "maica_core_nostream_reply", "maica_dscl_status",
        "maica_loop_warn_finished", "MAICAWSCookiesHandler",
    ]
    found = [name for name in retired if name in runtime]
    assert not found, "retired production protocol/owners remain: {}".format(", ".join(found))


def test_persistent_filter_is_valid_json():
    data = json.loads(source("game/Submods/MAICA_ChatSubmod/persistent_filter.json"))
    assert isinstance(data, (list, dict))
