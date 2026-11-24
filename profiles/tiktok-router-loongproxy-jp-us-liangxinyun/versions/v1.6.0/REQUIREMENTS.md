# 良心云分层自动选择 v1.6.0 候选需求

状态：**candidate，本地严格留档验证失败，暂不部署**。方案 ID 为 `tiktok-router-loongproxy-jp-us-liangxinyun`，继承 [v1.5.0](../v1.5.0/REQUIREMENTS.md) 的 TikTok 日本首跳和普通代理出口要求。本次只调整良心云普通代理的节点范围与自动选择方式。[验证记录](VALIDATION.md)已将检测时间差从潜在风险更新为已复现问题。

- L15：良心云只纳入本订阅中名称包含“日本专线”“日本高速”“美国高速”，或同时包含“美国”和“流媒体”的节点；编号、旗帜和分隔符不影响这四类名称匹配。`美国05|流媒体|0.1x` 属于美国流媒体。其他类别不得进入普通代理候选，订阅更新后符合条件的节点自动纳入，不固定节点编号或数量。
- L16：普通代理入口继续叫 `良心云`，使用 `fallback` 按“日本专线 → 日本高速 → 美国流媒体 → 美国高速”选择；四个子组各用 `url-test`，从本档可用节点中选择最近健康检查延迟最低者，容差为 0。当前档仍有可用节点时应留在当前档，整档失败后才降级；高优先级档恢复后自动回切，不要求手选节点或子组。
- L17：provider 与总组持续健康检查，统一 HTTPS 204 测试地址、60 秒周期、5 秒超时、期望状态 204，关闭懒惰检测。空档使用 REJECT 并允许总组选下一可用档；四档均失败时不得转为 DIRECT、iKuuu 或其他类别。检测结果存在时间差，嵌套组的短暂提前降级必须单独观察，不能把稳态通过写成原子切换保证。
- L18：TikTok 继续手选 iKuuu 日本 Z01–Z04 → `TikTok-ISP-Local` → Loongproxy 美国 SOCKS5；保留 `udp: false`、缺失时 REJECT、本地凭据边界。普通流量规则、规则顺序、DNS、插件设置与最新稳定滚动模块一致；手动直连快照取自 `3372eb5`，唯一维护源仍是 `rules/manual-direct.yaml`。正式滚动模块与 v1.5.0 快照在候选阶段不变。

## 验收条件

1. 对照运行配置确认四档完整纳入符合名称的多个良心云节点，排除香港、新加坡及其他类别；iKuuu 不进入四档。
2. 高优先级档延迟较高、低优先级档延迟较低时，仍选高优先级档；档内选最低延迟。不得以节点下载速度或平台解锁状态替代延迟结果。
3. 分别验证同档部分故障、整档故障、逐档降级、空档跳过、恢复回切及订阅新增节点。记录检测收敛时间和是否出现短暂提前降级；若持续提前降级或同档切换不正确，不予验收。
4. 四档全部失效时普通代理失败；恢复后自动选回最高可用档。新连接检查实际出口，既有下载／播放连接不保证无感迁移。
5. 用户复测 TikTok 播放、直连样例、YouTube/Telegram/Claude 等普通代理，提供对应候选的脱敏调试日志及应用结果，才可发布。合成节点核心测试和静态检查不能替代目标 alpha 核心与实际线路验收。

## 技术依据

- [OpenClash 用户指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md)及 [16-overwrite-module-format.md §16.2.3](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)：仅用 `[YAML]` 合并 provider 健康检查，保留本地订阅与认证。
- Mihomo [url-test](https://wiki.metacubex.one/config/proxy-groups/url-test/)、[fallback](https://wiki.metacubex.one/config/proxy-groups/fallback/)、[策略组通用字段](https://wiki.metacubex.one/config/proxy-groups/)和 [provider 健康检查](https://wiki.metacubex.one/config/proxy-providers/)。
- [v1.19.34 fallback 源码](https://github.com/MetaCubeX/mihomo/blob/v1.19.34/adapter/outboundgroup/fallback.go)：外层依据子组最近探测状态选择，未实现四档所有叶节点状态的原子聚合；全失败返回首项尝试，不等同于明确命中 REJECT。
- [Mihomo #2588](https://github.com/MetaCubeX/mihomo/issues/2588)及 [#2612](https://github.com/MetaCubeX/mihomo/issues/2612)：与本地复现一致的嵌套组提前回退报告；截至 2026-11-23 查询仍为 Open。不能把调低检测间隔当作已解决的证据。
