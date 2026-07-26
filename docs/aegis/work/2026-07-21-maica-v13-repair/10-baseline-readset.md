# 基线读取集

## 后端权威

- 仓库：<https://github.com/Mon1-innovation/MAICA>
- 提交：`8d2c44795dbe44a70dcb42a5870051912dae4f73`
- API 文档：<https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Documents.md>
- `maica/maica_utils/agent_tools.py`：MTrigger 名称、字符串、switch、meter schema。
- `maica/maica_utils/session_early.py`：affection/switch/meter/boolean 数量上限。
- `maica/maica_utils/ws_config.py`：`triggers` 字段、session 类型、10 条和 16 KiB 限制。
- `maica/maica_utils/setting_utils.py`：三个 `Literal[0, 1, 2]` 设置和 MSpire `ctg_weight`。
- `maica/maica_ws.py`：流式完成、MPostal 和 loop 状态。
- `maica/mtrigger/post_core_pipeliner.py`：质量状态。

## 本地运行代码

- `game/python-packages/maica_mtrigger.py`：模板、触发器序列化和触发响应。
- `game/Submods/MAICA_ChatSubmod/trigger.rpy`：内置触发器定义和回调。
- `game/python-packages/maica_tasker_sub_sessionsender.py`：WebSocket 请求封装和 session processor。
- `game/python-packages/maica_tasker_sub.py`：WebSocket 事件及 streaming packet validator。
- `game/python-packages/maica.py`：设置默认值、回调、昵称、MPostal 和版本状态。
- `game/python-packages/maica_vista_files_manager.py`：MVista REST 路由。
- `game/python-packages/emotion_analyze_v2.py`：消息表情解析和本地回退。
- `game/Submods/MAICA_ChatSubmod/migrations.rpy`：`1.8.0` 持久化迁移。
- `game/Submods/MAICA_ChatSubmod/header.rpy`：默认设置和 `mas_player_additions` 输入。
- `game/Submods/MAICA_ChatSubmod/screen_subs.rpy`：高级设置控件。
- `game/Submods/MAICA_ChatSubmod/api.rpy`：版本号、访问检查和旧回调调用点。
- `game/Submods/MAICA_ChatSubmod/dev_enable.rpy`：被 `.gitignore` 排除的本地开发覆盖。

## 当前验证基线

- 隔离 worktree 基于提交 `d1c08d2`，业务代码是干净的 `1.7.8` 基线。
- `python -m pytest tests -q`：干净基线 `1 passed`。
- 此基线尚无 `tests/test_backend_v13_compat.py`，严格 MT、事件名、MVista `/vista/list`、完成消息、三态设置和昵称占位符测试均需重新创建。
- 旧迁移改动保存在主仓库的 `stash@{0}`，只可用于审查对照，不得整体应用到隔离 worktree。
