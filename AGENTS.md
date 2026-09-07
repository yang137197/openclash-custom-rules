# Codex / AI 开发约定

本仓库后续维护不得依赖历史聊天上下文。

在分析、修改或提交任何 OpenClash 规则前，必须先读取：

1. `docs/CODEX-HANDOFF.md` — 当前设计、已验证结论、历史故障与决策边界
2. `README.md` — 使用方法与总体架构
3. `overwrite/openclash-overwrite.conf` — 实际主覆写
4. `rules/manual-direct.yaml` — 当前额外直连规则
5. `docs/acceptance-log.md` — 验收要求
6. `CHANGELOG.md` — 历史变更

维护原则：

- 先根据实际日志定位，再做最小修改。
- 不要因为偶发 `i/o timeout` 就重写 GeoSite、Fake-IP、DNS 或整套规则。
- 普通额外直连域名优先修改 `rules/manual-direct.yaml`。
- OneDrive Consumer 网页 / 文件链路当前是明确例外：由主覆写强制走 `美国`；不要重新加入 `Manual-Direct`，除非重新完成 A/B 验证。
- Microsoft Account / Windows / Store / 中国区 Microsoft 365 / Azure 的已收录系统端点保持 DIRECT。
- 不使用 `DOMAIN-SUFFIX,microsoft.com`、`DOMAIN-SUFFIX,live.com`、`DOMAIN-SUFFIX,windows.net` 这类过宽规则。
- 不整体覆盖 OpenClash 自动生成的 `rule-providers`，避免再次破坏 `oc-cn-domain`。
- 保持 RFC1918 私网显式 DIRECT。
- `美国` 策略组保持手工 `select`，除非需求明确改变。
- TikTok 固定走 `TikTok-ISP`；该组只收集本地模块注入的 `IPRoyal-US-ISP`，不得回落到机场节点。
- IPRoyal 服务器、端口、用户名和密码只保存在 OpenClash 本地模块，禁止提交到本仓库。
- 修改后按 `docs/CODEX-HANDOFF.md` 的验收清单验证。
- 任何新的关键设计决定、已验证故障结论或例外规则，必须同步更新 `docs/CODEX-HANDOFF.md` 和必要的 `CHANGELOG.md`。

如果文档与当前实际运行配置或可复现日志冲突，以最新实际配置和可复现证据为准，并在本次提交中同步修正文档。
