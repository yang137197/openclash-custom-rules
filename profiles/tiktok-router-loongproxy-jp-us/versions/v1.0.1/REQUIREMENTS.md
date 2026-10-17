# tiktok-router-loongproxy-jp-us v1.0.1 — 候选需求合同

状态：**candidate，待实机验收**。本候选沿用 v1.0.0 的 J1–J11 与强制 iKuuu 日本首跳链路，只增加 J12。正式版 v1.0.0 及其标签保持不变。

## 需求

J1–J11 与 [`v1.0.0 正式需求合同`](../v1.0.0/REQUIREMENTS.md) 相同且继续有效。

- J12：精确域名 `update.kies.samsung.com` 使用 `DOMAIN,update.kies.samsung.com,DIRECT`，规则置于 Google/Play 规则之后、Manual-Direct 规则之前、`MATCH,美国` 之前。只匹配这个完整域名，不扩大到 `samsung.com`、其他 Samsung 域名或其子域名。其余分流、129 条 Manual-Direct 和日本首跳链路保持不变。

## 验收条件

- 新建连接到 `update.kies.samsung.com` 时，OpenClash/Mihomo 连接记录显示该精确规则并使用 `DIRECT`。
- 未匹配其他 Samsung 域名的流量；其他境外连接仍按现行规则使用用户手选的美国组。
- 完整配置通过仓库静态校验；实机验收与静态校验分别记录。当前日志仅证明该域名曾命中 `MATCH → 美国`，没有证明候选已加载或验收通过。
