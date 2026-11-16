# 良心云默认代理 v1.1.0 候选需求

状态为 **candidate**。沿用 [v1.0.0 候选](../v1.0.0/REQUIREMENTS.md)所基于的正式版同步快照 `57ff42265dd3dffe44e86b7f78206b3d768f3d81`。进入正式发布前重新核对当时已同步的手动直连规则。

- L5：TikTok 专用策略经原 iKuuu 日本首跳与 Loongproxy 美国 SOCKS5 出口。该链路仅承载 TikTok 规则和 TikTok 专用 DNS。日本入口排除良心云节点，沿用空组拒绝和 TikTok 紧邻拒绝规则。
- L6：Claude 网页和 Claude Code 及原相关域名归入常规分流。移除原 Claude 专用出口条目和只用于 YouTube、Telegram 的分类。所有未命中直连或 TikTok 专用规则的代理流量走良心云。Google、Google Play 和 GitHub 相关规则沿用原命中优先级，代理目标改为良心云。良心云组只选其订阅节点，空组拒绝。最终拒绝规则处理代理组跳过的流量；良心云故障时在同订阅内换节点。
- L7：沿用 141 条已同步手动直连快照、局域网及大陆直连条目和原规则相对顺序。保留 DNS 解析规则与 Fake-IP 顺序，将原普通美国组专用 DoH 和大陆域名规则集的下载出口改为良心云。保留现有大陆规则缓存路径，初次部署需确认加载成功。

实机验收依次检查 TikTok 播放和原链路、局域网／手动／大陆直连、Claude 网页及 Claude Code、YouTube、Telegram、GitHub、Google Play。检查良心云订阅失效时 TikTok 和直连仍可工作，普通代理连接失败且未回落到 iKuuu。目标路由器的环境和应用结果待记录。

本地 Mihomo v1.19.34 使用模拟订阅及预置大陆规则集缓存，确认 Claude、YouTube、Telegram、Google Play、GitHub 和普通目标的路由选择。模拟订阅不可用时，良心云组使用 REJECT，TikTok 和手动直连的策略选择仍按原规则执行。
