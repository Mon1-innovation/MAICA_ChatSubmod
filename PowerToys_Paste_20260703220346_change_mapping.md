# MAICA v1.3 更新清单对应关系

来源清单: `D:\Windows\Download\v1.2_to_v1.3.txt`

说明:
- “当前项目改动”按当前工作区相对 `HEAD` 的变更归类。
- 旧参数名仍会出现在兼容映射和兼容性测试输入中，这是为了迁移旧存档/旧后端参数，不属于运行路径继续使用旧名。

## 逐项对应

| 清单项 | 当前项目对应改动 | 状态 |
| --- | --- | --- |
| 数据结构验证普遍采用pydantic | 当前前端 diff 未见 pydantic 相关直接调用，判断为后端实现项。 | 未见直接对应 |
| 数据库交互普遍采用sqlalchemy | 当前前端 diff 未见 sqlalchemy 相关直接调用，判断为后端实现项。 | 未见直接对应 |
| 添加与RAG相关的支持 | 当前 diff 未见 RAG 相关新增文件或调用。 | 未见直接对应 |
| 更新会话管理到v2 | `game/python-packages/maica.py` 将 `SUPPORT_BACKEND` 提升到 `1.3.000`；新增 `normalize_chat_params` 统一 v1.3 参数；`game/Submods/MAICA_ChatSubmod/migrations.rpy` 增加 `1.8.0` 迁移。 | 已对应 |
| 添加MVista的native实现(需要核心模型支持vl) | 当前 diff 未见直接新增 MVista native 实现。现有 `api.rpy`/`maica.py` 中保留 Vista manager 相关已有路径，但不是本次 diff 新增。 | 未见直接对应 |
| 更改部分高级设置命名: | `header.rpy`、`screen_subs.rpy`、`main.rpy`、`maica.py`、`migrations.rpy`、`tl/*.rpy` 已更新运行路径名称；兼容映射保留旧名到新名。 | 已对应 |
| `sfe_aggressive -> prompt_pname_repl` | `screen_subs.rpy` UI 和 `header.rpy` 默认值使用 `prompt_pname_repl`；`maica.py`/`migrations.rpy` 保留迁移映射。 | 已对应 |
| `mf_aggressive -> mf_llm_concl` | `screen_subs.rpy` UI、提示文本和 `header.rpy` 默认值使用 `mf_llm_concl`；相关翻译同步。 | 已对应 |
| `tnd_aggressive -> mf_const_tools` | `screen_subs.rpy` UI 改为 `mf_const_tools`，范围改为 `0..2`；`maica.py` 将旧值 `3` 降为 `2`。 | 已对应 |
| `esc_aggressive -> esearch_llm_concl` | `header.rpy` 默认值、`screen_subs.rpy` UI、`maica.py` 默认参数和迁移映射已更新。 | 已对应 |
| `amt_aggressive -> mf_precheck_mt` | `header.rpy` 默认值、`screen_subs.rpy` UI、`maica.py` 默认参数和迁移映射已更新。 | 已对应 |
| `pre_additive -> mf_context_rnds` | `screen_subs.rpy` UI、`header.rpy` 默认值、`main.rpy` MSpire 继续对话临时参数已更新。 | 已对应 |
| `post_additive -> mt_context_rnds` | `screen_subs.rpy` UI、`header.rpy` 默认值、`maica.py` 默认参数和迁移映射已更新。 | 已对应 |
| `dscl_pvn -> gen_quality_chk` | `header.rpy` 常规设置键、`maica.py` 实例属性/发送参数、通知 screen 名称、触发调用、图片资产名均改为 `gen_quality_chk`；旧名只留兼容映射/测试。 | 已对应 |
| `pre_astp -> mf_disable_loop` | `screen_subs.rpy` UI、`header.rpy` 默认值、`maica.py` 默认参数和迁移映射已更新。 | 已对应 |
| `post_astp -> mt_disable_loop` | `screen_subs.rpy` UI、`header.rpy` 默认值、`maica.py` 默认参数和迁移映射已更新。 | 已对应 |
| `enforce_lang -> gen_enforce_lang` | `screen_subs.rpy` UI、`header.rpy` 默认值、`maica.py` 默认参数和迁移映射已更新。 | 已对应 |
| tz移动到常规设置 | `header.rpy` 常规设置中已有 `tz`，`maica.py` 发送 `tz`。 | 已对应 |
| 添加语言auto的支持 | `maica.py` 增加 `MaicaAiLang.auto`；`screen_subs.rpy` 语言选择增加 `auto | 自动`。 | 已对应 |
| 添加高级设置mf_sf_access_impl | `header.rpy` 默认值、`screen_subs.rpy` UI、`maica.py` 默认参数已加入。 | 已对应 |
| 添加高级设置mt_concl_memory | `header.rpy` 默认值、`screen_subs.rpy` UI、`maica.py` 默认参数已加入。 | 已对应 |
| 现在发送maica_mcore_gen_start标记断点续传介入 | `maica_tasker_sub.py` 的 `AutoResumeTasker` 监听 `maica_mcore_gen_start`/`maica_chat_loop_finished`，重连时根据标记请求续传。 | 已对应 |
| 弃用mas_sf_hcb | `maica.py`/`migrations.rpy` 的 `DEPRECATED_CHAT_PARAMS` 删除该参数；`json_exporter.py`/`persistent_filter.json` 上传白名单移除该字段；测试覆盖，并确认上一版误写的 `mas_hf_hcb` 不再出现。 | 已对应 |
| affection trigger的参数键改为alter_value | `maica_mtrigger.py` 模板 datakey 改为 `alter_value`，保留 `affection` fallback；`trigger.rpy` 内置 affection 触发改读 `alter_value`。 | 已对应 |
| 添加高级设置mf_const_sf_access | `header.rpy` 默认值、`screen_subs.rpy` UI、`maica.py` 默认参数已加入。 | 已对应 |
| mt_disable_loop默认变为True | `header.rpy`、`maica.py` 默认值为 `True`；`normalize_chat_params` 缺省补 `True`。 | 已对应 |
| traceray_id更名为tracker_id | `maica_tasker_sub.py` 日志/错误事件改为 `tracker_id`；解析器兼容 `traceray` 和 `tracker`。 | 已对应 |
| 弃用mf_const_tools == 3 | `screen_subs.rpy` UI 上限改为 `2`；`normalize_chat_params` 和迁移将 `3` 压到 `2`。 | 已对应 |
| 现在第三方serp注册采用标准数据模型 | 当前 diff 未见 serp 数据模型相关改动。 | 未见直接对应 |
| sf_extraction更名为savefile_access | `header.rpy` 设置键、`maica.py` 实例属性/发送参数、`test_maica.py` 均改为 `savefile_access`；旧名只留兼容映射/测试。 | 已对应 |
| 弃用mt_extraction | `maica.py` 发送参数不再包含 `mt_extraction`；兼容 normalize/migration 删除旧键；测试覆盖。 | 已对应 |
| max_length更名为session_len_limit, 上限改回28672 | `maica.py` 发送 `session_len_limit` 并限制到 `28672`；`header.rpy` UI 范围和运行迁移同步；测试覆盖。 | 已对应 |
| MPostal ic_prep更名为twk_super | `maica.py`/`migrations.rpy` 仅有兼容映射；当前 diff 未见 MPostal 运行路径直接使用 `twk_super`。 | 部分对应 |
| legality接口查询地址现在返回经纬度 | `screen_subs.rpy` 的地理位置验证成功消息显示 `latitude/longitude`，兼容 `lat/lng/lon`。 | 已对应 |
| 弃用websocket不传入type的自动类型推断 | `MAICALoginTasker` 登录包新增 `type: auth`；现有 query/params/reconn/ping/sping 均已有 `type`。 | 已对应 |
| MSpire添加参数ctg_weight | `MAICAMSpireProcessor` 分类请求内新增 `ctg_weight`。 | 已对应 |
| MSpire的use_cache参数变为条目内参数 | `MAICAMSpireProcessor` 不再发送顶层 `use_cache`，改为 `inspire.use_cache`。 | 已对应 |
| 整理mp部分配置为MSpire, MPostal通用高级配置 | 当前 diff 未见明确通用高级配置字段。 | 未见直接对应 |
| 弃用了ms, mp的简单模式. 对于ms, 现在传空字典{}以采用默认配置 | MSpire 无分类时发送 `inspire: {}`；MPostal 当前未见对应默认空字典路径。 | 部分对应 |
| websocket信息中的code现在是int | 当前前端 diff 未见对 websocket `code` 字段的字符串依赖。 | 未见需改 |
| 弃用了反劫持cookie, 纯自欺欺人来的 | 已删除 `MAICAWSCookiesHandler`、`WSCookiesTask` 注册、`strict_mode` 设置/UI、所有业务 websocket 请求里的 `cookie` 字段追加分支。 | 已对应 |
| maica_model_mvista等变为maica_feature_mvista等 | 当前 diff 未见 `maica_model_mvista` 旧名。 | 未见需改 |
| maica_loop_warn_continue变为maica_loop_warn_reset | 当前 diff 未见 `maica_loop_warn_continue` 旧名。 | 未见需改 |
| 应该还有更多状态码变了, 具体根据用的找吧 | 已按当前代码搜索旧明确状态名；未发现需要改的旧名。 | 已检查 |
| 非流式输出的状态码与流式输出统一 | 当前 diff 未见单独非流式状态码处理路径。 | 未见需改 |
| 添加高级参数prompt_allow_nickname | `header.rpy`、`screen_subs.rpy`、`maica.py` 已加入默认值/UI/默认参数。 | 已对应 |
| 现在连接初始化消息原生双语(用|分隔) | 当前前端主要显示服务端消息；未见本地需要拆分/拼接初始化消息的路径。 | 未见需改 |
| 长连接限长调整至64KB, query调整至4/16KB | 当前 diff 未见前端请求长度限制常量。 | 未见直接对应 |
| 短连接限长调整至1MB(MVista是32MB) | 当前 diff 未见前端短连接长度限制常量。 | 未见直接对应 |
| 添加按键取出账号级偏好功能 | 当前 diff 未见账号级偏好取出端点/UI。 | 未见直接对应 |
| 弃用账号级偏好的删除端点, 重置端点改为覆盖修改 | 当前 diff 未见账号级偏好删除端点调用。 | 未见需改 |
| 弃用处理表情端点, 其功能已由pprt覆盖 | 当前 diff 未见处理表情端点调用。 | 未见需改 |
| 拆分了mv图片列举和下载端点 | 当前 diff 未见 MV 图片列举/下载端点改动。 | 未见直接对应 |
| mas_player_additions扩容到最多512条, 每条最长1536字节 | `header.rpy` 新增共享校验，`screen_subs.rpy`/`chat.rpy` 输入入口改走校验并放宽输入长度。 | 已对应 |
| 弃用了mas_player_additions静默允许超长, 现在超长会拒绝 | `maica_upsert_player_addition()` 对超量/超长使用 `renpy.notify` 拒绝，不再静默追加。 | 已对应 |

## 当前变更文件归属

| 文件 | 对应清单项 |
| --- | --- |
| `game/Submods/MAICA_ChatSubmod/api.rpy` | 迁移逻辑从 `api.rpy` 移出，配合“更新会话管理到v2”和参数迁移。 |
| `game/Submods/MAICA_ChatSubmod/migrations.rpy` | v1.8.0 迁移、参数改名、弃用参数清理、`mf_const_tools == 3` 降级、`session_len_limit` 上限。 |
| `game/Submods/MAICA_ChatSubmod/persistent_filter.json` | 弃用 `mas_sf_hcb`，不再上传该账号级偏好字段。 |
| `game/Submods/MAICA_ChatSubmod/header.rpy` | 常规设置/高级设置新名、`prompt_allow_nickname`、`savefile_access`、`gen_quality_chk`、`tz`、`session_len_limit` 上限、旧常规键迁移、`mas_player_additions` 限制。 |
| `game/Submods/MAICA_ChatSubmod/main.rpy` | `pre_additive` 运行路径改为 `mf_context_rnds`。 |
| `game/Submods/MAICA_ChatSubmod/screen_subs.rpy` | 高级设置 UI 新名、新高级设置、`prompt_allow_nickname`、语言 auto、经纬度显示、`gen_quality_chk` 通知 screen、玩家补充信息输入限制。 |
| `game/Submods/MAICA_ChatSubmod/trigger.rpy` | `alter_value` 兼容、`gen_quality_chk` 通知引用名。 |
| `game/Submods/MAICA_ChatSubmod/trigger_labels.rpy` | `gen_quality_chk` 通知 screen 名。 |
| `game/Submods/MAICA_ChatSubmod/tl/header.rpy` | 翻译缓存同步新设置名，并删除 strict/cookie 旧文案。 |
| `game/Submods/MAICA_ChatSubmod/tl/screen_subs.rpy` | 翻译缓存同步 `mf_llm_concl` 文案。 |
| `game/mod_assets/console/dscl_pvn.png -> game/mod_assets/console/gen_quality_chk.png` | `dscl_pvn -> gen_quality_chk` 资产名同步。 |
| `game/python-packages/maica.py` | v1.3 参数发送、参数 normalize、默认值、新语言、`prompt_allow_nickname`、弃用参数清理、MSpire 设置透传。 |
| `game/python-packages/maica_mtrigger.py` | affection trigger 改为 `alter_value`，兼容旧 `affection`。 |
| `game/python-packages/maica_tasker_sub.py` | 断点续传标记、登录包 `type: auth`、反劫持 cookie 代码删除、`tracker_id` 更名和兼容解析。 |
| `game/python-packages/maica_tasker_sub_sessionsender.py` | MSpire `inspire` 对象结构、`ctg_weight`、条目内 `use_cache`、空字典默认模式。 |
| `game/python-packages/json_exporter.py` | 弃用 `mas_sf_hcb`，不再上传该账号级偏好字段。 |
| `game/python-packages/test_maica.py` | 示例/手动测试脚本改用 `savefile_access`；修正 `NothingEmoSelector.analyze()` 返回 `(emote, message)` 列表，匹配正式 `EmoSelector` 契约，避免在线聊天完成后组装回复时报参数缺失。 |
| `tests/test_backend_v13_compat.py` | v1.3 兼容性测试，覆盖参数改名、迁移注册、`tracker_id`、`alter_value`、断点续传标记、登录 type、MSpire 新结构、cookie 代码删除、`prompt_allow_nickname`、玩家补充信息限制。 |

## 旧名扫描结论

运行路径中已清除 `dscl_pvn`、`sf_extraction`、`pre_additive` 等旧参数名的直接使用。当前仍出现旧名的位置为:
- `maica.py` / `migrations.rpy` / `header.rpy` 的旧名到新名兼容映射。
- `tests/test_backend_v13_compat.py` 的旧参数输入和断言，用于验证迁移。
- 原始更新清单文件本身。
