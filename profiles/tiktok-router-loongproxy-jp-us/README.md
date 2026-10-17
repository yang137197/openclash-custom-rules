# tiktok-router-loongproxy-jp-us

**v1.0.0 stable**：TikTok 必须使用 iKuuu 日本节点作为 Loongproxy 美国 SOCKS5 的链式第一跳。用户于 2026-10-16 确认实机验收通过并授权正式发布。

- [部署、验收及本地 ISP 密码修改](versions/v1.0.0/SETUP.md)
- [J1–J11 正式需求合同](versions/v1.0.0/REQUIREMENTS.md)
- [固定版本完整覆写](versions/v1.0.0/openclash-overwrite.conf)
- [滚动云覆写](overwrite/openclash-overwrite.conf)
- [本地节点占位模板（不含凭据）](versions/v1.0.0/local-tiktok-proxy.conf.example)
- [v1.0.0 Release 独立下载本地节点模板](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.0/tiktok-router-loongproxy-jp-us-v1.0.0-local-module.conf.example)；填写字段和保留项见[标签固定部署说明](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/SETUP.md)。真实凭据只填写到路由器本地副本。

正式云覆写订阅链接：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

固定使用 v1.0.0 时，请使用对应的 [GitHub Release](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-v1.0.0) 和[标签固定覆写链接](https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/openclash-overwrite.conf)。Release 标签中的文件不会随 `main` 更新。

日本组按名称自动纳入已加载节点，但实际使用时必须手选 iKuuu 的日本节点。缺少匹配的日本节点时保持 REJECT，不得改用其他首跳或添加机场/DIRECT 回退。真实 ISP 地址和凭据只配置在路由器本地模块。
