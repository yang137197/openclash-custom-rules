# OpenClash 最小分流配置

## 需求基线（不得擅自改变）

以下内容是本仓库的需求合同。后续修复、调整或重构必须先核对这些需求；没有用户新的明确授权时，行为必须保持不变。

| 编号 | 需求 | 当前实现 | 不允许出现的回退 |
| --- | --- | --- | --- |
| R1 | TikTok 只由手机 SocksTun 通过 IPRoyal ISP 代理 | OpenClash 对 TikTok DNS 返回空结果，并拒绝可识别的 TikTok 连接 | TikTok 改走机场`美国`、直连或重新由 OpenClash 连接 IPRoyal |
| R2 | 除 TikTok 外的国外流量走机场美国节点 | 最终 `MATCH,美国`，`美国`组由用户手工选择节点 | 自动切换到其他国家、直连或把 IPRoyal 加入该组 |
| R3 | 中国大陆域名和 IP 直连 | `GEOSITE,cn,DIRECT`、`GEOIP,CN,DIRECT` | 中国流量无条件走机场 |
| R4 | 保留用户人工维护的额外直连域名 | `rules/manual-direct.yaml` 位于 TikTok/Google 专用规则之后、中国规则之前 | 删除、清空、改名、批量改写或用自动规则替代该文件 |
| R5 | 局域网和私有地址直连 | 私网 GeoSite、GeoIP 和 CIDR 规则位于最前 | 私网流量进入机场代理 |
| R6 | Google 与 Google Play 稳定走机场美国节点 | Google 路由和 DNS 位于中国规则之前；Play 下载域名有显式规则 | `services.googleapis.cn` 或 `xn--ngstr-lra8j.com` 被中国规则抢先直连 |
| R7 | 插件运行选项由用户在中文界面手工设置 | 覆写只包含 `[YAML]` | 在覆写中加入 `[General]` 或强制改变运行模式 |

仓库仅保留：

```text
README.md
overwrite/openclash-overwrite.conf
rules/manual-direct.yaml
```

## 当前稳定基线

- 运行配置基线：提交 `ab5e683`。
- 2026-09-17 已确认：OpenClash 能正常加载该覆写，Google Play 应用下载恢复正常，不再卡在 0%、31% 或 98%。
- Google Play 故障的已确认原因：旧规则把部分 Google 流量送往`美国`，同时把 `services.googleapis.cn` 和 `xn--ngstr-lra8j.com` 判为中国直连；后者解析到 `58.63.233.x`、`113.108.239.x` 后持续连接超时，破坏了同一次下载流程的出口一致性。
- 已验证修复：Google 分类和 `xn--ngstr-lra8j.com` 都优先走`美国`，并通过`美国`策略连接公共 DNS 解析。
- `nameserver-policy` 中 `geosite:google` 与 `+.xn--ngstr-lra8j.com` 必须是两个独立键。把两者写进同一个 `geosite:` 组合键，会导致 Mihomo 把普通域名当作 GeoSite 列表名并报 `list +.xn--ngstr-lra8j.com not found in GeoSite.dat`，OpenClash 无法启动。

“稳定基线”表示上述行为已经在当前环境验证，不代表任何未来改动可以跳过复核。后续以仓库当前配置为起点，不重新假设需求，也不恢复已废弃的旧方案。

## 变更规则

任何后续修改都必须遵守：

1. 修改前先阅读本节需求基线和当前生效的 `overwrite/openclash-overwrite.conf`，列出受影响的需求编号。
2. 未涉及的需求必须保持行为等价；不能为了修复一个服务而改变 TikTok、国内直连、人工直连或其他国外流量的出口。
3. 调整规则顺序、DNS、运行模式、TikTok 出口、`美国`组或删除 `manual-direct.yaml`，都必须先说明影响并取得用户明确同意。
4. 优先最小改动；不得顺带恢复旧的测试设置、完整覆写、TUN、GSO、TCP 并发或其他没有当前证据支持的选项。
5. 配置提交前至少完成 YAML 解析、DNS 策略键检查和差异检查；配置只有在 OpenClash 实际加载成功并完成下面的应用验收后，才能标记为稳定。
6. 重构必须保持 R1–R7 全部成立，并逐项完成回归检查；不能以“结构更简单”为理由改变已有行为。
7. 新的稳定结论写回本 README，注明验证日期、对应配置和验证结果；只记录长期有效的结论，不保存冗长排查日志。

## 分工边界

- 每台需要使用 TikTok 的手机：安装并持续运行 SocksTun，只选择 TikTok 应用，并把该应用全部流量送入 IPRoyal SOCKS5。
- OpenClash：不再配置、选择或测速 IPRoyal；只处理中国直连、其他国外流量走`美国`，并拒绝泄漏出来的 TikTok。
- IPRoyal 服务器 IP：在 OpenClash 的“本地 IPv4 网络绕过列表”中手工直连，避免手机到 SOCKS5 入口的外层连接再次被 OpenClash 送入机场。

路由器只能看到连接目标，不能识别 Android 应用包名。因此“只代理 TikTok”的主约束必须由 SocksTun 的应用列表实现；OpenClash 的 TikTok 拒绝规则是防泄漏措施。

### 唯一允许的 TikTok 路径

```text
TikTok 应用 → 手机 SocksTun → IPRoyal SOCKS5 → TikTok
```

本方案不提供以下例外：

- 不允许任何设备的 TikTok 使用机场`美国`策略组；
- 不允许 TikTok 直连；
- 不允许 OpenClash 代替手机连接 IPRoyal；
- 不建立“允许部分设备的 TikTok 走机场”的设备白名单。

没有安装、没有启动或没有正确接管 TikTok 的 SocksTun 设备，应当无法访问 TikTok。这是设计目标，不是故障。

## TikTok 稳定使用建议

如需长期使用 TikTok，建议购买 IPRoyal 或其他正规服务商提供的**专用、静态 ISP 代理**，并选择符合实际使用地区的节点。本仓库当前按美国 ISP 使用场景编写。

不建议把机场订阅节点作为 TikTok 出口。机场节点通常不能保证出口 IP 专用、长期不变或具备 ISP/住宅网络属性，也可能存在多人共享、地区变化或线路切换。上述情况会降低网络身份的一致性，并可能增加登录验证、地区异常或平台风控的概率。

这里的建议只用于提高出口一致性，不代表任何 ISP 代理都能避免平台风控。TikTok 的具体风控规则并未公开，账号状态、设备环境和使用行为等因素也可能产生影响。

选择代理服务时建议确认：

- 产品类型明确为静态 ISP / 静态住宅代理，而不是轮换住宅代理或共享数据中心代理；
- IP 为专用或独享，并能在订阅周期内保持不变；
- 支持 `SOCKS5`，并明确支持手机代理工具所需的 TCP/UDP；
- 国家和地区固定，不在日常使用中频繁更换；
- 服务商能够提供清晰的服务器、端口、认证方式和有效期信息。

IPRoyal 是可选服务商之一，不是本仓库的依赖或保证。其官方资料将 ISP 代理描述为静态住宅代理，并提供专用 IP 与 SOCKS5 支持；其他服务商只要满足以上条件，也可以替换。

### 固定操作步骤

1. 购买并固定一个符合目标地区的专用静态 ISP IP；同一台设备日常使用同一个出口，不频繁切换 IP、国家或代理协议。
2. 在手机安装 SocksTun 或其他支持 Android 每应用 VPN 与 SOCKS5 的可信工具。
3. 在工具中填写 ISP 代理的服务器、SOCKS5 端口、用户名和密码；IPRoyal 当前使用 SOCKS5，不使用 HTTP 入口。凭据只保存在手机，不提交到仓库、聊天、日志或截图。
4. 代理范围选择“仅允许所选应用”，并且只选择 TikTok。不要选择“所有应用”。
5. 保持工具规定的 DNS 设置；本方案中 SocksTun 的 `DNS IPv4` 保持默认 `8.8.8.8`。
6. 允许代理工具后台运行，在手机电池管理中设为“不受限制”，并避免同时运行其他 VPN 或全局代理工具。
7. 将 ISP 代理服务器 IPv4 的 `/32` 地址加入 OpenClash“本地 IPv4 网络绕过列表”，防止手机到代理入口的连接再次进入机场代理。
8. 删除 OpenClash 中旧的 IPRoyal 节点和本地 IPRoyal 覆写模块；OpenClash 只负责阻断 TikTok 泄漏。
9. 每次先确认 SocksTun 已连接，再打开 TikTok。Wi-Fi、移动数据或网络发生切换后，先确认 SocksTun 已重新连接。
10. 如果 SocksTun 断开，先退出 TikTok，恢复代理连接后再重新打开；不要让 TikTok 在无代理状态下继续重试。

### SocksTun 建议设置

| 设置项 | 建议值 | 说明 |
| --- | --- | --- |
| `UDP relay over TCP` | 关闭 | 这是 Hev 服务端使用的 UDP-over-TCP 扩展；IPRoyal 只明确支持标准 SOCKS5 TCP/UDP，没有确认支持该扩展 |
| `Remote DNS` | 开启 | 让所选应用的 DNS 随 SocksTun 处理，减少 DNS 旁路 |
| `DNS IPv4` | `8.8.8.8` | 保持 SocksTun 默认值；当前版本不支持修改时无需处理 |
| `IPv4` | 开启 | 当前 IPRoyal 与 OpenClash 方案均以 IPv4 为基线 |
| `IPv6` | 关闭 | 避免 TikTok 通过未纳入代理的 IPv6 旁路 |
| `Global` | 关闭 | 不代理整台手机，只使用按应用代理 |
| `Apps` | 只选择 TikTok | 其他应用继续使用手机原有网络和 OpenClash 分流 |

关闭 `UDP relay over TCP` 后使用标准 SOCKS5 UDP 转发。只有代理服务商明确确认兼容 Hev UDP-in-TCP 扩展时，才考虑开启；不要把它作为普通的“启用 UDP”开关。

## 为什么选择 Meta

OpenClash 中的 `Meta` 是 Mihomo 核心。本配置需要它提供的：

- `GEOSITE,tiktok`、`GEOSITE,cn` 和 `GEOIP,CN` 规则；
- DNS `nameserver-policy` 及 `rcode://success` 空响应，用于阻断泄漏的 TikTok DNS；
- 按名称筛选机场美国节点的 `include-all`、`filter`；
- 策略组为空时使用 `empty-fallback: REJECT`，避免错误回退。

这里不使用 Smart。`美国`由用户手工选择机场节点，不自动切换；OpenClash 中不再存在 `TikTok-ISP` 策略组。

## OpenClash 中文界面建议配置

远程覆写只包含 `[YAML]`，以下插件选项全部在中文界面手工设置。

### 基础设置

| 中文设置项 | 建议值 | 说明 |
| --- | --- | --- |
| 运行内核 | Meta | 支持本配置使用的 GeoSite、DNS 策略和策略组过滤 |
| 运行模式 | Fake-IP（增强）模式 | 手动选择；不使用 TUN 或 TUN 混合模式 |
| 代理模式 | 规则模式 | 严格按规则顺序选择出口 |
| 路由器本机代理 | 开启 | 让路由器自身受管流量也按规则处理 |
| UDP 代理 | 开启 | 保留机场节点和其他国外应用的 UDP 能力；TikTok 由手机 SocksTun 处理 |
| 禁用 QUIC | 保持 OpenClash 默认（开启） | 与手机 SocksTun 能否连接 IPRoyal 无关；只控制是否阻断 UDP/443 |
| IPv6 代理 | 关闭 | 避免未纳入规则的 IPv6 旁路 |
| IPv6 DNS | 关闭 | 与 IPv4 分流保持一致 |
| 域名嗅探 | 开启 | 识别泄漏到 OpenClash 的 TikTok 域名 |
| 纯 IP 连接嗅探 | 开启 | 尽量识别目标信息不完整的连接 |
| 进程查找模式 | 关闭 | 路由器无法依靠进程名识别手机应用 |

### “禁用 QUIC”开关说明

这是一个双重否定开关：

- **开启“禁用 QUIC”**：OpenClash 在防火墙层拒绝适用范围内的 UDP/443，阻止应用使用 QUIC。
- **关闭“禁用 QUIC”**：不添加这项 UDP/443 阻断，允许 QUIC 和其他使用 UDP/443 的连接通过。

QUIC 是基于 UDP 的加密传输协议，常用于降低连接建立延迟并支持网络路径切换。OpenClash 提供这个开关，主要用于强制支持回退的应用改用 TCP，或者规避特定网络、代理节点不支持 UDP/QUIC 的情况；它不是普通的代理总开关。

OpenClash 当前官方默认开启“禁用 QUIC”。本仓库不在远程覆写中强制修改该开关；普通情况下保持默认即可。只有在代理节点完整支持 UDP，并且其他应用确实需要 QUIC 时，才按实际需求关闭。

手机 SocksTun 曾出现“开启 OpenClash 后连接 IPRoyal 超时、关闭 OpenClash 后正常”的现象，现已确认原因是 IPRoyal 服务器 IP 没有加入“本地 IPv4 网络绕过列表”，与“禁用 QUIC”开启或关闭无关。不要通过切换 QUIC 开关解决 IPRoyal 入口连接问题。

“禁用 QUIC”和 SocksTun 的 `UDP relay over TCP` 是两个不同功能：前者是 OpenClash 对 UDP/443 的防火墙阻断，后者是 SocksTun 与兼容 Hev 服务端之间的非标准 UDP-over-TCP 封装。IPRoyal 没有确认支持后者，因此 SocksTun 的 `UDP relay over TCP` 仍保持关闭。

### 防火墙与分流设置

| 中文设置项 | 建议值 | 说明 |
| --- | --- | --- |
| 仅允许内网访问 | 开启 | 不向外网开放 OpenClash 代理端口 |
| 旁路网关兼容模式 | 关闭 | 当前规则不需要额外兼容处理 |
| 绕过常用端口 | 关闭 | 避免 80、443 等流量跳过规则判断 |
| 绕过中国大陆 IPv4 | 关闭 | 国内流量进入核心后由中国规则直连 |
| 绕过中国大陆 IPv6 | 关闭 | IPv6 已关闭 |
| 中国大陆 IP 列表自动更新 | 关闭 | 中国大陆防火墙绕过已关闭，该列表不参与当前分流 |
| 仅代理命中规则流量 | 关闭 | 其他国外流量必须进入最终`美国`策略 |
| OpenClash 本地自定义规则 | 关闭 | 避免旧规则改变本仓库的规则顺序 |
| 绕过代理服务器地址 | 开启 | 机场服务器连接直接建立，避免重复代理 |

“OpenClash 本地自定义规则”关闭不影响下面的“本地 IPv4 网络绕过列表”；两者不是同一个功能。

### IPRoyal 入口直连

进入“插件设置 → 流量控制”，在“本地 IPv4 网络绕过列表”末尾增加一行：

```text
IPRoyal面板显示的服务器IPv4/32
```

例如服务器是 `203.0.113.10`，写成 `203.0.113.10/32`。不要把真实 IPRoyal 地址提交到公开仓库。

这是当前方案的必要条件，不是可选优化。由于 IPRoyal 已不再作为 OpenClash 节点存在，“绕过代理服务器地址”不会自动识别手机 SocksTun 使用的 IPRoyal 入口；必须在此处显式填写。

该列表只让手机到 IPRoyal SOCKS5 入口的外层连接绕过 OpenClash，不会把手机的普通流量整体直连。如果遗漏，外层连接可能被 OpenClash 再次接管并送入机场，表现为开启 OpenClash 时 SocksTun 连接超时、关闭 OpenClash 后恢复。修改后保存并重启 OpenClash。

删除或停用原来的本地 IPRoyal 覆写模块；OpenClash 中不应再保留带账号密码的 `IPRoyal-US-ISP` 节点，也不应手工选择它。

### DNS 设置

| 中文设置项 | 建议值 | 说明 |
| --- | --- | --- |
| 自定义 DNS | 开启 | 使用覆写中定义的国内、美国及 TikTok 泄漏阻断策略 |
| DNS 重定向 | 开启，选择 Dnsmasq 转发 | 接管局域网常规 DNS 请求 |
| 遵循分流规则 | 开启 | DNS 连接遵循目标流量策略 |
| 自动追加默认 DNS | 关闭 | 避免额外 DNS 混入配置 |
| 追加上游分配 DNS | 关闭 | 避免运营商 DNS 改变解析路径 |
| Fake-IP 持久化缓存 | 开启 | 减少重启后重复建立映射 |
| Fake-IP 过滤 | 开启，黑名单模式 | 保留局域网和自建服务域名的真实 IP 解析 |

泄漏到 OpenClash 的 TikTok DNS 使用 `rcode://success` 返回空结果；SocksTun 内部的 TikTok DNS 应随手机 VPN 处理，不经过此规则。

Google 分类和 Google Play 下载域名 `xn--ngstr-lra8j.com` 使用经`美国`策略连接的公共 DNS。该策略必须位于中国 DNS 策略之前，避免 `googleapis.cn` 等 Google 域名先命中中国分类并返回当前网络无法直连的中国 CDN 地址。

### Google Play 稳定规则

Google Play 不是一条连接完成全部下载。商店接口、图片和安装包下载可能使用不同 Google 域名；这些域名如果一部分走`美国`、另一部分直连，可能出现页面正常但下载卡住。

当前稳定配置必须同时满足：

```yaml
dns:
  nameserver-policy:
    '+.xn--ngstr-lra8j.com':
      - 'https://1.1.1.1/dns-query#美国'
      - 'https://8.8.8.8/dns-query#美国'
    'geosite:google':
      - 'https://1.1.1.1/dns-query#美国'
      - 'https://8.8.8.8/dns-query#美国'
    'geosite:cn,private':
      - https://223.5.5.5/dns-query
      - https://1.12.12.12/dns-query

rules:
  - DOMAIN-SUFFIX,xn--ngstr-lra8j.com,美国
  - GEOSITE,google,美国
  - RULE-SET,Manual-Direct,DIRECT
  - GEOSITE,cn,DIRECT
  - GEOIP,CN,DIRECT,no-resolve
  - MATCH,美国
```

这里展示的是生效顺序；覆写文件中的实际键名是 `rules!`。不得把 Google 两条路由移动到 `Manual-Direct` 或中国规则之后，也不得把两个 DNS 匹配器合并成一个 `geosite:` 键。

如果以后需要改变 Google 的出口，必须先重新确认以下三项：

1. `services.googleapis.cn`、`xn--ngstr-lra8j.com` 和其他 Google 下载域名采用同一条可用出口；
2. DNS 解析路径与流量出口一致；
3. 使用真实 Google Play 应用下载完成测试，不能只以商店页面能够打开作为验收。

### 更新和高级设置

| 中文设置项 | 建议值 | 说明 |
| --- | --- | --- |
| GeoIP 数据库 | 开启 | 中国 IP 直连规则需要 |
| GeoIP 自动更新 | 开启 | 保持中国 IP 数据更新 |
| GeoSite 自动更新 | 开启 | 保持 TikTok 和中国域名分类更新 |
| TCP 并发 | 保持默认 | 当前规则不要求强制修改 |
| 统一延迟 | 保持默认 | 不影响手工选择的`美国`策略 |
| TUN 网络栈 | 保持默认 | 当前使用增强模式，不启用 TUN |
| GSO 相关选项 | 保持默认 | 没有当前设备的验证依据，不强制修改 |

不要叠加其他会修改规则、策略组、规则集或 DNS 的完整覆写模块。

## 安装

1. 在每台需要使用 TikTok 的手机上完成 SocksTun 配置，并确保只有 TikTok 被加入代理应用列表。
2. 在 OpenClash 添加机场订阅并设为当前配置。
3. 按本 README 手工设置 OpenClash，并把 IPRoyal 服务器 IPv4 加入“本地 IPv4 网络绕过列表”。
4. 删除或停用旧的本地 IPRoyal 覆写模块。
5. 在“覆写设置 → 模块设置”添加并启用：

   ```text
   https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/overwrite/openclash-overwrite.conf
   ```

6. 适用配置只选择当前机场配置。
7. 更新覆写，应用配置并重启 OpenClash。
8. 在`美国`组手工选择一个机场美国节点。

`美国`组只接收带有`🇺🇸`、`美国`、`美國`、`United States`、`USA`或独立`US`标识的节点。没有合格节点时使用 `REJECT`，不会静默直连。

## 规则顺序

```text
私网/LAN                    -> DIRECT
TikTok DNS 泄漏            -> 空响应
TikTok 可识别连接          -> REJECT
Google/Google Play          -> 美国
Manual-Direct              -> DIRECT
中国大陆域名/IP            -> DIRECT
其他所有流量               -> 美国
```

OpenClash 不能把普通 TikTok 流量“转交给手机 SocksTun”；SocksTun 必须先在手机系统层接管 TikTok。仓库规则的职责是确保未被接管的 TikTok 不会使用任何其他出口。

## 维护直连域名

需要增加直连域名时，只修改：

```text
rules/manual-direct.yaml
```

主域名及其全部子域名使用：

```yaml
- DOMAIN-SUFFIX,example.com
```

只匹配一个完整域名时使用：

```yaml
- DOMAIN,api.example.com
```

不要写协议、路径、端口或参数。普通中国大陆网站已由 `GEOSITE,cn` / `GEOIP,CN` 处理，不需要重复加入。

`manual-direct.yaml` 的现有有效条目属于需要保留的用户配置。未经用户明确要求，不得批量删除、重新分类、去重或替换。新增直连域名只修改该文件；TikTok 防泄漏规则和 Google Play 稳定规则仍具有更高优先级，不能通过在此文件增加同名域名绕过 R1 或 R6。

## 应用后检查

1. R1：OpenClash 中不存在 `TikTok-ISP` 策略组，`美国`组中也没有 IPRoyal 节点。
2. R1：开启 SocksTun 后，TikTok 可以访问，IPRoyal 面板或 SocksTun 连接记录能看到对应流量；OpenClash 日志不应出现 TikTok 命中`美国`或`DIRECT`。
3. R1：关闭 SocksTun 后，TikTok 无法访问；若 OpenClash 识别到连接，应命中 `GeoSite(tiktok) using REJECT`，绝不能命中`美国`或`DIRECT`。
4. R2：其他国外网站命中最终 `MATCH` 并走`美国`。
5. R6：使用 Google Play 完整下载一个应用；`services.googleapis.cn` 应命中 `GeoSite(google)` 并走`美国`，`xn--ngstr-lra8j.com` 应命中 `DomainSuffix` 并走`美国`，二者都不能命中 `GeoSite(cn) using DIRECT`。
6. R3：普通中国大陆网站命中 `GEOSITE,cn` 或 `GEOIP,CN` 并直连。
7. R4：`manual-direct.yaml` 中的域名命中 `Manual-Direct` 并直连。
8. R5：路由器、局域网服务和私有地址保持直连。
9. R7：覆写文件只有 `[YAML]`，运行模式仍由 OpenClash 中文界面手工设置。

纯 IP、未被嗅探且尚未收录进 GeoSite 的新 TikTok 目标，路由器无法单独判断它属于 TikTok。因此最终保证仍来自手机 SocksTun 的“仅允许 TikTok”应用级 VPN 配置；若关闭 SocksTun 后 TikTok 仍能访问，应立即停止测试并检查 SocksTun 的应用选择和手机上的其他 VPN/代理。

## 官方参考

- [Android 每应用 VPN](https://developer.android.com/develop/connectivity/vpn#per-app)
- [SocksTun 官方仓库与 UDP 转发说明](https://github.com/heiher/sockstun)
- [IPRoyal ISP 代理说明](https://iproyal.com/isp-proxies/)
- [IPRoyal ISP 快速入门](https://iproyal.com/quick-start-guides/static-residential-proxies/)
- [OpenClash 设置中的本地 IPv4 网络绕过列表](https://github.com/vernesong/OpenClash/blob/master/luci-app-openclash/luasrc/model/cbi/openclash/settings.lua)
- [Mihomo DNS](https://wiki.metacubex.one/config/dns/)
- [Mihomo 策略组](https://wiki.metacubex.one/config/proxy-groups/)
- [OpenClash：Google Play 无法下载的同类案例](https://github.com/vernesong/OpenClash/discussions/3131)
- [MetaCubeX：Google 域名同时进入 Google/CN 分类的问题](https://github.com/MetaCubeX/meta-rules-dat/issues/84)
- [MetaCubeX TikTok GeoSite](https://github.com/MetaCubeX/meta-rules-dat/blob/meta/geo/geosite/tiktok.yaml)
- [RFC 9000：QUIC 是基于 UDP 的传输协议](https://www.rfc-editor.org/rfc/rfc9000.html)
