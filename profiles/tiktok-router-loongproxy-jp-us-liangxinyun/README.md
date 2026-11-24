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

[v1.8.0 Lua＋curl 完整控制器](versions/v1.8.0/REQUIREMENTS.md)：延续四档严格优先级，使用现有 Lua 5.1、LuCI JSON／UCI、nixio 和 curl；默认只读预检，另有 Shell 停止监督和 procd 模板。2026-11-24完整脚本基础只读预检已完成，当前02手选未变；下一步为用户已授权的一次[独立原生锁测试](../../scripts/LIANGXINYUN_NATIVE_LOCK.md)。不安装／启用路由器服务，不改TikTok或直连；完整候选未验收。

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
