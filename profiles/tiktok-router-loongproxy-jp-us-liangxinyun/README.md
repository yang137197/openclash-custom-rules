# tiktok-router-loongproxy-jp-us-liangxinyun

**v1.5.0 stable**，用户于 2026-11-16 确认实机验收通过。TikTok 首跳手选 iKuuu 日本 Z01–Z04，使用 Loongproxy 美国出口。Claude 和其余代理流量走良心云，沿用现有直连规则。

- [需求合同](versions/v1.5.0/REQUIREMENTS.md)
- [部署、设置与回退](versions/v1.5.0/SETUP.md)
- [环境记录](versions/v1.5.0/ENVIRONMENT.json)
- [本地模块占位模板](versions/v1.5.0/local-tiktok-proxy.conf)
- [v1.5.0 Release](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-liangxinyun-v1.5.0)
- [标签固定覆写](https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-liangxinyun-v1.5.0/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.5.0/openclash-overwrite.conf)
- [滚动远程覆写](https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/overwrite/openclash-overwrite.conf)

## 当前候选（candidate）

[v1.8.1 权限兼容修正](versions/v1.8.1/REQUIREMENTS.md)：修正v1.8.0中nixio.open不合法的数值权限参数384，改为 `rw-------`。只改两处权限实参，选路和覆写有效YAML不变；旧运行文件保留，v1.8.0暂不部署。用户要求继续隔离状态文件写入与替换测试，该单次测试已成功回传，权限、正常替换、读回与清理通过，授权已结束；不接入API、不安装／启用服务。

[停止监督脚本离线测试](../../scripts/LIANGXINYUN_SUPERVISOR_OFFLINE.md)已于2026-11-24收到目标成功回传：仅运行原监督脚本与合成worker，immediate／delayed两项均正常停止、回收并清理，监督退出码0，未使用强制清理；API／测速请求0、选择未应用、正式验收false。该单项已完成，不重测；本地372项替代接口断言、8项实际Shell／Lua／源文件场景另行通过。TikTok、直连和正式入口不变，未安装或启用服务。

[候选配置只读差异核对](../../scripts/LIANGXINYUN_CANDIDATE_READONLY.md)已收到2026-11-24目标回传：快照与来源检查通过，45节点中允许四档共21个、档外24个；REJECT非首项、组／提供商含档外节点、检测URL与预期状态码不符，共五项导致candidateCompatible=false。本项已完成，API请求4、测速0、未切换或写配置，不安装服务。完整控制器仍未运行；本地101项Lua断言及8项HTTP场景另行通过。

- [v1.8.1 设置与单项验证](versions/v1.8.1/SETUP.md)
- [v1.8.1 环境与证据边界](versions/v1.8.1/ENVIRONMENT.json)
- [v1.8.1 本地验证](versions/v1.8.1/VALIDATION.md)

[仅良心云的应用与回退方案](APPLY_ROLLBACK_PLAN.md)已准备，当前不应用、不安装服务。历史141／148条已复核为仅7条仓库新增、原序保留；增量结构只精确匹配良心云，避免带入直连更新和TikTok变化。最新运行路径文件输出待只读确认，结构草案尚非可部署模块，未来须更高候选。

## v1.8.0 已知权限缺陷（candidate）

[v1.8.0 Lua＋curl 完整控制器](versions/v1.8.0/REQUIREMENTS.md)：延续四档严格优先级，使用现有 Lua 5.1、LuCI JSON／UCI、nixio 和 curl；默认只读预检，另有 Shell 停止监督和 procd 模板。2026-11-24完整脚本基础只读预检已完成，当前02手选未变；随后获授权的一次[独立原生锁测试](../../scripts/LIANGXINYUN_NATIVE_LOCK.md)已成功回传，授权已完成；状态写入和服务启停仍待验证。不安装／启用路由器服务，不改TikTok或直连；完整候选未验收。

- [v1.8.0 设置、只读预检与回退](versions/v1.8.0/SETUP.md)
- [v1.8.0 环境与证据边界](versions/v1.8.0/ENVIRONMENT.json)
- [v1.8.0 本地验证](versions/v1.8.0/VALIDATION.md)

## 先前候选（candidate）

[v1.7.0 独立控制器](versions/v1.7.0/REQUIREMENTS.md)：用户选择保持严格顺序，控制器直接按叶节点健康状态与延迟自动管理良心云。Ruby 实现完成本地策略与真实核心夹具验证，但目标所需库加载失败，暂不部署。Lua＋curl 只读预检和两个单次步骤已完成：01 超时、02 对同目标检测成功且为 159 ms，历史读回及 02 手选保持已验证。完整 Lua 控制器尚待实现，自动选优及长期运行未验收。

- [v1.7.0 设置、预检与回退](versions/v1.7.0/SETUP.md)
- [v1.7.0 环境记录](versions/v1.7.0/ENVIRONMENT.json)
- [v1.7.0 本地验证](versions/v1.7.0/VALIDATION.md)
- [Lua 基础预检记录](versions/v1.7.0/READ_ONLY_PREFLIGHT.md)
- [单次 Lua 只读模拟工具](../../scripts/LIANGXINYUN_READONLY.md)
- [单节点诊断记录（01 超时，02 为 159 ms，两项均完成）](../../scripts/LIANGXINYUN_PROBE_ONE.md)

[v1.6.0 分层自动选择](versions/v1.6.0/REQUIREMENTS.md)：四个 url-test 配合 fallback 的候选组合。本地已复现同档部分故障时短暂提前降级，尚未严格满足需求，暂不部署；稳定入口仍为 v1.5.0。

- [候选部署、设置与回退](versions/v1.6.0/SETUP.md)
- [候选环境记录](versions/v1.6.0/ENVIRONMENT.json)
- [候选验证与已知问题](versions/v1.6.0/VALIDATION.md)

## 历史候选（candidate）

[v1.0.0 历史候选](versions/v1.0.0/REQUIREMENTS.md)仅分流 YouTube 和 Telegram。

[v1.1.0 历史候选](versions/v1.1.0/REQUIREMENTS.md)增加良心云默认代理。

[v1.1.1 历史候选](versions/v1.1.1/REQUIREMENTS.md)修复提供商覆写合并。

[v1.2.0 历史候选](versions/v1.2.0/REQUIREMENTS.md)引入手选美国首跳。

[v1.2.1 历史候选](versions/v1.2.1/REQUIREMENTS.md)修复美国节点的旗帜前缀匹配。

[v1.3.0 历史候选](versions/v1.3.0/REQUIREMENTS.md)用于 iKuuu 美国与日本首跳对照。

[v1.4.0 历史候选](versions/v1.4.0/REQUIREMENTS.md)用于良心云首跳对照，未通过实机验收。
