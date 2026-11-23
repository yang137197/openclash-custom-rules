# v1.7.0 本地验证记录

2026-11-23，独立自动控制器的本地验证通过，**尚未验证目标路由器或真实机场线路**。

## 已确认

- `scripts/test_liangxinyun_controller.rb`：278 项断言通过，包括四档各两个节点的 256 种存活组合、最高可用档最低延迟、unknown／过期／未来时间、不同测试 URL、来源筛选、同延迟保留、启动先 REJECT、停止 REJECT，以及拒绝修改旧稳定方案或不一致订阅快照。
- `scripts/check_liangxinyun_controller.py`：13 项真实核心夹具通过。Mihomo Meta v1.19.34 linux amd64，go1.26.11／with_gvisor（2026-11-11 构建）；Ruby 3.3.8，运行于 WSL Ubuntu。API 使用含引号、美元符号和反斜杠的合成 secret，确认可认证且不进入控制器参数或日志。
- OpenClash v0.48.002 标签的实际 `YAML.rb` 合并函数验证本地订阅 URL、`LXY: ` 前缀、Loongproxy `dialer-proxy` 与 `udp: false` 得到保留，云模块健康检查合并成功；合并后的完整合成配置通过同版 Mihomo `-t`。WSL 没有 OpenClash `uci.sh`，加载参考文件时有相关警告；本项只验证合并函数，未验证插件启动链或实际 UCI 设置。
- 本地与公共候选均不包含真实订阅、地址或认证；正式 v1.5.0 快照及两个正式滚动模块没有被本次变更改写。

| 核心夹具项目 | 结果 |
| --- | --- |
| 只读预检不切换节点、不写状态文件 | 通过 |
| 日本专线优先，档内最低延迟 | 通过 |
| 单实例锁，secret 不在 argv | 通过 |
| 专线 02 失效、专线 01 存活时不提前降级 | 通过，连续采样只见同档节点／REJECT |
| 三次整档失效，逐档进入下一档 | 3 项通过 |
| 四档全失效明确选择 REJECT，新连接失败 | 通过 |
| 最高档恢复、档内最低延迟变化 | 2 项通过 |
| 空档跳过、订阅新增编号 12 自动纳入 | 2 项通过 |
| 正常停服务 REJECT，TikTok 手选值不变、日志无 secret | 通过 |

夹具所有订阅、HTTP CONNECT 代理和目标响应均为回环合成服务，没有使用用户真实线路。健康检查和控制器周期加速为 1 秒，超时加速为 300 ms；生产 60 秒／5 秒时序未实测。TikTok 验证只覆盖组成员和手选值保持，不是实际视频播放验证。

## 尚未验证

Ruby 控制器读取 UCI 与认证、procd 自启动／重启、核心及控制器异常重启、实际健康检查目标可达性、应用层播放／下载仍未验证。后续已确认 Ruby 所需库加载失败、Lua 基础读取通过；见下节，不能继续将依赖列为全未知。API 故障或 SIGKILL 时不保证已清理选择，相关限制见合同。不得把本地通过写成 alpha-gbc76c13 或完整实机通过。

## 安装前设备记录（2026-11-23）

11:06 调试日志确认 OpenClash 0.48.002、Mihomo alpha-gbc76c13、OpenWrt 24.10.2 r7492-3fda82b52、x86_64，Ruby 3.3.6-1 和 curl 8.11.1-1 已安装。核心 `/version` API 返回正常；现有良心云仍为手选结构，不能视作 v1.7.0 已加载或通过验收。额外 Ruby 模块没有在日志中检查，不能据此断言它们缺失或已齐全。

官方 v0.48.002 [openclash_debug.sh](https://github.com/vernesong/OpenClash/blob/v0.48.002/luci-app-openclash/root/usr/share/openclash/openclash_debug.sh)主动省略配置中的 proxies/proxy-providers；本日志未显示节点及 provider 不能作为缺失结论。覆写模块清单章节为空，无法确认实际模块顺序。采样活动连接仅含直连，不能证明 TikTok 或良心云应用可用。

运行 Manual-Direct 与 v1.5.0 固定快照逐项相同（141 条），仓库当前滚动模块及候选为 148 条，新增来自先前流程 A 的日常维护。部署前须核对差异，未在本次分析中应用任何规则变更。原始附件不入仓，环境记录状态仍为 pending／not-run。

## 后续基础预检与 Lua 模拟准备（2026-11-23）

用户回传确认 Ruby 所需库加载失败、Python3 不存在；现有 Lua 5.1、JSON／UCI／nixio 模块与 curl 的只读查询通过。45 个 provider 节点存在普通历史和至少一个 URL 历史，不等于 45 个节点当前健康；真实 URL、时间及预期状态仍待核对。详见 [READ_ONLY_PREFLIGHT.md](READ_ONLY_PREFLIGHT.md)。

另备 `scripts/liangxinyun_readonly.lua` 单次只读模拟工具。第一版经 321 项策略断言与 14 个 HTTP 场景后已由用户在设备执行：四档 4／5／7／5 共 21 个节点，默认 URL 记录全部缺失，未发现四档任意 URL 的非空历史；按未知处理，未写选择，不等于节点全失败。前次 45 个节点有历史与本次结果的差异仍待核对。

工具增加历史结构摘要及 JSON 转义 URL／数组自检，本地 Lua 5.1.5 的 336 项策略断言及 16 个实际 curl／本地 HTTP 场景通过。工具没有测速、写选择、状态文件或服务，不替换 Ruby 运行实现；Lua 模块替身与真实路由器的验证边界见[工具说明](../../../../scripts/LIANGXINYUN_READONLY.md)。用户已运行增强摘要：JSON 自检通过，45 个节点的 extra 全为空表，普通历史和逐 URL 历史非空计数均为 0；四档 21 个也相同，当前选择未写入。只读预检完成，但没有数据可验证实际最低延迟选择。单节点主动检测仍为待授权建议，不将单次模拟计入控制器实机验收。

## 复核入口

运行 Ruby 策略测试：`ruby scripts/test_liangxinyun_controller.rb`。真实核心夹具按脚本 `--help` 提供自己的 Mihomo 和 Ruby 可执行入口。v1.6.0 的[失败对照](../v1.6.0/VALIDATION.md)保留用于证明为什么改变实现，不能拿其预期非零退出误报为 v1.7.0 回归。
