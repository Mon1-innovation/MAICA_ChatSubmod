# 完整日志与隐私风险

## 位置

- `game/python-packages/maica_tasker_sub_sessionsender.py`：`start_request` 在 DEBUG 级别记录请求的位置参数和关键字参数，可能包含聊天内容、MPostal 正文、视觉引用、MTrigger 数据和会话号。
- `game/Submods/MAICA_ChatSubmod/main.rpy`：记录当前 MTrigger 表、逐段模型输出、完整回复、MPostal 标题和回复正文，以及触发后的动作数据。
- `game/Submods/MAICA_ChatSubmod/raw_session_example.rpy`：记录 raw-session 的逐段模型输出。
- `game/python-packages/maica.py`：记录设置请求、无法解析的服务端响应、响应处理失败时的原始消息，以及部分 HTTP 响应正文。
- `game/python-packages/maica_tasker_sub.py`：登录任务会记录 access token 的前 15 个字符；MTrigger 处理器会记录完整结构化 payload。
- `game/Submods/MAICA_ChatSubmod/header.rpy`：记录完整高级设置。

日志主要进入 MAS 的 `submod_log.log`，部分内容也会进入子模组控制台。实际保留周期、文件权限和用户分享方式由 MAS、Ren'Py 运行环境及用户操作共同决定。

## 原因与当前决定

该前端运行环境复杂，问题常与设备、Ren'Py 版本、网络节点、服务端状态、流式分片和用户设置组合有关。完整上下文对复现低频故障和跨设备排障具有现实价值。按本轮审核决定，暂不删减这些日志，也不改变现有日志等级。

## 影响范围

- 聊天、信件和 raw-session 内容可能包含用户主动提供的私密信息。
- MTrigger、设置、视觉引用和服务端响应可能间接暴露游戏状态、偏好、会话元数据及服务节点信息。
- token 前缀本身不是完整凭据，但会增加日志与账号或会话关联的可能性。
- 用户在论坛或 issue 中直接上传完整日志时，上述数据会离开本地设备。
- DEBUG 日志与异常 traceback 可能在未来新增字段后记录当前未预见的敏感数据。

## 后续处理建议

后续应单独设计日志分级和脱敏规范，至少覆盖凭据字段的强制遮盖、内容日志的显式开关、导出前自动清理、保留周期说明，以及面向用户的日志分享提示。实施前需确认哪些字段是远程排障的最小必要集合，并为兼容环境保留可临时启用的诊断模式。

## 本次处理边界

本次只记录风险，不修改日志调用、默认等级、输出位置或内容范围。
