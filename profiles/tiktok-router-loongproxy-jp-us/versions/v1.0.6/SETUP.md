# tiktok-router-loongproxy-jp-us v1.0.6 — 候选部署与验收

**状态：candidate，待路由器实机验收。** 本候选只增加 `huzhou.host` 主域名及所有子域名的 DIRECT 规则；其他运行规则和插件设置继承 v1.0.5。此候选不是正式版，也不会更改 GitHub `main` 上现有稳定滚动覆写。

## 候选远程覆写链接

在 OpenClash 远程覆写模块中使用此候选地址：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/codex/huzhou-host-direct-v1-0-6/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.6/openclash-overwrite.conf

本候选完整云覆写使用远程模块；唯一的本地覆写模块仍为 `tiktok-router-loongproxy`，真实 ISP 凭据继续只留在路由器本地。不要把候选完整云覆写保存为第二个本地模块。

## 应用和检查

在 OpenClash 运行状态页的「覆写模块」窗口，将完整云覆写远程模块更新到上方候选地址，然后重启 OpenClash。保持配套本地节点模块及原有手选出口不变。

重启后检查连接记录：

- `huzhou.host` 应命中 DIRECT。
- 任一实际使用的子域名（如 `www.huzhou.host`）应命中 DIRECT。
- `not-huzhou.host` 等相似但不是该后缀的域名不应由此规则命中。
- 原有 GitHub、TikTok、Google 和普通中国大陆规则继续按 v1.0.5 行为处理。

候选静态检查通过不等于路由器已验收。请以目标路由器重启后的连接记录确认实际命中；若未命中，保留脱敏日志和连接时间，候选继续保持未验收。

## 回退

如候选导致其他异常，将完整云覆写远程地址恢复为 v1.0.5 固定地址并重启 OpenClash：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.5/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.5/openclash-overwrite.conf

本地 `tiktok-router-loongproxy` 模块与凭据不需要修改。
