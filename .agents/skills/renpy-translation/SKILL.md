---
name: renpy-translation
description: Generate, insert, and validate Ren'Py dialogue translations and placeholder translate blocks. Use when work involves .rpy files, tl directories, missing dialogue translations, source line ranges, translation label renames, or Ren'Py translation identifiers and MD5 digests in MAICA ChatSubmod or similar Ren'Py projects.
---

# Ren'Py Translation

Use the bundled script for the repository's common single-line Say statements. Keep generation read-only until the proposed blocks have been reviewed.

## Workflow

1. Inspect the source range, destination context, and current diff. Preserve unrelated user changes.
2. Generate placeholder blocks to stdout:

   ```powershell
   python .agents/skills/renpy-translation/scripts/renpy_translation.py generate game/Submods/MAICA_ChatSubmod/chat.rpy --start 1267 --end 1276 --language chinese --project-root .
   ```

3. Verify the detected source label, line references, dialogue text, attributes, text tags, interpolations, and identifiers against the requested range.
4. Insert only the reviewed blocks at the requested destination with `apply_patch`. A placeholder repeats the source dialogue verbatim; do not invent a translation.
5. Validate the affected destination blocks:

   ```powershell
   python .agents/skills/renpy-translation/scripts/renpy_translation.py validate game/Submods/MAICA_ChatSubmod/tl/chat.rpy --identifier-prefix maica_wants_location_reread_
   ```

6. Run the relevant project tests and inspect the final scoped diff.

For one statement, compute its identifier directly:

```powershell
python .agents/skills/renpy-translation/scripts/renpy_translation.py id --source game/Submods/MAICA_ChatSubmod/chat.rpy --line 1269
```

## Safety Boundaries

- Treat script output as a proposal, not authorization to overwrite a translation file.
- Do not replace an existing human translation with a placeholder.
- Stop instead of guessing when the selected range contains multiline Say syntax, an explicit `id` clause, custom parser statements, or translation grouping that the script rejects.
- Use the project's Ren'Py translation generator for unsupported syntax. Check upstream source only for a version-specific behavior claim or when generated output contradicts the installed engine.
- Read [translation-identifiers.md](references/translation-identifiers.md) when explaining the algorithm, diagnosing an ID mismatch, or extending the script.
