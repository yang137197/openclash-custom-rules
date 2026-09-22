# tiktok-hybrid-device-us v1.0.0

状态：稳定

验证日期：2026-09-22

版本类型：新方案首个稳定版本

本方案与稳定方案 `tiktok-sockstun-us` 的 TikTok 出口要求互斥，因此使用独立方案 ID、独立版本目录和独立覆写 URL。不得与其他完整覆写同时启用。

## 需求

| 编号 | 冻结需求 | 实现 |
| --- | --- | --- |
| H1 | 固定设备 `192.168.100.248` 的 TikTok 使用现有机场`美国`策略组 | 来源 IP 与 `GEOSITE,tiktok` 使用 `AND` 规则，优先于通用拒绝规则 |
| H2 | 除 H1 指定设备外，TikTok 默认仍由手机 SocksTun 通过 IPRoyal ISP；泄漏到 OpenClash 的可识别连接失败关闭 | 指定设备规则之后保留 `GEOSITE,tiktok,REJECT` |
| H3 | 除 TikTok 外的国外流量走机场美国节点 | 最终 `MATCH,美国`，用户手工选节点，空组回退 `REJECT` |
| H4 | 中国大陆域名和 IP 直连 | `GEOSITE,cn,DIRECT`、`GEOIP,CN,DIRECT,no-resolve` |
| H5 | 保留人工维护的额外直连域名 | `RULE-SET,Manual-Direct,DIRECT`，共享 `rules/manual-direct.yaml` |
| H6 | 局域网和私有地址直连 | 私网 GeoSite、GeoIP 和 CIDR 位于最前 |
| H7 | Google 与 Google Play 继续使用已经验证的美国路径 | Google 路由和 DNS 位于中国规则之前，下载域名显式走`美国` |
| H8 | OpenClash 插件运行选项全部由用户在中文界面手工设置 | 覆写只有 `[YAML]`，不写 `[General]` |
| H9 | 保持当前国内应用稳定设置 | Fake-IP（增强）模式；“禁用 QUIC”和“绕过中国大陆 IPv4”均不勾选 |

## TikTok 路径

```text
192.168.100.248 的 TikTok → OpenClash → 美国策略组 → TikTok
其他手机的 TikTok          → 手机 SocksTun → IPRoyal SOCKS5 → TikTok
其他设备泄漏的 TikTok      → OpenClash → REJECT
```

`192.168.100.248` 必须在路由器 DHCP 中保持固定。若地址改变，该设备会落入通用 TikTok 拒绝规则。增加、删除或更换授权设备属于路由行为变更，必须创建本方案的新候选版本，不能直接修改已发布版本。

## DNS 边界

为了让 H1 设备能够解析 TikTok，`geosite:tiktok` 使用经`美国`策略连接的公共 DNS，不再返回空结果。此 DNS 策略是全局的，OpenClash 不能仅靠 `nameserver-policy` 按来源设备返回不同结果。

因此，其他设备也可能获得 TikTok 域名解析结果，但解析成功不代表连接获准；随后可识别的 TikTok 连接仍由 `GEOSITE,tiktok,REJECT` 拒绝。本需求不要求为此划分独立 VLAN 或独立 DNS。

使用 SocksTun 的手机继续启用 Remote DNS，TikTok DNS 应由 SocksTun 内部处理。

## 与其他方案的边界

- 不修改稳定方案 `tiktok-sockstun-us v1.0.0`；
- 不修改其日本候选 `v1.1.0`；
- 本方案不包含`日本`策略组或 `Manual-Japan`；
- 不更新根目录兼容覆写 `overwrite/openclash-overwrite.conf`；
- 只能启用本方案的完整覆写，不能与其他稳定方案或日本候选叠加。

## 中文界面设置

沿用 `tiktok-sockstun-us v1.0.0` 的中文界面设置，重点保持：

| 设置项 | 固定值 |
| --- | --- |
| 运行内核 | Meta |
| 运行模式 | Fake-IP（增强）模式 |
| 代理模式 | 规则模式 |
| UDP 代理 | 勾选 |
| 禁用 QUIC | 不勾选 |
| IPv6 代理、IPv6 DNS | 不勾选 |
| 域名嗅探、纯 IP 连接嗅探 | 勾选 |
| 绕过中国大陆 IPv4、IPv6 | 不勾选 |
| OpenClash 本地自定义规则 | 不勾选 |
| 自定义 DNS、DNS 重定向、遵循分流规则 | 勾选 |
| 绕过代理服务器地址 | 勾选 |

需要 SocksTun/IPRoyal 的其他手机，仍须把 IPRoyal 入口 IPv4 `/32` 手工加入 OpenClash 的本地 IPv4 网络绕过列表。

## 规则顺序

```text
私网/LAN                              → DIRECT
192.168.100.248 + TikTok              → 美国
其他可识别 TikTok                     → REJECT
Google/Google Play                    → 美国
Manual-Direct                         → DIRECT
中国大陆域名/IP                       → DIRECT
其他所有流量                          → 美国
```

## 验收清单

1. OpenClash 能加载本候选覆写，且覆写只有 `[YAML]`。
2. `192.168.100.248` 地址已通过 DHCP 固定到目标设备。
3. 该设备访问 TikTok 时，实时日志命中 `AND` 规则并使用`美国`，不能命中 `DIRECT` 或 `REJECT`。
4. 另一台未授权设备在不使用 SocksTun 时访问 TikTok，实时日志命中 `GeoSite(tiktok) using REJECT`。
5. 未授权手机启动 SocksTun 后，TikTok 仍通过 IPRoyal 使用；OpenClash 不得把内部 TikTok 流量改送机场。
6. 其他国外网站命中最终 `MATCH` 并走`美国`。
7. 使用 Google Play 完整下载一个应用，相关域名继续走`美国`。
8. 中国大陆网站、Manual-Direct 和局域网分别保持直连。
9. “禁用 QUIC”和“绕过中国大陆 IPv4”均不勾选，淘宝连续刷新正常。

## 稳定验收记录

2026-09-22，用户完成真实设备测试并确认运行正常，随后明确授权将本版本发布为稳定版并推送标签。本方案的稳定发布不改变根目录兼容覆写；兼容入口继续对应 `profiles/catalog.json` 的 `currentProfile`。

本目录自稳定发布后不可直接修改。任何规则、授权设备、DNS、界面设置或需求变化都必须创建新版本。
