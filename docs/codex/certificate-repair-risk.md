# Certifi 修复流程风险记录

## 位置

- `game/Submods/MAICA_ChatSubmod/api.rpy`：`maica_download_certifi_files`（约 259-305 行）及其后台启动函数。
- `game/Submods/MAICA_ChatSubmod/api.rpy`：`start_maica` 对 `mas_can_import.certifi()` 的检测和触发逻辑。

## 原因

部分设备，尤其是某些 Ren'Py/Android 运行环境，Ren'Py 内置 Python 无法正确读取设备根证书或 MAS 提供的 certifi 包。没有可信根证书时，客户端无法同时做到“从网络获取修复材料”和“验证修复材料来源”这两个条件；因此不存在在当前运行环境内完全安全的自修复方案。

当前流程在证书异常时使用 `verify=False` 下载 Python 源码和 CA bundle，先尝试 GitHub raw，再 fallback 到明文 HTTP 镜像，并直接覆盖本地 `certifi` 文件。该流程属于兼容性兜底，不是可信供应链更新机制。

## 影响范围

- **供应链完整性**：TLS 验证被禁用，镜像或链路被篡改可能导致任意 Python 代码或证书内容写入游戏目录。
- **运行时稳定性**：下载到错误版本或截断文件会使后续 HTTPS、导入或启动失败。
- **凭据与隐私**：修复失败后可能继续切换到普通连接节点，风险见 [`plaintext-provider-fallback.md`](plaintext-provider-fallback.md)。
- **更新一致性**：文件来自 moving `master`/镜像，不与当前子模组版本绑定。

## 本次处理边界

按审核决定，本次只记录问题，不修改该流程、不替换下载源、不改变 `verify=False` 行为。任何后续整改都应先确定设备信任根、签名/哈希校验、原子替换和回滚方案，再单独评审。
