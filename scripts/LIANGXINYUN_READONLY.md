# 良心云 Lua 单次只读决策模拟

2026-11-23，关联 `tiktok-router-loongproxy-jp-us-liangxinyun` 的 L19–L22 候选准备。工具为 [liangxinyun_readonly.lua](liangxinyun_readonly.lua)，**不是自动控制服务，也不替换 v1.7.0 目录中的 Ruby 控制器**。当前正式方案仍为 v1.5.0。

## 操作边界

复用路由器已有 Lua 5.1、`luci.jsonc`、`luci.model.uci`、`nixio` 和 curl。只读 UCI 中现有 API 端口／密钥，依次 GET 本机回环 API 的 `/version`、`/proxies/良心云`、`/providers/proxies/liangxinyun`，再读一次良心云组检查成员与手选值是否变化。成员须与该 provider 完全对应（可额外包含 REJECT），否则停止分析。

不调用健康检查、延迟测试、订阅更新、组选择或连接清理接口；没有 apply 模式、后台循环、文件写入、安装器、服务启用和配置更新。TikTok、直连、DNS 和插件选项不在写入范围内。当前运行的 141 条直连与仓库 148 条的差异不在本次处理。

密钥由子进程读取，经标准输入交给 curl，不放入命令行参数、结果或日志。curl 禁用默认配置、环境代理与重定向；只允许固定的本机 GET 路径。自定义测试 URL **仅用作已有记录的查找键**，不会请求该地址；输出中遮蔽自定义 URL，避免回传私有参数。

## 执行与结果

对已取得的同一份脚本，仅运行一次：

```sh
lua liangxinyun_readonly.lua
```

远程执行必须使用维护者提供的完整提交 SHA 固定地址，不能将随时变化的分支地址当作固定代码。无需刷新覆写、重启 OpenClash、安装依赖或手动测速。正常结果是一行 JSON；没有输出或有 `error` 均不算通过。

- `readOnly: true`、`selectionApplied: false`：这次只模拟，没有切换。`currentSelection` 是读取时的现行手选值。
- `recommendation.tiers`：四档各自的节点数量、健康／失败／未知数量及未知原因。仅纳入该 provider 的 `LXY: ` 节点；美国流媒体兼容“美国05|流媒体”等非相邻名称。
- `recommendation.wouldSelect`：按日本专线 → 日本高速 → 美国流媒体 → 美国高速，选择最高可用档内**最近有效记录**延迟最低的节点；同延迟优先保留当前节点。同档还有健康节点时继续留档；高档无健康但有未知时不能降级。
- `wouldSelect: REJECT`：模拟认为应停止选择，**不影响现有流量**，也不向现行手选组添加 REJECT。高档记录未知与四档全部失败分别给出不同 `reason`。
- `observedTestUrls`：符合四档名称的节点有哪些非空 URL 历史及覆盖数量，不代表记录有效或当前节点健康。
- `jsonUrlArraySelfTest: true`：当前 JSON 模块对合成的转义 URL 键、布尔值和从 1 开始的历史数组自检通过；失败会在 API 查询前停止。
- `historyDiagnostics`：分别统计全部 provider 节点与四档节点的全局历史、空／缺失 extra、URL 状态及空／缺失／非空历史。不输出自定义字段名或 URL。可区分“默认 URL 不匹配”和“没有任何非空逐 URL 历史”；不能用全局记录代替后者。
- `providerHealthContractMatches`：提供商元数据是否恰好声明选定 URL 和预期 204；不是一次 HTTP 204 实测。为 false 时结果带 `warning`，只能作为待核对的模拟建议，不能据此启用自动切换。
- `formalAcceptance: false`：不表示完整控制器已兼容或实机验收通过。

默认查找 `https://www.gstatic.com/generate_204`，不从空的 provider `testUrl` 猜测测试地址。只使用此键下 `extra` 的最后一条记录，不能用全局 `history` 或其他 URL 替代。记录超过 130 秒、未来超过 5 秒、无有效时间戳或状态／延迟不一致都记为未知；`alive=false` 且 `delay=0` 才是明确失败。健康为 `alive=true` 且整数延迟 1–65534 ms。时间按 RFC3339 时区解析，避免路由器本地时区偏差。

可用参数为 `--test-url URL`（仅改变查找键）、`--max-age SECONDS`（1–3600，默认 130）和 `--help`。本阶段不通过放宽时限把旧记录当成当前健康；应先回传默认输出核对实际 URL 与新鲜度。不要回传 API secret、订阅或原始 provider 响应。

## 本地验证及边界

已使用独立解包、未安装到系统路径的 Lua 5.1.5 和现有 curl，在 WSL Ubuntu 执行：

```sh
python3 scripts/verify_liangxinyun_readonly.py --lua /absolute/path/to/lua5.1
```

- 336 项真实 Lua 5.1 策略断言：256 种四档各两节点存活组合、未知／过期／未来记录、UTC／偏移时区、来源、名称、同延迟、读取边界、结构计数及拒绝不兼容 JSON 数组。
- 16 个实际 Lua＋curl／本地 HTTP 场景：原 14 项覆盖旧方案空 `testUrl`、元数据匹配、同档未知、整档降级、过期阻止降级、全失败、URL 遮蔽、401、302 不跟随、无效 JSON、选择变化、成员变化、端口拒绝和禁止 apply；另加 21 个四档节点无 URL 历史但其余 24 节点有历史、JSON 结构自检失败时零 API 请求。捕获的请求均为固定 GET；合成密钥含引号和反斜杠，认证成功且不进入 curl 参数或输出。

HTTP 夹具使用合成数据，替代 UCI、时间和 JSON 模块。JSON 输入适配器将预定义响应映射为 Lua 表，不是目标 `luci.jsonc` 的实现验证；目标设备基础 JSON 解析已由用户单独确认。本地测试没有真实机场线路或设备连接，不证明 TikTok 播放、完整自动控制或长时间稳定性。

2026-11-23，用户已执行提交 df02abf 的第一版只读模拟：45 个 provider 节点，四档计数分别为 4／5／7／5，共 21 个；其余 24 个仅在模拟中忽略，实际组仍为 45 个。21 个节点均未命中默认 URL 记录，`observedTestUrls` 为空，建议为未知高档阻止降级的 REJECT；`selectionApplied=false`，当前手选未改变。**这不证明 21 个节点超时。**

随后提交 8cf2778 的增强工具也已在设备执行：JSON URL／数组自检通过，45 个节点（含四档 21 个）的 extra 全为空表，普通历史和逐 URL 历史非空计数均为 0，未发现缺失／非表 extra 或异常状态。这次确认是采样时没有检测数据，不是单纯测试地址不匹配；与更早历史摘要的差异原因尚未确定。只读预检完成，不需反复执行本工具等待其生成样本。用户随后单独允许仅检测当前日本专线 01 一次，使用[另一份单节点工具](LIANGXINYUN_PROBE_ONE.md)，实机结果待回传；本只读工具仍没有任何检测接口。完整控制器仍未验收。

接口依据：[OpenClash 官方 API 指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/15-api.md)、[目标 Mihomo 提交的逐 URL 状态](https://github.com/MetaCubeX/mihomo/blob/bc76c1398c6e70089367a30169d0df7c7f77c42d/adapter/adapter.go)。
