# tiktok-router-loongproxy-jp-us v1.0.7

**正式版（stable）**。用户于 2026-10-28 确认 v1.0.7 验收通过。本版本将手动直连规则统一为可编辑源并自动同步到滚动远程覆写；不改变原有规则优先级、出口、DNS、代理链路或 OpenClash 插件设置。

## 适用规则与维护方式

- 继承 v1.0.6 已验收需求；Loongproxy 美国 SOCKS5 仍须通过用户手选的 iKuuu 日本节点作为首跳，缺少该链路时失败关闭。
- 唯一手动直连源为 `rules/manual-direct.yaml`。保留 YAML/列表、`DOMAIN`/`DOMAIN-SUFFIX` 及域名格式校验，也校验滚动 inline payload 与源文件逐项一致；规则清单和条数不固定，允许随时新增、修改或删除任意数量的有效规则，重复项保留。
- GitHub Actions 校验源并生成滚动模块及 catalog SHA-256。工作流成功后，路由器继续使用同一个远程覆写地址，点击更新并重启 OpenClash。日常规则数据变更不创建新版本或 Release。
- 环境元数据复用 v1.0.6 已验收记录；用户确认 v1.0.7 验收通过。本版本未提供新的调试日志。详见 [部署设置](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.7/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.7/SETUP.md)、[需求合同](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.7/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.7/REQUIREMENTS.md) 和 [环境记录](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.7/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.7/ENVIRONMENT.json)。原始调试日志不随版本发布。

## 固定完整覆写

在 OpenClash 远程覆写模块中使用：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.7/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.7/openclash-overwrite.conf

模块 SHA-256：`78c96ecb06b55cebb683564a2566ca0471ad9a526aba9b34b168eef607560e3f`

此标签固定地址不会随 `main` 修改。日常手动规则维护请继续使用下方滚动地址。

## 同一滚动远程覆写地址

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf

源文件提交到 `main` 后，先等 `Sync manual direct rules` 工作流成功并确认生成文件已提交；然后在 OpenClash 中更新远程覆写并重启。失败时不要把未同步的源提交当成已部署。

## 唯一本地节点模板

[下载 tiktok-router-loongproxy-jp-us-v1.0.7-local-module.conf](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.7/tiktok-router-loongproxy-jp-us-v1.0.7-local-module.conf)

附件 SHA-256：`d7639bd7ac733c2312103bcb8e73764b2b354b3ccb7bcb578f7ee5d3706da522`

按服务商提供的 SOCKS5 信息填写模板中的 `FILL_ME_PROXY_HOST`、`FILL_ME_PROXY_PORT`、`FILL_ME_USERNAME` 和 `FILL_ME_PASSWORD`。保留节点名 `TikTok-ISP-Local`、`type: socks5`、`udp: false` 和 `dialer-proxy: 日本-入口`。示例地址 `203.0.113.10`、端口 `20000`、用户名 `demo_user`、密码 `demo_password` 均为虚构值。

真实凭据只填写在路由器的本地模块中，不要提交或公开已填写文件。OpenClash 设置、模块顺序和回退步骤见上方 `SETUP.md`。
