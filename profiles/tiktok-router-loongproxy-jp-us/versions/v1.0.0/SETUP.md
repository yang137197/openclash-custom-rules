# tiktok-router-loongproxy-jp-us v1.0.0 — 部署与验收

**状态：candidate，未完成 CatWrt/OpenClash 实机验收。** 用户于 2026-10-16 报告 OpenClash v0.48.002 / alpha-gbc76c13；PC 上的日本首跳 → Loongproxy 美国 SOCKS5 已成功。其他首跳失败原因尚未确认。

## 本轮导入两个配套模块

入口：**服务 → OpenClash → 运行状态 → 顶部「覆写模块」按钮**，弹出模块编辑窗口；不是菜单「覆写设置」。

1. 保存当前配置、启用模块清单及插件设置截图。保留旧文件，停用其他完整分流覆写、旧本地 ISP 模块，以及原本启用且会修改 DNS/规则/策略组的 default、Google_Play 等模块。
2. **添加新模块 → 本地模块**：上传仓库外已填好本次测试参数的 `tiktok-loongproxy-jp-us-local.conf`，无需修改地址、端口、账号、密码。公共仓库 `.example` 仅是占位模板。只保留一个名为 `TikTok-ISP-Local` 的节点。
3. **添加新模块 → 订阅链接**：使用以下候选分支 URL；模块名建议 `tiktok-router-loongproxy-jp-us-cloud`。

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/feature/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

4. 两个模块匹配同一当前机场配置的**完整路径**，例如 `/etc/openclash/config/实际机场文件名.yaml`；也支持 `all`，但会作用于所有配置，不能只填文件名。云模块放在本地节点模块上方；列表越靠上合并越晚。启用二者，核对下表后统一**重启 OpenClash**。
5. 在仪表盘 `日本-入口` 中从自动纳入的日本节点里手选首跳，优先使用 PC 上成功的节点；`美国` 中手选美国机场节点；`TikTok-ISP` 应只有 `TikTok-ISP-Local`。若只显示 REJECT，先停止手机测试，核对节点与订阅加载，不能增加 DIRECT/其他国家作回退。

日本组以 `include-all: true` 自动纳入当前配置中已加载的顶层节点和 proxy-providers，名称任意位置含 `jp`、`日本`、`Japan` 或 🇯🇵 即可，忽略大小写，无需提供完整节点名。节点名称匹配不证明供应商身份或可达性；此模块不会下载 iKuu 订阅。刷新云覆写并重启后若仍只有 REJECT，说明组内仍未纳入匹配节点，应先生成调试日志，检查运行配置的节点、代理提供商加载和生效筛选，不添加其他国家或 DIRECT 回退。

PR 未合并时用上述分支 URL，`main/profiles/tiktok-router-loongproxy-jp-us/...` 不是当前测试地址。验收期间保留开发分支；合并、稳定入口和标签另行处理。

## 独立手工设置

下列路径均在「服务 → OpenClash」下。模块只含 `[YAML]`，不修改插件开关。

| 页面 | 设置 | 本轮值 |
| --- | --- | --- |
| 插件设置 → 模式设置 | 运行模式 / 代理模式 | Fake-IP（增强），非 TUN、非混合；规则模式 |
| 同上 | UDP 流量转发 | 开启；本地 SOCKS5 仍固定 `udp: false` |
| 同上 | 旁路网关兼容 | 主路由或回程正常时关闭；仅依据旁路回程证据调整 |
| 插件设置 → 流量控制 | 路由器本机代理 | 开启 |
| 同上 | 实验性：绕过指定区域 IPv4 | 绕过中国大陆；数据源 MetaCubeX `cn.mrs` |
| 同上 | 禁用 QUIC | 开启，作为本候选基线 |
| 同上 | 绕过服务器地址 / 仅允许内网访问 | 开启 |
| 同上 | 仅允许常用端口流量 | 关闭 |
| 插件设置 → IPv6 设置 | IPv6 代理 / IPv6 DNS / 区域 IPv6 绕过 | 关闭；核对手机没有独立 IPv6 出口 |
| 插件设置 → DNS 设置 | 本地 DNS 劫持 | Dnsmasq 转发 |
| 覆写设置 → DNS 设置 | 自定义上游 DNS / 遵守路由规则 / Fake-IP 持久化 | 开启；若界面要求上游条目，保留 HTTPS `223.5.5.5:443` |
| 同上 | 附加上游 DNS / 自动追加默认 DNS / Fallback | 关闭；解析器列表由云模块管理 |
| 同上 | 自定义 Fake-IP-Filter | 开启，规则（rule）模式，不填旧黑名单列表 |
| 覆写设置 → Meta 设置 | 域名嗅探 / 纯 IP 嗅探 / 进程查找 | 嗅探开启；进程查找 off |
| 覆写设置 → 规则设置 | 仅代理命中规则流量 / 额外本地自定义规则 | 关闭 |
| 插件设置 → GEO 数据库订阅 / 大陆白名单订阅 | GeoSite、GeoIP、大陆 IPv4 列表 | 确认下载有效，保持更新 |

DNS 顺序为 TikTok/Google Fake-IP → 私网/Manual-Direct real-ip → CN real-ip → 其他 Fake-IP。TikTok 专用 DoH 经 `TikTok-ISP`，Google/Play 专用 DoH 经`美国`，国内解析独立。初次启动需要 GEO 数据和 CN provider 可用，本地静态测试不证明路由器能下载它们。

大陆真实 IP 可在防火墙旁路，未出现在核心面板不表示失败。禁用 QUIC 可在核心前拒绝 UDP/443，境外目标的人工 DIRECT UDP/443 业务也可能受影响。关闭 IPv6 代理不等于全网 IPv6 关闭。手机使用路由器 DNS；存在私有 DNS、额外 DNS 服务或另一网关时，先核对实际路径。

## 单次刷新规则

129 条原始人工直连记录全部保留，包括重复记录；每条 `DOMAIN-SUFFIX` 覆盖该域名及下级域名，不扩大到父域名/兄弟域名。inline payload 与 `rules/manual-direct-isp.yaml`、本候选固定目录同次提交同步。

日后更新本仓库规则：**只刷新这一个云覆写模块 → 重启 OpenClash**。本地凭据模块保持本地，不单独刷新 Manual-Direct Rule Provider。刷新只下载，重启才合并生效。机场订阅、GeoSite/GeoIP/CN 外部数据仍有各自更新机制。

## 手机验收与回退

先做第 1 项，成功后继续；失败不连续更换首跳或开关。

1. 手机连路由器 Wi-Fi，关闭移动数据和手机 VPN。重新打开 TikTok，查看新连接的规则、链路及上下行：命中 TikTok 专属策略，包含 `TikTok-ISP-Local` 与所选日本入口，视频持续加载；保存脱敏证据。普通浏览器 IP 查询默认走美国组，不能据此证明 TikTok ISP 出口；测速成功也不能替代播放验收。
2. 验证 Google Play 完整下载、其他境外网站经美国；国内 App、局域网与典型 Manual-Direct 域名及子域名正常。只看到 DIRECT 不等于应用正常响应。
3. 失败关闭：停用本地 ISP 模块并重启，新 TikTok 连接应被空组 REJECT，不能回退美国/直连；然后恢复。ISP 存在但连接失败时应连接报错，不必命中下一条 REJECT。`udp: false` 的 TikTok UDP 若进入核心，应继续匹配紧邻 REJECT；已在防火墙被拦截的 UDP/443 不能当作核心规则验收。
4. 仅覆盖进入 Mihomo 且命中 TikTok 分类的流量；未知域名、私有 DNS/HTTPDNS、其他网关/IPv6 和应用账号状态不在静态保证范围内。

启动错误、链路不符或播放失败时，先到 **运行日志 → 调试日志 → 生成日志**，保留故障时间和连接详情；分享前遮盖代理凭据、订阅与面板密钥。证据不足，不归因为“其他地区被封”。

回退：停用本方案两个模块，恢复此前唯一完整覆写、配套节点及设置截图，**最后统一重启一次**。不要在所有完整覆写关闭的过渡状态测试手机。

## 技术依据

- [官方指南入口与文档路由](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md)
- [16-overwrite-module-format.md §16.1.1 / §16.2.3](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)：入口、顺序、操作符与重启。
- [08-settings-mode-traffic.md §8.2 / §8.3](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/08-settings-mode-traffic.md)、[09-settings-dns-ac-ipv6.md §9.1 / §9.5](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/09-settings-dns-ac-ipv6.md)、[11-overwrite-settings.md §11.3 / §11.4 / §11.6](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/11-overwrite-settings.md)、[10-settings-geo-misc-src.md §10.1](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/10-settings-geo-misc-src.md)：设置与更新。
- 按指南查证 [Mihomo dialer-proxy](https://wiki.metacubex.one/config/proxies/dialer-proxy/)、[策略组](https://wiki.metacubex.one/config/proxy-groups/)、[规则优先级](https://wiki.metacubex.one/config/rules/)：链式拨号、空组回退、UDP 继续匹配。

指南核对日期 2026-10-16；dev 文档可能变化，不能据此宣称目标 alpha-gbc76c13 已实测兼容。
