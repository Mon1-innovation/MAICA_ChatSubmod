# MAICA 后端 v1.3 前端兼容性修复实施计划

> **给代理执行者：** 实施时按任务顺序使用 `aegis:subagent-driven-development` 或 `aegis:executing-plans`，逐项完成复选框并在任务之间复核。以下步骤按可独立验证的 2–5 分钟动作拆分。

**目标：** 从干净 `1.7.8` 基线重新实现完整后端 v1.3 迁移，发布版本为 `1.8.0`，并安全迁移既有存档。

**架构：** Python 层集中负责协议规范化、严格校验、WebSocket 状态解析和 REST 路由；Ren'Py 层只提供业务值和执行动作。旧持久化键保留一版作为回滚数据，旧网络字段和事件在本版本退役。

**技术栈：** Python 3、Ren'Py `.rpy`、WebSocket 客户端、`requests`、pytest、现有持久化迁移框架。

**基线/权威资料：** 上游 MAICA 提交 `8d2c44795dbe44a70dcb42a5870051912dae4f73`；上游 API 文档；[20-spec.md](20-spec.md)；[10-baseline-readset.md](10-baseline-readset.md)。后端可执行 schema 优先于文档中错误的 `trigger` 示例。

**兼容边界：** `1.7.8` 存档必须可迁移且不静默丢失玩家内容；正常聊天、现有 UI 布局和 session 编号保持稳定。前端不再发送 v1.2 字段，也不监听已退役状态。

**验证总门槛：** 每个任务先写失败测试，再实现，再运行该任务测试；最终运行 `python -m pytest tests -q`、纯 Python 编译、退役协议扫描、任务范围内 `git diff --check`，有 Ren'Py SDK 时运行 lint。

**测试夹具约定：** `tests/test_v13_contract_runtime.py` 内定义测试专用的 `build_switch_payload()`、`build_meter_payload()`、`build_all_builtin_triggers()`、`FakePack`、`NullLogger`、`make_validator()`、`FakeResponse`、`make_vista_manager()`、`analyze_message()` 和 `analyze_unknown_emotion()`；生产模块提供并在对应任务中实现 `MAICAGeneralChatProcessor.build_request()`、`validate_raw_context()`、`validate_query_text()`、`normalize_mspire_weight()`、`normalize_nickname_placeholder()`、`migrate_setting_values()` 和 `backup_and_filter_player_additions()`。这样每个测试名称都有明确所有者，不依赖未声明的第三方插件。

---

### 任务 1：建立可执行的 v1.3 契约测试夹具

**文件：**

- 创建：`tests/test_v13_contract_runtime.py`
- 创建：`tests/test_backend_v13_compat.py`

**目的：** 现有测试主要检查源码字符串，无法发现 `False` switch、`curr_value=0`、错误完成消息等运行时问题。先建立精确请求对象和边界测试，后续修复才有可靠失败信号。

**影响/兼容性：** 测试只模拟请求构造和事件对象，不连接真实后端，不改生产行为；保留现有兼容映射测试。

**修复轨：** 将后端 `agent_tools.py`、`session_early.py`、`ws_config.py` 的规则写成行为断言，并为原迁移清单中的设置改名、认证 type、cookie 退役、断点续传、MSpire、持久化白名单和玩家补充信息建立失败测试。

**退役轨：** 删除只断言“源码包含某字符串”的重复断言；旧字段只在“发送结果不含旧字段”的负向测试中出现。

**步骤：**

- [ ] **1.1 写失败测试。** 在 `tests/test_v13_contract_runtime.py` 定义稳定的导入夹具和以下断言，先调用尚未实现的生产辅助函数：

```python
from maica_mtrigger import MTriggerBase, MTriggerExprop, common_switch_template
from maica_tasker_sub_sessionsender import MAICAGeneralChatProcessor

def build_switch_payload(name, item_list, curr_item):
    return MTriggerBase(
        common_switch_template,
        name,
        exprop=MTriggerExprop(
            item_name_zh="服装",
            item_name_en="clothes",
            item_list=item_list,
            curr_value=curr_item,
        ),
    ).build()

def build_meter_payload(curr_value):
    return MTriggerBase(
        common_meter_template,
        "quality",
        exprop=MTriggerExprop(
            item_name_zh="质量",
            item_name_en="quality",
            value_limits=[0, 1],
            curr_value=curr_value,
        ),
    ).build()

def test_switch_payload_uses_choice_curr_item_and_string_items():
    payload = build_switch_payload(
        name="clothes",
        item_list=["__none__", "制服"],
        curr_item="__none__",
    )
    assert payload["exprop"]["item_list"] == ["__none__", "制服"]
    assert payload["exprop"]["curr_item"] == "__none__"
    assert "curr_value" not in payload["exprop"]
    assert "selection" not in payload

def test_zero_meter_current_value_is_serialized():
    payload = build_meter_payload(curr_value=0)
    assert payload["exprop"]["curr_value"] == 0

def test_request_has_triggers_not_trigger():
    request = MAICAGeneralChatProcessor.build_request(
        query="hello", session=1, triggers=[], pprt=False
    )
    assert request["triggers"] == []
    assert "trigger" not in request
```

- [ ] **1.2 运行失败测试。** 运行 `python -m pytest tests/test_v13_contract_runtime.py -q`；预期当前实现因 `selection`、`curr_value` 或 `trigger` 字段失败。

- [ ] **1.3 增加全量边界断言。** 覆盖名称正则、256 字符、switch/meter 两元素边界、数量 `1/6/6/20`、`-1` session 的 10 条与 16 KiB、MSpire `ctg_weight` `1..100`。

- [ ] **1.4 运行测试确认仍只暴露预期失败。** 运行 `python -m pytest tests/test_v13_contract_runtime.py -q`，记录失败断言，不修改生产代码以迎合测试以外的行为。

- [ ] **1.5 提交测试基线。** 暂存两个测试文件，提交信息使用 `test: lock v1.3 contract boundaries`；若当前工作流不提交，则保留同样的原子差异边界。

**验证：** 任务 1 完成时，新测试必须在旧实现上失败，并且失败原因对应本次审查发现。

### 任务 2：修复 MTrigger 序列化、严格校验和六个内置 switch

**文件：**

- 修改：`game/python-packages/maica_mtrigger.py`
- 修改：`game/python-packages/maica_tasker_sub_sessionsender.py`
- 修改：`game/Submods/MAICA_ChatSubmod/trigger.rpy`
- 测试：`tests/test_v13_contract_runtime.py`

**目的：** 消除 MT 的字段名、类型、假值、数量和 built-in switch 超限问题。

**影响/兼容性：** 内部回调继续接收业务选择；只有网络层字段改为后端 v1.3。佩戴饰品与取下饰品合并为一个 switch，两个动作都保留。

**修复轨：**

- 将 `common_switch_template` 的 datakey 改为 `choice`。
- 将 affection 模板与回调参数改为 `alter_value`，只在内部兼容旧 `affection` 输入。
- `MTriggerBase.build()` 对 `curr_item`/`curr_value` 使用 `is not None`，并输出 v1.3 字段。
- 在 `MTriggerBase.build()` 和 manager 批量构造处校验名称、条目、meter limits、字符串长度和数量。
- `process_request()` 将顶层键改为 `triggers`。
- 将所有 `False` 选项替换为稳定字符串 `__none__`；删除 hair 当前项尾逗号。
- 合并 `UnWearTrigger` 与 `AcsTrigger` 为一个 `AccessoryTrigger`，以 `wear|<name>` 和 `unwear|<name>` 字符串映射两个动作。

**退役轨：** 删除运行路径对 `selection`、`trigger` 和布尔 switch 值的依赖；测试保留旧值仅用于确认发送前拒绝。

**步骤：**

- [ ] **2.1 写 MT 失败测试。** 增加以下断言：

```python
def test_invalid_trigger_name_is_rejected():
    with pytest.raises(ValueError):
        build_trigger_payload(name="bad name", item_list=["ok"])

def test_switch_items_must_be_strings():
    with pytest.raises(ValueError):
        build_trigger_payload(name="ok_name", item_list=["ok", False])

def test_accessory_actions_share_one_switch():
    payload = build_all_builtin_triggers()
    switches = [item for item in payload if item["template"] == "common_switch_template"]
    assert len(switches) == 6
    assert any("wear|" in item["exprop"]["item_list"][0] for item in switches)
```

- [ ] **2.2 运行失败测试。** 运行 `python -m pytest tests/test_v13_contract_runtime.py -q -k "trigger or switch or accessory"`；预期失败。

- [ ] **2.3 实现模板字段修复。** 在 `maica_mtrigger.py` 将模板 datakey 改为 `choice`，将条件改为 `self.exprop.curr_value is not None`，对 `curr_item`、`curr_value` 分别写入正确字段。

- [ ] **2.4 实现集中校验。** 添加 `MTriggerBase.validate()` 与 `MTriggerManager.validate_batch()`；对名称使用 `re.fullmatch(r"[A-Za-z0-9_-]{1,64}", name)`，对每个字符串限制 256 字符，对 meter 强制 `len(value_limits) == 2` 且升序，对四类数量执行 `1/6/6/20`。

- [ ] **2.5 修正请求封装。** 新增纯函数式静态方法 `MAICAGeneralChatProcessor.build_request(query, session, triggers, visions=None, pprt=False)`，由 `process_request()` 调用。静态方法返回以下字典，`process_request()` 只负责 JSON 编码和发送：

```python
data = {
    "type": "query",
    "chat_session": session,
    "query": query,
    "triggers": triggers,
    "pprt": pprt,
}
```

保留已有 vision 等可选字段，但不得重新加入 `trigger`。

- [ ] **2.6 修正 Ren'Py 触发器。** 将 `clothes_data[False]`、`unlocked_games_dict[False]` 等改为 `"__none__"`；将回调读取改为 `data.get("choice")`；修复 hair 的 `curr_value` 尾逗号；新增合并饰品触发器并将两个动作映射到原有 label。

- [ ] **2.7 运行任务测试。** 运行 `python -m pytest tests/test_v13_contract_runtime.py -q -k "trigger or switch or accessory"`，预期全部通过。

- [ ] **2.8 记录原子提交。** 使用 `fix: align mtrigger payload with v13 schema`。

**验证：** 生成的完整内置触发器列表严格为六个 switch，所有 item 均为字符串，`curr_value=0` 不丢失，出站对象不含 `trigger`/`selection`。

### 任务 3：修复 session、MSpire 与发送前尺寸校验

**文件：**

- 修改：`game/python-packages/maica_tasker_sub_sessionsender.py`
- 修改：`game/python-packages/maica_context_query.py`
- 修改：`game/python-packages/maica.py`
- 测试：`tests/test_v13_contract_runtime.py`

**目的：** 使 `-1 session`、普通 session 和 MSpire 请求在本地即符合后端边界。

**影响/兼容性：** 合法 query 语义不变；超限输入从“发送后失败”变为“发送前明确报错”。

**修复轨：**

- `-1 session` 使用 `ensure_ascii=False, separators=(',', ':')` 的 UTF-8 字节数，最多 10 条。
- 普通 session 使用 UTF-8 4 KiB 限制。
- `ctg_weight` 默认 `10`，强制整数 `1..100`，并透传到 `inspire` 对象。
- MSpire `start_MSpire()` 显式传递规范化权重。
- MSpire 将 `use_cache` 放入 `inspire` 条目；无分类时发送空字典 `{}` 采用后端默认配置。
- MPostal 使用 `postmail` 配置并采用 `twk_super`，不再使用简单模式或 `ic_prep`。

**退役轨：** 删除 `MAX_CONTEXT_LENGTH = 4096` 及其旧说明；不保留把超长 query 静默裁剪的分支。

**步骤：**

- [ ] **3.1 写边界失败测试。** 使用以下形式覆盖字节而非字符：

```python
def test_raw_context_accepts_ten_rounds_and_compact_16k_bytes():
    query = [{"role": "user", "content": "a"}] * 10
    assert validate_raw_context(query) is None

def test_raw_context_rejects_eleven_rounds():
    with pytest.raises(ValueError, match="10"):
        validate_raw_context([{"role": "user", "content": "a"}] * 11)

def test_mspire_weight_is_integer_1_to_100():
    assert normalize_mspire_weight(10) == 10
    with pytest.raises(ValueError):
        normalize_mspire_weight(0.4)
```

- [ ] **3.2 运行失败测试。** 运行 `python -m pytest tests/test_v13_contract_runtime.py -q -k "session or mspire"`。

- [ ] **3.3 实现紧凑 JSON 校验。** 在 sessionsender 模块新增 `validate_raw_context(query)`，使用 `json.dumps(query, ensure_ascii=False, separators=(",", ":")).encode("utf-8")` 并检查 `len(payload) <= 16 * 1024`；同时检查列表长度不超过 10。

- [ ] **3.4 实现普通 session 和 MSpire 校验。** 在 sessionsender 模块新增 `validate_query_text(query)` 和 `normalize_mspire_weight(value)`；前者检查字符串 UTF-8 不超过 4 KiB，后者在转换前拒绝 `bool`、小数和范围外值并返回 `1..100` 的整数，默认调用值为 `10`。

- [ ] **3.5 更新文档和常量。** 同步 `maica_context_query.py`、sessionsender docstring、`maica.py` 的 `start_raw_context()` 说明和 MSpire 参数默认值。

- [ ] **3.6 运行任务测试。** 运行 `python -m pytest tests/test_v13_contract_runtime.py -q -k "session or mspire"`，预期通过。

- [ ] **3.7 记录原子提交。** 使用 `fix: enforce v13 session and mspire limits`。

**验证：** 10 条/16 KiB 边界通过，11 条或超出字节数失败，普通 session 按 UTF-8 4 KiB 失败，`ctg_weight=10` 通过而 `0.4` 失败。

### 任务 4：统一 WebSocket 状态与完成包验证

**文件：**

- 修改：`game/python-packages/maica_tasker_sub.py`
- 修改：`game/python-packages/maica.py`
- 修改：`game/python-packages/maica_tasker_sub_sessionsender.py`
- 修改：`game/Submods/MAICA_ChatSubmod/header.rpy`
- 修改：`game/Submods/MAICA_ChatSubmod/tl/header.rpy`
- 测试：`tests/test_v13_contract_runtime.py`

**目的：** 修复 MPostal、质量、loop 状态名，并让完成包验证适配当前后端文本且跨轮安全。

**影响/兼容性：** 普通流式消息处理保持不变；只改变状态名和验证器对完成消息的解析。

**修复轨：**

- MPostal processor 监听 `maica_core_streaming_continue`。
- 回调使用 `maica_quality_status` 和 `maica_loop_warn_reset`。
- 登录请求显式发送 `type: auth`，不依赖后端自动推断。
- AutoResumeTasker 以 `maica_mcore_gen_start` 标记生成开始，并在聊天循环结束时清理断点状态。
- 删除 `MAICAWSCookiesHandler`、`WSCookiesTask`、strict-mode 设置/UI 以及所有 WebSocket 请求中的 cookie 注入。
- 新增 `_extract_reported_packets(content)`，只解析包数，不要求 tracker ID。
- `_validate_and_process_complete()` 在所有退出路径调用 `_reset_count()`。

**退役轨：** 运行代码中删除三个旧状态名和 tracker ID 强制解析；只在负向测试中保留旧文本。

**步骤：**

- [ ] **4.1 写完成消息失败测试。** 添加：

```python
class NullLogger(object):
    def __getattr__(self, _name):
        return lambda *args, **kwargs: None

class FakePack(object):
    def __init__(self, content):
        self.content = content

def make_validator():
    validator = object.__new__(StreamingPacketValidator)
    validator._packet_count = 0
    validator._enabled = True
    validator._validation_passed = True
    validator.logger = NullLogger()
    return validator

def test_complete_message_without_tracker_id_validates_and_resets():
    validator = make_validator()
    validator._packet_count = 3
    validator._validate_and_process_complete(
        FakePack(content="Streaming finished for user, 3 packets sent")
    )
    assert validator.packet_count == 0
    assert validator.validation_passed is True

def test_malformed_complete_message_resets_count():
    validator = make_validator()
    validator._packet_count = 2
    validator._validate_and_process_complete(FakePack(content="(from cache)"))
    assert validator.packet_count == 0
```

- [ ] **4.2 运行失败测试。** 运行 `python -m pytest tests/test_v13_contract_runtime.py -q -k "complete or status"`。

- [ ] **4.3 实现解析器。** 让 `_extract_reported_packets()` 支持当前的 `..., <n> packets sent` 和缓存完成文本；解析不到整数时记录错误并返回 `None`，调用方先重置再进入受控断连。

- [ ] **4.4 修正状态注册和回调。** 将 MPostal `except_ws_status` 和 `mpostal_callback()` 同步为 `maica_core_streaming_continue`；更新质量和 loop 状态。

- [ ] **4.5 覆盖跨轮计数。** 测试成功、数量不匹配、畸形完成、断开和显式 reset 后下一轮从 0 开始。

- [ ] **4.6 运行任务测试并提交。** 运行 `python -m pytest tests/test_v13_contract_runtime.py -q -k "complete or status"`；提交 `fix: normalize v13 websocket statuses`。

**验证：** 当前后端完成文本不需要 tracker ID；所有成功和失败路径都不会污染下一轮计数。

### 任务 5：修复 MVista 路由、昵称占位符和表情回退

**文件：**

- 修改：`game/python-packages/maica_vista_files_manager.py`
- 修改：`game/python-packages/maica.py`
- 修改：`game/python-packages/emotion_analyze_v2.py`
- 修改：`game/Submods/MAICA_ChatSubmod/screen_subs.rpy`
- 测试：`tests/test_v13_contract_runtime.py`

**目的：** 让 Vista 列举命中新端点，退役 `/emotion`，并确保 `[player_nickname]` 不被当成未知表情。

**影响/兼容性：** Vista 上传、删除、下载保持原路径；聊天消息继续使用本地表情回退和 MAS 昵称函数。

**修复轨：**

- 将列表请求改为 `GET /vista/list`，保留下载 `GET /vista?content=`。
- legality 成功结果显示 `latitude/longitude`，并兼容响应中的 `lat/lng/lon` 别名。
- `MoodStatus` 不再把 `MaicaAi.get_emotion` 作为网络回退；未知标签使用 `FallBackEmo`。
- 在解析器中把 `player_nickname` 视为占位符并改写为 `[mas_get_player_nickname()]`。

**退役轨：** 删除 `get_emotion()` 的 `/emotion` 请求和测试脚本调用；删除旧 Vista 列表 URL 的运行分支。

**步骤：**

- [ ] **5.1 写 REST 与消息失败测试。** 添加：

```python
def test_vista_list_uses_list_endpoint(monkeypatch):
    calls = []
    monkeypatch.setattr(
        maica_vista_files_manager.requests,
        "get",
        lambda url, **kwargs: calls.append((url, kwargs)) or FakeResponse([]),
    )
    manager = make_vista_manager()
    manager.list_files()
    assert calls[-1][0].endswith("/vista/list")

def test_player_nickname_is_local_placeholder():
    result = analyze_message("[player_nickname]你好")
    assert "[mas_get_player_nickname()]" in result

def test_emotion_endpoint_is_not_called(monkeypatch):
    monkeypatch.setattr(requests, "get", fail_if_called)
    assert analyze_unknown_emotion("[未知标签]文本")
```

- [ ] **5.2 运行失败测试。** 运行 `python -m pytest tests/test_v13_contract_runtime.py -q -k "vista or nickname or emotion"`。

- [ ] **5.3 修正 Vista 路由。** 只修改列举方法的 URL，下载方法继续使用带 `content` 参数的 `/vista`。

- [ ] **5.4 退役网络表情回退。** 移除 `get_emotion()` 中的 requests 调用，将 `MaicaAi` 初始化改为本地回退配置；让 `emotion_analyze_v2.py` 在 `fallback_predictor is None` 时使用 `fallback_selector.predict()`。

- [ ] **5.5 处理昵称占位符。** 在表情标签清洗阶段识别 `player_nickname`，替换为 `[mas_get_player_nickname()]` 后再交给消息队列。

- [ ] **5.6 运行任务测试并提交。** 运行 `python -m pytest tests/test_v13_contract_runtime.py -q -k "vista or nickname or emotion"`；提交 `fix: retire obsolete emotion route and update vista list`。

**验证：** Vista 列举请求为 `/vista/list`，下载路径不变，未知表情不发网络请求，昵称可正常插值。

### 任务 6：修复三态设置、默认值与 `1.8.0` 持久化迁移

**文件：**

- 创建：`game/python-packages/maica_v13_migration.py`
- 创建：`game/Submods/MAICA_ChatSubmod/migrations.rpy`
- 修改：`game/Submods/MAICA_ChatSubmod/header.rpy`
- 修改：`game/Submods/MAICA_ChatSubmod/screen_subs.rpy`
- 修改：`game/Submods/MAICA_ChatSubmod/main.rpy`
- 修改：`game/Submods/MAICA_ChatSubmod/trigger.rpy`
- 修改：`game/Submods/MAICA_ChatSubmod/trigger_labels.rpy`
- 修改：`game/Submods/MAICA_ChatSubmod/tl/header.rpy`
- 修改：`game/Submods/MAICA_ChatSubmod/tl/screen_subs.rpy`
- 修改：`game/Submods/MAICA_ChatSubmod/persistent_filter.json`
- 修改：`game/python-packages/json_exporter.py`
- 修改：`game/python-packages/maica.py`
- 移动：`game/mod_assets/console/dscl_pvn.png` → `game/mod_assets/console/gen_quality_chk.png`
- 测试：`tests/test_v13_contract_runtime.py`

**目的：** 让三个三态设置符合后端 `Literal[0,1,2]`，使迁移实际从 `1.7.8` 运行到 `1.8.0`，并保护历史玩家补充信息。

**影响/兼容性：** 新默认值与后端一致；旧布尔值按 `False->0`、`True->1` 保留用户已见状态；旧键保留一版但运行时只读新键。

**修复轨：**

- 迁移函数和队列目标保持 `1.8.0`，但 `maica_ver` 在任务 9 发布门禁通过前仍保持 `1.7.8`。
- 三个设置默认整数 `1`，UI 改用数值控件。
- 完整实现以下改名：`sfe_aggressive→prompt_pname_repl`、`mf_aggressive→mf_llm_concl`、`tnd_aggressive→mf_const_tools`、`esc_aggressive→esearch_llm_concl`、`amt_aggressive→mf_precheck_mt`、`pre_additive→mf_context_rnds`、`post_additive→mt_context_rnds`、`dscl_pvn→gen_quality_chk`、`pre_astp→mf_disable_loop`、`post_astp→mt_disable_loop`、`enforce_lang→gen_enforce_lang`、`sf_extraction→savefile_access`、`max_length→session_len_limit`、`ic_prep→twk_super`。
- 添加 `prompt_allow_nickname`、`mf_sf_access_impl`、`mf_const_sf_access`、`mt_concl_memory` 和语言 `auto`；`mt_disable_loop` 默认 `True`，`session_len_limit` 上限 `28672`，`mf_const_tools` 最大值 `2`。
- 从持久化上传白名单移除 `mas_sf_hcb`，从出站参数移除 `mt_extraction`，将 `tz` 保持为常规设置。
- 同步 `gen_quality_chk` 的 screen、trigger label、翻译和图片资产名。
- 迁移保留旧键、删除废弃出站键，并将 `mf_const_tools == 3` 降为 `2`。
- 在迁移前将完整 additions 保存到 `persistent._maica_v18_player_additions_backup`，活动列表只上传合法的 512/1536 字节范围。

**退役轨：** 退役运行路径中的旧参数名和删除/静默截断逻辑；旧键仅保留为一版回滚数据。

**步骤：**

- [ ] **6.1 写迁移失败测试。** 添加：

```python
def test_bool_settings_migrate_without_losing_visible_state():
    values = {"mf_sf_access_impl": False, "mf_const_sf_access": True}
    migrate_setting_values(values)
    assert values["mf_sf_access_impl"] == 0
    assert values["mf_const_sf_access"] == 1

def test_player_additions_backup_is_created_once():
    values = ["a" * 1537, "ok"]
    backup = []
    backup_and_filter_player_additions(values, backup)
    original = list(backup)
    backup_and_filter_player_additions(values, backup)
    assert backup == original
```

- [ ] **6.2 运行失败测试。** 运行 `python -m pytest tests/test_v13_contract_runtime.py -q -k "migration or setting or addition"`。

- [ ] **6.3 实现纯迁移函数。** 在 `maica_v13_migration.py` 实现 `migrate_setting_values(values, status=None)` 和 `backup_and_filter_player_additions(values, backup, limit=512, bytes_limit=1536)`；函数只操作传入字典/列表，便于 pytest 直接验证，不依赖 Ren'Py。

- [ ] **6.4 实现完整设置迁移与默认值。** 更新 `header.rpy`、`screen_subs.rpy`、`main.rpy`、翻译文件和 `maica.py`，覆盖修复轨列出的全部改名、新参数、默认值和范围；将三个新增设置的 Toggle 替换为现有 `mf_const_tools` 数值选择模式。此步骤不得修改 `api.rpy` 的 `maica_ver`。

- [ ] **6.5 实现幂等迁移。** 创建 `migrations.rpy` 并从 `api.rpy` 的内联迁移入口调用；在 `migration_1_8_0()` 中调用纯函数，先创建 additions 备份，再规范化 active list；旧键迁移后保留副本，废弃键不进入运行参数；依赖现有版本框架并检查备份字段，保证重复执行安全。

- [ ] **6.6 同步白名单、通知和资产。** 从 `persistent_filter.json`、`json_exporter.py` 移除 `mas_sf_hcb`，同步 `gen_quality_chk` 的 screen/trigger/翻译引用，并使用 `git mv` 重命名图片资产。

- [ ] **6.7 修复上传前 additions 处理。** 将剩余 1000 字符限制改为 UTF-8 1536 字节，超过 512 条或非法条目进入备份并只通知一次。

- [ ] **6.8 运行任务测试并提交。** 运行 `python -m pytest tests/test_v13_contract_runtime.py -q -k "migration or setting or addition"`；提交 `fix: migrate settings and player additions for v13`。

**验证：** 从 `1.7.8` 运行一次和两次迁移结果一致；三态出站值为整数；玩家原始 additions 可从备份恢复。

### 任务 7：修复可访问状态、开发覆盖和旧 `disable` 调用

**文件：**

- 修改：`game/python-packages/maica.py`
- 修改：`game/Submods/MAICA_ChatSubmod/api.rpy`
- 修改：`game/Submods/MAICA_ChatSubmod/dev_enable.rpy`（本地忽略文件）
- 测试：`tests/test_v13_contract_runtime.py`

**目的：** 保证 `version_info` 始终存在，让开发覆盖可用，并修正 `disable(status)` 的既存崩溃。

**影响/兼容性：** 无参数 `disable()` 行为不变；传入状态时更新状态并关闭可访问标记。开发文件仍不进入发布包。

**修复轨：**

- 在 `MaicaAi.__init__` 设置 `self.version_info = {"success": False, "content": {}}`。
- 将签名改为 `def disable(self, status=None)`，有 status 时保存它。
- `override_accessable()` 设置同样的安全 `version_info` 哨兵。

**退役轨：** 删除 api 与实现之间不匹配的调用假设；不让 dev override 通过跳过网络检查来跳过字段初始化。

**步骤：**

- [ ] **7.1 写失败测试。** 添加：

```python
def test_disable_accepts_optional_status(maica_instance):
    maica_instance.disable(maica_instance.MaicaAiStatus.VERSION_OLD)
    assert maica_instance.status == maica_instance.MaicaAiStatus.VERSION_OLD

def test_dev_override_keeps_version_info_invariant():
    instance = make_maica_instance()
    override_accessable(instance)
    assert instance.version_info["success"] is False
```

- [ ] **7.2 运行失败测试。** 运行 `python -m pytest tests/test_v13_contract_runtime.py -q -k "disable or accessible or dev"`。

- [ ] **7.3 实现初始化与签名修复。** 按修复轨修改三个文件；不要在 `dev_enable.rpy` 中调用真实网络请求。

- [ ] **7.4 运行任务测试并提交。** 运行同一 `-k` 测试；提交 `fix: preserve maica accessibility invariants`。

**验证：** API 版本检查不再因缺少 `version_info` 或 `disable` 参数而崩溃；开发覆盖可启动且保持安全哨兵。

### 任务 8：退役旧协议并补齐静态扫描

**文件：**

- 修改：`game/python-packages/test_maica.py`
- 修改：`tests/test_backend_v13_compat.py`
- 可能修改：任务 2–7 中列出的运行文件

**目的：** 确保所有旧字段、事件、端点只出现在负向测试、迁移回滚数据或文档中，不再从生产路径发出或监听。

**影响/兼容性：** 不删除旧存档回滚键；只删除网络运行时的旧分支和手动测试脚本 `/emotion` 调用。

**修复轨：** 增加运行时对象扫描：`trigger`、`selection`、`maica_core_nostream_reply`、`maica_dscl_status`、`maica_loop_warn_finished`、旧 Vista 列举 URL、`/emotion` 不得出现在生产路径。

**退役轨：** 删除 `test_maica.py` 的 `/emotion` 手动请求；保留测试中的旧名仅用于断言“不发送/不监听”。

**步骤：**

- [ ] **8.1 写扫描失败测试。** 在 `tests/test_backend_v13_compat.py` 增加运行文件扫描，并排除迁移回滚映射、文档和负向测试区域。

- [ ] **8.2 运行失败扫描。** 运行 `python -m pytest tests/test_backend_v13_compat.py -q -k retired`；记录每个生产命中位置。

- [ ] **8.3 删除生产旧分支。** 逐个清理旧网络键、状态和端点；不使用全仓库替换，避免破坏迁移测试输入。

- [ ] **8.4 运行扫描与全量测试。** 运行 `python -m pytest tests -q`，预期所有测试通过。

- [ ] **8.5 记录原子提交。** 使用 `chore: remove retired v13 protocol paths`。

**验证：** 生产运行文件扫描无旧协议命中；迁移和负向测试仍能证明旧名称被拒绝或不出站。

### 任务 9：版本、发布门禁和手工冒烟

**文件：**

- 修改：`game/Submods/MAICA_ChatSubmod/api.rpy`
- 修改：`game/Submods/MAICA_ChatSubmod/migrations.rpy`
- 修改：`docs/aegis/work/2026-07-21-maica-v13-repair/50-evidence.md`

**目的：** 只有全部修复通过后才切换 `1.8.0`，并留下可复核的发布证据。

**影响/兼容性：** 版本号变更是最后一步；失败时保留 `1.7.8`，不让半完成迁移触发线上存档变更。

**修复轨：** 运行全部自动测试、纯 Python 编译、静态扫描、任务范围 `git diff --check`；有 SDK 时运行 Ren'Py lint；完成手工冒烟。

**退役轨：** 不删除旧回滚键，直到下一版本有独立验证；不通过测试就不更新版本常量。

**步骤：**

- [ ] **9.1 运行全量自动检查。**

```powershell
python -m pytest tests -q
python -m compileall game/python-packages/maica.py game/python-packages/maica_mtrigger.py game/python-packages/maica_tasker_sub.py game/python-packages/maica_tasker_sub_sessionsender.py game/python-packages/maica_context_query.py game/python-packages/maica_vista_files_manager.py game/python-packages/emotion_analyze_v2.py
git diff --check --ignore-space-at-eol -- game/Submods/MAICA_ChatSubmod game/python-packages tests docs/aegis
```

- [ ] **9.2 运行退役协议扫描。** 运行 `python -m pytest tests/test_backend_v13_compat.py -q -k retired`；结果必须为 PASS。

- [ ] **9.3 执行 Ren'Py lint。** 若 `renpy.exe` 已加入 PATH，运行 `renpy.exe E:\GithubKu\MAICA_ChatSubmod lint`；若命令不可用，在 `50-evidence.md` 记录未执行原因，不伪造通过结果。

- [ ] **9.4 执行手工冒烟。** 使用 `1.7.8` 存档副本验证迁移幂等、普通聊天两轮流式响应、MPostal、MSpire、六个内置 switch、MVista 列举/下载、`-1 session`、昵称插值和 `dev_enable.rpy`。

- [ ] **9.5 最后更新版本。** 所有检查通过后才把 `api.rpy` 的 `maica_ver` 改为 `1.8.0`，确认迁移队列仍注册 `1.8.0`，再运行一次迁移测试。

- [ ] **9.6 写入证据并交付。** 将命令输出、手工结果、警告和未执行检查写入 `50-evidence.md`；提交 `release: publish v1.8.0 backend v13 compatibility`。

**验证：** 只有全量自动检查、可用的 Ren'Py lint 和手工冒烟都满足或已明确记录剩余风险时，才可宣称发布准备完成。

## 回滚面

- 代码回滚以任务原子提交为单位；版本号提交必须最后执行。
- 旧设置键和 additions 完整备份保留一版，允许旧前端恢复用户配置。
- 迁移重复执行不会覆盖备份；发现数据问题时先从 `_maica_v18_player_additions_backup` 恢复，再回滚代码。
- 不恢复旧网络字段运行分支；若后端必须回退到 v1.2，应整体回滚到修复前版本，而不是混用两套协议。

## 计划自检

- 每个审查发现均映射到任务 2–8 的修复与测试。
- 所有步骤都有具体文件、命令、断言或预期结果，没有未定义的处理步骤。
- 三态设置、饰品 switch 合并、玩家 additions 备份和版本最后更新均已明确。
- 兼容边界、非目标、修复轨、退役轨和回滚面均已写明。
