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
- SOCKS5 UDP，以及让 DNS 连接遵循分流规则的能力。

这里不使用 Smart。`美国`必须由用户手工选择机场节点；`TikTok-ISP`只能包含名称严格等于 `IPRoyal-US-ISP` 的本地节点，不需要自动选路或模型切换。

## OpenClash 中文界面建议配置

这是一份针对本仓库分流规则的相对稳定基线。下表中的 OpenClash 插件选项必须全部在中文界面中手动设置，远程覆写不会修改这些选项。

远程覆写模块有意不包含 `[General]`，只保留 `[YAML]` 配置。这样可以避免不同 OpenClash 版本解析 `[General]` 时的兼容问题，并确保插件设置页面与实际运行设置一致。

### 基础设置

| 中文设置项 | 建议值 | 说明 |
| --- | --- | --- |
| 运行内核 | Meta | 支持本配置使用的规则、策略组、SOCKS5 UDP 和 DNS 分流能力 |
| 运行模式 | Fake-IP（增强）模式 | 手动选择；不使用 TUN 或 TUN 混合模式 |
| 代理模式 | 规则模式 | 严格按本仓库的规则顺序选择出口 |
| 路由器本机代理 | 开启 | 让路由器自身的受管流量也按规则处理 |
| UDP 代理 | 开启 | TikTok 和 IPRoyal SOCKS5 可以使用 UDP |
| 禁用 QUIC | 关闭 | 允许 UDP/443；当前需求没有禁用 QUIC 的依据 |
| IPv6 代理 | 关闭 | 避免未纳入规则的 IPv6 流量旁路 |
| IPv6 DNS | 关闭 | 与仅使用 IPv4 的分流基线保持一致 |
| 域名嗅探 | 开启 | 提高纯 IP 或目标信息不完整连接的域名识别率 |
| 纯 IP 连接嗅探 | 开启 | 配合域名规则识别纯 IP 连接 |
| 进程查找模式 | 关闭 | 路由器按域名/IP分流，不依赖终端应用进程 |

### 防火墙与分流设置

| 中文设置项 | 建议值 | 说明 |
| --- | --- | --- |
| 仅允许内网访问 | 开启 | 不向外网开放 OpenClash 代理端口 |
| 旁路网关兼容模式 | 关闭 | 当前规则不需要额外的旁路网关兼容处理 |
| 绕过常用端口 | 关闭 | 避免 80、443 等流量在进入规则判断前被跳过 |
| 绕过中国大陆 IPv4 | 关闭 | 让国内流量进入核心后由中国域名和中国 IP 规则直连 |
| 绕过中国大陆 IPv6 | 关闭 | IPv6 已关闭，不额外维护 IPv6 绕过链路 |
| 中国大陆 IP 列表自动更新 | 关闭 | 中国大陆防火墙绕过已关闭，该列表不参与当前分流 |
| 仅代理命中规则流量 | 关闭 | 未命中特例的国外流量必须继续进入最终“美国”策略 |
| OpenClash 本地自定义规则 | 关闭 | 避免路由器上残留的旧规则改变本仓库规则顺序 |
| 绕过代理服务器地址 | 开启 | 机场和 IPRoyal 服务器的连接直接建立，避免再次进入代理链路 |

关闭“绕过中国大陆 IPv4”不等于中国流量走代理。中国域名和 IP 仍由本配置中的中国大陆规则直连。

### DNS 设置

| 中文设置项 | 建议值 | 说明 |
| --- | --- | --- |
| 自定义 DNS | 开启 | 使用本覆写中定义的国内、美国和 TikTok DNS 分流 |
| DNS 重定向 | 开启，选择 Dnsmasq 转发 | 统一接管局域网常规 DNS 请求 |
| 遵循分流规则 | 开启 | DNS 连接使用与目标流量一致的策略 |
| 自动追加默认 DNS | 关闭 | 避免额外 DNS 混入既定配置 |
| 追加上游分配 DNS | 关闭 | 避免运营商 DNS 改变解析路径 |
| Fake-IP 持久化缓存 | 开启 | 减少重启后重复建立映射 |
| Fake-IP 过滤 | 开启，黑名单模式 | 保留局域网和自建服务域名的真实 IP 解析 |

DNS 服务器、策略组和 Fake-IP 过滤内容由远程覆写的 `[YAML]` 部分写入，不需要在 OpenClash 页面重复添加；本节表格中的插件开关仍需手动设置。

### 更新和高级设置

| 中文设置项 | 建议值 | 说明 |
| --- | --- | --- |
| GeoIP 数据库 | 开启 | 中国 IP 直连规则需要 |
| GeoIP 自动更新 | 开启 | 保持中国 IP 数据更新 |
| GeoSite 自动更新 | 开启 | 保持 TikTok 和中国域名分类更新 |
| TCP 并发 | 保持默认 | 当前分流目标不需要强制修改 |
| 统一延迟 | 保持默认 | 不影响手工选择的“美国”策略 |
| TUN 网络栈 | 保持默认 | 当前使用增强模式，不启用 TUN |
| GSO 相关选项 | 保持默认 | 没有针对当前设备的验证依据，不强制修改 |

不要叠加其他会修改规则、策略组、规则集或 DNS 的完整覆写模块。`美国`策略组保持手工选择，不开启自动切换。

本配置只能保证分流关系和失败时不回退到错误出口。单个 IPRoyal ISP 节点仍然是单点；其入口或线路超时不能通过修改 OpenClash 规则解决。

## 安装

1. 在 OpenClash 添加机场订阅并设为当前配置。
2. 按“OpenClash 中文界面建议配置”中的表格手动设置全部插件选项。
3. 确认“插件设置 → 运行模式”为“Fake-IP（增强）模式”，不要选择 TUN 或 TUN-混合模式。
4. 在“覆写设置 → 模块设置”添加并启用：

   ```text
   https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/overwrite/openclash-overwrite.conf
   ```

5. 适用配置只选择当前机场配置。
6. 添加并启用下面的本地 IPRoyal 模块。
7. 更新覆写，应用配置并重启 OpenClash。
8. 在`美国`组手工选择一个机场美国节点。

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
