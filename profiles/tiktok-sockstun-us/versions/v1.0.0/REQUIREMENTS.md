# tiktok-sockstun-us v1.0.0

状态：稳定

验证日期：2026-09-17

本文件是 `v1.0.0` 的冻结需求和验收合同。发布后不得直接修改；需求或行为变化必须创建新版本。

## 需求

| 编号 | 冻结需求 | 实现 |
| --- | --- | --- |
| R1 | TikTok 只由手机 SocksTun 通过 IPRoyal ISP 代理，其他路径失败关闭 | OpenClash 对 TikTok DNS 返回空结果并拒绝可识别连接 |
| R2 | 除 TikTok 外的国外流量走机场美国节点 | 最终 `MATCH,美国`，用户手工选节点，空组回退 `REJECT` |
| R3 | 中国大陆域名和 IP 直连 | `GEOSITE,cn,DIRECT`、`GEOIP,CN,DIRECT,no-resolve` |
| R4 | 保留人工维护的额外直连域名 | `RULE-SET,Manual-Direct,DIRECT`，数据来自 `rules/manual-direct.yaml` |
| R5 | 局域网和私有地址直连 | 私网 GeoSite、GeoIP 和 CIDR 位于最前 |
| R6 | Google 与 Google Play 稳定走机场美国节点 | Google 路由和 DNS 位于中国规则之前，下载域名显式走`美国` |
| R7 | 插件运行选项由用户在中文界面手工设置 | 覆写只有 `[YAML]`，不写 `[General]` |
| R8 | 国内应用在 Fake-IP（增强）模式下稳定使用 | “禁用 QUIC”不勾选；淘宝已完成实际刷新验证 |

## 唯一 TikTok 路径

```text
TikTok 应用 → 手机 SocksTun → IPRoyal SOCKS5 → TikTok
```

OpenClash 中不得存在 IPRoyal 节点或 `TikTok-ISP` 策略组。IPRoyal 入口 IPv4 `/32` 必须加入 OpenClash 的本地 IPv4 网络绕过列表。

## 中文界面设置

| 设置项 | v1.0.0 固定值 |
| --- | --- |
| 运行内核 | Meta |
| 运行模式 | Fake-IP（增强）模式 |
| 代理模式 | 规则模式 |
| 路由器本机代理 | 勾选 |
| UDP 代理 | 勾选 |
| 禁用 QUIC | 不勾选 |
| IPv6 代理 | 不勾选 |
| IPv6 DNS | 不勾选 |
| 域名嗅探 | 勾选 |
| 纯 IP 连接嗅探 | 勾选 |
| 进程查找模式 | 不勾选 |
| 仅允许内网访问 | 勾选 |
| 旁路网关兼容模式 | 不勾选 |
| 绕过常用端口 | 不勾选 |
| 绕过中国大陆 IPv4 | 不勾选 |
| 绕过中国大陆 IPv6 | 不勾选 |
| 中国大陆 IP 列表自动更新 | 不勾选 |
| 仅代理命中规则流量 | 不勾选 |
| OpenClash 本地自定义规则 | 不勾选 |
| 绕过代理服务器地址 | 勾选 |
| 自定义 DNS | 勾选 |
| DNS 重定向 | 勾选，并选择 Dnsmasq 转发 |
| 遵循分流规则 | 勾选 |
| 自动追加默认 DNS | 不勾选 |
| 追加上游分配 DNS | 不勾选 |
| Fake-IP 持久化缓存 | 勾选 |
| Fake-IP 过滤 | 勾选，并选择黑名单模式 |
| GeoIP 数据库 | 勾选 |
| GeoIP 自动更新 | 勾选 |
| GeoSite 自动更新 | 勾选 |

SocksTun 固定设置：`UDP relay over TCP` 不勾选、`Remote DNS` 勾选、`DNS IPv4` 保持 `8.8.8.8`、IPv4 勾选、IPv6 和 Global 不勾选、Apps 只选择 TikTok。

## 规则顺序

```text
私网/LAN                    → DIRECT
TikTok DNS 泄漏            → 空响应
TikTok 可识别连接          → REJECT
Google/Google Play          → 美国
Manual-Direct              → DIRECT
中国大陆域名/IP            → DIRECT
其他所有流量               → 美国
```

## 已确认稳定结果

- OpenClash 可以加载覆写；
- Google Play 可以完成应用下载，不再卡在 0%、31% 或 98%；
- `services.googleapis.cn` 和 Google Play 下载域名使用一致的美国出口和 DNS；
- “禁用 QUIC”不勾选并重启 OpenClash 后，淘宝恢复正常刷新；
- 手机 SocksTun 使用 IPRoyal 时，TikTok 可以访问；停止 SocksTun 后 TikTok 不得回退到其他出口。

## 验收清单

1. OpenClash 中不存在 `TikTok-ISP`，`美国`组不含 IPRoyal。
2. 启动 SocksTun 后 TikTok 可访问；停止后不可访问。
3. 其他国外网站命中最终 `MATCH` 并走`美国`。
4. Google Play 完整下载一个应用；Google 下载相关域名不得命中中国直连。
5. 普通中国大陆网站命中中国规则并直连。
6. `rules/manual-direct.yaml` 中的域名命中 `Manual-Direct` 并直连。
7. 局域网和私有地址直连。
8. 覆写只包含 `[YAML]`，没有 `[General]`。
9. “禁用 QUIC”不勾选，淘宝连续刷新正常。

## 禁止直接修改

不得覆盖本目录中的文件。任何规则、设置、人工直连列表或需求变化都必须创建新版本，并按 `MAINTENANCE.md` 完成验证、提交、推送和标签。
