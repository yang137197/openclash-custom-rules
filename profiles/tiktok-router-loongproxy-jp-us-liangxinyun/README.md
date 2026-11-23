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

[v1.7.0 独立控制器](versions/v1.7.0/REQUIREMENTS.md)：用户选择保持严格顺序，控制器直接按叶节点健康状态与延迟自动管理良心云。Ruby 实现完成本地策略与真实核心夹具验证，但目标所需库加载失败，暂不部署。Lua＋curl 只读预检已完成，四档共 21 个节点；01 的单次实机检测已读回超时记录，保持 02 手选不变。02 同条件对照另获授权、待执行，实际最低延迟选择及完整控制器仍未实机验收。

- [v1.7.0 设置、预检与回退](versions/v1.7.0/SETUP.md)
- [v1.7.0 环境记录](versions/v1.7.0/ENVIRONMENT.json)
- [v1.7.0 本地验证](versions/v1.7.0/VALIDATION.md)
- [Lua 基础预检记录](versions/v1.7.0/READ_ONLY_PREFLIGHT.md)
- [单次 Lua 只读模拟工具](../../scripts/LIANGXINYUN_READONLY.md)
- [单节点检测工具（01 超时，02 对照待执行）](../../scripts/LIANGXINYUN_PROBE_ONE.md)

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
