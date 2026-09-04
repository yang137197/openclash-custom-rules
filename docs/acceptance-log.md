# 验收记录

## 2026-09-04：统一美国出口

- 覆写 YAML 段可由 PyYAML 正常解析。
- 当前仅定义 `美国`、`自动-美国` 两个策略组和 `Linyang-Manual-Direct` 一个规则提供者。
- `+rules` 顺序为私有/局域网直连、手工直连、中国大陆域名/IP直连、`MATCH,美国`。
- 旧设备、地区、Docker、TikTok、Google Play 规则文件已删除；规则提供者缓存路径改为 `linyang-v3-manual-direct.yaml`。
- `git diff --check` 通过。

部署验收：更新覆写订阅后应用配置并重启 OpenClash；非直连、非大陆连接的日志应显示 `Match using 美国`，手工直连和大陆连接应显示 `DIRECT`。
