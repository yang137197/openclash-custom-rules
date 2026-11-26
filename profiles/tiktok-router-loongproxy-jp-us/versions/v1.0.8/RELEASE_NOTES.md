# tiktok-router-loongproxy-jp-us v1.0.8

状态：**stable**。沿现有v1.0.7迭代的正式重构，用户于2026-11-26确认达到验收标准。没有独立控制器、额外服务安装、面板适配或自动写插件开关。

## 需求和变更

| 策略组 | 允许节点 | 选择逻辑与检测 |
|---|---|---|
| TikTok首跳 | 仅iKuuu日本Z数字IEPL，当前用户报告Z01–Z11，后续编号可动态加入 | 原生url-test，选最近一次检测最低有效延迟，tolerance=0 |
| Tiktok美国出口测速 | 仅原TikTok-ISP-Local Loongproxy美国SOCKS5 | 固定出口select，检测经所选日本首跳到美国出口的完整代理链 |
| 良心云-日本专线流媒体 | 仅良心云日本专线xx BGP流媒体、日本高速xx BGP CUCM | 单层fallback，专线01→…→99→高速01→…→99，按顺序故障切换、恢复返回，不按最低延迟选 |
| ikuuu-默认代理 | 与首跳相同范围的iKuuu日本节点 | 独立url-test最低延迟，默认与首跳不要求选同一节点 |

四组及提供商每60秒检测、5000毫秒超时、期望HTTP204、lazy:false，不依赖面板打开。默认GLOBAL保留手选且不定时检测。界面按原生组类型展示，不修改面板标签。

原日本-入口改为TikTok首跳；原TikTok-ISP改为Tiktok美国出口测速；撤除原“美国”机场组，绝不将美国机场节点并入固定ISP。首跳从手选改自动，Claude/Anthropic及普通代理从旧专项/美国组转iKuuu默认代理，属于本版明确授权的行为变化。

两订阅用显式提供商隔离，分别加IK:/LXY:前缀，容忍旗帜、前后缀、空格及大小写变化。iKuuu不固定11节点；良心云遵循两位编号01–99，新增专线05/高速06等自动纳入并独立于订阅原始顺序排序。超出编号、彻底改名或类别标签变更须重新核对。相同类别同编号多个别名保留提供商内部原序。

## 流量路径

- TikTok：iKuuu日本自动首跳 → 原Loongproxy美国ISP。保留udp:false和紧邻TikTok REJECT；UDP不能通过时拒绝，不能回退机场、良心云或DIRECT。
- 良心云：YouTube、Netflix、Telegram、Disney+、HBO/Max、Prime Video、Twitch、Spotify、Apple TV+、Steam、Epic、Blizzard、MEGA、Dropbox及GitHub的objects/release-assets专用下载域名。整站分类包含Telegram文字、游戏平台商店及登录；不是按HTTPS路径或文件大小拆分。Google Drive/OneDrive不整站迁移，无法识别的下载仍默认iKuuu。
- iKuuu默认：Google、AI/Claude、GitHub网页/API/普通raw内容、邮件、电商、新闻及其余普通境外流量。
- DIRECT：私网、国内及手动直连。新媒体分类排除Manual-Direct、CN域名及已解析CN IP，保留原Google→Manual-Direct→CN→MATCH相对顺序。

唯一手动直连源仍为rules/manual-direct.yaml；本次148条记录逐项、同序、含重复项保留，不设未来域名清单或条数限制。流程A继续由GitHub Actions生成同一滚动模块及哈希；日常增删不新建版本或改固定快照。

## 日常滚动覆写订阅

保持原地址，发布后同步为v1.0.8，以后日常直连仍通过它更新：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf

## 本版本标签固定覆写订阅

固定快照不会随日常源规则更新：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.8/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.8/openclash-overwrite.conf

云模块SHA-256：`b4cd3349c48c4df6a617bc500cd4e3a594b1c87b74d7aeb24b03d93bdc903fec`

## 唯一本地模板附件

[下载 local-tiktok-proxy.conf](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.8/local-tiktok-proxy.conf)

附件SHA-256：`0860797f702ba8189e07324ba06b5fc956594199abdf36e0cd9e4f90deacedb0`

只附这一个与标签模板相同的.conf文件；GitHub自动源码压缩包不能代替本地模板。已完成候选测试的用户可继续使用已填写的配对本地模块，不必重填。

| 占位字段 | 服务商信息及格式 |
|---|---|
| FILL_ME_IKUUU_SUBSCRIPTION_URL | iKuuu的Mihomo/Clash YAML订阅，必须含proxies列表，完整URL用YAML单引号 |
| FILL_ME_LIANGXINYUN_SUBSCRIPTION_URL | 良心云的同类YAML订阅；不是Base64 URI节点列表 |
| FILL_ME_PROXY_HOST | 原Loongproxy美国出口主机，字符串 |
| FILL_ME_PROXY_PORT | 原服务端口，填写整数 |
| FILL_ME_USERNAME | 原用户名，字符串 |
| FILL_ME_PASSWORD | 原密码，字符串；内部单引号写成两个单引号 |

以下仅为**虚构填写示例**，不可直接使用：两个订阅分别为`https://example.invalid/ikuuu.yaml`和`https://example.invalid/liangxinyun.yaml`；ISP server为`proxy.example.invalid`、port为`1080`、username为`DEMO_USER`、password为`DEMO_PASSWORD`。只替换对应占位值，保留节点名TikTok-ISP-Local、socks5、udp:false和dialer-proxy: TikTok首跳，以及命名提供商/筛选/检测字段。

真实订阅URL、令牌、节点主机和认证只填路由器本地，禁止提交仓库、Release、聊天或公开日志。模块只含[YAML]，不会安装程序或自动调整OpenClash插件设置。

## 应用与回退

云模块为远程订阅，本地模块上传填好的.conf；匹配同一当前配置完整路径，云在本地上方。只启用一套配对模块。已验收候选的用户把云订阅改回上面的原main地址，点更新并重启OpenClash。

不要混用v1.0.8本地模块与v1.0.7云模块；旧云只有日本-入口，会报dialer-proxy找不到TikTok首跳。回退必须恢复旧云和它的配对本地模块后统一重启，不能只关闭新云留下新的首跳引用。

## 环境、验收和限制

- 本轮调试日志：2026-11-26 15:28:14；OpenClash 0.48.002、运行alpha-gbc76c13、OpenWrt 24.10.2 r7492-3fda82b52、QEMU x86_64、内核6.12.38。用户设备称CatWrt.v25.8.amd64 / LEDE R25.7.7。
- 日志确认四组字段、路由结构及148条手动直连；IP规则在日志中被脱敏，节点/提供商认证被隐藏。用户截图补证云在本地上方且两者启用。禁用QUIC实际停用，作为已验收偏差保留，本版不改开关。
- 用户整体确认达到验收标准。业务通过来自用户确认；不声称日志采样独立覆盖所有平台播放、故障切换与回退。用户实测的固定提交57217e8与本版云/本地模板逐字节相同，版本迁移没有改变运行内容。
- 桌面静态检查及官方OpenClash合并、Mihomo v1.19.34合成网络回归与实机证据分开记录。204可达不证明带宽/解锁；顺序回退不保证已建立连接无缝迁移；自动组选中节点可能受面板人工固定影响。良心云全部不可用时不跨订阅兜底。
- 原始日志、私有配置和截图不入公开仓库。v1.0.7及更早已发布目录、标签和Release不修改。

[详细需求D1–D13](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.8/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.8/REQUIREMENTS.md) · [OpenClash设置及完整回退](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.8/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.8/SETUP.md) · [环境记录](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.8/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.8/ENVIRONMENT.json) · [验证记录](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.8/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.8/VALIDATION.md)
