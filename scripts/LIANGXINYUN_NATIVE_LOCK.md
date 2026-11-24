# 独立原生锁诊断（单次实机测试已通过）

用于补充完整控制器只读预检中的 `nativeLockTested: false`。它不是安装器，不启动完整控制器，不访问 UCI／Mihomo API，不测速或切换节点。

默认或 `--inspect-only` 仅检查需要的 nixio 函数和常量。**`--test-once` 超出此前只读授权，必须得到用户允许后才在目标执行。** 用户于2026-11-24明确答复“允许仅原生锁测试”，随后回传成功结果。这次单次授权已执行完毕，不重测，不把它扩成状态文件测试或安装／启用服务授权。

测试操作已限定：

1. `nixio.mkstemp('liangxinyun-native-lock')` 在 `/tmp` 随机创建一个文件；上游实现随即解除文件名，只保留打开的描述符。无持久路径，不使用生产控制器的锁文件。
2. 父进程 `tlock` 加锁；最多启动两个短暂子进程，分别验证锁被占用时返回 EACCES／EAGAIN、释放后能成功获取。每个子进程最多轮询等候约5秒，超时时仅结束本次已创建且未回收的测试子进程，不自动重试。
3. 关闭描述符；不写文件内容、不安装依赖、创建服务或更改配置。并不验证状态文件写入、原子更名、Shell／procd、全控制器重启或长期稳定性。

本次调用方式：`lua liangxinyun_native_lock.lua --test-once`，脚本来自固定提交 `79f657d40b7ce6daaa02086f039698d7823f81c0`。用户回传 `parentLockAcquired`、`competingChildBlocked`、`childAcquiredAfterUnlock`、`descriptorClosed` 和 `nativeLockTested` 均为true；`apiRequests`、`probeRequests` 均0，`selectionApplied=false`、`formalAcceptance=false`。确认本机这一次临时文件上的原生锁占用互斥、释放后获取和描述符关闭通过；不证明生产路径权限、状态文件写入、服务启停或长期稳定性。

本地 `test_liangxinyun_native_lock.lua` 的70项断言使用实际 Lua 和替代 nixio，验证成功、失败、超时和错误码的判定逻辑；不作为目标原生锁通过的证据。

依据：[nixio mkstemp／tlock](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/file.c)、[fork／wait](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/process.c)、[错误返回值和常量](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/nixio.c)。上游接口与本次目标回传分别记录，均不等于完整控制器验收。
