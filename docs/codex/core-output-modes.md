# 核心模型输出模式

核心 WebSocket 输出统一由 `game/python-packages/maica_tasker_sub_sessionsender.py` 的 `SessionSenderAndReceiver.consume_core_output` 处理。处理器通过两个参数声明本轮行为：

- `core_input_mode`: 后端传输预期，`stream` 表示可接收多个分片，`complete` 表示请求要求完整输出（对应 `bypass_stream=True`）。
- `core_output_mode`: 前端交付方式，`incremental` 立即交付每个分片，`complete` 累计到 `maica_chat_loop_finished` 后一次性交付。

当前调用约定：

| 场景 | input | output | 目的 |
| --- | --- | --- | --- |
| 普通聊天 | `stream` | `incremental` | 保持实时分句和逐段显示 |
| MSpire | `stream` | `incremental` | 保持主题回复的实时显示 |
| raw session | `stream` | `incremental` | 保持实验接口的既有交互 |
| MPostal | `complete` | `complete` | 显式请求 `bypass_stream=True`，即使兼容后端分段也只在完成状态后写入一封完整回信 |

完成判断只使用 `status == "maica_chat_loop_finished"`，不读取 `maica_core_complete.content`。核心分片的 `content` 仅作为模型文本输入统一处理层；其他 WebSocket 状态仍按各自的结构化例外契约处理。
