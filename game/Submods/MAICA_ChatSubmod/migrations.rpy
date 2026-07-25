default persistent._maica_v18_player_additions_backup = None
default persistent._maica_v18_player_additions_notice_seen = False

init 998 python:
    import copy
    import maica_v13_migration

    chat_param_renames = {
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

    def migration_1_8_0():
        maica_v13_migration.migrate_setting_values(
            persistent.maica_setting_dict
        )
        maica_v13_migration.migrate_setting_values(
            persistent.maica_advanced_setting,
            persistent.maica_advanced_setting_status
        )

        additions = list(persistent.mas_player_additions or [])
        if persistent._maica_v18_player_additions_backup is None:
            persistent._maica_v18_player_additions_backup = copy.deepcopy(additions)
        filtered = maica_v13_migration.backup_and_filter_player_additions(
            additions,
            persistent._maica_v18_player_additions_backup
        )
        if filtered != additions:
            persistent._maica_v18_player_additions_notice_seen = False
        persistent.mas_player_additions = filtered

    migration_queue = [
        ("1.8.0", migration_1_8_0),
    ]
