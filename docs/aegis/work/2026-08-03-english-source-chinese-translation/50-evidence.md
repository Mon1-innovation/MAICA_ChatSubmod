# 验证证据

日期：2026-08-03

## 自动验证

- `python -m pytest tests/test_translation_source_language.py -q`：8 passed。
- `python -m pytest tests/test_backend_v13_compat.py -q -x`：137 passed。
- `python -m pytest tests -q -x`：315 passed。
- `rg -n '^translate english' game/Submods/MAICA_ChatSubmod/tl`：无匹配。
- `git -c core.whitespace=cr-at-eol diff --check`：无输出。

迁移契约覆盖默认语言、英文翻译块退役、插值 token 一致性、默认玩家可见源中文、对话插值变量、MAS 事件菜单元数据、中文翻译 ID 唯一性和重复英文 key 冲突。

## 范围审计

默认源中保留的中文已逐项分类为：

- 注释、docstring 与开发日志。
- `raw_session_example.rpy` 中明确排除的示例 prompt 与示例消息。
- `item_name_zh` 等显式双语业务字段。
- MTrigger 内部选择值与兼容键，不属于 Ren'Py 玩家可见源文本。

`raw_session_example.rpy` 与 `styles.rpy` 的临时格式差异已精确恢复。一次性迁移器已删除，不构成运行时或维护期第二所有者。

## 调试证据

语言反转使既有测试中的两个隐含假设失效：固定 500 字符 UI 检查窗口，以及用于 RPY 字符串剥离的回溯正则。前者改为分别检查 `textbutton` 动作块和 `use num_bar` 范围行；后者改用现有线性 `lex_source()`。目标测试和完整回归均通过。

## 剩余风险

- `Get-Command renpy` 无结果，仓库也没有 `renpy.exe`、`renpy.py` 或 launcher，因此未运行 Ren'Py 官方 lint/编译。
- 未在实际 MAS 游戏中切换 `english`/`chinese` 完成视觉与交互抽查。
- 按用户要求，既有英文中的语法、拼写和措辞问题原样保留。
- 少量既有中英文文本标签差异原样保留；自动检查仅强制运行时插值 token 一致。

## 结论草案

- EvidenceBundleDraft：静态迁移契约、后端兼容测试、完整 pytest、翻译块扫描和范围审计均有直接证据。
- DriftCheckDraft：范围、存档/协议兼容边界和翻译 ID 所有权保持；无运行时适配层残留。
- 证据等级：B。核心静态契约与回归有直接证据，但缺少 Ren'Py 官方解析和实际游戏主流程验证。
