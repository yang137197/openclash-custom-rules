# tiktok-router-isp-us v1.0.0 — 候选需求合同

状态：candidate。仅完成配置静态整理，尚未在目标 OpenClash 路由器和手机上验收。此候选取代 IPRoyal 路由器候选作为当前开发方向；IPRoyal 历史文件仅归档。

## 需求

- C1：所有由 OpenClash 接管、且命中中国大陆域名分类的域名走 `DIRECT`；中国大陆 IP 走 `DIRECT`。
- C2：保留仓库原有 129 条人工直连域名；本方案单独保存其副本，并将每一条统一为 `DOMAIN-SUFFIX`，使条目域名及其子域名均命中 `Manual-Direct`。不改动其他方案共用的 `rules/manual-direct.yaml`。
- C3：所有手机中命中 Mihomo `GEOSITE,tiktok` 的流量只走本地 `TikTok-ISP-Local` SOCKS5 节点；本地节点必须经手选的 `美国` 策略组建立链式连接。
- C4：TikTok 不得回退机场、`DIRECT` 或其他节点。保留紧随 TikTok 代理规则后的 `GEOSITE,tiktok,REJECT`；本地节点缺失或未匹配时应失败关闭。
- C5：除 TikTok 外，所有其他境外流量走用户手选的 `美国` 策略组；`美国` 组不得包含 `TikTok-ISP-Local`，避免链式拨号递归。
- C6：Google 与 Google Play 规则先于中国大陆分类，并走 `美国`，维持现有下载路径。
- C7：私网与局域网直连。
- C8：云端完整覆写不含任何代理账号、密码或用户专属凭据；凭据只存在路由器本地 TikTok 节点模块。
- C9：`Manual-Direct` 使用 `type: inline`，其 129 条规则与 `rules/manual-direct-isp.yaml` 同步；用户只刷新完整云覆写模块并重启 OpenClash。
- C10：插件运行选项由用户在 OpenClash 中文界面手工设置；覆写文件只含 `[YAML]`，不写 UCI 或 `[General]`。
- C11：验收只在接入 OpenClash 的手机上进行，不使用 PC 作为流量验收设备；需验证 TikTok 播放、本地 ISP 命中、国内/境外分流及缺节点时失败关闭。

## 边界

本方案按域名类别路由，不保证未被 `GEOSITE,tiktok` 识别的域名、其他 VPN/移动网络/IPv6 绕行或 TikTok 服务端账号可用性。`dialer-proxy: 美国` 是 Mihomo 链式拨号配置；机场美国节点能否访问 LoongProxy 入口以及 TikTok 对该住宅/ISP 出口的实际可用性，必须在路由器上实测。
