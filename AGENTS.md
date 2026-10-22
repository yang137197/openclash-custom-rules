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

## 当前事实与授权

- 当前正式方案：`tiktok-router-loongproxy-jp-us v1.0.4`，继承 J1–J11 并实现 J13–J15，stable。用户于 2026-10-22 确认实机验收通过；对应调试日志记录的环境版本、配置标签、主要设置与模块顺序已写入该版本 `ENVIRONMENT.json`。不补造逐项延迟或性能指标。
- 当前未验收候选：v1.0.1 仅新增 `update.kies.samsung.com` 精确域名 DIRECT；v1.0.2 加入 Claude Code 官方端点；v1.0.3 将 Claude 网页 Anthropic/Claude 第一方域名统一指向 TikTok-ISP。v1.0.4 继续保持 Claude 出口，并将 `github.com`、`githubusercontent.com` 与 `githubassets.com` 改走美国组。
- **强制链路前提**：TikTok 必须由 Loongproxy 美国 SOCKS5 出口，并通过用户在 `日本-入口` 手选的 iKuuu 日本节点建立链式代理（`dialer-proxy: 日本-入口`）。不得换成美国首跳或其他机场节点，不得回退机场、DIRECT 或其他出口；没有匹配的 iKuuu 日本节点时失败关闭。
- 用户授权清理已停用的供应商/手机代理方案，并在 2026-10-16 批准以本方案作为全新正式基线。当前文件树只维护上述日本首跳正式方案；按后续明确授权，旧版本标签和 Release 清理，Git 提交历史保留。
- 用户于 2026-10-17 明确授权整理 v1.0.0 Release：只保留与标签模板一致的一个本地模块下载附件，字段填写说明直接放在 Release 正文；删除额外的注释模板和独立填写指南附件。标签源码及原始模板内容保持不变。
- `日本-入口` 从已加载的顶层节点和 proxy-providers 中，按名称任意位置的 `jp`、`日本`、`Japan`、🇯🇵（忽略大小写）筛选。用户必须手动选择 iKuuu 日本节点；名称筛选本身不证明供应商身份或可达性。
- 目标版本由用户报告为 OpenClash v0.48.002 / alpha-gbc76c13。正式验收结果来自用户确认。

## 行为边界

1. 私网/局域网 → Claude Code 与 Claude/Anthropic 第一方域名走 TikTok-ISP、GitHub 指定域名走美国 → 通用 TikTok ISP → TikTok REJECT → Google/Play 美国 → Manual-Direct → 中国大陆域名/IP DIRECT → 美国 MATCH，保持此优先级。
2. `TikTok-ISP` 只匹配本地精确节点名 `TikTok-ISP-Local`；本地 SOCKS5 `dialer-proxy: 日本-入口`，`udp: false`。实际首跳必须是 iKuuu 日本节点。三个组均手选，空组 REJECT，TikTok 不得回退机场或 DIRECT。日本/美国组排除该 ISP 节点以免递归。
3. 保留 `rules/manual-direct.yaml` 的全部 129 条原始记录。`rules/manual-direct-isp.yaml` 保持逐条对应的 DOMAIN-SUFFIX 副本，包括已有重复项；不得静默删除、改名或扩大到父域名。
4. 当前稳定方案的 Manual-Direct inline payload、固定版本模块、滚动模块与规则源必须同步；用户只刷新完整云覆写并重启，无需单独更新 Manual-Direct provider。
5. 单个配置只启用一个完整方案及其配套本地节点模块。所有模块仅含 `[YAML]`；插件选项由用户在 LuCI 手工设置，禁止 `[General]`、UCI 或其他自动写入插件选项的机制。
6. 真实代理地址、账号、密码不入 Git/GitHub。经授权生成的私有文件存仓库外；公共库只留占位模板。
7. 修改其他规则顺序、DNS、运行模式、QUIC、区域绕过、IPv6/TUN，或删改人工域名，需用户明确授权；不得把本次日本名称筛选授权扩大到这些设置。
8. 当前 `v1.0.4` 为正式稳定版本且目录不可改写；后续行为变更需新版本合同、目录和 URL，实机验收前保持 candidate。不得移动或重写既有发布标签/Release。

## 每次变更

按 `DEVELOPMENT_RULES.md` 完成候选信息收集、环境记录、隐私检查和发布门禁；标明方案 ID、需求编号与版本类型，更新对应合同、设置说明和 `CHANGELOG.md`。运行 `python -m unittest discover -s scripts -p "test_*.py"`、`python scripts/validate_repository.py --base-ref origin/main` 和 `git diff --check`，审查完整差异。仓库校验与实机验收分别记录，不保存冗长排查流水账。
