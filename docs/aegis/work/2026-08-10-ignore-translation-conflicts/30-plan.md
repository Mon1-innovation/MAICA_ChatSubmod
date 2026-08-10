# Ignore Translation Conflicts Dependency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use aegis:subagent-driven-development (recommended) or aegis:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Declare `Ignore Translation Conflicts` as an unrestricted MAICA dependency and acquire its `v1.0.0` source directory during release packaging.

**Architecture:** Keep dependency acquisition in `.github/workflows/release.yml`, immediately before the existing zip step, and copy only the dependency's known MAS submod directory into the checked-out tree. Keep the runtime contract in `header.rpy`, using the existing MAS `Submod.dependencies` interface with `(None, None)`.

**Tech Stack:** GitHub Actions on `ubuntu-latest`, Bash utilities (`curl`, `unzip`, `find`, `cp`), Ren'Py `.rpy` source, and pytest static contract checks.

**Baseline / Authority Refs:** `docs/aegis/specs/2026-08-10-ignore-translation-conflicts-design.md`, `.github/workflows/release.yml`, `game/Submods/MAICA_ChatSubmod/header.rpy`, the user-provided MAS `zz_submods.rpy`, and the `v1.0.0` dependency archive layout.

**Compatibility Boundary:** Preserve the existing release conditions, package name, release notes, upload behavior, MAICA registration fields, and MAS dependency semantics. Do not commit the downloaded dependency or edit the external MAS registry.

**Verification:** Run the new focused pytest contract test through red/green, run the existing test suite under `tests`, run the CRLF-aware `git diff --check`, and inspect the final diff/status. Separately verify the remote tag archive and expected internal path can be read from memory when network access permits.

---

### Task 1: Add the failing dependency contract test

**Files:**
- Create: `tests/test_ignore_translation_conflicts_dependency.py`

**Why this task exists:** The requested dependency has two observable owners: the MAICA runtime registration and the release package assembly. A static contract test prevents either side from being removed or moved after this task.

**Impact / Compatibility:** The test reads repository source only; it does not import Ren'Py or execute the GitHub Actions runner. It must assert the exact dependency name, unrestricted version tuple, requested tag URL, expected target path, and ordering before `Create zip package`.

**Verification:** Run `pytest -q tests/test_ignore_translation_conflicts_dependency.py` before production changes and confirm it fails because the current source lacks the new registration and workflow download contract.

- [x] Write focused assertions against `header.rpy` and `release.yml`.
- [x] Run the focused test and record the expected red failure.

### Task 2: Add the unrestricted MAICA dependency declaration

**Files:**
- Modify: `game/Submods/MAICA_ChatSubmod/header.rpy:3-9`

**Why this task exists:** MAS performs dependency validation after registrations are collected. The MAICA registration must require the bundled submod while accepting any installed version.

**Impact / Compatibility:** Keep the user's dependency-format comment and all existing fields. Add `dependencies={"Ignore Translation Conflicts": (None, None)},` before `settings_pane` so the current MAS checker skips both minimum and maximum comparisons.

**Verification:** The focused contract test must pass its registration assertion; `git diff --check` must remain clean.

- [x] Add the dependency keyword argument without changing unrelated registration fields.
- [x] Run the focused test and confirm the registration assertion is green.

### Task 3: Download and stage the dependency during release builds

**Files:**
- Modify: `.github/workflows/release.yml` immediately before `Create zip package`

**Why this task exists:** The repository intentionally does not vendor the dependency. A release package must stage the dependency directory before the existing recursive zip command runs.

**Impact / Compatibility:** Use the existing release-creation condition. Download `https://github.com/MAS-Submod-MoyuTeam/MAS_ignore_tl_conficts_submod/archive/refs/tags/v1.0.0.zip`, extract to a temporary directory, locate and validate `game/Submods/IgnoreTranslationConflicts`, then copy that directory to `game/Submods/`. Any failed download, extraction, or missing expected directory must fail the job before packaging.

**Verification:** The focused contract test must pass URL, path, failure-check, and ordering assertions. A temporary archive smoke check should confirm the remote tag contains the expected `.rpy` file when network access is available.

- [x] Add the conditional dependency download/staging step.
- [x] Run the focused test and confirm all workflow assertions are green.
- [x] Inspect the step ordering and condition against the existing package step.

### Task 4: Run regression and final scope checks

**Files:**
- Verify: `tests/test_ignore_translation_conflicts_dependency.py`, `tests/`, `.github/workflows/release.yml`, `game/Submods/MAICA_ChatSubmod/header.rpy`

**Why this task exists:** This is a cross-file build/runtime contract change; focused checks alone do not show that existing MAICA static/runtime contracts remain intact.

**Impact / Compatibility:** Do not stage or alter the user's pre-existing `header.rpy` edits beyond the dependency argument. Do not include downloaded temporary files in the repository.

**Verification:** Run the focused test, then `pytest -q tests`, `git diff --check`, and a final `git status --short`/diff inspection. Report the remote archive smoke check and any unavailable workflow-run verification as residual risk.

- [x] Run the focused and repository test suites.
- [x] Run whitespace and source-structure checks.
- [x] Confirm only intended source/test files are changed, plus the already-existing user edit.
