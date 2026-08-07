# 已移除的可读 `content` 协议解析

## 依据

后端 API 文档（MAICA `1f59109a267eec1734d255bd8628e27eb283e859`）规定：WebSocket envelope 的 `content` 通常是供人类阅读的排障文本，客户端应优先根据 `status` 判断行为。核心模型分片、MTrigger payload、质量检查结果和登录用户字段是文档明确的可处理例外。

## 本次删除

| 功能 | 原位置 | 删除内容 | 影响 |
| --- | --- | --- | --- |
| 核心输出完成包数校验 | `game/python-packages/maica_tasker_sub.py` 的 `StreamingPacketValidator` | 删除从 `maica_core_complete.content` 提取用户名、包数、seed/traceray 尾缀的正则，以及包数不一致时断开 WebSocket、发送 `streaming_packet_mismatch` 的路径 | `maica_core_complete` 现在只作为状态通知使用，不再因可读文本格式变化而误断线 |
| 完成包数校验任务注册 | `game/python-packages/maica.py` 的 `MaicaAi.__init__` | 删除 `StreamingPacketValidator` 实例及其 `maica_core_complete` 监听注册 | 不再维护与后端排障文本耦合的 seq/packet tracker |
| 对应旧契约测试 | `tests/test_v13_contract_runtime.py` | 删除依赖上述正则、账户名和 packet count 的测试 | 测试改由核心输出模式和状态驱动行为覆盖 |

这里的“seq”是早期实现从人类可读完成文本间接得到的 packet 数量，不是后端当前协议提供的结构化序号。WebSocket 的顺序由传输层保证，因此前端不再自行验证该文本数字。

## 明确保留

- `maica_core_streaming_continue.content`：后端文档定义为模型输出分片，仍由统一核心输出处理层消费。
- `maica_mtrigger_trigger.content`：后端文档明确是机器可处理的 trigger payload。
- `maica_quality_status.content`：后端文档明确是 `[reasonable, confidence]` 结构。
- `maica_login_user/id/nickname.content`：后端在登录完成后直接发送对应字段，前端仍直接保存展示。
- `maica_connection_initiated.content`：文档规定其为中英双语欢迎语，前端保留 `|` 拆分并在异常时 fallback 原文。

后续新增 WebSocket 处理器应先登记其 `status` 和 `content` 类型；除上述例外外，不得从可读文本推断控制状态、身份或计数。
