# Lua＋curl 基础只读预检记录

日期：2026-11-23。关联方案 `tiktok-router-loongproxy-jp-us-liangxinyun`，处于 v1.7.0 候选准备阶段，涉及 L20–L22 的环境和读取边界。结果由用户在当前 CatWrt 终端执行查询并回传摘要；代理凭据、订阅、节点地址和原始 API 响应未保存到仓库。

**结论：现有 Lua 组件和本机 API 读取预检通过，完整自动控制器尚未验收。** 本目录的控制器及服务仍是 Ruby 实现；本记录没有把它们改写成 Lua，没有创建新运行版本或替换正式入口。

## 已确认事实

| 检查项 | 用户回传结果 |
| --- | --- |
| Lua | 5.1 |
| 模块加载 | `luci.jsonc`、`luci.model.uci`、`luci.sys`、`nixio` 均 OK |
| JSON | 解析检查 OK |
| curl | 8.11.1，x86_64-openwrt-linux-gnu，支持 HTTP/HTTPS |
| 核心 API | `alpha-gbc76c13` |
| 良心云策略组 | `Selector`，45 个成员 |
| `liangxinyun` 提供商 | 45 个节点 |
| 普通历史 | 45 个节点均有非空 `history` |
| 按 URL 历史 | 45 个节点均有 `extra`，且至少一个 URL 的 `history` 非空 |
| 抽样记录字段 | 普通记录包含 `delay`、`time`；按 URL 的状态包含 `alive`、`history` |
| 提供商测试地址 | 首次摘要 `testUrlPresent=false`；补查包含 `testUrl` 字段，类型为 `string` |

提供商公开字段包括 `expectedStatus`、`name`、`proxies`、`subscriptionInfo`、`testUrl`、`type`、`updatedAt`、`vehicleType`；只记录字段名，不保存其敏感内容。

现有 Ruby 候选的所需库加载未通过；模拟包查询未安装软件。Python3 命令不存在。本轮未通过安装依赖、换源或升级运行库来推进。

## 计数修正与证据边界

第一次查询仅统计 `extra[provider.testUrl]`。`testUrl` 不为非空字符串时，计数会返回 0；该结果不证明 `extra` 或 `history` 不存在。补查不依赖提供商测试地址，已确认 45 个节点均有按 URL 的历史。两次摘要与测试地址为空字符串相符；未保存其原始值或实际 URL 键。

目前未验证历史属于哪一个具体 URL、是否对应预期 HTTP 204、每条记录的新鲜度及每个节点的实时可用性。不能用“存在历史”替代“当前健康”，也不能把记录缺失、过期或 URL 未确认直接当作超时来降级。

初次预检未验证四档节点筛选；后续单次模拟已取得四档计数，见下节。严格分档选择、策略组写入、故障恢复、重启行为、资源占用或持续运行稳定性仍未实机验证；没有本轮 TikTok 播放或直连应用回归结果。基础读取通过不代表完整控制器稳定、bug 少或 v1.7.0 已获用户验收；ENVIRONMENT.json 保持 `pending`、`runtimeAcceptance: not-run`、`userConfirmed: false`。

## 本轮操作范围

查询只读现有 UCI 端口及密钥，连接 `127.0.0.1`；密钥经管道输入 curl，不进入命令参数或摘要。访问范围为 GET `/version`、GET `/proxies/良心云` 和 GET `/providers/proxies/liangxinyun`，补查只重复最后一个读取接口。

没有调用健康检查、延迟测试、提供商更新、策略组切换或连接清理接口；没有安装软件、写入路由器配置或文件、启用服务、重启核心。TikTok 首跳和落地、直连规则及现有插件选项均未调整。当前正式方案继续使用 v1.5.0。

路由器现有 141 条 Manual-Direct 与仓库／候选 148 条的已有差异仍待部署前单独核对，本次未同步这 7 条维护数据。

后续已准备[单次 Lua 只读模拟工具](../../../../scripts/LIANGXINYUN_READONLY.md)，首次本地通过 321 项 Lua 5.1 策略断言和 14 个 HTTP 场景后由用户执行。它不替换本目录的 Ruby 控制器，也不解除后续部署和验收门禁。

## 首次单次模拟回传（2026-11-23）

提交 df02abf 的实机摘要确认：组与 provider 各 45 个节点，成员和当前手选在两次读取间一致；日本专线 4、日本高速 5、美国流媒体 7、美国高速 5，共 21 个纳入模拟，另 24 个忽略，实际组成员未删减。

21 个节点均为 `test-url-record-missing`，并且四档的 `observedTestUrls` 为空；provider 测试 URL／预期 204 元数据不匹配。`wouldSelect=REJECT` 的原因为高档未知阻止降级，不能解释为节点全失败或超时。`selectionApplied=false`，本轮没有应用该建议。

与前次“45 个节点有 URL 历史”的摘要在时间、范围和检查方式上均不同，尚未定位差异；不能仅归因为 URL 不一致，也没有证据认定核心或 Lua 解析出错。官方 LuCI 源码将数组解析为从 1 开始的 Lua 表，Mihomo 源码以 URL 为 extra 的键；当前程序采用相同约定。

下一步只增加历史结构计数及合成 JSON 自检，保持原有四个 GET 请求、URL 和时限，不触发测速或写选择。增强工具本地通过 336 项策略断言与 16 个 HTTP 场景，待设备运行；仍不构成自动控制器验收。

## 增强摘要回传：只读预检完成（2026-11-23）

用户已执行提交 8cf2778 的增强工具。`jsonUrlArraySelfTest=true`，解析自检通过；全部 45 个节点的 `extra` 均为空表，普通历史非空计数与逐 URL 历史非空计数均为 0。四档 21 个节点得到相同结论；缺失／非表 extra、异常状态和非 URL 键计数均为 0。当前样本是历史数据为空，不是仅默认 URL 不匹配，也没有证据证明 JSON 结构不兼容。

读取前后组成员与手选值一致，实际组仍有 45 个成员；`selectionApplied=false`，没有执行模拟 REJECT。不能把“无样本”标为失败或超时。前次摘要为 45 个节点有历史的具体差异原因仍未确定；当前结果不证明订阅曾刷新或核心曾重启。

目标核心源码 `adapter/adapter.go` 的 `URLTest()` 在检测完成时追加普通历史和逐 URL 历史，普通 `DialContext()` 不做这项记录；`NewProxy()` 从空历史开始。仓库 v1.5.0 的本地模板没有提供商 health-check 配置，与当前无检测数据相符，但本次摘要没有直接验证实机定时健康检查开关。因此只读预检已完成，继续重复相同读取不会主动产生检测样本。

**后续单节点范围已获用户明确授权，尚未执行：** 对用户回传的当前良心云日本专线 01 做一次 HTTPS 204 延迟检测；先核对仍选中该节点，使用 provider 下的单节点接口，目标 `https://www.gstatic.com/generate_204`、超时 5000 ms、期望 204，不检测整个 45 节点集合，不写组选择或配置，不启用服务。请求模板为：

```text
GET /providers/proxies/liangxinyun/<当前节点URL编码>/healthcheck?url=https%3A%2F%2Fwww.gstatic.com%2Fgenerate_204&timeout=5000&expected=204
```

此 GET 会产生代理检测流量并更新内存历史，属于主动检测，超出先前只读范围；用户随后明确回复“允许单节点检测（推荐）”，已获得这一项独立授权，无需再索取。成功且出现新的同 URL 有效记录，才证明这条检测与读取链可用；失败或仍无记录时核对 HTTP 状态和该记录，不将单节点结果扩大到整档。提供商健康检查配置、其他 20 个候选节点、自动切换与长期稳定性仍未验证。

已准备独立[单节点工具](../../../../scripts/LIANGXINYUN_PROBE_ONE.md)，先检查固定节点、现有 URL 状态和选择变化，确认条件后只发一个检测请求，再读回；没有自动重试、组写入或安装动作。本地 18 个实际 Lua 5.1／curl HTTP 夹具场景通过，原只读工具 336 项策略断言及 16 个 HTTP 场景也通过。实机单节点结果仍待回传，不改变完整控制器 `not-run`／未验收状态。

接口依据：[目标核心 provider 单节点路由](https://github.com/MetaCubeX/mihomo/blob/bc76c1398c6e70089367a30169d0df7c7f77c42d/hub/route/provider.go)、[检测参数处理](https://github.com/MetaCubeX/mihomo/blob/bc76c1398c6e70089367a30169d0df7c7f77c42d/hub/route/proxies.go)、[历史写入](https://github.com/MetaCubeX/mihomo/blob/bc76c1398c6e70089367a30169d0df7c7f77c42d/adapter/adapter.go)。

## 单节点调用被前置核对拦截（2026-11-23）

用户执行提交 7166293 的工具，结果为 `current-selection-not-authorized-node`、`probeRequestAttempted=false`、`probeRequests=0`、`selectionApplied=false`。只进行了版本和策略组读取，没有发出检测。该条件检查“精确目标名已选中且存在组内”；旧摘要未包含实际选择值，尚不能断定选择变化、名称格式差异或目标成员缺失。

仅补充 `--inspect-only` 查看模式，读取 `/version` 和良心云组后返回；显示实际选择、两项精确匹配结果及名称 UTF-8 字节，不检测、不切换，也不扩大到其他节点。检测模式的固定目标与保护条件不变。新增模式与已有检测场景合计 22 个本地 HTTP 夹具通过，目标查看结果待回传。此前单节点授权继续有效，但实际检测仍未发生，不应反复执行检测模式排查此错误。

## 已定位选择差异并修正多余前置条件（2026-11-23）

用户回传 fe22816 的只读结果：`currentSelection` 为良心云日本专线 02，`authorizedNodeInGroup=true`、`authorizedNodeSelected=false`；名称字节仅编号 02／01 不同。没有触发检测。当前问题不是名称格式或 01 缺失，而是程序要求选中 01、实际选中 02。

目标核心的 provider 单节点路由按 provider 与固定节点名直接查找，不依赖 select 的当前选择。要求先选中 01 是开发者加得过严的条件，已修正：01 仍须在组和 provider 中、仍只检测 01 一次；检测前后核对原手选值保持不变，前置读取期间选择变化仍停止。保持用户现有 02 手选，不写切换 API，不把授权对象改为 02。授权对象、URL、5 秒超时与次数未扩大，不再索取同一授权。

23 个本地 HTTP 夹具通过，包含保持 02 时只发 01 检测请求、01 缺失时零检测；实际单节点请求数仍为 0，修正后工具待用户执行。本结论只定位诊断工具拦截原因，不证明任一线路可用或完整控制器已验收。

依据：[OpenClash 官方 API 指南 15-api.md §15.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/15-api.md)、[Mihomo 节点状态序列化源码](https://github.com/MetaCubeX/mihomo/blob/bc76c1398c6e70089367a30169d0df7c7f77c42d/adapter/adapter.go)。实机结论以上述用户回传为准，源码只用于核对接口含义。
