# OpenClash 最小可维护分流

本仓库只保留实际配置与规则说明，目标如下：

1. TikTok 域名只走 IPRoyal ISP。
2. 其他国外流量走手工选择的机场美国节点。
3. 中国大陆域名/IP直连。
4. `Manual-Direct` 中长期维护的例外域名直连。
5. 局域网和私有地址直连。

## 仓库文件

```text
README.md
overwrite/openclash-overwrite.conf
rules/manual-direct.yaml
```

- `openclash-overwrite.conf`：策略组、DNS、运行参数和规则顺序。
- `manual-direct.yaml`：用户手工维护的直连域名，必须保留。
- TikTok 不再维护重复的自定义规则文件，统一使用持续更新的 `GEOSITE,tiktok`。

## 为什么使用 Meta

`Meta` 即 Mihomo。本配置依赖它支持的：

- `GEOSITE,tiktok`、`GEOSITE,cn`、`GEOIP,CN`；
- `include-all`、`filter`、`exclude-filter`；
- `empty-fallback: REJECT`，保证错误出口不静默回退；
- SOCKS5 TCP/UDP；
- `respect-rules` 与按策略组发起的 DNS 查询。

不使用 Smart：本需求强调固定、可预测的出口，不需要模型自动切换节点。`美国`保持手工 `select`；`TikTok-ISP`只接受名称严格等于 `IPRoyal-US-ISP` 的节点。

## 推荐运行设置

主覆写已固定下列关键值：

| 设置 | 推荐值 |
| --- | --- |
| 核心 | Meta |
| 运行模式 | Fake-IP（TUN） |
| TUN 网络栈 | System |
| 代理模式 | Rule |
| 路由器本机代理 | 开启 |
| 绕过中国大陆 IPv4 | 开启 |
| QUIC UDP/443 | 禁用 |
| quic-go GSO | 禁用 |
| TCP 并发、统一延迟 | 开启 |
| 域名、纯 IP、自定义嗅探 | 开启 |
| DNS 重定向、自定义 DNS、respect-rules | 开启 |
| 追加 Default/WAN DNS | 关闭 |
| Fake-IP 缓存、Fake-IP Filter | 开启，blacklist |
| IPv6代理、IPv6 DNS | 关闭 |

不要改成 Fake-IP（增强）或 Fake-IP（TUN混合）。本机稳定组合是 `Fake-IP（TUN）+ System`。

## 安装与启用

1. 在 OpenClash 添加机场订阅并设为当前配置。
2. 在“覆写设置 → 模块设置”添加并启用：

   ```text
   https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/overwrite/openclash-overwrite.conf
   ```

3. 适用配置只选择当前机场配置。
4. 再启用下面的本地 IPRoyal 模块。
5. 更新覆写，应用配置并重启 OpenClash。
6. 在`美国`组手工选择一个机场美国节点。

不要叠加其他会修改 `rules`、`proxy-groups`、`rule-providers` 或 DNS 的完整覆写模块。

## 本地 IPRoyal 模块

IPRoyal 地址和凭证只保存在路由器本地：

```yaml
[YAML]

proxies+:
  - name: IPRoyal-US-ISP
    type: socks5
    server: "IPRoyal 面板显示的服务器或 IP"
    port: SOCKS5端口
    username: "用户名"
    password: "密码"
    udp: true
    ip-version: ipv4
```

要求：

- 节点名称必须严格为 `IPRoyal-US-ISP`。
- 不得把服务器、端口、用户名、密码提交到仓库、聊天、日志或截图。
- 本地模块不要添加规则、DNS或策略组。

## 最终规则顺序

```text
私网/LAN                         -> DIRECT
TikTok GeoSite                  -> TikTok-ISP -> IPRoyal-US-ISP
OneDrive Consumer、Google Play  -> 美国
Manual-Direct                   -> DIRECT
中国大陆域名/IP                 -> DIRECT
其他所有流量                    -> 美国
```

IPRoyal 不存在时 TikTok 进入 `REJECT`；美国组没有合格节点时其他国外流量也进入 `REJECT`。两者都不会静默直连或使用错误地区节点。

## 维护直连域名

以后需要增加直连例外，只修改：

```text
rules/manual-direct.yaml
```

优先使用：

```yaml
- DOMAIN-SUFFIX,example.com
```

只有需要匹配单个完整域名时使用：

```yaml
- DOMAIN,api.example.com
```

不要写协议、路径、端口或参数，也不要增加过宽的全球域名后缀。普通中国大陆网站已经由 `GEOSITE,cn` / `GEOIP,CN` 处理，不需要重复加入。

`Manual-Direct` 通过 `behavior: classical` 加载，每天更新一次。主覆写只追加它，不整体覆盖 OpenClash 自动生成的 provider。

## Geo 数据更新

主覆写每周更新中国大陆路由、GeoIP 和 GeoSite 数据。TikTok 使用上游 `GEOSITE,tiktok`，避免自定义 `.snssdk.com` 等共享字节域名误伤国内抖音。

如果日志确认一个新的 TikTok 域名漏到`美国`，先核对 GeoSite 更新是否成功；不要直接添加宽泛关键词规则。

## 验收

启动日志不得出现：

```text
Parse config error
not found rule-set
not found proxy
```

必须确认：

1. `TikTok-ISP`只有`IPRoyal-US-ISP`。
2. `美国`只有机场美国节点，不含 IPRoyal。
3. TikTok → `GeoSite(tiktok)` → `TikTok-ISP[IPRoyal-US-ISP]`。
4. `manual-direct.yaml`中的域名 → `Manual-Direct` → `DIRECT`。
5. 中国大陆网站 → `GeoSite(cn)` / `GeoIP(CN)` → `DIRECT`。
6. Google、GitHub、ChatGPT等 → `美国`。
7. OneDrive Consumer与Google Play下载正常走`美国`。
8. 私网、路由器、NAS、PVE、WireGuard地址 → `DIRECT`。
9. 京东图片、微信/企业微信语音、米家设备工作正常。

首次测试时关闭终端设备自己的VPN、代理、浏览器安全DNS和Android私人DNS，避免绕过OpenClash。

## 能力边界

路由器只能按域名/IP分流，不能识别局域网设备上的Android/iOS应用包名。如果其他应用调用相同TikTok专用域名，也会使用IPRoyal；如果TikTok启用尚未进入GeoSite的新域名，该连接可能暂时进入`美国`。

任何配置都不能保证永远没有缺陷。本方案通过已验证稳定的运行组合、最少外部规则文件、失败关闭和固定手选出口，降低错误回退、节点自动切换和provider覆盖风险。

## 官方参考

- OpenClash模块参数：<https://github.com/vernesong/OpenClash/blob/master/luci-app-openclash/root/etc/openclash/overwrite/default>
- Mihomo策略组：<https://wiki.metacubex.one/config/proxy-groups/>
- Mihomo Rule-Providers：<https://wiki.metacubex.one/config/rule-providers/>
- Mihomo SOCKS5：<https://wiki.metacubex.one/config/proxies/socks/>
- Mihomo DNS：<https://wiki.metacubex.one/config/dns/>
- MetaCubeX TikTok GeoSite：<https://github.com/MetaCubeX/meta-rules-dat/blob/meta/geo/geosite/tiktok.yaml>
