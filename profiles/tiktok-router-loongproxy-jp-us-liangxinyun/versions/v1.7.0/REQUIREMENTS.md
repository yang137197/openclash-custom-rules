# 良心云严格自动选择 v1.7.0 候选需求

**candidate，待路由器预检和实机验收。** 方案为 `tiktok-router-loongproxy-jp-us-liangxinyun`。用户在 v1.6.0 嵌套组提前降级被实测复现后，明确选择“保持严格顺序，准备独立自动控制器”。本版本继承 [v1.5.0](../v1.5.0/REQUIREMENTS.md) 已验收链路与 [v1.6.0](../v1.6.0/REQUIREMENTS.md) 的 L15–L18 业务目标，替换未通过的嵌套回退实现。

- L19：只从 `liangxinyun` provider 选择名称带 `LXY: ` 前缀且属于日本专线、日本高速、美国流媒体、美国高速的节点。美国流媒体为名称同时含美国和流媒体，兼容美国05\|流媒体等格式；不固定编号或数量。只在最高有健康节点的档中选最近检测延迟最低者，档序固定为日本专线 → 日本高速 → 美国流媒体 → 美国高速，延迟相同优先保留当前节点，容差为 0。
- L20：路由器上的独立 Ruby 控制器直接读取 provider 的叶节点状态并选择具体节点，不通过嵌套组健康状态推断整档故障。统一 HTTPS 204 探测；默认每 60 秒发起 provider 完整健康检查，每 2 秒核对最近结果。只使用本测试 URL 的 `extra` 状态及有效时间戳，超过 130 秒、时间异常、缺少检测记录均视为 unknown。高档无健康节点但尚有 unknown 时选 REJECT，不能据此降级；确认高档每个节点均为最近检测失败或该档为空，才进入下一档。
- L21：Mihomo `良心云` 是自动控制程序的 select 写入入口，初始与空组均 REJECT；用户无需手选。控制器只可 PUT 该组的合规具体节点或 REJECT，不能改 TikTok、DNS、规则、插件设置或其他组。只连接本机回环 API，默认只读 UCI 获取现有端口和 secret；secret 经 curl 标准输入传递，不进入命令行参数或日志。单实例运行，正常停止尽力选择 REJECT，四档全部失败时明确选择 REJECT。API 不可用时不能声称已改变内核选择；procd 负责异常退出后的有限重启，SIGKILL／系统崩溃没有清理保证。
- L22：TikTok 手选 iKuuu 日本 Z01–Z04 → 本地 `TikTok-ISP-Local`／Loongproxy 美国出口、`udp: false`、失败关闭继续沿用 v1.5.0。本地凭据模板逐字节不变；路由规则、DNS、插件选项和 Manual-Direct 采用 3372eb5 稳定滚动快照。只增加良心云节点过滤／健康检查和独立服务，不替换内核，不自动安装依赖、不启用路由器服务、不替换正式滚动入口；当前阶段仅准备和本地验证。

## 验收

1. 本地策略测试覆盖所有两节点四档的 256 种成功／失败组合、未知／过期／异常时间、来源筛选、同延迟、启动与停止及写入边界。
2. 真实 Mihomo 与控制器夹具验证：同档部分失败不提前降级，整档依次降级，最高档恢复，档内更低延迟变化，新增／删除节点，四档全失败 REJECT；每种场景都核对实际新连接出口，TikTok 手选值保持。
3. 目标路由器先做只读预检，核对依赖与 API。2026-11-23 已确认 Ruby 所需库加载失败，改用现有 Lua＋curl 完成基础读取检查，不安装依赖、不启用服务；独立的[单次 Lua 模拟工具](../../../../scripts/LIANGXINYUN_READONLY.md)只用于核对筛选、记录和建议，不替换本合同的 Ruby 运行实现。安装前日志已确认当前 OpenClash、Mihomo、OpenWrt 版本，但未运行本候选，不据此宣称兼容 alpha-gbc76c13。
4. 用户应用候选与控制器后，提供本版本脱敏调试日志与 TikTok 视频、直连、普通代理及分层故障测试结果，才可正式发布。

严格顺序基于已完成／最近有效的健康检查结果，不是对物理网络瞬时状态的保证。探测与轮询期间已有连接可能失败；切换不会无感迁移旧连接。启动控制器首轮先选 REJECT，核心与控制器重启并非原子操作；控制器未运行／被强杀时内核可能保留上次选择，必须纳入实机验收。人工固定节点会被下一轮自动决策覆盖。

## 依据

- [v1.6.0 已复现问题](../v1.6.0/VALIDATION.md)，上游 [#2588](https://github.com/MetaCubeX/mihomo/issues/2588)及 [#2612](https://github.com/MetaCubeX/mihomo/issues/2612)。
- [OpenClash 官方 API 指南 15-api.md §15.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/15-api.md)、[v0.48.002 控制器源码](https://github.com/vernesong/OpenClash/blob/v0.48.002/luci-app-openclash/luasrc/controller/openclash.lua)：现有端口与 secret 来源、组切换接口。
- [Mihomo v1.19.34 provider API](https://github.com/MetaCubeX/mihomo/blob/v1.19.34/hub/route/provider.go)及[逐 URL 状态](https://github.com/MetaCubeX/mihomo/blob/v1.19.34/adapter/adapter.go)：provider 全量健康检查、`extra` 测试记录。
