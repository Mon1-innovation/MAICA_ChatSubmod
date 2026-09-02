default persistent._maica_v18_player_additions_backup = None
default persistent._maica_v18_player_additions_notice_seen = False
default persistent._maica_successful_chat_count = 0
default persistent._maica_main_changed_dialogue_count = 0
default persistent._maica_main_not_exist_dialogue_count = 0
default persistent._maica_mspire_13004_search_migrated = False

init 998 python:
    import copy
    import maica_v13_migration

    _MAICA_UNSET = object()
    try:
        _MAICA_STRING_TYPES = (basestring,)
    except NameError:
        _MAICA_STRING_TYPES = (str,)

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

    def _maica_event_unlocked(eventlabel):
        try:
            event = _maica_get_event(eventlabel)
            return bool(event is not None and getattr(event, "unlocked", False))
        except Exception:
            return False

    def _maica_event_shown_count(event):
        """Read both runtime Event objects and old persistent tuple rows."""
        if event is None:
            return 0
        try:
            count = getattr(event, "shown_count", None)
        except Exception:
            # A stale MAS Event can still be reachable through the aggregate
            # lookup after its persistent row was removed.
            count = None
        if count is None and isinstance(event, (tuple, list)) and len(event) > 12:
            count = event[12]
        try:
            return max(0, int(count or 0))
        except Exception:
            return 0

    def _maica_event_databases():
        """Return the authoritative persistent and runtime EVE databases."""
        candidates = []
        try:
            candidates.append(getattr(persistent, "event_database", None))
        except Exception:
            pass
        try:
            evhand = getattr(store, "evhand", None)
            candidates.append(getattr(evhand, "event_database", None))
        except Exception:
            pass

        databases = []
        for event_db in candidates:
            if event_db is None or not hasattr(event_db, "get"):
                continue
            if any(event_db is existing for existing in databases):
                continue
            databases.append(event_db)
        return databases

    def _maica_sync_event_lookup(eventlabel):
        """Remove an obsolete EVE entry from MAS's aggregate lookup.

        ``mas_all_ev_db`` is built once during MAS init and is not rebuilt by
        ``mas_rebuildEventLists``. If a label moved from EVE to GRE, retain the
        GRE object; otherwise remove the stale aggregate entry.
        """
        aggregate = globals().get("mas_all_ev_db", None)
        if aggregate is None or not hasattr(aggregate, "get"):
            return False

        replacement = None
        try:
            db_map = globals().get("mas_all_ev_db_map", None)
            if db_map is not None and hasattr(db_map, "items"):
                # Prefer the surviving non-EVE registration (for example GRE).
                for code, event_db in db_map.items():
                    if code == "EVE" or event_db is None:
                        continue
                    try:
                        replacement = event_db.get(eventlabel)
                    except Exception:
                        replacement = None
                    if replacement is not None:
                        break
                if replacement is None:
                    # Keep an EVE object only if removal from the authoritative
                    # database failed for some reason.
                    eve_db = db_map.get("EVE", None)
                    if eve_db is not None:
                        replacement = eve_db.get(eventlabel)
        except Exception:
            replacement = None

        try:
            current = aggregate.get(eventlabel, None)
            if replacement is None:
                if current is not None or eventlabel in aggregate:
                    aggregate.pop(eventlabel, None)
                    return True
                return False
            if current is not replacement:
                aggregate[eventlabel] = replacement
                return True
        except Exception:
            pass
        return False

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

    def _maica_event_condition_result(event):
        """Evaluate an Event conditional without letting diagnostics interrupt startup."""
        if event is None:
            return "missing"
        try:
            conditional = getattr(event, "conditional", None)
            if conditional is None:
                # Keep the existing dispatch diagnostic meaning: no
                # conditional is reported as ``None`` rather than as an
                # evaluated ``True``.
                return None
            checker = getattr(event, "checkConditional", None)
            if checker is None:
                return "unavailable"
            return bool(checker())
        except Exception as exc:
            return "error:{}:{}".format(exc.__class__.__name__, exc)

    def _maica_event_affection_result(event, affection_known, affection):
        if event is None or not affection_known:
            return "unavailable"
        try:
            checker = getattr(event, "checkAffection", None)
            if checker is None:
                return "unavailable"
            return bool(checker(affection))
        except Exception as exc:
            return "error:{}:{}".format(exc.__class__.__name__, exc)

    def _maica_greeting_call(function_name, *args, **kwargs):
        """Call a read-only greeting prerequisite and preserve diagnostic errors."""
        try:
            function = globals().get(function_name)
            if not callable(function):
                function = getattr(store, function_name, None)
            if not callable(function):
                return None
            return function(*args, **kwargs)
        except Exception as exc:
            return "error:{}:{}".format(exc.__class__.__name__, exc)

    def _maica_greeting_attr(name, default=None):
        try:
            if name in globals():
                return globals().get(name)
            return getattr(store, name, default)
        except Exception:
            return default

    def _maica_greeting_event_attr(event, name, default=None):
        """Read a GRE Event field without allowing a damaged row to abort logging."""
        try:
            return getattr(event, name, default)
        except Exception as exc:
            return "error:{}:{}".format(exc.__class__.__name__, exc)

    def _maica_get_greeting_event(eventlabel):
        """Read the GRE database before MAS's aggregate lookup.

        MAS builds ``mas_all_ev_db`` as a startup snapshot. A stale EVE entry
        can therefore shadow the live GRE object after an old save is loaded;
        greeting selection itself reads ``evhand.greeting_database``.
        """
        try:
            evhand = getattr(store, "evhand", None)
            greeting_db = getattr(evhand, "greeting_database", None)
            if greeting_db is not None and hasattr(greeting_db, "get"):
                event = greeting_db.get(eventlabel)
                if event is not None:
                    return event
        except Exception:
            pass
        return _maica_get_event(eventlabel)

    def _maica_greeting_bool_call(function_name, *args, **kwargs):
        value = _maica_greeting_call(function_name, *args, **kwargs)
        if value is None:
            return None
        if isinstance(value, _MAICA_STRING_TYPES) and value.startswith("error:"):
            return value
        try:
            return bool(value)
        except Exception as exc:
            return "error:{}:{}".format(exc.__class__.__name__, exc)

    def _maica_greeting_is_error(value):
        return (
            isinstance(value, _MAICA_STRING_TYPES)
            and value.startswith("error:")
        )

    def _maica_greeting_is_unknown(value):
        # Keep comparisons safe when a diagnostic value is an Event property
        # with an unusual type (for example a list or a proxy object).
        return (
            value is None
            or (
                isinstance(value, _MAICA_STRING_TYPES)
                and value in ("missing", "unavailable")
            )
        )

    def _maica_greeting_not(value):
        if _maica_greeting_is_unknown(value) or _maica_greeting_is_error(value):
            return value
        try:
            return not bool(value)
        except Exception as exc:
            return "error:{}:{}".format(exc.__class__.__name__, exc)

    def _maica_greeting_all(values):
        unknown = False
        for value in values:
            if _maica_greeting_is_error(value):
                return value
            if _maica_greeting_is_unknown(value):
                unknown = True
            else:
                try:
                    if not bool(value):
                        return False
                except Exception as exc:
                    return "error:{}:{}".format(
                        exc.__class__.__name__,
                        exc,
                    )
        return None if unknown else True

    def _maica_greeting_threshold(value, threshold):
        if _maica_greeting_is_unknown(value) or _maica_greeting_is_error(value):
            return value
        try:
            return value >= threshold
        except Exception as exc:
            return "error:{}:{}".format(exc.__class__.__name__, exc)

    def _maica_greeting_priority(event):
        if event is None:
            return None
        try:
            priority_rule = globals().get("MASPriorityRule")
            if priority_rule is None:
                priority_rule = getattr(store, "MASPriorityRule", None)
            getter = getattr(priority_rule, "get_priority", None)
            if getter is not None:
                priority = getter(event)
                if priority is not None:
                    return priority
        except Exception as exc:
            return "error:{}:{}".format(exc.__class__.__name__, exc)

        try:
            rules = getattr(event, "rules", None)
            if rules is not None and hasattr(rules, "get"):
                priority_key = globals().get("EV_RULE_PRIORITY", "rule_priority")
                priority = rules.get(priority_key)
                if priority is None and priority_key != "priority":
                    # Keep compatibility with lightweight/legacy Event stubs.
                    priority = rules.get("priority")
                return priority
        except Exception as exc:
            return "error:{}:{}".format(exc.__class__.__name__, exc)
        return None

    def _maica_greeting_registration(eventlabel):
        """Return the greeting databases that currently contain an event label."""
        locations = []
        try:
            persistent_greetings = getattr(persistent, "greeting_database", None)
            if persistent_greetings is not None and eventlabel in persistent_greetings:
                locations.append("persistent")
        except Exception:
            pass
        try:
            evhand = getattr(store, "evhand", None)
            runtime_greetings = getattr(evhand, "greeting_database", None)
            if runtime_greetings is not None and eventlabel in runtime_greetings:
                locations.append("runtime")
        except Exception:
            pass
        return ",".join(locations) if locations else None

    def _maica_mark_seen(eventlabel):
        """Keep canonical seen data usable when a legacy label supplied evidence."""
        try:
            seen_ever = getattr(persistent, "_seen_ever", None)
            if seen_ever is not None:
                seen_ever[eventlabel] = True
        except Exception:
            pass

    def _maica_topic_seen(eventlabel, legacy_labels=()):
        """Return (seen, evidence) from labels, persistent history, or shown_count."""
        for candidate in (eventlabel,) + tuple(legacy_labels):
            if _maica_seen_label(candidate) or _maica_seen_ever(candidate):
                if candidate != eventlabel:
                    _maica_mark_seen(eventlabel)
                return True, "seen:{}".format(candidate)

            if _maica_event_shown_count(_maica_get_event(candidate)) > 0:
                _maica_mark_seen(eventlabel)
                return True, "shown_count:{}".format(candidate)

        return False, "not-seen"

    _MAICA_SOURCE_DEFINITIONS = (
        ("heaven", "maica_prepend_2", ()),
        ("main", "maica_main", ("maica_end_1", "maica_talking")),
        ("location", "maica_wants_location2", ("maica_pre_set_location",)),
        ("preferences", "maica_wants_preferences2", ("maica_wants_preferences",)),
        ("mspire", "maica_wants_mspire", ()),
        ("mpostal", "maica_wants_mpostal", ()),
        ("mvista", "maica_pre_wants_mvista", ()),
    )

    _MAICA_DISPATCH_EVENTLABELS = (
        "maica_prepend_1",
        "maica_wants_location2",
        "maica_wants_preferences2",
        "maica_pre_wants_mvista",
        "maica_chr2",
        "maica_chr_gone",
    )

    _MAICA_GREETING_EVENTLABELS = (
        "maica_greeting",
        "maica_wants_mpostal",
        "maica_chr_corrupted2",
    )

    def _maica_read_source(source_name):
        """Read one canonical source and its legacy aliases in one place."""
        if source_name == "character":
            for label, aliases in (
                    ("maica_chr2", ("maica_chr",)),
                    ("maica_chr_gone", ()),
                    ("maica_chr_corrupted2", ("maica_chr_corrupted",)),
                ):
                seen, evidence = _maica_topic_seen(label, aliases)
                if seen:
                    return True, "{} ({})".format(label, evidence)
            return False, "not-seen"

        for name, label, aliases in _MAICA_SOURCE_DEFINITIONS:
            if name == source_name:
                seen, evidence = _maica_topic_seen(label, aliases)
                if (
                        source_name == "mvista"
                        and not seen
                        and getattr(persistent, "_maica_vista_enabled", False)
                    ):
                    _maica_mark_seen(label)
                    return True, "legacy:_maica_vista_enabled"
                return seen, evidence

        return False, "unknown-source:{}".format(source_name)

    def maica_topic_source_seen(source_name):
        """Runtime conditional helper for source-dependent event contracts."""
        return _maica_read_source(source_name)[0]

    def maica_topic_main_ready():
        """The main entry is an upstream gate; children never promote it."""
        return bool(
            _maica_read_source("heaven")[0]
            or _maica_read_source("main")[0]
        )

    def maica_topic_ready(source_name):
        """Return whether a child source is valid behind the main gate."""
        return bool(
            maica_topic_main_ready()
            and maica_topic_source_seen(source_name)
        )

    def _maica_gate_progress(source_seen, source_evidence, main_ready):
        """Apply the one-way graph rule: children require the main entry."""
        if source_seen and not main_ready:
            return False, "blocked-by:main ({})".format(source_evidence)
        return bool(source_seen), source_evidence

    def maica_get_topic_progress():
        """Evidence -> main gate -> child gates; no reverse promotion is allowed."""
        raw = {}
        for source_name, unused_label, unused_aliases in _MAICA_SOURCE_DEFINITIONS:
            raw[source_name] = _maica_read_source(source_name)
        raw["character"] = _maica_read_source("character")

        main_ready = bool(raw["heaven"][0] or raw["main"][0])
        if raw["heaven"][0]:
            main_evidence = "source:maica_prepend_2 ({})".format(raw["heaven"][1])
        elif raw["main"][0]:
            main_evidence = "source-history ({})".format(raw["main"][1])
        else:
            main_evidence = "not-seen"

        progress = {
            "main_ready": main_ready,
            "main_evidence": main_evidence,
            "main_event_unlocked": _maica_event_unlocked("maica_main"),
            "heaven_intro_seen": raw["heaven"][0],
            "heaven_intro_evidence": raw["heaven"][1],
            # A valid main state implies the original Heaven Forest flow. This
            # keeps the main topic and its reread topic consistent after repair.
            "heaven_reread_ready": main_ready,
            "heaven_reread_evidence": (
                raw["heaven"][1]
                if raw["heaven"][0]
                else "implied-by:maica_main ({})".format(main_evidence)
                if main_ready
                else "not-seen"
            ),
        }

        for source_name, unused_label, unused_aliases in _MAICA_SOURCE_DEFINITIONS:
            if source_name == "heaven" or source_name == "main":
                continue
            ready, evidence = _maica_gate_progress(
                raw[source_name][0],
                raw[source_name][1],
                main_ready,
            )
            progress["{}_seen".format(source_name)] = ready
            progress["{}_evidence".format(source_name)] = evidence
            progress["{}_raw_seen".format(source_name)] = raw[source_name][0]

        character_ready, character_evidence = _maica_gate_progress(
            raw["character"][0],
            raw["character"][1],
            main_ready,
        )
        progress["character_seen"] = character_ready
        progress["character_evidence"] = character_evidence
        progress["character_raw_seen"] = raw["character"][0]
        progress["heaven_seen"] = main_ready
        progress["heaven_evidence"] = progress["heaven_reread_evidence"]
        return progress

    def _maica_set_event(eventlabel, unlocked=_MAICA_UNSET,
                         conditional=_MAICA_UNSET, action=_MAICA_UNSET,
                         random=_MAICA_UNSET, pool=_MAICA_UNSET,
                         clear_unlock_date=False):
        """Apply a small Event contract and report whether persistent state changed."""
        event = _maica_get_event(eventlabel)
        if event is None:
            return False, None, None

        changed = False
        before = None
        try:
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
            current = getattr(event, "unlocked", False)
        except Exception:
            # A damaged legacy Event must not prevent other contracts from
            # being reconciled. The next startup can retry this entry.
            return changed, before, None

        return changed, before, current

    def _maica_set_no_unlock_rule(eventlabel):
        try:
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
        except Exception:
            return False
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

    def _maica_topic_contract_specs():
        """Single source of truth for all Event contracts and state targets."""
        queue_action = _maica_action("EV_ACT_QUEUE", "queue")
        push_action = _maica_action("EV_ACT_PUSH", "push")
        unlock_action = _maica_action("EV_ACT_UNLOCK", "unlock")
        main_gate = "maica_topic_main_ready() and "
        source_ready = "maica_topic_ready('{}') and ".format

        # (label, state_key, evidence_key, kind, static_expected, fields,
        #  no_unlock_rule, greeting_rule)
        return (
            # Hidden dispatch events.
            ("maica_prepend_1", None, "internal-contract", "internal", False, {
                "conditional": "not renpy.seen_label('maica_prepend_1') and not mas_inEVL('maica_prepend_1')",
                "action": queue_action, "random": False, "pool": False,
            }, False, None),
            ("maica_wants_location2", None, "internal-contract", "internal", False, {
                "conditional": main_gate + "maica_has_successful_chat() and not renpy.seen_label('maica_wants_location2') and not mas_inEVL('maica_wants_location2')",
                "action": queue_action, "random": False, "pool": False,
            }, False, None),
            ("maica_wants_preferences2", None, "internal-contract", "internal", False, {
                "conditional": main_gate + "maica_get_successful_chat_count() >= 2 and not renpy.seen_label('maica_wants_preferences2') and not mas_inEVL('maica_wants_preferences2')",
                "action": queue_action, "random": False, "pool": False,
            }, False, None),
            ("maica_pre_wants_mvista", None, "internal-contract", "internal", False, {
                "conditional": main_gate + "maica_get_successful_chat_count() >= 3 and not renpy.seen_label('maica_pre_wants_mvista') and not mas_inEVL('maica_pre_wants_mvista')",
                "action": queue_action, "random": False, "pool": False,
            }, False, None),
            ("maica_chr2", None, "internal-contract", "internal", False, {
                "conditional": main_gate + "maica_get_successful_chat_count() >= 4 and not renpy.seen_label('maica_chr2') and not renpy.seen_label('maica_chr_gone') and not renpy.seen_label('maica_chr_corrupted2') and not mas_inEVL('maica_chr2')",
                "action": queue_action, "random": False, "pool": False,
            }, False, None),
            ("maica_chr_gone", None, "internal-contract", "internal", False, {
                "conditional": main_gate + "not maica_chr_exist and not renpy.seen_label('maica_chr_gone') and not mas_inEVL('maica_chr_gone')",
                "action": push_action, "random": False, "pool": False,
            }, False, None),
            ("maica_wants_mspire", None, "internal-contract", "internal", False, {
                "conditional": main_gate + "maica_has_successful_chat() and not renpy.seen_label('maica_wants_mspire')",
                "action": None, "random": False, "pool": False,
            }, False, None),
            # Hidden processing events.
            ("maica_mspire", None, "internal-contract", "processing", False, {
                "conditional": source_ready("mspire") + "spire_has_past(datetime.timedelta(minutes=persistent.maica_setting_dict.get('mspire_interval'))) and persistent.maica_setting_dict.get('mspire_enable') and not store.maica.maica_instance.is_in_exception()",
                "action": None, "random": False, "pool": False,
            }, False, None),
            ("maica_mpostal_received", None, "internal-contract", "processing", False, {
                "conditional": None, "action": None, "random": False, "pool": False,
            }, False, None),
            ("maica_mpostal_replyed", None, "internal-contract", "processing", False, {
                "conditional": None, "action": None, "random": False, "pool": False,
            }, False, None),
            # User-facing topics. Their state is derived, never auto-unlocked by MAS.
            ("maica_main", "main_ready", "main_evidence", "topic", None, {
                "conditional": None, "action": None, "random": False, "pool": True,
            }, True, None),
            ("maica_mods_location", "location_seen", "location_evidence", "topic", None, {
                "conditional": None, "action": None, "random": False, "pool": True,
            }, True, None),
            ("maica_mods_preferences", "preferences_seen", "preferences_evidence", "topic", None, {
                "conditional": None, "action": None, "random": False, "pool": True,
            }, True, None),
            # Rereads follow the same state keys as their source topics. The
            # Heaven Forest reread deliberately follows main_ready: main_ready
            # implies its original flow was reached.
            ("maica_prepend_reread", "heaven_reread_ready", "heaven_reread_evidence", "reread", None, {
                "conditional": "maica_topic_main_ready() and not renpy.seen_label('maica_prepend_reread')",
                "action": unlock_action, "random": False, "pool": True,
            }, True, None),
            ("maica_wants_location_reread", "location_seen", "location_evidence", "reread", None, {
                "conditional": source_ready("location") + "not renpy.seen_label('maica_wants_location_reread')",
                "action": unlock_action, "random": False, "pool": True,
            }, True, None),
            ("maica_wants_preferences_reread", "preferences_seen", "preferences_evidence", "reread", None, {
                "conditional": source_ready("preferences") + "not renpy.seen_label('maica_wants_preferences_reread')",
                "action": unlock_action, "random": False, "pool": True,
            }, True, None),
            ("maica_wants_mspire_reread", "mspire_seen", "mspire_evidence", "reread", None, {
                "conditional": source_ready("mspire") + "not renpy.seen_label('maica_wants_mspire_reread')",
                "action": unlock_action, "random": False, "pool": True,
            }, True, None),
            ("maica_wants_mpostal_reread", "mpostal_seen", "mpostal_evidence", "reread", None, {
                "conditional": source_ready("mpostal") + "not renpy.seen_label('maica_wants_mpostal_reread')",
                "action": unlock_action, "random": False, "pool": True,
            }, True, None),
            ("maica_wants_mvista_reread", "mvista_seen", "mvista_evidence", "reread", None, {
                "conditional": source_ready("mvista") + "not renpy.seen_label('maica_wants_mvista_reread')",
                "action": unlock_action, "random": False, "pool": True,
            }, True, None),
            ("maica_chr_reread", "character_seen", "character_evidence", "reread", None, {
                "conditional": source_ready("character") + "not renpy.seen_label('maica_chr_reread')",
                "action": unlock_action, "random": False, "pool": True,
            }, True, None),
            # Greeting events stay registered and are gated by their conditionals.
            ("maica_greeting", None, "greeting-contract", "greeting", True, {
                "conditional": "persistent._mas_greeting_type is None and renpy.seen_label('maica_prepend_1') and not mas_isSpecialDay() and not mas_isplayer_bday() and not renpy.seen_label('maica_prepend_2')",
                "action": None, "random": False, "pool": False,
            }, False, ("skip_visual", None, 20)),
            ("maica_wants_mpostal", None, "greeting-contract", "greeting", True, {
                "conditional": main_gate + "persistent._mas_greeting_type is None and maica_get_successful_chat_count() >= 2 and not mas_isSpecialDay() and not mas_isplayer_bday() and not renpy.seen_label('maica_wants_mpostal') and not (maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2'))",
                "action": None, "random": False, "pool": False,
            }, False, (None, "monika 3hubsa", 20)),
            ("maica_chr_corrupted2", None, "greeting-contract", "greeting", True, {
                "conditional": main_gate + "persistent._mas_greeting_type is None and not mas_isSpecialDay() and not mas_isplayer_bday() and maica_chr_changed and not renpy.seen_label('maica_chr_corrupted2')",
                "action": None, "random": False, "pool": False,
            }, False, ("skip_visual", None, 0)),
        )

    def _maica_update_greeting_rules(eventlabel, rule_spec):
        if rule_spec is None:
            return False
        try:
            event = _maica_get_event(eventlabel)
            if event is None:
                return False
            rules = getattr(event, "rules", None)
            if rules is None:
                rules = {}
                event.rules = rules
            previous_rules = dict(rules)
            skip_visual, forced_exp, priority = rule_spec
            if forced_exp is not None:
                rules.update(MASGreetingRule.create_rule(forced_exp=forced_exp))
            else:
                rules.update(MASGreetingRule.create_rule(skip_visual=bool(skip_visual)))
            rules.update(MASPriorityRule.create_rule(priority))
            return rules != previous_rules
        except Exception:
            return False

    def _maica_apply_topic_contracts(progress, reason):
        """Apply every declarative contract and return (state_changes, changed)."""
        changes = []
        contracts_changed = False
        for (
                eventlabel,
                state_key,
                evidence_key,
                kind,
                static_expected,
                contract,
                no_unlock,
                rule_spec,
            ) in _maica_topic_contract_specs():
            expected = (
                bool(progress[state_key])
                if state_key is not None
                else bool(static_expected)
            )
            fields = dict(contract)
            fields["unlocked"] = expected
            # A stale unlock date is meaningful only while an event is unlocked.
            # Keep a valid date when restoring a topic, but clear it whenever the
            # reconciler locks that topic again.
            fields["clear_unlock_date"] = not expected
            changed, before, unused_current = _maica_set_event(eventlabel, **fields)
            contracts_changed = contracts_changed or changed
            if no_unlock:
                contracts_changed = _maica_set_no_unlock_rule(eventlabel) or contracts_changed
            contracts_changed = _maica_update_greeting_rules(
                eventlabel,
                rule_spec,
            ) or contracts_changed
            if before is not None:
                _maica_record_state_change(
                    changes,
                    eventlabel,
                    expected,
                    before,
                    progress.get(evidence_key, evidence_key),
                    reason,
                )
        return changes, contracts_changed

    _MAICA_LEGACY_PROGRESS_MAP = {
        "maica_pre_set_location": "maica_wants_location2",
        "maica_set_location_reread": "maica_mods_location",
        "maica_chr": "maica_chr2",
        "maica_chr_corrupted": "maica_chr_corrupted2",
        "maica_wants_preferences": "maica_wants_preferences2",
    }
    _MAICA_OBSOLETE_EVENTLABELS = (
        "maica_pre_set_location",
        "maica_set_location_reread",
        "maica_chr",
        "maica_chr_corrupted",
        "maica_wants_preferences",
        # This label was once registered in EVE and later moved to GRE.
        "maica_chr_corrupted2",
    )

    def _maica_migrate_legacy_references():
        """Rewrite queued and bookmarked references using the legacy map."""
        changed = False
        try:
            event_list = getattr(persistent, "event_list", None)
            if event_list is not None:
                for index, item in enumerate(event_list):
                    if isinstance(item, (tuple, list)) and item:
                        old_label = item[0]
                    else:
                        old_label = item
                    try:
                        new_label = _MAICA_LEGACY_PROGRESS_MAP.get(old_label)
                    except Exception:
                        continue
                    if new_label is None:
                        continue
                    if isinstance(item, tuple):
                        event_list[index] = (new_label,) + item[1:]
                    elif isinstance(item, list):
                        event_list[index] = [new_label] + item[1:]
                    else:
                        event_list[index] = new_label
                    changed = True
        except Exception:
            pass

        for attr_name in ("_mas_player_bookmarked", "_mas_player_derandomed"):
            try:
                topic_list = getattr(persistent, attr_name, None)
                if topic_list is None:
                    continue
                migrated = []
                for label in topic_list:
                    try:
                        migrated.append(
                            _MAICA_LEGACY_PROGRESS_MAP.get(label, label)
                        )
                    except Exception:
                        migrated.append(label)
                if migrated != topic_list:
                    setattr(persistent, attr_name, migrated)
                    changed = True
            except Exception:
                pass

        try:
            flagged = getattr(persistent, "flagged_monikatopic", None)
            try:
                migrated_flagged = _MAICA_LEGACY_PROGRESS_MAP.get(flagged, flagged)
            except Exception:
                migrated_flagged = flagged
            if migrated_flagged != flagged:
                persistent.flagged_monikatopic = migrated_flagged
                changed = True
        except Exception:
            pass
        return changed

    def _maica_cleanup_legacy_event_records():
        """Migrate legacy evidence and remove duplicate EVE registrations."""
        changed = _maica_migrate_legacy_references()
        processed_db_ids = []
        event_dbs = _maica_event_databases()
        for event_db in event_dbs:
            if id(event_db) in processed_db_ids:
                continue
            processed_db_ids.append(id(event_db))
            try:
                for old_label, new_label in _MAICA_LEGACY_PROGRESS_MAP.items():
                    old_event = event_db.get(old_label)
                    old_count = _maica_event_shown_count(old_event)
                    old_seen = (
                        _maica_seen_label(old_label)
                        or _maica_seen_ever(old_label)
                        or old_count > 0
                    )
                    if old_seen:
                        _maica_mark_seen(new_label)

                    # Preserve a legacy Event's history when the replacement is
                    # already present in this database. The seen-label marker is
                    # still the authoritative evidence used by the state graph.
                    if old_count > 0:
                        new_event = event_db.get(new_label)
                        if new_event is None:
                            new_event = _maica_get_event(new_label)
                        new_count = _maica_event_shown_count(new_event)
                        if new_event is not None and old_count > new_count:
                            try:
                                new_event.shown_count = old_count
                                changed = True
                            except Exception:
                                pass

                old_corrupted_event = event_db.get("maica_chr_corrupted2")
                if _maica_event_shown_count(old_corrupted_event) > 0:
                    _maica_mark_seen("maica_chr_corrupted2")

                for eventlabel in _MAICA_OBSOLETE_EVENTLABELS:
                    if eventlabel in event_db:
                        event_db.pop(eventlabel, None)
                        changed = True
            except Exception:
                # A malformed legacy database must not prevent the state check
                # from repairing the remaining runtime Event objects.
                pass

        # ``mas_all_ev_db`` is a startup snapshot, so rebuilding topic lists
        # alone does not remove labels deleted above. Refresh only the labels
        # handled by this migration; current GRE registrations win over an old
        # EVE duplicate with the same label.
        for eventlabel in _MAICA_OBSOLETE_EVENTLABELS:
            changed = _maica_sync_event_lookup(eventlabel) or changed
        return changed

    def _maica_queue_label(item):
        if isinstance(item, (tuple, list)) and item:
            return item[0]
        return item

    def _maica_dispatch_queue_positions(eventlabel):
        positions = []
        try:
            for index, item in enumerate(getattr(persistent, "event_list", None) or ()):
                if _maica_queue_label(item) == eventlabel:
                    positions.append(index)
        except Exception:
            pass
        return positions

    def _maica_normalize_dispatch_queue(reason):
        """Remove completed/duplicate dispatch entries without touching current ELI data."""
        result = {
            "changed": False,
            "removed": 0,
            "removed_by_label": {},
        }
        try:
            event_list = getattr(persistent, "event_list", None)
            if event_list is None:
                return result

            original = list(event_list)
            retained = set()
            repaired_reversed = []
            # MAS pops from the end. Keeping the last queued copy preserves the
            # entry that would run first, including one restored by restartEvent.
            for item in reversed(original):
                eventlabel = _maica_queue_label(item)
                if eventlabel not in _MAICA_DISPATCH_EVENTLABELS:
                    repaired_reversed.append(item)
                    continue

                completed = _maica_event_shown_count(
                    _maica_get_event(eventlabel)
                ) > 0
                if completed or eventlabel in retained:
                    result["removed"] += 1
                    result["removed_by_label"][eventlabel] = (
                        result["removed_by_label"].get(eventlabel, 0) + 1
                    )
                    continue

                retained.add(eventlabel)
                repaired_reversed.append(item)

            repaired = list(reversed(repaired_reversed))
            if repaired != original:
                event_list[:] = repaired
                result["changed"] = True
        except Exception as exc:
            _maica_state_log(
                "warning",
                "MAICA: dispatch queue normalization failed ({}) {}: {}".format(
                    reason,
                    exc.__class__.__name__,
                    exc,
                ),
            )
            return result

        if result["changed"]:
            removed_summary = ", ".join(
                "{}={}".format(eventlabel, count)
                for eventlabel, count in sorted(result["removed_by_label"].items())
            )
            _maica_state_log(
                "warning",
                "MAICA: dispatch queue normalized ({}) removed={} [{}]".format(
                    reason,
                    result["removed"],
                    removed_summary,
                ),
            )
        return result

    def _maica_log_dispatch_diagnostics(reason):
        """Log enough scheduler state to diagnose a topic that did not dispatch."""
        try:
            event_list = getattr(persistent, "event_list", None) or ()
            current_topic = getattr(persistent, "current_monikatopic", None)
            mas_globals = getattr(store, "mas_globals", None)
            idle_mode = getattr(mas_globals, "in_idle_mode", None)
            pause_until = getattr(mas_globals, "event_unpause_dt", None)
            affection_known = "mas_curr_affection" in globals()
            affection = globals().get("mas_curr_affection", None)
            try:
                successful_chats = maica_get_successful_chat_count()
            except Exception:
                successful_chats = None

            _maica_state_log(
                "info",
                "MAICA: dispatch diagnostics ({}) queue_total={} current={!r} "
                "idle={!r} pause_until={!r} affection={!r} successful_chats={!r}".format(
                    reason,
                    len(event_list),
                    current_topic,
                    idle_mode,
                    pause_until,
                    affection if affection_known else "unavailable",
                    successful_chats,
                ),
            )

            for eventlabel in _MAICA_DISPATCH_EVENTLABELS:
                event = _maica_get_event(eventlabel)
                queue_positions = _maica_dispatch_queue_positions(eventlabel)
                try:
                    label_exists = bool(renpy.has_label(eventlabel))
                except Exception:
                    label_exists = None

                if event is None:
                    _maica_state_log(
                        "warning",
                        "MAICA: dispatch event ({}) label={} event=missing "
                        "label_exists={!r} queued={} queue_positions={!r} current={}".format(
                            reason,
                            eventlabel,
                            label_exists,
                            len(queue_positions),
                            queue_positions,
                            current_topic == eventlabel,
                        ),
                    )
                    continue

                conditional = getattr(event, "conditional", None)
                condition_result = _maica_event_condition_result(event)
                affection_result = _maica_event_affection_result(
                    event,
                    affection_known,
                    affection,
                )

                _maica_state_log(
                    "debug",
                    "MAICA: dispatch event ({}) label={} label_exists={!r} "
                    "seen_label={} seen_ever={} shown_count={} unlocked={!r} "
                    "random={!r} pool={!r} action={!r} conditional={!r} "
                    "condition_result={!r} affection_ok={!r} queued={} "
                    "queue_positions={!r} current={}".format(
                        reason,
                        eventlabel,
                        label_exists,
                        _maica_seen_label(eventlabel),
                        _maica_seen_ever(eventlabel),
                        _maica_event_shown_count(event),
                        getattr(event, "unlocked", None),
                        getattr(event, "random", None),
                        getattr(event, "pool", None),
                        getattr(event, "action", None),
                        conditional,
                        condition_result,
                        affection_result,
                        len(queue_positions),
                        queue_positions,
                        current_topic == eventlabel,
                    ),
                )

        except Exception as exc:
            _maica_state_log(
                "warning",
                "MAICA: dispatch diagnostics failed ({}) {}: {}".format(
                    reason,
                    exc.__class__.__name__,
                    exc,
                ),
            )

        # Greeting selection uses a separate MAS database and must remain
        # observable even if a malformed dispatch queue/event prevented the
        # regular diagnostics above from completing.
        try:
            _maica_log_greeting_diagnostics(reason)
        except Exception as exc:
            _maica_state_log(
                "warning",
                "MAICA: greeting diagnostics dispatch hook failed ({}) {}: {}".format(
                    reason,
                    exc.__class__.__name__,
                    exc,
                ),
            )

    def _maica_log_greeting_diagnostics(reason):
        """Log greeting selection inputs and each MAICA greeting candidate."""
        try:
            greeting_events = tuple(
                (eventlabel, _maica_get_greeting_event(eventlabel))
                for eventlabel in _MAICA_GREETING_EVENTLABELS
            )
            greetings_registered = any(
                event is not None for unused_label, event in greeting_events
            )

            event_list = getattr(persistent, "event_list", None) or ()
            try:
                queue_total = len(event_list)
            except Exception:
                queue_total = "unavailable"
            current_topic = getattr(persistent, "current_monikatopic", None)
            mas_globals = getattr(store, "mas_globals", None)
            try:
                pause_until = getattr(mas_globals, "event_unpause_dt", None)
            except Exception:
                pause_until = None
            try:
                idle_mode = getattr(mas_globals, "in_idle_mode", None)
            except Exception:
                idle_mode = None
            if idle_mode is None:
                try:
                    idle_mode = getattr(persistent, "_mas_in_idle_mode", None)
                except Exception:
                    idle_mode = None
            try:
                affection = globals().get("mas_curr_affection", _MAICA_UNSET)
                if affection is _MAICA_UNSET:
                    affection = getattr(store, "mas_curr_affection", None)
            except Exception:
                affection = None
            # ``None`` means the affection value is not available; zero is a
            # valid affection value and must still be checked.
            affection_known = affection is not None
            successful_chats = _maica_greeting_call(
                "maica_get_successful_chat_count"
            )
            selected_greeting = _maica_greeting_attr(
                "selected_greeting",
                "unavailable",
            )
            _maica_state_log(
                "info",
                "MAICA: greeting diagnostics ({}) hook=ch30_preloop "
                "type={!r} timeout={!r} force={!r} game_crashed={!r} "
                "closed_self={!r} idle={!r} selected={!r} queue_total={} "
                "current={!r} pause_until={!r} affection={!r} "
                "successful_chats={!r}".format(
                    reason,
                    getattr(persistent, "_mas_greeting_type", None),
                    getattr(persistent, "_mas_greeting_type_timeout", None),
                    getattr(persistent, "_mas_forcegreeting", None),
                    getattr(persistent, "_mas_game_crashed", None),
                    getattr(persistent, "closed_self", None),
                    idle_mode,
                    selected_greeting,
                    queue_total,
                    current_topic,
                    pause_until,
                    affection if affection_known else "unavailable",
                    successful_chats,
                ),
            )

            if not greetings_registered:
                _maica_state_log(
                    "warning",
                    "MAICA: greeting diagnostics ({}) no registered greeting events "
                    "labels={!r}".format(reason, _MAICA_GREETING_EVENTLABELS),
                )
                return

            condition_results = {}
            affection_results = {}
            for eventlabel, event in greeting_events:
                queue_positions = _maica_dispatch_queue_positions(eventlabel)
                try:
                    label_exists = bool(renpy.has_label(eventlabel))
                except Exception:
                    label_exists = None
                registration = _maica_greeting_registration(eventlabel)
                registered = registration is not None
                try:
                    selected = selected_greeting == eventlabel
                except Exception:
                    selected = False
                try:
                    selected = selected or (
                        getattr(selected_greeting, "eventlabel", None)
                        == eventlabel
                    )
                except Exception:
                    pass

                if event is None:
                    _maica_state_log(
                        "warning",
                        "MAICA: greeting event ({}) label={} event=missing "
                        "label_exists={!r} registration={!r} registered={!r} queued={} "
                        "queue_positions={!r} current={} selected={}".format(
                            reason,
                            eventlabel,
                            label_exists,
                            registration,
                            registered,
                            len(queue_positions),
                            queue_positions,
                            current_topic == eventlabel,
                            selected,
                        ),
                    )
                    condition_results[eventlabel] = "missing"
                    affection_results[eventlabel] = "unavailable"
                    continue

                condition_result = _maica_event_condition_result(event)
                affection_result = _maica_event_affection_result(
                    event,
                    affection_known,
                    affection,
                )
                condition_results[eventlabel] = condition_result
                affection_results[eventlabel] = affection_result
                _maica_state_log(
                    "debug",
                    "MAICA: greeting event ({}) label={} label_exists={!r} "
                    "registration={!r} registered={!r} seen_label={} "
                    "seen_ever={} shown_count={} "
                    "unlocked={!r} unlock_date={!r} random={!r} pool={!r} "
                    "action={!r} flags={!r} "
                    "priority={!r} category={!r} aff_range={!r} "
                    "affection_ok={!r} conditional={!r} "
                    "condition_result={!r} rules={!r} queued={} "
                    "queue_positions={!r} current={} selected={}".format(
                        reason,
                        eventlabel,
                        label_exists,
                        registration,
                        registered,
                        _maica_seen_label(eventlabel),
                        _maica_seen_ever(eventlabel),
                        _maica_event_shown_count(event),
                        _maica_greeting_event_attr(event, "unlocked"),
                        _maica_greeting_event_attr(event, "unlock_date"),
                        _maica_greeting_event_attr(event, "random"),
                        _maica_greeting_event_attr(event, "pool"),
                        _maica_greeting_event_attr(event, "action"),
                        _maica_greeting_event_attr(event, "flags"),
                        _maica_greeting_priority(event),
                        _maica_greeting_event_attr(event, "category"),
                        _maica_greeting_event_attr(event, "aff_range"),
                        affection_result,
                        _maica_greeting_event_attr(event, "conditional"),
                        condition_result,
                        _maica_greeting_event_attr(event, "rules"),
                        len(queue_positions),
                        queue_positions,
                        current_topic == eventlabel,
                        selected,
                    ),
                )

            # Keep these fields in lockstep with the greeting conditionals in
            # chat.rpy. The Event result remains the authoritative total when
            # MAS can evaluate the condition; the fallback makes old/corrupt
            # Event objects diagnosable as well.
            generic_start = (
                getattr(persistent, "_mas_greeting_type", None) is None
            )
            prepend_seen = _maica_seen_label("maica_prepend_1")
            post_door_seen = _maica_seen_label("maica_prepend_2")
            greeting_seen = _maica_seen_label("maica_greeting")
            special_day = _maica_greeting_bool_call("mas_isSpecialDay")
            player_bday = _maica_greeting_bool_call("mas_isplayer_bday")
            main_ready = _maica_greeting_bool_call("maica_topic_main_ready")
            chat_threshold = _maica_greeting_threshold(successful_chats, 2)
            character_changed = _maica_greeting_attr(
                "maica_chr_changed",
                None,
            )
            if character_changed is not None and not _maica_greeting_is_error(
                    character_changed
                ):
                character_changed = bool(character_changed)
            mpostal_seen = _maica_seen_label("maica_wants_mpostal")
            corrupted_seen = _maica_seen_label("maica_chr_corrupted2")
            character_conflict = _maica_greeting_all(
                (
                    character_changed,
                    _maica_greeting_not(corrupted_seen),
                )
            )

            fallback_results = {
                "maica_greeting": _maica_greeting_all(
                    (
                        generic_start,
                        prepend_seen,
                        _maica_greeting_not(special_day),
                        _maica_greeting_not(player_bday),
                        _maica_greeting_not(post_door_seen),
                    )
                ),
                "maica_wants_mpostal": _maica_greeting_all(
                    (
                        generic_start,
                        main_ready,
                        chat_threshold,
                        _maica_greeting_not(special_day),
                        _maica_greeting_not(player_bday),
                        _maica_greeting_not(mpostal_seen),
                        _maica_greeting_not(character_conflict),
                    )
                ),
                "maica_chr_corrupted2": _maica_greeting_all(
                    (
                        generic_start,
                        main_ready,
                        _maica_greeting_not(special_day),
                        _maica_greeting_not(player_bday),
                        character_changed,
                        _maica_greeting_not(corrupted_seen),
                    )
                ),
            }

            # Normal MAS Event objects expose ``checkAffection`` and that
            # result must win because it reflects the registered aff_range.
            # These direct checks mirror the MTTS diagnostics and keep the
            # condition summary useful for legacy or lightweight Event rows.
            affectionate_or_higher = _maica_greeting_bool_call(
                "mas_isMoniAff",
                higher=True,
            )
            normal_or_higher = _maica_greeting_bool_call(
                "mas_isMoniNormal",
                higher=True,
            )
            affection_fallbacks = {
                "maica_greeting": affectionate_or_higher,
                "maica_wants_mpostal": affectionate_or_higher,
                "maica_chr_corrupted2": normal_or_higher,
            }

            def _greeting_affection(eventlabel):
                affection_result = affection_results.get(
                    eventlabel,
                    "missing",
                )
                if _maica_greeting_is_unknown(affection_result):
                    return affection_fallbacks.get(
                        eventlabel,
                        affection_result,
                    )
                return affection_result

            def _greeting_total(eventlabel):
                # MAS applies the Event conditional and affection range as
                # separate filters. Report their conjunction as the total so
                # a passing conditional cannot look available when affection
                # is outside the greeting's range.
                condition_result = condition_results.get(eventlabel, "missing")
                affection_result = _greeting_affection(eventlabel)
                if condition_result == "missing":
                    return "missing"
                if _maica_greeting_is_error(condition_result):
                    return condition_result
                if _maica_greeting_is_unknown(condition_result):
                    condition_result = fallback_results.get(
                        eventlabel,
                        condition_result,
                    )
                return _maica_greeting_all(
                    (condition_result, affection_result)
                )

            _maica_state_log(
                "debug",
                "MAICA: maica_greeting condition: generic start={} "
                "prepend seen={} special day={} player birthday={} "
                "post-door seen={} greeting seen={} affection threshold={} "
                "total condition={} condition_result={} reason={}".format(
                    generic_start,
                    prepend_seen,
                    special_day,
                    player_bday,
                    post_door_seen,
                    greeting_seen,
                    _greeting_affection("maica_greeting"),
                    _greeting_total("maica_greeting"),
                    _greeting_total("maica_greeting"),
                    reason,
                ),
            )
            _maica_state_log(
                "debug",
                "MAICA: maica_wants_mpostal condition: generic start={} "
                "main ready={} successful chats={!r} chat threshold={} "
                "special day={} player birthday={} greeting seen={} "
                "character changed={} corruption greeting seen={} "
                "character conflict={} "
                "affection threshold={} total condition={} condition_result={} "
                "reason={}".format(
                    generic_start,
                    main_ready,
                    successful_chats,
                    chat_threshold,
                    special_day,
                    player_bday,
                    mpostal_seen,
                    character_changed,
                    corrupted_seen,
                    character_conflict,
                    _greeting_affection("maica_wants_mpostal"),
                    _greeting_total("maica_wants_mpostal"),
                    _greeting_total("maica_wants_mpostal"),
                    reason,
                ),
            )
            _maica_state_log(
                "debug",
                "MAICA: maica_chr_corrupted2 condition: generic start={} "
                "main ready={} special day={} player birthday={} "
                "character changed={} corruption greeting seen={} "
                "affection threshold={} total condition={} condition_result={} "
                "reason={}".format(
                    generic_start,
                    main_ready,
                    special_day,
                    player_bday,
                    character_changed,
                    corrupted_seen,
                    _greeting_affection("maica_chr_corrupted2"),
                    _greeting_total("maica_chr_corrupted2"),
                    _greeting_total("maica_chr_corrupted2"),
                    reason,
                ),
            )
        except Exception as exc:
            _maica_state_log(
                "warning",
                "MAICA: greeting diagnostics failed ({}) {}: {}".format(
                    reason,
                    exc.__class__.__name__,
                    exc,
                ),
            )

    def maica_reconcile_topic_state(reason="startup", repair_contracts=False):
        """Run one pipeline: collect -> derive gates -> apply contracts -> log."""
        # ``repair_contracts`` is retained for compatibility with the first
        # 1.8.17 implementation. Contracts are now always applied, so migration
        # and startup use exactly the same path.
        legacy_changed = _maica_cleanup_legacy_event_records()
        progress = maica_get_topic_progress()
        changes, contracts_changed = _maica_apply_topic_contracts(progress, reason)
        contracts_changed = bool(contracts_changed or legacy_changed)
        queue_result = _maica_normalize_dispatch_queue(reason)
        if legacy_changed:
            _maica_state_log(
                "info",
                "MAICA: legacy topic records normalized ({})".format(reason),
            )

        state_labels = (
            ("main", "main_ready", "main_evidence"),
            ("location", "location_seen", "location_evidence"),
            ("preferences", "preferences_seen", "preferences_evidence"),
            ("mspire", "mspire_seen", "mspire_evidence"),
            ("mpostal", "mpostal_seen", "mpostal_evidence"),
            ("mvista", "mvista_seen", "mvista_evidence"),
            ("character", "character_seen", "character_evidence"),
        )
        state_summary = ", ".join(
            "{}={}".format(label, bool(progress[state_key]))
            for label, state_key, unused_evidence_key in state_labels
        )
        evidence_summary = ", ".join(
            "{}={}".format(label, progress[evidence_key])
            for label, unused_state_key, evidence_key in state_labels
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

        _maica_log_dispatch_diagnostics(reason)

        return {
            "progress": progress,
            "changes": changes,
            "changed": bool(contracts_changed or queue_result["changed"]),
            "legacy_changed": bool(legacy_changed),
            "queue_changed": queue_result["changed"],
            "queue_removed": queue_result["removed"],
        }

    def migration_1_8_17():
        # The migration and every-startup audit intentionally share one path.
        maica_reconcile_topic_state(reason="migration_1_8_17")

    def migration_1_8_22():
        if persistent._maica_mspire_13004_search_migrated:
            return
        maica_v13_migration.migrate_mspire_13004_search_type(
            persistent.maica_setting_dict
        )
        persistent._maica_mspire_13004_search_migrated = True

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

        # Keep queued and Talk references in one shared legacy-rewrite path.
        _maica_migrate_legacy_references()
        for old_label in location_label_map:
            persistent._seen_ever.pop(old_label, None)

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
        ("1.8.22", migration_1_8_22),
    ]
