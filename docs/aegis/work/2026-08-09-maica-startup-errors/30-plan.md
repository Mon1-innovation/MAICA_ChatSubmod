# MAICA Android Startup Errors Repair Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use aegis:subagent-driven-development (recommended) or aegis:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent Android startup from raising `NameError` for `ANDROID_MASBASE` and prevent legacy MAICA migration from raising `KeyError` for `max_history_token`.

**Architecture:** Keep the Android host-owned path in the `store` namespace and qualify it from the `maica` namespace. Keep `max_history_token` as the internal `MaicaAi` attribute, while using `session_len_limit` as the persistent and outbound contract owner.

**Tech Stack:** Ren'Py `.rpy` source, Python 2/3-compatible bundled modules, pytest static/runtime contract tests.

**Baseline / Authority Refs:** `game/Submods/MAICA_ChatSubmod/api.rpy`, `header.rpy`, `game/python-packages/maica_v13_migration.py`, Android host `0mobile.rpy`, and MAICA v1.3 API documentation/backend setting model.

**Compatibility Boundary:** Preserve `store.ANDROID_MASBASE` as the host-provided Android path; preserve `maica.MaicaAi.max_history_token` as an internal attribute; emit only `session_len_limit` to the backend; keep old persistent settings migratable without requiring the obsolete key.

**Verification:** Run the two new regression tests, the existing v1.3/runtime/startup test set, the full pytest suite, `git diff --check`, and inspect the final diff/status.

---

### Task 1: Repair Android startup and persistent migration

**Files:**
- Modify: `game/Submods/MAICA_ChatSubmod/api.rpy:237,322,648-649`
- Test: `tests/test_backend_v13_compat.py` and `tests/test_v13_contract_runtime.py`

**Why this task exists:** The Android startup plugin currently resolves a host-global name from the wrong Ren'Py namespace, and the migration callback still assumes a persistent key retired by the v1.3 settings migration.

**Impact / Compatibility:** The fix is limited to the Android branch and the legacy migration callback. Existing PC behavior, the internal `max_history_token` attribute, and the current `session_len_limit` bounds remain unchanged.

**Repair Track:**
- Root causes: unqualified lookup inside `init python in maica`, and stale direct lookup of the retired persistent key.
- Canonical owners: `store.ANDROID_MASBASE` for the host path and `session_len_limit` for persistent/outbound settings.
- Smallest change: qualify the two `maica`-namespace path reads and remove the obsolete clamp that is immediately discarded by `maica_reset_setting()`.

**Retirement Track:**
- Retire the direct persistent `max_history_token` lookup from the `1.2.0` migration.
- Retain `maica.MaicaAi.max_history_token` only as the internal runtime property consumed by the existing `session_len_limit` adapter.
- Future removal trigger: remove the old `1.2.0` migration entirely only after the supported persistent-version floor no longer requires it.

**Verification steps:**
- [x] Add tests that fail on the current bare `ANDROID_MASBASE` references and stale migration lookup.
- [x] Run those tests and confirm the failures identify the missing namespace qualification and old key.
- [x] Apply the minimal source changes.
- [x] Run focused, scoped-full, and diff checks.

**Evidence:** The new tests failed 2/2 before the source patch, then passed 2/2. The focused suite passed 329 tests and the scoped project suite passed 340 tests. An unscoped `pytest -q` remains unsuitable because it collects bundled Python 2 tests under `game/python-packages`.
