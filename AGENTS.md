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

**永久更新流程 A：仅手动新增域名直连规则。**在现有 `rules/manual-direct.yaml` 的 `payload` 末尾追加 `DOMAIN-SUFFIX,example.com`（含主域名及其全部子域名）或 `DOMAIN,host.example.com`（仅精确主机名），同步更新滚动模块 `profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf` 并更新 `profiles/catalog.json` 中滚动模块的 `latestModuleSha256`，提交到 GitHub `main`。手动规则源不维护固定哈希或条数校验；不创建候选版本、版本记录、`CHANGELOG.md` 条目或正式 Release，也不改固定版本快照或版本级哈希。路由器继续使用同一个滚动远程覆写地址，点击更新后重启 OpenClash。

**永久更新流程 B：大版本更新或重构。**创建高于该方案已记录最高版本的候选版，完成候选验证并经用户验收后发布正式版本；正式发布时将已验收模块同步到同一滚动模块路径并更新 `latestModuleSha256`。路由器仍使用同一个滚动远程覆写地址，点击更新后重启 OpenClash。已发布版本快照、标签和 Release 不得改写。流程 A 不得用于调整规则优先级、策略组、DNS、代理链路、插件设置或删除既有规则。

上述 A/B 是仓库永久维护流程，不得因日常提交、版本候选或文档整理而删改或绕过；只有用户明确重新定义长期流程时才可调整。除流程 A 的手动新增域名外，其他运行行为更改均须经过候选验证和正式发布门禁。

## 当前事实与授权

- 当前正式方案：`tiktok-router-loongproxy-jp-us v1.0.5`，继承 J1–J11 并实现 J13–J16，stable。用户于 2026-10-22 确认 v1.0.4 实机验收通过；v1.0.5 只修正本地模块附件扩展名，复用 v1.0.4 环境快照，不改变运行规则。OpenClash 本地文件选择器尚未在路由器实测，不作已测试声明。
- 当前未验收候选：v1.0.1 仅新增 `update.kies.samsung.com` 精确域名 DIRECT；v1.0.2 加入 Claude Code 官方端点；v1.0.3 将 Claude 网页 Anthropic/Claude 第一方域名统一指向 TikTok-ISP。v1.0.4 继续保持 Claude 出口，并将 `github.com`、`githubusercontent.com` 与 `githubassets.com` 改走美国组。
- **强制链路前提**：TikTok 必须由 Loongproxy 美国 SOCKS5 出口，并通过用户在 `日本-入口` 手选的 iKuuu 日本节点建立链式代理（`dialer-proxy: 日本-入口`）。不得换成美国首跳或其他机场节点，不得回退机场、DIRECT 或其他出口；没有匹配的 iKuuu 日本节点时失败关闭。
- 用户授权清理已停用的供应商/手机代理方案，并在 2026-10-16 批准以本方案作为全新正式基线。当前文件树只维护上述日本首跳正式方案；按后续明确授权，旧版本标签和 Release 清理，Git 提交历史保留。
- 用户于 2026-10-17 明确授权整理 v1.0.0 Release：只保留与标签模板一致的一个本地模块下载附件，字段填写说明直接放在 Release 正文；删除额外的注释模板和独立填写指南附件。标签源码及原始模板内容保持不变。
- v1.0.4 的本地模板附件使用 `.conf.example`，不在 OpenClash 官方指南列出的本地上传文件类型 `.txt`、`.conf` 中；该 Release 不可改写。v1.0.5 已将本地模块模板改为 `.conf` 并正式发布。OpenClash 官方指南列出 `.conf` 为可选文件类型，但本次没有在路由器文件选择器上实测。
- `日本-入口` 从已加载的顶层节点和 proxy-providers 中，按名称任意位置的 `jp`、`日本`、`Japan`、🇯🇵（忽略大小写）筛选。用户必须手动选择 iKuuu 日本节点；名称筛选本身不证明供应商身份或可达性。
- 目标版本由用户报告为 OpenClash v0.48.002 / alpha-gbc76c13。正式验收结果来自用户确认。

## 行为边界

1. 私网/局域网 → Claude Code 与 Claude/Anthropic 第一方域名走 TikTok-ISP、GitHub 指定域名走美国 → 通用 TikTok ISP → TikTok REJECT → Google/Play 美国 → Manual-Direct → 中国大陆域名/IP DIRECT → 美国 MATCH，保持此优先级。
2. `TikTok-ISP` 只匹配本地精确节点名 `TikTok-ISP-Local`；本地 SOCKS5 `dialer-proxy: 日本-入口`，`udp: false`。实际首跳必须是 iKuuu 日本节点。三个组均手选，空组 REJECT，TikTok 不得回退机场或 DIRECT。日本/美国组排除该 ISP 节点以免递归。
3. `rules/manual-direct.yaml` 是手动规则来源，不以固定哈希或条数限制其修改。流程 A 的新增域名追加到其 `payload`，并同步滚动覆写；不要求为每次手动规则更新维护 `manual-direct-isp.yaml`。已发布快照仍不可改写。
4. 当前方案的滚动覆写模块与其规则来源必须同步；用户只刷新远程完整云覆写并重启，无需单独更新 Manual-Direct provider。
5. 单个配置只启用一个完整方案及其配套模块。唯一的本地覆写模块为 `tiktok-router-loongproxy`；完整云覆写必须使用远程订阅模块。所有模块仅含 `[YAML]`；插件选项由用户在 LuCI 手工设置，禁止 `[General]`、UCI 或其他自动写入插件选项的机制。
6. 真实代理地址、账号、密码不入 Git/GitHub。经授权生成的私有文件存仓库外；公共库只留占位模板。需导入 OpenClash 的本地模块模板使用 `.conf` 后缀；历史已发布 `.conf.example` 文件仅为保留快照，使用前需改名。
7. 修改其他规则顺序、DNS、运行模式、QUIC、区域绕过、IPv6/TUN，或删改人工域名，需用户明确授权；不得把本次日本名称筛选授权扩大到这些设置。
8. 当前 `v1.0.5` 为正式稳定版本且目录不可改写。仅手动新增域名走 GitHub `main` 滚动覆写，不创建版本或 Release；大版本更新或重构走递增候选版、验收和正式发布。不得移动或重写既有发布标签/Release。

## 每次变更

仅新增手动域名时，按永久更新流程维护规则来源和滚动覆写，不创建候选版本或正式 Release。大版本更新或重构按 `DEVELOPMENT_RULES.md` 完成候选信息收集、环境记录、隐私检查和发布门禁；标明方案 ID、需求编号与版本类型，更新对应合同、设置说明和 `CHANGELOG.md`，并完成仓库验证。已发布快照及凭据边界始终保持不变。
