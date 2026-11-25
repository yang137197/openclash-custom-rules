# v1.8.4 candidate：节点显示、定时测速与回退

本候选在GitHub准备，不操作用户电脑或路由器，不安装服务。v1.8.3用户已确认业务测试正常并报告回退恢复；本版的新显示/检测字段尚未实机验收。正式稳定版仍v1.5.0。

## 面板和测速

| 组 | 显示与节点 | 选路 | 检测 |
| --- | --- | --- | --- |
| TikTok首跳 | 原iKuuu日本Z01–Z04与REJECT | 手选，原首跳不变 | 每60秒检测，lazy:false |
| TikTok测速 | 原TikTok-ISP-Local | 手选，Loongproxy美国出口不变 | 每60秒检测该链路 |
| 良心云 | 唯一子组良心云-严格控制 | 原生URLTest外层 | 每60秒检测当前链路 |
| 良心云-严格控制 | 可见，REJECT及四档实际节点 | 控制器严格四档管理 | 组检测字段齐全；provider定时检测叶节点 |

不把外层的唯一子组误认为全部机场节点。节点及延迟在可见内部组查看；前端对延迟记录的具体展示仍须实机核验。定时测速与自动选路不同：TikTok两组保持select和原手选，内部仍由控制器管理，不更改TikTok链路。

所有检测使用 https://www.gstatic.com/generate_204，60秒、5秒超时、204、lazy:false。对use引入的叶节点，保留provider health-check；只添加组url不能替代叶节点检测。本版不会把其他节点加入外层以伪装列表，这会绕过严格优先级。

依据：[Mihomo通用字段](https://wiki.metacubex.one/config/proxy-groups/)、[select](https://wiki.metacubex.one/config/proxy-groups/select/)、[v1.19.34核心组解析](https://github.com/MetaCubeX/mihomo/blob/v1.19.34/adapter/outboundgroup/parser.go)。接口支持及合成测试不代表目标alpha-gbc76c13已实测通过。

## 原配置与直连维护

完整云继续使用当前滚动地址，保留用户全部手动直连源；不使用固定条数或旧快照回滚源。rules/manual-direct.yaml仍是唯一可编辑源，流程A/B保持。

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/overwrite/openclash-overwrite.conf

原已填凭据模块不替换。完整参考openclash-overwrite.conf仅供本地验证，不用于本次已有配置升级；升级使用新远程增量。

## 仅在准备好维护窗口后应用

详细步骤见[REAL_DEVICE_TEST.md](REAL_DEVICE_TEST.md)。候选期间保持当前已恢复配置，勿只启用增量而不运行控制器。

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.4/liangxinyun-incremental.conf

采用新的私有/root测试目录，避免/tmp材料因重启丢失；保存本轮真实应用前完整运行快照，不用已应用后的配置冒充改动前基线。下载固定提交并核对BUNDLE。复用已有原生依赖/锁/状态/监督单项，不重测或安装依赖。

按[官方模块16.1](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)创建远程增量，名称liangxinyun-v184-incremental.conf，绑定活动配置完整路径。内建脚本保持第一项，新增量在完整云上方，完整云在原本地模块上方。关闭其他版本增量后再启用本版，统一重启OpenClash插件。

新Ruby只读工具scripts/liangxinyun_v184_runtime_scope.rb仍仅需要现有Ruby YAML。运行方式为ruby 工具 当前运行YAML 完整云缓存 新增量缓存 < 本轮应用前基线；成功应passed、outsideAuthorizedScopeUnchanged、tiktokRoutingUnchanged、automaticProbesConfigured均true。它允许唯一源已授权的规则更新，不证明核心内存中全部规则。不得将v1.8.3工具用于本版，旧工具会正确拒绝新增的TikTok检测字段。

随后--preflight必须candidateCompatible:true。--once仅一轮，持续运行必须通过原监督脚本--run并保持会话；本版未安装常驻服务。控制器仅写良心云-严格控制，不切换TikTok。

## 正常停止与恢复日常代理

1. 正常写入监督PID对应stop标记，等待第一窗口supervisor-stop、verifiedSelection:true及监督退出码0；只执行touch不代表已停止。
2. 停止后内部组为REJECT，普通代理暂时无法连接是该清理策略的结果。恢复日常配置还要在覆写模块关闭本候选、恢复操作前的增量开关/绑定/顺序，然后重启OpenClash。
3. 在恢复后的手动良心云组手选原可用节点，再验证普通代理、TikTok和直连。不要只重启却仍停在REJECT，也不重新启用已停止控制器对应的自动外层。
4. 若仍显示自动外层，先只读核对实际运行组和模块状态，不反复重启、不删除历史缓存。没有恢复结果则不能认定回退成功。完整云保留最新已授权直连源。

已知measurements-changed-before-selection保护及API故障/掉电竞争限制沿用前版，不声称已解决。

## OpenClash 独立手工设置


沿用v1.5.0实机值，本候选不改插件设置。目标记录为OpenClash0.48.002／alpha-gbc76c13／CatWrt24.10.2 x86_64；v1.8.4尚未实机运行，环境来自2026-11-25的v1.8.3日志。以下路径在「服务 → OpenClash」下，供新装／恢复设置参考：

| 页面 | 设置 | 建议／适用条件 |
| --- | --- | --- |
| 插件设置 → 模式设置 | 运行模式／代理模式 | 方案基线：Fake-IP增强，非TUN／混合；规则模式 |
| 同上 | UDP流量转发／旁路兼容 | UDP开启，ISP仍udp:false；旁路兼容按回程证据，主路由关闭 |
| 插件设置 → 流量控制 | 路由器本机代理 | 开启 |
| 同上 | 实验性：绕过指定区域IPv4 | 沿用中国大陆及MetaCubeX cn.mrs |
| 同上 | 禁用QUIC | 建议开启；当前停用，本次沿用现值 |
| 同上 | 绕过服务器地址／仅允许内网访问／仅常用端口 | 前两项开启；仅常用端口关闭 |
| 插件设置 → IPv6设置 | IPv6代理／IPv6 DNS／区域IPv6绕过 | 关闭，核对客户端无独立IPv6出口 |
| 插件设置 → DNS设置 | 本地DNS劫持 | Dnsmasq转发 |
| 覆写设置 → DNS设置 | 自定义上游／遵守路由／Fake-IP持久化 | 方案必需：开启；界面需要条目时HTTPS223.5.5.5:443 |
| 同上 | 附加上游／追加默认DNS／Fallback | 关闭，解析器由既有完整云模块管理 |
| 同上 | 自定义Fake-IP-Filter | 开启、rule模式，不填旧黑名单 |
| 覆写设置 → Meta设置 | 嗅探／进程查找 | 嗅探开启，进程查找off |
| 覆写设置 → 规则设置 | 仅代理命中规则／额外本地规则 | 关闭 |
| 插件设置 → GEO数据库订阅／大陆白名单订阅 | 分类数据 | 确认下载有效并保持更新 |

DNS顺序、TikTok专用DoH、Manual-Direct及CN直连全部沿用原完整模块；IPv6代理关闭不代表全网IPv6关闭，QUIC可在核心前被拒绝。客户端继续使用路由器DNS。

依据：[官方覆写16.1／16.2.3](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)、[API15.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/15-api.md)、[固定合并源码](https://github.com/vernesong/OpenClash/blob/e553e82e01c697aefbe1555261a503f425e00ccd/luci-app-openclash/root/usr/share/openclash/YAML.rb)。这些接口不等于官方保证本控制器兼容或稳定。
