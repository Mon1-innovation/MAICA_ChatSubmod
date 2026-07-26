# 长任务检查点

## TaskIntentDraft

从干净 `1.7.8` 基线重新实现完整 MAICA 后端 v1.3 前端迁移，目标版本 `1.8.0`。旧 stash 仅用于审查对照，不应用旧业务代码。

## BaselineReadSetHint

- 原始清单：`D:\Windows\Download\v1.2_to_v1.3 (1).txt`
- 后端权威提交：`8d2c44795dbe44a70dcb42a5870051912dae4f73`
- 规格：`20-spec.md`
- 实施计划：`30-plan.md`
- 本地映射：`PowerToys_Paste_20260703220346_change_mapping.md`

## ImpactStatementDraft

影响设置、持久化迁移、WebSocket/REST 契约、MTrigger、MSpire/MPostal、消息解析、资产引用与测试。不得修改后端、重设计 UI、恢复 v1.2 网络协议或覆盖旧 stash。

## TodoCheckpointDraft

- 当前任务：任务 9，执行全量发布门禁并最后更新前端版本。
- 已完成：隔离 worktree、干净基线测试、中文设计与计划恢复、任务 1A/1B 契约测试、任务 2 MTrigger、任务 3 session/MSpire、任务 4 WebSocket/完成包、任务 5 Vista/emotion/nickname/legality，以及逐任务规格和质量审查。
- 待完成：任务 9 的全量自动检查、可用 lint、可执行冒烟、最终版本更新与发布证据。
- 阻塞项：无。
- 下一步：先运行全量门禁与环境能力检查；只有门禁满足或剩余人工风险被明确记录后，才把 `maica_ver` 更新为 `1.8.0` 并复跑。

## EvidenceBundleDraft

- worktree：`E:\GithubKu\MAICA_ChatSubmod\.worktrees\maica-v13-repair`
- 分支：`codex/maica-v13-repair`
- 基线提交：`d1c08d2`
- 基线测试：`python -m pytest tests -q` → `1 passed`
- 旧实现备份：主仓库 `stash@{0}`
- 任务 1A 提交：`18d99b2de010e8a8a48386cce51fffe23fc76364`
- 任务 1A 目标测试：`50 collected, 38 failed, 12 passed, 0 errors`
- 任务 1A 审查：规格通过；质量无 Critical/Important。
- 任务 1B 最终提交：`bbf239e31aab96463abba365bf71f60b824c4612`
- 任务 1B 目标测试：`118 collected, 90 failed, 28 passed, 0 errors`；旧生产红灯符合预期。
- 任务 1B 定向 owner/scanner 复审：`13 passed, 105 deselected`；22 个主动 runtime 正反例全部匹配。
- 任务 1B 审查：规格通过；质量 Approved，无 Critical/Important。
- 任务 2 最终提交：`25a3d4a6d937019b310facc53e0dcf4300a5e908`
- 任务 2 目标测试：`42 passed`；完整 runtime 为 `46 passed, 20 failed`，剩余均属后续任务。
- 任务 2 审查：规格通过；质量 Approved，无 Critical/Important。
- 任务 3 最终提交：`7579f3e257bf14c02f0615d5019f74fb94c8da89`
- 任务 3 目标测试：`59 passed`；完整 runtime 为 `99 passed, 8 failed`，剩余均属后续任务。
- 任务 3 审查：规格通过；质量 Approved，无 Critical/Important/Minor。
- 任务 4 最终提交：`8026472d0334569074d2f4afac6675d806267eda`
- 任务 4 目标测试：`23 passed`；完整 runtime 为 `122 passed, 5 failed`，剩余均属后续任务。
- 任务 4 审查：规格通过；质量 Approved，无 Critical/Important/Minor。
- 任务 5 实现提交：`64ceac14a0c2e0ef3e50592ad0dd04198633b5a9`；审查修复提交：`bafb16b`。
- 任务 5 目标测试：runtime `8 passed`，静态契约 `4 passed`；完整 runtime 为 `130 passed, 2 failed`，剩余均属后续任务。
- 任务 5 审查：规格通过；质量 Approved，无 Critical/Important/Minor。
- 任务 6 定向静态测试：`129 passed, 1 deselected`；定向 runtime：`138 passed, 2 deselected`。
- 任务 6 编译和 `git diff --check` 通过；仅保留既存 ASCII 图转义警告。
- 任务 6 修复三态设置、完整改名、幂等迁移、additions 备份/过滤、MPostal `twk_super`、迁移优先级和英文翻译同步。
- 任务 7 runtime：`140 passed`；静态测试排除任务 8 门禁后 `129 passed, 1 deselected`。
- 任务 7 已初始化 `version_info`、兼容 `disable(status=None)`，本地 dev override 已修复且保持忽略。
- 任务 8 退役扫描：`16 passed, 114 deselected`；runtime：`140 passed`。
- 任务 8 完整静态测试仅因最终 `maica_ver` 尚未更新而剩 `1 failed, 129 passed`，符合版本最后切换门禁。

## DriftCheckDraft

- 原始意图：保持一致，现已明确为从干净基线完整重做。
- 兼容边界：保持 `1.7.8` 存档和现有用户流程。
- 新增所有者：MTrigger、request/session/MSpire validator、AutoResume 状态机、完成包解析器与本地 `FallBackEmo` 成为各自协议 owner，符合计划；后续纯迁移辅助模块仍未创建。
- 退役轨：旧字段、状态、cookie、端点和 v1.2 网络分支仍明确退役。
- 决策：`continue`；任务 8 已完成且未提前修改前端发布版本，进入任务 9。

## ResumeStateHint

恢复时先读取本文件、`00-intent.md`、`10-baseline-readset.md`、`20-spec.md` 和 `30-plan.md`，再比较 worktree 状态与最近任务提交。不得从主工作区或 stash 自动恢复业务代码。
