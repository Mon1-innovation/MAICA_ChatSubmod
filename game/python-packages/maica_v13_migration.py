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
}

RETIRED_PERSISTENT_SETTINGS = (
    "ic_prep",
    "twk_super",
)

TRISTATE_SETTINGS = (
    "mf_sf_access_impl",
    "mf_const_sf_access",
    "mt_concl_memory",
)

try:
    TEXT_TYPES = (basestring,)
except NameError:
    TEXT_TYPES = (str,)

try:
    INTEGER_TYPES = (int, long)
except NameError:
    INTEGER_TYPES = (int,)


def utf8_byte_length(value):
    if isinstance(value, bytes):
        return len(value)
    if isinstance(value, TEXT_TYPES):
        return len(value.encode("utf-8"))
    return len(str(value).encode("utf-8"))


def _rename_values(values):
    for old, new in SETTING_RENAMES.items():
        if old in values:
            values[new] = values[old]


def remove_retired_persistent_settings(values, status=None):
    for key in RETIRED_PERSISTENT_SETTINGS:
        values.pop(key, None)
        if status is not None:
            status.pop(key, None)
    return values


def normalize_tristate_values(values, warning_callback=None):
    for key in TRISTATE_SETTINGS:
        existed = key in values
        value = values.get(key, 1)
        if isinstance(value, bool):
            value = int(value)
        elif not isinstance(value, INTEGER_TYPES) or value not in (0, 1, 2):
            if existed and warning_callback is not None:
                warning_callback(
                    "MAICA: invalid persisted value for {}; reset to 1".format(key)
                )
            value = 1
        values[key] = value
    return values


def migrate_setting_values(values, status=None, warning_callback=None):
    _rename_values(values)
    if status is not None:
        _rename_values(status)

    remove_retired_persistent_settings(values, status)
    normalize_tristate_values(values, warning_callback)

    if values.get("mf_const_tools") == 3:
        values["mf_const_tools"] = 2
    session_len_limit = values.get("session_len_limit")
    if (
        isinstance(session_len_limit, INTEGER_TYPES)
        and not isinstance(session_len_limit, bool)
        and session_len_limit > 28672
    ):
        values["session_len_limit"] = 28672

    return values


def backup_and_filter_player_additions(
    values,
    backup,
    limit=512,
    bytes_limit=1536,
    backup_initialized=False,
):
    if not backup_initialized and not backup:
        backup.extend(values)

    active = []
    for value in values:
        if len(active) >= limit:
            break
        if not isinstance(value, TEXT_TYPES):
            continue
        try:
            value_bytes = utf8_byte_length(value)
        except UnicodeError:
            continue
        if value_bytes > bytes_limit:
            continue
        active.append(value)
    return active
