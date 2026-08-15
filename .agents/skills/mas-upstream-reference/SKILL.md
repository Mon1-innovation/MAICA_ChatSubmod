---
name: mas-upstream-reference
description: Verify MAICA ChatSubmod integration with its host mod, Monika After Story (MAS), against the upstream MAS source. Use when a task depends on MAS labels, screens, store variables, persistent data, event or submod APIs, hooks, initialization and load order, file layout, Ren'Py behavior, version compatibility, or any claim about how MAS currently works.
---

# MAS Upstream Reference

Treat this repository as a submod that runs inside Monika After Story, not as a standalone frontend.
Treat the Monika After Story repository as the authoritative upstream implementation for this submod:

- Upstream repository: https://github.com/monika-after-story/monikamoddev

## Verification Workflow

1. Inspect the relevant MAICA ChatSubmod code first. Identify the exact MAS symbol, hook, lifecycle assumption, or behavior on which it depends.
2. Establish the target MAS revision. Honor a user-provided version, tag, branch, or commit. If none is provided, inspect the upstream default branch for current behavior and state that choice. Do not assume the latest upstream source matches an installed MAS release.
3. Prefer an existing local MAS checkout when it matches the target revision. Otherwise inspect the repository on GitHub or create a temporary shallow clone outside this repository. Do not vendor or commit upstream files here.
4. Search upstream definitions and call sites together. Check guards, initialization order, mutations, and version-specific branches; a symbol's definition alone may not establish runtime behavior.
5. Determine whether the dependency is a documented or intentionally exposed submod API, or an internal MAS implementation detail. Do not claim stability or compatibility without evidence.
6. Compare the verified upstream behavior with the local assumption before changing code. Keep any compatibility handling narrowly scoped and consistent with existing project conventions.
7. When upstream verification materially affects the result, report the inspected revision and relevant source path or symbol. Prefer a commit permalink when citing GitHub source.

## Evidence Rules

- Treat upstream source as evidence only for the inspected revision.
- Distinguish source behavior from behavior observed in a running MAS installation.
- Distinguish facts verified upstream from local inferences and proposed compatibility measures.
- If upstream cannot be accessed or the target version cannot be identified, state the limitation instead of presenting an assumption as verified behavior.
