# tiktok-router-loongproxy-jp-us v1.0.0 — 正式需求合同

状态：**stable**。用户于 2026-10-16 确认 CatWrt/OpenClash 实机验收通过并授权正式发布；目标环境由用户报告为 OpenClash v0.48.002 / alpha-gbc76c13。验收按用户总体确认记录，不虚构逐项测试日志。

## 不可变链路前提

**TikTok 的 Loongproxy 美国 SOCKS5 出口必须通过用户手选的 iKuuu 日本节点建立链式代理。** iKuuu 日本节点是首跳，不是可选偏好。不得换用美国首跳或其他机场节点，不得回退普通机场、DIRECT 或其他节点。若没有可用 iKuuu 日本节点，链路必须失败关闭。

## 需求

- J1：中国大陆已知域名及大陆 IP 直连；Geo 数据库不能保证覆盖全球所有大陆域名。
- J2：私网、局域网优先 DIRECT。
- J3：TikTok 唯一出口为路由器本地 Loongproxy SOCKS5 节点 `TikTok-ISP-Local`，并强制 `dialer-proxy: 日本-入口`。用户必须在日本组中手选实际 iKuuu 日本节点。组按名称自动筛选：已加载 proxies/proxy-providers 中名称任意位置含 `jp`、`日本`、`Japan` 或 🇯🇵，忽略大小写。名称匹配不证明供应商身份或节点可达；日本组为空时 REJECT。
- J4：TikTok 不得回退到美国组、普通机场、DIRECT 或其他节点；紧邻同范围 `GEOSITE,tiktok,REJECT` 阻止不支持 UDP 时继续匹配。
- J5：Google 与 Google Play 在中国规则前走美国组。
- J6：保留原始 129 条 Manual-Direct；各条改为 `DOMAIN-SUFFIX`，覆盖域名本身与其子域名，同时保留既有重复项。
- J7：其他境外流量使用用户手选的美国组；该组排除 `TikTok-ISP-Local`，避免链式拨号递归。
- J8：云覆写内嵌 `type: inline` 的 Manual-Direct；用户只刷新一个云覆写模块并重启 OpenClash 即可更新本仓库规则。机场节点订阅和 GEO 数据仍各自更新。
- J9：真实 ISP 地址、账号和密码只保存在路由器本地模块，不进入 Git、云覆写或公开日志。
- J10：云覆写及本地模块只含 `[YAML]`；OpenClash LuCI 插件选项由用户手工设置，不自动写 UCI。
- J11：用户确认目标 OpenClash 实机验收通过。未单独提供的逐项日志和指标不作独立确认或补造。静态校验不替代实机验收。

## 规则优先级

私网/局域网 → TikTok ISP → 紧邻 TikTok REJECT → Google/Play → Manual-Direct → 中国大陆域名/IP → 美国 MATCH。

**稳定版约束：**该版本目录、发布提交和标签不可改写、移动或覆盖。行为变更须新建候选版本及独立 URL；新的实机验收和发布须另行授权。
