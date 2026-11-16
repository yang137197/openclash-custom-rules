# TikTok 日本首跳 v1.5.0 候选需求

状态为 **candidate**。按用户指定的日本首跳验收范围收窄 [v1.4.0](../v1.4.0/REQUIREMENTS.md) 的节点选择。

- L14：`TikTok首跳` 只允许手选 iKuuu 日本 Z01–Z04 IEPL，兼容 🇯🇵 前缀和无旗帜拼写。未手选或所选节点消失时使用 REJECT。TikTok 及专用 DNS 经 `TikTok测速`、`TikTok-ISP-Local` 和 Loongproxy 美国静态出口。其他代理流量继续走良心云，直连、现有本地模块及插件设置沿用既有配置。

2026-11-16 15:24 的 v1.4.0 日志记录 iKuuu 日本 Z04 和 `TikTok-ISP-Local` 的活动连接，作为本轮选定首跳范围的依据。验收 v1.5.0 时，手选日本 Z04，检查 TikTok 视频、直连样例和良心云默认代理，生成对应版本的调试日志。

本地使用 OpenClash v0.48.002 合并函数与 Mihomo v1.19.34 验证四条 iKuuu 日本节点从顶层或代理提供商进入组，手选 Z04 在重启后保留，节点消失时回到 REJECT。目标路由器上的 v1.5.0 播放与配置生效待验收。
