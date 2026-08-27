"""Collectable static contracts for the backend-v1.3 release cut-over."""

import ast
import builtins
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
ADVANCED_SETTING_KEYS = (
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
    "memory_concl_arc",
    "nsfw_acceptive",
    "mf_context_rnds",
    "mt_context_rnds",
    "mf_disable_loop",
    "mt_disable_loop",
    "gen_enforce_lang",
)


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


def is_python2_string_prefix_error(error):
    """Identify Python 3.14 rejecting Python 2's ``ur`` string prefix."""
    return "prefixes are incompatible" in str(error)


def strip_comments_and_strings(text, suffix):
    """Leave identifiers/operators while eliminating prose false positives."""
    if suffix == ".py":
        try:
            tokens = tokenize.generate_tokens(io.StringIO(text).readline)
            return tokenize.untokenize(
                (kind, "" if kind in (tokenize.COMMENT, tokenize.STRING) else value)
                for kind, value, _start, _end, _line in tokens
            )
        except (tokenize.TokenError, IndentationError, SyntaxError) as error:
            if not is_python2_string_prefix_error(error):
                raise
            return " ".join(value for kind, value in lex_source(text) if kind != "STRING")
    return " ".join(value for kind, value in lex_source(text) if kind != "STRING")


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
            if is_python2_string_prefix_error(tokenize_error):
                try:
                    return rpy_owner_names(text)
                except AssertionError as lexer_error:
                    snippet = text[:120].replace("\n", "\\n")
                    raise AssertionError(
                        "could not parse {} (AST: {}; tokenize: {}; fallback: {}; input: {!r})".format(
                            context, ast_error, tokenize_error, lexer_error, snippet
                        )
                    )
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
    range_control = re.search(r"use\s+num_bar\s*\(\s*['\"]{}['\"][^\n]*".format(key), text)
    assert range_control, "no numeric UI control found for {}".format(key)
    assert re.search(
        r"\b0\s*,\s*{}\b|(?:max|upper|maximum)\s*=\s*{}\b".format(upper, upper),
        range_control.group(0),
    )
    context = block_after(text, r"textbutton[^\n]*['\"]{}['\"]".format(key), 500)
    assert not re.search(
        r"ToggleDict\s*\(\s*persistent\.maica_advanced_setting\s*,\s*['\"]{}['\"]".format(key),
        context,
    )


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


def test_a_frontend_version_declaration_is_authoritative():
    client = source("game/python-packages/maica.py")
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")

    assert "SUPPORT_BACKEND" not in client
    assert "legc_version" not in client
    assert not re.search(r"\bis_outdated\b", client + api + header)
    assert re.search(r"def\s+is_frontend_version_outdated\(version_info=None\)", api)
    assert 'get("fe_blessland_version")' in api
    assert "maica_version_parts(store.maica_ver)" in api
    assert "maica_version_parts(min_version)" in api
    assert "compare_maica_versions(" in api
    validate = function_body(api, "validate_version")
    assert "maica_version_parts(libv)" in validate
    assert "maica_version_parts(uiv)" in validate
    assert "if accessible and is_frontend_version_outdated():" in api
    assert "elif maica.is_frontend_version_outdated():" in header


def test_rss_setup_is_deferred_to_optional_update_initialization():
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    early_init = api.split("default persistent._maica_updatelog_version_seen", 1)[0]
    update_init = api.split("init 5 python in maica:", 1)[1].split("\ninit ", 1)[0]

    assert "maica_rss_provider" not in early_init
    assert "except:\n        pass" not in early_init
    assert "maica_rss_provider.set_ua(store.maica_ver)" in update_init
    assert "except Exception as e:" in update_init
    assert update_init.index("    import bot_interface") < update_init.index("    try:")


def test_a_frontend_version_comparison_uses_numeric_segments():
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    init_block = api.split("init 5 python in maica:", 1)[1].split("\ninit ", 1)[0]
    python_source = "\n".join(
        line[4:] if line.startswith("    ") else line
        for line in init_block.splitlines()
    )
    tree = ast.parse(python_source)
    helper_names = {
        "_maica_is_version_sequence",
        "_maica_is_version_dict",
        "maica_version_parts",
        "compare_maica_versions",
        "is_frontend_version_outdated",
    }
    functions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name in helper_names
    ]
    assert {node.name for node in functions} == helper_names

    class StoreStub(object):
        maica_ver = "1.8.11"

    namespace = {
        "store": StoreStub(),
        "_maica_version_builtin_types": builtins,
    }
    module = ast.Module(body=functions, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, "api.rpy", "exec"), namespace)

    assert namespace["maica_version_parts"](" 1.8.11\n") == [1, 8, 11]
    assert namespace["maica_version_parts"](("1", 8, "11")) == [1, 8, 11]
    assert namespace["maica_version_parts"]("1.8.x") is None
    assert namespace["compare_maica_versions"]([1, 8], [1, 8, 0]) == 0
    assert namespace["is_frontend_version_outdated"]({
        "success": True,
        "content": {"fe_blessland_version": "1.8.5"},
    }) is False
    assert namespace["is_frontend_version_outdated"]({
        "success": True,
        "content": {"fe_blessland_version": "1.8.12"},
    }) is True
    assert namespace["is_frontend_version_outdated"]({
        "success": True,
        "content": {"fe_blessland_version": "1.8.11.0"},
    }) is False
    assert namespace["is_frontend_version_outdated"]({
        "success": True,
        "content": {"fe_blessland_version": "invalid"},
    }) is False
    assert namespace["is_frontend_version_outdated"]({
        "success": True,
        "content": [],
    }) is False


def test_a_settings_connection_preserves_the_submods_screen_without_label_kwargs():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    pane = named_screen(
        header,
        "maica_setting_pane",
    )
    assert re.search(
        r"Function\(\s*_maica_connect_from_settings_once\s*\)",
        pane,
    )
    assert "_clear_layers" not in pane
    assert "connection_busy = ai.is_connecting()" in pane
    assert "availability_busy = ai.is_checking_availability()" in pane
    assert "MaicaAiStatus.WAIT_AVAILABILITY" in pane
    assert "get_provider_refresh_error()" in pane
    assert "Provider list refresh failed" in pane
    assert "maica.maica_instance.is_connecting()" in pane
    assert "MaicaAiStatus.is_submod_exception" in pane
    assert "MaicaAiStatus.CERTIFI_BROKEN" in pane
    assert "13400 <=" not in pane
    assert re.search(
        r"has_token\(\).*?is_accessable\(\).*?not\s+"
        r"maica\.maica_instance\.is_connected\(\)",
        pane,
        re.S,
    )

    helper = function_body(
        header,
        r"_maica_call_in_new_context_preserve_layers",
    )
    assert "version >= (8, 3)" in helper
    assert "(7, 8) <= version < (8, 0)" in helper
    assert "renpy.call_in_new_context(label, _clear_layers=False)" in helper
    assert "renpy.call_in_new_context(label, *args, **call_kwargs)" in helper
    assert re.search(
        r"renpy\.execution\.Context\(\s*False\s*,\s*contexts\[-1\]\s*,\s*"
        r"clear\s*=\s*False\s*\)",
        helper,
    )
    assert "renpy.store._args = args or None" in helper
    assert "renpy.store._kwargs = None" in helper

    guarded_entry = function_body(
        header,
        r"_maica_connect_from_settings_once",
    )
    assert "_maica_settings_connect_context_active" in guarded_entry
    assert "not ai.is_accessable()" in guarded_entry
    assert "not ai.has_token()" in guarded_entry
    assert "ai.is_connected()" in guarded_entry
    assert "ai.is_connecting()" in guarded_entry
    assert "\"maica_connect_from_settings\"" in guarded_entry
    assert "finally:" in guarded_entry


def test_a_connection_entrypoints_wait_for_shutdown_and_block_mutation():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    main = source("game/Submods/MAICA_ChatSubmod/main.rpy")
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    screens = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    client = source("game/python-packages/maica.py")

    provider_sync = function_body(header, r"sync_provider_id")
    assert re.search(r"if\s+reconnect:\s*ai\.close_wss_session\(\)", provider_sync)
    assert "ai.disable()" in provider_sync
    assert "WAIT_AVAILABILITY" not in provider_sync
    assert "ai.status" not in provider_sync
    assert "ai.wait_for_connection_shutdown(6.0)" in provider_sync
    assert "ai.multi_lock" not in provider_sync
    assert "provider_manager.get_provider()" not in provider_sync
    assert provider_sync.count("store.maica.check_accessibility()") == 1
    assert "availability_ready = store.maica.check_accessibility()" in provider_sync

    provider_screen = named_screen(screens, "maica_node_setting")
    assert "provider_manager.get_provider" not in provider_screen
    assert "refresh_provider_list" in provider_screen
    assert "maica_start_provider_task" in provider_screen
    assert "is_provider_refreshing()" in provider_screen

    provider_task = function_body(header, r"maica_start_provider_task")
    assert "renpy.invoke_in_thread(task)" in provider_task
    assert "is_provider_refreshing()" in provider_task
    assert "is_checking_availability()" in provider_task

    assert "self._availability_check_lock = threading.Lock()" in client
    accessibility = function_body(client, r"accessable")
    assert "_availability_check_lock" in accessibility
    assert "finally:" in accessibility

    token_change = function_body(api, r"change_token")
    assert re.search(
        r"is_connected\(\)\s+or\s+store\.maica\.maica_instance\.is_connecting\(\)",
        token_change,
    )

    connect_label = main.split(
        "label maica_init_connect", 1
    )[1].split("\nlabel maica_connect_from_settings", 1)[0]
    assert connect_label.index("ai.init_connect()") < connect_label.index(
        "renpy.pause(2.3)"
    )
    assert re.search(
        r"not ai\.is_connected\(\) and not ai\.is_connecting\(\):\s*"
        r"ai\.init_connect\(\)",
        connect_label,
    )


def test_a_certificate_repair_and_version_disable_are_sticky():
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    repair = function_body(api, r"maica_download_certifi_files")
    startup = function_body(api, r"start_maica")
    version_guard = function_body(api, r"check_accessibility")
    provider_refresh = function_body(api, r"refresh_provider_list")

    assert "13408" not in api
    assert repair.count("CERTIFI_RESTART_REQUIRED") == 1
    assert re.search(
        r"disable\(\s*.*?CERTIFI_RESTART_REQUIRED\s*,\s*sticky\s*=\s*True",
        repair,
        re.S,
    )
    assert "check_accessibility()" in startup
    assert re.search(
        r"disable\(\s*.*?VERSION_OLD\s*,\s*sticky\s*=\s*True",
        version_guard,
        re.S,
    )
    assert "instance.refresh_provider_list()" in provider_refresh
    assert re.search(
        r"disable\(\s*.*?VERSION_OLD\s*,\s*sticky\s*=\s*True",
        provider_refresh,
        re.S,
    )


def test_a_development_build_contract():
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    translation = source("game/Submods/MAICA_ChatSubmod/tl/header.rpy")
    workflow = source(".github/workflows/release.yml")

    assert re.search(r"force_current\s*=\s*store\.maica_is_dev", api)
    assert "if store.maica_is_dev:" in header
    assert "development build" in header
    assert "开发版本" in translation
    assert "steps.get_version.outputs.is_development == 'false'" in workflow
    assert "steps.get_version.outputs.is_development == 'true'" in workflow


def test_a_migration_is_structurally_registered_and_invoked():
    migration = source("game/Submods/MAICA_ChatSubmod/migrations.rpy")
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    queue = block_after(migration, r"migration_queue\s*=", 1000)
    assert re.search(r"\(\s*['\"]1\.8\.0['\"]\s*,\s*migration_1_8_0\s*\)", queue)
    assert re.search(r"\bmaica_migration\s*\(", api) or re.search(r"\bmigrations\.migration_instance\s*\(", api)
    assert re.search(r"persistent\._maica_last_version\s*=\s*store\.maica_ver", api)


def test_a_maica_namespace_qualifies_android_host_path():
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    maica_block = api.split("init 5 python in maica:", 1)[1].split("\ninit ", 1)[0]

    assert "store.ANDROID_MASBASE" in maica_block
    assert not re.search(r"(?<![A-Za-z0-9_.])ANDROID_MASBASE\b", maica_block)


def test_a_legacy_migration_does_not_index_retired_history_key():
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    migration = function_body(api, r"migration_1_2_0")

    assert "maica_reset_setting()" in migration
    assert "max_history_token" not in migration


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


def test_b_connection_recovery_defaults_are_enabled_without_overwriting_saved_values():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    persistent_defaults = literal_dict(header, "persistent.maica_setting_dict")
    canonical_defaults = block_after(header, r"maica_default_dict\s*=", 250)

    for key in ("auto_reconnect", "auto_resume"):
        assert persistent_defaults[key] is True
        assert re.search(
            r"['\"]{}['\"]\s*:\s*True".format(key),
            canonical_defaults,
        )

    assert "maica_default_dict.update(persistent.maica_setting_dict)" in header


@pytest.mark.parametrize("new", PERSISTENT_SETTINGS)
def test_b_canonical_ui_owner_exists(new):
    ui = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    ui += "\n".join(screen_blocks(source("game/Submods/MAICA_ChatSubmod/header.rpy")))
    assert ui_owner_exists(ui, new), "UI owner missing: {}".format(new)


@pytest.mark.parametrize("new", PERSISTENT_SETTINGS)
def test_b_canonical_runtime_upload_owner_exists(new):
    runtime = source("game/python-packages/maica.py")
    if new in ADVANCED_SETTING_KEYS:
        allowlist = literal_assignment(
            source("game/python-packages/maica_v13_migration.py"),
            "ADVANCED_SETTING_KEYS",
        )
        assert new in allowlist
        assert "filter_advanced_settings(self.modelconfig)" in runtime
    else:
        runtime += source("game/python-packages/maica_tasker_sub_sessionsender.py")
        assert runtime_owner_exists(runtime, new), "runtime owner missing: {}".format(new)


def test_b_advanced_setting_allowlist_matches_the_supported_ui_contract():
    allowlist = literal_assignment(
        source("game/python-packages/maica_v13_migration.py"),
        "ADVANCED_SETTING_KEYS",
    )
    assert allowlist == ADVANCED_SETTING_KEYS


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
    timezone_default = function_body(header, r"maica_get_language_default_timezone")
    refresh_automatic = function_body(header, r"maica_refresh_automatic_settings")
    assert re.search(r"['\"]chinese['\"]\s*:\s*['\"]zh['\"]", target_default)
    assert re.search(r"['\"]english['\"]\s*:\s*['\"]en['\"]", target_default)
    assert re.search(r"\.get\s*\([^,]+,\s*['\"]auto['\"]\s*\)", target_default)
    assert 'if target_lang == "zh"' in timezone_default
    assert 'return "Asia/Shanghai"' in timezone_default
    assert 'return "America/Indiana/Vincennes"' in timezone_default
    assert re.search(r"['\"]target_lang['\"]\s*:\s*maica_get_default_target_lang\s*\(\s*\)", header)
    assert re.search(r"['\"]tz['\"]\s*:\s*maica_get_system_timezone\s*\(\s*\)", header)
    assert 'persistent._maica_target_lang_mode == "renpy"' in refresh_automatic
    assert 'persistent._maica_tz_mode == "system"' in refresh_automatic
    assert 'persistent._maica_tz_mode == "language"' in refresh_automatic
    assert "current_tz = store.maica_get_system_timezone()" in screen
    assert "language_tz = store.maica_get_language_default_timezone(" in screen


def test_c_language_and_timezone_selectors_use_explicit_two_level_highlights():
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    language = named_screen(screen, "maica_select_language")
    timezone = named_screen(screen, "maica_tz_setting")

    assert 'use maica_setter_medium_frame(' in language
    assert language.count("use divider_plain_small()") == 1
    assert timezone.count("use divider_plain_small()") == 1
    assert 'style_prefix "maica_check"' not in language
    assert 'style_prefix "maica_check"' not in timezone

    assert 'selected persistent._maica_target_lang_mode == "renpy"' in language
    assert language.count("selected current_target_lang ==") == 3
    assert 'selected persistent._maica_tz_mode == "language"' in timezone
    assert 'selected persistent._maica_tz_mode == "system"' in timezone
    assert "selected selected_tz == timezone_dict[item]" in timezone

    assert "SetField(persistent, \"_maica_target_lang_mode\"" not in language
    assert "SetField(persistent, \"_maica_tz_mode\"" not in timezone


def test_c_automatic_language_and_timezone_modes_sync_and_roll_back():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    target_select = function_body(header, r"maica_select_target_lang")
    timezone_select = function_body(header, r"maica_select_timezone")
    reset = function_body(header, r"maica_reset_setting")
    discard = function_body(header, r"maica_discard_setting")
    apply_setting = function_body(header, r"maica_apply_setting")
    setting_screen = named_screen(header, "maica_setting")

    assert 'persistent.maica_setting_dict["target_lang"] = target_lang' in target_select
    assert "persistent._maica_target_lang_mode = mode" in target_select
    assert 'persistent._maica_tz_mode == "language"' in target_select
    assert "maica_get_language_default_timezone(target_lang)" in target_select
    assert 'persistent.maica_setting_dict["tz"] = timezone' in timezone_select
    assert "persistent._maica_tz_mode = mode" in timezone_select

    assert 'persistent._maica_target_lang_mode = "renpy"' in reset
    assert 'persistent._maica_tz_mode = "system"' in reset
    assert "maica_refresh_automatic_settings(persistent.maica_setting_dict)" in reset
    assert "maica_refresh_automatic_settings(persistent.maica_setting_dict)" in apply_setting

    assert "persistent._maica_target_lang_mode = target_lang_mode" in discard
    assert "persistent._maica_tz_mode = tz_mode" in discard
    assert "default target_lang_mode_before_edit" in setting_screen
    assert "default tz_mode_before_edit" in setting_screen
    assert re.search(
        r"Function\s*\(\s*store\.maica_discard_setting\s*,\s*"
        r"target_lang_mode_before_edit\s*,\s*tz_mode_before_edit",
        setting_screen,
    )


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
    (("mf_sf_access_impl", 1), ("mf_const_sf_access", 0), ("memory_concl_arc", 1)),
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
    assert re.search(r'^\s*old\s+"Max length each session will preserve, in range of 512-28672\.', translation, re.M)
    assert re.search(r'^\s*new\s+"会话保留的最大长度\. 范围512-28672\.', translation, re.M)


@pytest.mark.parametrize("relative", ("game/python-packages/maica.py", "game/python-packages/maica_tasker_sub_sessionsender.py"))
def test_c_each_outbound_builder_retires_mt_extraction(relative):
    assert not re.search(r"['\"]mt_extraction['\"]\s*:", source(relative)), relative


def test_c_persistent_exports_retire_mas_sf_hcb():
    assert "mas_sf_hcb" not in source("game/python-packages/maica_savefile.py")


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
    expected = ADVANCED_SETTING_KEYS
    positions = [ui.index('textbutton "{}'.format(name)) for name in expected]
    assert positions == sorted(positions)
    assert "twk_super" not in ui


def test_e_advanced_setting_screen_supports_discard_and_independent_local_switches():
    screen = named_screen(
        source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy"),
        "maica_advance_setting",
    )
    assert "Function(store.maica_discard_advanced_setting)" in screen
    assert "MAICA: Advanced setting changes discarded" in screen
    translation = source("game/Submods/MAICA_ChatSubmod/tl/screen_subs.rpy")
    assert 'old "MAICA: Advanced setting changes discarded"' in translation
    assert 'new "MAICA: 已放弃高级设置修改"' in translation
    for key in ("mf_sf_access_impl", "mf_const_sf_access", "mf_const_tools", "memory_concl_arc"):
        assert re.search(
            r"ToggleDict\s*\(\s*persistent\.maica_advanced_setting_status\s*,\s*['\"]{}['\"]".format(key),
            screen,
        )
        assert not re.search(
            r"SetDict\s*\(\s*persistent\.maica_advanced_setting_status\s*,\s*['\"]{}['\"]\s*,\s*True".format(key),
            screen,
        )


def test_e_advanced_setting_apply_replaces_the_runtime_snapshot():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    apply_body = function_body(header, r"maica_apply_advanced_setting")
    assert "filter_advanced_settings" in apply_body
    assert re.search(r"modelconfig\s*=\s*settings_dict", apply_body)
    assert not re.search(r"modelconfig\.update\s*\(", apply_body)


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
        r"MTriggerBase\(\s*memory_writeback_template\s*,\s*['\"]write_memory['\"]",
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
    memory_callback = function_body(trigger, r"mtrigger_write_memory_callback")
    assert memory_callback.count("store._upload_persistent_dict()") == 1
    assert memory_callback.index("mas_player_additions.append(addition)") < memory_callback.index(
        "store._upload_persistent_dict()"
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
    assert "bot_interface.escape_renpy_text(text)" in escape_helper

    addition_screen = named_screen(screen, "maica_addition_setting")
    assert re.search(r"textbutton\s+maica_escape_display_text\s*\(\s*item\s*\)", addition_screen)

    delete_label = block_after(chat, r"label\s+maica_delete_information", 900)
    assert re.search(
        r"items\.append\s*\(\s*\[\s*maica_escape_display_text\s*\(\s*i\s*\)\s*,\s*i\s*,",
        delete_label,
        re.S,
    )


def test_e_dynamic_error_and_external_fields_use_display_escape_boundaries():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    templates = source("game/Submods/MAICA_ChatSubmod/screen_templates.rpy")

    location_screen = named_screen(screen, "maica_location_input")
    provider_screen = named_screen(screen, "maica_node_setting")
    log_screen = named_screen(screen, "maica_log")
    message_screen = templates

    assert "res.get(\"exception\")" in location_screen
    assert 'renpy.show_screen("maica_message"' in location_screen
    assert "screen maica_message" in message_screen
    assert "label maica_escape_display_text(_(message))" in message_screen
    assert "maica_escape_display_text(maica_log.get(\"title\"))" in log_screen
    assert "maica_escape_display_text(content)" in log_screen
    for field in ("name", "description", "servingModel", "portalPage"):
        assert re.search(
            r"maica_escape_display_text\(\s*provider\.get\(\s*['\"]{}['\"]".format(field),
            provider_screen,
        )

    token_helper = function_body(header, r"_maica_verify_token")
    assert "maica_escape_display_text(detail)" not in token_helper


def test_e_chat_and_mpostal_escape_only_at_renpy_display_edges():
    main = source("game/Submods/MAICA_ChatSubmod/main.rpy")
    raw = source("game/Submods/MAICA_ChatSubmod/raw_session_example.rpy")
    runtime = source("game/python-packages/maica.py")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")

    assert "ai.prepare_message_for_renpy(message[1])" in main
    assert "ai.prepare_message_for_renpy(message[1])" in raw
    assert "def prepare_message_for_renpy" in runtime
    assert "RENPY_DIALOGUE_SUBSTITUTIONS" in runtime
    assert 'cur_postal["responsed_content"] = message[1]' in main
    assert "maica_escape_dialogue_text(content, interpolation_passes=2)" in main
    assert "maica_build_display_preview" in screen
    assert "preview_text.count" not in screen


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


def test_e_editable_list_items_expand_for_wrapped_text():
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")

    for name in ("maica_addition_setting", "maica_mspire_category_setting"):
        setting_screen = named_screen(screen, name)
        assert re.search(
            r"textbutton\s+maica_escape_display_text\s*\(\s*item\s*\)\s*:\s*"
            r"yminimum\s+36\s*ymaximum\s+None",
            setting_screen,
        )


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
    control = block_after(ui, r"(?m)^\s*textbutton[^\n]*prompt_allow_nickname", 1000)
    assert re.search(
        r"action[^\n]*(?:ToggleDict|SetDict)\s*\(\s*persistent\.maica_advanced_setting\s*,\s*['\"]prompt_allow_nickname['\"]",
        control,
    )
    assert re.search(r"persistent\.maica_advanced_setting(?:_status)?[^\n]*['\"]prompt_allow_nickname['\"]", control)


def test_f_legality_response_displays_distinct_latitude_and_longitude():
    client = source("game/python-packages/maica.py")
    extractor = function_body(client, r"extract_legality_coordinates")
    screen_source = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    location_screen = named_screen(screen_source, "maica_location_input")
    translation = source("game/Submods/MAICA_ChatSubmod/tl/screen_subs.rpy")

    assert 'get("latitude")' in extractor
    assert 'get("longitude")' in extractor
    for retired_key in ('get("lat"', 'get("lng"', 'get("lon"'):
        assert retired_key not in extractor

    assert "extract_legality_coordinates" in location_screen
    assert re.search(
        r"format\s*\(\s*latitude\s*,\s*longitude\s*\)",
        location_screen,
    )
    assert "geocode" not in location_screen.lower()
    assert 'old "Location geocode: "' not in translation


def test_g_header_shared_additions_helper_uses_the_backend_limits():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    helper = function_body(header, r"_?maica_\w*addition\w*")
    contract = source("game/python-packages/maica_savefile.py")

    assert "maica_savefile.PLAYER_ADDITIONS_MAX_ITEMS" in helper
    assert "maica_savefile.validate_player_addition_item" in helper
    assert literal_assignment(contract, "PLAYER_ADDITIONS_MAX_ITEMS") == 512
    assert literal_assignment(contract, "PLAYER_ADDITION_MAX_BYTES") == 1536


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


def test_g_persistent_upload_uses_the_field_specific_sanitizer():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    upload = function_body(header, r"_upload_persistent_dict")

    assert "maica_savefile.sanitize_persistent_dict(d)" in upload
    assert "REMOVED|TOO_LONG" not in upload
    assert upload.index("sanitize_persistent_dict") < upload.index("upload_save(d)")
    invalid_branch = block_after(
        upload,
        r"except\s+maica_savefile\.PlayerAdditionsValidationError",
        500,
    )
    assert re.search(r"\breturn\b", invalid_branch)


def test_g_persistent_upload_includes_the_effective_target_language():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    upload = function_body(header, r"_upload_persistent_dict")
    upload_keys = literal_assignment(
        source("game/python-packages/maica_savefile.py"),
        "PERSISTENT_UPLOAD_KEYS",
    )

    assert re.search(
        r"d\[['\"]target_lang['\"]\]\s*=\s*"
        r"store\.maica\.maica_instance\.target_lang",
        upload,
    )
    assert "target_lang" in upload_keys
    assert "maica_savefile.sanitize_persistent_dict(d)" in upload


def test_g_v18_migration_runs_before_persistent_upload():
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    migration_body = function_body(api, r"maica_migration")
    assert "cleanup_advanced_settings" in migration_body
    assert "store.maica_apply_advanced_setting()" in migration_body
    assert re.search(r"modelconfig\s*=\s*\{\s*\}", migration_body)

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
    assert "mtrigger_manager.run_trigger()" in main
    trigger_run = main.index("call maica_run_mtriggers")
    quality_consume = main.index("ai.consume_quality_statuses")
    stop_check = main.index("if store.action['stop']")
    assert trigger_run < quality_consume < stop_check


def test_h_quality_ui_never_runs_display_calls_in_a_background_thread():
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    labels = source("game/Submods/MAICA_ChatSubmod/trigger_labels.rpy")
    assert "invoke_in_thread" not in screen + labels
    assert "timer 5.0 action Function(maica_hide_quality_chibi)" in screen


def test_h_quality_ui_scopes_chibi_transitions_to_master_layer():
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    hide_body = function_body(screen, r"maica_hide_quality_chibi")
    show_body = function_body(screen, r"maica_handle_quality_status")

    assert re.search(r"renpy\.hide\(\s*['\"]chibi_peek['\"]\s*\)", hide_body)
    assert re.search(
        r"renpy\.transition\(\s*moveoutleft\s*,\s*layer\s*=\s*['\"]master['\"]\s*\)",
        hide_body,
    )
    assert "transition=" not in hide_body
    assert "transition=" not in show_body
    assert "transform=" not in show_body
    assert re.search(
        r"renpy\.transition\(\s*moveinleft\s*,\s*layer\s*=\s*['\"]master['\"]\s*\)",
        show_body,
    )


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


def test_python2_ur_literals_fall_back_when_tokenizer_rejects_prefix(monkeypatch):
    text = (
        "note = ur'maica_dscl_status and sfe_aggressive are prose'\n"
        "data[ur'sfe_aggressive'] = value\n"
        "maica_core_nostream_reply = value\n"
    )

    def reject_python2_prefix(_readline):
        yield from ()
        raise tokenize.TokenError("'u' and 'r' prefixes are incompatible", (1, 10))

    monkeypatch.setattr(tokenize, "generate_tokens", reject_python2_prefix)

    assert python_owner_names(text) == {"sfe_aggressive"}
    identifiers = strip_comments_and_strings(text, ".py")
    assert "maica_dscl_status" not in identifiers
    assert "maica_core_nostream_reply" in identifiers


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


def test_persistent_upload_filter_has_one_unique_owner():
    upload_keys = literal_assignment(
        source("game/python-packages/maica_savefile.py"),
        "PERSISTENT_UPLOAD_KEYS",
    )

    assert len(upload_keys) == len(set(upload_keys))
    assert not (SUBMOD / "persistent_filter.json").exists()
    assert not re.search(
        r"(?m)^persistent_filter\s*=",
        source("game/python-packages/json_exporter.py"),
    )
