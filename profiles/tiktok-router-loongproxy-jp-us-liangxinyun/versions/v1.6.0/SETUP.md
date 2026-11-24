# 良心云分层自动选择 v1.6.0 候选部署与设置

**candidate，本地已复现提前降级，暂不部署。** 四档嵌套组合未严格满足 L16。继续使用已验收 v1.5.0；[验证记录](VALIDATION.md)说明失败场景。当前设备环境未知；[v1.5.0 环境](../v1.5.0/ENVIRONMENT.json)仅为历史参考，不能证明本候选的目标兼容性。

## 保留的部署草案（问题解决前不执行）

候选分支源码地址（用于审阅；不是已通过测试的部署入口，候选阶段可随分支修正）：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/codex/liangxinyun-strict-auto/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.6.0/openclash-overwrite.conf

1. 在 **服务 → OpenClash → 运行状态 → 覆写模块**，记下现有正式远程模块地址和开关，然后将该远程模块地址改为上述候选地址，刷新／更新后确认正文是 v1.6.0。
2. 保持现有已填好的本地模块启用，两个模块匹配同一个 iKuuu 配置完整路径，远程模块位于本地模块上方，保存后重启 OpenClash。只刷新开关或重载核心不会重新执行完整覆写合并。
3. `TikTok首跳` 继续手选已验证可用的 iKuuu 日本节点。`良心云` 和四个子组自动选择，勿在面板中固定其节点。先核对良心云选择日本专线子组、子组显示其最低延迟节点，再复测 TikTok 与直连。

初始节点健康状态可能尚未完成检测；等待健康检查收敛后检查新连接。本版统一 60 秒健康检查、5 秒超时；嵌套组还存在选择缓存与检测时间差，不能承诺故障后恰好 5 秒或 60 秒完成切换。

已填好的 v1.5.0 本地模块可直接复用，无需重新填写订阅或 Loongproxy 凭据。[本地占位模板](local-tiktok-proxy.conf)与 v1.5.0 逐字节一致，仅供新安装；真实值只保留在路由器本地。候选云模块合并 `liangxinyun` 的名称过滤与健康检查，不覆盖其 URL、认证、缓存路径及 `LXY: ` 前缀。

## 策略与检测

| 组名 | 类型 | 节点范围／优先级 |
| --- | --- | --- |
| 良心云 | fallback | 下列四组自上而下，恢复后回选较高优先级 |
| 良心云-日本专线 | url-test | 名称包含日本专线 |
| 良心云-日本高速 | url-test | 名称包含日本高速 |
| 良心云-美国流媒体 | url-test | 名称同时包含美国和流媒体，兼容美国05\|流媒体 |
| 良心云-美国高速 | url-test | 名称包含美国高速 |

四个子组只使用 `liangxinyun` provider；provider 也过滤为这四类。所有组与 provider 统一使用 `https://www.gstatic.com/generate_204`，期望状态 204，非懒惰检测。组内容差为 0，按最近检测结果选最低延迟，延迟相同不要求固定编号。探测有少量流量开销，不能据此保证实际吞吐量或平台解锁。

总组按子组探测结果工作，子组探测与叶节点探测并非原子操作。故障过渡可能短暂提前降级，必须在验收中记录。全失败时内核可能仍显示日本专线并尝试其失败节点，不能仅凭“now”字段判断可用；应核对请求结果。空档配置 REJECT，不能回退直连。

## 独立手工设置

本次不调整插件选项。下表保留 v1.5.0 的设置建议；已部署用户沿用现行值，新装用户按适用条件核对。所有页面均在「服务 → OpenClash」下。历史实测为 OpenClash 0.48.002／alpha-gbc76c13／OpenWrt 24.10.2 x86_64；v1.6.0 当前环境与应用结果待补。

| 页面 | 设置 | 建议与适用条件 |
| --- | --- | --- |
| 插件设置 → 模式设置 | 运行模式 / 代理模式 | 方案基线：Fake-IP（增强），非 TUN、非混合；规则模式 |
| 同上 | UDP 流量转发 | 开启；TikTok 本地 SOCKS5 必须仍为 `udp: false` |
| 同上 | 旁路网关兼容 | 主路由或回程正常时关闭；只依据旁路回程证据调整 |
| 插件设置 → 流量控制 | 路由器本机代理 | 开启，用于本机代理访问 |
| 同上 | 实验性：绕过指定区域 IPv4 | 沿用绕过中国大陆；数据源 MetaCubeX `cn.mrs` |
| 同上 | 禁用 QUIC | 建议开启；v1.5.0 实机停用，本候选沿用现行值 |
| 同上 | 绕过服务器地址 / 仅允许内网访问 | 开启 |
| 同上 | 仅允许常用端口流量 | 关闭 |
| 插件设置 → IPv6 设置 | IPv6 代理 / IPv6 DNS / 区域 IPv6 绕过 | 关闭；核对客户端没有独立 IPv6 出口 |
| 插件设置 → DNS 设置 | 本地 DNS 劫持 | Dnsmasq 转发 |
| 覆写设置 → DNS 设置 | 自定义上游 DNS / 遵守路由规则 / Fake-IP 持久化 | 方案必需：开启；界面要求上游条目时保留 HTTPS `223.5.5.5:443` |
| 同上 | 附加上游 DNS / 自动追加默认 DNS / Fallback | 关闭，云模块管理解析器 |
| 同上 | 自定义 Fake-IP-Filter | 开启，rule 模式，不填旧黑名单列表 |
| 覆写设置 → Meta 设置 | 域名嗅探 / 纯 IP 嗅探 / 进程查找 | 嗅探开启；进程查找 off |
| 覆写设置 → 规则设置 | 仅代理命中规则流量 / 额外本地自定义规则 | 关闭 |
| 插件设置 → GEO 数据库订阅 / 大陆白名单订阅 | GeoSite、GeoIP、大陆 IPv4 列表 | 确认下载有效，保持更新 |

DNS 顺序为 TikTok/Google Fake-IP → 私网/Manual-Direct real-ip → CN real-ip → 其他 Fake-IP。TikTok DoH 继续经 `TikTok测速`；Google/Play DoH 和 CN 规则集更新经 `良心云`。手动直连内容取自本候选创建时最新稳定滚动模块，后续源规则更新按永久流程 A；候选固定快照不自动追随源数据变动。

大陆真实 IP 可在防火墙旁路，面板缺少记录不能单独判为失败。禁用 QUIC 可在进入核心前拒绝 UDP/443；关闭 IPv6 代理不代表全网 IPv6 关闭。客户端继续使用路由器 DNS，存在其他 DNS／网关时核对实际路径。

## 验收与回退

先确认 TikTok 视频、直连样例与普通代理均正常，再进行[需求合同](REQUIREMENTS.md)的分层故障测试。记录同档部分故障是否仍留档、整档逐级降级、恢复回切、空档与全失效结果。切换主要作用于新连接，既有视频／下载不保证无感迁移。测试完生成本候选对应的脱敏调试日志，当前环境字段及应用结果填入 [ENVIRONMENT.json](ENVIRONMENT.json)；原始日志不得入 Git。

回退时将同一个远程模块恢复为正式滚动地址，刷新／更新后重启；已填本地模块继续复用：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/overwrite/openclash-overwrite.conf

启动报错或实际链路异常时，按[官方日志指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/13-logs.md)在 **运行日志 → 调试日志 → 生成日志**取证；分享前遮盖订阅、认证和面板密钥。模块入口、顺序及重启行为依据 [16-overwrite-module-format.md §16.1、§16.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)。
