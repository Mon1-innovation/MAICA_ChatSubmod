import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBMOD = ROOT / "game" / "Submods" / "MAICA_ChatSubmod"
TL = SUBMOD / "tl"
NON_RUNTIME_TEXT_FILES = {"raw_session_example.rpy"}

TRANSLATE_ENGLISH_RE = re.compile(r"(?m)^\s*translate\s+english(?:\s+\S+)?\s*:")
TRANSLATE_CHINESE_ID_RE = re.compile(r"(?m)^\s*translate\s+chinese\s+(?!strings\b)(?P<id>\S+)\s*:")
STRING_PAIR_RE = re.compile(
    r'^\s*old\s+(["\'])(?P<old>.*?)(?<!\\)\1\s*\r?\n'
    r'^\s*new\s+(["\'])(?P<new>.*?)(?<!\\)\3\s*$',
    re.MULTILINE,
)
INTERPOLATION_RE = re.compile(r"(?<!\[)\[(?!\[)[^\]]+\]")
HAN_RE = re.compile(r"[\u3400-\u9fff]")
LOCALIZED_LITERAL_RE = re.compile(r"_\(\s*([\"'])(?P<value>.*?)(?<!\\)\1")
DIALOGUE_RE = re.compile(r"^\s*(?:m|extend)\s+[^\"\r\n]*\"(?P<value>.*)\"", re.MULTILINE)
SCREEN_TEXT_RE = re.compile(r"^\s*(?:text|textbutton)\s+([\"'])(?P<value>.*?)(?<!\\)\1", re.MULTILINE)
ASSIGNMENT_RE = re.compile(r"^\s*\$\s+(?P<name>[A-Za-z_]\w*)\s*=\s*(?P<value>.*)$", re.MULTILINE)
EVENT_METADATA_RE = re.compile(r"^\s*(?:prompt|category)\s*=\s*(?P<value>.*)$", re.MULTILINE)


def rpy_files(directory):
    return sorted(directory.glob("*.rpy"))


def read(path):
    return path.read_text(encoding="utf-8-sig")


def tokens(value):
    return sorted(INTERPOLATION_RE.findall(value))


def test_default_language_remains_english():
    api = read(SUBMOD / "api.rpy")
    assert re.search(
        r'if\s+not\s+config\.language\s*:\s*\r?\n\s*config\.language\s*=\s*["\']english["\']',
        api,
    )


def test_english_translation_blocks_are_retired():
    matches = []
    for path in rpy_files(TL):
        for match in TRANSLATE_ENGLISH_RE.finditer(read(path)):
            line = read(path).count("\n", 0, match.start()) + 1
            matches.append("{}:{}".format(path.relative_to(ROOT), line))

    assert not matches, "remaining English translation blocks:\n{}".format("\n".join(matches))


def test_chinese_string_pairs_preserve_interpolation_tokens():
    mismatches = []
    for path in rpy_files(TL):
        source = read(path)
        for match in STRING_PAIR_RE.finditer(source):
            if tokens(match.group("old")) != tokens(match.group("new")):
                line = source.count("\n", 0, match.start()) + 1
                mismatches.append("{}:{}".format(path.relative_to(ROOT), line))

    assert not mismatches, "translation interpolation mismatches:\n{}".format("\n".join(mismatches))


def test_default_localized_literals_and_dialogue_are_not_chinese():
    matches = []
    for path in rpy_files(SUBMOD):
        if path.name in NON_RUNTIME_TEXT_FILES:
            continue
        source = read(path)
        for pattern in (LOCALIZED_LITERAL_RE, DIALOGUE_RE, SCREEN_TEXT_RE):
            for match in pattern.finditer(source):
                line_start = source.rfind("\n", 0, match.start()) + 1
                if source[line_start:match.start()].lstrip().startswith("#"):
                    continue
                if HAN_RE.search(match.group("value")):
                    line = source.count("\n", 0, match.start()) + 1
                    matches.append("{}:{}".format(path.relative_to(ROOT), line))

    assert not matches, "Chinese remains in default player-visible source:\n{}".format("\n".join(matches))


def test_interpolated_dialogue_variables_are_not_assigned_chinese():
    matches = []
    for path in rpy_files(SUBMOD):
        if path.name in NON_RUNTIME_TEXT_FILES:
            continue
        source = read(path)
        for match in ASSIGNMENT_RE.finditer(source):
            if "[{}]".format(match.group("name")) in source and HAN_RE.search(match.group("value")):
                line = source.count("\n", 0, match.start()) + 1
                matches.append("{}:{}".format(path.relative_to(ROOT), line))

    assert not matches, "Chinese assigned to interpolated dialogue variables:\n{}".format("\n".join(matches))


def test_event_menu_metadata_is_not_chinese_by_default():
    matches = []
    source = read(SUBMOD / "chat.rpy")
    for match in EVENT_METADATA_RE.finditer(source):
        if HAN_RE.search(match.group("value")):
            line = source.count("\n", 0, match.start()) + 1
            matches.append("chat.rpy:{}".format(line))

    assert not matches, "Chinese remains in event menu metadata:\n{}".format("\n".join(matches))


def test_chinese_translation_ids_are_unique():
    owners = {}
    duplicates = []
    for path in rpy_files(TL):
        for match in TRANSLATE_CHINESE_ID_RE.finditer(read(path)):
            translation_id = match.group("id")
            if translation_id in owners:
                duplicates.append("{} ({}, {})".format(translation_id, owners[translation_id], path.name))
            owners[translation_id] = path.name

    assert not duplicates, "duplicate Chinese translation IDs:\n{}".format("\n".join(duplicates))


def test_duplicate_chinese_string_keys_have_one_translation():
    translations = {}
    conflicts = []
    for path in rpy_files(TL):
        for match in STRING_PAIR_RE.finditer(read(path)):
            old = match.group("old")
            new = match.group("new")
            if old in translations and translations[old] != new:
                conflicts.append("{} -> {!r} / {!r}".format(old, translations[old], new))
            translations[old] = new

    assert not conflicts, "conflicting Chinese string translations:\n{}".format("\n".join(conflicts))
