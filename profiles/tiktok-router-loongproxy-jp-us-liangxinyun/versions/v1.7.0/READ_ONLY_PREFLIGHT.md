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

尚未验证四档节点筛选、严格分档选择、策略组写入、故障恢复、重启行为、资源占用或持续运行稳定性；没有本轮 TikTok 播放或直连应用回归结果。基础读取通过不代表完整控制器稳定、bug 少或 v1.7.0 已获用户验收；ENVIRONMENT.json 保持 `pending`、`runtimeAcceptance: not-run`、`userConfirmed: false`。

## 本轮操作范围

查询只读现有 UCI 端口及密钥，连接 `127.0.0.1`；密钥经管道输入 curl，不进入命令参数或摘要。访问范围为 GET `/version`、GET `/proxies/良心云` 和 GET `/providers/proxies/liangxinyun`，补查只重复最后一个读取接口。

没有调用健康检查、延迟测试、提供商更新、策略组切换或连接清理接口；没有安装软件、写入路由器配置或文件、启用服务、重启核心。TikTok 首跳和落地、直连规则及现有插件选项均未调整。当前正式方案继续使用 v1.5.0。

路由器现有 141 条 Manual-Direct 与仓库／候选 148 条的已有差异仍待部署前单独核对，本次未同步这 7 条维护数据。

后续已在本地准备[单次 Lua 只读模拟工具](../../../../scripts/LIANGXINYUN_READONLY.md)，通过 321 项 Lua 5.1 策略断言和 14 个实际 curl／本地 HTTP 场景；仅输出建议，不发起测速或写选择，待用户在路由器执行。它不替换本目录的 Ruby 控制器，也不解除后续部署和验收门禁。

依据：[OpenClash 官方 API 指南 15-api.md §15.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/15-api.md)、[Mihomo 节点状态序列化源码](https://github.com/MetaCubeX/mihomo/blob/bc76c1398c6e70089367a30169d0df7c7f77c42d/adapter/adapter.go)。实机结论以上述用户回传为准，源码只用于核对接口含义。
