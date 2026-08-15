"""Generate and validate placeholder translations for common Ren'Py Say lines."""

from __future__ import print_function

import argparse
import hashlib
import re
import sys
from pathlib import Path


LABEL_RE = re.compile(r"^\s*label\s+([A-Za-z_][A-Za-z0-9_.]*)\b")
SAY_RE = re.compile(
    r'^(?P<who>[A-Za-z_][A-Za-z0-9_.]*)'
    r'(?:\s+@?[A-Za-z0-9_]+)*\s+"'
)
TRANSLATE_RE = re.compile(
    r"^\s*translate\s+\S+\s+([A-Za-z_][A-Za-z0-9_]*)\s*:"
)
HASH_SUFFIX_RE = re.compile(r"_([0-9a-f]{8})(?:_\d+)?$")
EXPLICIT_ID_RE = re.compile(r"(?:^|\s)id\s+[A-Za-z_][A-Za-z0-9_]*\b")

NON_SAY_HEADS = {
    "call",
    "default",
    "define",
    "elif",
    "for",
    "hide",
    "if",
    "image",
    "jump",
    "label",
    "new",
    "old",
    "play",
    "queue",
    "return",
    "scene",
    "screen",
    "show",
    "stop",
    "style",
    "transform",
    "translate",
    "voice",
    "while",
    "with",
}


class TranslationError(Exception):
    pass


def strip_inline_comment(line):
    quote = None
    escaped = False

    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue

        if char == "\\" and quote is not None:
            escaped = True
            continue

        if quote is not None:
            if char == quote:
                quote = None
            continue

        if char in ('"', "'"):
            quote = char
        elif char == "#":
            return line[:index]

    return line


def collapse_outer_whitespace(text):
    output = []
    quote = None
    escaped = False
    pending_space = False

    for char in text.strip():
        if escaped:
            output.append(char)
            escaped = False
            continue

        if quote is not None:
            output.append(char)
            if char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue

        if char in ('"', "'"):
            if pending_space and output:
                output.append(" ")
            pending_space = False
            quote = char
            output.append(char)
        elif char.isspace():
            pending_space = True
        else:
            if pending_space and output:
                output.append(" ")
            pending_space = False
            output.append(char)

    return "".join(output)


def closing_double_quote(code, opening_index):
    escaped = False

    for index in range(opening_index + 1, len(code)):
        char = code[index]
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            return index

    return None


def parse_say_code(line):
    code = collapse_outer_whitespace(strip_inline_comment(line))
    match = SAY_RE.match(code)
    if match is None or match.group("who") in NON_SAY_HEADS:
        return None

    opening_index = match.end() - 1
    closing_index = closing_double_quote(code, opening_index)
    if closing_index is None:
        raise TranslationError("multiline or unterminated dialogue is unsupported")

    tail = code[closing_index + 1 :].strip()
    if EXPLICIT_ID_RE.search(tail):
        raise TranslationError("an explicit id clause requires the Ren'Py generator")

    return code


def statement_digest(code):
    payload = (code + "\r\n").encode("utf-8")
    return hashlib.md5(payload).hexdigest()[:8]


def normalized_label(label):
    return label.replace(".", "_")


def next_identifier(label, digest, reserved):
    base = "{}_{}".format(normalized_label(label), digest)
    identifier = base
    suffix = 0

    while identifier in reserved:
        suffix += 1
        identifier = "{}_{}".format(base, suffix)

    reserved.add(identifier)
    return identifier


def source_display_path(source, project_root):
    source = source.resolve()
    root = project_root.resolve()
    try:
        return source.relative_to(root).as_posix()
    except ValueError:
        return source.as_posix()


def source_statement(source, line_number):
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    if line_number < 1 or line_number > len(lines):
        raise TranslationError(
            "line {} is outside file length {}".format(line_number, len(lines))
        )

    current_label = None
    for index, line in enumerate(lines, 1):
        label_match = LABEL_RE.match(line)
        if label_match is not None:
            current_label = label_match.group(1)
        if index == line_number:
            code = parse_say_code(line)
            if code is None:
                raise TranslationError(
                    "line {} is not a supported Say statement".format(line_number)
                )
            if current_label is None:
                raise TranslationError(
                    "line {} is not inside a source label".format(line_number)
                )
            return current_label, code


def generate_blocks(source, start, end, language, project_root):
    if start < 1 or end < start:
        raise TranslationError("line range must satisfy 1 <= start <= end")

    lines = source.read_text(encoding="utf-8-sig").splitlines()
    if end > len(lines):
        raise TranslationError(
            "end line {} exceeds file length {}".format(end, len(lines))
        )

    current_label = None
    reserved = set()
    selected = []

    for line_number, line in enumerate(lines, 1):
        label_match = LABEL_RE.match(line)
        if label_match is not None:
            current_label = label_match.group(1)

        try:
            code = parse_say_code(line)
        except TranslationError as exc:
            if start <= line_number <= end:
                raise TranslationError("line {}: {}".format(line_number, exc))
            continue

        if code is None or current_label is None:
            continue

        identifier = next_identifier(
            current_label, statement_digest(code), reserved
        )
        if start <= line_number <= end:
            selected.append((line_number, identifier, code))

    if not selected:
        raise TranslationError("no supported Say statements found in the selected range")

    display_path = source_display_path(source, project_root)
    blocks = []
    for line_number, identifier, code in selected:
        blocks.extend(
            [
                "# {}:{}".format(display_path, line_number),
                "",
                "translate {} {}:".format(language, identifier),
                "    # {}".format(code),
                "    {}".format(code),
                "",
            ]
        )

    return "\n".join(blocks).rstrip() + "\n"


def iter_translation_blocks(lines):
    identifier = None
    start_line = None
    source_codes = []

    for line_number, line in enumerate(lines, 1):
        match = TRANSLATE_RE.match(line)
        if match is not None:
            if identifier is not None:
                yield identifier, start_line, source_codes
            identifier = match.group(1)
            start_line = line_number
            source_codes = []
            continue

        if identifier is None:
            continue

        comment = re.match(r"^\s*#\s?(.*)$", line)
        if comment is None:
            continue

        try:
            code = parse_say_code(comment.group(1))
        except TranslationError:
            code = None
        if code is not None:
            source_codes.append(code)

    if identifier is not None:
        yield identifier, start_line, source_codes


def validate_file(path, identifier_prefix):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    checked = 0
    skipped = 0
    errors = []

    for identifier, line_number, source_codes in iter_translation_blocks(lines):
        if identifier_prefix and not identifier.startswith(identifier_prefix):
            continue
        if not source_codes:
            skipped += 1
            continue

        match = HASH_SUFFIX_RE.search(identifier)
        if match is None:
            skipped += 1
            continue

        payload = "".join(code + "\r\n" for code in source_codes)
        expected = hashlib.md5(payload.encode("utf-8")).hexdigest()[:8]
        actual = match.group(1)
        checked += 1
        if actual != expected:
            errors.append(
                "{}:{}: {} uses {}, expected {}".format(
                    path, line_number, identifier, actual, expected
                )
            )

    if checked == 0:
        raise TranslationError(
            "no hash-based translation blocks with source Say comments were checked"
        )
    if errors:
        raise TranslationError("\n".join(errors))

    return checked, skipped


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate and validate common Ren'Py placeholder translations."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    id_parser = subparsers.add_parser("id", help="compute one translation identifier")
    id_parser.add_argument("statement", nargs="?", help="canonical one-line Say statement")
    id_parser.add_argument("--label", help="enclosing label for a supplied statement")
    id_parser.add_argument("--source", type=Path, help="read the statement from this file")
    id_parser.add_argument("--line", type=int, help="one-based source line number")

    generate_parser = subparsers.add_parser(
        "generate", help="print placeholder blocks for a source line range"
    )
    generate_parser.add_argument("source", type=Path)
    generate_parser.add_argument("--start", type=int, required=True)
    generate_parser.add_argument("--end", type=int, required=True)
    generate_parser.add_argument("--language", default="chinese")
    generate_parser.add_argument("--project-root", type=Path, default=Path.cwd())

    validate_parser = subparsers.add_parser(
        "validate", help="validate hashes using generated source comments"
    )
    validate_parser.add_argument("translation", type=Path)
    validate_parser.add_argument("--identifier-prefix")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    try:
        if args.command == "id":
            if args.source is not None:
                if args.statement is not None or args.label is not None:
                    raise TranslationError(
                        "use either --source/--line or --label with a statement"
                    )
                if args.line is None:
                    raise TranslationError("--source requires --line")
                label, code = source_statement(args.source, args.line)
            else:
                if args.line is not None:
                    raise TranslationError("--line requires --source")
                if args.statement is None or args.label is None:
                    raise TranslationError(
                        "supply --source/--line or --label with a statement"
                    )
                code = parse_say_code(args.statement)
                if code is None:
                    raise TranslationError("statement is not a supported Say statement")
                label = args.label
            print(
                "{}_{}".format(
                    normalized_label(label), statement_digest(code)
                )
            )
        elif args.command == "generate":
            sys.stdout.write(
                generate_blocks(
                    args.source,
                    args.start,
                    args.end,
                    args.language,
                    args.project_root,
                )
            )
        else:
            checked, skipped = validate_file(
                args.translation, args.identifier_prefix
            )
            print(
                "Validated {} translation blocks (skipped {}).".format(
                    checked, skipped
                )
            )
    except (OSError, TranslationError) as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
