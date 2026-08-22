default persistent._maica_v18_player_additions_backup = None
default persistent._maica_v18_player_additions_notice_seen = False
default persistent._maica_successful_chat_count = 0

init 998 python:
    import copy
    import maica_v13_migration

    _MAICA_UNSET = object()

    def _maica_state_log(level, message):
        """Write state-repair diagnostics without making migrations depend on a logger stub."""
        try:
            logger = store.mas_submod_utils.submod_log
            getattr(logger, level)(message)
        except Exception:
            # Runtime logging is best effort. A broken logger must not block a save migration.
            pass

    def _maica_get_event(eventlabel):
        try:
            return mas_getEV(eventlabel)
        except Exception:
            return None

    def _maica_seen_ever(eventlabel):
        try:
            seen_ever = getattr(persistent, "_seen_ever", None) or {}
            return bool(seen_ever.get(eventlabel, False))
        except Exception:
            return False

    def _maica_seen_label(eventlabel):
        try:
            return bool(renpy.seen_label(eventlabel))
        except Exception:
            return False

    def _maica_mark_seen(eventlabel):
        """Keep canonical seen data usable when an old label/event supplied the evidence."""
        try:
            seen_ever = getattr(persistent, "_seen_ever", None)
            if seen_ever is not None:
                seen_ever[eventlabel] = True
        except Exception:
            pass

    def _maica_topic_seen(eventlabel, legacy_labels=()):
        """Return (seen, evidence) using every persistent signal available to MAS."""
        candidates = (eventlabel,) + tuple(legacy_labels)
        for candidate in candidates:
            if _maica_seen_label(candidate) or _maica_seen_ever(candidate):
                if candidate != eventlabel:
                    _maica_mark_seen(eventlabel)
                return True, "seen:{}".format(candidate)

            event = _maica_get_event(candidate)
            if event is not None and (getattr(event, "shown_count", 0) or 0) > 0:
                _maica_mark_seen(eventlabel)
                return True, "shown_count:{}".format(candidate)

        return False, "not-seen"

    def maica_get_topic_progress():
        """Derive MAICA progression without trusting stale Event.unlocked fields."""
        location_seen, location_evidence = _maica_topic_seen(
            "maica_wants_location2",
            ("maica_pre_set_location",)
        )
        preferences_seen, preferences_evidence = _maica_topic_seen(
            "maica_wants_preferences2",
            ("maica_wants_preferences",)
        )
        mspire_seen, mspire_evidence = _maica_topic_seen("maica_wants_mspire")
        mpostal_seen, mpostal_evidence = _maica_topic_seen("maica_wants_mpostal")
        mvista_seen, mvista_evidence = _maica_topic_seen("maica_pre_wants_mvista")
        if getattr(persistent, "_maica_vista_enabled", False) and not mvista_seen:
            # This flag existed in builds before the introduction label became the
            # source of truth. Preserve it as migration evidence, never as a
            # standalone unlock state.
            mvista_seen = True
            mvista_evidence = "legacy:_maica_vista_enabled"
            _maica_mark_seen("maica_pre_wants_mvista")

        character_seen = False
        character_evidence = "not-seen"
        for character_label in (
                "maica_chr2",
                "maica_chr_gone",
                "maica_chr_corrupted2",
            ):
            legacy_labels = {
                "maica_chr2": ("maica_chr",),
                "maica_chr_corrupted2": ("maica_chr_corrupted",),
            }.get(character_label, ())
            seen, evidence = _maica_topic_seen(character_label, legacy_labels)
            if seen:
                character_seen = True
                character_evidence = "{} ({})".format(character_label, evidence)
                break

        heaven_seen = False
        heaven_evidence = "not-seen"
        heaven_intro_seen, heaven_intro_evidence = _maica_topic_seen("maica_prepend_2")
        for heaven_label in (
                "maica_end_1",
                "maica_main",
                "maica_talking",
            ):
            seen, evidence = _maica_topic_seen(heaven_label)
            if seen:
                heaven_seen = True
                heaven_evidence = "{} ({})".format(heaven_label, evidence)
                break
        if heaven_intro_seen:
            heaven_seen = True
            heaven_evidence = "maica_prepend_2 ({})".format(heaven_intro_evidence)

        # Any completed downstream topic proves that the player reached the
        # Heaven Forest flow, even when an old build failed to persist its intro
        # label. Reread-only events deliberately do not count as proof.
        downstream_progress = (
            ("location", location_seen, location_evidence),
            ("preferences", preferences_seen, preferences_evidence),
            ("mspire", mspire_seen, mspire_evidence),
            ("mpostal", mpostal_seen, mpostal_evidence),
            ("mvista", mvista_seen, mvista_evidence),
            ("character", character_seen, character_evidence),
        )
        downstream_evidence = "not-seen"
        for downstream_label, downstream_seen, evidence in downstream_progress:
            if downstream_seen:
                downstream_evidence = "downstream:{} ({})".format(
                    downstream_label,
                    evidence,
                )
                break
        main_ready = heaven_seen or downstream_evidence != "not-seen"

        return {
            "main_ready": main_ready,
            "main_evidence": heaven_evidence if heaven_seen else downstream_evidence,
            "heaven_seen": heaven_seen,
            "heaven_evidence": heaven_evidence,
            "heaven_intro_seen": heaven_intro_seen,
            "heaven_intro_evidence": heaven_intro_evidence,
            "location_seen": location_seen,
            "location_evidence": location_evidence,
            "preferences_seen": preferences_seen,
            "preferences_evidence": preferences_evidence,
            "mspire_seen": mspire_seen,
            "mspire_evidence": mspire_evidence,
            "mpostal_seen": mpostal_seen,
            "mpostal_evidence": mpostal_evidence,
            "mvista_seen": mvista_seen,
            "mvista_evidence": mvista_evidence,
            "character_seen": character_seen,
            "character_evidence": character_evidence,
        }

    def _maica_set_event(eventlabel, unlocked=_MAICA_UNSET,
                         conditional=_MAICA_UNSET, action=_MAICA_UNSET,
                         random=_MAICA_UNSET, pool=_MAICA_UNSET,
                         clear_unlock_date=False):
        """Apply a small Event contract and report whether persistent state changed."""
        event = _maica_get_event(eventlabel)
        if event is None:
            return False, None, None

        changed = False
        before = getattr(event, "unlocked", False)
        if unlocked is not _MAICA_UNSET and before != unlocked:
            event.unlocked = unlocked
            changed = True
        if conditional is not _MAICA_UNSET and getattr(event, "conditional", None) != conditional:
            event.conditional = conditional
            changed = True
        if action is not _MAICA_UNSET and getattr(event, "action", None) != action:
            event.action = action
            changed = True
        if random is not _MAICA_UNSET and getattr(event, "random", False) != random:
            event.random = random
            changed = True
        if pool is not _MAICA_UNSET and getattr(event, "pool", False) != pool:
            event.pool = pool
            changed = True
        if clear_unlock_date and getattr(event, "unlock_date", None) is not None:
            event.unlock_date = None
            changed = True

        return changed, before, getattr(event, "unlocked", False)

    def _maica_set_no_unlock_rule(eventlabel):
        event = _maica_get_event(eventlabel)
        if event is None:
            return False
        rules = getattr(event, "rules", None)
        if rules is None:
            rules = {}
            event.rules = rules
        if "no_unlock" not in rules or rules.get("no_unlock") is not None:
            rules["no_unlock"] = None
            return True
        return False

    def _maica_action(name, fallback):
        return globals().get(name, fallback)

    def _maica_record_state_change(changes, eventlabel, expected, before,
                                   evidence, reason):
        if before == expected:
            return
        changes.append(eventlabel)
        _maica_state_log(
            "warning",
            "MAICA: topic state corrected ({}) {} unlocked {} -> {} ({})".format(
                reason,
                eventlabel,
                bool(before),
                bool(expected),
                evidence,
            )
        )

    def maica_reconcile_topic_state(reason="startup", repair_contracts=False):
        """Reconcile all MAICA topic unlocks with the current progression graph."""
        progress = maica_get_topic_progress()
        changes = []
        contracts_changed = False
        queue_action = _maica_action("EV_ACT_QUEUE", "queue")
        push_action = _maica_action("EV_ACT_PUSH", "push")
        unlock_action = _maica_action("EV_ACT_UNLOCK", "unlock")

        # Internal dispatch events are never user-selectable. Their conditional
        # and action fields remain active so a later threshold can queue them.
        internal_contracts = {
            "maica_prepend_1": (
                "not renpy.seen_label('maica_prepend_1')",
                queue_action,
                True,
            ),
            "maica_wants_location2": (
                "maica_has_successful_chat() and not renpy.seen_label('maica_wants_location2')",
                queue_action,
                False,
            ),
            "maica_wants_preferences2": (
                "maica_get_successful_chat_count() >= 2 and not renpy.seen_label('maica_wants_preferences2')",
                queue_action,
                False,
            ),
            "maica_pre_wants_mvista": (
                "maica_get_successful_chat_count() >= 3 and not renpy.seen_label('maica_pre_wants_mvista')",
                queue_action,
                False,
            ),
            "maica_chr2": (
                "maica_get_successful_chat_count() >= 4 and not renpy.seen_label('maica_chr2') and not renpy.seen_label('maica_chr_gone') and not renpy.seen_label('maica_chr_corrupted2')",
                queue_action,
                False,
            ),
            "maica_chr_gone": (
                "not maica_chr_exist and renpy.seen_label('maica_prepend_2') and not renpy.seen_label('maica_chr_gone')",
                push_action,
                False,
            ),
            "maica_wants_mspire": (None, None, False),
        }
        for eventlabel, (conditional, action, is_random) in internal_contracts.items():
            changed, before, expected = _maica_set_event(
                eventlabel,
                unlocked=False,
                conditional=conditional if repair_contracts else _MAICA_UNSET,
                action=action if repair_contracts else _MAICA_UNSET,
                random=is_random if repair_contracts else _MAICA_UNSET,
                pool=False if repair_contracts else _MAICA_UNSET,
                clear_unlock_date=True,
            )
            contracts_changed = contracts_changed or changed
            if before is not None:
                _maica_record_state_change(
                    changes, eventlabel, False, before,
                    "internal-dispatch", reason
                )

        # Processing events must remain hidden from both topic menus. MSpire's
        # conditional is still active, while the two MPostal workers are pushed
        # by their dedicated loop plugins.
        processing_contracts = {
            "maica_mspire": (
                "renpy.seen_label('maica_wants_mspire') and spire_has_past(datetime.timedelta(minutes=persistent.maica_setting_dict.get('mspire_interval'))) and persistent.maica_setting_dict.get('mspire_enable') and not store.maica.maica_instance.is_in_exception()",
                None,
            ),
            "maica_mpostal_received": (None, None),
            "maica_mpostal_replyed": (None, None),
        }
        for eventlabel, (conditional, action) in processing_contracts.items():
            changed, before, expected = _maica_set_event(
                eventlabel,
                unlocked=False,
                conditional=conditional if repair_contracts else _MAICA_UNSET,
                action=action if repair_contracts else _MAICA_UNSET,
                random=False if repair_contracts else _MAICA_UNSET,
                pool=False if repair_contracts else _MAICA_UNSET,
                clear_unlock_date=True,
            )
            contracts_changed = contracts_changed or changed
            if before is not None:
                _maica_record_state_change(
                    changes, eventlabel, False, before,
                    "internal-processing", reason
                )

        # Main topic and its two direct setting topics.
        user_topics = {
            "maica_main": (progress["main_ready"], progress["main_evidence"]),
            "maica_mods_location": (progress["location_seen"], progress["location_evidence"]),
            "maica_mods_preferences": (progress["preferences_seen"], progress["preferences_evidence"]),
        }
        for eventlabel, (expected, evidence) in user_topics.items():
            changed, before, current = _maica_set_event(
                eventlabel,
                unlocked=expected,
                random=False if repair_contracts else _MAICA_UNSET,
                pool=True if repair_contracts else _MAICA_UNSET,
                conditional=None if repair_contracts else _MAICA_UNSET,
                action=None if repair_contracts else _MAICA_UNSET,
                clear_unlock_date=not expected,
            )
            contracts_changed = contracts_changed or changed
            if repair_contracts:
                contracts_changed = _maica_set_no_unlock_rule(eventlabel) or contracts_changed
            if before is not None:
                _maica_record_state_change(
                    changes, eventlabel, expected, before, evidence, reason
                )

        reread_topics = {
            "maica_prepend_reread": (progress["heaven_intro_seen"], progress["heaven_intro_evidence"]),
            "maica_wants_location_reread": (progress["location_seen"], progress["location_evidence"]),
            "maica_wants_preferences_reread": (progress["preferences_seen"], progress["preferences_evidence"]),
            "maica_wants_mspire_reread": (progress["mspire_seen"], progress["mspire_evidence"]),
            "maica_wants_mpostal_reread": (progress["mpostal_seen"], progress["mpostal_evidence"]),
            "maica_wants_mvista_reread": (progress["mvista_seen"], progress["mvista_evidence"]),
            "maica_chr_reread": (progress["character_seen"], progress["character_evidence"]),
        }
        reread_sources = {
            "maica_prepend_reread": "maica_prepend_2",
            "maica_wants_location_reread": "maica_wants_location2",
            "maica_wants_preferences_reread": "maica_wants_preferences2",
            "maica_wants_mspire_reread": "maica_wants_mspire",
            "maica_wants_mpostal_reread": "maica_wants_mpostal",
            "maica_wants_mvista_reread": "maica_pre_wants_mvista",
            "maica_chr_reread": "maica_chr2",
        }
        for eventlabel, (expected, evidence) in reread_topics.items():
            source_label = reread_sources[eventlabel]
            conditional = _MAICA_UNSET
            if repair_contracts:
                if eventlabel == "maica_chr_reread":
                    conditional = (
                        "(renpy.seen_label('maica_chr2') or "
                        "renpy.seen_label('maica_chr_gone') or "
                        "renpy.seen_label('maica_chr_corrupted2')) "
                        "and not renpy.seen_label('maica_chr_reread')"
                    )
                else:
                    conditional = (
                        "renpy.seen_label('{}') and not renpy.seen_label('{}')".format(
                            source_label,
                            eventlabel,
                        )
                    )
            changed, before, current = _maica_set_event(
                eventlabel,
                unlocked=expected,
                conditional=conditional,
                action=unlock_action if repair_contracts else _MAICA_UNSET,
                random=False if repair_contracts else _MAICA_UNSET,
                pool=True if repair_contracts else _MAICA_UNSET,
                clear_unlock_date=not expected,
            )
            contracts_changed = contracts_changed or changed
            if repair_contracts:
                contracts_changed = _maica_set_no_unlock_rule(eventlabel) or contracts_changed
            if before is not None:
                _maica_record_state_change(
                    changes, eventlabel, expected, before, evidence, reason
                )

        # Greeting events are always registered as selectable. Their conditionals
        # are the gate; locking them would prevent a later normal greeting retry.
        greeting_contracts = {
            "maica_greeting": (
                "persistent._mas_greeting_type is None and renpy.seen_label('maica_prepend_1') and not mas_isSpecialDay() and not mas_isplayer_bday() and not renpy.seen_label('maica_prepend_2')",
                20,
            ),
            "maica_wants_mpostal": (
                "persistent._mas_greeting_type is None and maica_get_successful_chat_count() >= 2 and not mas_isSpecialDay() and not mas_isplayer_bday() and not renpy.seen_label('maica_wants_mpostal') and not (maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2'))",
                20,
            ),
            "maica_chr_corrupted2": (
                "persistent._mas_greeting_type is None and not mas_isSpecialDay() and not mas_isplayer_bday() and renpy.seen_label('maica_prepend_2') and maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2')",
                0,
            ),
        }
        for eventlabel, (conditional, priority) in greeting_contracts.items():
            changed, before, current = _maica_set_event(
                eventlabel,
                unlocked=True,
                conditional=conditional if repair_contracts else _MAICA_UNSET,
                action=None if repair_contracts else _MAICA_UNSET,
            )
            contracts_changed = contracts_changed or changed
            if repair_contracts:
                event = _maica_get_event(eventlabel)
                if event is not None:
                    try:
                        rules = getattr(event, "rules", None)
                        if rules is None:
                            rules = {}
                            event.rules = rules
                        previous_rules = dict(rules)
                        rules.update(MASGreetingRule.create_rule(
                            skip_visual=True
                        ) if eventlabel != "maica_wants_mpostal" else MASGreetingRule.create_rule(
                            forced_exp="monika 3hubsa"
                        ))
                        rules.update(MASPriorityRule.create_rule(priority))
                        contracts_changed = (rules != previous_rules) or contracts_changed
                    except Exception:
                        pass

        state_labels = (
            "main", "location", "preferences", "mspire", "mpostal",
            "mvista", "character",
        )
        state_summary = ", ".join(
            "{}={}".format(label, bool(progress["{}_seen".format(label)] if label != "main" else progress["main_ready"]))
            for label in state_labels
        )
        evidence_summary = ", ".join(
            "{}={}".format(
                label,
                progress["{}_evidence".format(label)] if label != "main" else progress["main_evidence"],
            )
            for label in state_labels
        )
        _maica_state_log(
            "info",
            "MAICA: topic state check ({}) [{}]; evidence=[{}]; corrected={}".format(
                reason,
                state_summary,
                evidence_summary,
                len(changes),
            )
        )

        if contracts_changed:
            try:
                mas_rebuildEventLists()
            except Exception:
                pass

        return {
            "progress": progress,
            "changes": changes,
            "changed": bool(contracts_changed),
        }

    def migration_1_8_17():
        # Remove stale EVE registrations left by label renames or by the old
        # character-file greeting registration. Seen history is kept in
        # _seen_ever and Ren'Py's label database; only obsolete Event objects
        # are removed here. Handle both persistent and runtime DB references.
        obsolete_eventlabels = (
            "maica_pre_set_location",
            "maica_set_location_reread",
            "maica_chr",
            "maica_chr_corrupted",
            "maica_wants_preferences",
            "maica_chr_corrupted2",
        )
        legacy_progress_map = {
            "maica_pre_set_location": "maica_wants_location2",
            "maica_chr": "maica_chr2",
            "maica_chr_corrupted": "maica_chr_corrupted2",
            "maica_wants_preferences": "maica_wants_preferences2",
        }
        obsolete_removed = False
        for event_db in (
                getattr(persistent, "event_database", None),
                getattr(getattr(store, "evhand", None), "event_database", None),
            ):
            try:
                if event_db is not None:
                    for old_label, new_label in legacy_progress_map.items():
                        old_event = event_db.get(old_label)
                        if (
                                _maica_seen_label(old_label)
                                or _maica_seen_ever(old_label)
                                or (
                                    old_event is not None
                                    and (getattr(old_event, "shown_count", 0) or 0) > 0
                                )
                            ):
                            _maica_mark_seen(new_label)
                    old_corrupted_event = event_db.get("maica_chr_corrupted2")
                    if (
                            old_corrupted_event is not None
                            and (getattr(old_corrupted_event, "shown_count", 0) or 0) > 0
                        ):
                        _maica_mark_seen("maica_chr_corrupted2")
                    for eventlabel in obsolete_eventlabels:
                        if eventlabel in event_db:
                            event_db.pop(eventlabel, None)
                            obsolete_removed = True
            except Exception:
                pass
        maica_reconcile_topic_state(
            reason="migration_1_8_17",
            repair_contracts=True,
        )
        if obsolete_removed:
            try:
                mas_rebuildEventLists()
            except Exception:
                pass

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

    def migration_1_8_11():
        # Entering maica_greeting marks it seen before the player chooses a
        # door action. Use the first shared post-door label as completion so a
        # safe quit from the black-screen menu does not consume the intro.
        event_conditions = {
            "maica_greeting": "persistent._mas_greeting_type is None and renpy.seen_label('maica_prepend_1') and not mas_isSpecialDay() and not mas_isplayer_bday() and not renpy.seen_label('maica_prepend_2')",
            "maica_chr_corrupted2": "persistent._mas_greeting_type is None and not mas_isSpecialDay() and not mas_isplayer_bday() and renpy.seen_label('maica_prepend_2') and maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2')",
            "maica_wants_mpostal": "persistent._mas_greeting_type is None and maica_get_successful_chat_count() >= 2 and not mas_isSpecialDay() and not mas_isplayer_bday() and not renpy.seen_label('maica_wants_mpostal') and not (maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2'))",
            "maica_chr_gone": "not maica_chr_exist and renpy.seen_label('maica_prepend_2') and not renpy.seen_label('maica_chr_gone')",
        }
        for eventlabel, conditional in event_conditions.items():
            ev = mas_getEV(eventlabel)
            if ev is not None:
                ev.conditional = conditional

        mpostal_ev = mas_getEV("maica_wants_mpostal")
        if mpostal_ev is not None:
            mpostal_ev.rules.update(
                MASGreetingRule.create_rule(forced_exp="monika 3hubsa")
            )

        mas_rebuildEventLists()

    def migration_1_8_12():
        # MAS preserves these fields from existing persistent Event objects.
        # Keep internal dispatch events out of both Talk menu branches even if
        # an older registration left one unlocked or pooled.
        internal_eventlabels = (
            "maica_prepend_1",
            "maica_wants_location2",
            "maica_wants_preferences2",
            "maica_wants_mspire",
            "maica_pre_wants_mvista",
            "maica_chr_gone",
            "maica_chr2",
            "maica_mspire",
            "maica_mpostal_received",
            "maica_mpostal_replyed",
        )
        for eventlabel in internal_eventlabels:
            ev = mas_getEV(eventlabel)
            if ev is not None:
                ev.unlocked = False
                ev.unlock_date = None
                ev.pool = False

        mvista_ev = mas_getEV("maica_pre_wants_mvista")
        mvista_reread_ev = mas_getEV("maica_wants_mvista_reread")
        mvista_seen = (
            renpy.seen_label("maica_pre_wants_mvista")
            or (
                mvista_ev is not None
                and mvista_ev.shown_count > 0
            )
        )
        if mvista_reread_ev is not None:
            mvista_reread_ev.unlocked = (
                mvista_seen
                or renpy.seen_label("maica_wants_mvista_reread")
                or mvista_reread_ev.shown_count > 0
            )

        mas_rebuildEventLists()

    def migration_1_8_13():
        # MVista unlock state is now derived from its introduction label. Carry
        # forward every reliable unlock signal used by older builds.
        mvista_ev = mas_getEV("maica_pre_wants_mvista")
        mvista_reread_ev = mas_getEV("maica_wants_mvista_reread")
        mvista_seen = (
            getattr(persistent, "_maica_vista_enabled", False)
            or renpy.seen_label("maica_pre_wants_mvista")
            or (
                mvista_ev is not None
                and mvista_ev.shown_count > 0
            )
            or renpy.seen_label("maica_wants_mvista_reread")
            or (
                mvista_reread_ev is not None
                and mvista_reread_ev.shown_count > 0
            )
        )
        if mvista_seen:
            persistent._seen_ever["maica_pre_wants_mvista"] = True

        if mvista_reread_ev is not None:
            mvista_reread_ev.unlocked = mvista_seen

        mas_rebuildEventLists()

    migration_queue = [
        ("1.8.0", migration_1_8_0),
        ("1.8.6", migration_1_8_6),
        ("1.8.7", migration_1_8_7),
        ("1.8.8", migration_1_8_8),
        ("1.8.9", migration_1_8_9),
        ("1.8.10", migration_1_8_10),
        ("1.8.11", migration_1_8_11),
        ("1.8.12", migration_1_8_12),
        ("1.8.13", migration_1_8_13),
        ("1.8.17", migration_1_8_17),
    ]
