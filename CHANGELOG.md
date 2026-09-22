# 版本记录

只记录形成版本的长期变化。临时命令、失败尝试和排查流水不写入本文件。

## tiktok-hybrid-device-us v1.0.0 — 2026-09-21

状态：稳定

验证日期：2026-09-22

方案：`tiktok-hybrid-device-us`

需求：H1–H9

- 新建独立方案，不修改稳定方案 `tiktok-sockstun-us v1.0.0`、其 `v1.1.0` 日本候选或兼容覆写入口；
- `192.168.100.248/32` 的 TikTok 通过现有机场`美国`策略组访问；
- 其他设备泄漏到 OpenClash 的可识别 TikTok 连接继续 `REJECT`，手机 SocksTun/IPRoyal 路径保留；
- TikTok DNS 改为经`美国`策略解析，以支持指定设备；其他设备可以获得解析结果，但连接权限仍由路由规则控制；
- Google/Google Play、中国直连、Manual-Direct、局域网直连和当前中文界面稳定设置保持不变；
- 本方案不包含尚未验收的日本策略组和人工日本规则。

2026-09-22 用户完成真实设备测试并确认正常，随后明确批准稳定发布。稳定标签为 `tiktok-hybrid-device-us-v1.0.0`；本方案不得与其他完整覆写叠加，根目录兼容覆写保持指向原 `currentProfile`。

## v1.1.0 — 2026-09-18

状态：候选，待真实 OpenClash 设备验收

方案：`tiktok-sockstun-us`

需求：R1–R10

在保持 v1.0.0 的 R1–R8 行为不变的基础上：

- 新增手选`日本`策略组，自动收录名称带日本、东京、大阪、JP、Japan 等标识的机场节点；
- 日本组没有匹配节点时回退 `REJECT`，且排除名称以 `IPRoyal-` 开头的节点；
- 新增 `rules/manual-japan.yaml` 和 `Manual-Japan` 规则集；
- `t27.cdn2020.com`、`hscangku.com`、`222.0cck.cc`、`51cg1.com`、`tx.doudou520.online`、`mts.hhjd.mobi` 优先走`日本`；
- 日本规则位于 Google/Google Play 之后、人工直连和中国规则之前；
- DNS、TikTok、Google、人工直连、最终美国出口和 OpenClash 中文界面设置均未修改。

本候选不更新当前稳定版本、兼容覆写入口或 Git 标签。

## v1.0.0 — 2026-09-17

状态：稳定

方案：`tiktok-sockstun-us`

需求：R1–R8

首次把当前已验证配置固化为正式版本：

- TikTok 只由手机 SocksTun 通过 IPRoyal ISP SOCKS5 代理，泄漏到 OpenClash 的 TikTok 被拒绝；
- 其他国外流量走用户手工选择的机场美国节点；
- 中国大陆、局域网和人工维护域名直连；
- Google 与 Google Play 使用一致的美国路由和 DNS，实际下载已恢复正常；
- Fake-IP（增强）模式由用户手工选择，不写入覆写的 `[General]`；
- “禁用 QUIC”不勾选后，淘宝实际刷新恢复正常；
- “绕过中国大陆 IPv4”保持不勾选；
- IPRoyal 入口 IPv4 `/32` 必须加入本地 IPv4 网络绕过列表；
- 保留 `rules/manual-direct.yaml` 作为持续维护的共享人工直连规则。

本版本来源于提交 `b65a814` 所代表的已验证行为；正式 `v1.0.0` 标签包含本次版本化目录、维护规范和自动校验文件。
