# 版本记录

## tiktok-router-loongproxy-jp-us v1.0.5 — 2026-10-24

- 状态：stable，用户明确授权正式发布。仅将本地 SOCKS5 模板附件改为 OpenClash 本地上传器支持的 `.conf` 扩展名；模板正文和云覆写与 v1.0.4 一致，不改变分流、凭据字段或首跳链路。
- 环境记录复用已验收的 v1.0.4 快照；路由器本地文件选择器本次未实测，不声称该项实机验收通过。v1.0.4 Release 附件、标签和目录保持不变，旧附件 `.conf.example` 使用前可改名为 `.conf`。
- 发布唯一 `.conf` 占位模板并在 Release 正文说明字段映射和虚构填写示例；真实 ISP 凭据仍只保存在路由器本地。

## tiktok-router-loongproxy-jp-us v1.0.4 — 2026-10-22

- 状态：stable。用户于 2026-10-22 确认实机验收通过；调试日志环境信息、活动配置标识、设置基线及用户确认的模块顺序已记入 `ENVIRONMENT.json`，原始日志未入仓。
- 新增 J15：Claude/Anthropic 第一方域名继续走 TikTok-ISP；`github.com`、`githubusercontent.com` 与 `githubassets.com` 改走美国组，避免 GitHub 下载经过受限带宽 ISP。保持 iKuuu 日本首跳、失败关闭和 129 条 Manual-Direct；v1.0.0 发布快照不改写。
- 验收记录不包含可复核的时延/下载速度指标；本版本不宣称 GitHub 延迟或无线端加载已恢复。

## tiktok-router-loongproxy-jp-us v1.0.3 — 2026-10-20

- 状态：candidate，等待用户实机验证。沿用 v1.0.2 的 Claude Code 官方端点规则，并新增 J14：Claude 网页相关 Anthropic/Claude 第一方域名后缀统一走 TikTok-ISP；补齐官方文档中的 `claudemcpcontent.com` 交互组件域名。
- 保持 iKuuu 日本首跳与 Loongproxy 美国静态 ISP 链路；共享第三方 CDN 不整体改道，规则命中不作为公网出口 IP 恒定的证明。v1.0.0 稳定版和 v1.0.1/v1.0.2 候选快照不改写。
- 依据：[Anthropic 官方网络配置文档](https://code.claude.com/docs/en/network-config)，包括 Claude Code 网络访问表及 Claude Desktop/网页端点说明。

## tiktok-router-loongproxy-jp-us v1.0.2 — 2026-10-20

- 状态：candidate，等待用户实机验证。新增 J13：Claude Code 官方文档列出的端点域名按规则走 TikTok-ISP，测试链接位于候选分支。该测试按域名作用于所有客户端；不修改稳定 v1.0.0、滚动入口、ISP 凭据或本地模块；不包含仍待验收的 v1.0.1 Samsung J12。官方来源：https://code.claude.com/docs/en/corporate-proxy。

## tiktok-router-loongproxy-jp-us v1.0.1 — 2026-10-17

状态：candidate；影响 J12。用户提供的连接日志显示 `update.kies.samsung.com` 命中 `MATCH → 美国`，候选尚未实机验收。

- 新增精确规则 `DOMAIN,update.kies.samsung.com,DIRECT`，范围仅限该完整主机名。
- 保持 v1.0.0 发布快照、129 条 Manual-Direct、其他分流和 iKuuu 日本首跳链路不变。

## Release 固定覆写链接展示 — 2026-10-17

- 在 v1.0.0 Release 正文单独展示完整、标签固定的覆写订阅 URL，并保留模块 SHA-256。
- 在根 README、方案 README、Release 模板及开发规则中统一固定地址的展示要求；滚动 `main` 地址与固定版本地址分别说明。

## v1.0.0 Release 排版与模板说明 — 2026-10-17

- 修正 GitHub Release 正文的 Markdown 标题、段落和列表换行，恢复清晰的字体层级和排版。
- Release 只保留一个与标签文件一致的本地模块模板；字段对应和虚构填写示例直接写在正文，不另附注释模板或独立填写指南。
- 保留 v1.0.0 标签源码和原始模板附件逐字节不变，删除此前新增的辅助文件与 Release 附件。

## 仓库开发流程 — 2026-10-17

- 新增跨工具开发规则和统一接续提示词；用户需求、已接受建议、候选状态和验收证据必须能从仓库读取。
- 明确不同方案独立维护 SemVer、固定覆写链接和 Release；根 README 作为方案总览目录。
- 新增候选需求收集单、环境记录和 Release 说明模板；行为变更的 stable 发布必须具备对应调试日志来源、准确环境版本及实机验收确认，原始日志不得提交。
- 明确需要本地节点模块的正式 Release 必须提供独立下载的占位模板、附件 SHA-256 和标签固定填写说明；自动源码归档不能替代模板附件。本次按用户要求为 v1.0.0 Release 补充模板附件。
- 扩展版本校验器，允许多个独立 profile 和仅有候选版的新方案，并逐方案检查版本递增、环境记录、环境复用来源、固定 Release 链接及原始调试日志误提交。日志检查只针对 Git 跟踪或未忽略的待提交文件；首个正式版 v1.0.0 保持不可变，作为没有环境清单的历史基线。

## tiktok-router-loongproxy-jp-us v1.0.0 — 2026-10-16

状态：stable。用户确认 CatWrt/OpenClash 实机验收通过并授权正式发布。影响 J3/J4/J6/J8–J11；按用户总体确认记录验收，不补造逐项日志。

- 正式链路前提：TikTok 的 Loongproxy 美国 SOCKS5 必须经用户手选的 iKuuu 日本节点建立链式代理；不得改成美国或其他机场首跳，不得回退机场/DIRECT。
- 日本组自动纳入已加载的顶层节点与代理提供商中名称含 `jp`、`日本`、`Japan` 或 🇯🇵 的节点；实际首跳手选，缺节点时 REJECT。
- 稳定入口切换为 main 上的本方案；唯一当前维护方案为日本首跳链路。移除未发布的美国首跳 Loongproxy 候选，避免与强制链路前提冲突。
- 保留全部 129 条原始人工规则及 DOMAIN-SUFFIX 副本；云模块 inline 与源一致，只需刷新云模块并重启。真实 ISP 地址和凭据只放路由器本地节点模块。
- 更新正式部署文档，说明如何在本地 `TikTok-ISP-Local` 模块手动修改密码；公共仓库仅保留占位模板。
- 版本索引改为单一稳定方案，验证器覆盖 stable 状态、iKuuu 日本首跳合同、模块哈希、129 条规则、占位凭据、历史快照和本地链接。

## 仓库版本基线 — 2026-10-17

- 将 `tiktok-router-loongproxy-jp-us v1.0.0` 固定为唯一首个正式版本；此前的其他版本和 beta 版本从当前记录、Git 标签与 GitHub Releases 清理，Git 提交历史保留。
- 后续版本号必须严格递增，并在对应版本记录中写入具体更新内容。保留本正式版的 OpenClash 设置建议、专家角色和官方指南入口。
