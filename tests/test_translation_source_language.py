import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBMOD = ROOT / "game" / "Submods" / "MAICA_ChatSubmod"
TL = SUBMOD / "tl"
NON_RUNTIME_TEXT_FILES = {"raw_session_example.rpy"}
KNOWN_HOST_TRANSLATION_KEYS = {
    "Actually...",
    "Add",
    "Cancel",
    "Close",
    "Good luck with Monika!",
    "Hi [player],",
    "Ignore",
    "It's about [_gtext].",
    "It's me.",
    "It's nothing to worry about.",
    "Knock.",
    "Listen.",
    "Nevermind",
    "No",
    "Not yet",
    "Okay.",
    "Open the door.",
    "P.S: Don't tell her about me!",
    "Paste",
    "Quit",
    "Submods",
    "Yes",
    "[_opendoor_text]",
}

TRANSLATE_ENGLISH_RE = re.compile(r"(?m)^\s*translate\s+english(?:\s+\S+)?\s*:")
TRANSLATE_CHINESE_ID_RE = re.compile(r"(?m)^\s*translate\s+chinese\s+(?!strings\b)(?P<id>\S+)\s*:")
TRANSLATE_CHINESE_HEADER_RE = re.compile(r"^translate\s+chinese\s+(?!strings\b)\S+\s*:\s*$")
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


def test_chinese_translation_headers_are_separate_and_blocks_are_indented():
    malformed = []
    for path in rpy_files(TL):
        lines = read(path).splitlines()
        for index, line in enumerate(lines):
            if "translate chinese" in line and not line.startswith("translate chinese"):
                malformed.append("{}:{} translation header is joined to another statement".format(
                    path.relative_to(ROOT), index + 1
                ))

            if not TRANSLATE_CHINESE_HEADER_RE.match(line):
                continue

            body_index = index + 1
            while body_index < len(lines):
                body = lines[body_index]
                if body.strip() and not body.lstrip().startswith("#"):
                    break
                body_index += 1

            if body_index >= len(lines) or not lines[body_index].startswith((" ", "\t")):
                malformed.append("{}:{} translation block has no indented statement".format(
                    path.relative_to(ROOT), index + 1
                ))

    assert not malformed, "malformed Chinese translation blocks:\n{}".format("\n".join(malformed))


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


def test_chinese_string_keys_do_not_conflict_with_known_host_translations():
    conflicts = []
    for path in rpy_files(TL):
        for match in STRING_PAIR_RE.finditer(read(path)):
            if match.group("old") in KNOWN_HOST_TRANSLATION_KEYS:
                conflicts.append("{}: {}".format(path.relative_to(ROOT), match.group("old")))

    assert not conflicts, "Chinese string keys conflict with host translations:\n{}".format(
        "\n".join(conflicts)
    )


def test_maica_description_status_and_event_overrides_are_chinese():
    source = read(TL / "maica_description.rpy")
    normalized_source = " ".join(source.split())
    expected_snippets = [
        'MaicaAiStatus.IDLE: u"MAICA当前空闲"',
        'MaicaAiStatus.CONNECTED: u"MAICA已连接并准备就绪"',
        'MaicaAiStatus.TOKEN_INVALID: u"账号或密码无效"',
        'MaicaAiStatus.VERSION_OLD: u"检测到安装版本过旧, 请更新到最新版"',
        'MaicaAiStatus.NO_INTERNET: u"检测到子模组离线',
        'MaicaAiStatus.CERTIFI_RESTART_REQUIRED: u"执行了证书修复, 请重启以生效"',
        'prompt="我们去天堂树林吧", category=["你", "我们", "模组", "MAICA"]',
        'prompt="关于\'MVista\'", category=["你", "我们", "模组", "MAICA"]',
    ]

    missing = [
        snippet for snippet in expected_snippets if snippet not in normalized_source
    ]

    assert not missing, "missing Chinese MAICA description overrides:\n{}".format(
        "\n".join(missing)
    )
