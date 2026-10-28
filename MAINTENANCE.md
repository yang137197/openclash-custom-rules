# 仓库维护规范

## 不可变版本规则

正式版本 `tiktok-router-loongproxy-jp-us v1.0.0` 是本仓库第一版正式版。此前的历史版本及 beta 版本已从当前文件树、Git 标签和 GitHub Releases 清理；Git 提交历史保留。

每个方案（profile）独立维护 SemVer：同一方案的新候选版和正式版必须严格高于该方案已记录最高版本；禁止回退、复用或覆盖。不同方案的版本号互不比较，例如 A v1.0.0 与 B v1.0.0 可以同时存在。每个新版本必须在 `CHANGELOG.md` 增加同方案、同版本标题和具体更新内容。已发布版本目录、标签和 Release 不得改写；更新一律在对应方案内创建递增版本。

`AGENTS.md` 开头的专家角色和官方指南入口，以及正式版 `SETUP.md` 中的 OpenClash 设置建议，都是不可删除的仓库前提；任何整理不得删除或削弱这些内容。

需要本地模块的 Release 只附一个与版本目录模板逐字节一致、扩展名为 `.conf` 的可导入文件；OpenClash 官方本地模块上传器支持 `.txt`、`.conf`，因此 `.example` 不能作为最终附件扩展名。字段填写说明和虚构示例直接写在 Release 正文，不另附注释模板或填写指南。GitHub 自动生成的源码归档不能代替模板附件。

已发布的 v1.0.4 Release 仍保留其 `.conf.example` 附件及内容，不改写历史；需要使用该历史附件时，先将文件名改为 `.conf`。v1.0.5 正式版已将本地模块模板修正为 `.conf`。本次未在路由器文件选择器上实测，不声称通过该项实机测试。

用户于 2026-10-17 明确授权整理 v1.0.0 Release：保留原始模板附件与标签源码不变，删除额外注释模板及独立填写指南附件，并把填写映射和示例直接写入 Release 正文。该授权不涉及版本目录、配置或 Git 标签。

用户于 2026-10-17 明确要求在 v1.0.0 Release 正文中完整、单独显示标签固定的覆写订阅 URL，并同步根 README、方案 README 和后续开发规则。本次仅整理发布说明文案，不改写版本目录、标签或附件。

## 当前正式基线

当前唯一支持方案是 `tiktok-router-loongproxy-jp-us v1.0.6`（继承 J1–J11、J13–J16，新增 J17，stable），索引位于 `profiles/catalog.json`。J17 将 `huzhou.host` 主域名及全部子域名直连。用户于 2026-10-28 确认实机验收通过；候选对应调试日志记录目标环境，并显示主域名命中 DIRECT。日志未记录子域名连接，子域名验收依据为用户确认。验收环境中“禁用 QUIC”为停用，与 SETUP 建议不同；本版本未修改此设置。

当前未验收候选包括：`v1.0.1` 增加 `update.kies.samsung.com` 精确域名直连；`v1.0.2` 增加 Claude Code 官方端点分流；`v1.0.3` 将 Claude 网页 Anthropic/Claude 第一方域名统一指向 TikTok-ISP。正式版 `v1.0.5` 仅修正本地模板扩展名；当前正式版 v1.0.6 另新增 Huzhou 主域名及子域名直连。

**不可改变的链路前提：**路由器本地 Loongproxy 美国 SOCKS5 必须通过用户手选的 iKuuu 日本节点建立链式代理。`TikTok-ISP-Local` 必须保留 `dialer-proxy: 日本-入口` 与 `udp: false`。日本入口自动筛选已加载节点中名称含 `jp`、`日本`、`Japan` 或 🇯🇵 的节点（忽略大小写），但必须由用户选中实际 iKuuu 日本节点。日本节点缺失或不可用时失败关闭，严禁切换美国首跳、其他机场首跳、机场/DIRECT 回退。

Google/Google Play 与其他境外流量走用户手选的美国组；中国大陆域名和 IP 直连；保留完整 129 条 Manual-Direct。日本、美国和 ISP 组均须排除本地 ISP 节点以避免递归，空组保持 REJECT。

## 配置与凭据

- 单个配置仅启用一个完整云覆写及其配套本地节点模块。云模块管理规则；本地模块只追加精确名为 `TikTok-ISP-Local` 的 SOCKS5 节点。
- 更新规则只刷新正式云覆写模块并重启 OpenClash；机场节点订阅、GEO 数据各自更新。
- 修改 Loongproxy 密码时，只在路由器本地 `TikTok-ISP-Local` 模块改 `password`；按本地服务商提供的信息同步修改 `username`、`server`、`port`（如有变化）。保留节点名、`type: socks5`、`udp: false`、`dialer-proxy: 日本-入口`。详细 UI 路径见版本 `SETUP.md`。
- 真实 ISP 主机、账号和密码只存路由器本地模块，不进入仓库、云覆写、PR 或日志。公共仓库只保存占位模板；供 OpenClash 导入的模板使用 `.conf` 后缀。
- 需要本地模块的每个正式 Release 只附一个独立可下载的 `.conf` 模板并列出 SHA-256；字段填写说明和虚构示例直接写在 Release 正文，不另附注释模板或填写指南。固定覆写订阅 URL 必须完整显示并单独占一行，供用户直接点击或复制。
- 所有模块仅含 `[YAML]`；OpenClash 插件选项由用户在 LuCI 手工设置，禁止覆写模块写入 `[General]`、UCI 或自动修改插件设置。

## 规则与版本

- 流程 A/B 是仓库永久维护约定，不得因一般开发或文档整理删改、绕过；只有用户明确重新定义长期流程时才可调整。手动域名数据变更之外的运行行为更改均走候选验证和正式发布门禁。
- 保持规则优先级：私网/局域网 → Claude Code 与 Claude/Anthropic 第一方域名走 TikTok-ISP、GitHub 指定域名走美国 → 通用 TikTok ISP → 同范围 TikTok REJECT → Google/Play 美国 → Manual-Direct → 中国大陆域名/IP → 美国 MATCH。
- 流程 A 适用于手动直连域名的新增、修改和删除：只编辑 `rules/manual-direct.yaml` 的 `payload`，GitHub Actions 自动生成滚动覆写 inline payload 并更新 `profiles/catalog.json` 的滚动 SHA-256，再提交生成文件。源文件不维护固定哈希或条数校验；`manual-direct-isp.yaml` 是历史副本，不要求日常同步；不创建候选、版本记录、`CHANGELOG.md` 条目或正式 Release。已发布版本快照不改写。
- 流程 B 用于大版本更新或重构：建立递增候选并完成验证，经用户验收后发布正式版本；再将验收通过的模块同步到同一滚动模块路径并更新滚动哈希。已发布版本目录、标签和 Release 不可改写、移动或覆盖；新需求应建立独立方案并从自己的版本线开始。其他修改不得套用流程 A。纯打包或文档版本可复用未改变的最新稳定环境快照，但必须把未做的文件/应用验收明确列为未验证。
- 唯一本地覆写模块为 `tiktok-router-loongproxy`；完整云覆写必须使用远程订阅模块。刷新远程覆写后重启 OpenClash 生效，不更新机场节点订阅。
- 当前稳定版本为 `v1.0.6`；`v1.0.7` 候选调整手动规则生成/同步方式，尚待路由器及工作流验收，不视为正式发布。更早停用版本及 beta 的当前目录、标签和 Release 已清理。保留 Git 提交历史，不重写历史。

## 每次变更门禁

仅手动域名新增、修改或删除不走候选版本门禁、不更新版本合同或 `CHANGELOG.md`；提交源文件后，先确认 `Sync manual direct rules` 工作流成功及生成提交已进入 `main`。路由器再使用同一远程地址更新并重启，确认命中结果。工作流失败时滚动覆写仍保留上一次生成版本。

大版本更新或重构必须遵循 [`DEVELOPMENT_RULES.md`](DEVELOPMENT_RULES.md)。开始工作前阅读 `AGENTS.md`、`README.md`、`profiles/catalog.json` 和受影响方案/版本的 `REQUIREMENTS.md`、`SETUP.md`、`ENVIRONMENT.json`（若存在）；标明方案 ID、需求编号与版本类型；完成对应文档、环境记录和 `CHANGELOG.md`；检查凭据及完整差异；运行：

```text
python -m unittest discover -s scripts -p "test_*.py"
python scripts/validate_repository.py --base-ref origin/main
git diff --check
```

若没有可用 Git 比较基线，可省略 `--base-ref`，但不得声称历史保护校验已执行。静态检查、桌面核心夹具与真实设备验收必须分开记录。新版本的 OpenClash 环境记录和日志门禁按 `DEVELOPMENT_RULES.md` 执行；原始调试日志不得提交到公共仓库。
