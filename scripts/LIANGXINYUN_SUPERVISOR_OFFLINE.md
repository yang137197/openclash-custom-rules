# 停止监督脚本离线单次测试

2026-11-24，用户明确授权：“继续下一步，做停止监督脚本的离线测试，不安装服务、不接入 OpenClash API，TikTok 链路和直连规则保持不变。”本次仅准备并交付这一项测试，目标结果待回传。已完成的锁和状态单项不重测。

`liangxinyun_supervisor_offline.lua` 内嵌的 Shell 原文与 v1.8.1 的 `liangxinyun-controller.run` 逐字节一致，由本地回归校验。它只监督合成 Lua 测试任务，不加载完整控制器、UCI、订阅、凭据或生产锁／状态文件。下载脚本需要访问 GitHub；下载完成后的测试不发起网络请求，不接入 OpenClash API，不测速、不切换节点、不安装或启用服务。

默认或 `--inspect-only` 仅检查已有 nixio 接口；`--test-once` 执行以下两个场景，各启动一个临时 Shell 监督进程及其合成 Lua 子进程：

1. `immediate`：收到停止标记后立即清理并退出。
2. `delayed`：收到停止标记后等待约200ms，再清理并退出，模拟正常停止期间仍有有限任务未完成。

父诊断进程仅向自己 fork 出、尚未 wait 回收的直接监督子进程发送 SIGTERM；异常清理必要时才向同一未回收直接子进程发送 SIGKILL。它不向测试 worker、任意既有 PID 或进程组发信号。worker 仅通过父 PID 和 `/proc/<pid>/stat` 的启动时间识别，用于确认退出，不作为发信号依据。worker 还会检查父进程是否退出，并有约20秒的自退出循环。

测试从 `/dev/urandom` 生成 `/tmp/liangxinyun-supervisor-<16位十六进制>`，排他创建0700私有目录；存在则停止，不复用。目录内只写监督脚本、合成 worker 和各场景固定名称的日志、ready、work、done 文件。两个测试监督进程还会按原脚本逻辑分别使用 `/tmp/liangxinyun-stop.<自身PID>`；exec 前检查该路径不存在，若已有文件则拒绝启动，不覆盖。正常停止由原脚本移除标记。清理只删除自建目录中的固定名称及已确认属于本次、相关进程已退出的标记，再删除空目录，不递归删除。

两项均要求：监督进程已回收且退出码0、worker 已写出完成确认并退出、work 和停止标记已清理。输出应包含 `supervisorTestPassed:true`、`cleanupComplete:true`、`forcedCleanupUsed:false`，两个 `cases` 中 `passed:true`；`apiRequests` 和 `probeRequests` 均0，`selectionApplied:false`、`formalAcceptance:false`。失败时报告错误；无法确认清理完成时保留临时目录路径，不把强制清理当作通过。请回传完整JSON，失败后不自动重试。

本地结果：372项实际Lua／替代接口断言通过，包含只读默认行为、失败路径、清理范围和禁止向worker发信号；8项实际Shell／Lua／源文件场景通过，包含两个正常停止、三个故障反例（停止标记未清理、退出码7、监督提前退出）、自然退出码0／7传递和内嵌源一致性。真实子进程测试使用本地 `/bin/sh`，JSON及部分nixio接口为替代模块；父诊断的原生fork／exec／wait／dup及目标BusyBox ash仍须由本次CatWrt回传验证。

本测试不验证 procd、完整控制器的 API 清理、真实检测调用、生产文件路径、SIGINT、强杀恢复或长期稳定性；不据此宣称完整候选验收通过。正式滚动入口、TikTok链路、直连源均不变。

接口依据：[OpenWrt LuCI nixio进程实现](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/process.c)、[nixio文件及dup实现](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/file.c)。本诊断属于独立用户脚本，不是OpenClash官方功能，范围按[官方指南的范围外说明](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/99-out-of-scope.md)区分。
