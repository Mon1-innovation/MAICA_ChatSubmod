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

- 当前任务：任务 3，修复 session、MSpire 与发送前尺寸校验。
- 已完成：隔离 worktree、干净基线测试、中文设计与计划恢复、任务 1A/1B 契约测试、任务 2 MTrigger 严格协议与六个内置 switch，以及逐任务规格和质量审查。
- 待完成：任务 3–9 的实现、两阶段逐任务复核、最终全局审查和发布门禁。
- 阻塞项：无。
- 下一步：派发任务 3 实现代理，先运行 session/MSpire 定向红灯，再实现 UTF-8 字节限制、紧凑 JSON 和 `ctg_weight` 规范化。

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

## DriftCheckDraft

- 原始意图：保持一致，现已明确为从干净基线完整重做。
- 兼容边界：保持 `1.7.8` 存档和现有用户流程。
- 新增所有者：MTrigger validation 与 request builder 成为协议规范化 owner，符合计划；后续纯迁移辅助模块仍未创建。
- 退役轨：旧字段、状态、cookie、端点和 v1.2 网络分支仍明确退役。
- 决策：`continue`；任务 2 未引入 v1.2 网络 fallback，未触及后续设置迁移或版本门禁。

## ResumeStateHint

恢复时先读取本文件、`00-intent.md`、`10-baseline-readset.md`、`20-spec.md` 和 `30-plan.md`，再比较 worktree 状态与最近任务提交。不得从主工作区或 stash 自动恢复业务代码。
