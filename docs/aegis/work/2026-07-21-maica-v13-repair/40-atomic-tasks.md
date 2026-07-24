# 原子任务清单

按以下顺序执行；每个任务完成其测试和复核后再进入下一项。

- [x] 1. 添加 v1.3 运行时契约测试夹具和边界断言。
- [x] 1a. 为完整设置改名、认证 type、cookie 退役、断点续传和 MSpire 新结构添加失败测试。
- [x] 2. 修复 MTrigger `choice`、`curr_item`、`triggers` 和严格 schema 校验。
- [x] 3. 将佩戴/取下饰品合并为一个 switch，确保内置 switch 总数为 6。
- [x] 4. 修复 `-1 session` UTF-8/紧凑 JSON/10 条限制。
- [x] 5. 修复普通 session 4 KiB 和 MSpire `ctg_weight=1..100`。
- [x] 6. 统一 MPostal、质量、loop WebSocket 状态名。
- [x] 6a. 添加登录 `type: auth`、断点续传标记并删除 cookie/strict-mode 运行路径。
- [x] 7. 改造 `maica_core_complete` 解析并覆盖所有计数器重置路径。
- [ ] 8. 将 MVista 列举改为 `/vista/list`，保留下载路径。
- [ ] 9. 退役 `/emotion` 网络回退，增加本地未知表情回退。
- [ ] 10. 修复 `[player_nickname]` 到 MAS 函数的消息转换。
- [ ] 11. 将三个布尔高级设置改为整数三态和后端默认值。
- [ ] 11a. 重建全部 v1.3 设置改名、弃用参数、语言 auto、范围和资产引用。
- [ ] 12. 实现 `1.8.0` 幂等迁移、旧键回滚副本和 `mf_const_tools=3` 降级。
- [ ] 13. 备份并规范化历史 `mas_player_additions`，修复上传前 1000 字符限制。
- [ ] 14. 初始化 `version_info`、修复 `disable(status)`、修复本地 dev 覆盖。
- [ ] 15. 删除生产路径旧字段/状态/端点，并补齐退役扫描。
- [ ] 16. 运行全量测试、编译、diff 检查和 Ren'Py lint（若可用）。
- [ ] 17. 完成旧存档、聊天、MPostal、MSpire、MT、Vista、`-1 session` 和昵称手工冒烟。
- [ ] 18. 最后更新版本为 `1.8.0`，写入证据并交付。
