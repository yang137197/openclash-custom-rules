# v2.0.0 正式版：OpenClash 中文界面设置

本页只适用于所有手机 TikTok 使用 SocksTun/IPRoyal 的 v2.0.0 正式版。技术基准为文末指南；旧版“必须关闭大陆绕过/QUIC”的说明不适用。所有步骤由用户手工执行，覆写不写 UCI。

用户报告环境：OpenClash v0.48.002、alpha-gbc76c13。2026-10-15 用户已总体确认候选验证通过并批准发布，未另行提供版本回读；在其他安装环境中，若缺少“规则模式”过滤或 CN 数据源选择、加载报错，停在此处并提供调试日志，不猜测其他开关。

## 1. 保存回退材料

保存当前启用的机场配置、覆写模块和插件设置截图；保留 IPRoyal 入口绕过条目，私密地址与凭据不要放入仓库。记录哪些旧模块原来启用。

## 2. 安装正式覆写

1. 进入 **服务 → OpenClash → 运行状态**，点击顶部 **覆写模块** 按钮。
2. 点击 **添加新模块 → 本地模块**，上传同目录 `openclash-overwrite.conf`。
3. 名称建议 `tiktok-sockstun-us-v2.0.0`；匹配配置选择当前机场配置，底层匹配值必须为完整路径（如 `/etc/openclash/config/实际文件名.yaml`），不能只填文件名。
4. 保存模块；停用旧完整覆写及会修改 DNS/规则/策略组的内建 default、Google_Play 或其他模块。仅在它们原本启用时停用，不删除回退文件。
5. 启用本版本，继续完成以下设置，最后统一保存并重启。

本地文件可直接上传。正式版固定 URL 见下方；兼容入口现对应 v2.0.0，但固定版本更便于回退，两者只选一个。

固定 URL：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-sockstun-us-v2.0.0/profiles/tiktok-sockstun-us/versions/v2.0.0/openclash-overwrite.conf
```

使用订阅链接时，仍从运行状态顶部“覆写模块 → 添加新模块 → 订阅链接”导入，只匹配当前机场配置。当前模块继续从 GitHub main 拉取原有人工直连数据，并从 MetaCubeX 拉取 CN MRS；首次加载需要这两个地址可达。

## 3. 模式与流量控制

以下均在 **服务 → OpenClash** 下；中文名称可能因安装版本略有差异，以括号中的功能名核对。

| 页面 | 设置 | 值 |
| --- | --- | --- |
| 运行状态/版本更新 | 运行内核 | Meta/Mihomo，使用支持本版本字段的内核 |
| 插件设置 → 模式设置 | 运行模式 | Fake-IP（增强），非 TUN、非混合 |
| 模式设置/运行状态 | 代理模式 | 规则模式 |
| 插件设置 → 模式设置 | UDP 流量转发 | 勾选；所选机场节点须支持所需 UDP |
| 插件设置 → 流量控制 | 路由器本机代理 | 勾选 |
| 同上 | 实验性：绕过指定区域 IPv4 | **绕过中国大陆**；不是“绕过海外” |
| 同上 | 中国大陆域名数据源 | **MetaCubeX 规则 cn.mrs（默认）** |
| 同上 | 禁用 QUIC | **勾选，作为默认基线**；非所有业务的绝对要求 |
| 同上 | 绕过代理服务器地址 | 勾选 |
| 同上 | 仅允许内网访问 | 勾选 |
| 同上 | 仅允许常用端口流量（Common Ports） | 关闭，不限制代理端口范围 |
| 插件设置 → 模式设置 | 旁路网关兼容 | 主路由或回程正常时关闭；旁路由绕过流量回程不成立时才开启 |
| 插件设置 → IPv6 设置 | IPv6 代理、允许 IPv6 类型 DNS 解析、区域 IPv6 绕过 | 本版本均关闭 |

在“流量控制 → 本地 IPv4 网络绕过列表”保留现有局域网条目，并追加 **IPRoyal 面板所示服务器 IPv4/32**；不要填手机 IP、整个网段或代理账号。机场服务器绕过不能自动替代这个独立 SocksTun 入口。

大陆绕过使真实国内 IP 在防火墙层跳过核心。旁路由被绕过的连接保留客户端源地址，因此需要上游能回程；这个拓扑条件与 DNS 或域名规则无关。

禁用 QUIC 在大陆绕过模式下阻断适用范围内的非大陆 UDP/443。人工指定 DIRECT、但目标在境外的远程控制/隧道等业务仍可能受影响；本版本不承诺这些业务都兼容。出现明确相关故障时保留日志，再调整此项，不循环猜测。

## 4. DNS 与 Meta 设置

| 页面 | 设置 | 值 |
| --- | --- | --- |
| 插件设置 → DNS 设置 | 本地 DNS 劫持/DNS 重定向 | **Dnsmasq 转发** |
| 覆写设置 → DNS 设置 | 自定义上游 DNS | 勾选；若界面要求至少一条，保留 NameServer 类型 HTTPS、地址 223.5.5.5、端口 443，其他最终列表由模块替换 |
| 同上 | 遵守路由规则/遵循分流规则 | 勾选 |
| 同上 | 附加上游 DNS、自动追加默认 DNS | 均不勾选；本版本明确使用国内 DoH |
| 同上 | Fallback 服务器/自定义 Fallback-Filter | 不启用；模块显式清空/删除 |
| 同上 | Fake-IP 持久化 | 勾选 |
| 同上 | 自定义 Fake-IP-Filter | 勾选，模式选 **规则（rule）**；不要再填旧黑名单通配符列表 |
| 覆写设置 → Meta 设置 | 域名嗅探、纯 IP 嗅探 | 勾选 |
| 同上 | 进程查找 | 关闭（off） |
| 覆写设置 → 规则设置 | 仅代理命中规则流量 | 关闭，避免其余国外流量直连 |
| 同上 | 额外本地自定义规则 | 关闭，完整规则由本模块管理 |

模块最终管理的国内 DoH 是 `https://223.5.5.5/dns-query`、`https://1.12.12.12/dns-query`。Google/Play 单独使用经美国的公共 DoH；TikTok 保留泄漏查询策略。不要再叠加 MosDNS/SmartDNS/AdGuardHome 的 DNS 转发链；已有这类服务时先核对实际 DNS 链，不能仅凭本页假定已经移除冲突。

**Fake-IP 过滤顺序必须是：TikTok/Google fake-ip → 本地/Manual-Direct real-ip → CN MRS real-ip → 其余 fake-ip。** 模块强制替换这一列表，避免 Google 同时属于 CN 分类时提前拿到真实地址而旁路。Nameserver-policy 保留 Google 专用解析；区域绕过黑名单不能单独替代这两项。使用客户端私有 DNS/HTTPDNS 或缓存真实 IP 的连接不受这项域名保证覆盖。

IPv6 代理关闭不等于全网 IPv6 被关闭。若客户端仍有另一条 IPv6 网关或私有 DNS，不能据此宣称 TikTok 已无旁路；SocksTun 的按应用接管及实机验证仍必需。

## 5. 数据更新与应用

1. **插件设置 → GEO 数据库订阅**：启用使用中的 GeoSite、GeoIP 自动更新，先确认现有数据库下载有效。CN MRS 不能替代 TikTok/Google/私网所用的 GeoSite 数据。
2. **插件设置 → 大陆白名单订阅**：启用大陆 IPv4 列表自动更新，先手动更新并确认成功；IPv6 未使用，无需启用 IPv6 列表。本版本的 CN MRS 由 provider 每 86400 秒更新，与防火墙 IP 列表是两份不同数据。
3. 保存设置，进入 **运行状态 → 重启 OpenClash**。仅保存文件或重载防火墙不会重跑覆写。
4. 在仪表盘 **美国**组手工选择机场美国节点；确认组中没有 IPRoyal。
5. 刷新客户端 DNS 状态后再验收，避免旧模式缓存的真实地址或 Fake-IP 影响观察；不要在故障取证前反复清缓存。

SocksTun 继续仅选择 TikTok，Remote DNS 开启、IPv4 开启、IPv6/Global 关闭；IPRoyal 凭据只在手机保存。OpenClash 不会把普通 TikTok 连接“交给”手机 VPN。

## 6. 只做这一轮验收

按 REQUIREMENTS.md 的未勾选清单执行：国内 App 连续刷新、人工直连/局域网、Google Play 完整下载、其他国外网站、SocksTun 开关下的 TikTok。

- 国内普通域名应获得真实 IPv4；Google/Play 域名应保持 Fake-IP，Google 连接走美国。
- 国内连接可能已在防火墙旁路，核心面板中没有它们不代表失败；仅看到 DIRECT 也不证明应用响应成功。
- 某项失败时，先到 **运行日志 → 调试日志 → 生成日志**，保留 App、时间及失败请求。没有日志不归因于“丢包”，不连续更换开关。
- 如模块无法加载、TikTok 出口不符或 Google Play 错误直连，停止本轮验收并回退。

## 7. 回退

停用 v2.0.0，恢复此前唯一启用的旧模块及设置截图。若回到主方案 v1.0.0，尤其恢复：大陆 IPv4 绕过关闭、禁用 QUIC 不勾选、Fake-IP 过滤黑名单模式，以及旧版 DNS/更新设置；按旧版 REQUIREMENTS.md 核对后重启。只换回模块、保留 v2 界面开关不构成完整回退。

## 技术依据

指南及子文档核对日期：2026-10-15。dev 文档会变化；这些引用不是对用户所装版本的兼容认证。

- [入口及诊断流程](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md)
- [08-settings-mode-traffic.md §8.2.1、§8.3.2、§8.3.5、§8.3.9–10](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/08-settings-mode-traffic.md)
- [09-settings-dns-ac-ipv6.md §9.1.1、§9.5](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/09-settings-dns-ac-ipv6.md)
- [10-settings-geo-misc-src.md §10.1](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/10-settings-geo-misc-src.md)
- [11-overwrite-settings.md §11.3、§11.4、§11.6](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/11-overwrite-settings.md)
- [16-overwrite-module-format.md §16.1.1、§16.2.3](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)
- [06-firewall-options-dnsmasq.md §6.2（旁路回程）](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/06-firewall-options-dnsmasq.md)

按指南 §11.3 和 §16.1 对未展开的字段查证其指定权威资料：[Mihomo DNS 的 rule 过滤、direct-nameserver 和策略语义](https://wiki.metacubex.one/config/dns/)。classical provider 在 rule 过滤中仅生效域名规则；现有 124 条均为域名规则，因此无需复制另一份人工列表。
