# tiktok-router-iproyal-us v1.0.2-beta.3

状态：**candidate / beta**。版本类型：v1.0.2-beta.2 的规则提供者内联修订；真实设备验收未通过。

用户明确要求“所有手机 → OpenClash → IPRoyal → TikTok，手机无需 SocksTun”。技术基础为 OpenClash 用户指南；从已发布指南架构派生，原方案的 SocksTun 要求不适用于本方案。原稳定版本的验收不能转用为本版验收。

## 需求合同

| 编号 | 要求 |
| --- | --- |
| P1 | 所有受本路由器 OpenClash 接管的手机，可识别 TikTok 域名连接经 TikTok-ISP → 本地 IPRoyal-US-ISP；无需手机 SocksTun，不按来源 IP 限定 |
| P2 | TikTok 不回退机场或 DIRECT；本地节点缺失时组内为 REJECT，不支持的 UDP 由紧随的同分类 REJECT 收口 |
| P3 | 其他国外流量走手选机场美国节点；美国组排除 IPRoyal，空组拒绝 |
| P4 | 国内域名/IP 直连，采用指南 Fake-IP 非 TUN＋大陆 IPv4 旁路基线 |
| P5 | 保留共享 Manual-Direct 现有条目和阿里妈妈规则；使用 `DOMAIN-SUFFIX,mmstat.com` 覆盖主域名及其全部子域名；其他精确/后缀语义和局域网直连保持 |
| P6 | Google/Play 的 Fake-IP、美国 DNS 与美国路由优先级保持 |
| P7 | TikTok 优先 Fake-IP，专用 DoH 经 TikTok-ISP；删除旧 rcode 空响应策略；其他 DNS 职责沿用指南基线 |
| P8 | 只有 [YAML]，插件设置由用户手工执行；IPRoyal 地址、账号密码仅留路由器，不提交仓库 |
| P9 | 国内 App、Google Play、TikTok 及节点缺失验收通过前保持候选，不替换稳定入口或发布正式版 |
| P10 | 仅 IPRoyal 本地节点通过已手选的机场`美国`组拨号；TikTok 最终出口仍为 IPRoyal，其他域名分流、失败关闭及插件设置不变 |
| P11 | Manual-Direct 规则以内联 payload 随完整覆写模块一起订阅；刷新模块并重启后应用同一仓库最新规则，不要求单独刷新规则提供者；仓库校验保证内联规则与 rules/manual-direct.yaml 一致 |

IPRoyal 官方提供的是 Shadowrocket 的双跳排障步骤，不是 OpenClash 或第三方机场的官方推荐。本版使用 Mihomo `dialer-proxy` 将其连接思路适配到现有机场首跳，属于待实机验证的技术推断。补丁模块必须晚于本地节点模块合并；若节点不存在，补丁不得自行创建伪节点。

## 规则与边界

本候选将 Manual-Direct 改为 Mihomo type: inline 规则提供者，payload 与仓库共享规则文件保持一致。订阅模块应使用方案专属滚动入口；固定 beta 标签仅用于复现该 beta 快照。

路由顺序：局域网 → TikTok-ISP → TikTok REJECT → Google/Play 美国 → Manual-Direct → CN MRS → CN IP → 美国。Fake-IP 过滤中 TikTok/Google 位于 CN 真实地址规则之前，防止正常域名连接提前进入大陆旁路。

TikTok-ISP 只从配置顶层 proxies 精确筛选 `IPRoyal-US-ISP`，不引入机场 provider 或其他策略组。节点存在但连接失败时仍只尝试该节点；不支持 UDP 时，Mihomo 可能跳过该条代理规则，因此下一条同分类 REJECT 必须保留。禁用 QUIC 是客户端 TCP 降级基线，不代表 ISP 服务支持 UDP、直播或所有功能。

本方案按域名类别分流，不是手机应用级 VPN。未知 TikTok 域名、纯 IP/私有 DNS/HTTPDNS、未经过本路由器的 IPv6、移动数据或其他 VPN 不在域名保证范围。仅关闭 OpenClash IPv6 代理不等于关闭客户端 IPv6；验收网络必须确保手机没有其他出网路径。共享同一代理的并发及业务权限以购买套餐为准；不承诺账号风控、地区解锁或无限设备。

## 待实机验收

- [ ] 使用方案专属滚动 URL 刷新覆写模块并重启；运行配置中的 `Manual-Direct` 是 `type: inline`，没有 HTTP URL/path/interval，129 条 payload 与仓库规则逐条一致；不单独刷新 Rule Provider。
- [ ] 重启加载无未知字段、DNS 循环或 provider 错误；TikTok-ISP 只有 IPRoyal-US-ISP，美国组没有 IPRoyal。
- [ ] 手机停止 SocksTun/其他 VPN、关闭移动数据，使用路由器网关/DNS；至少两台手机分别及同时打开、刷新、播放 TikTok，连接记录均命中 TikTok-ISP，核对实际 IPRoyal 出口。
- [ ] 临时停用本地凭据模块或移除测试配置中的本地节点并重启，TikTok-ISP 变为 REJECT；新建 TikTok 连接失败，没有机场或 DIRECT；恢复节点并重启后恢复。不能只断开网络模拟“节点缺失”。
- [ ] UDP 不支持时命中紧随的 TikTok REJECT；不能落入美国。发现未知域名进入美国时记录域名和日志，候选不得发布。
- [ ] 国内常用 App 连续加载/刷新；人工直连和局域网服务正常；Google Play 完整下载，其他国外网站走所选机场美国。
- [ ] `one.alimama.com` 命中 `Manual-Direct` 并走 `DIRECT`，不再命中最终 `美国` 规则。
- [ ] `mmstat.com`、`d-gm.mmstat.com` 与另一个 `mmstat.com` 子域名均命中 `Manual-Direct` 并走 `DIRECT`。
- [ ] 更新一次机场订阅并重启，确认本地 IPRoyal 节点仍存在且路由正确；避免发布后订阅覆盖造成失效。

v1.0.0 的仓库/YAML/隔离回环夹具检查不能转作本版实机验收。已确认的实际故障是 IPRoyal 直连端口 TCP 超时；链式拨号能否改善仍待单机实测。
