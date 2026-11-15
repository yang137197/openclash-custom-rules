# OpenClash 设置与验收

**v1.0.1 candidate**。目标设备和真实双订阅待测。云覆写与唯一配套本地模块都使用 `[YAML]`。按[官方覆写模块指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)操作。

直连以 GitHub main 已同步的 `57ff422` 滚动覆写为准。该快照包含 `whoer.net` 后缀直连及同批已同步的 `ping0.cc`、`ippure.com`、`ipkk.com`。

## 本地模块

从现有 iKuuu 配置复制 Z01、Z02 的完整节点 YAML，替换 [本地模板](local-tiktok-proxy.conf) 的前两项，将其 `name` 分别改为 `iKuuu-US-Z01`、`iKuuu-US-Z02`。使用 v1.0.0 已填好的本地模块升级时，将原 `iKuuu-US-FirstHop` 改名为 `iKuuu-US-Z01`，再加入 Z02。保留原协议、服务器、端口及认证字段。iKuuu 更新节点参数时同步本地条目。

填入现有 Loongproxy SOCKS5 的主机、整数端口、用户名和密码。保留 `TikTok-ISP-Local`、`udp: false` 和 `dialer-proxy: TikTok-首跳`。将 `url` 替换为良心云账户内的 Clash/Mihomo 订阅 URL。用 `filter` 精确列出订阅响应中已确认的日本高速节点名称。例如虚构名称可写成 `'^(日本高速 01|日本高速 02)$'`。节点名有正则元字符时按正则规则转义。订阅更新导致节点改名时，白名单也需对应更新。真实 URL、凭据、填好的模块和完整运行配置留在路由器本地。

## 应用候选

1. 记录当前启用的稳定版云模块与本地模块及其顺序，供回退。
2. 在「服务 → OpenClash → 运行状态 → 覆写模块」添加候选提交固定 raw URL 的远程模块，以及填好的本地 `.conf`。两者匹配当前配置的完整路径，云模块放在本地模块上方。
3. 停用同一配置上原先启用的两份覆写模块，启用候选两份模块，核对设置后统一重启。插件设置沿用 [v1.0.7 的独立手工设置](../../../tiktok-router-loongproxy-jp-us/versions/v1.0.7/SETUP.md#独立手工设置)，包括 Fake-IP 增强／规则模式、大陆 IPv4 旁路、DNS 劫持及现有 IPv6／UDP 设置。保留当前已验证设置，候选模块不写插件选项。
4. 日常在仪表盘 `良心云-日本` 中选一条已实测的日本节点。

## 实机验收

- 配置和加载。确认良心云订阅从路由器可达，首次加载和重启后均能加载日本白名单。运行配置有 `TikTok-首跳`、`TikTok-ISP` 和 `良心云-日本` 三个自定义策略组，良心云组内只有确认的日本节点。仪表盘仍可能有核心内置的 `GLOBAL`。
- TikTok。确认首跳组默认选择健康的 Z01，测速时查看 Z01、Z02 的结果。模拟 Z01 不可达后，等待健康检查更新并确认**新连接**经 Z02 到原 Loongproxy 落地。对 `TikTok-ISP` 测速并实测播放；这项测速经过完整链路。两个首跳都实际不可用时，TikTok 不应转到日本或直连。
- 首跳组优先选择第一个通过健康检查的成员，保持自动模式即可。测速使用 Google 204 地址，耗时包括代理往返，不能测出视频带宽。探测失败但节点仍能访问其他目标时，组仍按探测状态选择。两项探测都失败时 Mihomo 仍可尝试列表首项。
- 日本出口。查看 YouTube 4K、Telegram 大文件、Google Play 完整下载、GitHub 和 Claude 的实际连接链。核对晚高峰播放、下载及常用流媒体；观察日本组为空时代理流量失败。
- 直连。对照旧配置确认局域网、国内服务及 `okcaros.com`、`huzhou.host` 等现有手工直连样本。核对运行配置里的域名列表、顺序、DNS 和大陆旁路。大陆旁路流量可能未进入 Mihomo，按当前模式核对实际路径。

回退时停用候选两份模块，恢复此前已用的云模块、本地模块及顺序，再统一重启。
