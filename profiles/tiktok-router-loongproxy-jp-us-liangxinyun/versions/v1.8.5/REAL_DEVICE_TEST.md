# v1.8.5 实机验证与回退门禁

状态：尚未运行。只由用户手动操作，不安装服务或自启。当前v1.8.4旧监督程序尚未确认停止；本文件不是“已经停止”的记录。

1. **保持当前运行状态准备材料**：从VALIDATION.md列出的通过CI提交固定下载本版本控制器、原监督脚本、增量及scripts/liangxinyun_v185_runtime_scope.rb；依BUNDLE.json核对SHA-256，保存到新的私有/root测试目录，不覆盖旧材料。保存操作前完整运行YAML、模块缓存、模块开关/顺序/完整绑定和当前TikTok/良心云选择；备份含秘密，不分享原文。云缓存的Manual-Direct须与当前运行文件逐项同序一致。
2. **只读计划检查**：将before-v185.yaml作为stdin，参数为当前运行YAML、完整云缓存、本版增量缓存，执行配套Ruby工具的--plan。必须passed:true、globalScheduledProbe:false、threeExplicitGroups:true；无API/测速/写文件。额外策略组或定制规则/解析策略导致拒绝时停止，不删配置、不在线试应用。该投影结果还须与离线官方合并验证一致；它不是插件已经合并。
3. **开始维护窗口后停止旧监督**：从旧测试目录真实supervisor.pid读取并验证数字PID，写入该PID对应/tmp/liangxinyun-stop.PID，等待原窗口supervisor-stop、verifiedSelection:true及退出码0；不能用历史硬编码PID，也不能只touch就声称退出。停止可能使普通代理REJECT，随后立即进行已备妥的模块切换或恢复。
4. **只启用本版增量**：在OpenClash运行状态→Overwrite Module创建远程模块，绑定活动配置完整路径；禁用v182/v183/v184等旧增量，保留原完整云和本地凭据模块；新增量在完整云之上、完整云在本地之上。按官方指南重启插件，不用reload代替。新模块URL应固定到已验证提交，禁止混用不同版本脚本与增量。
5. **先核对引用和TikTok手选**：在TIKTOK首跳重新手选操作前同一条iKuuu日本节点；TIKTOK访问检测只显示原ISP。配套Ruby默认模式用before-v185.yaml为stdin读取实际运行YAML/云缓存/增量，必须passed:true且范围保护全部true；记录这是文件快照，非核心全量证明。
6. **启动前检查与临时运行**：本版--preflight应candidateCompatible:true、groupType:Selector、group:良心云-按档位自动切换；随后在原监督脚本下--run，使用新的独立锁/状态文件和stop标记。保持测试会话；不安装服务，不让旧控制器同时运行。
7. **业务验收**：实际API/面板只有TIKTOK首跳、TIKTOK访问检测、良心云-按档位自动切换、GLOBAL。良心云直接展示允许节点，三个业务组不点击人工测速也能刷新历史，首跳手选不变；GLOBAL不单独发起检测，显示共享历史不算失败。检查TikTok页面/播放、普通代理和当前全部直连；核对控制器最高健康档内最低延迟。未实测的全档故障/恢复如实标记，不能冒充通过。
8. **正常停止并恢复原配置**：写新监督PID对应stop标记，确认supervisor-stop及退出码；恢复操作前模块开关/顺序、重启OpenClash，在恢复后的原良心云组手选可用节点，检查原TikTok选择/播放、普通代理和直连。若普通代理仍REJECT或旧控制器未退出，不能认定回退成功；只读核对状态，不反复盲试。
9. **记录结果**：按官方日志指南生成本版对应脱敏调试日志，另记录页面/播放/直连/普通代理及停止回退结果。原始日志和完整配置不得提交Git。用户确认后才按既有授权正式发布；本文件/CI不代替实机验收。

工具文件名和具体命令在实机维护窗口前按通过CI提交、真实路径及当前PID一次性给出；未取得这三项时不使用旧命令拼接。官方依据：[覆写模块16.1](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)、[日志13](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/13-logs.md)。
