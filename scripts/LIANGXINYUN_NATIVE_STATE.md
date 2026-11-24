# 隔离状态文件单次测试

2026-11-24，用户在原生锁通过后按“下一步建议仅验证临时状态文件写入与原子替换”的提议要求继续。本步骤仅限这一次隔离测试，不安装或启用服务，不运行完整控制器，不访问UCI／OpenClash API、不测速或切换节点。旧锁测试已结束，不重测。

脚本 `liangxinyun_native_state.lua` 默认或 `--inspect-only` 仅检查接口。`--test-once` 从 `/dev/urandom` 读取8字节生成 `/tmp/liangxinyun-state-<随机后缀>`，一次排他创建0700目录；存在时停止、不复用、不清理既有目录。只创建 `state.json`、`replacement.tmp` 两个0600文件，数据为固定合成JSON，不涉及订阅或凭据。

验证初始写入／读回、重复独占创建被EEXIST拒绝、替换前原文件保持、同目录rename替换后新文件读回、旧打开描述符仍能读到旧内容及inode对应关系。结束关闭描述符，只清理自建目录中的这两个固定名称，再删除空目录，不递归删除；失败报告错误，清理未完成时另报临时目录路径。没有额外子进程或自动重试。

成功应为 `stateFileTestPassed`、`stateWriteReadback`、`replacementReadback`、`cleanupComplete` 均true，`stateFileMode`为 `rw-------`；API／测速请求均0、选择未应用、formalAcceptance=false。它是正常替换与读回检查，不验证掉电持久性、崩溃一致性、并发压力、真实生产路径或服务稳定性。

准备本检查时发现v1.8.0误将384传给nixio.open的权限实参：该接口数值形式接受600，不接受含数字8的384。该运行路径未在目标执行，独立原生锁用mkstemp也没有覆盖；[v1.8.1](../profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.1/REQUIREMENTS.md)改用明确的 `rw-------`，保留旧候选。正式滚动入口仍为v1.5.0。

本地161项内存文件系统断言和6项实际Lua／POSIX场景通过；本地JSON/nixio由替代模块提供，不能宣称目标原生通过。目标结果仍待用户执行回传。

依据：[nixio权限解析／文件系统接口](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/fs.c)、[nixio.open／write／close](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/file.c)。
