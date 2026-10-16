# 版本记录

## tiktok-router-loongproxy-jp-us v1.0.0 — 日本首跳 + Loongproxy 美国 ISP — 2026-10-16

状态：candidate，未完成 CatWrt/OpenClash 手机验收。新增独立开发方案，不改写历史版本或稳定入口。

- `日本-入口` 组手选 iKuu 日本节点，本地 `TikTok-ISP-Local` 配置 `dialer-proxy: 日本-入口`，其他境外流量仍走美国组。
- 沿用中国大陆直连、Google/Play 美国优先、TikTok REJECT，以及现有 129 条 `DOMAIN-SUFFIX` Manual-Direct；云覆写通过 inline payload 提供完整手动规则，刷新该模块并重启即可应用。
- ISP 凭据仅存路由器本地；新增候选版本及校验约束，不以 PC 测试结果冒充路由器验收。

只记录形成版本的长期变化。临时命令、失败尝试和排查流水不写入本文件。

## tiktok-router-isp-us v1.0.0 — 云覆写 + 本地 TikTok ISP 节点 — 2026-10-15

状态：candidate，未完成 OpenClash 路由器与手机验收。用户明确弃用 IPRoyal 路由候选；旧 IPRoyal 版本目录和 beta 快照保留为历史材料，不再推荐测试。

- 新建独立方案：完整云覆写只匹配精确本地节点 `TikTok-ISP-Local`；本地 SOCKS5 节点通过用户手选的`美国`组链式拨号。TikTok 保留专用 DNS、专属组和紧随其后的 REJECT，禁止回退机场或 DIRECT。
- 其他境外流量继续走手选机场`美国`；中国大陆分类/IP、私网/局域网按当前 v2.0.0 基线直连；Google 与 Google Play 继续先于中国分类走`美国`。
- 复制完整 129 条人工直连规则到方案专属 `rules/manual-direct-isp.yaml`，将每条统一为 `DOMAIN-SUFFIX`；没有改写共享的 `rules/manual-direct.yaml`。完整云覆写通过 inline payload 同步这 129 条。
- 本地节点凭据仅保存在用户设备的本地模块，不进入仓库云覆写。静态结构不等于 LoongProxy 实际连通或 TikTok 可用；须手机验收后才能讨论稳定发布。

## tiktok-router-iproyal-us v1.0.2-beta.3 — Manual-Direct 随模块同步 — 2026-10-15

状态：candidate / beta；未完成真实 OpenClash 与手机验收。影响新增需求 P11；P1–P10 及 beta.2 历史快照保持不变。

- 将 `Manual-Direct` provider 从独立 HTTP 文件改为 `type: inline`，把仓库 129 条人工直连规则嵌入完整覆写模块。
- 增加方案专属滚动模块入口；后续更新规则时，仓库维护者在同一提交同步规则源和 inline payload，仓库校验检查一致性。用户更新时只刷新覆写订阅模块并重启，不再单独刷新 Rule Provider。
- Mihomo 文档支持 inline rule provider；目标 OpenClash/Mihomo 运行环境尚未实测，故仍为候选。

## Manual-Direct 共享规则数据修订 — 2026-10-15

类型：共享规则数据候选修订；不改动已发布覆写模块，也未进行路由器实机验收。影响 R4、H5、P5 所引用的共享人工直连数据。

- 新增 `DOMAIN-SUFFIX,alimama.com`，使 `one.alimama.com` 及该域名下的子域名命中 `Manual-Direct` 并走 `DIRECT`。
- 原有 124 条保留，当前共享数据共 125 条；目录中的 SHA-256 与数量已更新。
- 规则仍通过共享 `rules/manual-direct.yaml` 提供；本地改动尚未提交或推送，路由器不会从 GitHub `main` 自动获取本次本地版本。

## tiktok-router-iproyal-us v1.0.1 — 2026-10-15

状态：candidate；修订 P1 的 IPRoyal 拨号路径，新增 P10；P2–P9、完整分流模块正文、人工直连清单与已发布版本不变。

- 脱敏实机日志确认 TikTok 规则命中，但路由器直连 IPRoyal SOCKS5 端口反复 TCP 超时；尚不能断定具体网络阻断原因。
- 依据 IPRoyal 官方 Shadowrocket 双跳排障思路与 Mihomo `dialer-proxy` 文档，增加无凭据 `proxies*` 补丁，使现有本地 IPRoyal 节点经手选机场美国节点连接；TikTok 最终仍只用 IPRoyal，失败不回退机场或 DIRECT。
- 官方未给出 OpenClash 使用第三方机场的保证；本适配和第一跳端口可达性均待实机验收，不发布稳定版或移动兼容入口。

## Manual-Direct 与 tiktok-router-iproyal-us v1.0.2-beta.1 — 2026-10-15

状态：共享直连规则已授权更新；v1.0.2-beta.1 为 beta/candidate，尚未通过真实路由器和手机验收。影响共享人工直连数据及新 IPRoyal 候选 P5；已发布稳定覆写正文不变。

- 新增精确规则 `DOMAIN,d-gm.mmstat.com`，只匹配此主机，不扩展到 `mmstat.com` 的其他子域名。
- 保留 GitHub `main` 上已有的阿里妈妈精确规则，以及此前候选中的 `DOMAIN-SUFFIX,alimama.com`；当前共享数据共 129 条，目录中的 SHA-256 与数量同步更新。
- v1.0.2-beta.1 沿用 v1.0.1 的待验收机场美国首跳 → 本地 IPRoyal 链式拨号，只更新版本资料及直连规则数据，不改变其他分流行为；发布为 GitHub beta，不晋升稳定版。

## Manual-Direct 与 tiktok-router-iproyal-us v1.0.2-beta.2 — 2026-10-15

状态：共享直连规则扩展已授权；v1.0.2-beta.2 为 beta/candidate，尚未通过真实路由器和手机验收。影响共享人工直连数据及新 IPRoyal 候选 P5；已发布稳定覆写正文和 beta.1 快照不变。

- 将新增的 mmstat 直连项改为 `DOMAIN-SUFFIX,mmstat.com`，覆盖主域名和所有子域名，包括 `d-gm.mmstat.com`；人工规则总数仍为 129。
- `DOMAIN-SUFFIX,alimama.com` 已覆盖阿里妈妈主域名和其子域名；本次保留已有人工条目。
- 新增 v1.0.2-beta.2 目录和不可变标签计划；沿用 v1.0.1 链式拨号候选，不改变其他分流行为。beta.1 原发布内容保持不变。

## tiktok-router-iproyal-us v1.0.0 — 2026-10-15

状态：candidate；新独立方案，需求 P1–P9，尚未实机验收。

- 按最新授权改为所有手机经 OpenClash 本地 IPRoyal 使用 TikTok，手机无需 SocksTun；其他国外流量继续手选机场美国。
- TikTok 独立组只匹配顶层本地 `IPRoyal-US-ISP`；空组 REJECT，紧随同分类 REJECT 防止不支持 UDP 时继续匹配机场/直连；TikTok 专用 DoH 改走该组。
- 继承指南大陆旁路、Google/Play 例外与国内 DNS 基线；人工直连 124 条不改。
- 增加本地凭据追加模块的填写说明、具体插件设置、订阅更新检查和回退；地址与凭据不入库。
- 保留已发布 v2.0.0、按设备稳定版、历史标签和兼容入口；新架构须独立实机验收后方可发布。

## tiktok-sockstun-us v2.0.0 — 2026-10-15

状态：stable。2026-10-15，用户确认“候选版本已验证，可发布正式版”，据此记录验收通过并发布；未另行提供逐项日志。

版本类型：主版本架构重构；受影响需求 R3、R6、R8，新增 R11/R12，保留 R1/R2/R4/R5/R7。

- 按用户授权以 OpenClash 用户指南为技术基准，舍弃旧版关闭大陆绕过等设置对新候选的约束；
- 改为 Fake-IP 非 TUN＋大陆 IPv4 旁路，CN MRS 用于真实地址过滤与核心直连补充；
- Google/TikTok 在有序 Fake-IP 过滤中先于中国分类，避免正常域名连接提前旁路；Google 保留经美国的专用 DNS；
- 国内 Nameserver、独立节点/直连解析、显式清空 Fallback 并替换 DNS 策略，避免意外继承；
- 保留原有 124 条人工域名及出口语义，不叠加日本/按设备方案；
- 增加完整中文设置、成套回退和实机门禁；校验器区分本候选与日本候选；
- 旧稳定目录和标签不改写；catalog 当前稳定版本及兼容入口提升到 v2.0.0，正式标签 tiktok-sockstun-us-v2.0.0。配置正文与验收候选相同，仅移除头部 candidate 注释标识。用户确认可发布不等于已独立确认 App 卡顿根因。

## tiktok-hybrid-device-us v1.0.1 — 2026-09-27

状态：稳定

验证日期：2026-09-27

方案：`tiktok-hybrid-device-us`

需求：H1–H9

- H1 授权设备由 `192.168.100.248/32` 改为 `192.168.100.198/32`；
- `.248` 不再获得 TikTok 机场美国出口权限，继续由通用 TikTok `REJECT` 规则失败关闭；
- H2–H9、DNS、策略组、Google/Google Play、Manual-Direct、中国直连、局域网和中文界面设置保持 `v1.0.0` 行为；
- 旧稳定版 `v1.0.0`、标签 `tiktok-hybrid-device-us-v1.0.0`、其他方案及根目录兼容覆写均未修改。

2026-09-27 用户完成真实设备测试并确认正常，随后明确批准立即发布。稳定标签为 `tiktok-hybrid-device-us-v1.0.1`。

## tiktok-hybrid-device-us v1.0.0 — 2026-09-21

状态：稳定

验证日期：2026-09-22

方案：`tiktok-hybrid-device-us`

需求：H1–H9

- 新建独立方案，不修改稳定方案 `tiktok-sockstun-us v1.0.0`、其 `v1.1.0` 日本候选或兼容覆写入口；
- `192.168.100.248/32` 的 TikTok 通过现有机场`美国`策略组访问；
- 其他设备泄漏到 OpenClash 的可识别 TikTok 连接继续 `REJECT`，手机 SocksTun/IPRoyal 路径保留；
- TikTok DNS 改为经`美国`策略解析，以支持指定设备；其他设备可以获得解析结果，但连接权限仍由路由规则控制；
- Google/Google Play、中国直连、Manual-Direct、局域网直连和当前中文界面稳定设置保持不变；
- 本方案不包含尚未验收的日本策略组和人工日本规则。

2026-09-22 用户完成真实设备测试并确认正常，随后明确批准稳定发布。稳定标签为 `tiktok-hybrid-device-us-v1.0.0`；本方案不得与其他完整覆写叠加，根目录兼容覆写保持指向原 `currentProfile`。

## v1.1.0 — 2026-09-18

状态：候选，待真实 OpenClash 设备验收

方案：`tiktok-sockstun-us`

需求：R1–R10

在保持 v1.0.0 的 R1–R8 行为不变的基础上：

- 新增手选`日本`策略组，自动收录名称带日本、东京、大阪、JP、Japan 等标识的机场节点；
- 日本组没有匹配节点时回退 `REJECT`，且排除名称以 `IPRoyal-` 开头的节点；
- 新增 `rules/manual-japan.yaml` 和 `Manual-Japan` 规则集；
- `t27.cdn2020.com`、`hscangku.com`、`222.0cck.cc`、`51cg1.com`、`tx.doudou520.online`、`mts.hhjd.mobi` 优先走`日本`；
- 日本规则位于 Google/Google Play 之后、人工直连和中国规则之前；
- DNS、TikTok、Google、人工直连、最终美国出口和 OpenClash 中文界面设置均未修改。

本候选不更新当前稳定版本、兼容覆写入口或 Git 标签。

## v1.0.0 — 2026-09-17

状态：稳定

方案：`tiktok-sockstun-us`

需求：R1–R8

首次把当前已验证配置固化为正式版本：

- TikTok 只由手机 SocksTun 通过 IPRoyal ISP SOCKS5 代理，泄漏到 OpenClash 的 TikTok 被拒绝；
- 其他国外流量走用户手工选择的机场美国节点；
- 中国大陆、局域网和人工维护域名直连；
- Google 与 Google Play 使用一致的美国路由和 DNS，实际下载已恢复正常；
- Fake-IP（增强）模式由用户手工选择，不写入覆写的 `[General]`；
- “禁用 QUIC”不勾选后，淘宝实际刷新恢复正常；
- “绕过中国大陆 IPv4”保持不勾选；
- IPRoyal 入口 IPv4 `/32` 必须加入本地 IPv4 网络绕过列表；
- 保留 `rules/manual-direct.yaml` 作为持续维护的共享人工直连规则。

本版本来源于提交 `b65a814` 所代表的已验证行为；正式 `v1.0.0` 标签包含本次版本化目录、维护规范和自动校验文件。
