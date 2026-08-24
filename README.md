# OpenClash 自定义覆写规则

本仓库给第三方订阅模板追加统一分流，不保存机场订阅、Sub-Store 地址、令牌或密钥，也不替换模板原有策略组、DNS 和规则。

## 当前能力

- `日本`、`美国`、`新加坡`：自动收集订阅中名称匹配的节点；默认自动测速，也可在面板手选节点。
- 按设备固定 IP 分流：公司、家里等不同局域网只需把地址追加到对应 `device-*.yaml`。
- 中国大陆域名和 IP 直连。
- 支持手工指定域名走 `DIRECT`、日本、美国或新加坡。
- Google Play 下载链路按设备保持同一出口，避免分流不一致导致更新卡住。
- TikTok 主站、API、CDN 和字节海外共享域名在国内判断前按设备地区代理。
- 局域网、链路本地和组播直连，并让 `.lan`、`.local`、`.home.arpa` 绕过 Fake-IP。
- 不再全局拒绝公网 IPv6；设备分流默认关闭 AAAA 返回，以 IPv4 来源地址稳定匹配。
- UDP 代理保持启用；UDP/443 QUIC 默认禁用并回落到 TCP，降低节点 UDP 不稳定导致的断流。
- 开启域名嗅探，识别 TLS/QUIC 纯 IP 连接中的 TikTok 域名。

兼容要求：OpenClash `v0.47.081+`，Mihomo `v1.19.28+`，规则模式。订阅节点本身必须支持 UDP。

## 覆写订阅地址

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/overwrite/openclash-overwrite.conf
```

备用地址：

```text
https://cdn.jsdelivr.net/gh/yang137197/openclash-custom-rules@main/overwrite/openclash-overwrite.conf
```

在 OpenClash 的“覆写设置 → 模块设置”中新建远程订阅，填入主地址并启用，然后更新配置订阅并应用。

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
- 修改后提交到 `main`，等待 Raw 文件可访问，再在 OpenClash 更新模块和配置。

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
5. 合并到 `main` 后，在 OpenClash 更新覆写模块和配置订阅，然后应用配置。

## 手工指定域名

| 出口 | 文件 |
| --- | --- |
| 直连 | `rules/manual-direct.yaml` |
| 日本 | `rules/manual-jp.yaml` |
| 美国 | `rules/manual-us.yaml` |
| 新加坡 | `rules/manual-sg.yaml` |

示例：

```yaml
payload:
  - DOMAIN,api.example.com
  - DOMAIN-SUFFIX,example.com
```

同一域名不要重复放入多个文件。优先级为 `DIRECT > 日本 > 美国 > 新加坡`，并高于国内直连、设备分流和第三方模板规则。

## 规则优先级

1. 局域网、链路本地、组播直连。
2. 手工域名规则。
3. TikTok、Google Play 按设备地区代理。
4. 中国大陆域名和 IP 直连。
5. 按设备来源地址走日本、美国或新加坡。
6. 俄罗斯电商、AI 日本和第三方模板原有规则。

“中国大陆全部直连”有两个有意保留的内置例外：TikTok 和 `rules/google-play.yaml`。前者必须按设备地区代理；Google 的部分下载域名带 `.cn` 或被国内列表收录，若这些请求直连、账号和校验请求走代理，Google Play 可能在 99% 停住。

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

1. 更新覆写模块、配置订阅和全部规则提供者，然后重启 OpenClash；只更新配置但不更新规则提供者可能仍使用旧缓存。
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
- `rules/ai.yaml`：AI 服务规则。
- `rules/ru-commerce.yaml`：Ozon / Wildberries 规则。
- `docs/acceptance-log.md`：本地验收记录。

参考：[OpenClash YAML 覆写示例](https://github.com/vernesong/OpenClash/blob/master/luci-app-openclash/root/etc/openclash/overwrite/default)、[Mihomo 路由规则](https://wiki.metacubex.one/config/rules/)、[Mihomo 域名嗅探](https://wiki.metacubex.one/config/sniff/)、[V2Fly TikTok 域名](https://github.com/v2fly/domain-list-community/blob/master/data/tiktok)、[blackmatrix7 TikTok 规则](https://github.com/blackmatrix7/ios_rule_script/blob/master/rule/Clash/TikTok/TikTok_No_Resolve.yaml)、[Microsoft 手机连接排错](https://support.microsoft.com/windows/apps/phonelink/troubleshooting-the-phone-link)、[Google Play 下载排错](https://support.google.com/googleplay/answer/14122894)。
