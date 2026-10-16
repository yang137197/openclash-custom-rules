# OpenClash 远程覆写规则

当前开发方案 **tiktok-router-loongproxy-jp-us v1.0.0 / candidate**：日本机场首跳 → 本地 Loongproxy 美国 SOCKS5 → TikTok。尚未完成 CatWrt/OpenClash 手机验收。

- [部署与验收](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/SETUP.md)
- [J1–J12 需求合同](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/REQUIREMENTS.md)
- [完整云覆写](profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf)
- [本地节点占位模板](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/local-tiktok-proxy.conf.example)

日本入口自动筛选当前机场配置中已加载的节点和代理提供商，匹配名称任意位置的 `jp`、`日本`、`Japan` 或 🇯🇵，不区分大小写。自动纳入后仍由用户手选节点；没有匹配节点时保持 REJECT。云覆写不提供机场订阅或私有凭据。

## 当前候选订阅

PR #8 未合并时使用开发分支地址：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/feature/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

只启用一个完整云覆写及其配套本地节点模块。后续规则更新只需刷新该云覆写并重启 OpenClash；129 条 Manual-Direct 已内嵌，无需单独更新规则提供者。机场订阅、Geo 数据仍独立更新。

## 分流约定

1. 私网、局域网直连。
2. TikTok 走专属 ISP，紧随同范围 REJECT，防止不支持 UDP 时继续匹配其他出口。
3. Google / Google Play 走美国。
4. 保留 129 条 Manual-Direct；每条覆盖其域名本身及子域名。
5. 已知中国大陆域名及大陆 IP 直连。
6. 其余流量走手选美国组。

Geo 数据不保证覆盖全部大陆域名；名称筛选也不证明节点可用。TikTok 缺节点或拨号失败时不得回退机场或直连。

## 维护范围

2026-10-16 按用户授权清除停用旧方案的当前目录、索引、说明及根兼容入口；原 Git 提交、标签和 Release 保留。清理没有晋升候选，当前文件树无稳定入口（`currentProfile=null`）。

仍保留 [美国首跳 Loongproxy 候选](profiles/tiktok-router-isp-us/README.md) 作为独立方案，不与本次日本首跳混用；原始 129 条规则保存在 [manual-direct.yaml](rules/manual-direct.yaml)，后缀副本为 [manual-direct-isp.yaml](rules/manual-direct-isp.yaml)。

维护前阅读 [AGENTS.md](AGENTS.md)、[MAINTENANCE.md](MAINTENANCE.md) 和 [版本索引](profiles/catalog.json)。技术依据为 [OpenClash 官方指南及文档路由表](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md)。
