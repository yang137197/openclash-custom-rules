# tiktok-router-loongproxy-jp-us v1.0.0 — 需求合同

状态：**candidate**，尚未完成 CatWrt/OpenClash 实机验收。

- J1 中国大陆已知域名及大陆 IP 直连；Geo 数据库不能保证覆盖全球所有大陆域名。
- J2 私网、局域网优先 DIRECT。
- J3 TikTok 唯一出口为美国 Loongproxy SOCKS5 本地节点 `TikTok-ISP-Local`，该节点必须 `dialer-proxy: 日本-入口`；日本组自动纳入已加载的 proxies/proxy-providers 中名称包含 jp、日本、Japan 或 🇯🇵 的节点，忽略大小写，不要求完整节点名；实际首跳手选，优先使用 PC 上成功的节点。组按名称筛选，不证明供应商身份或节点可达；日本组为空时 REJECT。
- J4 TikTok 不得回退到美国组、DIRECT 或其他节点；紧跟同范围 REJECT 阻止不支持 UDP 时继续匹配。
- J5 Google 与 Google Play 在 CN 规则前走美国组。
- J6 保留全部 129 条 Manual-Direct 原始条目，统一 DOMAIN-SUFFIX，覆盖域名本身和子域名；现有重复项仍保留。
- J7 其他国外流量使用手选美国组；组排除 `TikTok-ISP-Local` 避免递归。
- J8 云覆写内嵌 type:inline 的 Manual-Direct；用户仅刷新一个云覆写获取本仓库全部最新规则，重启 OpenClash 生效；GEO 数据仍独立维护。
- J9 凭据及真实私有代理地址只存用户授权的仓库外本机交付文件和路由器本地模块，不上传 Git/GitHub。
- J10 云覆写及本地模块仅 [YAML]；OpenClash LuCI 选项只能由用户手工设置，不自动写 UCI。
- J11 手机通过路由器验收 TikTok 美国 ISP 链路、Google/Play 美国组、国内直连及失败关闭。缺本地节点/缺日本入口时由空组 REJECT；ISP 连接失败时连接报错，不承诺命中下一条 REJECT；不支持的 TikTok UDP 才继续匹配紧随的 REJECT。三种情况均不得回退美国或 DIRECT。PC 测试不能替代实机验收。
- J12 按 2026-10-16 用户明确授权清理退役方案的当前文件树、索引、文档、校验依赖及根兼容入口；保留 Git 历史、已有标签和 Release。清理后 currentProfile=null，新方案保持 candidate，不自动晋升或发布稳定标签。

规则顺序：私网 → TikTok ISP → TikTok REJECT → Google/Play → Manual-Direct → 中国大陆 GEO → 美国 MATCH。

2026-10-16 接续审查：修复候选 YAML 拼接/重复块，补齐空组保护；本轮按授权自动纳入日本节点并清理退役方案。两份人工直连源未改。用户报告目标环境为 OpenClash v0.48.002 / alpha-gbc76c13；当前截图只显示日本组 REJECT，未提供运行配置，不能确定是节点未加载还是筛选未生效。

## 验证记录与限制

- 原 PR head `18ad980de731bcb4953d1b826f410df444a832d4` 的损坏 YAML 曾通过旧文本检查；严格解析已补齐，并验证拒绝损坏文件和重复键。
- 保留的两个候选共 6 个覆写/模板均须严格解析；完整云模块、滚动模块与 catalog 哈希一致，inline 逐条等于 129 条后缀规则源。
- 本机官方 Mihomo Meta v1.19.32 Windows amd64 隔离夹具验证六种配置：节点齐全、仅 provider 日本节点、仅顶层日本节点、缺 ISP、缺日本、缺美国。`JP.01`、`ikuu-jp专线`、日本、混合大小写 Japan 和旗帜名称均自动入组，非日本节点未混入；空组 REJECT 和 TikTok UDP/444 拒绝均通过。
- 夹具使用回环假节点和本地 GEO 文件，按文档模拟所用 YAML 操作符，未执行 OpenClash Ruby 合并、防火墙或真实机场/ISP 连接；不等同于目标 alpha-gbc76c13 兼容或手机验收。

待完成：目标路由器自动纳入日本节点、真实日本首跳链路、TikTok 播放与 ISP 出口证据、Google Play 下载、国内/人工直连及实机失败关闭。未确认前不得标记 stable。
