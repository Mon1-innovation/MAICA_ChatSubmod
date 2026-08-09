# MAICA Android Startup Errors Atomic Tasks

- [x] Add a source contract test proving `ANDROID_MASBASE` references inside `init 5 python in maica` are qualified through `store`.
- [x] Add a source contract test proving `migration_1_2_0` no longer indexes persistent settings with `max_history_token`.
- [x] Run the new tests against the unchanged source and record the expected red failures.
- [x] Qualify Android host path access in `api.rpy`.
- [x] Remove the obsolete migration clamp that was discarded by `maica_reset_setting()`.
- [x] Run the focused contract/runtime tests, the scoped project test suite, `git diff --check`, and inspect `git status`.
