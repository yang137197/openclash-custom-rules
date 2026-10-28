# tiktok-router-loongproxy-jp-us v1.0.6 — 正式需求合同

状态：**stable**。用户已确认候选验收通过并授权正式发布。v1.0.6 继承正式版 v1.0.5 的需求、出口、规则顺序和插件设置建议；v1.0.5 延续 v1.0.0 首发合同的 J1–J11 并实现 J13–J16。本版本只新增 J17。已发布的 v1.0.5 目录、标签与 Release 保持不变。

Loongproxy 美国 SOCKS5 仍必须通过用户手选的 iKuuu 日本节点建立链式首跳；不得换用美国首跳或其他机场首跳，也不得在链路不可用时回退机场或 `DIRECT`。本版本不改 TikTok/Claude ISP、GitHub/Google、其他 Manual-Direct、DNS 或 OpenClash 插件设置。

## 需求

- J17：`huzhou.host` 主域名及其全部子域名必须直连。使用 `DOMAIN-SUFFIX,huzhou.host,DIRECT`，放在 Google 规则之后、Manual-Direct 与中国大陆规则之前。匹配范围包括 `huzhou.host`、`www.huzhou.host` 及多级子域名；不匹配仅包含相似字符串但不以 `.huzhou.host` 结尾的其他域名。该规则作用于所有经过 OpenClash 的客户端，不按端口或客户端区分。

## 验收结果

1. 静态检查确认 `rules/manual-direct.yaml` 新增 `DOMAIN-SUFFIX,huzhou.host`，正式完整覆写中有且仅有一条对应的 `DOMAIN-SUFFIX,huzhou.host,DIRECT`。
2. 2026-10-28 的 OpenClash 调试日志显示运行配置含该规则，访问 `huzhou.host:4443` 命中 `DomainSuffix(huzhou.host)` 并走 `DIRECT`。用户确认候选验收通过；该用户确认覆盖主域名及子域名验收，附件日志本身未记录子域名连接。
3. 用户确认其他规则按 v1.0.5 行为保持；正式覆写保留原规则顺序与出口约束。仓库静态验证与路由器实机验收分别记录。

## 版本边界

`rules/manual-direct.yaml` 是手动域名维护入口。`rules/manual-direct-isp.yaml`、v1.0.5 固定完整覆写、标签及 Release 均未改写。后续仅手动新增直连域名仍按仓库流程 A 更新规则源及滚动覆写；大版本更新或重构按流程 B 创建更高候选、验收后发布。
