# tiktok-router-loongproxy-jp-us

**v1.0.4 stable**：用户于 2026-10-22 确认实机验收通过。Claude Code 与 Claude 网页的 Anthropic/Claude 第一方域名保持走 TikTok-ISP；GitHub 网站、内容下载和静态资源域名走美国组。GitHub 策略命中已确认，但没有可复核的性能改善指标，本版本不宣称延迟或下载速度已恢复。

Loongproxy 美国 SOCKS5 必须经用户手选的 iKuuu 日本节点作为链式第一跳。TikTok 与 Claude/Anthropic 相关请求使用 `TikTok-ISP-Local` 静态 ISP 出口；链路缺失时失败关闭，不回退普通机场或 DIRECT。保留 129 条 Manual-Direct、Google/Play 美国分流、中国大陆直连及其余境外美国分流。v1.0.4 不包含未验收的 v1.0.1 Samsung 规则。

## 当前正式版

- [v1.0.4 GitHub Release](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-v1.0.4)
- [v1.0.4 正式需求与验收范围](versions/v1.0.4/REQUIREMENTS.md)
- [v1.0.4 部署、设置与验收说明](versions/v1.0.4/SETUP.md)
- [v1.0.4 OpenClash 环境记录](versions/v1.0.4/ENVIRONMENT.json)
- [v1.0.4 唯一本地节点占位模板](versions/v1.0.4/local-tiktok-proxy.conf.example)
- [v1.0.4 固定完整云覆写](versions/v1.0.4/openclash-overwrite.conf)

正式 Release 提供标签固定覆写链接和唯一 `.example` 本地模块附件；字段填写映射和虚构示例见 Release 正文。真实 ISP 凭据只保存在路由器本地模块。用户侧更新仓库规则只需刷新云覆写模块并重启 OpenClash；启用顺序为云覆写在上、本地 TikTok-ISP 模块在下。

固定版本完整覆写订阅链接：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.4/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.4/openclash-overwrite.conf

滚动云覆写链接（随 `main` 更新）：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

## 未验收候选（candidate）

- **v1.0.1**：仅增加 `update.kies.samsung.com` 精确域名直连，未验收且不属于当前正式版。
- **v1.0.2**：Claude Code 官方端点分流的早期候选。
- **v1.0.3**：Claude 网页 Anthropic/Claude 第一方域名分流候选。

正式版本号按本方案递增；已发布目录、标签和 Release 不得改写。仓库级流程见 [`DEVELOPMENT_RULES.md`](../../DEVELOPMENT_RULES.md)。
