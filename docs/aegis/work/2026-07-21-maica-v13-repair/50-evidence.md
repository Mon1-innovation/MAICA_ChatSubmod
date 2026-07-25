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

## 任务 2：MTrigger 严格协议与六个内置 switch

- 最终提交：`25a3d4a6d937019b310facc53e0dcf4300a5e908`；初始实现提交为 `698a7d5aeb76b39960cb4d19256b520df85c4773`。
- 初始定向红灯：`19 failed, 8 passed`；实现和审查补充的调用链、跨 method 总量、有限数、模板伪造等回归均先得到预期失败。
- 最终任务范围：`42 passed`。
- `python -m pytest tests/test_v13_contract_runtime.py -q`：`46 passed, 20 failed`；剩余红灯属于后续 session/MSpire、WebSocket、Vista/emotion 和版本任务。
- `python -m pytest tests/test_start_maica_background_download.py -q`：`1 passed`。
- Python 编译与 `git diff --check`：通过；`maica.py:53` 仍有既存 ASCII 图 invalid escape `SyntaxWarning`，不由本任务引入。
- 出站契约：`choice`、`curr_item`、`curr_value`、`alter_value` 与顶层 `triggers` 已统一；网络运行路径不再发送 `selection`、顶层 `trigger` 或布尔 switch 条目。
- 六个 switch：`clothes`、`minigame`、`weather`、`music`、`hair`、`accessory`；饰品 `wear|名称` / `unwear|名称` 分别映射到原佩戴/取下动作，玩家挑选入口保留。
- 严格校验：四模板总量在 method 过滤前统一计算；名称、字符串、成员关系、meter 范围、bool、NaN/Infinity、Python 2 `long` 和 canonical template schema 均有回归。
- 规格审查：通过；修复了真实聊天仍使用 `trigger=`、跨 method 数量绕过和非有限 meter 三项缺口。
- 最终质量审查：Approved，无 Critical/Important；模板 clone/spoof 与 Python 2 数值兼容已通过独立探针。
- 延期 Minor：manager 暂不拒绝重复 trigger name；Ren'Py 内置触发器仍缺少执行 init 块的集成测试，留待最终 lint/手工冒烟覆盖。

## 任务 3：session 与 MSpire 边界

- 最终提交：`7579f3e257bf14c02f0615d5019f74fb94c8da89`；初始实现提交为 `606a55132ffc1484080997f3dce03f765b5a0805`。
- 初始定向红灯：`11 failed, 3 passed`；补齐 validator 与调用链后为 `19 failed, 3 passed`。审查发现的 session 类型、分类、cache、非有限 JSON 与 MSpire `-1` session 均先补失败测试。
- 最终定向测试：`59 passed`。
- `python -m pytest tests/test_v13_contract_runtime.py -q`：`99 passed, 8 failed`；剩余失败属于后续 WebSocket、emotion、Vista 和 version/disable 任务。
- `python -m pytest tests/test_start_maica_background_download.py -q`：`1 passed`；Python 编译与 `git diff --check` 通过，仅保留 `maica.py:53` 既存 banner 转义警告。
- 普通 query：严格文本与 UTF-8 4 KiB；session 仅允许整数 `-1..9`，`-1` 实际调用链强制 raw list。
- raw context：最多 10 条，紧凑 JSON UTF-8 不超过 16 KiB，`allow_nan=False`，序列化错误不包含用户正文。
- MSpire：权重严格整数 `1..100`；session 仅 `0..9`；cache 仅 session 0；分类必须为非空文本列表并保序、保重复、复制输入，title 始终为列表；空分类发送 `{}`。
- 中英文 `raw_session` 文档已同步为 10 条/16 KiB 与 `MAX_MESSAGES`/`MAX_BYTES`。
- 规格审查：通过；修复了 `-1` 分派、多分类丢失与 Python 2 bytes 校验缺口。
- 最终质量审查：Approved，无 Critical/Important/Minor；此前 session 宽松类型、MSpire 静默转换、非标准 NaN/Infinity JSON 与 MSpire raw session 均已关闭。

## 任务 4：WebSocket 状态、断点续传与完成包

- 最终提交：`8026472d0334569074d2f4afac6675d806267eda`；初始实现提交为 `d450a1d73940187f733f920ec1a0f35faa605696`。
- 本切片契约初始新增红灯：`12 failed`；断线顺序、对抗完成文本、禁用状态、异常清理和通知断连均按 TDD 补充并先复现失败。
- 最终定向 runtime：`23 passed`；静态 auth/cookie/strict/status：`7 passed, 111 deselected`。
- `python -m pytest tests/test_v13_contract_runtime.py -q`：`122 passed, 5 failed`；剩余为 emotion 两项、Vista、version_info 与 disable。
- 背景测试 `1 passed`；相关 Python 编译与 `git diff --check` 通过。保留 `maica.py` ASCII 图和 `test_maica.py` Windows 路径的既存转义警告。
- 状态与认证：MPostal、质量、loop 使用当前 v1.3 状态名；登录显式发送 `type: auth`；生成开始使用 `maica_mcore_gen_start`。
- 断点续传：仅“生成中且已计划重连”跨 `websocket_closed` 保留；登录成功只发送一次 `reconn`；终止、禁用、失败、重置和回调/发送异常均清理双标志。
- 完成包：只接受当前 streaming、cache 与确证 legacy 的整串白名单格式；包数为无符号十进制整数，不要求 tracker ID；负数、小数、任意年份/tracker、恶意尾部均拒绝。
- validator 在成功、数量不匹配、畸形、禁用、通知异常、close 异常和显式 reset 后均清零；通知异常仍执行安全断连且不被 close 异常覆盖。
- cookie/strict：handler、task、请求注入、运行属性/UI 和手工脚本死引用均退役；旧 persistent 默认键仅保留且无读取 owner。
- 规格审查：通过；修复了真实断线事件顺序、正则误取和 AutoResume 清理缺口。
- 最终质量审查：Approved，无 Critical/Important/Minor；异常组合、畸形完成包和退役 owner 已独立复核。

## 任务 5：MVista、表情回退、昵称与 legality

- 实现提交：`64ceac14a0c2e0ef3e50592ad0dd04198633b5a9`；主线程审查修复提交：`bafb16b`。
- 初始任务红灯覆盖 Vista 列举、未知表情、本地昵称转换与 legality 字段；审查新增的固定内部哨兵碰撞和 `FallBackEmo` 字典读取问题先得到 `2 failed, 130 deselected`。
- 审查修复 GREEN：`python -m pytest tests/test_v13_contract_runtime.py -q -k "literal_internal_text or configured_emotion_sequence"` → `2 passed, 130 deselected`。
- 最终定向 runtime：`8 passed, 124 deselected`；静态 Vista/nickname/emotion/legality 契约：`4 passed, 114 deselected`。
- `python -m pytest tests/test_v13_contract_runtime.py -q`：`130 passed, 2 failed`；仅剩任务 8 负责的 `version_info` 与 `disable(status)` 红灯。
- `python -m pytest tests/test_start_maica_background_download.py -q`：`1 passed`；相关 Python 编译通过，只有 `maica.py:53` 既存 ASCII 图转义警告；`git diff --check` 通过。
- REST：列举改为 `GET /vista/list`，下载仍为 `GET /vista?content=...`；上传和删除路径未改。
- 表情与昵称：生产路径不再请求 `/emotion`；未知标签由本地 `FallBackEmo` 处理；`[player_nickname]` 在保留普通正文的同时转换为 `[mas_get_player_nickname()]`。
- legality：显示 `latitude/longitude`，兼容 `lat/lng/lon` 别名。
- 规格审查：通过；任务 5 的修复轨、退役轨和兼容边界均有测试映射。
- 最终质量审查：Approved，无 Critical/Important/Minor；审查发现的两个问题已按 TDD 修复并加入回归。
