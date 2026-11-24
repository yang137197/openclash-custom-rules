# 良心云 Lua 控制器 v1.8.1 设置与单项验证

**candidate，未部署、未验收。** 当前正式方案仍是v1.5.0；本版只修正待部署控制器两处nixio权限参数，不修改节点策略、覆写有效YAML、本地模板或插件设置。

## 隔离状态文件单次测试已通过

用户在原生锁单项通过后要求继续前述状态写入与原子替换测试。2026-11-24已回传[独立状态诊断](../../../../scripts/LIANGXINYUN_NATIVE_STATE.md)通过：0700私有目录、0600合成JSON文件、独占创建、初始写入、同目录rename替换、新／旧打开文件读回和清理均成功；API／测速请求0，未应用选择，formalAcceptance=false。这一次授权已完成，不自动重测。没有运行完整控制器、使用生产状态文件路径或安装／启用服务。

原生锁的既有单次授权已完成，不重测；本次“下一步”不扩大为真实状态路径、服务启停或完整控制模式授权。

## 停止监督脚本离线单次测试已通过

2026-11-24用户已回传固定提交 `7c1119cd6a962d2cfd21975a0f7f80a97c84e3b9` 的本项成功结果，见[独立诊断说明](../../../../scripts/LIANGXINYUN_SUPERVISOR_OFFLINE.md)。内嵌监督Shell与候选逐字节一致，只运行合成worker；立即退出、延迟约200ms清理后退出两种场景均passed。监督退出码均0、子进程已回收、worker已退出，工作文件和停止标记已清理；supervisorTestPassed、cleanupComplete均true，forcedCleanupUsed=false，API／测速请求0、未应用选择、formalAcceptance=false。这次单项已完成，不重测。

本次仅使用私有 `/tmp/liangxinyun-supervisor-<随机后缀>` 和原监督脚本需要的 `/tmp/liangxinyun-stop.<测试进程PID>` 标记，均已清理。不安装服务、不接入OpenClash API、不加载完整控制器，不代表procd或完整控制器API清理已验证；详情及边界见上述说明。

## 只读配置差异核对已完成

用户要求下一步后，先使用[独立只读差异工具](../../../../scripts/LIANGXINYUN_CANDIDATE_READONLY.md)解释此前candidateCompatible=false。脚本不带参数，仅对本机版本、良心云组和提供商发出四次GET，核对REJECT首项、四类节点过滤、提供商来源和HTTPS204检测合同。不调用健康检测、不切换、不写配置、不安装服务；不输出订阅或密钥。已完成的锁、状态和停止监督不重测。

2026-11-24已收到交付提交 `01ee585cab50c31e016a6e9a0b4a40caeb11f7fb` 的结果：inspectionComplete=true、apiRequests=4、probeRequests=0、selectionApplied=false、configurationWritten=false；快照及来源核对通过，组和提供商各45节点，允许四档共21个（4／5／7／5），各24个档外节点。REJECT非首项、组及提供商含档外节点、检测URL和预期状态码不符，共五项导致candidateCompatible=false。状态码字段是string，具体内容未输出，不猜填。这次只读核对已完成，不自动重测；不接管旧手选组，完整控制器仍未运行。

用户现已要求准备[仅良心云的应用与回退方案](../../APPLY_ROLLBACK_PLAN.md)。原11月23日141条与仓库／候选148条已复核：仅仓库多7条、无删除且原序保留；11月24日已回传运行路径文件141条与历史基线逐项同序一致，差异仍只有对照仓库7项；两次读取相同、API／测速／文件写入均0，本项完成，不自动重测。核心内存一致性尚未证明。本阶段不整套替换v1.8.1、不带入这7条、不改TikTok或当前直连，不安装服务。方案中的增量结构只是草案，未来运行落地须更高候选及真实合并／差异验证；本轮不导入或启用。

## 增量草案本地合并验证已完成

用户授权的[真实OpenClash本地合并验证](../../INCREMENTAL_MERGE_VALIDATION.md)已完成，固定官方v0.48.002源码及哈希，18个本地场景通过（17公开场景加入CI）。本次基线变化仅良心云允许字段，完整规则、141条直连原序、DNS与TikTok组保持；ISP字段在稳定版占位模板夹具中保持。私有日志缺提供商和ISP定义，提供商占位补齐，不冒充真实订阅、凭据或当前整份配置已验证。未接触路由器、未安装／启动服务或核心、未生成可部署模块。未来仍须更高候选、实际配置基线和实机应用／回退验证。

## 权限修正与旧候选

上游nixio数值权限参数接受600，不接受384。v1.8.0误传384，既有只读预检和mkstemp原生锁测试未执行这两处open，旧本地替代模块也未校验参数。v1.8.1改用明确的 `rw-------`，并补充可复现旧值被拒绝的本地回归。旧v1.8.0运行文件和哈希保留，该候选暂不部署；本版完整控制器也未在路由器运行。

此前设备资料仍来自2026-11-23日志及11-24终端回传：Lua5.1、curl8.11.1与JSON/UCI/nixio已存在，alpha-gbc76c13；旧手选方案只读预检成功，candidateCompatible=false不代表新候选已应用。ENVIRONMENT维持pending，自动控制尚未验收。

## 后续部署与回退（本轮不执行）

完整控制器仍有Lua、Shell停止监督和procd模板三个文件，未来部署路径分别为 `/usr/share/openclash/liangxinyun-controller.lua`、`/usr/share/openclash/liangxinyun-controller.run`、`/etc/init.d/liangxinyun-controller`。本次不安装、不enable、不更新正式滚动模块，也不调用--once／--run。

隔离临时状态写入和合成worker的停止监督已单项通过；生产路径权限、完整控制器状态发布及停止时的API清理、procd启停／重启、默认检测参数及完整轮询仍须验证。以后另行安排候选应用时，远程完整模块仍在原本地凭据模块上方，匹配同一iKuuu配置完整路径，更新后重启OpenClash。核心组、检测合同和状态全部验收前不发布。

回退原则沿用v1.8.0：先恢复正式滚动覆写并重启，确认控制器不接管旧手选组，再停止／禁用独立服务，最后恢复良心云原手选。正常停止仍只尽力REJECT，强杀或API不可用不保证清理；不迁移旧连接。当前并未部署，不执行回退操作。

## OpenClash 独立手工设置

模块只含 `[YAML]`，保留 v1.5.0 建议，现有用户沿用当前值。本候选目标为已报告 OpenClash 0.48.002／alpha-gbc76c13／CatWrt OpenWrt 24.10.2 x86_64；已有 Lua 5.1 和 curl 8.11.1，完整控制器未实机验收。

| 页面（服务 → OpenClash 下） | 设置 | 建议与适用条件 |
| --- | --- | --- |
| 插件设置 → 模式设置 | 运行模式 / 代理模式 | 方案基线：Fake-IP（增强），非 TUN、非混合；规则模式 |
| 同上 | UDP 流量转发 | 开启；TikTok 本地 SOCKS5 仍必须 `udp: false` |
| 同上 | 旁路网关兼容 | 主路由或回程正常时关闭，仅依据旁路回程证据调整 |
| 插件设置 → 流量控制 | 路由器本机代理 | 开启 |
| 同上 | 实验性：绕过指定区域 IPv4 | 沿用绕过中国大陆，MetaCubeX `cn.mrs` |
| 同上 | 禁用 QUIC | 建议开启；当前实机停用，本候选不改现值 |
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

DNS、规则、TikTok 组及 148 条直连内容与 v1.7.0 有效 YAML 相同；本地凭据模板与 v1.5.0 逐字节相同。实际设备仍是 141 条直连，不能把仓库快照一致当作实机直连已更新；7 条既有维护差异在未来部署前单独核对，本轮不应用。客户端继续使用路由器 DNS；IPv6 代理关闭不等于全网 IPv6 关闭，QUIC 拒绝可能发生在内核之前。

## 验收记录

先核对新脚本只读预检，再单独安排原生运行测试。正式验收须覆盖普通代理、四档部分／整档故障与恢复、订阅变更、锁互斥、控制器与核心重启、正常停止、TikTok 播放和直连样例；记录时间与新连接实际出口。应用后在 **运行日志 → 调试日志 → 生成日志**取得对应脱敏证据，用户确认后才可发布。

正式回退入口：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/overwrite/openclash-overwrite.conf

依据：[OpenClash API §15.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/15-api.md)、[覆写模块 §16.1、§16.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)、[OpenWrt procd 参数](https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/system/procd/files/procd.sh)。不得分享已填模块、原始调试日志或 secret。
