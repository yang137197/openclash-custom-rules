# tiktok-router-dual-subscription-jp v1.0.0 需求合同

状态 **candidate**。需求来源：2026-11-26 用户明确重构要求及选择“固定顺序，故障切换、恢复返回”；本合同仅适用于本方案，不改变原正式版合同。

- D1：`日本-入口` 在新方案改为 `TikTok首跳`；仅使用显式 `dual-ikuuu` 提供商中名称含“日本Z＋数字＋IEPL”的节点。当前用户报告 Z01–Z11，不将 11 作为固定数量；Z12 等自动加入，容忍旗帜、前缀、空格、倍率后缀。按本次第5条使用原生 url-test 自动选最近一次检测最低有效延迟，tolerance=0。首跳自动选择是本次明确授权的行为变更。
- D2：原 `TikTok-ISP` 在新方案改为 `Tiktok美国出口测速`；撤除原“美国”机场组，不把其机场节点并入 ISP。出口组仅引用精确节点 `TikTok-ISP-Local`，保留 select、SOCKS5、udp:false；本地节点 dialer-proxy 仅改引用名为 `TikTok首跳`。ISP 地址、端口、账号密码由用户沿用本地现有值，云模块不保存。
- D3：TikTok 仍经 iKuuu 日本首跳 → Loongproxy 美国出口；保留紧邻 TikTok REJECT 规则，禁止回退普通机场、良心云或 DIRECT。缺少节点时 empty-fallback:REJECT；全组节点失败时原生组可能仍报告首个不可用节点，不宣称它会改成 REJECT 标签。
- D4：新增 `良心云-日本专线流媒体`，仅引用显式 `dual-liangxinyun` 提供商。允许“日本专线xx|BGP|流媒体”“日本高速xx|BGP|CUCM”，容忍前缀、旗帜、空格、大小写及分隔后的倍率后缀。当前4专线+5高速是用户报告，不锁定数量。
- D5：良心云使用单层原生 fallback，排序为专线01→02→…→99→高速01→02→…→99，缺号跳过。维持服务商两位编号约定；新增专线05、高速06等自动纳入，订阅原始乱序不改变优先级。00、100、彻底改名、类别或协议标签变化不自动加入，须重新核对并递增候选；不承诺任意未来命名都无需维护。同号多个别名仍按提供商原顺序，其内部顺序没有额外承诺。
- D6：按固定顺序选择第一个检测可用节点，不比较节点延迟大小；故障切换、恢复确认后返回更高优先节点。无需独立控制器、定时任务或安装服务。不要在面板手动固定自动组；人工固定可能改变原生自动行为。全部失败不跨订阅兜底；已有 TCP 连接不保证无缝迁移。
- D7：新增 `ikuuu-默认代理`，节点来源和筛选与 `TikTok首跳` 相同；使用独立 url-test 最低延迟选择，两组不要求选中同一个节点。普通境外、Google、AI（含 Claude/Anthropic）、GitHub网页/API、邮件、电商、新闻走此默认组，覆盖原 Claude 经 ISP 的旧特例。
- D8：四组及两个提供商使用 https://www.gstatic.com/generate_204，每60秒检测、5000毫秒超时、期望204、lazy:false。ISP 检测经过完整代理链；首跳检测仅证明首跳本身可达，不能替代完整链路和视频播放。保留内核默认 GLOBAL，不配置 GLOBAL 定时检测，不定制面板。
- D9：指定流媒体、网盘、游戏平台及专用下载域名走良心云。名单为 YouTube、Netflix、Telegram、Disney+、HBO/Max、Prime Video、Twitch、Spotify、Apple TV+、Steam、Epic、Blizzard、MEGA、Dropbox，以及 objects.githubusercontent.com 和 release-assets.githubusercontent.com。平台分类覆盖其整站（包括 Telegram 文字、游戏平台商店），不是按文件大小或 HTTPS 路径拆分。Google Drive/OneDrive 不整站自动迁移；无法识别的下载仍走默认组。
- D10：新分类全部置于 TikTok 与紧邻 REJECT 之后、Google 大类之前，并排除 Manual-Direct、CN域名及已解析CN IP，避免截走直连命中。Telegram补充IP规则。保留私网、Google→Manual-Direct→CN→MATCH 的既有相对顺序；只将其他代理目标改为新默认组。DNS结构/解析器沿用基线，只同步策略组引用；不改变防火墙、IPv6、TUN、QUIC或插件开关。
- D11：唯一手动直连源 rules/manual-direct.yaml 字节不变；候选 inline payload 与当前源逐项同序、含重复项一致，不固定域名清单、条数或源哈希。原方案目录和正式入口不变。
- D12：仅通过供应商提供商归属和名称双重筛选；绝不 include-all 混选两机场。本地提供商添加 IK:/LXY: 前缀防重名。真实订阅URL和代理凭据仅存在路由器本地；公共模板均为 FILL_ME 占位。订阅应返回 Mihomo YAML 的 proxies 列表；Base64 URI 订阅不作为此模板支持输入。
- D13：交付经本地验证、CI通过的候选供用户手动测试，不操作路由器、不安装服务。正式发布须取得本候选实机日志及用户确认，再按已有授权发布、同步 GitHub，并建立独立滚动入口和共享直连源同步；原正式方案仍可保留和回退。

## 验收标准

1. 实机仅出现四个显式策略组和内核 GLOBAL；两个 iKuuu 组当前各11节点，良心云当前9节点，ISP组仅1个本地出口（数量按实际订阅可变化）。
2. 面板关闭后仍有新检测记录；iKuuu自动选低延迟，良心云按顺序而非最低延迟选择；故障和恢复后新连接符合顺序。
3. TikTok 打开和持续播放，确认链路含日本首跳及原美国 ISP；首跳自动切换后重测完整链路。
4. 流媒体、默认代理、AI、GitHub网页/下载按合同命中；国内、局域网、手动直连及子域名正常。记录规则命中与业务结果，不能仅凭测速验收。
5. 停用新方案、恢复原来一套配对模块后统一重启，原业务恢复；不得把“全部云模块关闭”当作完成回退。

## 技术依据

- [OpenClash 官方指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md)及16-overwrite-module-format.md §16.1、§16.2。
- [Mihomo fallback](https://wiki.metacubex.one/config/proxy-groups/fallback/)、[url-test](https://wiki.metacubex.one/config/proxy-groups/url-test/)、[健康检查](https://wiki.metacubex.one/config/proxy-providers/)。
- [用户报告核心对应的排序源码](https://github.com/MetaCubeX/mihomo/blob/bc76c1398c6e70089367a30169d0df7c7f77c42d/adapter/outboundgroup/groupbase.go)。源码审阅不等于该设备已运行验证。
