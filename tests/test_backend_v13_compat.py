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
    "ic_prep": "twk_super",
}


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


def remove_compatibility_dicts(text):
    """Remove any pure old-to-canonical dictionary literal, regardless of name."""
    ranges = []
    for start, char in enumerate(text):
        if char != "{":
            continue
        depth = 0
        for index in range(start, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        value = ast.literal_eval(text[start:index + 1])
                    except (SyntaxError, ValueError, TypeError, RecursionError, OverflowError):
                        break
                    if (isinstance(value, dict) and value and
                            all(key in RENAMES and RENAMES[key] == item for key, item in value.items())):
                        ranges.append((start, index + 1))
                    break
    for start, end in reversed(ranges):
        text = text[:start] + text[end:]
    return text


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


def ui_owner_exists(text, key):
    for screen in screen_blocks(text):
        for control in re.findall(r"(?ms)^\s*(?:textbutton|use\s+\w+)[^\n]*.*?(?=^\s*(?:textbutton|use\s+\w+|if|elif|else)\b|\Z)", screen):
            if key not in control:
                continue
            if re.search(r"\baction\b[^\n]*(?:SetDict|ToggleDict|Function|SetField)[^\n]*['\"]{}['\"]".format(key), control):
                return True
    return False


def runtime_owner_exists(text, key):
    for match in re.finditer(r"(?m)^\s*def\s+(\w+)\s*\(", text):
        body = function_body(text[match.start():], re.escape(match.group(1)))
        if not re.search(r"\b(?:chat_params|modelconfig|settings_dict|request_body|payload|data)\b", body):
            continue
        if re.search(r"(?:['\"]{}['\"]\s*:|\[['\"]{}['\"]\]|\.{}\b)".format(key, key, key), body):
            return True
    return False


def python_owner_names(text):
    text = remove_compatibility_dicts(text)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(text)
    except (SyntaxError, ValueError, TypeError):
        try:
            tokens = [token for token in tokenize.generate_tokens(io.StringIO(text).readline)
                      if token.type not in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                                            tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING)]
        except (tokenize.TokenError, IndentationError):
            return set()
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
            if pairs and len(pairs) == len(node.keys) and all(key in RENAMES and RENAMES[key] == value for key, value in pairs):
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


def rpy_owner_names(text):
    """One linear pass: discard prose strings/comments, retain structural string keys."""
    found = set()
    index = 0
    code = []
    while index < len(text):
        char = text[index]
        if char == "#":
            end = text.find("\n", index)
            index = len(text) if end < 0 else end
            continue
        if char in "'\"":
            quote = char * (3 if text.startswith(char * 3, index) else 1)
            start = index + len(quote)
            end = text.find(quote, start)
            if end < 0:
                break
            value = text[start:end]
            before = "".join(code).rstrip()[-1:] or ""
            after_index = end + len(quote)
            after = text[after_index:].lstrip()[:1]
            if value in RENAMES and (before == "[" or after in (']', ':')):
                found.add(value)
            code.append(" ")
            index = after_index
            continue
        code.append(char)
        index += 1
    bare = "".join(code)
    for old in RENAMES:
        if re.search(r"(?:\.|\b){}\b\s*(?:=|\()".format(old), bare):
            found.add(old)
    return found


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


def test_a_backend_and_release_versions_are_final():
    assert re.search(r"SUPPORT_BACKEND\s*=\s*['\"]1\.3\.000['\"]", source("game/python-packages/maica.py"))
    api = source("game/Submods/MAICA_ChatSubmod/api.rpy")
    assignments = re.findall(r"(?m)^\s*maica_ver\s*=\s*['\"]([^'\"]+)['\"]", api)
    assert assignments, "init code never assigns maica_ver"
    assert assignments[-1] == "1.8.0", "final effective maica_ver assignment is {}".format(assignments[-1])


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
    mapping = literal_dict(source("game/Submods/MAICA_ChatSubmod/migrations.rpy"), "chat_param_renames")
    assert mapping.get(old) == new, "{} must migrate to {}".format(old, new)


def test_b_migration_rename_map_has_no_unreviewed_keys():
    mapping = literal_dict(source("game/Submods/MAICA_ChatSubmod/migrations.rpy"), "chat_param_renames")
    assert set(mapping) == set(RENAMES)


@pytest.mark.parametrize("new", RENAMES.values())
def test_b_canonical_default_owner_exists(new):
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    assert re.search(r"['\"]{}['\"]\s*:".format(new), header), "default owner missing: {}".format(new)


@pytest.mark.parametrize("new", RENAMES.values())
def test_b_canonical_ui_owner_exists(new):
    ui = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    ui += "\n".join(screen_blocks(source("game/Submods/MAICA_ChatSubmod/header.rpy")))
    assert ui_owner_exists(ui, new), "UI owner missing: {}".format(new)


@pytest.mark.parametrize("new", RENAMES.values())
def test_b_canonical_runtime_upload_owner_exists(new):
    runtime = source("game/python-packages/maica.py") + source("game/python-packages/maica_tasker_sub_sessionsender.py")
    assert runtime_owner_exists(runtime, new), "runtime owner missing: {}".format(new)


def test_b_owner_helpers_reject_default_only_synthetic_source():
    defaults = 'defaults = {"prompt_pname_repl": False}'
    assert not ui_owner_exists(defaults, "prompt_pname_repl")
    assert not runtime_owner_exists(defaults, "prompt_pname_repl")


def test_c_regular_settings_include_tz_and_auto_language_defaults():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    assert_key_default(header, "tz", r"(?:None|['\"][^'\"]+['\"])")
    assert_key_default(header, "target_lang", r"['\"]auto['\"]")


def test_c_tz_has_ui_and_outbound_owners():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    assert "maica_tz_setting" in screen and re.search(r"maica_setting_dict[^\n]*['\"]tz['\"]", screen)
    assert re.search(r"maica_setting_dict[^\n]*['\"]tz['\"]", header)


@pytest.mark.parametrize("key", ("mf_sf_access_impl", "mf_const_sf_access", "mt_concl_memory"))
def test_c_tristate_default_and_control_are_integer_zero_to_two(key):
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    assert_key_default(header, key, r"1\b")
    assert_key_control(screen, key, 2)


def test_c_tool_and_session_limits_are_two_and_28672():
    header = source("game/Submods/MAICA_ChatSubmod/header.rpy")
    screen = source("game/Submods/MAICA_ChatSubmod/screen_subs.rpy")
    assert_key_default(header, "mt_disable_loop", r"True\b")
    assert_key_control(screen, "mf_const_tools", 2)
    session_context = block_after(header + screen, r"(?:session_len_limit|max_history_token)", 800)
    assert re.search(r"(?:session_len_limit|max_history_token).{0,500}28672", session_context, re.S)
    normalize = source("game/python-packages/maica.py") + header
    assert_key_has_semantic_upper_bound(normalize, "mf_const_tools", 2)
    session_key = "session_len_limit" if "session_len_limit" in normalize else "max_history_token"
    assert_key_has_semantic_upper_bound(normalize, session_key, 28672)


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
        assert current in runtime
    for old in ("maica_dscl_status", "maica_loop_warn_finished", "maica_core_nostream_reply"):
        assert not re.search(r"except_ws_status\s*=\s*\[[^]]*{}".format(old), runtime, re.S)


def test_e_mtrigger_mspire_mpostal_and_temporary_trigger_payloads():
    trigger = source("game/python-packages/maica_mtrigger.py")
    sender = source("game/python-packages/maica_tasker_sub_sessionsender.py")
    assert "alter_value" in trigger and "alter_affection" not in runtime_identifiers("game/python-packages/maica_mtrigger.py")
    inspire = block_after(sender, r"class\s+MAICAMSpireProcessor", 3500)
    assert re.search(r"['\"]inspire['\"]\s*:\s*\{[^}]*ctg_weight", inspire, re.S)
    assert re.search(r"['\"]inspire['\"]\s*:\s*\{[^}]*use_cache", inspire, re.S)
    assert re.search(r"['\"]inspire['\"]\s*:\s*\{\s*\}", inspire)
    postal = block_after(sender, r"class\s+MAICAMPostalProcessor", 1800)
    assert "twk_super" in postal and "ic_prep" not in runtime_identifiers("game/python-packages/maica_tasker_sub_sessionsender.py")
    assert re.search(r"['\"]triggers['\"]\s*:", sender)
    assert not re.search(r"['\"]trigger['\"]\s*:", sender)


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


@pytest.mark.parametrize("relative", ("game/Submods/MAICA_ChatSubmod/header.rpy", "game/Submods/MAICA_ChatSubmod/chat.rpy", "game/Submods/MAICA_ChatSubmod/screen_subs.rpy"))
def test_g_old_1000_character_preprocessor_is_retired(relative):
    assert not re.search(r"(?:maxlen\s*=\s*1000|\[:\s*1000\s*\]|len\s*\([^)]*\)\s*>\s*1000)", source(relative)), relative


QUALITY_FILES = (
    "game/Submods/MAICA_ChatSubmod/header.rpy",
    "game/Submods/MAICA_ChatSubmod/screen_subs.rpy",
    "game/Submods/MAICA_ChatSubmod/trigger.rpy",
    "game/Submods/MAICA_ChatSubmod/trigger_labels.rpy",
    "game/Submods/MAICA_ChatSubmod/tl/screen_subs.rpy",
    "game/Submods/MAICA_ChatSubmod/tl/trigger.rpy",
    "game/Submods/MAICA_ChatSubmod/tl/trigger_labels.rpy",
)


@pytest.mark.parametrize("relative", QUALITY_FILES)
def test_h_each_quality_runtime_and_translation_reference_is_renamed(relative):
    text = source(relative)
    assert "gen_quality_chk" in text, "new quality owner missing in {}".format(relative)
    assert "dscl_pvn" not in runtime_identifiers(relative), "old quality runtime owner remains in {}".format(relative)


def test_h_quality_asset_is_replaced():
    assert not (ASSETS / "dscl_pvn.png").exists()
    assert (ASSETS / "gen_quality_chk.png").is_file()


def test_retired_setting_identifiers_are_not_runtime_owners():
    paths = [path for path in SUBMOD.rglob("*.rpy") if path.name != "migrations.rpy"]
    paths += [path for path in PYTHON.glob("*.py") if not path.name.startswith("test_")]
    found = {}
    for path in paths:
        text = path.read_text(encoding="utf-8")
        hits = python_owner_names(text) if path.suffix == ".py" else rpy_owner_names(remove_compatibility_dicts(text))
        if hits:
            found[str(path.relative_to(ROOT))] = sorted(hits)
    assert not found, "retired runtime setting identifiers remain: {}".format(found)


def test_retired_owner_scanners_ignore_prose_and_detect_real_subscripts():
    note = 'note = "sfe_aggressive = documentation only"\n'
    owner = 'data["sfe_aggressive"] = value\n'
    assert "sfe_aggressive" not in python_owner_names(note)
    assert "sfe_aggressive" in python_owner_names(owner)
    assert "sfe_aggressive" not in rpy_owner_names(note)
    assert "sfe_aggressive" in rpy_owner_names(owner)


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
