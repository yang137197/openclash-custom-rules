# 候选配置的只读差异核对

**2026-11-24只读核对已完成，当前配置不兼容候选控制合同。** 用户回传交付提交 `01ee585cab50c31e016a6e9a0b4a40caeb11f7fb` 的结果：inspectionComplete=true、snapshotConsistent=true、contractChecksAgree=true，核心alpha-gbc76c13；API请求4、测速请求0、selectionApplied=false、configurationWritten=false、formalAcceptance=false。本次未切换或写配置，不自动重测。

确认组和提供商各45个节点，其中四档共21个（日本专线4、日本高速5、美国流媒体7、美国高速5），各有24个档外节点。当前选择在两次读取间一致，节点来源检查通过、wrongSourceNodes=0。五项不符为：REJECT不在首项、组含档外节点、提供商含档外节点、testUrl不符、expectedStatus不符；expectedStatusType为string，不能据此知道实际字符串内容。首个拒绝原因为candidate-selector-required。此结果说明运行配置不满足候选条件，不证明CatWrt不兼容，也未检测节点健康或自动切换。

停止监督单项完成后，用户要求“下一步”，本工具用于解释此前只有candidateCompatible=false的结果。已完成的锁、状态、停止监督及本次差异核对均不自动重测；服务与完整控制模式仍未运行。

`liangxinyun_candidate_readonly.lua` 不带参数执行。它从现有UCI只读取得本机端口和认证，由单独Lua子进程将认证送到curl标准输入，不输出密钥、不放进curl参数。curl禁用curlrc、环境代理和重定向，仅访问 `127.0.0.1`。没有临时文件、锁、状态发布、安装或自启行为。

只发出四次GET，顺序为 `/version` → `/proxies/良心云`（URL编码）→ `/providers/proxies/liangxinyun` → `/proxies/良心云`。路径是固定白名单，不允许 `/healthcheck`、`/delay`、配置或连接管理接口；无PUT／POST／PATCH／DELETE。尤其GET健康检测接口也会触发测速，本诊断明确排除。它不主动触发检测、订阅更新或节点切换；无法阻止既有服务自行检测、用户手选或订阅更新，并发变化会使本次快照核对不通过。

诊断复制v1.8.1的名称分档、快照及兼容合同，测试逐段比较原文，未改完整控制器。输出包括 `candidateCompatible`、`firstRejection`、`blockingReasons`、`checks`、四档节点数量及档外节点数量，逐项核对：

- 组类型、成员、当前选择与提供商是否相符，两次组读取是否一致。
- REJECT是否位于组首；组和提供商是否仅含四类允许节点。
- 节点来源是否匹配；提供商检测URL是否为固定HTTPS204地址、expectedStatus是否为字符串204。

不输出节点名、实际选择名、其他字段、任意检测URL或API原始响应。`coreVersion`仅接受有限长度的版本字符，错误仅输出白名单代码；认证和非公开URL不回传。

成功完成核对时 `inspectionComplete:true`、`readOnly:true`、`apiRequests:4`、`probeRequests:0`、`selectionApplied:false`、`configurationWritten:false`、`formalAcceptance:false`。`candidateCompatible:false`本身不是本次核对失败：它表示当前配置不能交给候选控制器，将由原因列表解释。若快照不一致、接口错误或JSON错误，`inspectionComplete:false`且退出非0，不自动重试。请回传完整JSON，不粘贴UCI认证或完整API响应。

本地101项实际Lua断言通过，覆盖兼容／不兼容合同、与候选一致性、45节点／24档外的合成旧配置、数值204与字符串204区别、快照变化、非法输入和路径拒绝。8个实际Lua／curl／回环HTTP场景通过，包括兼容、旧配置、自定义URL脱敏、重定向、401、错误JSON、禁止控制参数及非法端口；JSON／UCI由本地替代模块提供，不作为目标原生结果。

它只检查配置形状，不检测节点健康、选择最低延迟、验证TikTok播放／直连、生产路径权限、procd或完整控制器稳定性。正式入口仍为v1.5.0，TikTok链路和直连源不变；设备141条与候选148条的既有差异尚未部署。

依据：[OpenClash指南15-api.md §15.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/15-api.md)、[Mihomo提供商GET及健康检测实现](https://github.com/MetaCubeX/mihomo/blob/Alpha/hub/route/provider.go)。独立诊断不属于OpenClash内置功能。
