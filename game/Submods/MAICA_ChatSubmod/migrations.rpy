default persistent._maica_v18_player_additions_backup = None
default persistent._maica_v18_player_additions_notice_seen = False

init 998 python:
    import copy
    import maica_v13_migration

    def migration_1_8_0():
        maica_v13_migration.migrate_setting_values(
            persistent.maica_setting_dict,
            warning_callback=store.mas_submod_utils.submod_log.warning
        )
        maica_v13_migration.migrate_setting_values(
            persistent.maica_advanced_setting,
            persistent.maica_advanced_setting_status,
            warning_callback=store.mas_submod_utils.submod_log.warning
        )

        # "dscl" was a local quality-status receiver, never a backend trigger.
        persistent.maica_mtrigger_status.pop("dscl", None)
        store.maica.maica_instance.mtrigger_manager.enable_map.pop("dscl", None)

        additions = list(persistent.mas_player_additions or [])
        if persistent._maica_v18_player_additions_backup is None:
            persistent._maica_v18_player_additions_backup = copy.deepcopy(additions)
        filtered = maica_v13_migration.backup_and_filter_player_additions(
            additions,
            persistent._maica_v18_player_additions_backup,
            backup_initialized=True
        )
        if filtered != additions:
            if not persistent._maica_v18_player_additions_notice_seen:
                renpy.notify(_("MAICA: 部分自定义MFocus信息超过v1.3限制，完整内容已备份"))
                persistent._maica_v18_player_additions_notice_seen = True
        persistent.mas_player_additions = filtered

    migration_queue = [
        ("1.8.0", migration_1_8_0),
    ]
