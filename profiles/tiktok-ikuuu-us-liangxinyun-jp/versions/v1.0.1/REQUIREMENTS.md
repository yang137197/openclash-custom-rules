# tiktok-ikuuu-us-liangxinyun-jp v1.0.1

状态为 candidate。直连和优先级基于 GitHub main 的 `57ff422` 滚动配置。目标路由器、真实节点及订阅待验收。

- U1：TikTok 及其专用 DoH 使用 `TikTok-ISP`，唯一成员为原 Loongproxy 美国静态 SOCKS5 出站。它通过 `TikTok-首跳` 拨号。保留 `udp: false`、紧邻的 TikTok 拒绝规则和专用链路。TikTok 故障时仅在美国首跳链路内处理。
- U2：保留私网、手工直连、大陆域名和大陆 IP 的匹配条件、顺序及美国／TikTok 原有规则与直连之间的相对优先级。保留手工直连快照、直连 DNS、Fake-IP 判定和大陆旁路设置。
- U3：所有其余代理流量走 `良心云-日本`，包括原 Claude 专项端点、GitHub、Google／Google Play 和境外兜底。原绑定美国组的 Google 专用 DoH、`cn.mrs` 下载也使用该组。
- U4：`良心云-日本` 只使用良心云日本节点白名单。另设可见的 `TikTok-首跳`、`TikTok-ISP` 两组。本地模块只载入 Z01、Z02 及 Loongproxy，替换继承的节点及 provider。各组空组拒绝。
- U5：节点和订阅凭据只保存在路由器本地。路由器冷启动时良心云订阅由 DIRECT 下载，避免依赖尚未加载的良心云节点。现有直连及其他插件设置沿用已验收基线。

- U6：`TikTok-首跳` 按 Z01、Z02 的优先顺序做健康检查，周期 60 秒，自动使用仍健康的美国节点。两个节点都健康时默认优先 Z01。`TikTok-ISP` 支持检测整个链路，周期 300 秒。健康检查检测代理到测试地址，真实 TikTok 可用性和既有连接的重连需要实机验证。

验收以 [SETUP.md](SETUP.md) 的实机项目为准。环境、路由器兼容性和性能结果记录在 [ENVIRONMENT.json](ENVIRONMENT.json)。
