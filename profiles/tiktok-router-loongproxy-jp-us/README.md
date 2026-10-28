# tiktok-router-loongproxy-jp-us

**v1.0.5 stable**：仅修正本地节点模板的扩展名为 `.conf`；完整分流云覆写与 v1.0.4 完全一致。v1.0.4 已由用户确认实机验收通过；v1.0.5 复用其环境快照，本地文件选择器本次未在路由器实测。

Loongproxy 美国 SOCKS5 必须经用户手选的 iKuuu 日本节点作为链式第一跳。TikTok 与 Claude/Anthropic 相关请求使用 `TikTok-ISP-Local` 静态 ISP 出口；链路缺失时失败关闭，不回退普通机场或 DIRECT。保留 129 条 Manual-Direct、Google/Play 美国分流、中国大陆直连及其余境外美国分流。v1.0.4 不包含未验收的 v1.0.1 Samsung 规则。

## 当前正式版

- [v1.0.5 GitHub Release](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-v1.0.5)
- [v1.0.5 正式需求与验收范围](versions/v1.0.5/REQUIREMENTS.md)
- [v1.0.5 部署、设置与验收说明](versions/v1.0.5/SETUP.md)
- [v1.0.5 环境记录](versions/v1.0.5/ENVIRONMENT.json)
- [v1.0.5 Release 正文](versions/v1.0.5/RELEASE_NOTES.md)
- [v1.0.5 唯一本地节点占位模板](versions/v1.0.5/local-tiktok-proxy.conf)
- [v1.0.5 固定完整云覆写](versions/v1.0.5/openclash-overwrite.conf)

v1.0.4 Release 的历史附件名为 `.conf.example`，使用前先将文件名改为 `.conf`。v1.0.5 Release 提供同内容、扩展名正确的 `.conf` 模板；官方指南列出 `.conf` 为支持的本地上传文件类型，但本次未在路由器文件选择器实测。真实 ISP 凭据只保存在唯一的本地 `tiktok-router-loongproxy` 模块；完整云覆写使用远程订阅模块。仅手动新增域名时，在根目录 `rules/manual-direct.yaml` 的 `payload` 末尾维护规则并同步滚动模块；路由器继续使用同一远程地址，点击更新并重启，无需正式 Release。大版本更新或重构走候选验收后发布正式版，再同步滚动模块。

v1.0.5 固定版本完整覆写订阅链接：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.5/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.5/openclash-overwrite.conf

滚动云覆写链接（随 `main` 更新）：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

## 未验收候选（candidate）

- **v1.0.6**：新增 `huzhou.host` 主域名及全部子域名 DIRECT；候选尚待路由器验收。
  - [候选部署与验收说明](versions/v1.0.6/SETUP.md)
  - 远程覆写候选链接：

    https://raw.githubusercontent.com/yang137197/openclash-custom-rules/codex/huzhou-host-direct-v1-0-6/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.6/openclash-overwrite.conf
- **v1.0.1**：仅增加 `update.kies.samsung.com` 精确域名直连，未验收且不属于当前正式版。
- **v1.0.2**：Claude Code 官方端点分流的早期候选。
- **v1.0.3**：Claude 网页 Anthropic/Claude 第一方域名分流候选。
正式版本号按本方案递增；已发布目录、标签和 Release 不得改写。仓库级流程见 [`DEVELOPMENT_RULES.md`](../../DEVELOPMENT_RULES.md)。
