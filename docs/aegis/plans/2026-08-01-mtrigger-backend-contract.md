# MTrigger Backend Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use aegis:subagent-driven-development (recommended) or aegis:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 同步 MTrigger 新 envelope、固定名称模板和 `memory_template`，并将有效记忆原样保存到玩家补充信息。

**Architecture:** `maica_mtrigger.py` 继续唯一拥有模板和请求构建契约，`maica_tasker_sub.py` 只适配 WebSocket envelope，`trigger.rpy` 负责 Ren'Py 持久化回调。旧 envelope 解析器直接退役，不增加 fallback。

**Tech Stack:** Python 2/3 兼容代码、Ren'Py `.rpy`、pytest。

**Baseline / Authority Refs:** `docs/aegis/specs/2026-08-01-mtrigger-backend-contract-design.md` 与用户提供的后端更新说明。

**Compatibility Boundary:** `alter_affection` 本地名称、非固定名称模板、`maica_quality_status`、手动玩家信息的 `[player]` 前缀和 `mt_concl_memory` 保持不变。

**Verification:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_v13_contract_runtime.py tests/test_backend_v13_compat.py -q`，随后 `git diff --check`。

---

### Task 1: 新 MTrigger 返回 Envelope

**Files:**
- Modify: `game/python-packages/maica_tasker_sub.py`
- Test: `tests/test_v13_contract_runtime.py`

**Repair Track:** 根因是 handler 遍历 envelope 字段；规范所有者是 `MTriggerWsHandler.on_received()`。只读取 `name` 与 `arguments` 并校验类型。

**Retirement Track:** 删除旧 `{trigger_name: arguments}` 遍历逻辑；没有保留理由或删除前置条件。

- [x] 添加新 envelope 分发与旧 envelope 拒绝测试。
- [x] 运行测试并确认旧实现产生两次错误分发且仍接受旧格式。
- [x] 改为 `self._trigger_func(content['name'], content['arguments'])` 的严格校验路径。
- [x] 增加非对象、缺字段及错误字段类型的参数化测试。
- [x] 运行 `python -m pytest tests/test_v13_contract_runtime.py -q -k "mtrigger_ws_handler"`，预期全部通过。

### Task 2: 固定名称与 Memory 模板

**Files:**
- Modify: `game/python-packages/maica_mtrigger.py`
- Test: `tests/test_v13_contract_runtime.py`

**Impact / Compatibility:** 固定模板在本地使用固定名称路由，build 必须发送该固定 `name`；普通模板保持当前 payload。

- [x] 添加失败测试：affection 只接受 `alter_affection` 且 build 发送该 name；memory 只接受 `write_memory`、build 发送该 name、上限为一、`memory_item` 传给回调。
- [x] 运行定向测试，预期因模板缺失和固定名称未验证而失败。
- [x] 新增 `memory_template = MTriggerTemplate("memory_template", "memory_item", ...)`、规范模板注册、两个固定名称映射和 memory 上限。
- [x] 在 `validate()` 拒绝固定模板的非固定名称；在 `build()` 对固定模板发送固定 name。
- [x] 运行 MTrigger 运行时测试，预期通过。

### Task 3: 注册 Write Memory 并安全写入

**Files:**
- Modify: `game/Submods/MAICA_ChatSubmod/header.rpy`
- Modify: `game/Submods/MAICA_ChatSubmod/trigger.rpy`
- Test: `tests/test_backend_v13_compat.py`

**Impact / Compatibility:** 手动输入仍添加 `[player]`；后端 memory_item 原样保留 `{player_name}`。持久化唯一入口仍为 `maica_validate_player_addition()`。

- [x] 添加失败的源契约测试：校验函数支持 `prefix_player=False`；`write_memory` 使用该参数并只在返回非 None 时 append；注册 `MTriggerBase(memory_template, "write_memory", ...)`。
- [x] 运行 `python -m pytest tests/test_backend_v13_compat.py -q -k "memory_template or player_addition"`，预期失败。
- [x] 将签名改为 `maica_validate_player_addition(raw_addition, additions, edittarget=None, prefix_player=True)`，仅在参数为真时添加 `[player]`。
- [x] 在 `trigger.rpy` 注册 request 方法的 `write_memory`，回调调用校验函数并在成功时追加。
- [x] 运行定向源契约测试，预期通过。

### Task 4: 回归与收尾

**Files:**
- Verify: all changed files

- [x] 运行 `python -m pytest tests/test_v13_contract_runtime.py tests/test_backend_v13_compat.py -q`。
- [x] 运行 `git diff --check` 并审阅限定 diff，确认没有旧 envelope fallback、没有 `[player]{player_name}` 双前缀和无关改动。
- [x] 记录测试数量、残余风险和旧逻辑退役情况。
