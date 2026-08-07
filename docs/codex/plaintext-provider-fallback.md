# 默认节点与普通连接 fallback 风险

## 位置

- `game/Submods/MAICA_ChatSubmod/header.rpy`：默认 `provider_id` 在 Windows 为 1，其他平台为 2。
- `game/Submods/MAICA_ChatSubmod/api.rpy`：Android 迁移、certifi 检测失败或 certifi 下载失败时将 `provider_id` 设为 2。
- `game/python-packages/maica_provider_manager.py`：节点列表提供 `wsInterface`/`httpInterface`，实际协议由节点数据决定。

## 原因与行为

部分设备无法读取根证书时，强制使用 TLS 连接会使 MAICA 完全不可用。为保留可用性，前端在这些条件下 fallback 到 provider 2；该节点在公开节点列表中可能使用普通 `ws://`/`http://` 接口。节点列表是远端动态数据，不能仅凭 provider ID 推断其当前传输安全性。

## 影响范围

- fallback 节点上的登录 token、聊天内容、MPostal/MVista 请求可能以明文传输，网络观察者可读取或篡改。
- fallback 不是证书修复成功的证明；用户应在节点设置中核对当前 `wsInterface`/`httpInterface`，并避免在不可信网络中使用。
- 该行为与 [`certificate-repair-risk.md`](certificate-repair-risk.md) 共享同一设备兼容性根因。

## 本次处理边界

本次不修改 provider 选择或证书相关代码，仅在公开 README 中说明该 fallback。后续若要收紧安全策略，应先提供设备信任根或用户明确确认机制，并单独评审可用性影响。
