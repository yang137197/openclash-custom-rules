# v1.8.5 candidate：四组、三组检测与安全迁移

本版本需求以[需求合同](REQUIREMENTS.md)和[本版本开发规则](DEVELOPMENT_RULES.md)为准。正式版仍v1.5.0；本候选未实机验收。不操作用户电脑或路由器，不安装服务。

## 四组及检测

| 策略组 | 选择方式 | 自动检测内容 |
| --- | --- | --- |
| TIKTOK首跳 | 手选iKuuu日本Z01–Z04 | 各首跳节点延迟/可达性 |
| TIKTOK访问检测 | 固定现有Loongproxy美国出口 | 经手选日本首跳的完整链路 |
| 良心云-按档位自动切换 | 控制器严格四档自动选择 | 四档实际节点健康和延迟 |
| GLOBAL | 保留手动选择全局出口 | **不做检测** |

前三组和良心云provider为60秒、5000毫秒、期望204、lazy:false，URL https://www.gstatic.com/generate_204。select也能定时检测；自动测速不等于自动换节点。检测成功不代替TikTok播放验收，GLOBAL共享显示的成员历史不表示它发起了检测。

良心云直接展示允许的实际节点，仍由独立控制器按日本专线→日本高速→美国流媒体→美国高速选择，档内最低有效延迟，未知不当失败。原版面板按Selector显示“手动选择”可能仍存在，本轮不做面板适配、不改TikTok组类型或GLOBAL模式来美化标签。

## 应用边界

升级仍用单独远程增量，完整openclash-overwrite.conf只作参考，不用它覆盖设备的全部配置或直连规则。真实凭据本地模块保留；补丁仅修改ISP dialer-proxy引用名称，不改其其他字段。新安装模板已使用TIKTOK首跳。当前滚动完整云及手动直连源在候选阶段不改。

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/overwrite/openclash-overwrite.conf

固定补丁包含三个目标组、原方案规则及DNS策略的名称迁移。应用前必须用配套Ruby YAML只读--plan检查完整配置；有额外策略组或自定义规则/DNS策略时拒绝，不强行覆盖。应用后范围检查同时拒绝旧名称残留、规则优先级或真实链路变化。直连按当前源全部保留，不能以历史141条回退。

## 实机迁移与回退

详见[REAL_DEVICE_TEST.md](REAL_DEVICE_TEST.md)。当前v1.8.4未确认停止：准备阶段不触碰它。进入用户维护窗口后，先正常停止旧监督程序并核对退出，再关闭旧增量、启用经校验的本版增量并重启OpenClash。原完整云和已填凭据模块保持。

三个新组名中的TikTok大小写改变可能使原手选缓存无法继承；重启后先在TIKTOK首跳中手选操作前同一条iKuuu日本节点，再核对TIKTOK访问检测只有TikTok-ISP-Local。本版控制器--preflight必须兼容，再由监督脚本临时运行，不安装服务。

停止新控制器会尽力把良心云设为REJECT，普通代理会暂时不可用。恢复日常配置须恢复原模块开关/顺序并重启，随后在原良心云组手选可用节点、检查原TikTok首跳及播放/直连。只停止或只重启不算回退完成。不要在旧/新控制器仍运行时交叉启用两个版本。

## 检查工具

- scope_guard.py：仅电脑离线工具，用已有Ruby加载固定官方合并；检查全树差异并准备原始字节备份/回退副本，不连接路由器。
- scripts/liangxinyun_v185_runtime_scope.rb：目标只需原生Ruby YAML；--plan仅投影固定补丁并验证范围，默认模式核对实际运行文件；两者API/测速/写文件均为0，不证明核心内存全量一致。
- liangxinyun-controller.lua：默认只读--preflight；--once会检测并选择一次，持续自动必须经原监督脚本--run。只写唯一良心云组，正常停止REJECT。

## OpenClash 独立手工设置


沿用v1.5.0实机值，本候选不改插件设置。目标记录为OpenClash0.48.002／alpha-gbc76c13／CatWrt24.10.2 x86_64；v1.8.5尚未实机运行，环境来自2026-11-25的v1.8.3日志。以下路径在「服务 → OpenClash」下，供新装／恢复设置参考：

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

依据：[OpenClash覆写16.1/16.2.3](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)、[API15.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/15-api.md)、[Mihomo组解析源码](https://github.com/MetaCubeX/mihomo/blob/v1.19.34/adapter/outboundgroup/parser.go)。这些接口支持不代表官方对自定义控制器作兼容或稳定保证。
