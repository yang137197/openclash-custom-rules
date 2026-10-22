# tiktok-router-loongproxy-jp-us v1.0.3 — 候选部署与测试

**状态：candidate，待用户实机验证。** 本候选把 Claude Code 官方端点及 Claude 网页的 Anthropic/Claude 第一方域名统一指向现有 TikTok-ISP 策略组。稳定版 v1.0.0、滚动云覆写、Release 和本地凭据模块均不修改。

## 导入候选覆写

测试链接（分支候选，尚未合并 main）：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/codex/claude-code-tiktok-test/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.3/openclash-overwrite.conf

按 **服务 → OpenClash → 运行状态 → 页面顶部「覆写模块」** 添加订阅模块，匹配当前配置的完整路径或 all。保留本地 TikTok-ISP-Local 节点模块，真实 ISP 凭据不需要改动。测试时只启用一个完整云覆写：启用 v1.0.3 候选模块，停用当前完整云覆写模块；保留原模块以便回退。候选中的测试规则已保留私网直连并排在后续分流规则之前。保存后重启 OpenClash。

OpenClash 的模块格式、规则前置操作符及重启生效机制见官方指南 [16-overwrite-module-format.md §16.1、§16.2.3](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md) 和 [17-overwrite-module-examples.md §17.3.5](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/17-overwrite-module-examples.md)。官方指南入口的路由表见 [SKILL.md](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md)。

## 测试 Claude 网页与 Claude Code

1. 仪表盘中确认 TikTok-ISP 选择本地节点 TikTok-ISP-Local；确认该节点仍设置 dialer-proxy: 日本-入口，并在 日本-入口 中手选实际 iKuuu 日本节点。这是 Loongproxy 链路的强制首跳。
2. 打开 Claude 网页，重新登录（如需要）并发送一条消息。检查本次实际出现的 `claude.ai`、`assets.claude.ai`、`assets-proxy.anthropic.com`、`s-cdn.anthropic.com` 等 Anthropic/Claude 连接，均命中 TikTok-ISP；连接详情应显示本地 TikTok-ISP-Local 及已手选的 iKuuu 日本首跳。
3. 如果对话中使用 MCP 交互组件，再检查实际出现的 `*.claudemcpcontent.com` 请求；Chrome 扩展/Artifact 等其他可选功能也只有在触发后才验证。Claude Code 可另外发起一条请求，检查实际出现的 `api.anthropic.com` 等端点。
4. 确认网页和请求能正常完成。若要确认公网出口 IP，使用外部 IP 检测分别核对；仅看到策略组命中不能证明 ISP 公网 IP 恒定。共享的第三方字体/CDN、用户自定义 MCP 和插件域名不在本候选保证范围内。
5. 其他应用访问规则中的 GitHub、npm、Google Storage 或 Anthropic/Claude 域名也会匹配 TikTok-ISP；规则按域名作用于所有客户端，不会只识别 Claude 浏览器或 Claude Code 进程。

## 继承的 OpenClash 设置与回退

本候选不更改插件设置。此前已验收设置建议、ISP 凭据填写方法、日本首跳选择和完整部署说明继续见 [v1.0.0 SETUP.md](../v1.0.0/SETUP.md)。v1.0.1 的 Samsung 直连候选不在本候选内。

回退时停用 v1.0.3 候选完整云覆写，重新启用原稳定云覆写并重启 OpenClash；保留 TikTok-ISP-Local 本地模块。不要将真实 ISP 凭据写入云覆写或仓库。

实机测试完成前，本候选不替换稳定入口、不创建 Release 或正式标签。
