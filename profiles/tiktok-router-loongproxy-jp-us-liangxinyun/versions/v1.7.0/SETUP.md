# 良心云严格自动选择 v1.7.0 候选部署与设置

**candidate，当前仅完成本地准备，目标路由器待预检。** [需求合同](REQUIREMENTS.md)和[验证记录](VALIDATION.md)分别说明要求与证据。本轮没有安装路由器服务、替换正式远程覆写或发布 Release。当前正式入口继续为 v1.5.0。

## 当前下一步：只读预检

2026-11-23 11:06 的安装前调试日志已核对，环境见 ENVIRONMENT.json；当前仍为原手选方案，未应用 v1.7.0。下一步把本目录的 `liangxinyun-controller.rb` 暂存路由器，不先启用候选模块或服务，运行 `ruby /实际暂存目录/liangxinyun-controller.rb --preflight`。此命令只读现有 UCI 和核心 API，不测速、不切换节点、不写状态文件。旧稳定结构的 `candidateCompatible: false` 是预期结果；先看 Ruby 依赖能否加载、API 是否可达及是否有逐 URL 状态。预检输出不包含 API 密钥或订阅；可遮盖节点名后分享。

控制器使用 OpenClash 原有 Ruby 与 curl。OpenWrt 将 Ruby 标准库拆成多个包，需要 `ruby-json`、`ruby-open3`、`ruby-optparse`、`ruby-time`、`ruby-uri` 及其依赖；是否已安装须以预检为准，不能因 OpenClash 自身能启动就假设齐全。在「系统 → 软件包」按缺失组件核对，控制器不自动安装。包名依据 [OpenWrt 24.10 Ruby Makefile](https://github.com/openwrt/packages/blob/openwrt-24.10/lang/ruby/Makefile)。

默认只读 `openclash.config.cn_port` 与 `openclash.config.dashboard_password`，连接 `127.0.0.1`，不需要再次填写机场订阅或 Loongproxy 凭据。端口／secret 变更后需重启控制器。若使用了覆盖这些设置的额外模块，须先核对实际 API 参数。

## 预检通过后才执行的部署草案

1. 保存现有远程模块地址、开关、顺序与 TikTok 手选节点。本地已填好的 v1.5.0 模块继续复用，与本候选占位模板一致。
2. 将本目录的 `liangxinyun-controller.rb` 安装到 `/usr/share/openclash/liangxinyun-controller.rb`，服务模板 `liangxinyun-controller.init` 安装为 `/etc/init.d/liangxinyun-controller` 并赋予执行权限。先启动为待机服务，确认它在旧稳定方案上只报告等待，不写节点选择；实际 enable／start 操作留到预检通过后安排。
3. 在 **服务 → OpenClash → 运行状态 → 覆写模块** 将同一个完整远程模块切换为候选分支中 `profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.7.0/openclash-overwrite.conf`；仍匹配当前 iKuuu 配置完整路径，远程模块位于现有本地模块上方。更新正文并统一重启 OpenClash。
4. 控制器确认严格候选形状后，首轮选择 REJECT、完成检测、自动选最高可用档最低延迟节点。核对 `/tmp/liangxinyun-controller-status.json` 和新连接的实际出口，再配置独立服务自启动。`TikTok首跳` 继续手选已验收的 iKuuu 日本节点。

预检通过后使用的候选远程地址（分支可更新，不是正式滚动入口）：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/codex/liangxinyun-strict-auto/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.7.0/openclash-overwrite.conf

`良心云` 在面板中显示 select，是自动程序写入入口；用户无需手选。组中只有 REJECT 和符合四类名称的良心云具体节点，不显示嵌套回退组。服务由 procd 按 `3600 5 5` 参数监督，连续快速退出超限时停止重试；正常停止尽力选回 REJECT。强杀或 API 故障时无法保证清理成功，状态中的 `verifiedSelection: false` 表示没有确认内核已切换。参数依据 [OpenWrt procd 源码](https://lxr.openwrt.org/source/procd/service/instance.c)。

默认 provider 每 60 秒检测、5 秒超时、期望 204；控制器每 60 秒请求完整检测，每 2 秒核对状态。高档存在未知检测结果时 REJECT，确认全部失败才降级；没有额外防抖，延迟相同保留当前节点。仅在核心接受有效选择后使用新出口。订阅更新与选择发生竞争时重新采样，不能把未观察到的高档节点当作已失效。

## 独立手工设置

模块只含 `[YAML]`，控制器不写插件设置。保留 v1.5.0 建议，现有用户沿用当前值。2026-11-23 安装前日志确认 OpenClash 0.48.002、alpha-gbc76c13、OpenWrt 24.10.2 x86_64，Ruby 3.3.6、curl 8.11.1；额外 Ruby 库与 v1.7.0 运行兼容性仍待验证。

| 页面（服务 → OpenClash 下） | 设置 | 建议与适用条件 |
| --- | --- | --- |
| 插件设置 → 模式设置 | 运行模式 / 代理模式 | 方案基线：Fake-IP（增强），非 TUN、非混合；规则模式 |
| 同上 | UDP 流量转发 | 开启；TikTok 本地 SOCKS5 仍必须 `udp: false` |
| 同上 | 旁路网关兼容 | 主路由或回程正常时关闭，仅依据旁路回程证据调整 |
| 插件设置 → 流量控制 | 路由器本机代理 | 开启 |
| 同上 | 实验性：绕过指定区域 IPv4 | 沿用绕过中国大陆，MetaCubeX `cn.mrs` |
| 同上 | 禁用 QUIC | 建议开启；v1.5.0 实机停用，本候选不改现值 |
| 同上 | 绕过服务器地址 / 仅允许内网访问 | 开启 |
| 同上 | 仅允许常用端口流量 | 关闭 |
| 插件设置 → IPv6 设置 | IPv6 代理 / IPv6 DNS / 区域 IPv6 绕过 | 关闭，核对客户端没有独立 IPv6 出口 |
| 插件设置 → DNS 设置 | 本地 DNS 劫持 | Dnsmasq 转发 |
| 覆写设置 → DNS 设置 | 自定义上游 DNS / 遵守路由规则 / Fake-IP 持久化 | 方案必需：开启；界面需要条目时保留 HTTPS `223.5.5.5:443` |
| 同上 | 附加上游 DNS / 自动追加默认 DNS / Fallback | 关闭，由云模块管理解析器 |
| 同上 | 自定义 Fake-IP-Filter | 开启，rule 模式，不填旧黑名单列表 |
| 覆写设置 → Meta 设置 | 域名嗅探 / 纯 IP 嗅探 / 进程查找 | 嗅探开启，进程查找 off |
| 覆写设置 → 规则设置 | 仅代理命中规则流量 / 额外本地自定义规则 | 关闭 |
| 插件设置 → GEO 数据库订阅 / 大陆白名单订阅 | GeoSite、GeoIP、大陆 IPv4 列表 | 确认下载有效，保持更新 |

DNS 顺序为 TikTok/Google Fake-IP → 私网/Manual-Direct real-ip → CN real-ip → 其他 Fake-IP。TikTok DoH 经 `TikTok测速`；Google/Play DoH 及 CN 规则集更新经 `良心云`。直连快照取自 3372eb5；日常维护唯一来源继续为 `rules/manual-direct.yaml`。候选快照不自动追随后续源数据更新。

安装前日志的运行 Manual-Direct 与 v1.5.0 固定快照逐项相同（141 条）；仓库滚动模块和候选包含已提交日常维护后的 148 条。部署前须单独核对这 7 条已有维护差异，不能把仓库快照一致写成当前设备直连逐项未变；本轮未应用任何直连更新。

大陆真实 IP 可在防火墙旁路；禁用 QUIC 可在核心前拒绝 UDP/443；关闭 IPv6 代理不等于全网 IPv6 关闭。客户端继续使用路由器 DNS，其他 DNS／网关路径需另行核对。

## 实机验收与回退

先验证 TikTok 视频、直连样例及普通代理，再按合同验证同档部分失败、整档逐级失败、恢复、订阅更新、核心／控制器重启、停止、全失败。记录节点、时间和新连接出口；已有视频和下载不保证无感迁移。最后在 **运行日志 → 调试日志 → 生成日志**采集本候选脱敏证据与应用结果，方可发布。

回退：先恢复正式滚动远程地址，刷新后重启 OpenClash。控制器看到旧版形状后不再写选择，再停止并取消独立服务自启动，最后在良心云组恢复原手选节点。这样不会在仍运行严格候选时直接停服务而留下 REJECT。已填的本地模块继续使用。

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/overwrite/openclash-overwrite.conf

接口与入口依据官方 [15-api.md §15.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/15-api.md)、[16-overwrite-module-format.md §16.1、§16.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)。不分享已填模块、原始调试日志或 API secret。
