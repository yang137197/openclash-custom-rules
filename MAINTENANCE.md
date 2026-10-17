# 仓库维护规范

## 不可变版本规则

正式版本 `tiktok-router-loongproxy-jp-us v1.0.0` 是本仓库第一版正式版。此前的历史版本及 beta 版本已从当前文件树、Git 标签和 GitHub Releases 清理；Git 提交历史保留。

每个方案（profile）独立维护 SemVer：同一方案的新候选版和正式版必须严格高于该方案已记录最高版本；禁止回退、复用或覆盖。不同方案的版本号互不比较，例如 A v1.0.0 与 B v1.0.0 可以同时存在。每个新版本必须在 `CHANGELOG.md` 增加同方案、同版本标题和具体更新内容。已发布版本目录、标签和 Release 不得改写；更新一律在对应方案内创建递增版本。

`AGENTS.md` 开头的专家角色和官方指南入口，以及正式版 `SETUP.md` 中的 OpenClash 设置建议，都是不可删除的仓库前提；任何整理不得删除或削弱这些内容。

本仓库现行发布门禁要求需要本地模块的正式 Release 在创建时附独立模板资产，避免发布后补改。仅本次 v1.0.0 补充模板附件及相应填写说明由用户于 2026-10-17 明确授权；附件必须与不可变标签中的占位模板逐字节一致，不改标签源码、版本文件或既有附件。此例外不授权发布后进行其他补改。

## 当前正式基线

当前唯一支持方案是 `tiktok-router-loongproxy-jp-us v1.0.0`（J1–J11，stable），索引位于 `profiles/catalog.json`。用户于 2026-10-16 确认实机验收通过并授权正式发布；不补写用户未提供的逐项日志或指标。

**不可改变的链路前提：**路由器本地 Loongproxy 美国 SOCKS5 必须通过用户手选的 iKuuu 日本节点建立链式代理。`TikTok-ISP-Local` 必须保留 `dialer-proxy: 日本-入口` 与 `udp: false`。日本入口自动筛选已加载节点中名称含 `jp`、`日本`、`Japan` 或 🇯🇵 的节点（忽略大小写），但必须由用户选中实际 iKuuu 日本节点。日本节点缺失或不可用时失败关闭，严禁切换美国首跳、其他机场首跳、机场/DIRECT 回退。

Google/Google Play 与其他境外流量走用户手选的美国组；中国大陆域名和 IP 直连；保留完整 129 条 Manual-Direct。日本、美国和 ISP 组均须排除本地 ISP 节点以避免递归，空组保持 REJECT。

## 配置与凭据

- 单个配置仅启用一个完整云覆写及其配套本地节点模块。云模块管理规则；本地模块只追加精确名为 `TikTok-ISP-Local` 的 SOCKS5 节点。
- 更新规则只刷新正式云覆写模块并重启 OpenClash；机场节点订阅、GEO 数据各自更新。
- 修改 Loongproxy 密码时，只在路由器本地 `TikTok-ISP-Local` 模块改 `password`；按本地服务商提供的信息同步修改 `username`、`server`、`port`（如有变化）。保留节点名、`type: socks5`、`udp: false`、`dialer-proxy: 日本-入口`。详细 UI 路径见版本 `SETUP.md`。
- 真实 ISP 主机、账号和密码只存路由器本地模块，不进入仓库、云覆写、PR 或日志。公共仓库只保留 `.example` 占位模板。
- 需要本地模块的每个正式 Release 都必须附上独立可下载的 `.example` 模板、附件 SHA-256 和标签固定填写说明；自动源码归档不能代替模板附件。
- 所有模块仅含 `[YAML]`；OpenClash 插件选项由用户在 LuCI 手工设置，禁止覆写模块写入 `[General]`、UCI 或自动修改插件设置。

## 规则与版本

- 保持规则优先级：私网/局域网 → TikTok ISP → 同范围 TikTok REJECT → Google/Play → Manual-Direct → 中国大陆域名/IP → 美国 MATCH。
- `rules/manual-direct.yaml` 保留原始 129 条；`rules/manual-direct-isp.yaml` 按原顺序逐条转换为 `DOMAIN-SUFFIX` 并保留重复项。若授权改规则，须同步固定模块、滚动模块、inline payload、校验和与文档。
- 已发布版本目录和标签不可改写、移动或覆盖。现有方案的行为变化须建立高于该方案已记录最高版本的新候选版本及独立完整 URL；新需求应建立独立方案并从自己的版本线开始。真实设备验收前保持 candidate。晋升 stable、创建正式标签和 GitHub Release 需用户明确授权。
- 当前版本记录只保留 `v1.0.0` 首个正式版；旧版本及 beta 的当前目录、标签和 Release 已清理。保留 Git 提交历史，不重写历史。

## 每次变更门禁

必须遵循 [`DEVELOPMENT_RULES.md`](DEVELOPMENT_RULES.md)。开始工作前阅读 `AGENTS.md`、`README.md`、`profiles/catalog.json` 和受影响方案/版本的 `REQUIREMENTS.md`、`SETUP.md`、`ENVIRONMENT.json`（若存在）；标明方案 ID、需求编号与版本类型；完成对应文档、环境记录和 `CHANGELOG.md`；检查凭据及完整差异；运行：

```text
python -m unittest discover -s scripts -p "test_*.py"
python scripts/validate_repository.py --base-ref origin/main
git diff --check
```

若没有可用 Git 比较基线，可省略 `--base-ref`，但不得声称历史保护校验已执行。静态检查、桌面核心夹具与真实设备验收必须分开记录。新版本的 OpenClash 环境记录和日志门禁按 `DEVELOPMENT_RULES.md` 执行；原始调试日志不得提交到公共仓库。
