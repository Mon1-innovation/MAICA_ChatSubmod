# MAICA 1.8.17 话题状态校正

## 背景

MAICA 的话题有两种不同的状态：

- 源话题是否真的执行过，由 `renpy.seen_label`、`persistent._seen_ever` 和 `Event.shown_count` 证明。
- 话题是否出现在 Talk 菜单，由 MAS 的 `Event.unlocked` 表示。

MAS `addEvent` 会保留已有 `Event` 的字段。旧版本在话题改名和重复注册后，可能只留下错误的 `unlocked=True`，例如 location、character file 或 Heaven Forest 的重读项已经解锁，但对应的常规话题从未执行。上一版校正器还把下游话题的历史反向当成主话题证据，造成 `maica_main` 被错误解锁。

## 状态图

`maica_prepend_2` 是初次 Heaven Forest 流程的上游门限。已执行的 `maica_main`、`maica_end_1` 或 `maica_talking` 也可以证明该流程已经到达主阶段。下游源话题不能反向提升这个门限。

主门限成立后，以下源话题才有资格解锁各自的常规/重读话题：

| 源 | 常规或重读目标 |
| --- | --- |
| `maica_wants_location2` | `maica_mods_location`, `maica_wants_location_reread` |
| `maica_wants_preferences2` | `maica_mods_preferences`, `maica_wants_preferences_reread` |
| `maica_wants_mspire` | `maica_wants_mspire_reread`、MSpire processing |
| `maica_wants_mpostal` | `maica_wants_mpostal_reread`、MPostal processing |
| `maica_pre_wants_mvista` | `maica_wants_mvista_reread`、MVista UI |
| `maica_chr2` / `maica_chr_gone` / `maica_chr_corrupted2` | `maica_chr_reread` |

主门限成立本身隐含初次 Heaven Forest 原话题已经到达，因此 `maica_prepend_reread` 必须同步解锁，即使存档中缺少 `maica_prepend_2` 的单独 seen 标记。

单独的 `Event.unlocked=True`、`unlock_date` 或下游重读状态都不是历史证据。它们会在校正时按上述关系回锁；源话题的真实历史会被保留，所以主门限稍后成立时仍能按原门限恢复后续话题。

## 统一流水线

`migrations.rpy` 中的 `maica_reconcile_topic_state` 是迁移和启动检查共用的唯一入口，步骤固定为：

1. 清理旧 EVE 注册、队列和 Talk 引用，并把旧标签的 seen/shown_count 证据映射到当前标签；同步清理 MAS 初始化时生成的 `mas_all_ev_db` 快照。若标签已迁移到 GRE，则保留 GRE 对象。
2. 读取所有源证据，不读取 `Event.unlocked` 作为进度。
3. 先计算 `main_ready`，再对每个下游源应用单向 gate；被阻断的证据会记录为 `blocked-by:main (...)`。
4. 遍历 `_maica_topic_contract_specs()` 的声明式契约表，一次性修正 `unlocked`、`conditional`、`action`、`random`、`pool` 和 greeting rules。
5. 输出一条汇总日志；只有状态或旧注册实际改变时调用一次 `mas_rebuildEventLists()`。

契约表显式保存每个条目的 `state_key` 和 `evidence_key`，避免通过字符串拼接推导证据字段。`maica_topic_main_ready()` 和 `maica_topic_ready(source)` 同时用于 Ren'Py 条件字符串和 Python push 入口，防止运行时插件绕过门限。

## Migration 与启动

- `migration_1_8_17` 只调用完整 reconciler；1.8.6--1.8.13 的历史迁移仍保留其版本专属数据转换，但不会替代 1.8.17 的最终状态审计。
- `api.rpy` 在 `ch30_preloop` 的迁移之后注册 `maica_topic_state_startup_check`，每次启动都会再次执行同一 reconciler，即使存档版本已经是当前版本。
- `maica_is_dev` 保持为 `True`，因此开发环境会重复执行 migration；流水线必须幂等，第二次检查只应产生 `corrected=0`，除非外部状态再次发生变化。

日志格式示例：

```text
MAICA: topic state corrected (migration_1_8_17) maica_mods_location unlocked True -> False (blocked-by:main (seen:maica_wants_location2))
MAICA: topic state check (startup) [main=False, location=False, ...]; evidence=[main=not-seen, location=blocked-by:main (...), ...]; corrected=0
```

旧 Event、队列或聚合查找表实际发生变化时，还会记录 `MAICA: legacy topic records normalized (<reason>)`；`corrected` 仍只统计 `Event.unlocked` 的变化。

`corrected` 统计实际的 unlock 状态变化；契约字段被修正但 unlock 状态不变时不会伪造 warning，不过仍会触发一次事件列表重建。

## 验证

已覆盖的回归场景包括：冷存档、仅有下游伪证据、只有主流程历史、主流程成立后恢复子话题、stale `unlocked=True`、旧 tuple Event 的 `shown_count`、旧 EVE/队列引用与 `mas_all_ev_db` 聚合快照清理、重复执行幂等性，以及单一重建调用。

本仓库没有 Ren'Py SDK 或 `renpy.exe`，因此无法运行官方 Ren'Py lint；项目 Python 测试和 `git diff --check` 应在修改后执行。MAS 行为依据本地上游 revision `a7e260c308000e2e21c173d5f751bce81e19b7ba` 的 `event-handler.rpy` 和 `definitions.rpy`。
