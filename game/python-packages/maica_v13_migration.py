from __future__ import unicode_literals


SETTING_RENAMES = {
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

TRISTATE_SETTINGS = (
    "mf_sf_access_impl",
    "mf_const_sf_access",
    "mt_concl_memory",
)

try:
    TEXT_TYPES = (basestring,)
except NameError:
    TEXT_TYPES = (str,)


def _rename_values(values):
    for old, new in SETTING_RENAMES.items():
        if old in values and new not in values:
            values[new] = values[old]


def migrate_setting_values(values, status=None):
    _rename_values(values)
    if status is not None:
        _rename_values(status)

    for key in TRISTATE_SETTINGS:
        value = values.get(key)
        if isinstance(value, bool):
            values[key] = int(value)

    if values.get("mf_const_tools") == 3:
        values["mf_const_tools"] = 2

    return values


def backup_and_filter_player_additions(values, backup, limit=512, bytes_limit=1536):
    if not backup:
        backup.extend(values)

    active = []
    for value in values:
        if len(active) >= limit:
            break
        if not isinstance(value, TEXT_TYPES):
            continue
        if len(value.encode("utf-8")) > bytes_limit:
            continue
        active.append(value)
    return active
