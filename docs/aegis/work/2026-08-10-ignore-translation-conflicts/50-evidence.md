# Ignore Translation Conflicts Verification Evidence

## Red/Green Contract Test

- RED: `pytest -q tests/test_ignore_translation_conflicts_dependency.py` failed
  2 tests before implementation: the MAICA registration assertion and the
  missing workflow step lookup.
- GREEN: the same command passed `2 passed` after implementation.

## Build and Archive Checks

- The remote tag archive smoke check found
  `MAS_ignore_tl_conficts_submod-1.0.0/game/Submods/IgnoreTranslationConflicts/zz_ignore_translation_conflicts.rpy`.
- PyYAML parsed `.github/workflows/release.yml`; the workflow contains 11
  steps, with dependency staging before package creation and the requested
  release condition.
- Git Bash `bash -n` accepted the extracted dependency step script.
- `git -c core.whitespace=cr-at-eol diff --check` passed. The repository has
  CRLF/mixed line endings, so the default check reports CR as trailing
  whitespace even for valid existing-style lines.

## Regression

- `pytest -q tests -k "not test_a_development_build_contract"`: `336 passed,
  1 deselected`.
- Unfiltered `pytest -q tests`: `336 passed, 1 failed`. The remaining failure is
  the pre-existing `test_a_development_build_contract`, which expects
  `maica_is_dev = True` while `api.rpy` and `HEAD` contain `False`; `api.rpy`
  was not changed by this task.

## Residual Risk

- A GitHub-hosted release run was not dispatched locally; the network archive,
  YAML structure, and Bash syntax were verified independently.
- Local source checkouts without the downloaded dependency will still fail the
  existing MAS dependency check by design.
