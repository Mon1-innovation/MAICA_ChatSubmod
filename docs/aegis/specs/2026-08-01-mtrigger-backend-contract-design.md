# MTrigger 后端契约同步设计

日期：2026-08-01

## 目标

同步当前后端 MTrigger 请求与返回契约，修复新返回结构被旧映射解析器拆错的问题，并增加后端提供的记忆模板。变更必须继续使用现有 MTrigger 管理器作为触发器注册、构建、限额和运行的唯一所有者。

## 当前问题

- 后端返回 `{"name": "idle", "arguments": {}}`，前端却把 `name` 和 `arguments` 当作两个触发器名称。
- `common_affection_template` 仍允许调用方提供任意名称，而后端已将其名称固定。
- 前端尚无 `memory_writeback_template`，无法请求或消费 `write_memory` 输出。

## 契约

### 返回消息

`MTriggerWsHandler` 只接受以下 `content`：

```json
{
  "name": "idle",
  "arguments": {}
}
```

`name` 必须是字符串，`arguments` 必须是对象。旧式 `{"idle": {}}` 不再兼容；畸形 payload 记录错误且不调用触发函数。

### 固定名称模板

- `common_affection_template` 的本地固定名称为现有的 `alter_affection`。
- `memory_writeback_template` 的本地固定名称为 `write_memory`。
- 固定名称模板仍以本地名称参与管理器注册和返回路由，请求 payload 必须包含后端规定的固定 `name`。
- 其他模板继续要求并发送调用方提供的 `name`。

### 记忆模板

新增规范模板：

```json
{
  "template": "memory_writeback_template",
  "name": "write_memory"
}
```

模板的数据键为 `memory_item`，最多注册一个，默认作为 request 方法触发器提供给后端。

收到 `write_memory` 后，回调从 `arguments.memory_item` 取得文本，调用现有 `maica_validate_player_addition()` 完成类型、空值、重复、数量和 UTF-8 字节边界校验。校验成功后追加到 `persistent.mas_player_additions`；失败时不写入。

后端返回的 `{player_name}` 原样保存。此次不迁移、不重写历史 `mas_player_additions`，也不在前端替换该占位符。

## 所有权与数据流

1. `maica_mtrigger.py` 定义规范模板、固定名称、构建规则和每模板数量限制。
2. `trigger.rpy` 注册内置 `alter_affection` 与 `write_memory`，并拥有 Ren'Py 持久化回调。
3. `maica_tasker_sub.py` 只负责验证 WebSocket 返回 envelope 并转交 `(name, arguments)`。
4. `MTriggerManager` 根据固定本地名称找到触发器，现有运行队列负责执行回调。

WebSocket 层不得直接修改 `persistent.mas_player_additions`，避免协议处理与游戏状态持久化形成第二所有者。

## 错误处理

- 非对象 content、非字符串 name、非对象 arguments：记录错误并丢弃。
- 未注册 name：沿用管理器当前行为，不加入触发队列。
- 无效或重复 memory_item：由现有玩家补充信息校验入口拒绝。
- 回调异常：沿用 MTrigger 运行阶段的错误边界，不增加兼容兜底。

## 测试

- 新 envelope 恰好分发一次，空 arguments 可用。
- 旧映射 envelope 不再分发。
- 畸形 envelope 不分发。
- 两个固定名称模板拒绝其他名称，并在请求中发送固定 name。
- memory_writeback_template 请求严格等于 `{"template": "memory_writeback_template", "name": "write_memory"}`。
- memory_writeback_template 总数上限为一。
- write_memory 提取 memory_item，经现有校验后写入；重复项和非法项不写入。
- 完整 MTrigger 与 v13 契约回归通过。

## 兼容与退役

退役旧 MTrigger 返回映射解析逻辑，不保留 fallback。既有非固定名称模板、`maica_quality_status` 特殊路径和 `memory_concl_arc` 设置不在本次变更范围内。

## 工作草案

- TaskIntentDraft：同步后端 MTrigger envelope、固定名称规则与 memory_writeback_template；风险集中在请求契约和持久化写入。
- BaselineReadSetHint：`maica_mtrigger.py`、`maica_tasker_sub.py`、`trigger.rpy`、`header.rpy` 及两个 v13 契约测试文件。
- ImpactStatementDraft：影响协议适配、模板构建、触发器注册和玩家补充信息写入；不改变服务器、UI、历史数据或 memory_concl_arc。
