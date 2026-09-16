# OpenClash 最小分流配置

本仓库只实现以下规则：

1. TikTok 域名只走本地 IPRoyal ISP 节点。
2. 其他国外域名和流量走手工选择的机场美国节点。
3. 中国大陆域名和 IP 直连。
4. `rules/manual-direct.yaml` 中手工维护的域名直连。
5. 局域网和私有地址直连。

仓库仅保留：

```text
README.md
overwrite/openclash-overwrite.conf
rules/manual-direct.yaml
```

## 为什么选择 Meta

OpenClash 中的 `Meta` 是 Mihomo 核心。本配置需要它提供的：

- `GEOSITE,tiktok`、`GEOSITE,cn` 和 `GEOIP,CN` 规则；
- 按名称过滤订阅节点的 `include-all`、`filter` 和 `exclude-filter`；
- 策略组为空时使用 `empty-fallback: REJECT`，避免错误回退；
- SOCKS5 UDP，以及按分流规则连接 DNS 的 `respect-rules`。

这里不使用 Smart。`美国`必须由用户手工选择机场节点；`TikTok-ISP`只能包含名称严格等于 `IPRoyal-US-ISP` 的本地节点，不需要自动选路或模型切换。

## 推荐设置

主覆写设置为：

| 设置 | 值 | 原因 |
| --- | --- | --- |
| 核心 | Meta | 支持本配置使用的规则和策略组能力 |
| 运行模式 | Fake-IP | 使用 OpenClash 当前默认基础模式，不启用 TUN |
| 代理模式 | Rule | 按规则决定出口 |
| 中国大陆 IPv4 绕过 | 关闭 | 让流量进入核心后按域名/IP规则判断，避免防火墙提前绕过 |
| UDP代理 | 开启 | TikTok 和 IPRoyal SOCKS5 可以使用 UDP |
| QUIC UDP/443 | 允许 | 本需求没有禁用 QUIC 的依据 |
| IPv6代理和IPv6 DNS | 关闭 | 避免未纳入规则的 IPv6 流量旁路 |
| 自定义 DNS、DNS重定向、respect-rules | 开启 | DNS连接与最终策略保持一致 |

没有固定 TUN 网络栈、TCP并发、统一延迟、GSO等与本分流目标无关的参数。

## 安装

1. 在 OpenClash 添加机场订阅并设为当前配置。
2. 在“覆写设置 → 模块设置”添加并启用：

   ```text
   https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/overwrite/openclash-overwrite.conf
   ```

3. 适用配置只选择当前机场配置。
4. 添加并启用下面的本地 IPRoyal 模块。
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
- 服务器、端口、用户名和密码不得提交到仓库、聊天、日志或截图。
- 本地模块不要添加规则、DNS或策略组。

## 规则顺序

```text
私网/LAN              -> DIRECT
TikTok GeoSite        -> TikTok-ISP -> IPRoyal-US-ISP
Manual-Direct         -> DIRECT
中国大陆域名/IP       -> DIRECT
其他所有流量          -> 美国
```

IPRoyal 节点不存在时，TikTok 使用 `REJECT`；`美国`组没有合格节点时，其他国外流量使用 `REJECT`。两者都不会静默直连或切换到错误出口。

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

不要写协议、路径、端口或参数。普通中国大陆网站已经由 `GEOSITE,cn` / `GEOIP,CN` 处理，不需要重复加入。

## 应用后检查

只检查当前目标：

1. `TikTok-ISP`只有`IPRoyal-US-ISP`。
2. `美国`只有机场美国节点，不包含 IPRoyal。
3. TikTok 命中`TikTok-ISP`。
4. `manual-direct.yaml`中的域名命中`Manual-Direct`并直连。
5. 中国大陆网站命中`GEOSITE,cn`或`GEOIP,CN`并直连。
6. 其他国外网站命中最终`MATCH`并走`美国`。

测试时关闭终端设备自身的 VPN、代理、浏览器安全 DNS 和 Android 私人 DNS，避免绕过 OpenClash。

路由器只能按域名/IP分流，不能识别终端上的 Android/iOS 应用包名。任何配置也不能保证不存在未知上游变化；发现异常时应以当时的 OpenClash 命中日志为准，只修改对应域名规则。

## 官方参考

- [OpenClash 模块参数](https://github.com/vernesong/OpenClash/blob/master/luci-app-openclash/root/etc/openclash/overwrite/default)
- [Mihomo 策略组](https://wiki.metacubex.one/config/proxy-groups/)
- [Mihomo Rule-Providers](https://wiki.metacubex.one/config/rule-providers/)
- [Mihomo SOCKS5](https://wiki.metacubex.one/config/proxies/socks/)
- [Mihomo DNS](https://wiki.metacubex.one/config/dns/)
- [MetaCubeX TikTok GeoSite](https://github.com/MetaCubeX/meta-rules-dat/blob/meta/geo/geosite/tiktok.yaml)
