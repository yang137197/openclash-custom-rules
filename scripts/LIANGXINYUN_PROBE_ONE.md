# 良心云单节点检测

2026-11-23，用户已明确允许：仅对当前良心云日本专线 01 做一次 HTTPS 204 延迟检测，超时 5 秒，再读取新历史。不切换节点、不安装依赖或启用服务，TikTok 链路和直连规则不变。本工具属于 L20–L22 的独立诊断准备，不是 v1.7.0 控制器的部署或验收。

工具：[liangxinyun_probe_one.lua](liangxinyun_probe_one.lua)。与[只读模拟工具](LIANGXINYUN_READONLY.md)分开；原只读程序没有加入检测接口。

## 固定范围

- 只连接 UCI 现有端口的 `127.0.0.1`；凭据由子 Lua 读取后经管道交给 curl，不进入参数或输出。
- 核心须仍为 `alpha-gbc76c13`，当前 `良心云` 须仍手选精确名 `LXY: 🇯🇵日本专线01|BGP|流媒体`，该节点须在 `liangxinyun` provider 中。选择或成员在检测前变化时停止。
- 固定目标 `https://www.gstatic.com/generate_204`，请求参数 `timeout=5000&expected=204`。仅调用 provider 下该节点的 `/healthcheck` 一次，不调用整个 provider 的检测或更新接口，不请求 TikTok 组。
- 若该 URL 已存在状态或历史，停止并报告 `existing-test-history-no-repeat` 或 `existing-test-state-no-repeat`，不再发起检测。每次运行内也有单次请求限制，curl 禁用重试与重定向；失败后只尝试普通读回。
- 不 PUT／PATCH／POST／DELETE，不删除连接，不写选择、规则、DNS、插件选项、服务或状态文件。检测会产生代理流量并写入核心的内存历史。单次 API 调用内部的 HEAD 请求行为由核心已有 `unified-delay` 设置决定，本工具不改它。

现有 URL 记录防止正常重复执行，不是跨核心／订阅重载的持久锁；重载清空记录后再次手工运行仍可能再检测。因此本次只执行一次，不因失败自行重跑或清空记录。

## 执行与结果

取得维护者提供的固定提交版本后，在路由器执行一次：

```sh
lua liangxinyun_probe_one.lua --probe-once
```

无需保存脚本的远程执行方式由维护者提供固定提交 URL。省略参数会停止，不发起 API 查询。此参数只是显式执行模式，不是再次请求用户授权。

正常输出为一行 JSON；回传摘要即可，不分享 API secret、订阅或原始 provider 响应。

| 字段／结果 | 含义 |
| --- | --- |
| `probeRequestAttempted`、`probeRequests` | 是否尝试检测 API，请求数最多 1；不保证超时或拒绝的请求实际完成检测 |
| `probeHttpStatus` | 本机 API 响应码，不是测试网站的状态码 |
| `recordAppearedAfterProbe` | 检测前无该 URL 状态，读回后出现带时间戳的记录；不声称原子快照或排除外部并发检测 |
| `urlAlive`、`urlDelayMs` | 指定 URL 的检测状态与延迟，不能用全局 alive／history 替代 |
| `currentSelectionUnchanged`、`groupMembersUnchanged` | 读取前后手选和成员是否一致；工具没有写入选择 |
| `providerUpdatedAtUnchanged` | 提供商更新时间是否可比较且未变化；不证明对象身份或原子读取 |
| `healthy-for-requested-204` | API 200、读回新 URL 状态为健康且正整数延迟与 API 相同，并通过上述快照一致性核对 |
| `failed-for-requested-204` | API 200／503／504，读回新 URL 状态明确失败且延迟 0；只说明这一个节点对此目标的结果，不能直接归因为节点故障 |
| `unknown` 或 `error` | 数据不完整、API 异常、检测前条件变化或检测后快照不一致；不重试、不扩展至其他节点 |
| `selectionApplied:false`、`formalAcceptance:false` | 没有自动选节点，也不表示完整控制器已验收 |

目标核心的延迟 API 可能返回 200，而 URL 的期望状态未满足；本工具必须同时核对 `extra[指定URL].alive/history`，不能凭 API 200 宣称 204 通过。检测失败也可能写入一条延迟 0 的记录；记录出现和线路可用是两件事。

## 验证边界

本地以真实 Lua 5.1.5、curl 和合成本机 HTTP 夹具通过 18 个场景：成功、503、504、API 200 但 URL 检测失败、无历史读回、检测后选择变化、provider 更新时间变化、检测前选错节点或发生变化、已有历史／状态、目标缺失、核心变化、缺少参数、JSON 形状不兼容、401 和 302 不跟随。认证检查与命令行脱敏沿用只读夹具，所有捕获请求均为固定 GET，最多一个单节点检测路径。

```sh
python3 scripts/verify_liangxinyun_probe_one.py --lua /absolute/path/to/lua5.1
```

UCI、JSON 模块和时间为夹具替身；没有真实机场、路由器或完整 Mihomo 参与本组测试。只读工具原有 336 项 Lua 策略断言与 16 个 HTTP 场景已重跑通过。**单节点工具尚待用户在目标设备运行，不能记录为实测成功。**

接口依据：[OpenClash 官方 API 指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/15-api.md)、[目标核心 provider 单节点路由](https://github.com/MetaCubeX/mihomo/blob/bc76c1398c6e70089367a30169d0df7c7f77c42d/hub/route/provider.go)、[参数与 HTTP 响应](https://github.com/MetaCubeX/mihomo/blob/bc76c1398c6e70089367a30169d0df7c7f77c42d/hub/route/proxies.go)、[逐 URL 历史写入](https://github.com/MetaCubeX/mihomo/blob/bc76c1398c6e70089367a30169d0df7c7f77c42d/adapter/adapter.go)。
