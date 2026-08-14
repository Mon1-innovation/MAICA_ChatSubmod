default persistent._maica_v18_player_additions_backup = None
default persistent._maica_v18_player_additions_notice_seen = False

init 998 python:
    import copy
    import maica_v13_migration

    def migration_1_8_0():
        maica_v13_migration.migrate_setting_values(
            persistent.maica_setting_dict,
            warning_callback=store.mas_submod_utils.submod_log.warning,
            fill_missing_tristates=False
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
                renpy.notify(_("MAICA: Some custom MFocus information exceeded the v1.3 limit; the full content was backed up"))
                persistent._maica_v18_player_additions_notice_seen = True
        persistent.mas_player_additions = filtered

    def migration_1_8_6():
        # The chat event graph changed, so repair both seen labels and the
        # persistent conditional/action fields of events created by older builds.
        legacy_seen_map = {
            "maica_chr": "maica_chr2",
            "maica_chr_corrupted": "maica_chr_corrupted2",
            "maica_wants_preferences": "maica_wants_preferences2",
        }
        for old_label, new_label in legacy_seen_map.items():
            if persistent._seen_ever.get(old_label, False) or renpy.seen_label(old_label):
                persistent._seen_ever[new_label] = True

        main_ev = mas_getEV("maica_main")
        if (
                renpy.seen_label("maica_talking")
                or renpy.seen_label("maica_main")
                or (main_ev is not None and main_ev.shown_count > 0)
            ):
            persistent._seen_ever["maica_end_1"] = True

        # This event moved from EVE to GRE. Remove the old duplicate before
        # repairing the greeting event, otherwise mas_getEV can resolve stale data.
        store.evhand.event_database.pop("maica_chr_corrupted2", None)

        event_conditions = {
            "maica_chr2": "mas_getEV('maica_main').shown_count >= 3 and not renpy.seen_label('maica_chr2') and not renpy.seen_label('maica_chr_gone') and not renpy.seen_label('maica_chr_corrupted2')",
            "maica_chr_gone": "not maica_chr_exist and renpy.seen_label('maica_greeting') and not renpy.seen_label('maica_chr_gone')",
            "maica_chr_corrupted2": "renpy.seen_label('maica_greeting') and maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2')",
            "maica_wants_preferences2": "renpy.seen_label('maica_end_1') and mas_getEV('maica_main').shown_count >= 1 and not renpy.seen_label('maica_wants_preferences2')",
            "maica_pre_set_location": "renpy.seen_label('maica_end_1') and not renpy.seen_label('maica_pre_set_location')",
            "maica_pre_wants_mvista": "renpy.seen_label('maica_end_1') and mas_getEV('maica_main').shown_count >= 2 and not renpy.seen_label('maica_pre_wants_mvista')",
            "maica_greeting": "renpy.seen_label('maica_prepend_1') and not mas_isSpecialDay() and not renpy.seen_label('maica_greeting')",
            "maica_wants_mpostal": "renpy.seen_label('maica_end_1') and mas_getEV('maica_main').shown_count >= 1 and not mas_isSpecialDay() and not renpy.seen_label('maica_wants_mpostal') and not (maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2'))",
        }
        event_actions = {
            "maica_chr2": EV_ACT_QUEUE,
            "maica_chr_gone": EV_ACT_PUSH,
            "maica_chr_corrupted2": EV_ACT_UNLOCK,
            "maica_wants_preferences2": EV_ACT_QUEUE,
            "maica_pre_set_location": EV_ACT_QUEUE,
            "maica_pre_wants_mvista": EV_ACT_QUEUE,
            "maica_greeting": EV_ACT_UNLOCK,
            "maica_wants_mpostal": EV_ACT_UNLOCK,
        }
        for eventlabel, conditional in event_conditions.items():
            ev = mas_getEV(eventlabel)
            if ev is not None:
                ev.conditional = conditional
                ev.action = event_actions[eventlabel]

        for eventlabel in (
                "maica_chr2",
                "maica_wants_preferences2",
                "maica_pre_set_location",
                "maica_pre_wants_mvista",
            ):
            ev = mas_getEV(eventlabel)
            if ev is not None:
                ev.random = True

        reread_sources = {
            "maica_prepend_reread": "maica_prepend_1",
            "maica_chr_reread": "maica_chr2",
            "maica_wants_preferences_reread": "maica_wants_preferences2",
            "maica_wants_mspire_reread": "maica_wants_mspire",
            "maica_wants_mpostal_reread": "maica_wants_mpostal",
            "maica_set_location_reread": "maica_pre_set_location",
            "maica_wants_mvista_reread": "maica_pre_wants_mvista",
        }
        for reread_label, source_label in reread_sources.items():
            ev = mas_getEV(reread_label)
            if ev is None:
                continue
            ev.conditional = "renpy.seen_label('{0}') and not renpy.seen_label('{1}')".format(
                source_label,
                reread_label
            )
            ev.action = EV_ACT_UNLOCK
            ev.unlocked = renpy.seen_label(source_label)

    def migration_1_8_7():
        event_conditions = {
            "maica_wants_preferences2": "maica_has_successful_chat() and mas_getEV('maica_main').shown_count >= 1 and not renpy.seen_label('maica_wants_preferences2')",
            "maica_pre_set_location": "maica_has_successful_chat() and not renpy.seen_label('maica_pre_set_location')",
            "maica_pre_wants_mvista": "maica_has_successful_chat() and mas_getEV('maica_main').shown_count >= 2 and not renpy.seen_label('maica_pre_wants_mvista')",
            "maica_wants_mpostal": "maica_has_successful_chat() and mas_getEV('maica_main').shown_count >= 1 and not mas_isSpecialDay() and not renpy.seen_label('maica_wants_mpostal') and not (maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2'))",
        }
        for eventlabel, conditional in event_conditions.items():
            ev = mas_getEV(eventlabel)
            if ev is not None:
                ev.conditional = conditional

    migration_queue = [
        ("1.8.0", migration_1_8_0),
        ("1.8.6", migration_1_8_6),
        ("1.8.7", migration_1_8_7),
    ]
