# 当前证据记录

## 审查证据

- 后端最新审查提交：`8d2c44795dbe44a70dcb42a5870051912dae4f73`。
- `.gitignore` 已包含 `game/Submods/MAICA_ChatSubmod/dev_enable.rpy`，且 `git check-ignore -v` 已确认生效。
- 审查用后端临时副本已删除。

## 测试证据

- 干净隔离基线运行 `python -m pytest tests -q`：`1 passed`。
- 旧迁移曾运行 `16/17 passed`，但测试与实现一起保存在 stash 中，不作为重新实现的通过证据。
- 新实现必须从零创建 v1.3 契约测试并留下新的失败/通过证据。

## 发布前必须新增的证据

实现计划完成后，应在本文件追加每个任务的测试命令、实际输出、手工冒烟结果和未执行检查的剩余风险；未满足这些证据时不得宣称 `1.8.0` 修复完成。

## 任务 1A：运行时契约测试

- 最终提交：`18d99b2de010e8a8a48386cce51fffe23fc76364`。
- `python -m pytest tests/test_v13_contract_runtime.py -q`：`50 collected, 38 failed, 12 passed, 0 errors`；红灯对应尚未实现的 v1.3 production 契约。
- `python -m pytest tests/test_start_maica_background_download.py -q`：`1 passed`。
- 规格审查：通过。
- 质量审查：无 Critical/Important；Validator 使用真实事件累计，MaicaAi 测试恢复全局日志状态。

## 任务 1B：静态迁移与退役契约测试

- 最终提交：`bbf239e31aab96463abba365bf71f60b824c4612`；测试范围从基线 `46a84bc82fcc7ee358f57afccc02ef9646407d4d` 开始。
- `python -m pytest tests/test_backend_v13_compat.py -q --collect-only`：`118 tests collected`，无 collection/import/fixture error。
- `python -m pytest tests/test_backend_v13_compat.py -q`：旧 `1.7.8` 生产实现为 `90 failed, 28 passed`，无 ERROR/warning；红灯对应待实现的 v1.3 生产契约。
- `python -m pytest tests/test_start_maica_background_download.py -q`：`1 passed`。
- `python -m py_compile tests/test_backend_v13_compat.py`：通过。
- `git diff --check`：通过；worktree clean。
- 覆盖范围：14 项设置改名、`1.8.0` 迁移注册、默认/UI/runtime 唯一 owner、三态设置、`tz`、语言 auto、cookie/strict 退役、认证与断点状态、MTrigger/MSpire/MPostal、Vista、emotion/nickname/legality、additions、质量设置与资产、退役协议扫描。
- 解析器证据：AST/tokenize 双失败显式拒绝；兼容映射只豁免完整、唯一、精确的 14 项映射；Ren'Py 扫描使用单遍栈，深度压力样本访问次数为 `2 * token 数`。
- owner 对抗证据：最终复审主动执行 22 个 runtime 正反例，`MISMATCH []`；定向测试 `13 passed, 105 deselected`。
- 规格审查：通过。
- 最终质量审查：Approved，无 Critical/Important；此前发现的 UI 跨属性、dead payload、值侧引用、任意 docs/log 嵌套、alias 快照、容器更新和控制流顺序问题均已补回归并修复。
