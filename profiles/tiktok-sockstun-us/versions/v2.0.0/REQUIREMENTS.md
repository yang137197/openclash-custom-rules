# tiktok-sockstun-us v2.0.0

状态：stable。

验收日期：2026-10-15。用户在本对话明确确认“候选版本已验证，可发布正式版”，据此记录实机验收通过并授权发布。证据类型为用户确认；未额外提供逐项日志、截图或设备清单，不将其描述为 Codex 独立实测。

版本类型：运行架构变更的正式主版本；从 v1.0.0 派生，不包含 v1.1.0 日本版本。

技术标准为 [OpenClash 用户指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md) 及其路由子文档。2026-10-15，用户明确授权舍弃旧文档中与指南推荐架构冲突的设置。业务出口意图继续保留，旧设置不约束本版本。

## 需求与变化

| 编号 | 本版本需求 | 相对 v1.0.0 |
| --- | --- | --- |
| R1 | 所有手机 TikTok 由 SocksTun/IPRoyal 承载；OpenClash 拒绝可识别泄漏，不含 IPRoyal 节点 | 保留；TikTok 的 Fake-IP 规则先于 CN 分类 |
| R2 | 其他国外流量最终走用户手选机场美国节点；无合格节点失败关闭 | 保留 |
| R3 | 中国大陆域名/IP 直连 | 改为 CN MRS 真实地址解析＋防火墙大陆旁路，核心中国规则补充 |
| R4 | 保留 Manual-Direct 的 124 条现有条目及其精确/后缀语义 | 文件不变；同一 classical provider 同时用于真实地址过滤和直连路由 |
| R5 | 局域网、私有地址、自建服务保持直连 | 保留真实地址解析 |
| R6 | Google/Google Play 明确走美国，优先于国内分类和人工直连 | 增加 Google 优先 Fake-IP，配合经美国的专用 DNS，避免域名连接提前进入大陆旁路 |
| R7 | 插件选项由用户手工配置，覆写只有 [YAML] | 保留；完整界面步骤见 SETUP.md |
| R8 | 国内 App 加载与刷新正常 | 用户确认本版已验证；不沿用旧版 QUIC 设置或旧测试结论 |
| R11 | 以指南的 Fake-IP 非 TUN＋大陆 IPv4 绕过为技术基线 | 新增；CN 域名使用 cn.mrs，禁用 QUIC 按指南默认启用作为正式基线 |
| R12 | DNS 配置职责明确，不意外继承订阅解析策略 | 新增；国内 Nameserver、无 Fallback、专用节点解析、明确 Google/TikTok 例外 |

R9/R10 属于独立的 v1.1.0 日本版本，本次不继承；H1–H9 属于按设备方案，本次不继承。

## 数据面与 DNS

1. 正常使用路由器 DNS 的 TikTok/Google 域名先按 Fake-IP 过滤规则处理；Google 保持 Fake-IP，进入核心后走美国，TikTok 可识别连接被拒绝。
2. Manual-Direct、局域网及 CN MRS 域名返回真实地址。真实目标属于大陆 IP 时，在防火墙层旁路；境外 IP 的人工直连连接仍可进入核心并命中 Manual-Direct。
3. 域名未命中上述列表时返回 Fake-IP，进入核心按最终美国策略处理。
4. 启用 respect-rules 时保留 proxy-server-nameserver；direct-nameserver 独立使用国内 DoH，不跟随代理类 DNS 策略。
5. 显式清空 fallback，删除 fallback-filter，替换 nameserver-policy、proxy-server-nameserver-policy 及 fake-ip-filter；保留插件生成的 DNS 监听地址、端口和运行模式。
6. 规则集 oc-cn-domain 显式声明 HTTP/MRS 来源，避免仅依赖插件版本自动生成 provider。provider hash 合并，不删除其他插件 provider。

TikTok 的 rcode://success 是已有泄漏查询策略，不应据此承诺所有 Fake-IP 查询均返回空结果；拒绝可识别连接仍由路由规则完成。纯 IP、客户端私有 DoH/HTTPDNS、未识别的新域名不能仅靠这些域名规则保证出口。SocksTun 的应用级接管仍是 TikTok 唯一路径的前提。

关闭 Fallback 不等于所有协议必然在代理服务器解析。需要核心实际解析的连接仍受 Nameserver/Policy 控制；若特定节点或域名不兼容，应以日志确定是否需要增加显式代理 DNS 策略，不能宣称所有国外解析已经验证。

## 已完成的静态验证（2026-10-15）

- 仓库校验、候选 YAML 语法和 git diff --check 通过；校验器能拒绝 Google Fake-IP 例外被移到 CN 分类之后的变更，即使重新计算 catalog 哈希也不能绕过该检查。
- 使用官方 Mihomo Meta v1.19.32 Windows amd64 对最小配置夹具执行配置检查，通过。夹具按指南操作符合并候选，保留模拟的插件 DNS 端口，并验证旧 Fallback/域名策略已清除；不是在真实 OpenClash 中执行覆写，也未启动代理服务或连接机场。
- 内核提示 classical provider 在 Fake-IP 过滤中仅匹配域名；本版本复用的 124 条全部为 DOMAIN/DOMAIN-SUFFIX，符合该限制。
- 远端 main 的 Manual-Direct 与本地 124 条快照哈希一致；旧版模块、兼容入口和人工规则未修改。
- 候选模块 SHA256：`463efd89b2599d7491bb3d8ae62e9a250c5b3738d44d457234bbefd2329d8e99`。

以上是候选阶段的静态验证，不等于 Codex 独立验证了用户所装 alpha-gbc76c13、防火墙或应用功能。正式发布依据另行取得的用户验收确认。正式模块只移除第一行注释中的 candidate 字样，配置正文与已验收候选一致，最终哈希见 catalog。

## 实机验收范围与证据

以下是本版本规定的验收范围。用户已总体确认候选验证通过，未提交逐项证据，因此不伪造逐项执行记录：

- 用户所用 v0.48.002 / alpha-gbc76c13 能加载模块，支持 fake-ip-filter-mode=rule 和 MRS；日志无未知字段、provider 缺失、DNS 循环或规则解析错误。
- 重启后运行配置中 Google/TikTok 的 fake-ip 规则在 CN real-ip 前；oc-cn-domain 已成功加载，Manual-Direct 仍为 124 条。
- 从使用路由器 DNS 的客户端查询普通 CN 域名，获得真实 IPv4；Google/Play 域名获得 Fake-IP，相关连接命中美国。
- 开启大陆绕过后，已知国内 App 连续加载/刷新正常，记录 App 名、时间、网络及结果。不能用 ping Fake-IP 判断，也不能要求旁路连接出现在核心面板。
- Google Play 完整下载应用，services.googleapis.cn 与 xn--ngstr-lra8j.com 未错误直连。
- 人工直连、自建服务、局域网可用，其他国外网站走手选美国节点。
- SocksTun 启动时 TikTok 可用；停止后无机场或直连回退，发现回退立即停止测试。
- 若为旁路由，国内真实 IP 的回程可达；仅在回程不成立时按指南启用旁路网关兼容，不把它当通用提速开关。
- 启用禁用 QUIC 后没有破坏人工直连的远程控制等业务；境外 DIRECT 的 UDP/443 不会仅因 DIRECT 路由自动获得豁免，必要时据日志调整。

静态校验通过不等于以上实机项目通过，也不证明 App 卡顿根因已解决。

## 发布与回退

本版本当前稳定标签为 `tiktok-sockstun-us-v2.0.0`；catalog 当前稳定版本及兼容入口更新为 v2.0.0。v1.0.0、v1.1.0、按设备方案及其历史标签不改写。回退必须同时恢复旧模块和旧界面设置，详见 SETUP.md。发布后本目录为不可变快照，后续修改进入新版本。
