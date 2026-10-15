# 所有手机经 OpenClash / IPRoyal 使用 TikTok

适用：`tiktok-router-iproyal-us v1.0.0` 候选。机场订阅仍提供其他国外流量的美国节点。IPRoyal 仅供 TikTok 连接及其必要的专用 DNS 查询，手机无需 SocksTun。

以下由用户在路由器中文界面手工执行。先备份当前配置、模块与开关截图。本地测试文件可直接上传；开发分支推送后也可使用下一节的候选链接。根目录兼容入口仍是旧 SocksTun 正式方案，不能用于本方案。

## 1. 保留机场，准备本地 IPRoyal 节点

进入 **服务 → OpenClash → 运行状态 → 顶部“覆写模块” → 弹出窗口 → 添加新模块**。先在电脑创建一个只在自己设备保存的 `.conf` 文件，按下面格式填好后通过“本地模块”上传；命名建议 `iproyal-local.conf`，匹配当前机场配置完整路径，如 `/etc/openclash/config/实际文件名.yaml`。

**以下是待填写模板，不能原样启用。** 服务器、SOCKS5 端口、代理用户名和密码从 IPRoyal 订单读取；不是网站登录密码。端口填整数；引号中的凭据若含单引号，用两个单引号表示。不要把填写后的文件或截图提交 GitHub、聊天或在线订阅转换服务。

```ini
[YAML]
proxies+:
  - name: IPRoyal-US-ISP
    type: socks5
    server: '填写订单服务器地址'
    port: 填写订单SOCKS5端口整数
    username: '填写代理用户名'
    password: '填写代理密码'
    udp: false
    dialer-proxy: DIRECT
```

`proxies+` 只追加这一个本地节点，保留机场节点；本地模块在每次插件启动/重启时重新合并，可避免仅编辑机场订阅文件后被更新覆盖。名称必须逐字一致，且只能定义一次。若当前配置已经有同名节点，先确认其来源，只保留一个定义，不重复追加。本方案仅匹配顶层 `proxies`，仅存在于 `proxy-providers` 的节点需先转成本地定义。

`dialer-proxy: DIRECT` 使路由器直接连接 IPRoyal，不串联机场；它不把 TikTok 改为直连。`udp: false` 是服务 UDP 能力未确认时的基线，不支持的 TikTok UDP 会被拒绝；不要仅因类型为 SOCKS5 就打开 UDP。是否支持直播等功能必须实测。

## 2. 安装唯一的完整分流模块

仍在顶部“覆写模块”窗口，**添加新模块 → 本地模块**，上传同目录 [openclash-overwrite.conf](openclash-overwrite.conf)，名称建议 `tiktok-router-iproyal-us-v1.0.0`，匹配同一机场配置完整路径。

开发候选的专属 URL（可随候选修正变化，不是稳定标签）：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/codex/router-iproyal-tiktok/profiles/tiktok-router-iproyal-us/versions/v1.0.0/openclash-overwrite.conf
```

使用链接时选择“添加新模块 → 订阅链接”，与本地上传二选一。首次使用须核对文件头为 `tiktok-router-iproyal-us v1.0.0 candidate`。

停用此前 SocksTun 完整覆写，以及其他修改 DNS、规则、策略组的完整模块；不要删除回退文件。启用新完整模块及上面的本地凭据模块。**一个完整分流模块＋一个仅追加节点的本地凭据模块**可以配合；不允许叠加两套完整方案。凭据模块只写 `proxies+`，没有规则、DNS 或插件开关，和完整模块不存在字段覆盖。

保存只是落盘，完成下面开关后统一点运行状态页 **重启 OpenClash**；重载防火墙不会重新执行覆写。

## 3. 插件手工设置

以下沿用指南基线，不沿用旧仓库“关闭大陆绕过”的要求。

| 页面（服务 → OpenClash） | 设置 | 值 |
| --- | --- | --- |
| 插件设置 → 模式设置 | 运行模式 | Fake-IP（增强），非 TUN、非混合 |
| 运行状态/模式设置 | 代理模式 | 规则模式 |
| 插件设置 → 模式设置 | UDP 流量转发 | 开启；TikTok 本地节点 UDP 基线仍为 false |
| 插件设置 → 流量控制 | 路由器本机代理 | 开启 |
| 同上 | 实验性：绕过指定区域 IPv4 | 绕过中国大陆 |
| 同上 | 中国大陆域名数据源 | MetaCubeX cn.mrs |
| 同上 | 禁用 QUIC | 开启，促使手机支持降级的连接使用 TCP |
| 同上 | 绕过代理服务器地址 | 开启 |
| 同上 | 仅允许内网访问 | 开启 |
| 同上 | 仅允许常用端口流量 | 关闭 |
| 插件设置 → 模式设置 | 旁路网关兼容 | 回程正常则关闭，仅旁路回程不成立时启用 |
| 插件设置 → DNS 设置 | 本地 DNS 劫持/重定向 | Dnsmasq 转发 |
| 覆写设置 → DNS 设置 | 自定义上游 DNS、遵守路由规则 | 开启；至少保留一条国内 HTTPS Nameserver 供界面保存 |
| 同上 | 附加上游 DNS、自动追加默认 DNS、Fallback、Fallback-Filter | 关闭 |
| 同上 | Fake-IP 持久化、自定义 Fake-IP-Filter | 开启；过滤模式选择规则（rule） |
| 覆写设置 → Meta 设置 | 域名嗅探、纯 IP 嗅探 | 开启 |
| 同上 | 进程查找 | off |
| 覆写设置 → 规则设置 | 仅代理命中规则流量、额外本地自定义规则 | 关闭 |
| 插件设置 → IPv6 设置 | IPv6 代理、IPv6 DNS 解析、区域 IPv6 绕过 | 关闭；不能据此认为 LAN/WAN IPv6 已关闭 |
| 插件设置 → GEO 数据库订阅/大陆白名单订阅 | 使用中的 GeoSite/GeoIP、大陆 IPv4 列表更新 | 启用并确认更新成功 |

在 **流量控制 → 本地 IPv4 网络绕过列表** 保留原有局域网条目，并添加订单服务器 IPv4 的精确 `/32`（如果服务器为域名，应核对当前服务器地址）；不要填手机地址或整个手机网段。该设置与节点的 DIRECT 拨号一起避免代理服务器被重复接管。不要额外添加 TikTok 域名直连。

最终 DNS 由模块明确配置：国内 DoH、无 Fallback；TikTok DoH 经 `TikTok-ISP`，Google/Play DoH 经`美国`。Fake-IP 顺序为 TikTok/Google → 本地和人工直连真实地址 → CN 真实地址 → 其余 Fake-IP。路由中 TikTok 紧随一个同分类 REJECT：Mihomo 可能跳过不支持 UDP 的代理规则，第二条防止继续命中机场或 DIRECT。不能删除它。

禁用 QUIC 不保证所有业务都能降级；境外 DIRECT 的 UDP/443 业务也可能受影响。手机必须确实使用本路由器网关和 DNS，验收时停止 SocksTun/其他 VPN、关闭移动数据和私有 DNS。若 LAN 仍发布可直出的 IPv6 网关，本方案的 IPv4 设置无法阻止该路径：先确认网络拓扑再验收，不凭此表承诺无泄漏。

## 4. 当前最有价值的验证

重启后先看仪表盘：**TikTok-ISP 应只有 IPRoyal-US-ISP，美国组应只有机场美国节点**，手选所需机场美国节点。若 TikTok-ISP 只有 REJECT，说明本地节点缺失或名称不匹配，先修正节点；不要选择机场替代。

用两台接入该路由器的手机关闭 SocksTun，打开并刷新 TikTok；核对新连接命中 `GEOSITE,tiktok → TikTok-ISP → IPRoyal-US-ISP`。浏览器随意打开 IP 检测网站会走机场，不能用它证明 TikTok 出口；需检查真实连接链及 IPRoyal 端对应出口。继续按 [REQUIREMENTS.md](REQUIREMENTS.md) 完成缺失节点、国内 App、Google Play、订阅更新验收后，才可发布。

失败时：**运行日志 → 调试日志 → 生成日志**，提供脱敏日志及 App、时间、失败请求；不要在没有证据时连续调整 DNS、TUN 或旁路开关。若国内 App 仍慢，不能直接认定是丢包或本次修改已解决。

## 5. 回退

停用新完整模块和新增的本地凭据模块，恢复备份中原来启用的唯一完整模块及插件开关，重启。若恢复 `tiktok-sockstun-us v2.0.0`，手机必须重新启用 SocksTun/IPRoyal；只恢复旧模块而不恢复手机路径，TikTok 会按旧方案拒绝。

## 依据和验证状态

依据核对日期：2026-10-15。指南 dev 内容可能变化；新方案尚未实机验收，不能把另一方案的成功记录当作本版成功。

- [OpenClash 用户指南与路由表](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md)
- [08-settings-mode-traffic.md §8.2、§8.3](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/08-settings-mode-traffic.md)：模式、旁路、QUIC 和服务器地址绕过。
- [09-settings-dns-ac-ipv6.md §9.1、§9.5](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/09-settings-dns-ac-ipv6.md)；[11-overwrite-settings.md §11.3](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/11-overwrite-settings.md)。
- [16-overwrite-module-format.md §16.1.1、§16.2.3](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)：入口、追加语义和重启。
- 指南要求主动查证的 Mihomo 字段：[SOCKS5](https://wiki.metacubex.one/config/proxies/socks/)、[策略组](https://wiki.metacubex.one/config/proxy-groups/)、[DNS](https://wiki.metacubex.one/config/dns/)、[DIRECT 拨号](https://wiki.metacubex.one/config/proxies/dialer-proxy/)。
- [Mihomo v1.19.32 match()](https://github.com/MetaCubeX/mihomo/blob/v1.19.32/tunnel/tunnel.go#L643)：不支持 UDP 的代理会继续匹配，故保留同分类拒绝收口。

2026-10-15 本地验证：仓库一致性、YAML 解析、差异空白检查通过；官方 Mihomo v1.19.32 对“本地节点存在/缺失”两份合并夹具均通过配置检查。启动仅监听 Windows 回环的隔离夹具，API 确认存在时 TikTok-ISP 仅含 IPRoyal-US-ISP、缺失时仅含 REJECT，美国组均排除 IPRoyal；向夹具发送 TikTok 域名 UDP 报文，两种状态均观察到 REJECT，未落入机场。夹具复用本地规则数据，不连接真实 IPRoyal/机场，不验证 OpenWrt 防火墙。合并检查保留插件 DNS 监听地址并清除旧 Fallback/策略。所有真实设备项目仍待用户执行。
