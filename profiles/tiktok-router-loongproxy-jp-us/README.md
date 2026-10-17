# tiktok-router-loongproxy-jp-us

**v1.0.0 stable**：TikTok 必须使用 iKuuu 日本节点作为 Loongproxy 美国 SOCKS5 的链式第一跳。用户于 2026-10-16 确认实机验收通过并授权正式发布。

**v1.0.1 candidate**：新增 `update.kies.samsung.com` 精确域名直连规则，尚待路由器验收；稳定入口仍是 v1.0.0。

- [v1.0.1 候选覆写](versions/v1.0.1/openclash-overwrite.conf)
- [v1.0.1 候选需求与验收条件](versions/v1.0.1/REQUIREMENTS.md)
- [v1.0.1 候选部署与设置](versions/v1.0.1/SETUP.md)

- [部署、验收及本地 ISP 密码修改](versions/v1.0.0/SETUP.md)
- [J1–J11 正式需求合同](versions/v1.0.0/REQUIREMENTS.md)
- [固定版本完整覆写](versions/v1.0.0/openclash-overwrite.conf)
- [滚动云覆写](overwrite/openclash-overwrite.conf)
- [下载唯一的本地节点占位模板](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.0/tiktok-router-loongproxy-jp-us-v1.0.0-local-module.conf.example)；字段对应和虚构填写示例见 [v1.0.0 Release 正文](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-v1.0.0)。填入真实凭据后只保存在路由器本地。

正式云覆写订阅链接：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

固定使用 v1.0.0 时，Release 正文与下方地址提供相同的标签固定覆写订阅链接；它不会随 `main` 更新：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/openclash-overwrite.conf

日本组按名称自动纳入已加载节点，但实际使用时必须手选 iKuuu 的日本节点。缺少匹配的日本节点时保持 REJECT，不得改用其他首跳或添加机场/DIRECT 回退。真实 ISP 地址和凭据只配置在路由器本地模块。
