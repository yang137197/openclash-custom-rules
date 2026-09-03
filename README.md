# OpenClash 自定义覆写规则

本仓库在第三方订阅规则最前面插入统一分流，不保存机场订阅、Sub-Store 地址、令牌或密钥。第三方订阅继续提供节点、原策略组和未指定设备的最终兜底。

## 当前能力

- `日本`、`美国`、`新加坡`：自动收集订阅中名称匹配的节点；默认自动测速，也可在面板手选节点。
- 按设备固定 IP 分流：公司、家里等不同局域网只需把地址追加到对应 `device-*.yaml`。
- 中国大陆域名和 IP 直连。
- 支持手工指定域名走 `DIRECT`、日本、美国或新加坡。
- GitHub 始终代理：手工日本规则覆盖核心 GitHub 域名；已登记设备也会按所在地区匹配 GitHub 分类，避免被第三方 Microsoft 规则错误直连。
- Google、Google Play 和 TikTok 按设备地区保持一致出口，优先于可能重叠的国内域名列表。
- Google Play 下载链路按设备保持同一出口，避免分流不一致导致更新卡住。
- TikTok 主站、API、CDN 和字节海外共享域名在国内判断前按设备地区代理。
- 局域网、链路本地和组播直连，并让 `.lan`、`.local`、`.home.arpa` 绕过 Fake-IP。
- 不再全局拒绝公网 IPv6；设备分流默认关闭 AAAA 返回，以 IPv4 来源地址稳定匹配。
- UDP 代理保持启用；UDP/443 QUIC 默认禁用并回落到 TCP，降低节点 UDP 不稳定导致的断流。
- 开启域名嗅探，识别 TLS/QUIC 纯 IP 连接中的 TikTok 域名。
- 中国域名使用国内加密 DoH 直连解析；其他域名使用 `DNS-海外` 组查询，不追加 WAN/运营商 DNS。
- 设备和手工规则每 60 秒检查 GitHub 更新；规则下载继续通过 `DNS-海外`，避免路由器直连 GitHub Raw 失败。

兼容要求：OpenClash `v0.47.081+`，Mihomo `v1.19.28+`，规则模式。订阅节点本身必须支持 UDP。

## 项目更新说明

- [`CHANGELOG.md`](CHANGELOG.md)：实时记录每次发布或功能更新、行为变化和应用要求。
- [`docs/acceptance-log.md`](docs/acceptance-log.md)：记录对应的技术验收结果。

## 覆写订阅地址

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/overwrite/openclash-overwrite.conf
```

一次性恢复地址（固定到已验收提交，不受 jsDelivr 分支缓存影响）：

```text
https://cdn.jsdelivr.net/gh/yang137197/openclash-custom-rules@477dad2/overwrite/openclash-overwrite.conf
```

不要使用 jsDelivr 的 `@main` 地址获取刚提交的覆写：分支地址可能缓存旧内容。GitHub Raw 暂时无法访问时，可用上面的固定提交地址恢复一次；成功应用后再换回主地址，以继续接收后续更新。

在 OpenClash 的“覆写设置 → 模块设置”中只保留一个本仓库订阅并启用，然后更新覆写订阅、应用配置并重启一次 OpenClash。首次安装或本模块本身有更新时，也必须完成同样步骤。

## 按设备维护地区

编辑以下文件，每行一个 `SRC-IP-CIDR`。同一设备在公司和家里的固定地址可以同时写入同一文件：

| 策略组 | 文件 |
| --- | --- |
| 日本 | [`rules/device-jp.yaml`](rules/device-jp.yaml) |
| 美国 | [`rules/device-us.yaml`](rules/device-us.yaml) |
| 新加坡 | [`rules/device-sg.yaml`](rules/device-sg.yaml) |

示例：

```yaml
payload:
  - SRC-IP-CIDR,192.168.100.173/32
  - SRC-IP-CIDR,192.168.20.73/32
```

要求：

- 各路由器用 DHCP 静态租约固定设备 IPv4。
- 手机关闭随机 Wi-Fi MAC，或让静态租约绑定当前网络实际使用的随机 MAC。
- 一个来源地址只能放在一个地区文件中；规则优先级是日本、美国、新加坡。
- 修改后提交到 `main`，等待 Raw 文件可访问；运行中的 OpenClash 最迟约 60 秒自动更新，也可在规则提供者页面手动刷新。

### 同一设备在不同局域网使用相同网段

规则只识别设备当前的来源 IP，不识别设备名称或 MAC 地址。因此：

- 家里和公司都是 `192.168.1.0/24`，且这台设备在两处都固定为 `192.168.1.173`：只需写一条 `SRC-IP-CIDR,192.168.1.173/32`，前提是两处各自使用 OpenClash 网关和同一份规则。
- 设备在两处获得不同 IP：把两个地址写入同一个地区文件。
- 其他设备如果也获得 `192.168.1.173`，同样会命中该策略；务必在每个路由器设置 DHCP 静态租约。
- 两个相同网段同时接入同一台集中式 OpenClash 网关时，网关无法区分两个相同的来源 IP。应改成不同子网/VLAN，或让两处分别使用各自的 OpenClash 网关。

手机可能对不同 Wi-Fi 使用不同的随机 MAC；请分别为实际 MAC 固定 IP，或按需要关闭该 Wi-Fi 的随机 MAC。

### 在 GitHub 网页修改并提交

1. 打开上表对应的地区文件，点击右上角铅笔图标 **Edit this file**。
2. 保留 `payload:`，在下面按 YAML 缩进每行添加一个地址，例如：

   ```yaml
   payload:
     # 家里
     - SRC-IP-CIDR,192.168.1.173/32
     # 公司
     - SRC-IP-CIDR,192.168.1.88/32
   ```

3. 点击 **Preview** 检查内容，再点击 **Commit changes...**，填写说明，例如 `chore: update device IP mapping`。
4. 简单修改可选择直接提交到 `main`。更稳妥的方式是选择新建分支，依次点击 **Propose changes**、**Create pull request**，确认后再点击 **Merge pull request**。
5. 合并到 `main` 后，设备规则会在约 60 秒内自动更新。要立即生效，可在 OpenClash 的规则提供者页面刷新对应的 `Linyang-Device-*`；若同时修改了覆写模块，再更新模块并应用/重启 OpenClash。

## 手工指定域名

### 域名不走代理：只维护这一个文件

以后需要直连的域名，统一编辑 [`rules/manual-direct.yaml`](rules/manual-direct.yaml)。所有条目统一填写业务主域名并使用 `DOMAIN-SUFFIX`，同时覆盖主域名和全部子域名。保留文件最上方的 `payload:`，每条规则前面用两个空格缩进并写 `-`：

```yaml
payload:
  - DOMAIN-SUFFIX,example.com
```

`DOMAIN-SUFFIX,example.com` 会匹配 `example.com` 本身及其全部子域名，例如 `www.example.com`、`api.example.com` 和 `a.api.example.com`。本仓库的手工直连文件不再使用只匹配单一完整域名的 `DOMAIN` 写法，避免业务新增 CDN 或接口子域名后再次误走代理。

以当前微信小程序域名为例：

```yaml
payload:
  - DOMAIN-SUFFIX,gdwzy.top
```

它会同时匹配 `gdwzy.top`、`web.gdwzy.top`、`webcdn.gdwzy.top` 以及其他全部子域名。

填写时注意：

- 只写域名，不要写 `https://`、端口、斜杠或网页路径。例如不要写 `https://api.example.com/v1`。
- 使用英文逗号 `,`，不要使用中文逗号 `，`。
- 只填写主域名并使用 `DOMAIN-SUFFIX`；不要使用 `DOMAIN`，也不要重复放进其他 `manual-*.yaml`。
- 每添加一个域名就新增一行；不要重复写第二个 `payload:`。

### 修改后如何生效

1. 在 GitHub 打开 [`rules/manual-direct.yaml`](rules/manual-direct.yaml)，点击铅笔图标。
2. 添加规则，点击 **Commit changes...**，直接提交到 `main`。
3. 等 GitHub 提交完成。运行中的 OpenClash 会每 60 秒检查一次 `Linyang-Manual-Direct`，通常不需要更新配置订阅或覆写模块。
4. 需要立即生效时，在 OpenClash 的“规则提供者”页面手动更新 `Linyang-Manual-Direct`。若找不到该入口，等待最多约 60 秒后再试。

OpenClash 的“刷新覆写订阅”只负责下载模块文件，手动刷新动作本身不保证立即重新加载当前配置。因此，只有修改了 `overwrite/openclash-overwrite.conf` 时才需要更新覆写模块，并随后应用配置或重启。模块的定时更新启用了 `RESTART = true`，定时更新成功后会自动重启。

生效后，连接日志应显示类似：

```text
match RuleSet/Linyang-Manual-Direct using DIRECT
```

### 其他手工出口文件

| 出口 | 文件 |
| --- | --- |
| 直连 | `rules/manual-direct.yaml` |
| 日本 | `rules/manual-jp.yaml` |
| 美国 | `rules/manual-us.yaml` |
| 新加坡 | `rules/manual-sg.yaml` |

同一域名不要重复放入多个文件。优先级为 `DIRECT > 日本 > 美国 > 新加坡`，并高于国内直连、设备分流和第三方模板规则。

## 规则优先级

1. 局域网、链路本地、组播直连。
2. 手工域名规则。
3. Google、TikTok、Google Play 按设备地区代理。
4. 中国大陆域名和 IP 直连。
5. 按设备来源地址走日本、美国或新加坡。
6. 未登记设备和未列出域名默认直连，不使用第三方订阅的最终 `MATCH`。

“中国大陆全部直连”有两个有意保留的业务例外：Google 和 TikTok。它们必须按设备地区代理；Google 的部分静态或下载域名带 `.cn` 或被国内列表收录，若账号、资源和校验请求出口不一致，Google Play 可能在 99% 停住。

## 2026-08-24 香港误路由根因

日志中的：

```text
192.168.100.203 ... match Match using 🐟 漏网之鱼[香港节点]
```

说明该连接没有命中 `Linyang-Device-US`，而是走到第三方订阅最后的 `MATCH`。`.203` 在 17:28 才写入 GitHub，但旧规则提供者使用相同本地路径和 24 小时更新周期，OpenClash 重启后仍可能复用此前包含 `.238` 的缓存。

当前修正：

- 设备规则使用新的 `linyang-v2-*` 缓存路径，首次加载必须重新下载。
- 设备及手工规则当前更新周期为 60 秒，并继续通过 `DNS-海外` 拉取。
- 规则下载显式使用 `DNS-海外`，不再由第三方 `MATCH` 决定下载出口。
- `+rules` 按 OpenClash 官方语义插入规则数组开头，设备规则始终早于第三方 `MATCH`。

Google 打开后出现香港区域或香港域名不是 DNS 泄露的直接证据。Google 会参考出口 IP、设备位置和账号历史；本次日志已经证明浏览流量实际使用了香港节点。修正后，`.203` 的 Google 连接会优先命中“美国”。

## DNS 策略

- `geosite:cn,private`：使用阿里/腾讯 DoH 直连解析。
- 其他域名：使用 Cloudflare/Google DoH，并通过 `DNS-海外` 发送；该组默认选择“美国”。
- 代理节点自身域名：使用国内 DoH 直连解析，避免先解析节点又必须先连接节点的循环。
- `APPEND_WAN_DNS = 0`：不把 WAN/运营商 DNS 加入 Mihomo 查询池。
- `IPV6_DNS = 0`：普通 DNS 不返回 AAAA，以固定 IPv4 稳定匹配设备规则。

## 已知问题判断

### Windows“手机连接”

代理可能是原因之一，但不是唯一原因。旧规则已让常见私网地址直连；本次进一步补齐链路本地、组播和本地域名，因此覆写本身不应再把同一局域网通信送进代理。

若仍不能连接，依次检查：

1. 手机和 Windows 位于同一可信 Wi-Fi/子网，Windows 网络类型为“专用”。
2. 路由器未启用 AP/Wireless Isolation，访客网络未隔离客户端。
3. 临时关闭 Windows 上的其他 VPN/第三方防火墙做对照测试。
4. 两端使用同一 Microsoft 账号，更新“手机连接”和“连接至 Windows”。
5. Android 对“连接至 Windows”关闭电池优化；通话功能另需正常的蓝牙配对。

微软官方排错同样把同一 Wi-Fi、AP 隔离、VPN/防火墙、账号、版本和电池优化列为主要检查项。

### TikTok 提示无网络

旧覆写有四个高概率触发点：地区手选组首项是 `REJECT`、全局拒绝公网 IPv6、`GEOSITE,tiktok` 未覆盖部分字节海外共享域名，以及节点 UDP/QUIC 不稳定。新规则补齐 TikTok 域名并放在国内判断之前，开启纯 IP 域名嗅探，关闭 AAAA 下发而非硬拒绝公网 IPv6，并让 UDP/443 回落到 TCP。

若仍无网络：

1. 更新覆写模块并重启 OpenClash，再刷新对应规则提供者；只改规则文件时无需更新配置订阅。
2. 在面板把设备对应地区组临时改为一个确定可用的真实节点，不要先用自动测速组；确认不是 `REJECT`。
3. 查看连接日志，确认 `tiktokv.com`、`byteintlapi.com`、`snssdk.com`、`ibyteimg.com` 等全部命中同一个地区组，没有 `DIRECT` 或 `REJECT`。
4. 若仍提示网络不稳定，在同一地区切换另一节点。测速正常只代表测试网址可达，不代表该出口 IP 可用 TikTok。
5. 强制停止 TikTok，清除应用缓存后重开；仍不行再用手机浏览器访问 `https://www.tiktok.com/` 做对照。

### Google Play 卡在 99%

本模块把商店、下载 CDN、校验和账号相关域名按设备地区保持一致出口。若仍复现，先确认这些连接全部命中同一地区组，再按 Google 官方步骤检查网络和存储、重启设备、清理 Play 商店/Play 服务缓存；不要把 `google-play.yaml` 中的域名同时加入 `manual-direct.yaml`。

## IPv6 边界

模块设置 `IPV6_DNS = 0`，让普通域名连接使用 IPv4，从而按固定设备 IPv4 稳定分流；它不会用 `::/0` 全局拒绝 IPv6。若要完整使用 IPv6 设备分流，必须为每个网络准备稳定 IPv6/ULA 来源段，追加到相应 `device-*.yaml`，再自行启用 IPv6 DNS。

## 文件

- `overwrite/openclash-overwrite.conf`：远程覆写模块。
- `rules/device-*.yaml`：设备到地区策略的来源地址映射。
- `rules/manual-*.yaml`：手工域名出口规则。
- `rules/google-play.yaml`：Google Play 一致出口规则。
- `rules/tiktok.yaml`：TikTok 主站、API、CDN 和字节海外共享域名规则。
- `CHANGELOG.md`：项目发布与功能更新说明。
- `docs/acceptance-log.md`：本地验收记录。

参考：[OpenClash YAML 覆写示例](https://github.com/vernesong/OpenClash/blob/master/luci-app-openclash/root/etc/openclash/overwrite/default)、[Mihomo 路由规则](https://wiki.metacubex.one/config/rules/)、[Mihomo DNS](https://wiki.metacubex.one/config/dns/)、[Mihomo 域名嗅探](https://wiki.metacubex.one/config/sniff/)、[V2Fly TikTok 域名](https://github.com/v2fly/domain-list-community/blob/master/data/tiktok)、[blackmatrix7 TikTok 规则](https://github.com/blackmatrix7/ios_rule_script/blob/master/rule/Clash/TikTok/TikTok_No_Resolve.yaml)、[Google 如何使用位置信息](https://policies.google.com/technologies/location-data)、[Microsoft 手机连接排错](https://support.microsoft.com/windows/apps/phonelink/troubleshooting-the-phone-link)、[Google Play 下载排错](https://support.google.com/googleplay/answer/14122894)。
