# OpenClash 远程覆写规则

本仓库按需求维护独立的 OpenClash 方案。当前正式方案为 **tiktok-router-loongproxy-jp-us v1.0.5 / stable**。TikTok 必须经用户手选的 iKuuu 日本节点作为第一跳，再由路由器本地 Loongproxy 美国 SOCKS5 出口；缺少日本首跳时失败关闭。

## 方案目录

| 方案 | 适用需求 | 稳定版本 | Release | 固定覆写链接 | 部署与设置 |
| --- | --- | --- | --- | --- | --- |
| [tiktok-router-loongproxy-jp-us](profiles/tiktok-router-loongproxy-jp-us/README.md) | TikTok 与 Claude/Anthropic 经 Loongproxy 静态 ISP；GitHub、Google 和其他境外流量走美国组；中国大陆直连 | v1.0.5 | [Release](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-v1.0.5) | [v1.0.5 YAML](https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.5/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.5/openclash-overwrite.conf) | [设置与验收](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.5/SETUP.md) |

### 当前方案要点

- 私网/局域网优先直连；Claude/Anthropic 专项域名走 `TikTok-ISP`，GitHub 专项域名走美国组；二者位于通用 TikTok 规则之前。TikTok 保持紧邻拒绝规则；Google/Google Play 走美国组；保留 129 条 Manual-Direct；中国大陆域名/IP 直连；其余境外流量走美国组。
- Loongproxy 美国 SOCKS5 必须通过 iKuuu 日本首跳，`dialer-proxy: 日本-入口`。不得改用美国或其他机场首跳，也不得在链路不可用时回退机场或 DIRECT。
- 真实 ISP 地址、账号和密码只填写到路由器本地节点模块。v1.0.5 Release 提供 `.conf` 模板并在正文说明字段映射与虚构填写示例；v1.0.4 的历史附件名为 `.conf.example`，使用前先改名。
- v1.0.5 仅修正模板扩展名，云覆写内容不变；OpenClash 本地文件选择器尚未在路由器实测，详见[环境记录](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.5/ENVIRONMENT.json)。
- 用户于 2026-10-22 确认 v1.0.4 实机验收通过。日志确认 GitHub 分流规则和运行环境；未提供可复核的延迟/下载速度改善数据，因此不宣称性能已恢复。

当前稳定版的滚动云覆写入口会随 `main` 更新：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

固定使用 v1.0.5 时，使用 Release 标签固定地址；该地址不会随 `main` 更新：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.5/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.5/openclash-overwrite.conf

## 版本索引

v1.0.5 是当前正式版。它继承 v1.0.4 已验收的分流规则，仅修正本地模板扩展名；v1.0.1 的 Samsung 直连、v1.0.2 的 Claude Code、v1.0.3 的 Claude 网页分流仍是未验收候选，不包含在当前正式版中。v1.0.4 已发布目录、标签和 Release 保持不变。

开发规则、候选信息门禁、日志隐私与跨工具接续要求见 [`DEVELOPMENT_RULES.md`](DEVELOPMENT_RULES.md)。更换 AI 开发工具或开启新对话时，在已打开仓库的工具中说“请你先读取仓库，我们继续开发”，再按规则恢复当前状态。
