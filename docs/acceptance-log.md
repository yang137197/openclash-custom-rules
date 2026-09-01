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

## 2026-08-29：奥智联与一汽奥迪 App 直连

范围：`rules/manual-direct.yaml`。

确认与变更：

- 奥智联的开发者和隐私政策均指向辽宁科大物联，官方业务站点为 `audi.askdwl.com`；添加 `DOMAIN-SUFFIX,askdwl.com`，覆盖该 App 同一自有域名下的接口和子域名。
- 一汽奥迪 App Store 的开发者隐私政策指向 `audi2c.faw-vw.com`，官方平台使用 `audi.cn`；添加 `DOMAIN-SUFFIX,faw-vw.com` 与 `DOMAIN-SUFFIX,audi.cn`。
- 三条手工直连规则位于设备地区规则和国内规则之前，优先命中 `DIRECT`。

验收：

- 全部 9 个规则 YAML 文件解析成功。
- 将新规则加载到既有最小合并配置后，官方 Mihomo `v1.19.30` 配置测试成功。
- Git 差异检查通过。

未覆盖：公开资料不能证明 App 运行期间调用的全部第三方 SDK、CDN 或临时域名。若实机仍有单项功能失败，应按手机源 IP 抓取该操作发生时的 OpenClash 连接日志，再只补充实际误走代理的域名。

## 2026-08-31：微信小程序 CDN 同级域名直连

触发证据：`192.168.100.216` 访问 `webcdn.gdwzy.top:443` 命中 `Linyang-Device-JP → 日本`。

根因与变更：

- 原规则 `DOMAIN-SUFFIX,web.gdwzy.top` 只覆盖 `web.gdwzy.top` 及其下级域名，不覆盖同级的 `webcdn.gdwzy.top`，并非规则优先级冲突。
- 将规则扩大为 `DOMAIN-SUFFIX,gdwzy.top`，统一覆盖 `gdwzy.top`、`web.gdwzy.top`、`webcdn.gdwzy.top` 及其他子域名。
- Cloudflare DoH 查询确认三个域名均正常解析；APNIC RDAP 显示对应地址分别属于中国 ALISOFT 和 CHINANET-JX 网段。

验收：

- 全部 9 个规则 YAML 文件解析成功。
- 新规则加载到最小合并配置后，官方 Mihomo `v1.19.30` 配置测试成功。
- 回读确认 `Linyang-Manual-Direct → DIRECT` 仍位于设备地区规则之前，Git 差异检查通过。

实机更新后应确认日志显示 `webcdn.gdwzy.top match RuleSet(Linyang-Manual-Direct) using DIRECT`。

## 2026-08-31：手工直连统一覆盖主域名和全部子域名

范围：`rules/manual-direct.yaml`、`README.md`。

变更与验收：

- 明确手工直连只填写业务主域名，并统一使用 `DOMAIN-SUFFIX`；不再使用只匹配单一完整域名的 `DOMAIN`。
- 当前 `gdwzy.top`、`askdwl.com`、`faw-vw.com`、`audi.cn` 四个直连主域名均已符合该规范，可同时匹配主域名和所有层级的子域名。
- README 示例同步改为 `DOMAIN-SUFFIX,gdwzy.top`，避免以后因新增同级接口或 CDN 子域名漏匹配。
- 全部 9 个规则 YAML 文件解析成功；官方 Mihomo `v1.19.30` 配置测试成功；检查确认 `manual-direct.yaml` 不含 `DOMAIN`、`DOMAIN-KEYWORD` 或过窄的 `web.gdwzy.top` 条目。

## 2026-08-31：微软服务全局直连

范围：`overwrite/openclash-overwrite.conf`、`README.md`。

变更：

- 在设备地区和第三方订阅规则之前新增 `GEOSITE,microsoft,DIRECT`、`GEOSITE,onedrive,DIRECT`、`GEOSITE,xbox,DIRECT`。
- 覆盖 Windows Update、Microsoft Store、微软账号、Microsoft 365/Office、Outlook、Teams、Skype、OneDrive/SharePoint 和 Xbox 等微软服务。
- 当时误判 GitHub 不在微软分类中；当前数据实际包含 GitHub，已由下方 2026-09-01 修正记录取代。LinkedIn 当前不在该微软分类中。

验收：

- 覆写 YAML 和全部 9 个规则文件解析成功。
- 官方 Mihomo `v1.19.30` 加载配置成功；当前 Geosite 数据分别加载 Microsoft 751 条、OneDrive 19 条、Xbox 45 条，目标均为 `DIRECT`。
- 三条微软直连规则位于所有手工地区规则、Google/TikTok/Google Play 设备规则和设备兜底规则之前；Git 差异检查通过。

未覆盖：没有用户路由器实时访问权；更新覆写模块并应用后，应从 OpenClash 日志确认微软域名命中 `GeoSite(microsoft|onedrive|xbox) using DIRECT`。

## 2026-09-01：修复 GitHub 被微软分类错误直连

范围：`overwrite/openclash-overwrite.conf`、`README.md`。

根因与变更：

- 当前 MetaCubeX `GEOSITE,microsoft` 含有 `github.com`、`githubusercontent.com`、`githubassets.com` 等 GitHub 域名；微软直连规则提前命中后，会使中国大陆网络直接连接 GitHub 并失败。
- 将手工域名规则保持在内置分类之前，确保用户显式规则优先。
- 在微软直连之前新增 GitHub 例外：登记设备跟随日本、美国或新加坡设备策略；未登记设备默认走“美国”。
- 规则提供者继续通过 `DNS-海外` 下载 GitHub Raw，不改为直连。

验收：

- `yq` 成功解析覆写的 YAML 段和全部 9 个规则文件。
- 官方 Mihomo `v1.19.30` 配置测试成功；当前 Geosite 数据加载 GitHub 64 条、Microsoft 751 条，GitHub 目标为设备地区或“美国”，Microsoft 目标为 `DIRECT`。
- 顺序检查通过：手工规则在前，GitHub 例外居中，Microsoft 直连在后；三条设备 GitHub 规则齐全，Git 差异检查通过。

实机更新后应确认：浏览器访问 `github.com`、`raw.githubusercontent.com` 时，日志命中 `GeoSite(github)`，策略为设备对应地区或未登记设备的“美国”，而不是 `DIRECT` 或 `GeoSite(microsoft)`。

## 2026-09-01：撤回 Microsoft 与 GitHub 专用分流

范围：`overwrite/openclash-overwrite.conf`、`README.md`、`CHANGELOG.md`。

变更：

- 删除 Microsoft、OneDrive、Xbox 全局直连规则。
- 删除 GitHub 按设备地区代理及未登记设备默认美国的专用规则。
- 保留手工域名规则、国内直连、设备地区规则及第三方订阅原规则；Microsoft 和 GitHub 流量按这些通用规则继续匹配。
- 新增项目更新日志，并在 README 提供统一入口；以后发布或功能更新同步维护更新说明和验收记录。

验收：

- `yq` 成功解析覆写 YAML 段和全部 9 个规则文件。
- 静态检查确认 `+rules` 中已不存在 `GEOSITE,microsoft`、`GEOSITE,onedrive`、`GEOSITE,xbox` 或 `GEOSITE,github`。
- 官方 Mihomo `v1.19.30` 配置测试成功，启动日志未加载上述四个已删除分类；Git 差异检查通过。

未覆盖：未连接用户的 OpenClash 实机。更新覆写模块并应用/重启后，需通过连接日志确认 Microsoft 与 GitHub 按通用规则命中。

## 2026-09-01：修复 Kimi API 开放平台无法访问

根因与范围：

- `platform.kimi.com` 的公共 DNS 解析一致指向火山引擎防护节点，排除常见 DNS 污染；Kimi 官方平台和文档从外部网络可正常访问。
- 本地直连 `platform.kimi.com:443` 在 TLS 握手阶段失败，而 `api.moonshot.cn`、`api.kimi.com`、`www.kimi.com` 可建立连接，故障范围收敛到开放平台域名的当前直连路径。
- 官方 Mihomo 规则实测确认修改前该域名命中 `GeoSite(cn) using DIRECT`。
- 在 `rules/manual-jp.yaml` 增加精确规则 `DOMAIN,platform.kimi.com`；不扩大为 `DOMAIN-SUFFIX,kimi.com`，避免改变其他可正常直连的 Kimi 服务。

验收：

- `yq` 成功解析全部 9 个规则文件和测试配置。
- 官方 Mihomo `v1.19.30` 配置测试成功。
- 代理请求日志命中 `RuleSet/Linyang-Manual-JP` 并选择“日本”，证明该精确规则位于 `GEOSITE,cn,DIRECT` 之前且已生效。
- 测试配置中的日本节点为本地不可用占位节点，因此本次功能测试只验收规则匹配，不代表用户订阅节点的真实可用性。
- 本次仅修改规则提供者文件；实机可等待最多约 60 秒自动更新，或手动更新 `Linyang-Manual-JP`，无需更新覆写模块或重启。

## 2026-09-01：更正 Kimi 为中国大陆直连

本记录取代上方“将开放平台临时分配到日本”的处理结论。

变更与诊断：

- 清空 `rules/manual-jp.yaml` 中的 `platform.kimi.com` 规则。
- 在 `rules/manual-direct.yaml` 使用 `DOMAIN-SUFFIX,kimi.com` 和 `DOMAIN-SUFFIX,moonshot.cn`，确保 Kimi 官网、开放平台及 Moonshot API 均优先直连。
- 路由器 DNS、Cloudflare DoH、Google DoH、阿里 DoH 均把 `platform.kimi.com` 解析为 `poevnnxxg2ygauv0f2cc.volcddos.com` 和 `103.143.17.156`，未发现解析分歧；该域名未返回 AAAA。
- `103.143.17.156:443` 的 TCP 连接成功，失败发生在 TLS ClientHello 之后；因此不能把问题归因于端口不通，也不应继续用日本节点绕行。

验收：

- `yq` 成功解析全部 9 个规则文件和测试配置。
- 官方 Mihomo `v1.19.30` 配置测试成功。
- 功能请求日志确认 `platform.kimi.com` 命中 `RuleSet(Linyang-Manual-Direct) using DIRECT`。
- 直连版本发布并刷新后，OpenSSL TLS 1.2、TLS 1.3、Windows Schannel、固定 IPv4 加 SNI 均成功完成握手，证书验证正常。
- `platform.kimi.com/`、`/console`、`/docs` 和 `www.kimi.com` 均返回 HTTP 200；`api.moonshot.cn/v1/models` 返回未带 API Key 时预期的 HTTP 401，证明 API 网络和 TLS 可达。
- 原始 TLS 中断目前已无法复现，证据不支持继续修改 DNS、MTU、IPv6、Fake-IP 或证书校验；保留显式直连规则作为稳定分流边界。

## 2026-09-01：定位 GitHub 仍命中旧 Microsoft 直连规则

现场证据：

- OpenClash 日志显示 `github.com`、`avatars*.githubusercontent.com` 仍命中 `GeoSite(microsoft) using DIRECT`，证明运行配置尚未加载已删除该规则的最新覆写。
- 同时，日本节点的代理服务器返回 `503 Service Unavailable`；这是独立的节点故障，不能解释 GitHub 的 `DIRECT` 命中。
- 实时回读发现 jsDelivr `@main` 返回 10187 字节旧覆写并含 7 条 Microsoft/GitHub 规则；固定提交 `@f78b82c` 与 GitHub Raw 主分支返回 9664 字节新覆写，相关规则数量为 0。

处理：

- README 备用地址改为固定提交 `@f78b82c`，并明确禁止用 jsDelivr `@main` 获取刚提交的实时覆写。
- 实机应只保留一个本仓库模块订阅，使用固定提交地址更新、应用并重启；确认日志不再命中旧 Microsoft 规则后，再恢复 GitHub Raw 主地址。
