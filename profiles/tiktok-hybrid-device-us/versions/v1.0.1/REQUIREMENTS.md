# tiktok-hybrid-device-us v1.0.1

状态：候选

验证日期：待真实 OpenClash 设备验收

版本类型：保持需求结构不变的授权设备地址修订

本版本从稳定版 `v1.0.0` 派生，只把 H1 授权设备由 `192.168.100.248/32` 改为 `192.168.100.198/32`。H2–H9、DNS、策略组、规则顺序和中文界面设置全部保持不变。

## 需求

| 编号 | 冻结需求 | 实现 |
| --- | --- | --- |
| H1 | 固定设备 `192.168.100.198` 的 TikTok 使用现有机场`美国`策略组 | 来源 IP 与 `GEOSITE,tiktok` 使用 `AND` 规则，优先于通用拒绝规则 |
| H2 | 除 H1 指定设备外，TikTok 默认仍由手机 SocksTun 通过 IPRoyal ISP；泄漏到 OpenClash 的可识别连接失败关闭 | 指定设备规则之后保留 `GEOSITE,tiktok,REJECT` |
| H3 | 除 TikTok 外的国外流量走机场美国节点 | 最终 `MATCH,美国`，用户手工选节点，空组回退 `REJECT` |
| H4 | 中国大陆域名和 IP 直连 | `GEOSITE,cn,DIRECT`、`GEOIP,CN,DIRECT,no-resolve` |
| H5 | 保留人工维护的额外直连域名 | `RULE-SET,Manual-Direct,DIRECT`，共享 `rules/manual-direct.yaml` |
| H6 | 局域网和私有地址直连 | 私网 GeoSite、GeoIP 和 CIDR 位于最前 |
| H7 | Google 与 Google Play 继续使用已经验证的美国路径 | Google 路由和 DNS 位于中国规则之前，下载域名显式走`美国` |
| H8 | OpenClash 插件运行选项全部由用户在中文界面手工设置 | 覆写只有 `[YAML]`，不写 `[General]` |
| H9 | 保持当前国内应用稳定设置 | Fake-IP（增强）模式；“禁用 QUIC”和“绕过中国大陆 IPv4”均不勾选 |

## 继承与变化

- 继承：`v1.0.0` 的 H2–H9、DNS、TikTok 通用拒绝、Google/Google Play、Manual-Direct、中国直连、局域网直连和最终美国出口；
- 修改：H1 的唯一授权来源从 `192.168.100.248/32` 改为 `192.168.100.198/32`；
- 删除：`192.168.100.248/32` 不再获得 TikTok 机场美国出口权限，将与其他未授权设备一样命中通用 `REJECT`；
- 新增：无。

## TikTok 路径

```text
192.168.100.198 的 TikTok → OpenClash → 美国策略组 → TikTok
其他手机的 TikTok          → 手机 SocksTun → IPRoyal SOCKS5 → TikTok
其他设备泄漏的 TikTok      → OpenClash → REJECT
```

`192.168.100.198` 必须在路由器 DHCP 中固定到目标设备。不得同时把旧地址 `.248` 保留为授权地址。

## DNS 边界

TikTok DNS 继续经`美国`策略连接的公共 DNS 解析。其他设备可能获得解析结果，但可识别的 TikTok 连接仍由 `GEOSITE,tiktok,REJECT` 拒绝；不要求划分 VLAN 或独立 DNS。

## 中文界面设置

全部沿用 `v1.0.0`：运行内核 Meta、Fake-IP（增强）模式、规则模式；“禁用 QUIC”和“绕过中国大陆 IPv4”均不勾选；所有设置继续由用户在中文界面手工完成，覆写不得加入 `[General]`。

## 规则顺序

```text
私网/LAN                              → DIRECT
192.168.100.198 + TikTok              → 美国
其他可识别 TikTok                     → REJECT
Google/Google Play                    → 美国
Manual-Direct                         → DIRECT
中国大陆域名/IP                       → DIRECT
其他所有流量                          → 美国
```

## 验收清单

1. OpenClash 能加载本候选覆写，且覆写只有 `[YAML]`。
2. `192.168.100.198` 已通过 DHCP 固定到目标设备。
3. `.198` 访问 TikTok 时命中 `AND` 规则并使用`美国`，不能命中 `DIRECT` 或 `REJECT`。
4. `.248` 在不使用 SocksTun 时访问 TikTok，命中 `GeoSite(tiktok) using REJECT`。
5. 另一台未授权设备在不使用 SocksTun 时同样命中 `REJECT`。
6. 使用 SocksTun 的其他手机仍通过 IPRoyal 访问 TikTok。
7. 其他国外流量、Google Play、中国直连、Manual-Direct、局域网和淘宝按稳定基线回归正常。

## 发布边界

真实设备完成以上验收并获得明确批准前，本版本保持 `candidate`：不修改 `v1.0.0`，不移动其标签，不创建 `v1.0.1` 稳定标签，也不改变根目录兼容覆写。
