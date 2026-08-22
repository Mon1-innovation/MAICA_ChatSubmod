# MAICA 1.8.17 话题状态校正

## 问题

MAICA 的话题状态同时由两类持久化数据组成：

- 源话题通过 `renpy.seen_label`、`persistent._seen_ever` 和 `Event.shown_count` 表示实际进度。
- 可见话题通过 MAS `Event.unlocked` 表示是否出现在 Talk 菜单。

MAS 的 `addEvent` 会保留旧 `Event` 的 `unlocked`、`conditional`、`action`、`pool` 等字段。旧版本曾在 Heaven Forest/location/character-file 话题重排时只修正部分字段，因此可能出现“重读话题已解锁，但对应常规话题尚未见过”的持久化不一致。主话题还曾在 `maica_prepend_1` 进入时无条件回锁，导致玩家完成或中断初次 Heaven Forest 流程后，`Let's go to the Heaven Forest` 仍保持锁定。

## 修复范围

`game/Submods/MAICA_ChatSubmod/migrations.rpy` 新增 `maica_reconcile_topic_state`，统一推导状态并修复：

- `maica_main`：只有进入 `maica_prepend_2`、`maica_main`、`maica_talking`、`maica_end_1`，或已完成下游常规话题后才解锁。
- location/preferences 操作话题：分别依赖 `maica_wants_location2`、`maica_wants_preferences2`。
- Heaven Forest、location、preferences、MSpire、MPostal、MVista、character-file 重读：分别依赖其源话题；character-file 支持 `chr2`、`chr_gone`、`chr_corrupted2` 任一分支。
- 内部 dispatch/processing 事件：始终保持 `unlocked=False`、`pool=False`；migration 还恢复其当前 `conditional/action/random` 合约，保证门限满足后仍由 MAS 正常 queue/push。
- greeting 事件：保持 `unlocked=True`，门限只由 greeting conditional 控制，避免错误回锁后无法再次触发 greeting。

状态证据按可靠性顺序使用 `renpy.seen_label`、`persistent._seen_ever` 和 `shown_count`。旧的 character/location 标签及旧 MVista 标记只用于迁移兼容；单独的旧 `unlocked=True` 不会被视为已完成。已实际见过的旧标签会补写到规范 `_seen_ever` 键。

## Migration 与启动检查

- 版本从 `1.8.16` 提升到 `1.8.17`。
- `migration_1_8_17` 先把旧标签的 seen/`shown_count` 证据映射到规范标签，再从持久化/运行时 EVE 字典移除旧注册（不删除 `_seen_ever` 或对话历史），随后执行一次完整合约和状态检查，并在发生变化时调用 `mas_rebuildEventLists()`。
- `maica_topic_state_startup_check` 注册在 `ch30_preloop`、migration 之后，每次启动都执行状态复核并写日志；开发模式下 `maica_is_dev=True` 会使当前 migration 也保持可重复执行。
- `maica_prepend_1` 增加同会话 guard，恢复旧队列项目时不会把已取得的进度再次回锁。
- 修复动作会记录 warning，例如 `MAICA: topic state corrected (...) ... unlocked True -> False`；每次检查都会记录 `MAICA: topic state check (...)` 汇总及进度证据，不包含用户聊天内容。

## 兼容性与验证

状态检查只修改 MAICA 事件对象和 `_seen_ever` 的规范键，不删除用户对话历史；未满足门限的常规事件仍保留原 conditional/action，因此后续 successful-chat 计数达到门限时可正常解锁。

已执行：

- `python -m pytest -q`：539 passed。
- `git diff --check`：通过。
- 纯 Python stub 验证冷状态、Heaven Forest 源话题、location 源话题和重复执行的幂等性。

本机未发现 Ren'Py SDK/`renpy.exe`，因此未执行官方 Ren'Py lint；MAS API 行为依据上游 revision `a7e260c308000e2e21c173d5f751bce81e19b7ba`（`Monika After Story/game/event-handler.rpy`、`definitions.rpy`）核对。
