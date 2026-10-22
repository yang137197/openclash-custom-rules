# tiktok-router-loongproxy-jp-us v1.0.2 — 候选部署与测试

**状态：candidate，待用户实机验证。** 本候选仅测试 Claude Code 域名是否能经现有 TikTok-ISP 策略组访问。稳定版 v1.0.0、滚动云覆写、Release 和本地凭据模块均不修改。

## 导入候选覆写

测试链接（分支候选，尚未合并 main）：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/codex/claude-code-tiktok-test/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.2/openclash-overwrite.conf

按 **服务 → OpenClash → 运行状态 → 页面顶部「覆写模块」** 添加订阅模块，匹配当前配置的完整路径或 all。保留本地 TikTok-ISP-Local 节点模块，真实 ISP 凭据不需要改动。测试时只启用一个完整云覆写：启用 v1.0.2 候选模块，停用当前完整云覆写模块；保留原模块以便回退。候选中的测试规则已保留私网直连并排在后续分流规则之前。保存后重启 OpenClash。

OpenClash 的模块格式、规则前置操作符及重启生效机制见官方指南 [16-overwrite-module-format.md §16.1、§16.2.3](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md) 和 [17-overwrite-module-examples.md §17.3.5](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/17-overwrite-module-examples.md)。官方指南入口的路由表见 [SKILL.md](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md)。

## 测试 Claude Code

1. 仪表盘中确认 TikTok-ISP 选择本地节点 TikTok-ISP-Local；确认该节点仍设置 dialer-proxy: 日本-入口，并在 日本-入口 中手选实际 iKuuu 日本节点。这是 Loongproxy 链路的强制首跳。
2. 关闭并重新启动 Claude Code，发起一条新的普通请求。检查 OpenClash 新连接记录：api.anthropic.com 应命中 DOMAIN-SUFFIX,anthropic.com,TikTok-ISP，策略组使用 TikTok-ISP。确认请求成功，不能只凭规则命中判定链路可用。
3. 如果希望额外测试登录、更新或插件，需实际触发这些功能，再核对 claude.ai/claude.com、downloads.claude.ai、registry.npmjs.org 等对应连接。Chrome、Artifact、Gerrit、Datadog 和 Homebrew 端点属于可选或条件性功能，不产生连接时无需测试。
4. 其他应用访问清单中的 GitHub、npm、Google Storage 等域名时也会走 TikTok-ISP；这是域名分流的正常范围，不代表只匹配 Claude Code 进程。自定义 MCP 和第三方依赖仍可能使用清单外域名。

## 继承的 OpenClash 设置与回退

本候选不更改插件设置。此前已验收设置建议、ISP 凭据填写方法、日本首跳选择和完整部署说明继续见 [v1.0.0 SETUP.md](../v1.0.0/SETUP.md)。v1.0.1 的 Samsung 直连候选不在本候选内。

回退时停用 v1.0.2 候选完整云覆写，重新启用原稳定云覆写并重启 OpenClash；保留 TikTok-ISP-Local 本地模块。不要将真实 ISP 凭据写入云覆写或仓库。

实机测试完成前，本候选不替换稳定入口、不创建 Release 或正式标签。
