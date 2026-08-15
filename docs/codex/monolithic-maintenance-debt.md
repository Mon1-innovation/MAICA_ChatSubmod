# 单体文件维护债务

## 当前范围

MAICA 的主要运行逻辑仍集中在少数大型文件中：`maica.py`、`header.rpy`、`chat.rpy` 和 `screen_subs.rpy`。这些文件同时承担状态管理、网络调用、Ren'Py label/screen glue 和兼容逻辑，导致局部修复容易触及不相关流程。

## 本次处理边界

本次只修复已确认的行为问题，不拆分上述文件，以保持每个 commit 的主题明确。后续若进行拆分，应先按运行时边界、初始化顺序和测试覆盖建立独立迁移计划，并逐步验证桌面、Linux 和 Android 运行时。

## 后续检查重点

- 统一 HTTP helper 的返回契约和异常策略。
- 为 Ren'Py 初始化钩子、后台线程和持久化状态建立独立测试。
- 拆分前保留现有 label、screen、persistent key 和上游 MAS 调用契约。
