# 良心云分流 v1.0.0 候选部署、设置与验收

本方案沿用 iKuuu 活动配置以及正式方案 v1.0.7 的 OpenClash 设置基线。实际插件、核心和系统构建见[待补充的环境记录](ENVIRONMENT.json)。

## 安装候选

1. 保存原模块开关、顺序、匹配配置、插件设置截图，以及当前手选的 iKuuu 日本节点。保留两个原模块以便回退。
2. 下载[候选本地模板](local-tiktok-proxy.conf)。在路由器本地填写原 Loongproxy 地址、端口、账号、密码和良心云 Clash/Mihomo 订阅地址。链接应返回 Mihomo 可读的节点内容，模板中的 `proxy: DIRECT` 需要路由器可直连拉取该地址。请先在本地确认格式和访问条件。保留提供商名称 `liangxinyun` 与节点前缀 `LXY: `。
3. 在 **服务 → OpenClash → 运行状态 → 覆写模块 → 添加新模块** 导入候选本地 `.conf` 和[候选远程完整覆写](https://raw.githubusercontent.com/yang137197/openclash-custom-rules/codex/loongproxy-liangxinyun-candidate/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.0.0/openclash-overwrite.conf)。将两个候选模块绑定到同一现有 iKuuu 配置的完整路径，远程模块放在本地模块上方。
4. 停用两个原模块，启用两个候选模块，统一重启一次。在仪表盘核对 `日本-入口` 仍手选原 iKuuu 日本节点，`美国` 仍使用原节点，`TikTok-ISP` 只有 `TikTok-ISP-Local`，然后在 `良心云` 手选一个可用的良心云节点。候选需同时加载两个模块。

订阅 URL 和代理认证只填写在路由器本地模块。下载的空白模板和公开覆写使用占位或公开数据。基线另见 [v1.0.7 的部署说明](../../../tiktok-router-loongproxy-jp-us/versions/v1.0.7/SETUP.md)。

## 独立手工设置

本次候选验收沿用路由器现行插件值。下表供新装或恢复默认设置时参考，路径均在「服务 → OpenClash」下。候选模块仅注入 `[YAML]`。

| 页面 | 设置 | 本轮值 |
| --- | --- | --- |
| 插件设置 → 模式设置 | 运行模式 / 代理模式 | Fake-IP（增强），非 TUN、非混合；规则模式 |
| 同上 | UDP 流量转发 | 开启；本地 SOCKS5 仍固定 `udp: false` |
| 同上 | 旁路网关兼容 | 主路由或回程正常时关闭；仅依据旁路回程证据调整 |
| 插件设置 → 流量控制 | 路由器本机代理 | 开启 |
| 同上 | 实验性：绕过指定区域 IPv4 | 绕过中国大陆；数据源 MetaCubeX `cn.mrs` |
| 同上 | 禁用 QUIC | 开启，沿用 v1.0.4 已验收设置 |
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

## 路由器验收与回退

1. 在手机 Wi-Fi 下先播放 TikTok，核对新连接经 `TikTok-ISP-Local` 和原 iKuuu 日本节点。用一个局域网地址、一个手工直连域名及一个大陆站点复测直连。
2. 播放 YouTube 视频，检查 `googlevideo.com` 媒体连接的上下行和 `良心云` 出口。打开 Telegram 下载一个文件，检查域名或 IP 命中与实际出站。复测 Google Play 下载和原美国组。
3. 核对 `日本-入口` 和 `美国` 没有 `LXY: ` 节点，`良心云` 只显示该订阅的节点。确认 YouTube、Telegram 域名与 Telegram IP 三个规则集均加载。若选中的良心云节点故障，可手选该订阅内的其他节点。
4. 在 **运行日志 → 调试日志 → 生成日志** 保存对应候选的脱敏记录，同时记录播放、下载和直连结果。遮盖真实订阅、认证、面板密钥、设备标识和敏感网络地址。

出现启动、TikTok 链路或直连异常时，停用两个候选模块，启用保存的原配套模块，统一重启一次并重新核对原 iKuuu 日本节点。

- [OpenClash 官方覆写模块指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)
- [OpenClash 官方调试日志指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/13-logs.md)
