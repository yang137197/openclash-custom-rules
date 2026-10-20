# tiktok-router-loongproxy-jp-us

**v1.0.0 stable**：TikTok 必须使用 iKuuu 日本节点作为 Loongproxy 美国 SOCKS5 的链式第一跳。用户于 2026-10-16 确认实机验收通过并授权正式发布。

**v1.0.1 candidate**：新增 `update.kies.samsung.com` 精确域名直连规则，尚待路由器验收；稳定入口仍是 v1.0.0。

**v1.0.2 candidate**：按 Claude Code 官方网络端点把相关域名指向 `TikTok-ISP`，由用户实机验证；不按设备 IP 或进程分流，也不包含尚未验收的 v1.0.1 Samsung 规则。稳定入口仍是 v1.0.0。

**v1.0.3 candidate**：继承 v1.0.2 的 Claude Code 端点分流，并将 Claude 网页相关 Anthropic/Claude 第一方域名（含 `claudemcpcontent.com`）统一指向 `TikTok-ISP`。该版本规则命中不证明公网出口 IP 恒定；测试改进见 v1.0.4。稳定入口仍是 v1.0.0。

**v1.0.4 candidate（最新测试版）**：延续 Claude/Anthropic 第一方域名经 `TikTok-ISP`，并把 `github.com`、`githubusercontent.com`、`githubassets.com` 明确改走美国组，覆盖 GitHub 网站、内容下载及页面静态资源，避免这些连接经过带宽受限的 ISP。依据是用户日志确认 GitHub 命中 v1.0.3 的 TikTok 规则及用户报告的变慢；性能恢复待实测。稳定入口仍是 v1.0.0。

最新测试覆写订阅链接（v1.0.4 分支候选）：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/codex/claude-code-tiktok-test/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.4/openclash-overwrite.conf

- [v1.0.4 候选覆写](versions/v1.0.4/openclash-overwrite.conf)
- [v1.0.4 候选需求与验收条件](versions/v1.0.4/REQUIREMENTS.md)
- [v1.0.4 候选部署与设置](versions/v1.0.4/SETUP.md)
- [v1.0.4 环境记录](versions/v1.0.4/ENVIRONMENT.json)
- [v1.0.3 候选覆写](versions/v1.0.3/openclash-overwrite.conf)
- [v1.0.3 候选需求与验收条件](versions/v1.0.3/REQUIREMENTS.md)
- [v1.0.3 候选部署与设置](versions/v1.0.3/SETUP.md)
- [v1.0.3 环境记录](versions/v1.0.3/ENVIRONMENT.json)
- [v1.0.2 候选覆写](versions/v1.0.2/openclash-overwrite.conf)
- [v1.0.2 候选需求与验收条件](versions/v1.0.2/REQUIREMENTS.md)
- [v1.0.2 候选部署与设置](versions/v1.0.2/SETUP.md)
- [v1.0.1 候选覆写](versions/v1.0.1/openclash-overwrite.conf)
- [v1.0.1 候选需求与验收条件](versions/v1.0.1/REQUIREMENTS.md)
- [v1.0.1 候选部署与设置](versions/v1.0.1/SETUP.md)

- [部署、验收及本地 ISP 密码修改](versions/v1.0.0/SETUP.md)
- [J1–J11 正式需求合同](versions/v1.0.0/REQUIREMENTS.md)
- [固定版本完整覆写](versions/v1.0.0/openclash-overwrite.conf)
- [滚动云覆写](overwrite/openclash-overwrite.conf)
- [下载唯一的本地节点占位模板](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.0/tiktok-router-loongproxy-jp-us-v1.0.0-local-module.conf.example)；字段对应和虚构填写示例见 [v1.0.0 Release 正文](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-v1.0.0)。填入真实凭据后只保存在路由器本地。

正式云覆写订阅链接：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

固定使用 v1.0.0 时，Release 正文与下方地址提供相同的标签固定覆写订阅链接；它不会随 `main` 更新：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/openclash-overwrite.conf

日本组按名称自动纳入已加载节点，但实际使用时必须手选 iKuuu 的日本节点。缺少匹配的日本节点时保持 REJECT，不得改用其他首跳或添加机场/DIRECT 回退。真实 ISP 地址和凭据只配置在路由器本地模块。
