# tiktok-router-loongproxy-jp-us v1.0.6

**正式版（stable）**，用户于 2026-10-28 确认候选实机验收通过。新增 `DOMAIN-SUFFIX,huzhou.host,DIRECT`，覆盖主域名及全部子域名；其他需求、规则顺序、代理链路和插件设置均继承 v1.0.5。

## 适用规则

- Loongproxy 美国 SOCKS5 必须通过用户手选的 iKuuu 日本节点建立链式代理，`dialer-proxy: 日本-入口`。这是强制第一跳；链路不可用时不回退其他机场或 `DIRECT`。
- 规则优先级保持 v1.0.5：私网/局域网 → Claude Code 与 Claude/Anthropic、GitHub 专项规则 → TikTok 与拒绝规则 → Google/Google Play → Huzhou 与 Manual-Direct → 中国大陆规则 → 美国 MATCH。
- J17：`huzhou.host` 主域名及全部子域名直连，不匹配仅含相似字符串的其他域名。
- 保留原有 129 条 Manual-Direct 记录。Huzhou 使用独立主规则，位于 Google 规则之后、Manual-Direct 及中国大陆规则之前。
- 真实 ISP 地址、账号、密码只填写在唯一的本地 `tiktok-router-loongproxy` 节点模块。完整云覆写必须使用远程订阅模块。

## OpenClash 环境与验收

- OpenClash：0.48.002（调试日志未单独标出插件构建号）。
- Mihomo：alpha-gbc76c13。
- OpenWrt：24.10.2 r7492-3fda82b52；x86_64；QEMU Standard PC。
- 2026-10-28 调试日志显示运行配置含 Huzhou DIRECT 规则，访问 `huzhou.host:4443` 命中 `DomainSuffix(huzhou.host)` 并走 `DIRECT`。用户确认候选验收通过；日志本身未记录子域名连接。
- 验收环境的“禁用 QUIC”为停用，与 `SETUP.md` 建议开启不同；本版本不调整该设置，测试连接为 TCP。
- 本地模块 `.conf` 文件选择器未在本次路由器实测。完整设置建议、部署与回退见 [SETUP.md](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.6/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.6/SETUP.md)；需求边界见 [REQUIREMENTS.md](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.6/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.6/REQUIREMENTS.md)，环境字段见 [ENVIRONMENT.json](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.6/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.6/ENVIRONMENT.json)。原始调试日志不随版本公开。

## 固定覆写订阅

在 OpenClash 远程覆写模块中使用此标签固定地址：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.6/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.6/openclash-overwrite.conf

云覆写 SHA-256：`79744763d8c28ff591de7c55c612724290c275faf0018d26b9e89ce539d36d42`

现有 `main` 滚动覆写地址也已同步 v1.0.6；保持原远程地址后点击更新并重启 OpenClash 即可。远程覆写模块内容只会在插件启动/重启时应用。

## 唯一本地节点模板

[下载 tiktok-router-loongproxy-jp-us-v1.0.6-local-module.conf](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.6/tiktok-router-loongproxy-jp-us-v1.0.6-local-module.conf)

附件 SHA-256：`d7639bd7ac733c2312103bcb8e73764b2b354b3ccb7bcb578f7ee5d3706da522`

按服务商提供的 SOCKS5 信息填写模板中的 `FILL_ME_PROXY_HOST`、`FILL_ME_PROXY_PORT`、`FILL_ME_USERNAME` 和 `FILL_ME_PASSWORD`。保留节点名 `TikTok-ISP-Local`、`type: socks5`、`udp: false` 和 `dialer-proxy: 日本-入口`。示例地址 `203.0.113.10`、端口 `20000`、用户名 `demo_user`、密码 `demo_password` 均为虚构值。

真实凭据只保存在路由器本地模块。不要提交或公开填好凭据的文件。OpenClash 设置与回退步骤见上方 `SETUP.md`。
