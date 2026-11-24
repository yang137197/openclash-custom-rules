# 独立原生锁诊断（尚未在路由器执行）

用于补充完整控制器只读预检中的 `nativeLockTested: false`。它不是安装器，不启动完整控制器，不访问 UCI／Mihomo API，不测速或切换节点。

默认或 `--inspect-only` 仅检查需要的 nixio 函数和常量。**`--test-once` 超出此前只读授权，必须得到用户允许后才在目标执行。** 用户于2026-11-24明确答复“允许仅原生锁测试”，这一单次步骤已获授权，结果仍待目标回传；不把它扩成状态文件测试或安装／启用服务授权。

测试操作已限定：

1. `nixio.mkstemp('liangxinyun-native-lock')` 在 `/tmp` 随机创建一个文件；上游实现随即解除文件名，只保留打开的描述符。无持久路径，不使用生产控制器的锁文件。
2. 父进程 `tlock` 加锁；最多启动两个短暂子进程，分别验证锁被占用时返回 EACCES／EAGAIN、释放后能成功获取。每个子进程最多轮询等候约5秒，超时时仅结束本次已创建且未回收的测试子进程，不自动重试。
3. 关闭描述符；不写文件内容、不安装依赖、创建服务或更改配置。并不验证状态文件写入、原子更名、Shell／procd、全控制器重启或长期稳定性。

已授权的调用方式：`lua liangxinyun_native_lock.lua --test-once`。成功应同时为 `parentLockAcquired: true`、`competingChildBlocked: true`、`childAcquiredAfterUnlock: true`、`descriptorClosed: true`，且 API／检测请求均0、选择未应用、正式验收为false。任何错误只表示该诊断没有通过，不继续安装或更改路由设置；已完成后不自动重测。

本地 `test_liangxinyun_native_lock.lua` 的70项断言使用实际 Lua 和替代 nixio，验证成功、失败、超时和错误码的判定逻辑；不作为目标原生锁通过的证据。

依据：[nixio mkstemp／tlock](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/file.c)、[fork／wait](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/process.c)、[错误返回值和常量](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/nixio.c)。这些是上游接口实现，CatWrt 实际结果仍待用户授权后验证。
