# v1.8.3 candidate：面板自动、设置与回退

本候选由 GitHub 分支和 CI 准备，用户电脑与路由器未由助手操作。未安装／启用服务，尚无 v1.8.3 实机结果。正式版本仍 v1.5.0。

## 当前已核对的基线

用户回传 v1.8.2 的预检通过及一次控制成功：选中日本专线02、157ms。随后发现原云模块缓存148条、备份运行配置141条；缓存前后哈希相同，重启后148条生效。按临时固定v1.5.0快照的恢复步骤后，用户回传运行条数141、直连内容及原序一致、良心云允许字段之外全树一致。修改后的完整云缓存哈希未单独回传，下一轮需由缓存重放门禁核对。没有把 v1.8.2 的单次结果当作持续自动、面板或 v1.8.3 验收。

## 文件与结构

`良心云 (URLTest，唯一成员)` → `良心云-严格控制 (Selector，hidden)` → 控制器选出的最高健康档最低延迟叶节点。

规则和 DNS 仍引用原名良心云；TikTok名称及链路不动。外层没有其他候选，不能自行跨档切到其他出口。hidden是否生效、当前叶节点如何展示依赖实际面板，须实测；不要求用户更新面板。自动类型标签不证明控制器正在运行。

- 升级只使用配套远程 `liangxinyun-incremental.conf`，替代v1.8.2增量；它精确更新原良心云并追加一个保留名内部组。
- `liangxinyun-controller.lua` 默认只读。监督脚本沿用旧字节，`.init`仅模板，不复制或安装到设备。
- `openclash-overwrite.conf`为148条完整参考，不用于本轮141条升级；本地模板保留旧字节，不覆盖已填凭据的模块。
- `BUNDLE.json`校验运行文件；`scope_guard.py`／`merge_official.rb`在开发电脑离线使用，不是新路由器依赖。

## 离线应用门禁

工具需要电脑现有 Python／PyYAML 与 Ruby，CatWrt不安装这些依赖。固定官方YAML.rb来自提交e553e82e01c697aefbe1555261a503f425e00ccd，SHA-256为1249abf411e1df9e8fe542fb3584f34a27e6e3a587942e5d9f759a32b1bd8261。

输入必须是当前完整运行YAML、所有相关原模块缓存及真实开关／order／完整路径绑定的清单，放在仓库外私有目录。清单格式、原字节备份与权限说明继承[v1.8.2设置](../v1.8.2/SETUP.md)。新增门禁会重放清单中启用的缓存，再与快照的受保护树比较；任何不一致先停止，不允许拿已过时的141条运行文件配上148条云缓存。示例路径仅供电脑离线操作：

```sh
python scope_guard.py prepare --baseline /private/current.yaml --module-state /private/modules.json --output /private/v183-bundle --openclash-yaml /private/YAML.rb --ruby-command '["ruby"]'
python scope_guard.py verify-bundle --bundle /private/v183-bundle
python scope_guard.py compare --baseline /private/current.yaml --candidate /private/v183-bundle/candidate.yaml
```

工具不联网或自动写设备；原输入、原模块和已有输出不覆盖，私有包含凭据不能上传。它不证明模块清单完整、实际插件顺序或核心内存一致。Windows需使用当前用户专用ACL目录。

## 后续由用户手动应用（本轮不执行）

1. 确认该提交CI通过，保留当前已核对的141条完整云、本地凭据模块、v1.8.2增量及元数据的私有备份；保存当前手选。完整云在本轮使用v1.5.0固定快照，避免重启带入仓库7项。临时固定仅为本轮测试，不改永久流程A/B。
2. 先下载并校验v1.8.3运行文件到隔离临时目录，不安装服务。覆写入口为运行状态页的覆写模块；新建远程增量时绑定同一配置完整路径，初始关闭。旧增量关闭、新增量开启，保留原完整云及已填本地模块；新增量在完整云之上、内建脚本仍第一项。两个增量不能并用。
3. 统一重启OpenClash后先保存新的运行副本，按scope_guard compare核对原规则、DNS、TikTok与凭据。只读预检为 `lua /private-test/liangxinyun-controller.lua --preflight`。必须candidateCompatible:true，外层URLTest且唯一内部成员；不符则撤增量回退。
4. 后续有限测试先执行一次 `--once`，成功后再按用户安排通过 `sh liangxinyun-controller.run lua liangxinyun-controller.lua --run --lock-file ... --state-file ...` 监督运行。前台Ctrl+C要求正常停止并读回内部REJECT；不后台脱管、不安装自启。没有运行控制器时，面板类型仍可能显示自动，不能据此称持续自动已启用。
5. 实测面板自动标签／当前出口可查看、四档内选优／全部失败才降级／恢复／全失败REJECT，TikTok播放、原直连、普通代理新连接及回退。真实延迟和播放由用户提供，不从合成测试推断。v1.8.3脱敏日志与用户验收之前保持candidate。

完整云固定地址（当前141条基线，模块哈希c85392a352914b988e879d12d3dc12ee20f87a6442c5c2abed5070345fbc88b1）：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-liangxinyun-v1.5.0/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.5.0/openclash-overwrite.conf

## 回退

先由原监督脚本正常停止控制器并确认进程已退出、内部组回到REJECT；当前没有服务可停用。关闭v1.8.3增量，恢复已备份的v1.8.2增量开关／顺序／绑定，保留141条固定云及原本地模块，重启OpenClash后恢复原良心云手选。若使用离线备份包，restore-copy只在候选未漂移时生成原字节副本：

```sh
python scope_guard.py restore-copy --bundle /private/v183-bundle --current /private/current-v183.yaml --output /private/restored.yaml
```

原最早before.tgz里的云缓存是148条，因此**不能整包还原该缓存后重启来恢复141条**。回退须用修复后的141条完整云基线。不要刷新main替代回退，也不删除仓库源中的那7项。

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

