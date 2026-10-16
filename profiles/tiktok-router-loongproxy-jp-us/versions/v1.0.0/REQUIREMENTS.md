# tiktok-router-loongproxy-jp-us v1.0.0 — 需求合同

状态：**candidate**，尚未完成 CatWrt/OpenClash 实机验收。

- J1 中国大陆已知域名及大陆 IP 直连；Geo 数据库不能保证覆盖全球所有大陆域名。
- J2 私网、局域网优先 DIRECT。
- J3 TikTok 唯一出口为美国 Loongproxy SOCKS5 本地节点 `TikTok-ISP-Local`，该节点必须 `dialer-proxy: 日本-入口`；日本组手动选择 iKuu 日本机场。
- J4 TikTok 不得回退到美国组、DIRECT 或其他节点；紧跟同范围 REJECT 阻止不支持 UDP 时继续匹配。
- J5 Google 与 Google Play 在 CN 规则前走美国组。
- J6 保留全部 129 条 Manual-Direct 原始条目，统一 DOMAIN-SUFFIX，覆盖域名本身和子域名；现有重复项仍保留。
- J7 其他国外流量使用手选美国组；组排除 `TikTok-ISP-Local` 避免递归。
- J8 云覆写内嵌 type:inline 的 Manual-Direct；用户仅刷新一个云覆写获取本仓库全部最新规则，重启 OpenClash 生效；GEO 数据仍独立维护。
- J9 凭据及真实私有代理地址仅存路由器本地模块，不上传仓库。
- J10 云覆写及本地模块仅 [YAML]；OpenClash LuCI 选项只能由用户手工设置，不自动写 UCI。
- J11 手机通过路由器验收 TikTok 美国 ISP 出口、Google/Play 美国组、国内直连及断开 ISP 时 REJECT；PC 测试不能替代实机验收。
- J12 保留全部已发布版本；新方案保持 candidate，不自行移动兼容入口或发布稳定标签。

规则顺序：私网 → TikTok ISP → TikTok REJECT → Google/Play → Manual-Direct → 中国大陆 GEO → 美国 MATCH。
