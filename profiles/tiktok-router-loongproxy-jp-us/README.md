# tiktok-router-loongproxy-jp-us

**v1.0.7 stable**：用户于 2026-10-28 确认验收通过。手动直连规则集中维护于 `rules/manual-direct.yaml`，保留规则语法与同步一致性校验，不固定域名清单或条数；GitHub Actions 自动更新滚动模块，使同一远程覆写地址可持续使用。

Loongproxy 美国 SOCKS5 必须经用户手选的 iKuuu 日本节点作为链式第一跳。TikTok 与 Claude/Anthropic 相关请求使用 `TikTok-ISP-Local` 静态 ISP 出口；链路缺失时失败关闭，不回退普通机场或 DIRECT。Manual-Direct 规则在唯一源中持续维护；其余分流包括 Google/Play 美国、中国大陆直连及其他境外美国分流。

## 当前正式版

- [v1.0.7 GitHub Release](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-v1.0.7)
- [v1.0.7 正式需求与验收范围](versions/v1.0.7/REQUIREMENTS.md)
- [v1.0.7 部署、设置与验收说明](versions/v1.0.7/SETUP.md)
- [v1.0.7 环境记录](versions/v1.0.7/ENVIRONMENT.json)
- [v1.0.7 Release 正文](versions/v1.0.7/RELEASE_NOTES.md)
- [v1.0.7 唯一本地节点占位模板](versions/v1.0.7/local-tiktok-proxy.conf)
- [v1.0.7 固定完整云覆写](versions/v1.0.7/openclash-overwrite.conf)

真实 ISP 凭据只保存在唯一的本地 `tiktok-router-loongproxy` 模块；完整云覆写必须使用远程订阅模块。手动直连规则唯一源为根目录 `rules/manual-direct.yaml`；保留语法和同步校验，规则可随时增删，不固定清单或条数。提交后由 GitHub Actions 更新滚动模块与哈希。工作流成功后，路由器继续使用同一远程地址，点击更新并重启即可生效，无需单独更新规则 provider 或发布日常规则版本。大版本更新或重构走候选验收后发布正式版。

v1.0.7 固定完整云覆写：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.7/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.7/openclash-overwrite.conf

v1.0.6 固定版本完整覆写订阅链接：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.6/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.6/openclash-overwrite.conf

滚动云覆写链接（随 `main` 更新）：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

## 历史版本

- v1.0.6：新增 `huzhou.host` 主域名及全部子域名直连；保留既有 Huzhou 验收记录与固定版本快照。
- **v1.0.1 candidate**：仅增加 `update.kies.samsung.com` 精确域名直连，历史未验收。
- **v1.0.2 candidate**：增加 Claude Code 官方端点，历史未验收。
- **v1.0.3 candidate**：统一 Claude/Anthropic 第一方域名策略，历史未验收。
- **v1.0.2**：Claude Code 官方端点分流的早期候选。
- **v1.0.3**：Claude 网页 Anthropic/Claude 第一方域名分流候选。

正式版本号按本方案递增；已发布目录、标签和 Release 不得改写。仓库级流程见 [`DEVELOPMENT_RULES.md`](../../DEVELOPMENT_RULES.md)。
