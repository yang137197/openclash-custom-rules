# OpenClash 远程覆写规则

本仓库可以维护多个需求不同的独立方案。每个方案有自己的需求合同、版本序列、固定覆写链接和 Release；版本号只在同一方案内递增。当前已发布方案：**tiktok-router-loongproxy-jp-us v1.0.0 / stable**。TikTok 必须经 iKuuu 日本节点作为第一跳，再由路由器本地 Loongproxy 美国 SOCKS5 出口。日本首跳是 Loongproxy 链式代理的前提；不得改为美国首跳，也不得在日本节点缺失时回退到机场或 DIRECT。

## 方案目录

| 方案 | 适用需求 | 稳定版本 | Release | 固定覆写链接 | 部署与设置 |
| --- | --- | --- | --- | --- | --- |
| [tiktok-router-loongproxy-jp-us](profiles/tiktok-router-loongproxy-jp-us/README.md) | TikTok 经 iKuuu 日本首跳链式连接 Loongproxy 美国 SOCKS5 | v1.0.0 | [Release](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-v1.0.0) | [v1.0.0 YAML](https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/openclash-overwrite.conf) | [设置与验收](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/SETUP.md) |

新增规则需求应建立独立方案，不能复用其他方案的需求合同、版本 URL 或滚动入口。候选版和正式版的开发、环境信息、Release 内容及验收要求见 [`DEVELOPMENT_RULES.md`](DEVELOPMENT_RULES.md)。

当前另有未验收候选：v1.0.1 仅新增 `update.kies.samsung.com` 精确域名直连；v1.0.2 用于 Claude Code 端点分流；最新 v1.0.3 继承前者并将 Claude 网页相关 Anthropic/Claude 第一方域名统一指向 TikTok-ISP。稳定入口仍为 v1.0.0。候选覆写和验收要求见[方案说明](profiles/tiktok-router-loongproxy-jp-us/README.md)。

v1.0.3 测试覆写链接：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/codex/claude-code-tiktok-test/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.3/openclash-overwrite.conf

更换 AI 开发工具或开启新对话时，在已打开本仓库的工具中说“请你先读取仓库，我们继续开发”，按开发规则读取当前方案、版本、Git 状态和未完成事项后接续。工具需先能访问本仓库；跨工具交接以仓库文件为准。

- [部署、验收与本地 ISP 密码修改说明](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/SETUP.md)
- [J1–J11 正式需求合同](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/REQUIREMENTS.md)
- [正式完整云覆写](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/openclash-overwrite.conf)

## 云覆写订阅链接

当前稳定版的滚动入口会随 `main` 更新：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

固定使用 v1.0.0 时，请使用对应 Release 的标签固定地址；此链接不会随 `main` 更新：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/openclash-overwrite.conf

日本入口自动筛选当前配置中已加载节点和 proxy-provider 里名称含 `jp`、`日本`、`Japan` 或 🇯🇵 的节点，忽略大小写；用户需在策略组中手动选择 iKuuu 的日本节点。名称筛选不会验证节点所属供应商或连通性。没有匹配的 iKuuu 日本首跳时，相关链路保持失败关闭。

国内域名和大陆 IP 直连；Google/Google Play 走美国组；保留 129 条 Manual-Direct；其余境外流量走手选美国组。云覆写只需刷新一个模块并重启 OpenClash；机场节点订阅及 GEO 数据仍独立更新。

## 维护基线

2026-10-16，用户确认 CatWrt/OpenClash 实机验收通过并授权正式发布。验收记录按用户总体确认保存，不补造逐项日志。Loongproxy 必须通过 iKuuu 日本首跳建立链式代理，是此正式方案不可更改的前提。

当前仓库以 `tiktok-router-loongproxy-jp-us v1.0.0` 作为首个正式版本；当前只有这一个正式方案。此前旧方案版本和 beta 的标签与 Release 已清理，Git 提交历史保留。未来新增需求使用独立方案 ID 和版本线；同一方案内版本严格递增，并在 `CHANGELOG.md` 记录具体更新。正式版部署文档中的 OpenClash 设置建议、仓库专家角色和官方指南入口均为不可删除前提。真实 ISP 地址、用户名和密码只能放在路由器的本地模块，不能提交到云覆写或 Git。

维护前阅读 [AGENTS.md](AGENTS.md)、[开发规则](DEVELOPMENT_RULES.md)、[MAINTENANCE.md](MAINTENANCE.md)、[版本索引](profiles/catalog.json) 和目标方案的需求合同、部署设置及环境记录。OpenClash 技术依据为[官方用户指南及文档路由表](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md)。
