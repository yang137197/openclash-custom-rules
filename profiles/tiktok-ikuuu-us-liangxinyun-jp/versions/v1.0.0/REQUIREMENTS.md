# tiktok-ikuuu-us-liangxinyun-jp v1.0.0

状态为 candidate。直连和优先级基于 GitHub main 的 `f59e24c` 滚动配置。目标路由器、真实节点及订阅待验收。

- U1：TikTok 及其专用 DoH 通过原 Loongproxy 美国静态 SOCKS5 节点出站，`dialer-proxy` 固定到用户指定的现有 iKuuu 美国节点。原 `udp: false` 和紧邻的 TikTok 拒绝规则保留。首跳或落地不可用时，TikTok 失败关闭。
- U2：保留私网、手工直连、大陆域名和大陆 IP 的匹配条件、顺序及美国／TikTok 原有规则与直连之间的相对优先级。保留手工直连快照、直连 DNS、Fake-IP 判定和大陆旁路设置。
- U3：所有其余代理流量走 `良心云-日本`，包括原 Claude 专项端点、GitHub、Google／Google Play 和境外兜底。原绑定美国组的 Google 专用 DoH、`cn.mrs` 下载也使用该组。
- U4：唯一自定义策略组为 `良心云-日本`，仅引用良心云 provider 内经用户确认的日本高速节点白名单。路由器本地模块只保留两条 TikTok 出站及良心云 provider，替换旧配置继承的节点及 provider。日本组为空时拒绝，组内只允许在白名单中手选节点。
- U5：节点和订阅凭据只保存在路由器本地。路由器冷启动时良心云订阅由 DIRECT 下载，避免依赖尚未加载的良心云节点。现有直连及其他插件设置沿用已验收基线。

验收以 [SETUP.md](SETUP.md) 的实机项目为准。环境、路由器兼容性和性能结果记录在 [ENVIRONMENT.json](ENVIRONMENT.json)。
