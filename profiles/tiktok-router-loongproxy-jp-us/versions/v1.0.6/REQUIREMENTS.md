# tiktok-router-loongproxy-jp-us v1.0.6 — 候选需求合同

状态：**candidate，待用户在路由器实机验收**。本候选由用户明确要求按候选方式发布；这不改变仓库永久流程 A 对后续手动域名新增的默认方式。本候选继承正式稳定版 v1.0.5 的需求、出口、规则顺序和设置基线，只新增 J17。v1.0.5 及其已发布目录、标签、Release 和稳定滚动入口在候选验收前保持不变。

Loongproxy 美国 SOCKS5 仍必须经用户手选的 iKuuu 日本节点建立链式首跳。不得更换美国首跳或其他机场首跳，也不得在链路不可用时回退机场或 `DIRECT`。本候选不改 TikTok/Claude ISP、GitHub/Google、其他 Manual-Direct、DNS 或 OpenClash 插件设置。

## 需求

- J17：`huzhou.host` 主域名及其全部子域名必须直连。使用 `DOMAIN-SUFFIX,huzhou.host,DIRECT`，放在 Google 规则之后、Manual-Direct 与中国大陆规则之前。匹配范围包括 `huzhou.host`、`www.huzhou.host` 及多级子域名；不匹配仅包含相似字符串但不以 `.huzhou.host` 结尾的其他域名。该规则作用于所有经过 OpenClash 的客户端，不按端口或客户端区分。

## 验收条件

1. 静态检查确认 `rules/manual-direct.yaml` 中仅新增一条 `DOMAIN-SUFFIX,huzhou.host`，候选完整覆写中有且只有一条对应的 `DOMAIN-SUFFIX,huzhou.host,DIRECT`。
2. 路由器加载候选远程覆写并重启后，连接日志中访问 `huzhou.host` 主域名及至少一个子域名时均命中 DIRECT，而不再命中美国策略组。
3. 确认其他规则仍按 v1.0.5 行为匹配；稳定版固定快照与稳定滚动入口未被本候选分支改变。
4. 仓库静态验证与路由器实机验收分别记录。当前候选尚未加载，未提供本候选调试日志或验收结果；不得据此声称已修复实机连接。

## 版本边界

规则源文件 `rules/manual-direct.yaml` 是手动域名维护入口。`rules/manual-direct-isp.yaml` 及 v1.0.5 固定完整覆写是已发布历史快照，本候选不改写它们。候选验收通过后，才可由用户确认晋升并更新稳定滚动覆写入口。
