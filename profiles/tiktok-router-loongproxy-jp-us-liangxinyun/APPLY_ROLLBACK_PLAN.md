# 仅调整良心云的应用与回退方案

**2026-11-24，准备阶段，未应用。** 用户明确要求先核对直连差异，保持TikTok链路和当前直连规则，暂不安装服务。本文件是可审阅的方案及结构草案，不是可导入模块，也不授权启用、重启、测速或控制模式。当前正式入口仍为v1.5.0，完整候选仍为v1.8.1；没有新建或发布运行版本。

## 直连差异与证据边界

已重新读取用户提供的2026-11-23实机调试日志，只比较Manual-Direct的有效payload，未公开原始日志或完整配置。该快照141条；固定仓库提交 `5ae361f2ea6ae9adc06956491476da6c4203ad1b` 的源和v1.8.1完整覆写均148条、逐项一致。原141条在仓库中按原序保留，未发现删除；仓库多出如下7条：

- `DOMAIN-SUFFIX,wyctt.com`
- `DOMAIN-SUFFIX,medeyun.com`
- `DOMAIN-SUFFIX,mede.com`
- `DOMAIN-SUFFIX,gdmd.com`
- `DOMAIN-SUFFIX,os.medeyun.com`
- `DOMAIN-SUFFIX,mede.vip`
- `DOMAIN-SUFFIX,mede.cn`

脱敏结果见[对比记录](DIRECT_DIFF_AUDIT.json)。这是11月23日快照的比较，**不是今天核心内存状态的证明**。本轮不增删任何直连规则，也不刷新现用完整云模块；直接替换v1.8.1完整覆写会带入上述7条，不符合本次保持现状的要求。永久流程A继续保留，今后直连维护仍可正常增删源文件，不受本次历史清单或条数限制。

## 当前唯一设备步骤：只读核对运行路径文件

工具为[liangxinyun_direct_readonly.lua](../../scripts/liangxinyun_direct_readonly.lua)，不带参数。交付时使用固定提交下载并以 `lua -` 执行一次。它只读现有UCI的config_path及运行时覆写config_path，按已核对的OpenClash v0.48.002源码推导 `/etc/openclash/<配置文件名>`，两次读取并比对该文件。路径歧义、特殊YAML、文件变化或缺失时停止，不改用猜测路径。

工具只接受OpenClash已dump的inline／classical Manual-Direct块；这是窄范围文本读取器，不是通用YAML解析器。不输出配置路径、完整规则清单、节点、订阅或凭据；对照结果仅输出固定公开仓库快照中缺少的项，额外的本地规则仅计数。`referenceOnly`表示对照仓库有而文件没有的规则，**不是要求补入**。重复项和原顺序保留比较。

预期有inspectionComplete=true、fileReadTwiceSame=true、readOnly=true；fileWrites／apiRequests／probeRequests均0、selectionApplied和configurationWritten均false。matchesNov23Snapshot=true表示文件payload与11月23日已核实基线逐项同序相同；若false，仅报告差异，不修改或自动重试。runtimeFileSnapshotOnly=true、activeCoreConfigurationVerified=false：它只核对运行路径文件，不能单凭此证明核心内存与文件同步。目标结果待回传。

该诊断内嵌的是上述固定提交的148条公开对照快照；这是诊断参考，不是对动态源的永久条数／清单／哈希门禁。本地132项实际Lua替代接口断言通过，覆盖重复／引号／顺序／额外规则脱敏、非法路径、文件变化及拒绝写入参数；另用真实Lua读取原私有日志，确认141条、仅7条对照差异和原序一致。目标原生UCI／JSON及当前文件结果尚未验证。不需要安装依赖。

## 增量设计草案（仅供后续候选实现）

未来仅在现有同一配置上增加一个**远程增量模块**，放在既有完整云模块上方，使其最后合并。保留原完整模块的本地缓存及唯一的本地凭据模块；不新增第二个完整方案，不增加本地覆写模块，不写UCI插件选项。两处精确目标是名称为良心云的组和键为liangxinyun的提供商。不得直接写 `proxy-groups:` 或 `proxy-groups!:`，二者会替换整个组数组。

以下只是结构草案，**本轮不生成可部署conf、不导入或启用**。落地前须创建高于v1.8.1的新候选，登记增量模块、环境和需求，完成真实合并及差异校验，不能绕过候选／发布门禁。

```ini
[YAML]
proxy-groups*:
  where:
    name: 良心云
  set:
    type: select
    proxies!: [REJECT]
    use!: [liangxinyun]
    include-all-:
    include-all-proxies-:
    include-all-providers-:
    exclude-filter-:
    default-selected: REJECT
    filter: '日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速'
    empty-fallback: REJECT
proxy-providers*:
  where:
    key: liangxinyun
  set:
    filter: '日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速'
    health-check!:
      enable: true
      url: https://www.gstatic.com/generate_204
      expected-status: 204
      interval: 60
      timeout: 5000
      lazy: false
```

名称不存在、重复，或提供商缺失时不补建，应用流程必须停止。提供商的真实URL、认证、path及additional-prefix保留。按最近组快照，允许四档共21个，档外24个；未来应用以当时订阅为准，不把数量写死。检测合同及REJECT仅服务于控制器准备；**此补丁本身不实现四档自动选择**。未启动控制器时可能停在REJECT、导致普通代理中断，不能提前单独启用；启用健康检查也会产生检测流量，本轮不执行。

## 后续应用顺序（本轮不执行）

1. 取得最新实际运行基线及模块顺序。私下保存原模块字节、开关／顺序／完整配置绑定、UCI配置及原手选节点；含凭据的备份只留设备或仓库外。确认文件与核心状态对应，排除计划中的订阅／覆写自动更新，避免操作期间基线变化；本轮不改这些设置。
2. 基于该基线离线合并新候选。允许变化的路径仅为良心云组指定字段及liangxinyun的filter／health-check。rules全部、Manual-Direct逐项与顺序、其他rule-providers、DNS、TikTok两组、本地ISP节点及其dialer-proxy／udp、其他组／提供商、插件选项都必须与基线相同。任何越界差异均停止，不靠总条数判断。
3. 完成真实OpenClash v0.48.002合并、目标核心语法及回退演练；另行安排候选应用和有限的控制模式测试。确认普通代理可能短暂REJECT的维护窗口；本轮不启用服务、不运行控制器。今后如需服务安装／自启，另行安排，不与这次方案准备混为一项。
4. 应用后先只读核对五项阻断已消失、TikTok链路和全部规则与基线一致，再检查四档行为、真实新连接和业务。记录实际结果，不以静态验证代替实机验收。保存对应脱敏调试日志，用户确认前不发布正式版本或改滚动入口。

## 回退顺序（本轮不执行）

1. 若后来已运行控制器，先停止并确认其及监督进程退出，防止继续改组；若后来安装了服务，还须确认不会自动重启。当前没有已安装服务，无须执行停止操作。
2. 停用／撤下本次增量层，恢复应用前保存的原模块本地字节、开关、顺序及配置绑定，不刷新main滚动地址，也不换回带148条规则的现行滚动文件。
3. 按官方模块流程重启OpenClash后，恢复应用前的良心云手选节点。完整rules、Manual-Direct原序、DNS和TikTok链路须与应用前基线逐项一致；若不符，停止后续操作并使用私有备份排查。回退可能短暂中断新连接，不承诺现有连接无感迁移。

## 验证状态与来源

已确认：历史141／148差异及7项清单、旧顺序保留、只读工具本地测试、增量结构的YAML可解析及目标字段范围检查。尚未验证：今天运行路径文件输出、核心内存一致性、新增量模块的真实OpenClash合并、目标应用／回退、完整控制器、procd及长期运行。本轮只交付方案和只读工具，没有写路由器配置。

依据：[官方覆写指南16.2.3条件更新、16.1模块顺序与重启](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)、[OpenClash v0.48.002运行路径及启动命令](https://github.com/vernesong/OpenClash/blob/v0.48.002/luci-app-openclash/root/etc/init.d/openclash#L3454)。
