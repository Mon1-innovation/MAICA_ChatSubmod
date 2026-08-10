# Ignore Translation Conflicts Dependency Design

## Goal

Make every release package contain the `Ignore Translation Conflicts` MAS submod
from `MAS_ignore_tl_conficts_submod` at tag `v1.0.0`, and declare it as an
unversioned dependency of MAICA.

## Design

The release workflow will download the dependency repository's tag archive
before the existing zip step. It will extract only
`game/Submods/IgnoreTranslationConflicts` into the checked-out repository, so
the existing package and release steps automatically include the dependency.
The download URL is pinned to the requested `v1.0.0` tag; the runtime
dependency declaration will not impose a minimum or maximum version.

The MAICA registration in
`game/Submods/MAICA_ChatSubmod/header.rpy` will pass:

```python
dependencies={"Ignore Translation Conflicts": (None, None)}
```

The MAS registry implementation at the user-provided `zz_submods.rpy` path is
reference-only for this task: it already accepts and checks the `dependencies`
parameter, including the unrestricted `(None, None)` case.

## Build Flow and Failure Handling

The dependency step will use the GitHub tag archive, fail on HTTP or extraction
errors, and verify that the expected submod directory exists before copying it.
It will run under the same release-creation condition as the existing package
step, preventing development builds and already-existing releases from gaining
unrelated workspace changes.

## Compatibility Boundary

- The existing MAICA registration fields and release naming remain unchanged.
- The dependency is not committed into the repository; release builds remain
  the owner of dependency acquisition.
- A packaged release must contain the expected dependency path before the zip
  is created.
- At runtime, an installation without `Ignore Translation Conflicts` will be
  rejected by the existing MAS dependency checker. This is intentional and is
  why the release workflow supplies the directory.

## Verification

Verification will inspect the final diff and assert that:

- the registration names the dependency with `(None, None)`;
- the workflow downloads the requested tag, checks the extracted path, and
  performs that work before `Create zip package`;
- the changed files have no whitespace errors; and
- the workflow's shell structure remains valid enough for the repository's
  available local checks.

## Working Artifacts

### TaskIntentDraft

- Requested outcome: add one packaged MAS dependency and declare it without a
  version constraint.
- Scope: release workflow and MAICA submod registration only.
- Risk hint: build-time network/archive failure and runtime missing-dependency
  startup failure.

### BaselineReadSetHint

- `.github/workflows/release.yml`: current release conditions and zip owner.
- `game/Submods/MAICA_ChatSubmod/header.rpy`: current registration and the
  user's dependency comment.
- External `zz_submods.rpy`: MAS constructor contract and dependency semantics.
- Dependency release source: actual archive layout and registered submod name.

### ImpactStatementDraft

- Owners: GitHub Actions owns acquisition; MAICA registration owns the runtime
  contract; MAS owns dependency validation.
- Non-goals: no changes to MAS registry code, dependency source, updater logic,
  or unrelated packaging behavior.
