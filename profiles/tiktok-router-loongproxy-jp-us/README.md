# tiktok-router-loongproxy-jp-us

**v1.0.6 stable**：新增 `DOMAIN-SUFFIX,huzhou.host,DIRECT`，覆盖 `huzhou.host` 主域名及全部子域名。用户于 2026-10-28 确认候选验收通过；当天调试日志显示主域名连接命中 DIRECT。日志未记录子域名连接，子域名验收依据为用户确认。

Loongproxy 美国 SOCKS5 必须经用户手选的 iKuuu 日本节点作为链式第一跳。TikTok 与 Claude/Anthropic 相关请求使用 `TikTok-ISP-Local` 静态 ISP 出口；链路缺失时失败关闭，不回退普通机场或 DIRECT。保留 129 条原始 Manual-Direct 规则、Google/Play 美国分流、中国大陆直连及其余境外美国分流。v1.0.6 不改变其他出口、DNS 或插件设置。

## 当前正式版

- [v1.0.6 GitHub Release](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-v1.0.6)
- [v1.0.6 正式需求与验收范围](versions/v1.0.6/REQUIREMENTS.md)
- [v1.0.6 部署、设置与验收说明](versions/v1.0.6/SETUP.md)
- [v1.0.6 环境记录](versions/v1.0.6/ENVIRONMENT.json)
- [v1.0.6 Release 正文](versions/v1.0.6/RELEASE_NOTES.md)
- [v1.0.6 唯一本地节点占位模板](versions/v1.0.6/local-tiktok-proxy.conf)
- [v1.0.6 固定完整云覆写](versions/v1.0.6/openclash-overwrite.conf)

真实 ISP 凭据只保存在唯一的本地 `tiktok-router-loongproxy` 模块；完整云覆写必须使用远程订阅模块。v1.0.7 候选验收并发布后，手动直连规则唯一源为根目录 `rules/manual-direct.yaml`；新增、修改或删除后，GitHub Actions 自动同步滚动模块与哈希。工作流成功后，路由器继续使用同一远程地址，点击更新并重启即可生效，无需单独更新规则 provider 或发布日常规则版本。大版本更新或重构走候选验收后发布正式版。

v1.0.6 固定版本完整覆写订阅链接：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.6/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.6/openclash-overwrite.conf

滚动云覆写链接（随 `main` 更新）：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

## 未验收候选（candidate）

- **v1.0.7**：将 `rules/manual-direct.yaml` 设为唯一可编辑手动规则源；GitHub Actions 自动同步滚动覆写及 SHA-256。候选用于验收生成模块和同步工作流，当前尚未合并或发布。

  - [候选需求合同](versions/v1.0.7/REQUIREMENTS.md)
  - [候选部署、设置与验收说明](versions/v1.0.7/SETUP.md)
  - [候选环境记录](versions/v1.0.7/ENVIRONMENT.json)
  - 候选远程完整覆写：

    https://raw.githubusercontent.com/yang137197/openclash-custom-rules/codex/manual-direct-source-generator-v1-0-7/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.7/openclash-overwrite.conf
- **v1.0.1**：仅增加 `update.kies.samsung.com` 精确域名直连，未验收且不属于当前正式版。
- **v1.0.2**：Claude Code 官方端点分流的早期候选。
- **v1.0.3**：Claude 网页 Anthropic/Claude 第一方域名分流候选。

正式版本号按本方案递增；已发布目录、标签和 Release 不得改写。仓库级流程见 [`DEVELOPMENT_RULES.md`](../../DEVELOPMENT_RULES.md)。
