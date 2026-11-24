# v1.8.2 candidate：本地准备、OpenClash设置与回退

**未部署。** 本轮不接触CatWrt、不安装／启用服务。先使用现有配置的完整离线副本完成范围检查；下一次实机应用另行安排。设备最近运行路径快照141条直连，仓库完整参考148条，不替换原完整云模块、不刷新滚动地址。

## 文件与入口

| 文件 | 用途 |
| --- | --- |
| liangxinyun-incremental.conf | 本次升级的配套远程增量层，仅良心云；未来放在现有完整云模块上方，最后合并，初始关闭 |
| liangxinyun-controller.lua | Lua5.1控制器；默认／--preflight只读，--dry-run只模拟，显式--once／--run才控制 |
| liangxinyun-controller.run／.init | 停止监督与procd模板；本轮只交付，不安装或启用 |
| scope_guard.py／merge_official.rb | 开发电脑离线范围检查及备份／回退副本工具，不运行于路由器 |
| openclash-overwrite.conf | 148条完整参考快照；本次保持141条的升级不得启用它 |
| local-tiktok-proxy.conf | 沿用稳定版占位模板；保留现有已填凭据模块，本轮不替换 |
| BUNDLE.json | 公共候选文件SHA-256清单，无真实配置／凭据 |

仍只启用一个完整方案和唯一的本地模块 `tiktok-router-loongproxy`，增量是远程配套层。不得将候选服务复制进设备或提前单独启用增量：无控制器时普通代理可能停在REJECT。健康检查会产生检测流量。

## 离线准备与范围检查

工具需要电脑本地Python＋PyYAML、Ruby3.3及固定官方YAML.rb；不在CatWrt装依赖。官方源码必须来自提交 `e553e82e01c697aefbe1555261a503f425e00ccd`，SHA-256为 `1249abf411e1df9e8fe542fb3584f34a27e6e3a587942e5d9f759a32b1bd8261`。

未来准备输入：完整当前运行YAML副本（含原ISP与提供商定义）及所有启用／相关模块的原文件副本，放在仓库外私有目录。现有历史日志缺少两项定义，不能补占位后用于真实应用。模块清单也在仓库外，结构为下方**虚构示例**；file为电脑本地副本路径，config为原模块绑定的完整路径，order／enabled／sourceType／selection必须填实际值，不能照抄示例：

```json
{"schemaVersion":1,"configBinding":"/etc/openclash/config/example.yaml","selection":"LXY: 日本专线02","modules":[{"id":"cloud","file":"/private/cloud.conf","enabled":true,"order":1,"config":"/etc/openclash/config/example.yaml","sourceType":"http"},{"id":"tiktok-router-loongproxy","file":"/private/local.conf","enabled":true,"order":2,"config":"/etc/openclash/config/example.yaml","sourceType":"file"}]}
```

所有命令仅在电脑离线执行，目录参数为虚构示例；候选目录下运行：

```sh
python scope_guard.py prepare --baseline /private/current.yaml --module-state /private/modules.json --output /private/new-bundle --openclash-yaml /private/YAML.rb --ruby-command '["ruby"]'
python scope_guard.py verify-bundle --bundle /private/new-bundle
python scope_guard.py compare --baseline /private/current.yaml --candidate /private/new-bundle/candidate.yaml
```

工具要求目标目录不存在、在Git仓库外；原文件只读，逐文件备份／哈希并最后写manifest。POSIX系统目录0700／文件0600；Windows应使用仅当前用户可访问的私有目录，POSIX权限参数不等于Windows ACL保证。备份含真实凭据，不上传仓库、不粘贴输出文件。成功只表示离线合并范围符合合同；任何失败停止，不生成可应用的成功报告。部分失败目录保留供本地检查，不自动删除或重用。

准备后的YAML是离线预览，**不得直接覆盖路由器运行配置**。未来实际OpenClash合并结果仍须另存并再次compare；新增未知字段、基线漂移或模块顺序不同都可能被拒绝。该工具不验证导出的模块清单是否覆盖了设备全部配置，不替代实际核心状态和插件注册核对。

## 后续应用门禁（本轮不执行）

1. 私下保存完整当前基线、全部原模块缓存／开关／顺序／绑定／UCI备份与原良心云手选，确认文件对应核心。核对操作期间无订阅／覆写更新竞争；不使用已过时日志冒充当前输入。
2. 校验公共候选哈希、离线范围检查及备份包。真实模块顺序按OpenClash官方规则：界面越靠上越晚合并；增量位于原完整云模块上方，原本地凭据模块保持。当前实际顺序尚未验证。
3. 另行安排有限维护窗口中的增量应用和控制器前台测试；核对候选五项配置合同、完整规则、TikTok及直连后再测自动选择。服务安装／自启属于后续阶段，不与本轮本地准备混合。
4. 实机覆盖逐档故障／恢复、普通新连接出口、TikTok打开播放、直连样例和回退；取得对应脱敏日志与用户确认前保持candidate，滚动入口仍v1.5.0。

## 回退

离线演练仅生成原始配置副本，不写设备；当前文件结构必须仍与包内候选一致，漂移则停止重新核对：

```sh
python scope_guard.py restore-copy --bundle /private/new-bundle --current /private/new-bundle/candidate.yaml --output /private/original-restored.yaml
```

原始注释、换行和字节保持；备份的模块字节／开关／顺序／绑定／原手选可从包内原清单读取，工具不执行其路径或自动修改插件。已有输出拒绝覆盖。正式设备回退必须按顺序：先确认控制器及监督已退出、procd不会重启；撤掉增量；恢复包内原模块缓存和原开关／顺序／绑定（必要时原UCI备份）；重启OpenClash；恢复原良心云手选；检查TikTok和全部原规则。**不能刷新main滚动地址充当回退**，否则会带入另7条直连更新。未安装服务的当前设备无须停止／禁用任何服务。

## OpenClash 独立手工设置

沿用v1.5.0实机值，本候选不改插件设置。目标记录为OpenClash0.48.002／alpha-gbc76c13／CatWrt24.10.2 x86_64；v1.8.2完整运行尚未实机验收。以下路径在「服务 → OpenClash」下，供新装／恢复设置参考：

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
