# 良心云分流 v1.0.0 候选需求

状态为 **candidate**。基线为正式方案 v1.0.7 在 Git 提交 `57ff42265dd3dffe44e86b7f78206b3d768f3d81` 的滚动覆写，取该提交已同步的 141 条手动直连。候选冻结这份验收快照。正式发布前以当时最新同步的手动直连源重新核对，使候选验收覆盖拟部署的规则。

- L1：经过 Mihomo 且命中 YouTube 域名集或 Telegram 域名/IP 集的流量走 `良心云`。YouTube 包含 `googlevideo.com`。Telegram IP 规则使用 `no-resolve`，在原私网、大陆 IP 和域名直连规则之后匹配。Google Play 专用规则先于良心云域名规则，通用 Google 规则继续走 `美国`。
- L2：`良心云` 手动选择其独立代理提供商的节点。节点加 `LXY: ` 前缀，`日本-入口` 和 `美国` 均排除该前缀。订阅为空时组回退 REJECT，无法承载的 UDP 由同一匹配条件的紧邻拒绝规则处理。订阅链接只保存在路由器的配套模块。
- L3：保留现行 TikTok 与 Claude/Anthropic 的静态 ISP 出口。Loongproxy SOCKS5 继续通过手选的 iKuuu 日本节点建立链式代理。保留 TikTok 相邻 REJECT 规则、原节点名、`udp: false` 及 `dialer-proxy: 日本-入口`。
- L4：保留已同步的 Manual-Direct 数据及所有现有规则的相对顺序。良心云域名规则跳过手动直连、大陆域名和大陆 IP；已有的私网规则先匹配。沿用现有 DNS、插件设置和公开／本地模块的凭据边界。

路由器验收涵盖 TikTok 播放与链路、局域网和手动／大陆直连、YouTube 视频媒体连接、Telegram 文件下载及 Google Play。记录良心云节点隔离和规则集加载状态。目标路由器与良心云真实订阅待实测。DNS 继续使用原解析策略，YouTube 与 Google 分类重叠时其专用 DNS 查询仍可经 `美国`。

本地 Mihomo v1.19.34 测试使用模拟节点和规则集缓存，验证 YouTube 媒体域名、Telegram 域名与 IP 的命中，良心云节点隔离、订阅不可用时的组行为，以及 TikTok、Google Play、手动直连和直连重叠用例的策略选择。路由器和应用播放验收仍待完成。

规则集来自 [MetaCubeX meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat)。分流基于核心可见域名和 IP，匹配范围随该上游数据更新。
