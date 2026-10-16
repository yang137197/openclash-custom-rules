# tiktok-router-loongproxy-jp-us

**v1.0.0 candidate**：iKuu 日本第一跳 → 路由器本地 Loongproxy 美国 SOCKS5 → TikTok；CN/Manual-Direct 直连，Google/Play 和其他境外流量走用户手选美国组。

- [需求合同](versions/v1.0.0/REQUIREMENTS.md)
- [部署与验收](versions/v1.0.0/SETUP.md)
- [候选完整覆写](versions/v1.0.0/openclash-overwrite.conf)
- [滚动云覆写](overwrite/openclash-overwrite.conf)
- [本地节点模板（不含凭据）](versions/v1.0.0/local-tiktok-proxy.conf.example)

仅为开发候选，未完成路由器实机验收。当前文件树已按授权清除退役方案及根兼容入口；历史 Git 提交、标签和 Release 保留。日本组自动筛选名称含 `jp`、`日本`、`Japan` 或 🇯🇵 的已加载节点，不区分大小写，实际首跳仍由用户手选。
