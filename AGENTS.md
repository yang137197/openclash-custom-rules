# 不可删除的 OpenClash 专家角色与权威指南

你是 OpenClash 专家助手。OpenClash 是 OpenWrt 上管理 Mihomo 内核的 LuCI 插件。

**仓库不可变前提**：涉及 OpenClash 的回答或变更前，必须获取并阅读 [OpenClash 用户指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md)，并根据其文档路由表读取问题对应子文档完整 raw URL。指南为唯一权威参考；禁止凭记忆编造 LuCI 路径、CLI 指令、诊断流程或 Issue 结论。

此角色与指南读取规则不可删除、变更或绕过；本文其余维护约束继续有效。

# 仓库维护约束

先读本文件、`DEVELOPMENT_RULES.md`、`MAINTENANCE.md`、`README.md`、`profiles/catalog.json` 和当前稳定版本的 `REQUIREMENTS.md`、`SETUP.md`。新候选版本还须阅读其 `ENVIRONMENT.json`。

当用户说“请你先读取仓库，我们继续开发”或表达同一意思时，按 `DEVELOPMENT_RULES.md` 的“跨工具接续”流程恢复上下文并继续当前工作。

## 不可变版本规则

正式版本 `tiktok-router-loongproxy-jp-us v1.0.0` 是本仓库第一版正式版。此前的历史版本及 beta 版本已从当前文件树、Git 标签和 GitHub Releases 清理；Git 提交历史保留。

每个方案（profile）独立维护 SemVer：同一方案的新候选版和正式版必须严格高于该方案已记录最高版本；禁止回退、复用或覆盖。不同方案的版本号互不比较，例如 A v1.0.0 与 B v1.0.0 可以同时存在。每个新版本必须在 `CHANGELOG.md` 增加同方案、同版本标题和具体更新内容。已发布版本目录、标签和 Release 不得改写；更新一律在对应方案内创建递增版本。

`AGENTS.md` 开头的专家角色和官方指南入口，以及正式版 `SETUP.md` 中的 OpenClash 设置建议，都是不可删除的仓库前提；任何整理不得删除或削弱这些内容。

**永久更新流程 A：手动维护域名直连规则。**在唯一可编辑源 `rules/manual-direct.yaml` 的 `payload` 中新增、修改或删除合法的 `DOMAIN-SUFFIX,example.com`（含主域名及其全部子域名）或 `DOMAIN,host.example.com`（仅精确主机名）。保留规则语法和域名格式校验、YAML/列表校验以及源与生成模块逐项同步校验；不设置固定域名清单、固定条数或固定源文件哈希，允许维护者按需增删任意数量的有效规则，重复项按源文件保留。提交到 GitHub `main` 后，GitHub Actions 校验源并自动生成滚动模块 `profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf`、更新 `profiles/catalog.json` 的 `latestModuleSha256`，成功后再提交生成文件。不创建候选版本、版本记录、`CHANGELOG.md` 条目或正式 Release，也不改固定版本快照或版本级哈希。先确认同步工作流成功及生成提交已进入 `main`，再在路由器对同一个滚动远程覆写地址点击更新并重启 OpenClash。`manual-direct-isp.yaml` 是历史副本，不作为日常维护入口。

**永久更新流程 B：大版本更新或重构。**创建高于该方案已记录最高版本的候选版，完成候选验证并经用户验收后发布正式版本；正式发布时将已验收模块同步到同一滚动模块路径并更新 `latestModuleSha256`。路由器仍使用同一个滚动远程覆写地址，点击更新后重启 OpenClash。已发布版本快照、标签和 Release 不得改写。流程 A 不涵盖规则优先级、策略组、DNS、代理链路、插件设置或生成/发布机制本身的变化。

上述 A/B 是仓库永久维护流程，不得因日常提交、版本候选或文档整理而删改或绕过；只有用户明确重新定义长期流程时才可调整。除流程 A 的手动域名数据变更外，其他运行行为更改均须经过候选验证和正式发布门禁。

## 当前事实与授权

- 当前正式方案：`tiktok-router-loongproxy-jp-us v1.0.8`，stable，需求D1–D13。用户于2026-11-26确认达到验收标准并授权发布；同日15:28:14调试日志及模块顺序截图已核对。目标OpenClash 0.48.002、alpha-gbc76c13、OpenWrt 24.10.2 / CatWrt amd64，详细环境及证据边界见本版ENVIRONMENT.json。
- 本次延续GitHub同一方案的v1.0.7版本线，不另起v1.0.0或新增profile。用户实测的较早固定候选路径与v1.0.8云/本地模板已逐字节证明相同；记录真实来源，不把编号迁移当作新线路测试。
- 四个显式组：TikTok首跳、Tiktok美国出口测速、良心云-日本专线流媒体、ikuuu-默认代理；保留默认GLOBAL但不定时检测。不使用独立控制器、不安装服务、不定制面板。
- TikTok首跳及默认代理仅用dual-ikuuu提供商的日本Z数字IEPL节点，自动选最近检测最低延迟。TikTok仍只经Loongproxy美国SOCKS5出口，本地TikTok-ISP-Local保留udp:false及dialer-proxy: TikTok首跳；不回退其他出口或DIRECT。
- 良心云仅用dual-liangxinyun的日本专线流媒体/日本高速CUCM节点，按两位编号01–99排序，专线全部在高速之前；使用单层fallback，故障向后、恢复返回。不是最低延迟选择，也不跨订阅兜底。
- 四组及提供商均60秒检测、5000毫秒超时、期望204、lazy:false。健康检测不证明带宽、解锁或播放；实机业务通过来自用户确认，日志采样不独立覆盖每一项场景。
- 唯一手动直连源rules/manual-direct.yaml保持可任意维护，正式滚动继续沿用原main地址；流程A/B不变。v1.0.7及更早发布快照、标签、Release全部保留且不可改写。

## 行为边界

1. 私网/局域网DIRECT → TikTok专用ISP及紧邻REJECT → 指定流媒体/下载良心云（排除手动直连、CN域名及已解析CN IP）→ Google默认代理 → Manual-Direct → CN域名/IP DIRECT → iKuuu默认MATCH。Claude/AI和普通GitHub网页/API走默认；仅明确专用下载域名改走良心云。
2. 两机场用命名提供商隔离并加IK:/LXY:前缀；不通过include-all混选。TikTok-ISP-Local只在固定美国出口组引用。TikTok UDP进入核心时命中REJECT是保留的保护行为，不据此单独判断TCP或播放故障。
3. rules/manual-direct.yaml是手动规则唯一可编辑源；不固定域名清单、数量或源哈希，保留语法、格式与源到滚动模块逐项同序校验，重复项保留。已发布固定快照不随日常源数据更新。
4. 手动源提交main后，先确认同步工作流及生成提交成功，再在路由器更新同一滚动云模块并重启；只reload防火墙不会重新合并模块。
5. 单个配置只启用一套完整云覆写及配对本地模块，云在本地上方。完整云模块用远程订阅；本地模块保存两个订阅与ISP参数。所有模块只含[YAML]，不写插件UCI或自动改开关。
6. 真实订阅URL、代理地址/账号/密码和面板密钥只存用户本地，不入Git/GitHub。公共仓库和Release只提供占位模板；唯一附件为.conf，字段填写和明确虚构示例写在Release正文。
7. 运行模式、DNS、QUIC、IPv6/TUN及规则策略变更须明确授权和候选验证。当前日志禁用QUIC停用已作为偏差保留；本次没有修改开关。
8. 当前 `v1.0.8` 为正式稳定版本，目录、标签、Release不可改写；后续同方案候选必须高于已记录最高版本。需求、设置、实机记录和验证详见本版合同及ENVIRONMENT.json。

## 每次变更

手动域名新增、修改或删除按永久更新流程 A 维护 `rules/manual-direct.yaml`，由 GitHub Actions 生成滚动覆写和哈希，不创建日常规则候选或正式 Release。生成/同步机制、大版本更新或重构按 `DEVELOPMENT_RULES.md` 完成候选信息收集、环境记录、隐私检查和发布门禁；标明方案 ID、需求编号与版本类型，更新对应合同、设置说明和 `CHANGELOG.md`，并完成仓库验证。已发布快照及凭据边界始终保持不变。
