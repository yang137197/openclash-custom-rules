# tiktok-sockstun-us v1.1.0

状态：候选

验证日期：待真实 OpenClash 设备验收

版本类型：兼容新增需求的次版本候选

本版本继承 `v1.0.0` 的 R1–R8，并新增日本策略组和人工日本规则。`v1.0.0` 继续作为当前稳定版本；本候选在真实设备验收前不得标记稳定或替换兼容覆写入口。

## 需求

| 编号 | 需求 | 实现 |
| --- | --- | --- |
| R1 | TikTok 只由手机 SocksTun 通过 IPRoyal ISP 代理，其他路径失败关闭 | OpenClash 对 TikTok DNS 返回空结果并拒绝可识别连接 |
| R2 | 除 TikTok 和人工日本规则外的国外流量走机场美国节点 | 最终 `MATCH,美国`，用户手工选节点，空组回退 `REJECT` |
| R3 | 中国大陆域名和 IP 直连 | `GEOSITE,cn,DIRECT`、`GEOIP,CN,DIRECT,no-resolve` |
| R4 | 保留人工维护的额外直连域名 | `RULE-SET,Manual-Direct,DIRECT`，数据来自 `rules/manual-direct.yaml` |
| R5 | 局域网和私有地址直连 | 私网 GeoSite、GeoIP 和 CIDR 位于最前 |
| R6 | Google 与 Google Play 稳定走机场美国节点 | Google 路由和 DNS 位于人工日本规则及中国规则之前 |
| R7 | 插件运行选项由用户在中文界面手工设置 | 覆写只有 `[YAML]`，不写 `[General]` |
| R8 | 国内应用在 Fake-IP（增强）模式下稳定使用 | “禁用 QUIC”不勾选，现有设置不变 |
| R9 | 新增日本手选策略组并自动收录日本节点 | `日本`组按日本、东京、大阪、JP、Japan 等名称标识筛选订阅节点，空组回退 `REJECT` |
| R10 | 指定特殊网站走日本节点 | `RULE-SET,Manual-Japan,日本`，数据来自 `rules/manual-japan.yaml` |

## 继承与变化

- 继承：R1–R8、DNS、Fake-IP、TikTok 防泄漏、Google/Google Play、人工直连和最终美国出口全部保持 `v1.0.0` 行为。
- 新增：`日本`手选策略组、`Manual-Japan` 规则集、`rules/manual-japan.yaml`。
- 修改：无既有需求被删除；R2 明确排除人工日本规则命中的流量。
- 删除：无。

本版本不修改 OpenClash 中文界面运行选项，也不修改 `rules/manual-direct.yaml`。

## 日本策略组

- 类型：`select`，由用户在 OpenClash 中手工选择具体日本节点。
- 节点来源：当前机场订阅中名称带 `🇯🇵`、`日本`、`东京`、`東京`、`大阪`、`名古屋`、`埼玉`、`Japan`、独立 `JP`、`Tokyo` 或 `Osaka` 标识的节点。
- 失败关闭：没有匹配节点时使用 `REJECT`，不得回退到美国或直连。
- IPRoyal 隔离：名称以 `IPRoyal-` 开头的节点不得进入日本组。

## 人工日本规则

`rules/manual-japan.yaml` 当前包含：

- `t27.cdn2020.com`
- `hscangku.com` 及其子域名
- `222.0cck.cc`
- `51cg1.com` 及其子域名
- `tx.doudou520.online`
- `mts.hhjd.mobi`

规则优先级低于 TikTok 和 Google/Google Play，高于 `Manual-Direct`、中国规则和最终 `MATCH,美国`。

## 中文界面设置

所有设置继承 `v1.0.0`，无需新增或修改 OpenClash 插件选项。应用候选覆写后，只需在`日本`组手工选择一个已自动收录的日本节点。

## 规则顺序

```text
私网/LAN                    → DIRECT
TikTok DNS 泄漏            → 空响应
TikTok 可识别连接          → REJECT
Google/Google Play          → 美国
Manual-Japan               → 日本
Manual-Direct              → DIRECT
中国大陆域名/IP            → DIRECT
其他所有流量               → 美国
```

## 验收清单

1. OpenClash 能加载候选覆写，且覆写只有 `[YAML]` 配置段。
2. `日本`组只包含名称匹配的日本节点，不包含 IPRoyal；用户可以手工选择新日本节点。
3. 日本节点为空时，`日本`组为 `REJECT`，不会回退到美国或直连。
4. `t27.cdn2020.com`、`hscangku.com`、`222.0cck.cc`、`51cg1.com`、`tx.doudou520.online`、`mts.hhjd.mobi` 分别命中 `Manual-Japan` 并走`日本`。
5. 通过 OpenClash 实时日志确认上述网站命中 `Manual-Japan` 并使用所选节点；另行验证该节点的公网出口位于日本，不能只以页面能打开作为验收。
6. R1–R8 按 `v1.0.0` 清单完整回归，尤其确认 TikTok 不泄漏、Google Play 完整下载、人工直连和中国直连不变。

## 发布边界

真实设备验收前，本版本只保持 `candidate`：

- 不更新 `overwrite/openclash-overwrite.conf`；
- 不修改 `profiles/catalog.json` 中的当前稳定版本；
- 不创建稳定标签；
- 不要求现有路由器切换。
