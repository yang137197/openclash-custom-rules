# OpenClash 远程覆写规则

本仓库按需求维护独立的 OpenClash 方案。当前正式方案为 **tiktok-router-loongproxy-jp-us v1.0.6 / stable**。TikTok 必须经用户手选的 iKuuu 日本节点作为第一跳，再由路由器本地 Loongproxy 美国 SOCKS5 出口；缺少日本首跳时失败关闭。

## 方案目录

| 方案 | 适用需求 | 稳定版本 | Release | 固定覆写链接 | 部署与设置 |
| --- | --- | --- | --- | --- | --- |
| [tiktok-router-loongproxy-jp-us](profiles/tiktok-router-loongproxy-jp-us/README.md) | TikTok 与 Claude/Anthropic 经 Loongproxy 静态 ISP；GitHub、Google 和其他境外流量走美国组；中国大陆直连，含 Huzhou 后缀直连 | v1.0.6 | [Release](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-v1.0.6) | [v1.0.6 YAML](https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.6/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.6/openclash-overwrite.conf) | [设置与验收](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.6/SETUP.md) |

### 当前方案要点

- 私网/局域网优先直连；Claude/Anthropic 专项域名走 `TikTok-ISP`，GitHub 专项域名走美国组；二者位于通用 TikTok 规则之前。TikTok 保持紧邻拒绝规则；Google/Google Play 走美国组；`huzhou.host` 主域名及全部子域名走 DIRECT；保留 129 条 Manual-Direct；中国大陆域名/IP 直连；其余境外流量走美国组。
- Loongproxy 美国 SOCKS5 必须通过 iKuuu 日本首跳，`dialer-proxy: 日本-入口`。不得改用美国或其他机场首跳，也不得在链路不可用时回退机场或 DIRECT。
- 真实 ISP 地址、账号和密码只填写到路由器本地节点模块。v1.0.6 Release 提供 `.conf` 模板并在正文说明字段映射与虚构填写示例；v1.0.4 的历史附件名为 `.conf.example`，使用前先改名。
- v1.0.6 新增 `DOMAIN-SUFFIX,huzhou.host,DIRECT`，覆盖主域名及其所有子域名。环境、验收证据和设置偏差见[环境记录](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.6/ENVIRONMENT.json)。本地文件选择器本次未在路由器实测。
- 用户于 2026-10-22 确认 v1.0.4 实机验收通过。日志确认 GitHub 分流规则和运行环境；未提供可复核的延迟/下载速度改善数据，因此不宣称性能已恢复。

当前稳定版的滚动云覆写入口会随 `main` 更新：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

v1.0.7 候选验收并发布后，手动直连域名的唯一维护入口为 [`rules/manual-direct.yaml`](rules/manual-direct.yaml)。在 `payload` 中新增、修改或删除规则并提交到 GitHub `main`；GitHub Actions 将自动生成滚动远程覆写中的 inline 规则并更新 catalog 哈希。先等待同步工作流成功及生成提交，再在路由器使用同一远程地址点击“更新”并重启 OpenClash。日常规则数据调整不创建 Release。唯一的本地覆写模块是 `tiktok-router-loongproxy`，完整云覆写使用远程模块。修改规则优先级、策略组、DNS、代理链路或其他运行逻辑属于大版本更新/重构，须走候选验证；用户验收后发布正式版本。

固定使用 v1.0.6 时，使用 Release 标签固定地址；该地址不会随 `main` 更新：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.6/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.6/openclash-overwrite.conf

## 版本索引

v1.0.6 是当前正式版，新增 `huzhou.host` 主域名及全部子域名直连。v1.0.7 是待验收候选，重构手动规则自动同步；当前稳定版 v1.0.6 和已发布目录、标签及 Release 均保持不变。v1.0.1–v1.0.3 仍是历史未验收候选。

开发规则、候选信息门禁、日志隐私与跨工具接续要求见 [`DEVELOPMENT_RULES.md`](DEVELOPMENT_RULES.md)。更换 AI 开发工具或开启新对话时，在已打开仓库的工具中说“请你先读取仓库，我们继续开发”，再按规则恢复当前状态。
