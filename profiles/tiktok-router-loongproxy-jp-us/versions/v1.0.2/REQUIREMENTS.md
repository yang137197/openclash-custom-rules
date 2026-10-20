# tiktok-router-loongproxy-jp-us v1.0.2 — 候选需求合同

状态：**candidate，待用户实机验收**。本候选继承正式稳定版 v1.0.0 的 J1–J11 与 iKuuu 日本首跳前提，只新增 J13。v1.0.1 的 Samsung J12 是另一项未验收候选，本版本不包含该规则。正式版及其文件、标签和 Release 均不变。

## 需求

J1–J11 与 [v1.0.0 正式需求合同](../v1.0.0/REQUIREMENTS.md) 相同且继续有效。

- J13：Claude Code 官方网络配置文档列出的主机名及条件性功能端点，通过 Mihomo 域名规则指向 TikTok-ISP。规则位于私网/局域网直连之后、现有 TikTok/Google/Manual-Direct/中国/美国规则之前。使用精确域名或域名后缀匹配，不按客户端进程或内网设备 IP 分流。Loongproxy 出口仍必须经用户手选的 iKuuu 日本节点建立链式代理，失败时不得改走美国普通节点、机场或 DIRECT。

### 覆盖端点

以下主机依据 [Claude Code 官方网络配置文档](https://code.claude.com/docs/en/corporate-proxy) 的 standalone CLI 网络访问表。对 Anthropic、Claude、npm、GitHub 和 Claudeusercontent 域名使用后缀规则，覆盖这些域名的根域名及其子域名。

- API、认证和连接器：anthropic.com、claude.ai、claude.com。
- 插件、安装与包管理：storage.googleapis.com、npmjs.org。
- 可选的 Chrome/Artifact 功能：claudeusercontent.com。
- GitHub 插件/市场、版本说明及相关内容：github.com、githubusercontent.com。
- 条件性或可选端点：*-review.googlesource.com、http-intake.logs.us5.datadoghq.com、browser-intake-us5-datadoghq.com、formulae.brew.sh。

这些是 Claude Code 官方列出的端点，不涵盖用户自定义 MCP 服务、插件或依赖实际访问的第三方域名，也不涵盖 AWS Bedrock、Google Cloud 或 Microsoft Foundry 等替代模型提供商的专属端点。

域名规则作用于所有经过 OpenClash 的客户端：使用 GitHub、npm 或上述其他端点的其他应用也会匹配 TikTok-ISP。它不能只识别 Claude Code 进程。

## 验收条件

- 对 Anthropic 直连账户执行一次新的 Claude Code 请求；连接记录中 api.anthropic.com 命中对应的测试域名规则并选择 TikTok-ISP。
- 登录、更新、插件或可选功能只有在实际触发时才验收；不能用未产生连接的可选域名宣称已验证。
- TikTok-ISP 使用本地 TikTok-ISP-Local，其 dialer-proxy 为 日本-入口；日本-入口手选 iKuuu 日本节点。确认实际链路成功后，才算链式路径实机验收通过。
- 私网规则仍在测试规则之前；非清单域名、Manual-Direct、国内规则、普通美国流量应保持原有行为。
- 仓库静态测试与用户路由器实测分别记录。当前未提供本候选的新调试日志；实机验收由用户执行，候选保持 pending。

## 明确边界

本测试不是整机/来源 IP 分流，不会把所有电脑流量送入 TikTok-ISP；仅清单内域名按规则走该策略组。它也不证明 Claude Code 的所有第三方扩展、MCP 或替代供应商都已覆盖。
