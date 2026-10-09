# Certifi 修复流程

MAICA 声明 `CertifiFixer` 为模组依赖，并在发布构建时获取它的最新 Release，
加入发布包的 `game/Submods/CertifiFixer/`；本仓库不保存其源码。其 `init -100` 脚本在 MAS
无法导入 `certifi` 时，将随包的 `core.py`、`__init__.py` 和 `cacert.pem` 复制到
`game/python-packages/certifi/`。文件在游戏启动阶段被直接覆盖，修复后可能需要
重启游戏，让 MAS 重新加载模块。

MAICA 在 `game/Submods/MAICA_ChatSubmod/api.rpy` 的 `start_maica()` 中重新调用
`store.mas_can_import.certifi()`；只有仍无法导入时才切换到 provider 2。MAICA
不再通过后台线程从网络下载修复文件。

迁移到 CertifiFixer 后，旧下载器中设置 `CERTIFI_RESTART_REQUIRED`（13418）的
唯一调用点已删除，相应状态码、提示和对白也已移除。该数值不再用于当前状态定义。
`CERTIFI_BROKEN`（13414）仍用于 MAICA 运行时检测：certifi 缺失、缺少 MAS 集成
接口，或本地 CA bundle / SSL 上下文不可用时仍会触发。随包提供证书并不替代这些检查。

随包文件需要与受支持的 MAS / Ren'Py Python 版本保持兼容。复制过程没有备份或
回滚；若依赖复制后导入仍失败，MAICA 会切换 provider 2。目标目录不可写等
未被 CertifiFixer 捕获的复制异常可能中断游戏初始化。
该节点的传输方式取决于远端节点列表，详见
[`plaintext-provider-fallback.md`](plaintext-provider-fallback.md)。
