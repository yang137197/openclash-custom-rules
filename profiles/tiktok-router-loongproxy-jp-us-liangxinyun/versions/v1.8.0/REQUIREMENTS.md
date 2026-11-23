# 良心云 Lua 严格自动选择 v1.8.0

**candidate，仅完成本地准备，待 CatWrt 实机验收。** 方案为 `tiktok-router-loongproxy-jp-us-liangxinyun`。继承 [v1.5.0 已验收链路](../v1.5.0/REQUIREMENTS.md)及 [v1.7.0 的 L19–L22 业务边界](../v1.7.0/REQUIREMENTS.md)，将完整运行实现改为目标已有的 Lua＋curl；旧 Ruby 候选保留，不覆写版本。

- L23：只从 `liangxinyun` provider 的 `LXY: ` 具体节点中，依次选择日本专线、日本高速、美国流媒体、美国高速；美国流媒体匹配同时含“美国”和“流媒体”的名称，不固定编号或数量。最高有健康节点的档内选最低延迟，同延迟保留当前节点。上档全部最近检测失败或该档为空才进入下档；上档无健康节点且仍有 unknown 则选 REJECT。
- L24：使用 Lua 5.1、已有 `luci.jsonc`／`luci.model.uci`／`nixio`、curl 和系统 Shell，不安装 Ruby／Python 或新依赖。统一 `https://www.gstatic.com/generate_204`，期望 204、单节点 5 秒超时；provider 自检及控制器完整检测默认 60 秒，每 2 秒核对。只信任该 URL 的逐节点 `extra`、时间戳与延迟，超过 130 秒、超前超过 5 秒、无记录或矛盾状态视为 unknown。周期从 `/proc/uptime` 计时，记录年龄用系统时间；不把全局历史当作该 URL 的结果。
- L25：默认及 `--preflight` 均为只读；`--dry-run` 只读模拟。只有显式 `--once`／`--run` 才能检测与写选择。接管前核对 Selector 首项 REJECT、四类成员、provider 来源／检测合同和前后快照一致；旧 45 节点手选方案不被接管。控制开始先 REJECT，只有本机 API 的 `良心云` 组可被 PUT；每次选择核对当前快照并读回确认，不写其他组、配置、UCI，不删除连接。
- L26：secret 由子 Lua 从现有 UCI 读取，经 curl stdin 传递；不得进入 argv、状态或日志。控制模式使用 nixio 非阻塞 POSIX 记录锁；状态原子更名、创建权限 0600。Shell 父进程接收正常停止信号，通知 Lua 尽力 REJECT 后退出，procd 有限重启；SIGKILL、API 故障、掉电没有清理保证。只读预检不创建锁、状态或停止文件，不主动检测节点。
- L27：TikTok 仍手选 iKuuu 日本 Z01–Z04 → Loongproxy 美国 SOCKS5，`TikTok-ISP-Local`、`dialer-proxy: TikTok首跳`、`udp: false` 和失败关闭不变。v1.8.0 模块与 v1.7.0 的有效 YAML 相同，DNS、路由顺序、148 条直连快照及本地模板保持；本轮不安装服务、不应用候选或改正式滚动入口。设备当前 141 条与候选 148 条的既有差异未部署，后续应用前须单独核对。

## 验收条件

1. 本地覆盖两节点四档 256 种成功／失败组合、未知高档、同延迟、过期、来源、写入读回与旧方案保护；真实 Lua／curl 故障夹具验证 API 错误、重定向、快照竞争及认证边界。
2. 真实 Mihomo 本地夹具逐次核对新连接出口：部分失败仍留档、整档降级、恢复、同档更低延迟、订阅增删、全失败、单实例与正常停止。LuCI／nixio 本地替代模块不算目标原生兼容证明。
3. 当前 CatWrt 先用完整新脚本只读预检；已有单节点诊断成功不等于本候选运行通过。之后另行安排安装／应用、原生锁、核心／控制器重启、停止／恢复及长期运行测试，并取得对应脱敏调试日志与用户验收，才可发布。

严格顺序基于最近有效检测记录，不保证网络瞬时健康或已有连接无感迁移。核心读写 API 不提供原子“快照加选择”，已做写前复核／写后确认，仍有请求间竞争窗口；不将未知当失败。API 不可用时不能声称已经 REJECT；控制器未运行时核心可能保留上次选择。

依据：[OpenClash API 指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/15-api.md)、[当前目标核心 provider 路由](https://github.com/MetaCubeX/mihomo/blob/bc76c1398c6e70089367a30169d0df7c7f77c42d/hub/route/provider.go)、[逐 URL 检测](https://github.com/MetaCubeX/mihomo/blob/bc76c1398c6e70089367a30169d0df7c7f77c42d/adapter/adapter.go)、[nixio 文件锁](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/file.c)、[信号接口](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/process.c)、[时间接口](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/poll.c)。上游提供接口，不表示官方为本自定义控制器提供兼容或稳定性保证。
