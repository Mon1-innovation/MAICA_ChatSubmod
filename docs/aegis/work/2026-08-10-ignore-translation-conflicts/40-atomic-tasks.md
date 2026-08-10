# Ignore Translation Conflicts Atomic Tasks

- [x] Add the static contract test for the registration and workflow.
- [x] Run the focused test and confirm the expected red result.
- [x] Add `dependencies={"Ignore Translation Conflicts": (None, None)},` to the MAICA registration.
- [x] Add the conditional `v1.0.0` archive download and target-directory staging step before packaging.
- [x] Run the focused contract test and confirm green.
- [x] Run `pytest -q tests` and the CRLF-aware whitespace check.
- [x] Inspect the final diff, status, package target path, and residual verification risk.
