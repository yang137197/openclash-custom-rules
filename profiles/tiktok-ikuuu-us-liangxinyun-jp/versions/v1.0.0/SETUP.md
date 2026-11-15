# OpenClash 设置与验收

**v1.0.0 candidate**。目标设备和真实双订阅待测。云覆写与唯一配套本地模块都使用 `[YAML]`。按[官方覆写模块指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)操作。

直连以 GitHub main 已同步的 `57ff422` 滚动覆写为准。该快照包含 `whoer.net` 后缀直连及同批已同步的 `ping0.cc`、`ippure.com`、`ipkk.com`。

## 本地模块

从 OpenClash「配置管理」查看现有运行配置，在顶层 `proxies:` 中找到已经使用的那条 iKuuu 美国节点，复制该节点完整 YAML 条目，替换 [local-tiktok-proxy.conf](local-tiktok-proxy.conf) 的首项并将 `name` 改为 `iKuuu-US-FirstHop`。如果节点来自 provider，请在路由器本地的代理集合文件中取出该节点完整条目。核对首跳条目可独立连接，且保留其原连接参数；依赖其他组的 `dialer-proxy` 须先核查。iKuuu 更新该节点参数时，本地条目需同步。

填入现有 Loongproxy SOCKS5 的主机、整数端口、用户名和密码。保留 `TikTok-ISP-Local`、`udp: false` 和 `dialer-proxy: iKuuu-US-FirstHop`。将 `url` 替换为良心云账户内的 Clash/Mihomo 订阅 URL。用 `filter` 精确列出订阅响应中已确认的日本高速节点名称。例如虚构名称可写成 `'^(日本高速 01|日本高速 02)$'`。节点名有正则元字符时按正则规则转义。订阅更新导致节点改名时，白名单也需对应更新。真实 URL、凭据、填好的模块和完整运行配置留在路由器本地。

## 应用候选

1. 记录当前启用的稳定版云模块与本地模块及其顺序，供回退。
2. 在「服务 → OpenClash → 运行状态 → 覆写模块」添加候选提交固定 raw URL 的远程模块，以及填好的本地 `.conf`。两者匹配当前配置的完整路径，云模块放在本地模块上方。
3. 停用同一配置上旧的两份稳定版模块，启用候选两份模块，核对设置后统一重启。插件设置沿用 [v1.0.7 的独立手工设置](../../../tiktok-router-loongproxy-jp-us/versions/v1.0.7/SETUP.md#独立手工设置)，包括 Fake-IP 增强／规则模式、大陆 IPv4 旁路、DNS 劫持及现有 IPv6／UDP 设置。保留当前已验证设置，候选模块不写插件选项。
4. 日常在仪表盘 `良心云-日本` 中选一条已实测的日本节点。

## 实机验收

- 配置和加载。确认良心云订阅从路由器可达，首次加载和重启后均能加载日本白名单。运行配置只有一个自定义策略组，组内只有确认的日本节点。运行配置中的两条独立 TikTok 出站仅用于链式拨号；仪表盘仍可能有核心内置的 `GLOBAL`。
- TikTok。核对运行配置的 `dialer-proxy` 绑定和实际首跳连接，再确认原 Loongproxy 落地和 TikTok 播放。仅观察到美国 IP 无法确认首跳。测试首跳不可用时 TikTok 失败且无良心云兜底，其他服务继续可用。
- 日本出口。查看 YouTube 4K、Telegram 大文件、Google Play 完整下载、GitHub 和 Claude 的实际连接链。核对晚高峰播放、下载及常用流媒体；观察日本组为空时代理流量失败。
- 直连。对照旧配置确认局域网、国内服务及 `okcaros.com`、`huzhou.host` 等现有手工直连样本。核对运行配置里的域名列表、顺序、DNS 和大陆旁路。大陆旁路流量可能未进入 Mihomo，按当前模式核对实际路径。

回退时停用候选两份模块，恢复原来的 v1.0.7 云模块、本地 ISP 模块及顺序，再统一重启。
