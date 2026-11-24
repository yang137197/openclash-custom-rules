# v1.8.3 candidate：部署、设置与回退

本候选的GitHub CI已经通过，验证依据见[VALIDATION.md](VALIDATION.md)。本轮按用户要求统一交付代码和仓库说明，停止逐步引导路由器操作。实际面板、CatWrt持续运行及回退尚未完成验证，服务未安装，正式稳定版仍v1.5.0。

## 直连以仓库唯一源为准

`rules/manual-direct.yaml`是唯一维护源，保留用户手动添加的全部规则。当前源为148条，仅表示本次快照；未来可按永久流程A任意增删有效条目，不锁定141或148，也不删除用户新增的7条。

正常规则维护仍为：修改源 → main上的同步工作流生成滚动模块及哈希 → 用户更新同一个远程完整云模块并重启OpenClash。规则数据维护不创建候选或Release，不要求重复做代理链路验收。良心云滚动地址：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/overwrite/openclash-overwrite.conf

此前141条固定快照、缓存／运行比对及备份是该次临时验证的历史记录，不是发布限制、长期部署地址或本轮新增工作要求。缓存已更新、运行尚未重启的直连差异，应先核对是否属于维护者已授权的源更新，并按正常流程使预期规则生效；不要默认恢复141条或删改源。

## 自动选择结构与文件

公开`良心云`为URLTest，只引用内部`良心云-严格控制`Selector。控制器在内部执行日本专线 → 日本高速 → 美国流媒体 → 美国高速严格顺序，档内最低有效延迟；未知高档阻止降级，全失败REJECT。TikTok仍为手选iKuuu日本Z01–Z04 → 原Loongproxy美国SOCKS5，其他规则、DNS与凭据模块沿用。

| 文件 | 用途 |
| --- | --- |
| liangxinyun-incremental.conf | 现有配置的远程配套增量，仅修改良心云并追加一个内部组 |
| liangxinyun-controller.lua | 默认只读预检；--once单次、--run持续控制 |
| liangxinyun-controller.run | 持续模式的停止监督脚本 |
| liangxinyun-controller.init | procd模板，未安装或启用 |
| openclash-overwrite.conf | 依据当前源的148条完整参考快照；现有配置升级使用增量 |
| local-tiktok-proxy.conf | 唯一的本地凭据占位模板，保留已填好的原模块 |
| scope_guard.py／merge_official.rb／BUNDLE.json | 离线范围、备份回退与文件完整性检查 |

面板hidden支持及当前出口的展示方式依实际前端，仍需实测。URLTest的“自动”类型标签不证明控制器正在持续运行；--once结束后不会继续自动切换。持续控制需要控制器常驻，不把本候选代码交付当作已安装服务。

## 部署说明

现有配置只替换对应增量与控制器；原完整云继续使用上面的滚动地址，本地凭据模块保留。新旧增量不能并用。按[官方模块指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)添加远程增量，绑定同一配置的完整路径；增量放在完整云上方，内建脚本仍第一项。模块更改须统一重启OpenClash。

候选配套增量地址（随候选目录维护；正式发布后以标签固定链接为准）：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.3/liangxinyun-incremental.conf

应用前保存当时有效配置、模块、顺序和原手选。核对BUNDLE的SHA-256；准备包工具仅在电脑离线使用，CatWrt不安装Python/Ruby依赖。官方合并实现固定至e553e82e01c697aefbe1555261a503f425e00ccd，哈希1249abf411e1df9e8fe542fb3584f34a27e6e3a587942e5d9f759a32b1bd8261。工具输入为当前完整运行副本与启用模块缓存及元数据；保留任意合法直连数量、原序和重复项，先核对已授权的源更新，再以一致的预期基线检查代理增量范围。工具不会验证清单完整性或核心内存，也不会自动写路由器。

应用后的--preflight必须candidateCompatible:true，随后单次控制与有限持续测试按一次完整维护窗口安排。既有Lua、curl、锁、状态文件及停止监督单项已经完成，不重复要求安装依赖、单节点授权或碎片化验收。正式版仍需本候选面板、四档故障／恢复、正常停止／回退、TikTok播放、直连与普通代理的对应实机证据；已有CI和v1.8.2结果不冒充v1.8.3实机记录。

## 回退

由监督脚本正常停止控制器并确认退出，撤掉本次增量，恢复操作前备份的模块开关／顺序／绑定与控制器版本，重启OpenClash并恢复原手选。直连按操作前已确认的预期规则集恢复；源更新不回滚，141不是固定恢复目标。离线restore-copy只生成原字节副本，当前候选漂移时停止；不能将较早备份中的云缓存内容误认为当时实际生效规则。

真实订阅、代理凭据与完整备份只在用户本地，不能上传GitHub。API不可用、强杀、掉电或核心重载竞争窗口可能保留旧选择，正常停止清理属于尽力行为；不承诺瞬时失败关闭或旧连接迁移。

## OpenClash 独立手工设置

沿用v1.5.0实机值，本候选不改插件设置。目标记录为OpenClash0.48.002／alpha-gbc76c13／CatWrt24.10.2 x86_64；v1.8.3完整运行尚未实机验收。以下路径在「服务 → OpenClash」下，供新装／恢复设置参考：

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
