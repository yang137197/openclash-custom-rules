# tiktok-router-loongproxy-jp-us v1.0.3 — 候选需求合同

状态：**candidate，待用户实机验收**。本候选继承正式稳定版 v1.0.0 的 J1–J11 与 iKuuu 日本首跳前提，并包含 J13、J14。v1.0.1 的 Samsung J12 是另一项未验收候选，本版本不包含该规则。正式版及其文件、标签和 Release 均不变。

## 需求

J1–J11 与 [v1.0.0 正式需求合同](../v1.0.0/REQUIREMENTS.md) 相同且继续有效。

- J13：Claude Code 官方网络配置文档列出的主机名及条件性功能端点，通过 Mihomo 域名规则指向 TikTok-ISP。规则位于私网/局域网直连之后、现有 TikTok/Google/Manual-Direct/中国/美国规则之前。使用精确域名或域名后缀匹配，不按客户端进程或内网设备 IP 分流。Loongproxy 出口仍必须经用户手选的 iKuuu 日本节点建立链式代理，失败时不得改走美国普通节点、机场或 DIRECT。
- J14：Claude 网页中 Anthropic/Claude 第一方服务及内容域名尽量统一命中 TikTok-ISP，保持同一 `TikTok-ISP-Local` 静态 ISP 出口和 iKuuu 日本首跳。至少覆盖 `anthropic.com`、`claude.ai`、`claude.com`、`claudeusercontent.com`、`claudemcpcontent.com` 的根域名及全部子域名。不得把这些第一方域名拆到美国或其他策略组；不改变 Loongproxy→iKuuu 日本链路及失败关闭行为。

### 覆盖域名

以下域名依据 [Anthropic 官方网络配置文档](https://code.claude.com/docs/en/network-config)，包括 Claude Code 网络访问表及 `Desktop and claude.ai` 一节。后缀规则覆盖域名本身和全部子域名。

- Claude API、认证、连接器、网页 CDN：anthropic.com、claude.ai、claude.com。
- 插件、安装与包管理：storage.googleapis.com、npmjs.org。
- Chrome 扩展桥接、Artifact 内容及网页 MCP 交互组件：claudeusercontent.com、claudemcpcontent.com。
- GitHub 插件/市场、版本说明及相关内容：github.com、githubusercontent.com。
- 条件性或可选端点：*-review.googlesource.com、http-intake.logs.us5.datadoghq.com、browser-intake-us5-datadoghq.com、formulae.brew.sh。

Anthropic 文档还列出可选的第三方字体和 JavaScript CDN。它们是多个网站共享的第三方域名，不属于 Anthropic 第一方域名，因此本候选不把它们整体改道；用户自定义 MCP、插件或依赖实际访问的其他第三方域名也不在本域名合同内。AWS Bedrock、Google Cloud 或 Microsoft Foundry 等替代模型提供商使用的专属端点同样不在范围内。

规则对所有经过 OpenClash 的客户端生效：访问同一服务域名的其他应用也会走 TikTok-ISP；域名规则不能识别 Claude 浏览器标签页或 Claude Code 进程。路由器规则只能让这些连接使用同一策略组和本地链路；是否始终由服务商分配同一个公网 IP，仍需由用户从外部核验，不能仅凭规则命中证明。

## 验收条件

- 打开 Claude 网页并实际登录、发送一条消息；检查当次实际出现的 Anthropic/Claude 第一方连接（例如 `claude.ai`、`assets.claude.ai`、`assets-proxy.anthropic.com`、`s-cdn.anthropic.com`）均命中 TikTok-ISP。交互式 MCP 组件等可选请求只有在实际触发时才验收。
- 若同时验证 Claude Code，执行一条新请求；`api.anthropic.com` 等实际出现的官方端点应命中 TikTok-ISP。登录、更新、插件等仅在触发时验收。
- TikTok-ISP 使用本地 TikTok-ISP-Local，其 dialer-proxy 为 日本-入口；日本-入口手选 iKuuu 日本节点。确认实际链路成功后，才算链式路径实机验收通过。
- 用外部 IP 检测或 ISP 提供方信息核对实际出口；策略组命中只证明规则选择，不单独证明公网 IP 恒定。
- 私网规则仍在测试规则之前；非清单域名、Manual-Direct、国内规则、普通美国流量应保持原有行为。
- 仓库静态测试与用户路由器实测分别记录。v1.0.3 尚未加载到路由器；实机验收由用户执行，候选保持 pending。

## 明确边界

本测试不是整机/来源 IP 分流，不会把所有电脑流量送入 TikTok-ISP；仅清单内域名按规则走该策略组。它不覆盖共享第三方 CDN、自定义 MCP/插件域名或替代供应商的端点，也不承诺 ISP 服务商永不更换其公网出口 IP。
