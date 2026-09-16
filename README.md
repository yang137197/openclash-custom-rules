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

在 OpenClash“插件设置”中手动选择运行模式。主覆写不写入 `EN_MODE`，避免覆写后的实际模式与插件设置页面显示不一致。

推荐设置为：

| 设置 | 值 | 原因 |
| --- | --- | --- |
| 核心 | Meta | 支持本配置使用的规则和策略组能力 |
| 运行模式 | Fake-IP（增强）模式，手动选择 | 不启用 TUN；插件设置页面与实际运行模式保持一致 |
| 代理模式 | Rule | 按规则决定出口 |
| 中国大陆 IPv4 绕过 | 关闭 | 让流量进入核心后按域名/IP规则判断，避免防火墙提前绕过 |
| 中国大陆 IP 列表自动更新 | 关闭 | 防火墙绕过已关闭，这份列表不参与当前分流 |
| OpenClash 本地自定义规则 | 关闭 | 只使用本仓库定义的规则，避免旧规则混入 |
| 绕过代理服务器地址 | 开启 | 让到机场和 IPRoyal 服务器的连接直接建立，避免代理服务器连接再次进入代理链路 |
| UDP代理 | 开启 | TikTok 和 IPRoyal SOCKS5 可以使用 UDP |
| QUIC UDP/443 | 允许 | 本需求没有禁用 QUIC 的依据 |
| IPv6代理和IPv6 DNS | 关闭 | 避免未纳入规则的 IPv6 流量旁路 |
| 自定义 DNS、DNS重定向、respect-rules | 开启 | DNS连接与最终策略保持一致 |

没有固定 TUN 网络栈、TCP并发、统一延迟、GSO等与本分流目标无关的参数。

配置文件中的英文参数与中文界面含义如下：

```text
CHINA_IP_ROUTE = 0            → “绕过中国大陆 IPv4”关闭
CHNR_AUTO_UPDATE = 0          → “中国大陆 IP 列表自动更新”关闭
ENABLE_CUSTOM_CLASH_RULES = 0 → “OpenClash 本地自定义规则”关闭
SKIP_PROXY_ADDRESS = 1        → “绕过代理服务器地址”开启
```

这里的`0`表示关闭，`1`表示打开。关闭“中国大陆 IPv4 绕过”不等于中国流量走代理；中国流量仍会进入 Meta 核心，并由`GEOSITE,cn`和`GEOIP,CN`规则直连。

应用覆写后，可通过路由器 SSH 用一条命令查询实际值：

```sh
printf '运行模式=%s\n绕过中国大陆 IPv4=%s\n中国大陆 IP 列表自动更新=%s\nOpenClash 本地自定义规则=%s\n绕过代理服务器地址=%s\n' "$(uci -q get openclash.config.en_mode)" "$(uci -q get openclash.config.china_ip_route)" "$(uci -q get openclash.config.chnr_auto_update)" "$(uci -q get openclash.config.enable_custom_clash_rules)" "$(uci -q get openclash.config.skip_proxy_address)"
```

“运行模式”预期输出`fake-ip`；随后三项预期输出`0`，“绕过代理服务器地址”预期输出`1`。

## 安装

1. 在 OpenClash 添加机场订阅并设为当前配置。
2. 在“插件设置 → 运行模式”手动选择“Fake-IP（增强）模式”，不要选择 TUN 或 TUN-混合模式。
3. 在“覆写设置 → 模块设置”添加并启用：

   ```text
   https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/overwrite/openclash-overwrite.conf
   ```

4. 适用配置只选择当前机场配置。
5. 添加并启用下面的本地 IPRoyal 模块。
6. 更新覆写，应用配置并重启 OpenClash。
7. 在`美国`组手工选择一个机场美国节点。

不要叠加其他会修改 `rules`、`proxy-groups`、`rule-providers` 或 DNS 的完整覆写模块。

`美国`组只接收带有`🇺🇸`、`美国`、`美國`、`United States`、`USA`或独立`US`标识的节点。仅写城市名或`America`的节点不会自动进入该组，避免误收耶路撒冷、南美洲等非美国节点。

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
