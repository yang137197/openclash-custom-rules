# Codex 交接说明：OpenClash 自定义规则

> 目的：让后续 Codex / AI 开发直接读取仓库即可理解当前设计、已验证行为、历史故障与维护边界，不依赖聊天上下文。
>
> 最后整理：2026-09-08

## 1. 当前目标

这套规则用于 OpenClash Meta / Mihomo，核心目标不是做复杂策略，而是保持可维护、可验证：

1. 局域网 / 私网 → `DIRECT`
2. 中国大陆常规域名 / IP → `DIRECT`
3. `Manual-Direct` 中指定的额外域名 → `DIRECT`
4. TikTok → `TikTok-ISP` → OpenClash 本地模块中的 `IPRoyal-US-ISP`
5. OneDrive Consumer 网页 / 文件链路 → 强制 `美国`
6. 其他未命中流量 → `美国`
7. `美国` 为手工 `select`，固定用户手选机场节点，不自动切换
8. 不按设备 IP、人员、MAC、手机型号写死规则

当前主配置：

- `overwrite/openclash-overwrite.conf`
- `rules/manual-direct.yaml`

## 2. 最后验证环境

2026-09-05 / 2026-09-07 实际环境：

- OpenClash：`0.47.156`
- Mihomo Meta：`alpha-ge183c58`（linux amd64）
- 模式：`rule`
- DNS 增强模式：`fake-ip`
- IPv6：关闭
- `ENABLE_REDIRECT_DNS=1`
- `ENABLE_CUSTOM_DNS=1`
- `ENABLE_RESPECT_RULES=1`
- `ROUTER_SELF_PROXY=1`
- UDP 代理开启
- QUIC 禁用
- Sniffer 开启

网络结构中，CatWrt LAN 为 `192.168.100.1/24`，WAN 上游示例为 `192.168.5.1`。

## 3. 主规则顺序非常重要

当前 `rules!` 的关键顺序：

```yaml
# 私网
- GEOSITE,private,DIRECT
- GEOIP,private,DIRECT,no-resolve
- IP-CIDR,10.0.0.0/8,DIRECT,no-resolve
- IP-CIDR,172.16.0.0/12,DIRECT,no-resolve
- IP-CIDR,192.168.0.0/16,DIRECT,no-resolve

# TikTok 专用 ISP；早于所有直连/兜底规则
- RULE-SET,TikTok-IPRoyal,TikTok-ISP
- GEOSITE,tiktok,TikTok-ISP

# OneDrive Consumer 例外：强制美国
- DOMAIN-SUFFIX,onedrive.live.com,美国
- DOMAIN-SUFFIX,onedrive.com,美国
- DOMAIN-SUFFIX,files.1drv.com,美国
- DOMAIN-SUFFIX,livefilestore.com,美国
# 其余 OneDrive Consumer 相关条目见主覆写文件

# 额外直连
- RULE-SET,Manual-Direct,DIRECT

# Google 静态资源误分类修正
- DOMAIN-SUFFIX,gstatic.com,美国

# 中国大陆
- GEOSITE,cn,DIRECT
- GEOIP,CN,DIRECT,no-resolve

# 兜底
- MATCH,美国
```

必须保持 TikTok 规则位于 `Manual-Direct`、`GEOSITE,cn` 和最终 `MATCH` 之前；OneDrive Consumer 的美国规则仍须位于 `Manual-Direct` 和 `GEOSITE,cn` 之前。

## 4. 为什么显式写 RFC1918 私网

历史运行日志出现过：

```text
192.168.100.1:53
```

没有按预期命中 `GEOIP,private`，最后落到 `MATCH,美国`。

因此现在显式写：

```yaml
10.0.0.0/8
172.16.0.0/12
192.168.0.0/16
```

不要删除。这用于保证：

- 路由器 / DNS
- PVE
- NAS
- Home Assistant
- WireGuard
- 跨网段私网访问

始终 DIRECT。

## 5. DNS 设计

当前设计：

### 国内 / 私有域名

```text
223.5.5.5
1.12.12.12
```

### 国外域名

```text
1.1.1.1
8.8.8.8
```

国外 DNS 连接本身走 `美国`。

TikTok 域名是例外：`geosite:tiktok` 和 `rule-set:TikTok-IPRoyal` 的 DNS 查询通过 `TikTok-ISP`，使解析与业务连接使用同一个 IPRoyal 出口。

关键配置：

```yaml
dns:
  respect-rules: true
  direct-nameserver-follow-policy: true
```

不要仅因为看到 `198.18.x.x` 就认为 DNS 异常；当前为 Fake-IP 模式，这是正常行为。

## 6. Manual-Direct 的维护原则

`rules/manual-direct.yaml` 只用于“必须直连的例外”。

优先：

```yaml
- DOMAIN-SUFFIX,example.com
```

只有单个精确子域名才使用：

```yaml
- DOMAIN,api.example.com
```

不要写：

```text
https://example.com
example.com:443
/path
?query=...
```

普通中国大陆网站不要重复大量加入 Manual-Direct，已有 `GEOSITE,cn` / `GEOIP,CN`。

### 6.1 “电脑远程开机卡控制”微信小程序

2026-09-08 实际日志显示：

```text
api.rmtsw.siwiot.com -> MATCH -> 美国
servicewechat.com -> GeoSite(cn) -> DIRECT
```

因此微信基础链路正常，异常集中在小程序业务接口 `api.rmtsw.siwiot.com` 未进入大陆规则。Google、Cloudflare、阿里和腾讯四个 DNS 查询源当时均解析为 `121.41.129.200`，APNIC RDAP 将该地址标记为中国大陆 `ALISOFT` 网段。

当前在 `Manual-Direct` 中维护：

```yaml
- DOMAIN-SUFFIX,siwiot.com
```

使用主域名后缀是为了同时覆盖当前接口和同一服务以后新增的子域名。不要写死 `121.41.129.200`；服务端 IP 可能变化。

本地使用 Mihomo Meta `v1.19.30` 合并测试通过，模拟请求已确认：

```text
api.rmtsw.siwiot.com -> RuleSet(Manual-Direct) -> DIRECT
```

## 7. Microsoft / Windows 的最终策略

### 7.1 应优先 DIRECT

当前 `Manual-Direct` 已包含大量 Microsoft / Windows 系统端点，设计原则：

- Windows Update
- Delivery Optimization
- Microsoft Store 核心服务
- Windows 激活 / 授权
- Microsoft Account / Entra 登录
- Windows 网络检测 / 遥测 / 推送
- Defender / SmartScreen
- Edge / Microsoft 365 客户端更新
- Microsoft 365 中国区（世纪互联）
- Azure / Entra 中国区

目的是让这些系统服务尽量使用中国大陆公网出口和微软自身的 CDN / DNS 调度。

不要粗暴增加：

```yaml
- DOMAIN-SUFFIX,microsoft.com,DIRECT
- DOMAIN-SUFFIX,live.com,DIRECT
- DOMAIN-SUFFIX,windows.net,DIRECT
```

这些范围过大，会把大量全球微软服务一起强制直连。

### 7.2 Microsoft Store 已补充的前端 / 目录 / CDN

2026-09-07 实际日志中发现以下域名最初落到 `MATCH → 美国`：

```text
storeedge.microsoft.com
c1.microsoft.com
go.microsoft.com
images-eds-ssl.xboxlive.com
```

随后已加入 `Manual-Direct`。当前还包括：

```text
apps.microsoft.com
store-images.microsoft.com
assets.onestore.ms
wcpstatic.microsoft.com
```

实际日志已验证：

```text
storeedge.microsoft.com -> Manual-Direct -> DIRECT
c1.microsoft.com -> Manual-Direct -> DIRECT
store-images.microsoft.com -> Manual-Direct -> DIRECT
storeedgefd.dsx.mp.microsoft.com -> Manual-Direct -> DIRECT
cdn.storeedgefd.dsx.mp.microsoft.com -> Manual-Direct -> DIRECT
```

### 7.3 Microsoft Store “已排队 / 取消无反应”故障

症状：

- 部分应用可以更新
- ChatGPT / TikTok / Instagram / WhatsApp 等显示“已排队”
- 点击取消无反应
- Store 网络核心端点已经正确 DIRECT
- Store 日志没有相应 timeout / connection refused

服务检查：

```powershell
Get-Service wuauserv,BITS,DoSvc,InstallService,ClipSVC |
Format-Table Name,Status,StartType -Auto
```

当时状态：

```text
BITS            Stopped   Manual
ClipSVC         Running   Manual
DoSvc           Running   Automatic
InstallService  Running   Manual
wuauserv        Stopped   Manual
```

该状态没有发现服务被 `Disabled`。

最终有效处理：

```powershell
Get-AppxPackage Microsoft.WindowsStore | Reset-AppxPackage
```

然后重启 Windows。

结果：**重启后 Microsoft Store 恢复正常。**

因此以后再出现相同 Store 队列卡死问题，不要优先继续加 OpenClash 域名；先区分“网络分流问题”与“Store 本地队列 / AppX 状态问题”。

## 8. OneDrive Consumer：不要再强制 DIRECT

### 8.1 实测结论

曾尝试把 OneDrive Consumer 网页 / 文件链路全部加入 `Manual-Direct`，包括：

```text
onedrive.live.com
www.onedrive.live.com
*.files.1drv.com
*.storage.live.com
```

实测：

```text
www.onedrive.live.com
-> Manual-Direct
-> DIRECT
-> 108.160.167.148:443
-> i/o timeout
```

网页无法打开。

因此当前策略改为：

- Microsoft Account / Entra 登录认证链路：`DIRECT`
- OneDrive Consumer 网页 / 文件链路：`美国`

### 8.2 保持 DIRECT 的认证域名

例如：

```text
account.live.com
login.live.com
oauth.live.com
login.microsoftonline.com
login.microsoft.com
login.windows.net
*.msauth.net
*.msauthimages.net
*.msftauth.net
*.msftauthimages.net
```

目的：尽量让微软账户认证看到中国大陆公网出口。

### 8.3 强制美国的 OneDrive Consumer 域名

主覆写中维护，当前包括：

```text
*.onedrive.live.com
*.onedrive.com
*.files.1drv.com
*.livefilestore.com
*.storage.live.com
*.docs.live.net
*.groups.office.live.com
*.groups.photos.live.com
*.groups.skydrive.live.com
*.policies.live.net
*.settings.live.net
*.storage.msn.com
g.live.com
p.sfx.ms
oneclient.sfx.ms
api.onedrive.com
api.live.net
apis.live.net
skyapi.live.net
snapi.live.net
photos.live.com
skydrive.live.com
favorites.live.com
spoprod-a.akamaihd.net
```

不要把这些再加回 `Manual-Direct`，除非在当前网络重新完成 A/B 验证。

## 9. DIRECT `i/o timeout` 调查结论

2026-09-05 曾大量看到：

```text
match GeoSite/cn using DIRECT
... i/o timeout
```

涉及：

- `mssdk.bytedance.com`
- `cn.bing.com`
- `rec.g.163.com`
- 淘宝 CDN
- AWS 中国 IP

同时也出现过美国代理节点入口超时。

做过的关键验证：

1. CatWrt 本机 `curl` 多个相同目标 IP，部分成功、部分超时。
2. Windows LAN 客户端对同一目标 IP，某一时刻超时，几十秒后恢复。
3. Bing 的相同 IP 在 CatWrt 和 LAN 客户端后续都能 HTTP 200。
4. 淘宝 `183.60.240.60`：Windows 一度超时，CatWrt 随后成功，Windows 再测又成功。
5. 当前连接表显示大量国内 DIRECT 实际有上下行流量。
6. CatWrt → 上游网关延迟约 0.3–0.7 ms，未见异常。
7. 对 `223.5.5.5` 100 次 ping：99 收到，1% 丢包，延迟约 9–10 ms。

当前结论：

- 没有证据证明自定义 `rules!` 写错。
- 没有证据证明 DIRECT 持续性失效。
- 更符合“间歇性建连 / CDN / 公网路径 / Mihomo 瞬时异常”之一。
- 不应仅因偶发 `i/o timeout` 就重写 GeoSite、Fake-IP、DNS 或整套 rules。

OpenClash 上游存在相似开放 Issue：

- `vernesong/OpenClash#5270`：大量直连错误

该 Issue 与本环境不是完全相同配置，而且没有公开根因或正式修复结论，只能作为相似案例参考，不能当作已确认根因。

## 10. 已确认不是规则错误的典型日志

规则正确命中时：

```text
mssdk.bytedance.com -> GeoSite(cn) -> DIRECT
cn.bing.com -> GeoSite(cn) -> DIRECT
rec.g.163.com -> GeoSite(cn) -> DIRECT
```

如果随后出现 `dial tcp ... i/o timeout`，说明规则匹配已经结束，错误发生在实际建连阶段。

因此不要把“正确命中 DIRECT 后连接超时”误判为“GeoSite 规则写错”。

## 11. 重要历史坑：不要整体覆盖 rule-providers

历史版本曾用 Ruby / `[Overwrite]` 逻辑整体替换 `rule-providers`，导致 OpenClash 自动生成的：

```text
oc-cn-domain
```

被删除，但 `fake-ip-filter` 仍引用它，最终报：

```text
Parse config error: not found rule-set: oc-cn-domain
```

当前设计明确避免整体覆盖 `rule-providers`。

不要恢复旧写法。

## 12. GitHub Raw provider

`Manual-Direct` provider 当前使用：

```yaml
proxy: 美国
```

原因：当前中国大陆直连 GitHub Raw 曾实际出现 EOF / timeout。

这只影响 provider 文件下载路径，不改变 `Manual-Direct` 命中后的 `DIRECT` 行为。

## 12.1 TikTok 与 IPRoyal 本地节点

远程仓库只保存公开策略：

- `TikTok-ISP` 通过 `include-all-proxies: true` 和精确 `filter` 收集 `IPRoyal-US-ISP`。
- `empty-fallback: REJECT`，节点缺失或本地模块未启用时不回落机场。
- `美国` 使用 `exclude-filter` 排除 `IPRoyal-US-ISP`。
- `TikTok-IPRoyal` 与 `GEOSITE,tiktok` 共同识别 TikTok 域名。

IPRoyal 的服务器、端口、用户名和密码只允许放在 OpenClash 本地覆写模块的 `proxies+` 中，不得写入 GitHub、日志、Issue 或截图。

这一设计对所有经过该 OpenClash 网关并命中 TikTok 域名的设备统一生效。路由器看不到 Android 包名，只能按域名/IP分流；其他应用如使用相同字节海外共享域名，也可能进入 IPRoyal。设备使用移动数据、其他网关、自己的 VPN/代理或绕过 OpenClash 的 DNS 时不在保证范围内。

### 2026-09-08 实机验收结论

- OpenClash 日志确认 TikTok 连接命中 `RuleSet(TikTok-IPRoyal) → TikTok-ISP[IPRoyal-US-ISP]`。
- CatWrt 对 IPRoyal SOCKS5 服务端口连续 5 次 TCP 建连均成功。
- 用户实测 TikTok 可正常打开和联网，证明真实节点、认证、策略组与业务链路组合可用。
- 当天较早日志曾出现短暂 `i/o timeout`，随后自行恢复；没有证据表明远程规则、TikTok 域名识别或本地节点格式存在错误。
- 当前不增加 `dialer-proxy`，也不因一次短暂超时修改 DNS 或 TikTok 规则。后续只有在持续、可复现失败时才升级排查。
- 仓库继续禁止记录真实 IPRoyal 服务器、端口和凭证。

## 13. Codex 修改规则前必须先做的事

每次新会话 / 新任务先读取：

1. `README.md`
2. `docs/CODEX-HANDOFF.md`
3. `overwrite/openclash-overwrite.conf`
4. `rules/manual-direct.yaml`
5. `docs/acceptance-log.md`
6. `CHANGELOG.md`

修改前必须回答：

- 这次需求应该改主 `rules!`，还是只改 `Manual-Direct`？
- 是否会与 OneDrive Consumer 的“强制美国”例外冲突？
- 是否会整体覆盖 OpenClash 自动生成 provider？
- 是否会把范围过大的全球域名强制 DIRECT？
- 是否有日志证明当前规则确实误匹配，而不是建连 timeout？
- 是否会把 IPRoyal 密钥或端点写入 GitHub？答案必须为否。
- TikTok 规则是否仍早于 `Manual-Direct`、`GEOSITE,cn` 和最终 `MATCH`？

原则：**先根据日志定位，再做最小修改。不要看到 timeout 就不断追加域名或重写 DNS。**

## 14. 修改后的验收清单

每次更新后检查：

1. OpenClash 可正常启动。
2. 无：
   ```text
   Parse config error
   not found rule-set
   ```
3. `Manual-Direct` provider 更新成功。
4. `TikTok-ISP` 只包含 `IPRoyal-US-ISP`，`美国` 不包含该节点。
5. TikTok 域名 → `TikTok-ISP[IPRoyal-US-ISP]`，TikTok DNS 也走该组。
6. 私网访问 DIRECT。
7. 中国常规网站命中 `GeoSite(cn)` / `GeoIP(cn)` → DIRECT。
8. Google / GitHub / ChatGPT 等海外服务 → 美国。
9. Microsoft Store 系统端点 → Manual-Direct / DIRECT。
10. Microsoft Account 认证端点 → Manual-Direct / DIRECT。
11. `onedrive.live.com` / `www.onedrive.live.com` → 美国。
12. `gstatic.com` → 美国。
13. 不要仅看瞬时 `0 B/s` 判断连接失败，应看累计上下行和实际应用表现。

## 15. 当前已验证的关键结果

2026-09-07：

- TikTok 专用 IPRoyal 结构已纳入远程规则；凭证只保留在 OpenClash 本地模块。
- OneDrive Consumer 强制美国后，规则命中已验证：
  ```text
  onedrive.live.com -> DomainSuffix(onedrive.live.com) -> 美国
  ```
- Microsoft Store 关键端点已验证 DIRECT。
- Microsoft Store 队列卡死最终通过 `Reset-AppxPackage` + 重启解决。
- 当前不要再基于该 Store 故障修改 OpenClash 网络规则。

---

后续 Codex 应把本文件视为“当前设计与历史决策记录”。如果实际运行日志与本文冲突，以**最新实际运行配置 + 可复现日志**为准，并同步更新本文与 `CHANGELOG.md`。
