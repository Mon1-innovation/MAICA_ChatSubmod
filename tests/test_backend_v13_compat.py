"""Collectable static contracts for the backend-v1.3 release cut-over."""

import ast
import io
import json
import re
import tokenize
import warnings
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SUBMOD = ROOT / "game" / "Submods" / "MAICA_ChatSubmod"
PYTHON = ROOT / "game" / "python-packages"
ASSETS = ROOT / "game" / "mod_assets" / "console"

RENAMES = {
    "sfe_aggressive": "prompt_pname_repl",
    "mf_aggressive": "mf_llm_concl",
    "tnd_aggressive": "mf_const_tools",
    "esc_aggressive": "esearch_llm_concl",
    "amt_aggressive": "mf_precheck_mt",
    "pre_additive": "mf_context_rnds",
    "post_additive": "mt_context_rnds",
    "dscl_pvn": "gen_quality_chk",
    "pre_astp": "mf_disable_loop",
    "post_astp": "mt_disable_loop",
    "enforce_lang": "gen_enforce_lang",
    "sf_extraction": "savefile_access",
    "max_length": "session_len_limit",
}
PERSISTENT_SETTINGS = tuple(sorted(set(RENAMES.values())))
RETIRED_PERSISTENT_SETTINGS = {"ic_prep", "twk_super"}


def path_for(relative):
    path = ROOT / relative
    assert path.is_file(), "required contract source is missing: {}".format(relative)
    return path


def source(relative):
    return path_for(relative).read_text(encoding="utf-8")


def block_after(text, marker, radius=700):
    match = re.search(marker, text)
    assert match, "source context is missing: {}".format(marker)
    return text[match.start():match.start() + radius]


def literal_dict(text, name):
    match = re.search(r"\b{}\s*=\s*\{{".format(re.escape(name)), text)
    assert match, "dictionary {!r} is missing".format(name)
    start = text.find("{", match.start())
    depth = 0
    quote = None
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in "'\"":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return ast.literal_eval(text[start:index + 1])
    assert False, "dictionary {!r} is not closed".format(name)


def literal_assignment(text, name):
    tree = ast.parse(text)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    assert False, "assignment {!r} is missing".format(name)


def lex_source(text):
    """Linear quote/escape/comment-aware lexer used for Ren'Py structure checks."""
    tokens = []
    index = 0
    while index < len(text):
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if char == "#":
            index = text.find("\n", index)
            if index < 0:
                break
            continue
        if char in "'\"":
            quote = char * (3 if text.startswith(char * 3, index) else 1)
            index += len(quote)
            value = []
            while index < len(text) and not text.startswith(quote, index):
                if text[index] == "\\" and index + 1 < len(text):
                    value.append(text[index + 1])
                    index += 2
                else:
                    value.append(text[index])
                    index += 1
            assert index < len(text), "unterminated string in static contract source"
            index += len(quote)
            tokens.append(("STRING", "".join(value)))
            continue
        if char.isalpha() or char == "_":
            end = index + 1
            while end < len(text) and (text[end].isalnum() or text[end] == "_"):
                end += 1
            tokens.append(("NAME", text[index:end]))
            index = end
            continue
        tokens.append(("OP", char))
        index += 1
    return tokens


def strip_comments_and_strings(text, suffix):
    """Leave identifiers/operators while eliminating prose false positives."""
    if suffix == ".py":
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        return tokenize.untokenize(
            (kind, "" if kind in (tokenize.COMMENT, tokenize.STRING) else value)
            for kind, value, _start, _end, _line in tokens
        )
    text = re.sub(r"(?s)(?:[rubfRUBF]*)('''.*?'''|\"\"\".*?\"\"\")", "", text)
    text = re.sub(r"(?m)#.*$", "", text)
    return re.sub(r"(?s)(?:[rubfRUBF]*)(['\"])(?:\\.|(?!\1).)*\1", "", text)


def runtime_identifiers(relative):
    path = path_for(relative)
    return strip_comments_and_strings(path.read_text(encoding="utf-8"), path.suffix)


def screen_blocks(text):
    return re.findall(r"(?ms)^screen\s+\w+[^\n]*:.*?(?=^(?:screen|label|init)\b|\Z)", text)


def named_screen(text, name):
    marker = re.compile(r"(?m)^screen\s+{}\b".format(re.escape(name)))
    for block in screen_blocks(text):
        if marker.search(block):
            return block
    assert False, "screen is missing: {}".format(name)


def default_owner_exists(text, key):
    tokens = lex_source(text)
    canonical = {"maica_default_dict", "maica_advanced_setting"}
    for index in range(len(tokens) - 2):
        if tokens[index][0] != "NAME" or tokens[index][1] not in canonical:
            continue
        if tokens[index + 1:index + 3] != [("OP", "="), ("OP", "{")]:
            continue
        depth = 1
        cursor = index + 3
        while cursor < len(tokens) and depth:
            kind, value = tokens[cursor]
            if (kind, value) == ("OP", "{"):
                depth += 1
            elif (kind, value) == ("OP", "}"):
                depth -= 1
            elif depth == 1 and kind == "STRING" and value == key:
                if cursor + 1 < len(tokens) and tokens[cursor + 1] == ("OP", ":"):
                    return True
            cursor += 1
    return False


def action_calls(tokens):
    for index, token in enumerate(tokens):
        if token != ("NAME", "action"):
            continue
        cursor = index + 1
        while cursor + 1 < len(tokens):
            if tokens[cursor][0] == "NAME" and tokens[cursor + 1] == ("OP", "("):
                name = tokens[cursor][1]
                depth = 1
                end = cursor + 2
                while end < len(tokens) and depth:
                    if tokens[end] == ("OP", "("):
                        depth += 1
                    elif tokens[end] == ("OP", ")"):
                        depth -= 1
                    end += 1
                if depth == 0:
                    yield name, tokens[cursor + 2:end - 1]
                    cursor = end
                    continue
            cursor += 1


def action_expressions(control):
    lines = control.splitlines()
    index = 0
    while index < len(lines):
        match = re.match(r"^(\s*)action\b", lines[index])
        if not match:
            index += 1
            continue
        indent = len(match.group(1))
        expression = [lines[index]]
        balance = sum(lines[index].count(char) for char in "([{") - sum(
            lines[index].count(char) for char in ")]}")
        index += 1
        while index < len(lines):
            next_match = re.match(r"^(\s*)(\w+)\b", lines[index])
            if balance <= 0 or (next_match and len(next_match.group(1)) <= indent):
                break
            expression.append(lines[index])
            balance += sum(lines[index].count(char) for char in "([{") - sum(
                lines[index].count(char) for char in ")]}")
            index += 1
        yield "\n".join(expression)


def call_arguments(tokens):
    arguments = []
    argument = []
    depth = 0
    for token in tokens:
        if token[0] == "OP" and token[1] in "([{":
            depth += 1
        elif token[0] == "OP" and token[1] in ")]}" and depth:
            depth -= 1
        if token == ("OP", ",") and depth == 0:
            arguments.append(argument)
            argument = []
        else:
            argument.append(token)
    if argument:
        arguments.append(argument)
    return arguments


def ui_owner_exists(text, key):
    for screen in screen_blocks(text):
        for control in re.findall(r"(?ms)^\s*(?:textbutton|use\s+\w+)[^\n]*.*?(?=^\s*(?:textbutton|use\s+\w+|if|elif|else)\b|\Z)", screen):
            for expression in action_expressions(control):
                for name, arguments in action_calls(lex_source(expression)):
                    positional = call_arguments(arguments)
                    if (name in ("SetDict", "ToggleDict", "SetField") and len(positional) >= 2
                            and positional[1] == [("STRING", key)]):
                        return True
                    if name == "Function" and any(argument == [("STRING", key)] for argument in positional[1:]):
                        return True
    return False


def subscript_parts(node):
    parts = []
    while isinstance(node, ast.Subscript):
        if not isinstance(node.slice, ast.Constant) or not isinstance(node.slice.value, str):
            return None, []
        parts.append(node.slice.value)
        node = node.value
    if isinstance(node, ast.Name):
        return node.id, list(reversed(parts))
    if isinstance(node, ast.Attribute):
        return node.attr, list(reversed(parts))
    return None, []


def runtime_owner_exists(text, key):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = ast.parse(text)

    allowed_containers = {"chat_params", "modelconfig", "settings_dict", "request_body", "payload"}

    def literal_paths(node):
        paths = set()
        if not isinstance(node, ast.Dict):
            return frozenset()
        for key_node, value_node in zip(node.keys, node.values):
            if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                continue
            if key_node.value == key:
                paths.add(())
            elif key_node.value in allowed_containers:
                paths.update((key_node.value,) + path for path in literal_paths(value_node))
        return frozenset(paths)

    def expression_paths(node, environment):
        if isinstance(node, ast.Name):
            return environment.get(node.id, frozenset())
        if isinstance(node, ast.Dict):
            return literal_paths(node)
        if isinstance(node, ast.Call):
            name = node.func.attr if isinstance(node.func, ast.Attribute) else ""
            if name in ("dumps", "dump"):
                return frozenset(path for argument in node.args for path in expression_paths(argument, environment))
            if name == "encode" and isinstance(node.func, ast.Attribute):
                return expression_paths(node.func.value, environment)
        return frozenset()

    def merge_environments(target, branches):
        for name in set().union(*(set(branch) for branch in branches)):
            target[name] = frozenset(path for branch in branches for path in branch.get(name, frozenset()))

    def analyze_statements(statements, environment):
        for statement in statements:
            if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
                value_paths = expression_paths(statement.value, environment)
                for target in targets:
                    if isinstance(target, ast.Name):
                        environment[target.id] = frozenset(value_paths)
                    elif isinstance(target, ast.Subscript):
                        root, parts = subscript_parts(target)
                        if root in environment and parts and parts[-1] == key:
                            container_path = tuple(parts[:-1])
                            if not container_path or all(item in allowed_containers for item in container_path):
                                environment[root] = environment[root] | {container_path}
                        elif root in environment and parts and all(item in allowed_containers for item in parts):
                            environment[root] = environment[root] | {
                                tuple(parts) + path for path in value_paths
                            }
            elif isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
                call = statement.value
                if isinstance(call.func, ast.Attribute) and call.func.attr in ("send", "send_json", "post", "request"):
                    if any(expression_paths(argument, environment) for argument in call.args):
                        return True
                if isinstance(call.func, ast.Attribute) and call.func.attr in ("update", "setdefault"):
                    root, parts = subscript_parts(call.func.value)
                    if isinstance(call.func.value, ast.Name):
                        root, parts = call.func.value.id, []
                    if root in environment and all(item in allowed_containers for item in parts):
                        added = set()
                        if call.func.attr == "setdefault" and call.args:
                            first = call.args[0]
                            if isinstance(first, ast.Constant) and first.value == key:
                                added.add(tuple(parts))
                        else:
                            for argument in call.args:
                                added.update(tuple(parts) + path for path in literal_paths(argument))
                            if any(keyword.arg == key for keyword in call.keywords):
                                added.add(tuple(parts))
                        environment[root] = environment[root] | added
            elif isinstance(statement, ast.Return):
                if expression_paths(statement.value, environment):
                    return True
            elif isinstance(statement, ast.If):
                branches = []
                for body in (statement.body, statement.orelse):
                    branch = dict(environment)
                    if analyze_statements(body, branch):
                        return True
                    branches.append(branch)
                merge_environments(environment, branches)
            elif isinstance(statement, (ast.For, ast.While)):
                branch = dict(environment)
                if analyze_statements(statement.body, branch):
                    return True
                merge_environments(environment, (environment, branch))
                if analyze_statements(statement.orelse, environment):
                    return True
            elif isinstance(statement, ast.Try):
                initial = dict(environment)
                normal = dict(initial)
                if analyze_statements(statement.body, normal):
                    return True
                if analyze_statements(statement.orelse, normal):
                    return True
                branches = [normal]
                for handler in statement.handlers:
                    branch = dict(initial)
                    if analyze_statements(handler.body, branch):
                        return True
                    branches.append(branch)
                merge_environments(environment, branches or [environment])
                if analyze_statements(statement.finalbody, environment):
                    return True
        return False

    for function in (node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
        names = {node.id for node in ast.walk(function) if isinstance(node, ast.Name)}
        relevant = re.search(r"(?:build|normalize|send|setting|config|process|chat)", function.name) or names.intersection(
            {"chat_params", "modelconfig", "settings_dict", "request_body", "payload", "data"})
        if relevant and analyze_statements(function.body, {}):
            return True
    return False


def python_owner_names(text, context="synthetic Python source"):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(text)
    except (SyntaxError, ValueError, TypeError) as ast_error:
        try:
            tokens = [token for token in tokenize.generate_tokens(io.StringIO(text).readline)
                      if token.type not in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                                            tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING)]
        except (tokenize.TokenError, IndentationError, SyntaxError) as tokenize_error:
            snippet = text[:120].replace("\n", "\\n")
            raise AssertionError(
                "could not parse {} (AST: {}; tokenize: {}; input: {!r})".format(
                    context, ast_error, tokenize_error, snippet
                )
            )
        found = set()
        for index, token in enumerate(tokens):
            if token.type == tokenize.NAME and token.string in RENAMES:
                previous = tokens[index - 1].string if index else ""
                following = tokens[index + 1].string if index + 1 < len(tokens) else ""
                if previous == "." or following in ("=", "("):
                    found.add(token.string)
            elif token.type == tokenize.STRING:
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", SyntaxWarning)
                        value = ast.literal_eval(token.string)
                except (SyntaxError, ValueError, TypeError):
                    continue
                previous = tokens[index - 1].string if index else ""
                following = tokens[index + 1].string if index + 1 < len(tokens) else ""
                if value in RENAMES and (previous == "[" or following in ("]", ":")):
                    found.add(value)
        return found
    pure_maps = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            pairs = []
            for key_node, value_node in zip(node.keys, node.values):
                if isinstance(key_node, ast.Constant) and isinstance(value_node, ast.Constant):
                    pairs.append((key_node.value, value_node.value))
            if (len(pairs) == len(node.keys) == len(RENAMES)
                    and len({key for key, _value in pairs}) == len(RENAMES)
                    and dict(pairs) == RENAMES):
                pure_maps.add(id(node))
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in RENAMES:
            found.add(node.id)
        elif isinstance(node, ast.Attribute) and node.attr in RENAMES:
            found.add(node.attr)
        elif isinstance(node, ast.Subscript):
            value = node.slice.value if isinstance(node.slice, ast.Constant) else None
            if value in RENAMES:
                found.add(value)
        elif isinstance(node, ast.keyword) and node.arg in RENAMES:
            found.add(node.arg)
        elif isinstance(node, ast.Dict) and id(node) not in pure_maps:
            for key_node in node.keys:
                if isinstance(key_node, ast.Constant) and key_node.value in RENAMES:
                    found.add(key_node.value)
    return found


def rpy_owner_names(text, stats=None):
    tokens = lex_source(text)
    exempt_indices = set()
    stack = []
    for index, token in enumerate(tokens):
        if stats is not None:
            stats["visits"] = stats.get("visits", 0) + 1
        if token == ("OP", "{"):
            if stack:
                stack[-1]["member"].append(token)
            stack.append({"members": [], "member": [], "start": index + 1, "depth": 0})
        elif token == ("OP", "}") and stack:
            state = stack.pop()
            if state["member"]:
                state["members"].append((state["start"], state["member"]))
            members = state["members"]
            strict = bool(members) and all(
                len(item) == 3 and item[0][0] == "STRING" and item[1] == ("OP", ":") and item[2][0] == "STRING"
                for _position, item in members
            )
            pairs = [(position, item[0][1], item[2][1]) for position, item in members] if strict else []
            if (len(pairs) == len(RENAMES)
                    and len({old for _position, old, _new in pairs}) == len(RENAMES)
                    and {old: new for _position, old, new in pairs} == RENAMES):
                exempt_indices.update(pos for pos, _old, _new in pairs)
            if stack:
                stack[-1]["member"].append(("OP", "}"))
        elif stack and token[0] == "OP" and token[1] in "([":
            stack[-1]["depth"] += 1
            stack[-1]["member"].append(token)
        elif stack and token[0] == "OP" and token[1] in ")]" and stack[-1]["depth"]:
            stack[-1]["depth"] -= 1
            stack[-1]["member"].append(token)
        elif stack and token == ("OP", ",") and stack[-1]["depth"] == 0:
            state = stack[-1]
            if state["member"]:
                state["members"].append((state["start"], state["member"]))
            state["member"] = []
            state["start"] = index + 1
        elif stack:
            stack[-1]["member"].append(token)
    found = set()
    for index, (kind, value) in enumerate(tokens):
        if stats is not None:
            stats["visits"] += 1
        if index in exempt_indices:
            continue
        previous = tokens[index - 1][1] if index else ""
        following = tokens[index + 1][1] if index + 1 < len(tokens) else ""
        if value in RENAMES and ((kind == "STRING" and (previous == "[" or following in ("]", ":")))
                                 or (kind == "NAME" and (previous == "." or following in ("=", "(")))):
            found.add(value)
    if stats is not None:
        stats["tokens"] = len(tokens)
    return found


def ws_status_owner_exists(text, status):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and any(isinstance(item, ast.Constant) and item.value == status for item in node.comparators):
            return True
        if isinstance(node, ast.keyword) and node.arg == "except_ws_status":
            if any(isinstance(item, ast.Constant) and item.value == status for item in ast.walk(node.value)):
                return True
    return False


def quality_reference_exists(text):
    tokens = lex_source(text)
    for index, (kind, value) in enumerate(tokens):
        if value != "gen_quality_chk":
            continue
        previous = tokens[index - 1][1] if index else ""
        following = tokens[index + 1][1] if index + 1 < len(tokens) else ""
        if kind == "NAME" or (kind == "STRING" and (previous in ("[", "(", ",") or following in ("]", ")", ":", ","))):
            return True
    return False


def assert_key_default(text, key, value_pattern):
    assert re.search(r"['\"]{}['\"]\s*:\s*{}".format(re.escape(key), value_pattern), text)


def assert_key_control(text, key, upper):
    context = block_after(text, r"(?:textbutton|use\s+\w+)[^\n]*{}|{}[^\n]*(?:textbutton|use\s+\w+)".format(key, key), 500)
    assert re.search(r"\b0\s*,\s*{}\b|(?:max|upper|maximum)\s*=\s*{}\b".format(upper, upper), context)
    assert "ToggleDict" not in context


def function_body(text, name_pattern):
    match = re.search(r"(?m)^(?P<indent>[ \t]*)def\s+(?:{})\s*\([^\n]*\):".format(name_pattern), text)
    assert match, "function is missing: {}".format(name_pattern)
    indent = match.group("indent")
    following = text[match.end():]
    next_def = re.search(r"(?m)^{}def\s+\w+\s*\(".format(re.escape(indent)), following)
    return following[:next_def.start()] if next_def else following


def conditional_body(text, condition_pattern):
    match = re.search(r"(?m)^(?P<indent>[ \t]*)if\s+{}\s*:\s*$".format(condition_pattern), text)
    assert match, "conditional branch is missing: {}".format(condition_pattern)
    indent = len(match.group("indent"))
    lines = []
    for line in text[match.end():].splitlines():
        if not line.strip():
            lines.append(line)
            continue
        width = len(line) - len(line.lstrip(" \t"))
        if width <= indent:
            break
        lines.append(line)
    return "\n".join(lines)


def assert_key_has_semantic_upper_bound(text, key, upper):
    contexts = []
    for match in re.finditer(r"\b{}\b|['\"]{}['\"]".format(key, key), text):
        contexts.append(text[max(0, match.start() - 220):match.end() + 320])
    assert contexts, "normalization owner is missing: {}".format(key)
    escaped = re.escape(key)
    clamp_patterns = (
        r"(?:\b{0}\b|['\"]{0}['\"])[^\n]{{0,160}}=\s*min\s*\([^,\n]+,\s*{1}\s*\)".format(escaped, upper),
        r"=\s*min\s*\([^,\n]*(?:\b{0}\b|['\"]{0}['\"])[^,\n]*,\s*{1}\s*\)".format(escaped, upper),
    )
    if any(any(re.search(pattern, context) for pattern in clamp_patterns) for context in contexts):
        return

    branch = re.compile(
        r"(?m)^(?P<indent>[ \t]*)if\s+[^\n]*(?:\b{0}\b|['\"]{0}['\"])[^\n]*"
        r"(?:>\s*{1}\b|not\s+[^\n]*<=\s*{1}\b)[^\n]*:\s*\n"
        r"(?P<body>(?:(?P=indent)[ \t]+[^\n]*(?:\n|$)){{1,12}})".format(escaped, upper)
    )
    for match in branch.finditer(text):
        body = match.group("body")
        clamps_to_upper = re.search(
            r"(?:\b{0}\b|\[['\"]{0}['\"]\])\s*=\s*{1}\b".format(escaped, upper),
            body,
        )
        rejects = re.search(r"\b(?:raise|return)\b", body)
        if clamps_to_upper or rejects:
            return
    assert False, "{} over {} is neither clamped nor rejected".format(key, upper)


def test_a_backend_version_is_final():
    assert re.search(r"SUPPORT_BACKEND\s*=\s*['\"]1\.3\.000['\"]", source("game/python-packages/maica.py"))


def test_a_migration_is_structurally_registered_and_invoked():
    migration = source("game/Submods/MAICA_ChatSubmod/migrations.rpy")
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    queue = block_after(migration, r"migration_queue\s*=", 1000)
    assert re.search(r"\(\s*['\"]1\.8\.0['\"]\s*,\s*migration_1_8_0\s*\)", queue)
    assert re.search(r"\bmaica_migration\s*\(", api) or re.search(r"\bmigrations\.migration_instance\s*\(", api)
    assert re.search(r"persistent\._maica_last_version\s*=\s*store\.maica_ver", api)


def test_a_dev_override_remains_ignored():
    assert re.search(r"(?:^|/)dev_enable\.rpy$", source(".gitignore"), re.M)


@pytest.mark.parametrize(("old", "new"), RENAMES.items())
def test_b_migration_rename_map_has_exact_pair(old, new):
    mapping = literal_dict(source("game/python-packages/maica_v13_migration.py"), "SETTING_RENAMES")
    assert mapping.get(old) == new, "{} must migrate to {}".format(old, new)


def test_b_migration_rename_map_has_no_unreviewed_keys():
    mapping = literal_dict(source("game/python-packages/maica_v13_migration.py"), "SETTING_RENAMES")
    assert set(mapping) == set(RENAMES)


def test_b_retired_persistent_settings_are_explicit():
    retired = set(literal_assignment(
        source("game/python-packages/maica_v13_migration.py"),
        "RETIRED_PERSISTENT_SETTINGS",
    ))
    assert retired == RETIRED_PERSISTENT_SETTINGS


def test_b_renpy_migration_does_not_duplicate_the_rename_map():
    migration = source("game/Submods/MAICA_ChatSubmod/migrations.rpy")
    assert "chat_param_renames" not in migration


@pytest.mark.parametrize(
    "relative",
    (
        "game/Submods/MAICA_ChatSubmod/header.rpy",
        "game/Submods/MAICA_ChatSubmod/screen_subs.rpy",
        "game/Submods/MAICA_ChatSubmod/tl/header.rpy",
        "game/Submods/MAICA_ChatSubmod/tl/screen_subs.rpy",
    ),
)
def test_b_user_visible_setting_text_retires_legacy_names(relative):
    text = source(relative)
    for old in RENAMES:
        assert not re.search(
            r"(?<![A-Za-z0-9_]){}(?![A-Za-z0-9_])".format(re.escape(old)),
            text,
        ), "{} remains in {}".format(old, relative)


@pytest.mark.parametrize("new", PERSISTENT_SETTINGS)
def test_b_canonical_default_owner_exists(new):
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    assert default_owner_exists(header, new), "default owner missing: {}".format(new)


@pytest.mark.parametrize("new", PERSISTENT_SETTINGS)
def test_b_canonical_ui_owner_exists(new):
    ui = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    ui += "\n".join(screen_blocks(source("game/Submods/MAICA_ChatSubmod/header.rpy")))
    assert ui_owner_exists(ui, new), "UI owner missing: {}".format(new)


@pytest.mark.parametrize("new", PERSISTENT_SETTINGS)
def test_b_canonical_runtime_upload_owner_exists(new):
    runtime = source("game/python-packages/maica.py") + source("game/python-packages/maica_tasker_sub_sessionsender.py")
    assert runtime_owner_exists(runtime, new), "runtime owner missing: {}".format(new)


def test_b_owner_helpers_reject_default_only_synthetic_source():
    defaults = 'defaults = {"prompt_pname_repl": False}'
    assert not ui_owner_exists(defaults, "prompt_pname_repl")
    assert not runtime_owner_exists(defaults, "prompt_pname_repl")


def test_b_owner_helpers_ignore_comments_but_accept_structural_owners():
    commented_ui = 'screen x():\n    # action SetDict(data, "prompt_pname_repl", True)\n    textbutton "x"\n'
    real_ui = 'screen x():\n    textbutton "x":\n        action SetDict(data, "prompt_pname_repl", True)\n'
    commented_runtime = 'def build_payload():\n    # data["prompt_pname_repl"] = value\n    return {}\n'
    real_runtime = 'def build_payload():\n    data = {"prompt_pname_repl": value}\n    return data\n'
    assert not ui_owner_exists(commented_ui, "prompt_pname_repl")
    assert ui_owner_exists(real_ui, "prompt_pname_repl")
    assert not runtime_owner_exists(commented_runtime, "prompt_pname_repl")
    assert runtime_owner_exists(real_runtime, "prompt_pname_repl")


def test_b_default_owner_requires_a_named_canonical_dictionary():
    key = "prompt_pname_repl"
    assert not default_owner_exists('# maica_default_dict = {"prompt_pname_repl": False}\n', key)
    assert not default_owner_exists('note = "maica_default_dict = {\\\"prompt_pname_repl\\\": False}"\n', key)
    assert not default_owner_exists('unrelated = {"prompt_pname_repl": False}\n', key)
    assert not default_owner_exists('maica_default_dict = {"group": {"prompt_pname_repl": False}}\n', key)
    assert default_owner_exists('maica_default_dict = {"prompt_pname_repl": False}\n', key)
    assert default_owner_exists('maica_advanced_setting = {"prompt_pname_repl": False}\n', key)


def test_b_ui_owner_binds_the_key_to_the_setting_action():
    misleading = (
        'screen x():\n'
        '    textbutton "prompt_pname_repl":\n'
        '        action SetDict(other, "other", True)\n'
    )
    assert not ui_owner_exists(misleading, "prompt_pname_repl")


def test_b_ui_owner_stops_at_the_next_control_property():
    misleading = (
        'screen x():\n'
        '    textbutton "x":\n'
        '        action SetDict(data, "other", True)\n'
        '        tooltip SetDict(data, "prompt_pname_repl", True)\n'
    )
    action_list = (
        'screen x():\n'
        '    textbutton "x":\n'
        '        action [SetDict(data, "other", True), '
        'SetDict(data, "prompt_pname_repl", True)]\n'
    )
    assert not ui_owner_exists(misleading, "prompt_pname_repl")
    assert ui_owner_exists(action_list, "prompt_pname_repl")


def test_b_runtime_owner_requires_an_outbound_payload_path():
    documentation = (
        'def build_payload():\n'
        '    labels = {"prompt_pname_repl": "Documentation"}\n'
        '    return {}\n'
    )
    attribute = 'def build_payload():\n    logger.prompt_pname_repl\n    return {}\n'
    nested_payload = (
        'def build_payload(value):\n'
        '    data = {"chat_params": {}}\n'
        '    data["chat_params"]["prompt_pname_repl"] = value\n'
        '    return data\n'
    )
    named_payload = (
        'def send(value):\n'
        '    request_body = {"prompt_pname_repl": value}\n'
        '    return request_body\n'
    )
    assert not runtime_owner_exists(documentation, "prompt_pname_repl")
    assert not runtime_owner_exists(attribute, "prompt_pname_repl")
    assert runtime_owner_exists(nested_payload, "prompt_pname_repl")
    assert runtime_owner_exists(named_payload, "prompt_pname_repl")


def test_b_runtime_owner_requires_keyed_data_to_reach_return_or_send():
    key = "prompt_pname_repl"
    dead_payload = 'def build():\n    payload = {"prompt_pname_repl": 1}\n    return {}\n'
    dead_chat_params = 'def build():\n    chat_params["prompt_pname_repl"] = 1\n    return {}\n'
    value_only = (
        'def build(labels):\n'
        '    payload = {}\n'
        '    payload.update({"other": labels["prompt_pname_repl"]})\n'
        '    return payload\n'
    )
    sent = (
        'def send(value, ws, json):\n'
        '    data = {"chat_params": {}}\n'
        '    data["chat_params"].update({"prompt_pname_repl": value})\n'
        '    ws.send(json.dumps(data))\n'
    )
    assert not runtime_owner_exists(dead_payload, key)
    assert not runtime_owner_exists(dead_chat_params, key)
    assert not runtime_owner_exists(value_only, key)
    assert runtime_owner_exists(sent, key)


def test_b_runtime_owner_accepts_direct_sink_dicts_and_local_aliases():
    key = "prompt_pname_repl"
    direct_send = 'def send(ws, value):\n    ws.send({"prompt_pname_repl": value})\n'
    nested_send = 'def send(ws, value):\n    ws.send({"chat_params": {"prompt_pname_repl": value}})\n'
    direct_return = 'def build(value):\n    return {"chat_params": {"prompt_pname_repl": value}}\n'
    alias = (
        'def send(ws, value):\n'
        '    payload = {"prompt_pname_repl": value}\n'
        '    wire = payload\n'
        '    ws.send(wire)\n'
    )
    assert runtime_owner_exists(direct_send, key)
    assert runtime_owner_exists(nested_send, key)
    assert runtime_owner_exists(direct_return, key)
    assert runtime_owner_exists(alias, key)


def test_b_runtime_owner_rejects_intermediate_subscript_components():
    source_text = (
        'def build(value):\n'
        '    payload = {}\n'
        '    payload["prompt_pname_repl"]["other"] = value\n'
        '    return payload\n'
    )
    assert not runtime_owner_exists(source_text, "prompt_pname_repl")


def test_b_runtime_owner_rejects_sink_value_side_references():
    source_text = (
        'def send(ws, labels):\n'
        '    ws.send({"other": labels["prompt_pname_repl"]})\n'
    )
    assert not runtime_owner_exists(source_text, "prompt_pname_repl")


def test_b_runtime_owner_rejects_unknown_nested_sink_containers():
    sent = 'def send(ws):\n    ws.send({"docs": {"prompt_pname_repl": "label"}})\n'
    returned = 'def build():\n    return {"docs": {"prompt_pname_repl": "label"}}\n'
    assert not runtime_owner_exists(sent, "prompt_pname_repl")
    assert not runtime_owner_exists(returned, "prompt_pname_repl")


def test_b_runtime_owner_preserves_alias_snapshot_across_rebinding():
    source_text = (
        'def send(ws, value):\n'
        '    payload = {"prompt_pname_repl": value}\n'
        '    wire = payload\n'
        '    payload = {}\n'
        '    ws.send(wire)\n'
    )
    assert runtime_owner_exists(source_text, "prompt_pname_repl")


def test_b_runtime_owner_tracks_serialization_wrapper_receivers():
    direct = (
        'def send(ws, json, value):\n'
        '    data = {"prompt_pname_repl": value}\n'
        '    ws.send(json.dumps(data).encode())\n'
    )
    alias = (
        'def send(ws, json, value):\n'
        '    data = {"prompt_pname_repl": value}\n'
        '    wire = json.dumps(data)\n'
        '    ws.send(wire.encode("utf-8"))\n'
    )
    assert runtime_owner_exists(direct, "prompt_pname_repl")
    assert runtime_owner_exists(alias, "prompt_pname_repl")


def test_b_runtime_owner_tracks_container_assignment_and_common_updates():
    key = "prompt_pname_repl"
    assigned = (
        'def build(value):\n'
        '    data = {}\n'
        '    data["chat_params"] = {"prompt_pname_repl": value}\n'
        '    return data\n'
    )
    setdefault = (
        'def build(value):\n'
        '    payload = {}\n'
        '    payload.setdefault("prompt_pname_repl", value)\n'
        '    return payload\n'
    )
    keyword_update = (
        'def build(value):\n'
        '    payload = {}\n'
        '    payload.update(prompt_pname_repl=value)\n'
        '    return payload\n'
    )
    value_side = (
        'def build(labels):\n'
        '    payload = {}\n'
        '    payload.setdefault("other", labels["prompt_pname_repl"])\n'
        '    return payload\n'
    )
    assert runtime_owner_exists(assigned, key)
    assert runtime_owner_exists(setdefault, key)
    assert runtime_owner_exists(keyword_update, key)
    assert not runtime_owner_exists(value_side, key)


def test_b_runtime_owner_analyzes_try_and_loop_else_paths():
    try_else = (
        'def send(ws, value):\n'
        '    try:\n'
        '        payload = {"prompt_pname_repl": value}\n'
        '    except ValueError:\n'
        '        payload = {}\n'
        '    else:\n'
        '        ws.send(payload)\n'
    )
    loop_else = (
        'def send(ws, values):\n'
        '    for value in values:\n'
        '        pass\n'
        '    else:\n'
        '        ws.send({"prompt_pname_repl": True})\n'
    )
    assert runtime_owner_exists(try_else, "prompt_pname_repl")
    assert runtime_owner_exists(loop_else, "prompt_pname_repl")


def test_c_regular_settings_use_renpy_language_and_system_timezone_defaults():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    target_default = function_body(header, r"maica_get_default_target_lang")
    assert re.search(r"['\"]chinese['\"]\s*:\s*['\"]zh['\"]", target_default)
    assert re.search(r"['\"]english['\"]\s*:\s*['\"]en['\"]", target_default)
    assert re.search(r"\.get\s*\([^,]+,\s*['\"]auto['\"]\s*\)", target_default)
    assert re.search(r"['\"]target_lang['\"]\s*:\s*maica_get_default_target_lang\s*\(\s*\)", header)
    assert re.search(r"['\"]tz['\"]\s*:\s*maica_get_system_timezone\s*\(\s*\)", header)
    assert 'persistent._maica_target_lang_mode == "renpy"' in header
    assert 'persistent._maica_tz_mode == "system"' in header
    assert "current_tz = store.maica_get_system_timezone()" in screen
    assert re.search(
        r"SetDict\s*\(\s*persistent\.maica_setting_dict\s*,\s*['\"]target_lang['\"]\s*,[^\n]*MaicaAiLang\.auto",
        screen,
    )
    assert re.search(r"SetField\s*\(\s*persistent\s*,\s*['\"]_maica_target_lang_mode['\"]\s*,\s*['\"]manual['\"]", screen)
    assert re.search(r"SetField\s*\(\s*persistent\s*,\s*['\"]_maica_tz_mode['\"]\s*,\s*['\"]system['\"]", screen)


def test_c_prompt_allow_nickname_uses_backend_default_true():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    runtime = source("game/python-packages/maica.py")
    assert_key_default(header, "prompt_allow_nickname", r"True\b")
    assert_key_default(runtime, "prompt_allow_nickname", r"True\b")
    assert re.search(r"get\s*\(\s*['\"]prompt_allow_nickname['\"]\s*,\s*True\s*\)", screen)


def test_c_savefile_access_defaults_to_enabled():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    runtime = source("game/python-packages/maica.py")
    assert_key_default(header, "savefile_access", r"True\b")
    assert re.search(r"self\.savefile_access\s*=\s*True\b", runtime)
    assert "savefile_access_marker_exists" in header
    assert "savefile_access_marker_exists" in runtime
    assert (ROOT / "game/Submods/MAICA_ChatSubmod/savefile_access").is_file()
    upload = function_body(header, r"_upload_persistent_dict")
    assert upload.index("savefile_access_marker_exists") < upload.index("copy.deepcopy")
    apply_settings = function_body(header, r"maica_apply_setting")
    discard_settings = function_body(header, r"maica_discard_setting")
    assert "savefile_access_marker_exists" not in apply_settings
    assert "savefile_access_marker_exists" not in discard_settings
    assert re.search(
        r"maica_instance\.savefile_access\s*=\s*persistent\.maica_setting_dict\[['\"]savefile_access['\"]\]",
        apply_settings,
    )


def test_c_tz_has_ui_and_outbound_owners():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    assert "maica_tz_setting" in screen and re.search(r"maica_setting_dict[^\n]*['\"]tz['\"]", screen)
    assert re.search(r"maica_setting_dict[^\n]*['\"]tz['\"]", header)


@pytest.mark.parametrize(
    ("key", "default"),
    (("mf_sf_access_impl", 1), ("mf_const_sf_access", 0), ("mt_concl_memory", 1)),
)
def test_c_tristate_default_and_control_are_integer_zero_to_two(key, default):
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    runtime = source("game/python-packages/maica.py")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    assert_key_default(header, key, r"{}\b".format(default))
    assert_key_default(runtime, key, r"{}\b".format(default))
    assert_key_control(screen, key, 2)


def test_c_tool_and_session_limits_are_two_and_28672():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    assert_key_default(header, "mt_disable_loop", r"True\b")
    assert_key_control(screen, "mf_const_tools", 2)
    normalize = source("game/python-packages/maica.py") + header
    assert_key_has_semantic_upper_bound(normalize, "mf_const_tools", 2)
    session_key = "session_len_limit" if "session_len_limit" in normalize else "max_history_token"
    assert_key_has_semantic_upper_bound(normalize, session_key, 28672)


def test_c_session_limit_translation_matches_the_current_source_range():
    translation = source("game/Submods/MAICA_ChatSubmod/tl/header.rpy")
    assert re.search(r'^\s*old\s+"会话保留的最大长度\. 范围512-28672\.', translation, re.M)
    assert re.search(r'^\s*new\s+"Max length each session will preserve, in range of 512-28672\.', translation, re.M)


@pytest.mark.parametrize("relative", ("game/python-packages/maica.py", "game/python-packages/maica_tasker_sub_sessionsender.py"))
def test_c_each_outbound_builder_retires_mt_extraction(relative):
    assert not re.search(r"['\"]mt_extraction['\"]\s*:", source(relative)), relative


def test_c_persistent_exports_retire_mas_sf_hcb():
    assert "mas_sf_hcb" not in source("game/Submods/MAICA_ChatSubmod/persistent_filter.json")
    assert "mas_sf_hcb" not in source("game/python-packages/json_exporter.py")


def test_d_login_and_generation_start_use_v13_protocol():
    tasker = source("game/python-packages/maica_tasker_sub.py")
    runtime = source("game/python-packages/maica.py") + tasker
    assert re.search(r"['\"]type['\"]\s*:\s*['\"]auth['\"]", tasker)
    assert "maica_mcore_gen_start" in runtime


@pytest.mark.parametrize("relative", ("game/python-packages/maica.py", "game/python-packages/maica_tasker_sub.py", "game/python-packages/maica_tasker_sub_sessionsender.py"))
def test_d_cookie_injection_is_retired_in_every_builder(relative):
    text = source(relative)
    patterns = (
        r"\[['\"]cookie['\"]\]\s*=", r"['\"]cookie['\"]\s*:",
        r"\.update\s*\([^)]*['\"]cookie['\"]", r"\.setdefault\s*\(\s*['\"]cookie['\"]",
        r"\bdict\s*\([^)]*\bcookie\s*=", r"\.update\s*\([^)]*\bcookie\s*=",
        r"\.setdefault\s*\(\s*cookie\s*=", r"\b(?:send|process_request|login|request_body)\s*\([^)]*\bcookie\s*=",
    )
    assert not any(re.search(pattern, text, re.S) for pattern in patterns), relative


def test_d_cookie_handler_task_and_strict_ui_are_retired():
    python_runtime = runtime_identifiers("game/python-packages/maica.py") + runtime_identifiers("game/python-packages/maica_tasker_sub.py")
    ui_runtime = runtime_identifiers("game/Submods/MAICA_ChatSubmod/header.rpy") + runtime_identifiers("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    assert "MAICAWSCookiesHandler" not in python_runtime
    assert "WSCookiesTask" not in python_runtime
    assert not re.search(r"\bstrict_mode\b", ui_runtime)


def test_d_current_ws_statuses_replace_retired_registrations():
    runtime = source("game/python-packages/maica.py") + source("game/python-packages/maica_tasker_sub.py")
    for current in ("maica_quality_status", "maica_loop_warn_reset", "maica_core_streaming_continue"):
        assert ws_status_owner_exists(runtime, current), "status is only prose or unregistered: {}".format(current)
    for old in ("maica_dscl_status", "maica_loop_warn_finished", "maica_core_nostream_reply"):
        assert not re.search(r"except_ws_status\s*=\s*\[[^]]*{}".format(old), runtime, re.S)


def test_d_ws_status_helper_ignores_comment_only_presence():
    assert not ws_status_owner_exists('def build():\n    # except_ws_status=["maica_quality_status"]\n    return None\n', "maica_quality_status")
    assert ws_status_owner_exists('def build():\n    task(except_ws_status=["maica_quality_status"])\n', "maica_quality_status")


def test_e_mtrigger_mspire_mpostal_and_temporary_trigger_payloads():
    trigger = source("game/python-packages/maica_mtrigger.py")
    sender = source("game/python-packages/maica_tasker_sub_sessionsender.py")
    assert "alter_value" in trigger
    assert re.search(
        r"common_affection_template\.name\s*:\s*['\"]alter_affection['\"]",
        trigger,
    )
    inspire = block_after(sender, r"class\s+MAICAMSpireProcessor", 3500)
    assert re.search(r"['\"]inspire['\"]\s*:\s*\{[^}]*ctg_weight", inspire, re.S)
    assert re.search(r"['\"]inspire['\"]\s*:\s*\{[^}]*use_cache", inspire, re.S)
    assert re.search(r"['\"]inspire['\"]\s*:\s*\{\s*\}", inspire)
    postal = block_after(sender, r"class\s+MAICAMPostalProcessor", 1800)
    assert "twk_super" in postal and "ic_prep" not in runtime_identifiers("game/python-packages/maica_tasker_sub_sessionsender.py")
    assert re.search(r"['\"]triggers['\"]\s*:", sender)
    assert not re.search(r"['\"]trigger['\"]\s*:", sender)


def test_e_twk_super_is_temporary_not_persistent():
    runtime = source("game/python-packages/maica.py")
    settings_builder = block_after(runtime, r"def\s+build_setting_config", 1800)
    assert "twk_super" not in settings_builder
    assert "remove_retired_persistent_settings(normalized)" in runtime

    ui = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    ui += source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    assert not ui_owner_exists(ui, "twk_super")
    assert ".pop(\"twk_super\"" not in ui


def test_e_advanced_setting_screen_matches_backend_document_order():
    ui = block_after(
        source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy"),
        r"screen\s+maica_advance_setting",
        30000,
    )
    expected = (
        "max_tokens",
        "seed",
        "top_p",
        "temperature",
        "frequency_penalty",
        "presence_penalty",
        "prompt_pname_repl",
        "prompt_allow_nickname",
        "mf_llm_concl",
        "mf_sf_access_impl",
        "mf_const_sf_access",
        "mf_const_tools",
        "esearch_llm_concl",
        "mf_precheck_mt",
        "mt_concl_memory",
        "nsfw_acceptive",
        "mf_context_rnds",
        "mt_context_rnds",
        "mf_disable_loop",
        "mt_disable_loop",
        "gen_enforce_lang",
    )
    positions = [ui.index('textbutton "{}'.format(name)) for name in expected]
    assert positions == sorted(positions)
    assert "twk_super" not in ui


def test_e_memory_template_preserves_backend_player_name_placeholder():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    trigger = source("game/Submods/MAICA_ChatSubmod/trigger.rpy")

    assert re.search(
        r"def\s+maica_validate_player_addition\([^)]*prefix_player\s*=\s*True",
        header,
    )
    assert re.search(
        r"addition\s*=\s*\(['\"]\{player_name\}['\"]\s*\+\s*raw_addition\.strip\(\)\s*if\s+prefix_player\s+else\s+raw_addition\.strip\(\)\)",
        header,
    )
    assert re.search(
        r"MTriggerBase\(\s*memory_template\s*,\s*['\"]write_memory['\"]",
        trigger,
    )
    assert re.search(
        r"maica_validate_player_addition\([^)]*prefix_player\s*=\s*False",
        trigger,
        re.S,
    )
    assert re.search(
        r"if\s+addition\s+is\s+not\s+None\s*:\s*(?:store\.)?persistent\.mas_player_additions\.append\(addition\)",
        trigger,
        re.S,
    )

    addition_input = named_screen(
        source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy"),
        "maica_addition_input",
    )
    assert re.search(
        r"if\s+persistent\._mas_player_addition\s+is\s+None\s*:\s*"
        r"persistent\._mas_player_addition\s*=\s*addition",
        addition_input,
    )
    assert re.search(r"prefix_player\s*=\s*edittarget\s+is\s+None", addition_input)


def test_e_player_addition_ui_escapes_markup_without_changing_values():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    chat = source("game/Submods/MAICA_ChatSubmod/chat.rpy")

    escape_helper = function_body(header, r"maica_escape_display_text")
    assert re.search(r"\.replace\(\s*['\"]\[['\"]\s*,\s*['\"]\[\[['\"]\s*\)", escape_helper)
    assert re.search(r"\.replace\(\s*['\"]\{['\"]\s*,\s*['\"]\{\{['\"]\s*\)", escape_helper)

    addition_screen = named_screen(screen, "maica_addition_setting")
    assert re.search(r"textbutton\s+maica_escape_display_text\s*\(\s*item\s*\)", addition_screen)

    delete_label = block_after(chat, r"label\s+maica_delete_information", 900)
    assert re.search(
        r"items\.append\s*\(\s*\[\s*maica_escape_display_text\s*\(\s*i\s*\)\s*,\s*i\s*,",
        delete_label,
        re.S,
    )


def test_e_list_setting_selection_is_screen_local_and_index_based():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    chat = source("game/Submods/MAICA_ChatSubmod/chat.rpy")

    assert "persistent.selectbool" not in header + screen + chat
    assert "default persistent.maica_player_additions_status" not in header

    for name in ("maica_addition_setting", "maica_mspire_category_setting"):
        setting_screen = named_screen(screen, name)
        assert re.search(r"default\s+selected_indices\s*=\s*set\s*\(\s*\)", setting_screen)
        assert re.search(r"for\s+index\s*,\s*item\s+in\s+enumerate\s*\(", setting_screen)
        assert re.search(r"ToggleSetMembership\s*\(\s*selected_indices\s*,\s*index\s*\)", setting_screen)
        assert re.search(r"Function\s*\(\s*maica_delete_selected_items\s*,", setting_screen)


def test_f_vista_list_and_download_routes_are_distinct():
    vista = source("game/python-packages/maica_vista_files_manager.py")
    listing = block_after(vista, r"def\s+list_remote\s*\(", 1600)
    download = block_after(vista, r"def\s+download\s*\(", 1600)
    assert "/vista/list" in listing
    assert re.search(r"/vista(?:['\"]|\?)", download)
    assert re.search(r"params\s*=\s*\{[^}]*['\"]content['\"]", download, re.S)


def test_f_emotion_endpoint_is_retired():
    for path in list(PYTHON.glob("*.py")) + list(SUBMOD.glob("*.rpy")):
        assert not re.search(r"['\"]/emotion(?:['\"/?]|$)", path.read_text(encoding="utf-8")), path.name


def test_f_nickname_has_default_and_ui_owner():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    assert_key_default(header, "prompt_allow_nickname", r"True\b")
    ui = header + screen
    control = block_after(ui, r"(?m)^\s*textbutton[^\n]*prompt_allow_nickname", 650)
    assert re.search(
        r"action[^\n]*(?:ToggleDict|SetDict)\s*\(\s*persistent\.maica_advanced_setting\s*,\s*['\"]prompt_allow_nickname['\"]",
        control,
    )
    assert re.search(r"persistent\.maica_advanced_setting(?:_status)?[^\n]*['\"]prompt_allow_nickname['\"]", control)


def test_f_legality_response_displays_distinct_latitude_and_longitude():
    runtime = source("game/python-packages/maica.py") + source("game/Submods/MAICA_ChatSubmod/api.rpy")
    legality = function_body(runtime, r"\w*legality\w*")
    latitude = re.search(
        r"(?P<var>\w+)\s*=\s*[^\n]*(?:content|result|res)[^\n]*(?:get\s*\(\s*['\"](?:latitude|lat)['\"]|\[['\"](?:latitude|lat)['\"]\])",
        legality,
    )
    longitude = re.search(
        r"(?P<var>\w+)\s*=\s*[^\n]*(?:content|result|res)[^\n]*(?:get\s*\(\s*['\"](?:longitude|lng|lon)['\"]|\[['\"](?:longitude|lng|lon)['\"]\])",
        legality,
    )
    assert latitude, "legality success path does not read latitude from response content"
    assert longitude, "legality success path does not read longitude from response content"
    lat_var, lon_var = latitude.group("var"), longitude.group("var")
    displays = re.findall(r"(?:format\s*\([^)]*\)|%\s*\([^)]*\)|f['\"][^'\"]*['\"])", legality, re.S)
    assert any(lat_var in display and lon_var in display for display in displays), "latitude and longitude must enter the same displayed success string"


def test_g_header_shared_additions_helper_enforces_both_byte_limits():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    helper = function_body(header, r"_?maica_\w*addition\w*")
    count_reject = conditional_body(helper, r"len\s*\(\s*\w*additions\w*\s*\)\s*(?:>=\s*512|>\s*511)")
    byte_reject = conditional_body(helper, r"len\s*\([^\n]*\.encode\s*\(\s*['\"]utf-8['\"]\s*\)[^\n]*\)\s*(?:>\s*1536|>=\s*1537)")
    for rejection in (count_reject, byte_reject):
        assert re.search(r"\b(?:return|raise|notify|show_screen)\b", rejection), "limit branch does not reject or notify"


def test_g_chat_and_screen_call_the_same_additions_helper():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    names = re.findall(r"def\s+(_?maica_\w*addition\w*)\s*\(", header)
    assert names, "shared additions validator is missing from header.rpy"
    chat = source("game/Submods/MAICA_ChatSubmod/chat.rpy")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    shared = [name for name in names if re.search(r"\b{}\s*\(".format(name), chat) and re.search(r"\b{}\s*\(".format(name), screen)]
    assert shared, "chat.rpy and screen_subs.rpy must call one shared additions helper"


def test_g_migration_preserves_additions_backup_and_notice():
    migration = source("game/Submods/MAICA_ChatSubmod/migrations.rpy")
    assert "_maica_v18_player_additions_backup" in migration
    assert "_maica_v18_player_additions_notice_seen" in migration
    migration_body = function_body(migration, r"migration_1_8_0")
    filtered_branch = conditional_body(migration_body, r"filtered\s*!=\s*additions")
    assert re.search(r"not\s+persistent\._maica_v18_player_additions_notice_seen", filtered_branch)
    assert re.search(r"\b(?:notify|show_screen)\b", filtered_branch)
    assert re.search(r"_maica_v18_player_additions_notice_seen\s*=\s*True", filtered_branch)


@pytest.mark.parametrize("relative", ("game/Submods/MAICA_ChatSubmod/header.rpy", "game/Submods/MAICA_ChatSubmod/chat.rpy", "game/Submods/MAICA_ChatSubmod/screen_subs.rpy"))
def test_g_old_1000_character_preprocessor_is_retired(relative):
    assert not re.search(r"(?:maxlen\s*=\s*1000|\[:\s*1000\s*\]|len\s*\([^)]*\)\s*>\s*1000)", source(relative)), relative


def test_g_persistent_upload_uses_the_player_addition_byte_limit():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    upload = function_body(header, r"_upload_persistent_dict")
    assert re.search(r"max_bytes\s*=\s*1536\b", upload)
    assert re.search(r"maica_v13_migration\.utf8_byte_length\s*\(", upload)


def test_g_v18_migration_runs_before_persistent_upload():
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")

    def ch30_preloop_priority(text, function_name):
        match = re.search(
            r"@store\.mas_submod_utils\.functionplugin\s*\(\s*['\"]ch30_preloop['\"]"
            r"(?P<args>[^)]*)\)\s*\n\s*def\s+{}\s*\(".format(function_name),
            text,
        )
        assert match, "{} is not registered for ch30_preloop".format(function_name)
        priority = re.search(r"\bpriority\s*=\s*(-?\d+)\b", match.group("args"))
        return int(priority.group(1)) if priority else 0

    migration_priority = ch30_preloop_priority(api, "maica_migration")
    upload_priority = ch30_preloop_priority(header, "_upload_persistent_dict")
    assert migration_priority < upload_priority


def test_g_chat_addition_input_does_not_keep_the_legacy_50_character_limit():
    chat = source("game/Submods/MAICA_ChatSubmod/chat.rpy")
    addition_label = block_after(chat, r"label\s+maica_input_information\s*:", 2200)
    assert re.search(r"\blength\s*=\s*1536\b", addition_label)


QUALITY_RUNTIME_FILES = (
    "game/Submods/MAICA_ChatSubmod/header.rpy",
    "game/Submods/MAICA_ChatSubmod/screen_subs.rpy",
    "game/python-packages/maica.py",
)

QUALITY_TRANSLATION_FILES = (
    "game/Submods/MAICA_ChatSubmod/tl/header.rpy",
    "game/Submods/MAICA_ChatSubmod/tl/screen_subs.rpy",
    "game/Submods/MAICA_ChatSubmod/tl/trigger.rpy",
    "game/Submods/MAICA_ChatSubmod/tl/trigger_labels.rpy",
)


@pytest.mark.parametrize("relative", QUALITY_RUNTIME_FILES)
def test_h_each_quality_runtime_reference_is_renamed(relative):
    text = source(relative)
    assert quality_reference_exists(text), "new quality owner missing in {}".format(relative)
    assert "dscl_pvn" not in runtime_identifiers(relative), "old quality runtime owner remains in {}".format(relative)


@pytest.mark.parametrize("relative", QUALITY_TRANSLATION_FILES)
def test_h_each_quality_translation_retires_the_old_identifier(relative):
    assert "dscl_pvn" not in runtime_identifiers(relative), "old quality translation remains in {}".format(relative)


def test_h_quality_asset_is_replaced():
    assert not (ASSETS / "dscl_pvn.png").exists()
    assert (ASSETS / "gen_quality_chk.png").is_file()


def test_h_quality_runtime_uses_the_active_user_setting():
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    handler = function_body(screen, r"maica_handle_quality_status")
    assert re.search(r"\bmaica_instance\.gen_quality_chk\b", handler)
    assert not re.search(r"default_setting\s*\[\s*['\"]gen_quality_chk['\"]\s*\]", handler)


def test_h_quality_status_is_not_registered_or_uploaded_as_a_trigger():
    trigger = source("game/Submods/MAICA_ChatSubmod/trigger.rpy")
    tasker = source("game/python-packages/maica_tasker_sub.py")
    assert "dscl_trigger" not in trigger
    assert "mtrigger_dscl" not in trigger
    assert not re.search(r"_trigger_func\s*\(\s*['\"]dscl['\"]", tasker)


def test_h_quality_status_has_a_separate_listener_and_post_response_consumer():
    runtime = source("game/python-packages/maica.py")
    main = source("game/Submods/MAICA_ChatSubmod/main.rpy")
    assert re.search(
        r"QualityStatusTasker\s*=\s*maica_tasker_sub\.QualityStatusWsHandler",
        runtime,
    )
    trigger_run = main.index("ai.mtrigger_manager.run_trigger")
    quality_consume = main.index("ai.consume_quality_statuses")
    stop_check = main.index("if store.action['stop']")
    assert trigger_run < quality_consume < stop_check


def test_h_quality_ui_never_runs_display_calls_in_a_background_thread():
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    labels = source("game/Submods/MAICA_ChatSubmod/trigger_labels.rpy")
    assert "invoke_in_thread" not in screen + labels
    assert "timer 5.0 action Function(maica_hide_quality_chibi)" in screen


def test_h_legacy_quality_receiver_status_is_removed_by_latest_migration():
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    migration = source("game/Submods/MAICA_ChatSubmod/migrations.rpy")
    migration_body = function_body(migration, r"migration_1_8_0")
    assert "maica_mtrigger_status.pop" not in api
    assert re.search(
        r"maica_mtrigger_status\.pop\s*\(\s*['\"]dscl['\"]\s*,\s*None\s*\)",
        migration_body,
    )
    assert re.search(
        r"mtrigger_manager\.enable_map\.pop\s*\(\s*['\"]dscl['\"]\s*,\s*None\s*\)",
        migration_body,
    )


def test_h_internal_quality_key_is_not_registered_as_an_english_translation():
    for path in (SUBMOD / "tl").rglob("*.rpy"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r'^\s*old\s+"gen_quality_chk"\s*$', text, re.M), str(path.relative_to(ROOT))


def test_retired_setting_identifiers_are_not_runtime_owners():
    paths = [path for path in SUBMOD.rglob("*.rpy") if path.name != "migrations.rpy"]
    paths += [path for path in PYTHON.glob("*.py") if not path.name.startswith("test_")]
    found = {}
    for path in paths:
        text = path.read_text(encoding="utf-8")
        hits = python_owner_names(text, str(path.relative_to(ROOT))) if path.suffix == ".py" else rpy_owner_names(text)
        if hits:
            found[str(path.relative_to(ROOT))] = sorted(hits)
    assert not found, "retired runtime setting identifiers remain: {}".format(found)


def test_retired_owner_scanners_ignore_prose_and_detect_real_subscripts():
    note = 'note = "hello \\" sfe_aggressive = documentation only"\n'
    owner = 'data["sfe_aggressive"] = value\n'
    compat = 'whatever_name = {"sfe_aggressive": "prompt_pname_repl"}\n'
    assert "sfe_aggressive" not in python_owner_names(note)
    assert "sfe_aggressive" in python_owner_names(owner)
    assert "sfe_aggressive" in python_owner_names(compat)
    assert "sfe_aggressive" not in rpy_owner_names(note)
    assert "sfe_aggressive" in rpy_owner_names(owner)
    assert "sfe_aggressive" in rpy_owner_names(compat)


def test_retired_python_scanner_rejects_unparseable_input():
    broken = 'note = """unterminated sfe_aggressive documentation'
    with pytest.raises(AssertionError, match=r"AST:.*tokenize:.*input:"):
        python_owner_names(broken, "unterminated synthetic fixture")


def test_retired_rpy_scanner_does_not_exempt_mixed_compatibility_dicts():
    pure = 'anything = {"sfe_aggressive": "prompt_pname_repl"}'
    mixed = 'anything = {"sfe_aggressive": "prompt_pname_repl", "other": value}'
    expanded = 'anything = {"sfe_aggressive": "prompt_pname_repl", **extra}'
    assert "sfe_aggressive" in rpy_owner_names(pure)
    assert "sfe_aggressive" in rpy_owner_names(mixed)
    assert "sfe_aggressive" in rpy_owner_names(expanded)


def compatibility_map_text():
    return ", ".join('"{}": "{}"'.format(old, new) for old, new in RENAMES.items())


def test_retired_owner_scanners_only_exempt_the_complete_unique_rename_map():
    complete = "anything = {" + compatibility_map_text() + "}\n"
    duplicate = complete[:-2] + ', "sfe_aggressive": "prompt_pname_repl"}\n'
    extra = complete[:-2] + ', "other": "value"}\n'
    subset = 'anything = {"sfe_aggressive": "prompt_pname_repl"}\n'
    for scanner in (python_owner_names, rpy_owner_names):
        assert not scanner(complete)
        assert "sfe_aggressive" in scanner(duplicate)
        assert "sfe_aggressive" in scanner(extra)
        assert "sfe_aggressive" in scanner(subset)


def test_retired_rpy_scanner_tracks_escaped_members_with_linear_visits():
    complete = compatibility_map_text()
    repeated = (
        'anything = {' + complete + '}\n'
        'data["sfe_aggressive"] = "quoted \\\"sfe_aggressive\\\" text"\n'
    )
    large = "anything = {" + complete + "}\n"
    deep = 'data = ' + '{"nested": ' * 2000 + '{' + complete + '}' + '}' * 2000 + '\n'
    stats = {}
    assert "sfe_aggressive" in rpy_owner_names(repeated)
    assert "sfe_aggressive" not in rpy_owner_names(large)
    assert "sfe_aggressive" not in rpy_owner_names(deep, stats=stats)
    assert stats["visits"] <= stats["tokens"] * 3


def test_retired_ws_protocol_identifiers_are_not_registered():
    paths = list(PYTHON.glob("*.py")) + list(SUBMOD.glob("*.rpy"))
    retired = ("maica_core_nostream_reply", "maica_dscl_status", "maica_loop_warn_finished")
    found = {}
    for path in paths:
        identifiers = strip_comments_and_strings(path.read_text(encoding="utf-8"), path.suffix)
        hits = [name for name in retired if re.search(r"\b{}\b".format(name), identifiers)]
        if hits:
            found[str(path.relative_to(ROOT))] = hits
    assert not found, "retired websocket identifiers remain: {}".format(found)


def test_persistent_filter_is_valid_json():
    assert isinstance(json.loads(source("game/Submods/MAICA_ChatSubmod/persistent_filter.json")), (list, dict))
