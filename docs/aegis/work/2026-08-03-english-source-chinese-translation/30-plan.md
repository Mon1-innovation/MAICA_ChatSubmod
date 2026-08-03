# Default English Source and Chinese Translation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use aegis:subagent-driven-development (recommended) or aegis:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make English the default source language for all player-visible MAICA ChatSubmod text and preserve Simplified Chinese as the `chinese` Ren'Py translation.

**Architecture:** Invert existing translation pairs in place, preserving each source file, translation ID, interpolation token, text tag, and control-flow owner. Use a repository-local static contract test to classify player-visible strings and catch English translation blocks, Chinese default-source leaks, and token mismatches; a one-time migration helper may perform mechanical edits but is not a runtime dependency.

**Tech Stack:** Ren'Py `.rpy`, Python 3, pytest, Git.

**Baseline / Authority Refs:** `docs/aegis/specs/2026-08-03-english-source-chinese-translation-design.md`, `CLAUDE.md`, `game/Submods/MAICA_ChatSubmod/api.rpy`.

**Compatibility Boundary:** Keep labels, translation IDs, interpolation variables, text tags, persistent data, `config.language = "english"`, backend language fields, prompts, logs, comments, and explicit bilingual business fields stable.

**Verification:** `python -m pytest tests/test_translation_source_language.py -q`, `python -m pytest tests -q`, repository scans for remaining `translate english` blocks and classified player-visible Chinese, plus Ren'Py lint if a runnable SDK entry point becomes available.

---

### Task 1: Define The Translation Migration Contract

**Files:**
- Create: `tests/test_translation_source_language.py`
- Modify: `docs/aegis/work/2026-08-03-english-source-chinese-translation/40-atomic-tasks.md`

**Why this task exists:**
- Protects the main journey: English users see English by default and Chinese users retain the original Chinese UI/dialogue.
- Converts scope exceptions into explicit test data instead of relying on an unsafe global Han-character ban.

**Impact / Compatibility:**
- Test-only change; no runtime files change.
- The test must distinguish player-visible Ren'Py statements from comments, Python strings, logs, prompts, URLs, and bilingual fields.

**Verification:**
- `python -m pytest tests/test_translation_source_language.py -q` must fail against the current Chinese-source structure for the expected migration-contract assertions.

- [ ] Write parser helpers that identify `translate <language>` blocks, `old/new` string pairs, dialogue/menu/screen strings, interpolation tokens, and Ren'Py text tags.
- [ ] Add assertions that migrated translation files have no reversible `translate english` text blocks, default player-visible source strings are English, Chinese translations exist for migrated pairs, and token/tag sets match.
- [ ] Run the target test and record the expected RED failures caused by current `translate english` and Chinese default-source text.
- [ ] Commit the test and RED evidence notes.

### Task 2: Invert String Translation Tables

**Files:**
- Modify: `game/Submods/MAICA_ChatSubmod/*.rpy`
- Modify: `game/Submods/MAICA_ChatSubmod/tl/*.rpy`
- Create then remove after use: `tools/invert_maica_translations.py`

**Why this task exists:**
- Moves `_()` UI strings, menu captions, status text, tooltips, and errors to English source ownership while retaining Chinese display text.

**Impact / Compatibility:**
- Only paired player-visible string literals change owners.
- Existing English text is copied byte-for-byte; missing English is newly translated.

**Verification:**
- `python -m pytest tests/test_translation_source_language.py -q` must reduce failures to dialogue-block or explicitly classified residuals.

**Repair Track:**
- Root cause: Chinese `old` strings are source keys and English `new` strings are secondary values.
- Canonical owners changed: matching main `.rpy` literals and `tl/*.rpy` string tables.
- Compatibility: interpolation and text-tag sets must remain equal after inversion.

**Retirement Track:**
- Retire reversible `translate english strings` ownership after each pair is promoted.
- Preserve unrelated `translate chinese style` blocks and any non-player-visible bilingual logic.

- [ ] Implement the one-time helper to extract unambiguous `old Chinese -> new English` pairs and reject duplicate conflicts or token/tag mismatches.
- [ ] Run the helper in dry-run mode and inspect its conflict report.
- [ ] Apply only conflict-free string-pair inversions to main and `tl` files.
- [ ] Manually resolve missing translations and conflicts within the approved player-visible scope.
- [ ] Run the target test and inspect every remaining failure.
- [ ] Remove the one-time helper after its output has been reviewed.
- [ ] Commit the string-table migration.

### Task 3: Invert Dialogue Translation Blocks

**Files:**
- Modify: `game/Submods/MAICA_ChatSubmod/chat.rpy`
- Modify: `game/Submods/MAICA_ChatSubmod/main.rpy`
- Modify: `game/Submods/MAICA_ChatSubmod/trigger_labels.rpy`
- Modify: corresponding `game/Submods/MAICA_ChatSubmod/tl/*.rpy`

**Why this task exists:**
- Makes spoken dialogue and translated menu flow English-first without changing story labels or execution order.

**Impact / Compatibility:**
- Translation IDs and source labels remain unchanged.
- Character speakers, expressions, `{w}`, `{nw}`, `{fast}`, substitutions, and control statements remain structurally identical.

**Verification:**
- `python -m pytest tests/test_translation_source_language.py -q` must pass after all classified blocks are migrated.

**Repair Track:**
- Root cause: English dialogue currently lives under `translate english <id>` while Chinese lives in the label source.
- Canonical owners changed: source dialogue statements and same-ID Chinese translation blocks.

**Retirement Track:**
- Retire `translate english <id>` blocks after promoting their dialogue.
- Preserve existing Chinese-only blocks that translate upstream English content not owned by this submod.

- [ ] Pair each English translation ID with its unique source statement and verify speaker/token/tag parity.
- [ ] Promote existing English dialogue exactly as written.
- [ ] Rewrite paired blocks as `translate chinese <same-id>` containing the original Chinese dialogue.
- [ ] Add English for player-visible Chinese dialogue with no current English block and retain the Chinese under stable generated/current IDs.
- [ ] Run the target test and resolve all non-exempt findings.
- [ ] Commit the dialogue-block migration.

### Task 4: Full Regression And Evidence Closure

**Files:**
- Modify: `docs/aegis/work/2026-08-03-english-source-chinese-translation/40-atomic-tasks.md`
- Create: `docs/aegis/work/2026-08-03-english-source-chinese-translation/50-evidence.md`

**Why this task exists:**
- Proves the migration stayed inside its boundary and did not break existing Python-side behavior.

**Impact / Compatibility:**
- Verification and documentation only.
- Ren'Py runtime rendering remains a residual risk if no local SDK executable is available.

**Verification:**
- `python -m pytest tests/test_translation_source_language.py -q`
- `python -m pytest tests -q`
- `rg -n "^translate english" game/Submods/MAICA_ChatSubmod/tl`
- `git diff --check`

- [ ] Run the translation contract test from a clean process.
- [ ] Run the complete repository pytest suite.
- [ ] Review every remaining `translate english` match and record why it is retained, or migrate it.
- [ ] Review the diff for accidental changes to logs, prompts, URLs, bilingual fields, labels, and persistent settings.
- [ ] Run `git diff --check` and any locally discoverable Ren'Py lint command.
- [ ] Record exact commands, results, runtime gaps, and residual risks in `50-evidence.md`.
- [ ] Update task/checkpoint status and commit verification artifacts with the implementation.

