# tiktok-router-isp-us

**当前候选：v1.0.0 / candidate。** 方案采用一份完整云覆写和一份路由器本地 TikTok SOCKS5 节点模块：其他境外流量走用户手选机场`美国`；TikTok 只走 `TikTok-ISP-Local`，该节点经`美国`组链式拨号。TikTok 不回退机场或直连。

- [滚动完整覆写](overwrite/openclash-overwrite.conf)
- [v1.0.0 固定候选覆写](versions/v1.0.0/openclash-overwrite.conf)
- [本地节点无凭据模板](versions/v1.0.0/local-tiktok-proxy.conf.example)
- [设置、手机验收与回退](versions/v1.0.0/SETUP.md)
- [C1–C11 需求合同](versions/v1.0.0/REQUIREMENTS.md)
- [候选专属人工直连清单](../../rules/manual-direct-isp.yaml)

云模块没有凭据。真实 SOCKS5 地址、端口、用户名和密码仅保存在路由器本地节点模块。仓库里的模板值为占位符，不能原样启用。

人工直连数据保留了既有 129 条域名条目，并将每项统一扩展为 `DOMAIN-SUFFIX`。这份方案专属副本不改变 `tiktok-sockstun-us` 等其他方案使用的 `rules/manual-direct.yaml`。

此版本尚未完成手机实机验收；静态校验通过不证明 ISP 链路或 TikTok 应用正常。
