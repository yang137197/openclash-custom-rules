# tiktok-router-loongproxy-jp-us v1.0.0 — 需求合同

状态：**candidate**，尚未完成 CatWrt/OpenClash 实机验收。

- J1 中国大陆已知域名及大陆 IP 直连；Geo 数据库不能保证覆盖全球所有大陆域名。
- J2 私网、局域网优先 DIRECT。
- J3 TikTok 唯一出口为美国 Loongproxy SOCKS5 本地节点 `TikTok-ISP-Local`，该节点必须 `dialer-proxy: 日本-入口`；日本组手动选择 PC 上已成功的同一 iKuu 日本节点。组按名称筛选，不证明供应商身份或节点可达；日本组为空时 REJECT。
- J4 TikTok 不得回退到美国组、DIRECT 或其他节点；紧跟同范围 REJECT 阻止不支持 UDP 时继续匹配。
- J5 Google 与 Google Play 在 CN 规则前走美国组。
- J6 保留全部 129 条 Manual-Direct 原始条目，统一 DOMAIN-SUFFIX，覆盖域名本身和子域名；现有重复项仍保留。
- J7 其他国外流量使用手选美国组；组排除 `TikTok-ISP-Local` 避免递归。
- J8 云覆写内嵌 type:inline 的 Manual-Direct；用户仅刷新一个云覆写获取本仓库全部最新规则，重启 OpenClash 生效；GEO 数据仍独立维护。
- J9 凭据及真实私有代理地址只存用户授权的仓库外本机交付文件和路由器本地模块，不上传 Git/GitHub。
- J10 云覆写及本地模块仅 [YAML]；OpenClash LuCI 选项只能由用户手工设置，不自动写 UCI。
- J11 手机通过路由器验收 TikTok 美国 ISP 链路、Google/Play 美国组、国内直连及失败关闭。缺本地节点/缺日本入口时由空组 REJECT；ISP 连接失败时连接报错，不承诺命中下一条 REJECT；不支持的 TikTok UDP 才继续匹配紧随的 REJECT。三种情况均不得回退美国或 DIRECT。PC 测试不能替代实机验收。
- J12 保留全部已发布版本；新方案保持 candidate，不自行移动兼容入口或发布稳定标签。

规则顺序：私网 → TikTok ISP → TikTok REJECT → Google/Play → Manual-Direct → 中国大陆 GEO → 美国 MATCH。

2026-10-16 接续审查：保持 candidate，仅修复本候选 YAML 拼接/重复块、补齐三个组的结构校验和部署说明（J3/J4/J6/J8–J12），不改历史版本、稳定入口或两份人工直连源。用户报告目标环境为 OpenClash v0.48.002 / alpha-gbc76c13；尚无该路由器本轮加载和手机验收证据。

## 已完成验证（2026-10-16）

- 原 PR head `18ad980de731bcb4953d1b826f410df444a832d4` 的 YAML 拼接损坏可通过旧文本校验；新增严格解析能拒绝原文件及重复 YAML 键。修复后全部 22 个覆写/模板、规则源、3 项解析回归测试通过。
- 修复后完整云模块与滚动模块一致，SHA256 为 `c40a1834f843ccaf6295dfb2d5de24ab34c5fc673ac8d180797dcf6aa0d22b30`；inline 内容与原 129 条 ISP 规则逐条一致。
- 本机官方 Mihomo Meta v1.19.32 Windows amd64 隔离夹具：节点齐全、缺 ISP、缺日本节点、缺美国节点四种配置均通过 `-t`；运行 API 确认三个组成员与空组 REJECT，发入的 TikTok UDP/444 均被拒绝，没有落到美国/DIRECT。
- 夹具使用回环假节点和本地 GEO 文件，按文档模拟本候选所用 YAML 操作符，验证保留 DNS 监听配置并清除旧 fallback/policy；未执行 OpenClash Ruby 合并、防火墙或真实机场/ISP 连接。不等同于 alpha-gbc76c13 实机兼容或手机验收。

待完成：目标路由器加载、同一 iKuu 日本节点的真实链路、TikTok 播放与 ISP 出口证据、Google Play 下载、国内/人工直连及实机失败关闭。任一项未确认，均不得写稳定验收通过。
