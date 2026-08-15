# Ren'Py Translation Identifiers

## Ordinary Say Statements

For the single-line Say statements used throughout this repository, Ren'Py builds the digest from canonical statement code followed by CRLF:

```text
digest = md5((canonical_say_code + "\r\n").encode("utf-8")).hexdigest()[:8]
identifier = normalized_label + "_" + digest
```

`normalized_label` replaces `.` with `_`. Canonical code includes the speaker, image attributes, quoted dialogue, and supported trailing clauses. It excludes indentation and source comments.

Example:

```text
m 2tsblp "I always want to know more about you, and there's no reason not knowing where my [bf] lives!"
```

has digest `77fbef55`. Under `label maica_wants_location2`, its normal identifier is `maica_wants_location2_77fbef55`.

If that identifier is already reserved, Ren'Py appends `_1`, `_2`, and so on. Identical dialogue under different labels keeps the same digest but receives a different full identifier.

## Cases Requiring Ren'Py

Use the target project's Ren'Py generator rather than reconstructing an identifier when a statement uses:

- multiline dialogue syntax;
- an explicit `id` clause;
- custom parser statements or unusual Character expressions;
- a translation block containing multiple Say nodes;
- engine-version-specific translation grouping.

The implementation lives in Ren'Py's script translator (`renpy/translation/__init__.py`, `ScriptTranslator.create_translate` and `unique_identifier`). The installed engine is authoritative when its output differs from this repository's common-case helper.

