default persistent._maica_v18_player_additions_backup = None
default persistent._maica_v18_player_additions_notice_seen = False
default persistent._maica_successful_chat_count = 0

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
            "maica_chr2": "maica_get_successful_chat_count() >= 4 and not renpy.seen_label('maica_chr2') and not renpy.seen_label('maica_chr_gone') and not renpy.seen_label('maica_chr_corrupted2')",
            "maica_chr_gone": "not maica_chr_exist and renpy.seen_label('maica_greeting') and not renpy.seen_label('maica_chr_gone')",
            "maica_chr_corrupted2": "renpy.seen_label('maica_greeting') and maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2')",
            "maica_wants_preferences2": "maica_get_successful_chat_count() >= 2 and not renpy.seen_label('maica_wants_preferences2')",
            "maica_pre_set_location": "maica_has_successful_chat() and not renpy.seen_label('maica_pre_set_location')",
            "maica_pre_wants_mvista": "maica_get_successful_chat_count() >= 3 and not renpy.seen_label('maica_pre_wants_mvista')",
            "maica_greeting": "renpy.seen_label('maica_prepend_1') and not mas_isSpecialDay() and not renpy.seen_label('maica_greeting')",
            "maica_wants_mpostal": "maica_get_successful_chat_count() >= 2 and not mas_isSpecialDay() and not renpy.seen_label('maica_wants_mpostal') and not (maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2'))",
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
            "maica_wants_preferences2": "maica_get_successful_chat_count() >= 2 and not renpy.seen_label('maica_wants_preferences2')",
            "maica_pre_set_location": "maica_has_successful_chat() and not renpy.seen_label('maica_pre_set_location')",
            "maica_pre_wants_mvista": "maica_get_successful_chat_count() >= 3 and not renpy.seen_label('maica_pre_wants_mvista')",
            "maica_wants_mpostal": "maica_get_successful_chat_count() >= 2 and not mas_isSpecialDay() and not renpy.seen_label('maica_wants_mpostal') and not (maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2'))",
        }
        for eventlabel, conditional in event_conditions.items():
            ev = mas_getEV(eventlabel)
            if ev is not None:
                ev.conditional = conditional

    def migration_1_8_8():
        # Older builds did not retain per-attempt results. Preserve their main
        # event count as a compatibility baseline without assuming that the
        # separate greeting conversation succeeded.
        main_ev = mas_getEV("maica_main")
        legacy_main_count = max(
            0,
            getattr(main_ev, "shown_count", 0) or 0
        )
        persistent._maica_successful_chat_count = max(
            persistent._maica_successful_chat_count or 0,
            legacy_main_count
        )

        event_conditions = {
            "maica_chr2": "maica_get_successful_chat_count() >= 4 and not renpy.seen_label('maica_chr2') and not renpy.seen_label('maica_chr_gone') and not renpy.seen_label('maica_chr_corrupted2')",
            "maica_wants_preferences2": "maica_get_successful_chat_count() >= 2 and not renpy.seen_label('maica_wants_preferences2')",
            "maica_pre_set_location": "maica_has_successful_chat() and not renpy.seen_label('maica_pre_set_location')",
            "maica_pre_wants_mvista": "maica_get_successful_chat_count() >= 3 and not renpy.seen_label('maica_pre_wants_mvista')",
            "maica_wants_mpostal": "maica_get_successful_chat_count() >= 2 and not mas_isSpecialDay() and not renpy.seen_label('maica_wants_mpostal') and not (maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2'))",
        }
        for eventlabel, conditional in event_conditions.items():
            ev = mas_getEV(eventlabel)
            if ev is not None:
                ev.conditional = conditional

    def migration_1_8_9():
        queued_event_conditions = {
            "maica_chr2": "maica_get_successful_chat_count() >= 4 and not renpy.seen_label('maica_chr2') and not renpy.seen_label('maica_chr_gone') and not renpy.seen_label('maica_chr_corrupted2')",
            "maica_wants_preferences2": "maica_get_successful_chat_count() >= 2 and not renpy.seen_label('maica_wants_preferences2')",
            "maica_pre_set_location": "maica_has_successful_chat() and not renpy.seen_label('maica_pre_set_location')",
            "maica_pre_wants_mvista": "maica_get_successful_chat_count() >= 3 and not renpy.seen_label('maica_pre_wants_mvista')",
        }
        for eventlabel, conditional in queued_event_conditions.items():
            ev = mas_getEV(eventlabel)
            if ev is not None:
                ev.conditional = conditional
                ev.action = EV_ACT_QUEUE
                ev.random = False

        # MAS addEvent preserves existing persistent Event objects, including
        # their old greeting and priority rules, so repair those explicitly.
        greeting_repairs = {
            "maica_chr_corrupted2": (
                "persistent._mas_greeting_type is None and not mas_isSpecialDay() and renpy.seen_label('maica_greeting') and maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2')",
                0,
            ),
            "maica_greeting": (
                "persistent._mas_greeting_type is None and renpy.seen_label('maica_prepend_1') and not mas_isSpecialDay() and not renpy.seen_label('maica_greeting')",
                20,
            ),
            "maica_wants_mpostal": (
                "persistent._mas_greeting_type is None and maica_get_successful_chat_count() >= 2 and not mas_isSpecialDay() and not renpy.seen_label('maica_wants_mpostal') and not (maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2'))",
                20,
            ),
        }
        for eventlabel, (conditional, priority) in greeting_repairs.items():
            ev = mas_getEV(eventlabel)
            if ev is not None:
                ev.conditional = conditional
                ev.action = None
                ev.unlocked = True
                ev.rules.update(MASGreetingRule.create_rule(skip_visual=True))
                ev.rules.update(MASPriorityRule.create_rule(priority))

        reread_repairs = {
            "maica_prepend_reread": (
                "renpy.seen_label('maica_prepend_2') and not renpy.seen_label('maica_prepend_reread')",
                renpy.seen_label("maica_prepend_2") or renpy.seen_label("maica_prepend_reread"),
            ),
            "maica_chr_reread": (
                "(renpy.seen_label('maica_chr2') or renpy.seen_label('maica_chr_gone') or renpy.seen_label('maica_chr_corrupted2')) and not renpy.seen_label('maica_chr_reread')",
                (
                    renpy.seen_label("maica_chr2")
                    or renpy.seen_label("maica_chr_gone")
                    or renpy.seen_label("maica_chr_corrupted2")
                    or renpy.seen_label("maica_chr_reread")
                ),
            ),
        }
        for eventlabel, (conditional, unlocked) in reread_repairs.items():
            ev = mas_getEV(eventlabel)
            if ev is not None:
                ev.conditional = conditional
                ev.action = EV_ACT_UNLOCK
                ev.unlocked = unlocked

        mas_rebuildEventLists()

    def migration_1_8_10():
        location_label_map = {
            "maica_pre_set_location": "maica_wants_location2",
            "maica_set_location_reread": "maica_mods_location",
        }
        location_seen = {}

        for old_label, new_label in location_label_map.items():
            old_ev = mas_getEV(old_label)
            new_ev = mas_getEV(new_label)
            old_seen = (
                persistent._seen_ever.get(old_label, False)
                or renpy.seen_label(old_label)
                or (
                    old_ev is not None
                    and old_ev.shown_count > 0
                )
            )
            location_seen[old_label] = old_seen

            if old_seen:
                persistent._seen_ever[new_label] = True
            persistent._seen_ever.pop(old_label, None)

            if old_ev is not None and new_ev is not None:
                new_ev.shown_count = max(new_ev.shown_count, old_ev.shown_count)
                if (
                        old_ev.last_seen is not None
                        and (
                            new_ev.last_seen is None
                            or old_ev.last_seen > new_ev.last_seen
                        )
                    ):
                    new_ev.last_seen = old_ev.last_seen

        # Preserve queued references created before the event labels were renamed.
        for index, item in enumerate(persistent.event_list):
            if isinstance(item, tuple) and item:
                new_label = location_label_map.get(item[0])
                if new_label is not None:
                    persistent.event_list[index] = (new_label,) + item[1:]
            elif item in location_label_map:
                persistent.event_list[index] = location_label_map[item]

        for attr_name in ("_mas_player_bookmarked", "_mas_player_derandomed"):
            topic_list = getattr(persistent, attr_name, None)
            if topic_list is not None:
                setattr(
                    persistent,
                    attr_name,
                    [location_label_map.get(label, label) for label in topic_list]
                )

        if persistent.flagged_monikatopic in location_label_map:
            persistent.flagged_monikatopic = location_label_map[
                persistent.flagged_monikatopic
            ]

        intro_ev = mas_getEV("maica_wants_location2")
        if intro_ev is not None:
            intro_ev.conditional = "maica_has_successful_chat() and not renpy.seen_label('maica_wants_location2')"
            intro_ev.action = EV_ACT_QUEUE
            intro_ev.random = False

        reread_ev = mas_getEV("maica_wants_location_reread")
        if reread_ev is not None:
            reread_ev.conditional = "renpy.seen_label('maica_wants_location2') and not renpy.seen_label('maica_wants_location_reread')"
            reread_ev.action = EV_ACT_UNLOCK

        intro_seen = (
            location_seen.get("maica_pre_set_location", False)
            or renpy.seen_label("maica_wants_location2")
        )
        if intro_seen:
            mas_unlockEVL("maica_mods_location", "EVE")
            mas_unlockEVL("maica_wants_location_reread", "EVE")

        for old_label in location_label_map:
            persistent.event_database.pop(old_label, None)

        mas_rebuildEventLists()

    migration_queue = [
        ("1.8.0", migration_1_8_0),
        ("1.8.6", migration_1_8_6),
        ("1.8.7", migration_1_8_7),
        ("1.8.8", migration_1_8_8),
        ("1.8.9", migration_1_8_9),
        ("1.8.10", migration_1_8_10),
    ]
