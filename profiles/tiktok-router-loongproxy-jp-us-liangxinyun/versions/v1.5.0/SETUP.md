# 良心云默认代理 v1.5.0 正式部署、设置与验收

沿用当前 iKuuu 活动配置和正式方案 v1.0.7 的 OpenClash 设置。目标路由器版本、良心云订阅和应用验收见[环境记录](ENVIRONMENT.json)。

## 正式覆写地址

选择滚动地址可接收手动直连更新。

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/overwrite/openclash-overwrite.conf

固定此版时使用标签地址。

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-liangxinyun-v1.5.0/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.5.0/openclash-overwrite.conf

## 从候选版更新

在覆写模块中将远程覆写地址换为下方 v1.5.0 地址，沿用已填好的本地模块，重启后在 `TikTok首跳` 确认并手选实测可用的 `🇯🇵 日本Z04 | IEPL`，随后打开 TikTok 播放。

## 安装正式版

1. 记下当前模块开关、顺序、匹配配置、插件值和已使用的首跳节点，保留已用模块备份。
2. 下载[本地模板](local-tiktok-proxy.conf)，在路由器本地填写原 Loongproxy 凭据和良心云 Clash/Mihomo 订阅地址。模板的 `proxy: DIRECT` 需要路由器可直连拉取该订阅。复用已填好的本地模块时，将 `dialer-proxy: 日本-入口` 改为 `dialer-proxy: TikTok首跳`，并确认 `proxy-providers` 里的键为 `liangxinyun:`。保留 `LXY: ` 前缀和既有 Loongproxy 凭据。
3. 在 **服务 → OpenClash → 运行状态 → 覆写模块 → 添加新模块** 添加[正式滚动覆写](https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/overwrite/openclash-overwrite.conf)。完整云覆写和本地模块绑定同一 iKuuu 配置完整路径，远程模块放在本地模块上方。
4. 停用原完整云覆写及替换掉的本地模块，启用本版配套模块后统一重启。首次启用时，在 `TikTok首跳` 中手选 iKuuu 日本 Z01–Z04 的 IEPL 节点。在良心云组中手选一个可用节点。检查 CN 规则集已加载。

真实订阅、认证信息及完整运行配置只在路由器本地保存。

## 独立手工设置

本次实机验收沿用路由器现行插件值。下表供新装或恢复默认设置时参考，路径均在「服务 → OpenClash」下。本版模块仅注入 `[YAML]`。

| 页面 | 设置 | 本轮值 |
| --- | --- | --- |
| 插件设置 → 模式设置 | 运行模式 / 代理模式 | Fake-IP（增强），非 TUN、非混合；规则模式 |
| 同上 | UDP 流量转发 | 开启；本地 SOCKS5 仍固定 `udp: false` |
| 同上 | 旁路网关兼容 | 主路由或回程正常时关闭；仅依据旁路回程证据调整 |
| 插件设置 → 流量控制 | 路由器本机代理 | 开启 |
| 同上 | 实验性：绕过指定区域 IPv4 | 绕过中国大陆；数据源 MetaCubeX `cn.mrs` |
| 同上 | 禁用 QUIC | 建议开启。v1.5.0 验收时实机停用 |
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

DNS 顺序为 TikTok/Google Fake-IP → 私网/Manual-Direct real-ip → CN real-ip → 其他 Fake-IP。TikTok 专用 DoH 经 `TikTok测速`，Google/Play 专用 DoH 经 `良心云`，国内解析独立。CN 规则集沿用原缓存路径，更新经良心云；首次部署应确认 CN 规则集成功加载。

大陆真实 IP 可在防火墙旁路，未出现在核心面板不表示失败。禁用 QUIC 可在核心前拒绝 UDP/443，境外目标的人工 DIRECT UDP/443 业务也可能受影响。关闭 IPv6 代理不等于全网 IPv6 关闭。手机使用路由器 DNS；存在私有 DNS、额外 DNS 服务或另一网关时，先核对实际路径。

## 路由器验收与回退

1. **先验收 TikTok 和直连。** 手机连路由器 Wi-Fi 后播放 TikTok，核对实际链路为手选的 iKuuu 日本节点 → `TikTok-ISP-Local`。建议复测日本 Z04，使用 `TikTok测速` 并持续播放一段 TikTok 视频，记录节点、时间和结果。测局域网、一个手动直连域名和一个大陆站点。
2. 复测 Claude 网页或 Claude Code、YouTube 视频、Telegram 文件下载、GitHub 和 Google Play。在连接详情核对出口是 `LXY: ` 节点。Claude 网页与 Claude Code 都在用时，各测一次。
3. 核对 `TikTok首跳` 只显示已加载的 iKuuu 日本 Z01–Z04 节点和 `REJECT`，`TikTok测速` 仅显示 `TikTok-ISP-Local`。首次启用无手选记录时应为 `REJECT`；原所选节点消失时须手动重新选。普通流量继续经良心云。
4. 在 **运行日志 → 调试日志 → 生成日志** 保存本版对应的脱敏记录，并记录播放／下载结果。分享前遮盖订阅、凭据、面板密钥和敏感网络信息。

若 TikTok、直连或启动验收失败，停用本版模块，恢复原模块开关与顺序。若在原本地模块上直接改过 `dialer-proxy`，也恢复备份中的原值。统一重启后核对原模块使用的首跳。

- [OpenClash 官方覆写指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)
- [OpenClash 官方调试日志指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/13-logs.md)

## 启动报错时检查模块

出现 `良心云: 'liangxinyun' not found` 时，先检查本地配套模块已启用、匹配当前 iKuuu 配置的完整路径，以及 `proxy-providers` 下的键为 `liangxinyun:`。若仍报错，在运行日志中生成调试日志，仅分享已脱敏的插件与内核版本、模块状态和启动报错。
