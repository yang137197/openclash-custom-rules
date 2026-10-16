# 版本记录

## tiktok-router-loongproxy-jp-us v1.0.0 — 2026-10-16

状态：stable。用户确认 CatWrt/OpenClash 实机验收通过并授权正式发布。影响 J3/J4/J6/J8–J11；按用户总体确认记录验收，不补造逐项日志。

- 正式链路前提：TikTok 的 Loongproxy 美国 SOCKS5 必须经用户手选的 iKuuu 日本节点建立链式代理；不得改成美国或其他机场首跳，不得回退机场/DIRECT。
- 日本组自动纳入已加载的顶层节点与代理提供商中名称含 `jp`、`日本`、`Japan` 或 🇯🇵 的节点；实际首跳手选，缺节点时 REJECT。
- 稳定入口切换为 main 上的本方案；唯一当前维护方案为日本首跳链路。移除未发布的美国首跳 Loongproxy 候选，避免与强制链路前提冲突；Git 历史、已有标签和 Release 保留。
- 保留全部 129 条原始人工规则及 DOMAIN-SUFFIX 副本；云模块 inline 与源一致，只需刷新云模块并重启。真实 ISP 地址和凭据只放路由器本地节点模块。
- 更新正式部署文档，说明如何在本地 `TikTok-ISP-Local` 模块手动修改密码；公共仓库仅保留占位模板。
- 版本索引改为单一稳定方案，验证器覆盖 stable 状态、iKuuu 日本首跳合同、模块哈希、129 条规则、占位凭据、历史快照和本地链接。

## tiktok-router-isp-us v1.0.0 — 2026-10-15（已退役）

状态：candidate，C1–C11。历史候选使用机场美国首跳 → 路由器本地 Loongproxy SOCKS5，与当前强制 iKuuu 日本首跳前提不符，已按用户授权从当前文件树退役；历史提交保留。

- 完整云覆写只匹配精确本地节点 `TikTok-ISP-Local`，专用 DNS、专属组及紧邻 REJECT 保持失败关闭。
- Google/Play 先于中国分类走美国；私网、已知大陆域名/IP 和 Manual-Direct 直连。
- 从原始 129 条记录生成完整 DOMAIN-SUFFIX 副本并内嵌；真实代理地址与账号密码只在本地模块保存。

退役方案的旧版本记录可从原 Git 历史与标签核验。
