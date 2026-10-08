# MPostal Attachment Lifecycle Implementation Plan

**Goal:** Remove an accepted `.mail` and its companion `.mms` from `characters` together while preserving image upload, retry, and history-preview behavior.

**Architecture:** Move accepted originals into `vista_cache/mpostal_pending` and store that managed path on the postal record. Keep the original through reply generation failures. After a reply is generated, delete only the managed original and retain the record-owned thumbnail. Delete that thumbnail only after the corresponding postal is removed from history.

**Compatibility Boundary:** Keep normal MVista upload behavior unchanged. Keep invalid, empty, and early mail handling unchanged. Use Python 2/3-compatible filesystem APIs and the existing MAS function-plugin/event lifecycle on desktop, zhCN, and mobile Ren'Py 8 variants.

**Verified Contracts:** MAICA backend `0f189fd504d1863f6b54105708bc9d488e84e29e` accepts multipart field `content` at `POST /vista`, returns the registered image UUID, and accepts its absolute URL in top-level `vision`. MAS revisions `a7e260c308000e2e21c173d5f751bce81e19b7ba`, `9a83771e92d2ed0344298a8cd41f96583e9ddaa3`, and `a5b1b7b9de2cc1b3b4989d4eed76f1ecfa5cef86` retain the function-plugin and event-list contracts used here.

## Task 1: Lock the lifecycle contract

- [x] Add real filesystem tests for managed staging, rollback, deletion, and path containment.
- [x] Add source-contract tests for receipt ordering and separate original/preview cleanup points.

## Task 2: Add managed attachment storage

- [x] Add a Ren'Py-independent attachment store under `game/python-packages`.
- [x] Stage valid companion images before deleting accepted mail.
- [x] Restore the image when accepted-mail deletion fails.
- [x] Adopt unambiguous legacy `characters/*.mms` paths at startup.

## Task 3: Separate original and preview ownership

- [x] Keep pending originals through upload and failed generation attempts.
- [x] Delete pending originals only after a response reaches `received`.
- [x] Prefer the postal-owned thumbnail in the history list.
- [x] Remove the postal by object identity before deleting its thumbnail.

## Task 4: Verify compatibility and scope

- [x] Run focused lifecycle tests and the complete pytest suite.
- [x] Run compile, whitespace, diff, and worktree checks.
- [x] Report runtime-only residual risks separately.
