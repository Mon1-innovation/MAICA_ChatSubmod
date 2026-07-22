# MAICA 后端 v1.3 前端兼容性修复设计

**状态：** 设计已确认，等待书面规格复核  
**日期：** 2026-07-21  
**目标前端版本：** `1.8.0`

## 任务意图

修复当前工作区与 MAICA 后端 v1.3 对照审查中确认的全部前端兼容性问题。修复后的前端必须在发送前拒绝非法数据，只使用当前网络契约，在不静默丢失用户内容的前提下迁移既有持久化数据，并通过行为测试覆盖实际协议，而不是仅搜索源码字符串。

工作范围包括协议缺陷修复、持久化数据迁移、废弃端点和状态名的定向退役，以及回归测试。不包括界面重设计或后端代码修改。

## 基线资料

- 上游后端提交 `8d2c44795dbe44a70dcb42a5870051912dae4f73` 是网络协议与数据验证的权威来源。
- 上游 `maica/maica_utils/agent_tools.py` 负责 MTrigger schema。
- 上游 `maica/maica_utils/session_early.py` 负责 MTrigger 数量上限。
- 上游 `maica/maica_utils/ws_config.py` 负责请求字段和 query 大小限制。
- 上游 `maica/maica_utils/setting_utils.py` 负责高级设置的类型和默认值。
- 上游 `maica/maica_ws.py` 与 `maica/mtrigger/post_core_pipeliner.py` 负责 WebSocket 状态和载荷。
- 上游 API 文档作为辅助说明。当文档写 `trigger`、后端模型写 `triggers` 时，以可执行的后端源码为准。
- 本地 `PowerToys_Paste_20260703220346_change_mapping.md` 记录 v1.2 到 v1.3 的预期迁移覆盖面，但不是协议权威。
- 本地源码与测试定义现有用户可见行为，除本规格明确退役的部分外均须保持稳定。

## 事实、假设与环境未知项

### 已知事实

- 当前已发布前端版本是 `1.7.8`；本次修复发布为 `1.8.0`。
- 现有迁移注册在 `1.8.0`，前端版本仍为 `1.7.8` 时不会执行。
- 现有测试能够通过，但部分请求无法通过后端 Pydantic 验证。
- 部署目标是 Ren'Py 及其内嵌 Python 环境。

### 设计假设

- 前端 `1.8.0` 面向后端 v1.3，不保留后端 v1.2 网络协议兼容性。
- 现有界面布局和正常聊天行为保持不变。
- 使用纯 Python 校验，不向 Ren'Py 包引入 Pydantic 依赖。

### 环境未知项

- 开发环境不一定安装 Ren'Py SDK。有可用可执行文件时，Ren'Py lint 是发布门槛；否则必须记录为剩余风险。
- 在线集成测试需要账号和运行中的后端。无论是否具备在线条件，确定性的模拟契约测试均为必选项。

## 影响范围

受影响层包括 Ren'Py 设置与触发器定义、Python 请求序列化、WebSocket 分发、持久化迁移、REST 路由、消息后处理和兼容性测试。兼容边界是现有存档及用户可见聊天流程。废弃的网络别名不属于兼容边界，将在本版本退役。

## 选定方案

采用集中契约适配。Python 模块负责规范化、严格校验和网络序列化；Ren'Py 只提供业务值并执行游戏动作，不重复维护后端字段名。测试直接固化后端 v1.3 契约。

未采用的方案：

- 分散替换字段虽然初始改动更少，但会保留本次协议漂移的根因。
- 将后端 Pydantic 模型复制到前端会增加运行时依赖，并产生第二个 schema 所有者。

## 组件职责

### MTrigger

- `game/python-packages/maica_mtrigger.py` 负责 MTrigger 模型规范化、校验、序列化和响应参数规范化。
- `game/Submods/MAICA_ChatSubmod/trigger.rpy` 只提供字符串选项与当前值，并消费已经规范化的内部动作参数。
- `game/python-packages/maica_tasker_sub_sessionsender.py` 将校验后的触发器放入顶层 `triggers` 请求字段。

### WebSocket 与请求处理

- `game/python-packages/maica_tasker_sub_sessionsender.py` 负责最终请求构造、MSpire 配置和原始上下文校验。
- `game/python-packages/maica_tasker_sub.py` 负责 v1.3 状态处理和流式数据包计数验证。
- `game/python-packages/maica.py` 负责回调、设置默认值、昵称占位符、可访问状态和废弃端点退役。

### 持久化与界面

- `game/Submods/MAICA_ChatSubmod/migrations.rpy` 负责幂等的 `1.8.0` 持久化数据迁移。
- `game/Submods/MAICA_ChatSubmod/header.rpy` 负责默认值和玩家补充信息校验。
- `game/Submods/MAICA_ChatSubmod/screen_subs.rpy` 使用 `mf_const_tools` 已采用的数值控件模式显示三态设置。

### REST

- `game/python-packages/maica_vista_files_manager.py` 负责 MVista 列举、上传、下载和删除路由。
- 删除废弃的表情 HTTP 回退；`emotion_analyze_v2.py` 对未知标签执行确定性的本地回退。

## 协议规则

### MTrigger 请求契约

- 临时触发器字段固定为 `triggers`，不再发送 `trigger`。
- 触发器名称必须匹配 `^[A-Za-z0-9_-]{1,64}$`。
- 双语条目名称的每个组成字符串最长 256 个字符。
- switch 的 `item_list` 只能包含长度为 1 至 256 个字符的字符串。
- switch 当前项序列化为 `curr_item`；只要值不是 `None` 就必须发送。
- switch 响应读取后端字段 `choice`。内部回调可以接收规范化值，但运行路径不得再读取网络字段 `selection`。
- meter 的 `value_limits` 必须恰好包含两个升序数值，当前值继续使用 `curr_value`。
- 触发器数量上限分别为：affection 1 个、switch 6 个、meter 6 个、customized/boolean 20 个。
- 现有“佩戴饰品”和“取下饰品”两个 switch 合并为一个饰品 switch。字符串选项在内部映射到佩戴或取下动作，在保留全部现有功能的同时把内置 switch 总数从 7 降为 6。
- 所有数量与 schema 校验必须在 WebSocket 发送前完成。

### Session 请求契约

- `0..9` session 接受 UTF-8 编码后不超过 4 KiB 的字符串 query。
- `-1` session 接受最多 10 条消息。列表使用 `ensure_ascii=False` 和分隔符 `(',', ':')` 序列化为紧凑 JSON 后不得超过 16 KiB；在受支持的消息数据范围内，该计数方式与后端 `orjson.dumps` 保持一致。
- MSpire 的 `ctg_weight` 必须是 `1..100` 的整数，默认值为 `10`。

### WebSocket 契约

- MPostal 从 `maica_core_streaming_continue` 接收内容；退役 `maica_core_nostream_reply`。
- 质量状态使用 `maica_quality_status`；退役 `maica_dscl_status`。
- 循环重置状态使用 `maica_loop_warn_reset`；退役 `maica_loop_warn_finished`。
- `maica_core_complete` 只从当前后端文本中提取报告的数据包数量，不再要求 tracker ID。
- 数据包计数器必须在正常完成、畸形完成包、数量不匹配处理、断开连接和显式任务重置后清零。

### REST 契约

- MVista 列举使用 `GET /vista/list`。
- MVista 下载继续使用 `GET /vista?content=<uuid>`。
- 不再调用 `/emotion`。未知或不受支持的表情标签使用现有本地回退选择器。

## 设置与迁移

只有在其余修复分片全部通过测试后，版本常量才更新为 `1.8.0`。迁移注册版本保持 `1.8.0`，并且迁移必须幂等。

对于 `mf_sf_access_impl`、`mf_const_sf_access` 和 `mt_concl_memory`：

- 新增或缺失的值默认为整数 `1`，与后端一致。
- 既有布尔值 `False` 迁移为整数 `0`，`True` 迁移为整数 `1`，保留此前界面展示给用户的状态。
- 既有整数 `0`、`1`、`2` 保持不变。
- 其他值重置为 `1`，并记录迁移警告。
- 界面控件使用现有 `0..2` 数值设置模式。

旧的已改名持久化键在 `1.8.0` 保留一版作为回滚数据，但运行时规范化、显示和上传只读取规范名称。后端不再接受的废弃参数无论是否存在回滚副本，都不得进入出站数据。后续版本在明确验证后可删除旧持久化副本。

规范化历史 `mas_player_additions` 前，迁移将完整副本保存到 `persistent._maica_v18_player_additions_backup`。活动列表最多保留 512 条，每条最长 1536 UTF-8 字节。非法项与溢出项留在备份中，不截断、不上传；通过 `persistent._maica_v18_player_additions_notice_seen` 保证只通知用户一次。重复执行迁移不得覆盖原始备份。

## 消息后处理

`prompt_allow_nickname` 继续按设置启用。表情与消息解析器将 `[player_nickname]` 识别为非表情占位符，并在 Ren'Py 插值前改写为 `[mas_get_player_nickname()]`。`[player]` 保持现有行为。删除 `/emotion` 后，占位符不得被当作未知表情标签，消息处理也不得依赖网络访问。

## 可访问状态与本地开发覆盖

`MaicaAi` 在初始化时将 `version_info` 设为失败形态的哨兵值，保证字段始终存在。`disable` 接受可选状态参数，同时保留现有无参数行为。被忽略的 `dev_enable.rpy` 在绕过 `accessable()` 时必须设置安全的 `version_info`。该辅助文件继续由 `.gitignore` 排除，不进入发布包。

## 错误处理

- 本地协议违规在网络 I/O 前抛出 `ValueError`；现有调用边界将预期的验证失败转换为简明用户提示。
- 用户输入错误应通知用户；程序错误继续记录带上下文的日志。
- WebSocket 畸形完成包处理必须记录载荷、标记验证失败、重置计数器，并进入现有的受控断连路径。
- 迁移不得删除玩家自定义内容的唯一副本。
- REST 错误沿用当前 manager 层报告行为；端点修复不得静默回退到废弃路由。

## 验证设计

### 自动化契约测试

- 断言精确的出站请求对象，不使用源码字符串搜索替代行为验证。
- 覆盖合法与非法的 MTrigger 名称、字符串、数量、switch 值、meter 范围和假值当前项。
- 覆盖原始上下文的消息数量与编码后大小边界。
- 覆盖 MSpire `ctg_weight` 的默认值、最小值、最大值、非整数和越界值。
- 重放当前后端 WebSocket 样例，覆盖流式响应、缓存完成包、MPostal、畸形完成包和跨轮计数清零。
- 模拟 REST 请求，断言准确的 MVista URL，并确认没有 `/emotion` 请求。
- 覆盖从 `1.7.8` 迁移、重复执行、三态转换、回滚键保留和玩家补充信息备份。
- 在无网络条件下覆盖 `[player]`、`[player_nickname]`、已知表情标签和未知表情标签。

### 静态检查与发布检查

- 运行项目全部测试。
- 编译发生修改的纯 Python 模块。
- 扫描运行文件中的废弃请求键、状态名和端点；测试与文档中用于证明退役的负向断言可以保留。
- 对本次修复涉及的文件执行 `git diff --check`，避免工作区中无关的既有换行问题干扰结果。
- 有 Ren'Py SDK 时执行 lint。

### 手工冒烟测试

- 使用 `1.7.8` 持久化存档副本升级，检查迁移日志、设置、备份数据和幂等性。
- 连接后进行正常聊天，验证连续两轮流式响应均能完成。
- 验证 MPostal、MSpire、全部内置 MTrigger 类别、MVista 列举与下载，以及 `-1 session`。
- 确认昵称输出能显示 MAS 昵称，且不会引发插值错误。
- 确认本地开发覆盖启动时不会出现缺失 `version_info` 的错误。

## 修复与退役双轨

### 修复轨

上述前端权威模块改为匹配后端 v1.3。每个修复分片先加入失败的回归测试，再实施最小修复并完成任务级验证。发布版本号在所有分片通过后最后修改。

### 退役轨

本版本停止在运行路径中使用 `trigger`、`selection`、switch `curr_value`、`maica_core_nostream_reply`、`maica_dscl_status`、`maica_loop_warn_finished`、旧 MVista 列举路由和 `/emotion`。旧持久化设置键只作为回滚数据保留，在后续版本验证 `1.8.0` 后再考虑删除。测试夹具仅可为证明旧名称被拒绝或不再出现在运行输出中而引用它们。

## 非目标

- 不修改后端仓库或上游 API 文档。
- 不重设计前端布局。
- 不向 Ren'Py 包引入 Pydantic。
- 不支持发送后端 v1.2 网络协议。
- 不对任务管理、日志或 provider 选择进行无关重构。

## 完成条件

- 每项已确认的审查发现都有对应自动化测试和明确的运行时修复所有者。
- 生产请求不再使用废弃字段、状态或端点。
- 既有存档能够迁移到 `1.8.0`，且不会静默丢失玩家自定义内容。
- 全部自动验证通过；无法执行的手工检查或 Ren'Py 检查必须明确记录为剩余风险。
