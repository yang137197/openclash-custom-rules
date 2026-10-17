# OpenClash 远程覆写规则

当前正式方案 **tiktok-router-loongproxy-jp-us v1.0.0 / stable**：TikTok 必须经 iKuuu 日本节点作为第一跳，再由路由器本地 Loongproxy 美国 SOCKS5 出口。日本首跳是 Loongproxy 链式代理的前提；不得改为美国首跳，也不得在日本节点缺失时回退到机场或 DIRECT。

- [部署、验收与本地 ISP 密码修改说明](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/SETUP.md)
- [J1–J11 正式需求合同](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/REQUIREMENTS.md)
- [正式完整云覆写](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/openclash-overwrite.conf)
- [本地节点占位模板（不含凭据）](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/local-tiktok-proxy.conf.example)

## 正式云覆写链接

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

日本入口自动筛选当前配置中已加载节点和 proxy-provider 里名称含 `jp`、`日本`、`Japan` 或 🇯🇵 的节点，忽略大小写；用户需在策略组中手动选择 iKuuu 的日本节点。名称筛选不会验证节点所属供应商或连通性。没有匹配的 iKuuu 日本首跳时，相关链路保持失败关闭。

国内域名和大陆 IP 直连；Google/Google Play 走美国组；保留 129 条 Manual-Direct；其余境外流量走手选美国组。云覆写只需刷新一个模块并重启 OpenClash；机场节点订阅及 GEO 数据仍独立更新。

## 维护基线

2026-10-16，用户确认 CatWrt/OpenClash 实机验收通过并授权正式发布。验收记录按用户总体确认保存，不补造逐项日志。Loongproxy 必须通过 iKuuu 日本首跳建立链式代理，是此正式方案不可更改的前提。

当前仓库以 `v1.0.0` 作为首个正式版本，当前记录只保留这一正式方案。旧版本和 beta 的标签与 Release 已清理，Git 提交历史保留。后续版本必须严格递增并在 `CHANGELOG.md` 记录具体更新内容。正式版部署文档中的 OpenClash 设置建议、仓库专家角色和官方指南入口均为不可删除前提。真实 ISP 地址、用户名和密码只能放在路由器的本地模块，不能提交到云覆写或 Git。

维护前阅读 [AGENTS.md](AGENTS.md)、[MAINTENANCE.md](MAINTENANCE.md)、[版本索引](profiles/catalog.json) 和本版本 [REQUIREMENTS.md](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/REQUIREMENTS.md)。OpenClash 技术依据为[官方用户指南及文档路由表](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md)。
