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
