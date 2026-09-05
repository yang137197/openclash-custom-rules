# 验收记录

## 2026-09-05：单一美国策略组

- 配置仅定义一个 `美国` 策略组，类型为 `url-test`；它仅筛选并测速美国节点。
- `proxy-groups!` 强制替换订阅原有策略组，`rules!` 同时替换原有规则，避免已删除组被规则引用。
- `MATCH,美国` 覆盖全部非直连、非中国大陆流量，包含 AI。

部署验收：更新覆写订阅后应用配置并重启 OpenClash。策略组页面应只显示 `美国`；访问非大陆网站或 AI 服务时，日志应显示 `Match using 美国`。

## 2026-09-04：统一美国出口

- 覆写 YAML 段可由 PyYAML 正常解析。
- 当前仅定义 `美国`、`自动-美国` 两个策略组和 `Linyang-Manual-Direct` 一个规则提供者。
- `+rules` 顺序为私有/局域网直连、手工直连、中国大陆域名/IP直连、`MATCH,美国`。
- 旧设备、地区、Docker、TikTok、Google Play 规则文件已删除；规则提供者缓存路径改为 `linyang-v3-manual-direct.yaml`。
- `git diff --check` 通过。

部署验收：更新覆写订阅后应用配置并重启 OpenClash；非直连、非大陆连接的日志应显示 `Match using 美国`，手工直连和大陆连接应显示 `DIRECT`。
