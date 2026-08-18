# MPostal Private Cache Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use aegis:executing-plans to implement this plan task-by-task.

**Goal:** Move successfully read MPostal `.mms` attachments into a private submod cache and remove the cached attachment when its MPostal record is deleted.

**Architecture:** `api.rpy` owns cache path construction, safe move, and safe deletion. `main.rpy` invokes the move only after a response is received. `screen_subs.rpy` invokes deletion through the API helper when the user deletes a record. The existing Vista cache remains separate.

**Tech Stack:** Ren'Py `.rpy` Python blocks, Python 2/3-compatible standard library APIs, pytest source-contract tests.

**Baseline / Authority Refs:** Existing `vista_cache` setup in `api.rpy`; MPostal loading and response lifecycle in `main.rpy`; MPostal list deletion in `screen_subs.rpy`; MAS uses `renpy.config.basedir` for filesystem paths.

**Compatibility Boundary:** Do not move attachments before successful response; failed uploads, connection failures, timeouts, and retries must retain the source path. Never delete a path outside `mpostal_cache`. Preserve `raw_image` as a normalized path so existing preview and reread behavior continues to work.

**Verification:** Run the focused MPostal pytest tests and source-contract tests. Run the broader regression collection where possible; report the existing Python 3.13 bundled-bytecode blocker separately.

### Task 1: Add lifecycle contracts

**Files:**
- Modify: `tests/test_mpostal_poem_cleanup.py`

**Why this task exists:** Proves the success-only move and cache-only deletion behavior before implementation.

**Verification:** `pytest -q tests/test_mpostal_poem_cleanup.py`

- [ ] Write assertions for cache helper ownership, successful-read ordering, and delete action wiring.
- [ ] Run the focused test and confirm it fails because the new contract is absent.

### Task 2: Implement private attachment lifecycle

**Files:**
- Modify: `game/Submods/MAICA_ChatSubmod/api.rpy`
- Modify: `game/Submods/MAICA_ChatSubmod/main.rpy`
- Modify: `game/Submods/MAICA_ChatSubmod/screen_subs.rpy`

**Repair Track:** The canonical attachment owner is the MPostal record's `raw_image` field. Add safe cache helpers there, move only after `responsed_status` becomes `received`, and route record deletion through the cleanup helper.

**Retirement Track:** Retire the commented-out eager `.mms` deletion in `find_mail_files`; leave source attachments untouched until successful response handling.

**Impact / Compatibility:** Existing Vista thumbnails and preview paths remain unchanged. A failed cache move leaves the received record and original attachment path intact and logs the failure.

- [ ] Add a dedicated `mpostal_cache` path under the submod directory, a safe move helper, and a cache-contained delete helper.
- [ ] Call the move helper after a response is received.
- [ ] Call the delete helper from the existing MPostal record deletion action.
- [ ] Run focused tests and inspect the diff for path-safety and ordering.

### Task 3: Regression verification

- [ ] Run `pytest -q tests/test_mpostal_poem_cleanup.py tests/test_overall_review_regressions.py`.
- [ ] Run `git diff --check` and verify only intended files changed.
- [ ] Report automated blockers and residual runtime risk precisely.
