# 验收记录

## 2026-08-24：设备地区分流、TikTok、手机连接与 Google Play

范围：`overwrite/openclash-overwrite.conf`、`rules/*.yaml`、`README.md`。

结果：

- OpenClash 覆写 `[YAML]` 段和全部规则文件通过 YAML 解析。
- 使用官方 Mihomo `v1.19.30` 将覆写合并到含日/美/新节点的最小配置，`mihomo -t` 验证成功。
- Mihomo API 回读确认：`日本`、`美国`、`新加坡`默认分别选择对应自动组；节点过滤结果分别只包含测试日/美/新节点。
- Mihomo API 回读确认：局域网、手工规则、TikTok/Google Play 设备逻辑规则、国内直连和设备规则按设计顺序加载。
- 空的新加坡设备文件和空的手工规则文件可被 Mihomo 作为 classical rule-provider 正常加载。
- 仓库未加入订阅地址、令牌或密钥。

未覆盖：未连接用户的 OpenWrt/OpenClash 实机，无法在本地替代真实手机、Windows、TikTok 和 Google Play 端到端测试。部署后应按 README 的故障检查项完成实机验收。

## 2026-08-24：设备 IP 维护说明

范围：`README.md`。

结果：

- 记录同一设备在不同局域网使用相同网段时的匹配行为、适用条件和地址冲突边界。
- 补充 GitHub 网页编辑、提交、创建拉取请求及 OpenClash 更新步骤。
- 设备地区规则文件改为可点击的相对链接；本次没有修改实际分流规则。
- Markdown 格式和 Git 差异检查通过。

## 2026-08-24：TikTok 网络不稳定修正

范围：`overwrite/openclash-overwrite.conf`、`rules/tiktok.yaml`、`README.md`。

结果：

- 新增独立 TikTok 规则提供者，覆盖主站、API、CDN、特效及字节海外共享域名，并保持在中国直连规则之前。
- 启用 TLS/QUIC 纯 IP 域名嗅探，减少 CDN 连接因缺少域名而误判直连。
- 保留 UDP 代理，但禁用 UDP/443 QUIC，使 UDP 不稳定节点回落到 TCP/HTTPS。
- 补充规则缓存、固定节点、连接日志和出口可用性检查步骤。
- 覆写 YAML 段和 11 个规则文件通过 YAML 解析；TikTok 规则共 41 条。
- 使用官方 Mihomo `v1.19.30` 加载最小合并配置，`mihomo -t` 验证成功。
- Mihomo API 回读确认：嗅探器正常加载，TikTok 规则提供者 41 条，前三条设备条件规则依次指向日本、美国、新加坡。

未覆盖：无法从本地访问用户的 OpenClash 实机和手机，因此节点出口是否被 TikTok 接受仍需部署后通过连接日志和手机实测确认。

## 2026-08-24：确定性分流与 DNS 重写

触发证据：`192.168.100.203` 访问 `www.dmv.org` 命中第三方 `MATCH`，实际选择香港节点，而不是“美国”。

根因：设备美国规则在 17:28 从 `.238` 改成 `.203`，但规则提供者沿用旧本地路径和 86400 秒更新周期，OpenClash 可继续加载旧缓存。

变更：

- 设备和手工规则改用新的 `linyang-v2-*` 缓存路径，更新周期缩短为 300 秒；静态 TikTok/Google Play 规则为 3600 秒。
- 所有规则提供者显式通过 `DNS-海外` 下载，避免下载连接落入第三方香港 `MATCH`。
- Google `GEOSITE` 在中国直连规则之前按设备地区匹配，避免 `gstatic` 等重叠域名出口分裂。
- DNS 改为中国域名国内 DoH、其他域名经 `DNS-海外` 使用境外 DoH；禁用 WAN DNS 追加，节点域名单独使用国内 DoH 防止循环依赖。
- 清理当前需求之外的 `AI-日本`、`俄罗斯电商` 策略组、规则提供者及 `rules/ai.yaml`、`rules/ru-commerce.yaml`。
- 整理设备规则 YAML 缩进，保留 `.216`、`.239` 走日本，`.203` 走美国。

验收：

- 覆写 YAML 和保留的 9 个规则文件通过 YAML 解析。
- 官方 Mihomo `v1.19.30` 加载 DNS、嗅探、Google/TikTok/Google Play、国内直连和第三方最终 `MATCH` 的最小合并配置，`mihomo -t` 成功。
- API 回读：`Linyang-Device-US` 1 条、`Linyang-Device-JP` 2 条、TikTok 41 条、Google Play 10 条；Google 美国逻辑规则位于设备美国兜底和最终 `MATCH` 之前。

未覆盖：没有用户路由器的实时 API/文件访问权，部署后仍需用 OpenClash 日志确认 `.203` 命中 `RuleSet/Linyang-Device-US → 美国`。

## 2026-08-25：微信小程序业务域名直连

触发：微信小程序访问 `web.gdwzy.top` 失败。

诊断与变更：

- Google、Cloudflare、AliDNS、DNSPod DoH 均解析为 `47.121.182.56`；APNIC RDAP 登记为中国 `ALISOFT` 地址段。
- 直接访问源站的 HTTP 返回 `301` 跳转 HTTPS，HTTPS 返回 `200 OK`，TLS 校验成功。
- 在 `rules/manual-direct.yaml` 添加 `DOMAIN-SUFFIX,web.gdwzy.top`，匹配该域名及其下级子域名，但不影响 `gdwzy.top` 的其他同级子域名。

验收：

- 全部 9 个规则 YAML 文件解析成功。
- 将新规则合并到既有最小配置后，官方 Mihomo 配置测试成功。

未覆盖：无法访问用户的 OpenClash 实机及微信小程序运行日志；部署后应确认连接命中 `RuleSet/Linyang-Manual-Direct → DIRECT`。若已经命中仍失败，应检查小程序后台的 `request` 合法域名及服务端应用日志。

## 2026-08-25：手工直连说明与快速规则更新

范围：`README.md`、`overwrite/openclash-overwrite.conf`。

变更：

- 明确以后所有“不走代理”域名统一维护在 `rules/manual-direct.yaml`，并说明 `DOMAIN` 与 `DOMAIN-SUFFIX` 的匹配范围、格式、示例和常见错误。
- 设备及手工规则提供者更新周期由 300 秒缩短为 60 秒。
- 模块加入 `RESTART = true`；远程模块定时更新成功后自动重启。
- 记录 OpenClash 手动刷新覆写订阅只下载模块文件，不保证立即重新加载配置；规则立即生效应刷新对应规则提供者，模块变更后应应用或重启。
- 保留规则提供者通过 `DNS-海外` 下载；不在启动阶段强制直连 GitHub Raw，避免下载失败阻断模块加载。

验收：

- 覆写 `[YAML]` 段和全部 9 个规则文件通过 YAML 解析。
- 回读确认共有 9 个规则提供者，其中 4 个手工规则和 3 个设备规则的 `interval` 均为 60 秒；`RESTART = true` 唯一且可被当前 OpenClash 解析。
- 9 个 GitHub Raw 规则地址均返回 HTTP 200，内容与提交前的 `origin/main` 一致。
- 使用官方 Mihomo `v1.19.30` 加载 60 秒更新周期的最小合并配置，`mihomo -t` 验证成功。
- Markdown 和 Git 差异检查通过。

未覆盖：没有用户路由器的实时访问权，无法替代 OpenClash 实机验证模块下载、重启和连接日志。
