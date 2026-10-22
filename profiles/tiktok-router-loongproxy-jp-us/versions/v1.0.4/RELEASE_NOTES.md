# tiktok-router-loongproxy-jp-us v1.0.4

**正式版（stable）**。用户于 2026-10-22 确认 OpenClash 实机验收通过。

## 适用规则

- Loongproxy 美国 SOCKS5 必须通过用户手选的 iKuuu 日本节点建立链式代理，`dialer-proxy: 日本-入口`。这是强制首跳；不允许替换首跳或在链路不可用时回退到机场、美国组或 `DIRECT`。
- Claude Code 端点及 Claude 网页的 Anthropic/Claude 第一方域名走 `TikTok-ISP`，保持同一静态 ISP 出口；这些域名规则作用于所有经 OpenClash 的客户端。
- GitHub 网站、API、下载内容和页面静态资源域名 `github.com`、`githubusercontent.com`、`githubassets.com` 走 `美国`，不走 TikTok ISP。
- 规则顺序：私网/局域网直连 → Claude Code 与 Claude/Anthropic 第一方域名走 TikTok-ISP、GitHub 指定域名走美国 → 通用 TikTok 规则及紧邻拒绝规则 → Google/Google Play 走美国 → 保留 129 条 Manual-Direct → 中国大陆域名/IP 直连 → 其他境外流量走美国组。

## OpenClash 环境与验收

- OpenClash：0.48.002；提供的版本标签未单独标出 OpenClash 构建号。
- Mihomo：alpha-gbc76c13。
- OpenWrt：24.10.2 r7492-3fda82b52；x86_64；QEMU Standard PC (2C2T)。
- 当前配置标识：`ikuuu`。模块启用顺序：云覆写在上，本地 TikTok-ISP 模块在下。
- 设置建议、LuCI 路径、部署和回退步骤见 [SETUP.md](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.4/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.4/SETUP.md)；需求和边界见 [REQUIREMENTS.md](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.4/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.4/REQUIREMENTS.md)；脱敏环境记录见 [ENVIRONMENT.json](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.4/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.4/ENVIRONMENT.json)。
- OpenClash 设置基线：Fake-IP 增强模式、规则模式；UDP 转发和路由器本机代理开启；绕过中国大陆 IPv4、禁用 QUIC；IPv6 代理/DNS/区域绕过关闭；本地 DNS 劫持用 Dnsmasq 转发；DNS 遵守路由规则并启用 Fake-IP 持久化。逐项 LuCI 路径、条件与风险见 `SETUP.md`。
- 仓库静态验证与用户路由器实机验收分别记录。没有可复核的延迟或下载速度数据；本 Release 不表示 GitHub、Claude 或无线端性能已改善。

## 固定覆写订阅

使用此标签固定链接获取 v1.0.4 完整云覆写：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.4/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.4/openclash-overwrite.conf

模块 SHA-256：`22f932afbc328e1d0d2188519378032e4db0b9cbbb9ce4ed7a8433f585741e6a`

## 本地模块模板与填写方法

下载此 Release 唯一提供的本地模块占位模板：

[下载 tiktok-router-loongproxy-jp-us-v1.0.4-local-module.conf.example](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.4/tiktok-router-loongproxy-jp-us-v1.0.4-local-module.conf.example)

附件 SHA-256：`0e36b6ff302f28deabb96dcd90f70c0deef44ba1d9af73f3501f5d2590dd0bd4`

按 Loongproxy 服务商提供的 SOCKS5 代理信息填写占位字段：

- `FILL_ME_PROXY_HOST`：填写服务商给出的**代理地址/IP**，不是单独的“出口 IP”栏；把占位文字替换为代理地址，保留左右单引号，例如 `server: '203.0.113.10'`。
- `FILL_ME_PROXY_PORT`：填写服务商给出的代理端口数字，例如 `20000`；替换占位文字，不加引号。
- `FILL_ME_USERNAME`：填写服务商提供的用户名，保留模板中的左右单引号。
- `FILL_ME_PASSWORD`：填写服务商提供的密码，保留模板中的左右单引号。
- 保留 `name: TikTok-ISP-Local`、`type: socks5`、`udp: false` 和 `dialer-proxy: 日本-入口`。特别是不能移除或更改日本首跳字段。

虚构填写示例（仅展示格式，不是真实服务商凭据）：

```yaml
[YAML]
proxies+:
  - name: TikTok-ISP-Local
    type: socks5
    server: '203.0.113.10'
    port: 20000
    username: 'demo_user'
    password: 'demo_password'
    udp: false
    dialer-proxy: 日本-入口
```

填写完成后，仅将本地模块导入路由器，模块顺序为云覆写在上、本地 TikTok-ISP 模块在下。真实凭据只保存在路由器本地，禁止上传或分享填好的文件。GitHub 自动生成的 `Source code (zip)` 和 `Source code (tar.gz)` 是源码快照，不是本地节点模块模板。
