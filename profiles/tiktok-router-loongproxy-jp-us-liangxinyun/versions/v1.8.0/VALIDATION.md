# v1.8.0 本地验证与边界

**candidate，未部署、未实机验收。** 2026-11-23 准备 Lua＋curl 完整实现；目标此前单节点检测只证明已有组件能发起检测并读回正／负历史，不能证明本控制器长期稳定。

2026-11-24后续准备状态测试时发现nixio.open权限实参384不符合上游接口；本地替代模块原先忽略此参数，没有检出。v1.8.0暂不部署，两处运行代码保留；[v1.8.1](../v1.8.1/REQUIREMENTS.md)另行修正。以下历史夹具结果不证明原生权限路径可用，已完成的只读和mkstemp锁测试也没有执行这两处open。

## 可重复的本地检查

```text
lua5.1 scripts/test_liangxinyun_lua_controller.lua profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.0/liangxinyun-controller.lua
python3 scripts/verify_liangxinyun_lua_controller.py --lua /path/to/lua5.1
python3 scripts/check_liangxinyun_controller.py --core /path/to/mihomo --lua /path/to/lua5.1 --report /outside/repository/report.json
python -m unittest discover -s scripts -p "test_*.py"
python scripts/validate_repository.py --base-ref origin/main
git diff --check
```

使用真实 Lua 5.1.5、curl 和 Mihomo Meta v1.19.34 linux amd64／go1.26.11。全部网络为本机回环、合成订阅与节点，无真实账号、外网节点或路由器访问。LuCI JSON 与 nixio 在本地由测试替代模块实现：JSON 由 Python 桥接，锁由 Python POSIX lockf 持有；不把它们算作 CatWrt 原生 C 模块验证。CLI 及 HTTP 的实际 curl、认证 stdin、进程退出、Shell 停止监督不被模拟。

- Lua 策略／状态机 358 项断言通过，含四档两节点的256种成败组合、未知阻止降级、同延迟、过期、来源与成员不符、旧组拒绝接管、启动 REJECT、显式检测、写入读回不符、只读不检测／不切换，以及核心重启丢失历史后在检测前 REJECT。
- curl／HTTP／CLI 故障夹具19个场景通过，覆盖默认预检、只读模拟、错误状态／JSON／重定向、快照竞争、未实际应用的 PUT、未知高档、参数与非回环地址拦截；认证内容不进入 curl argv 或输出。
- 真实 Mihomo 夹具13个场景通过：只读预检；最高档最低延迟；锁互斥；部分失败保持原档；三次整档降级；全部失败 REJECT；最高档恢复；档内最优变化；订阅删除最高档／新增返回；正常停止回 REJECT。每个稳态场景核对实际新连接出口和 TikTok 两组选择，停止时检查未泄露合成secret。
- Shell `.run`／`.init` 语法、61项仓库静态回归及版本／哈希／环境门禁检查通过，`git diff --check` 通过。正式快照、滚动模块、直连源和旧v1.7.0运行文件均未修改。

夹具为快速故障验证，检测间隔1秒、单节点超时300ms、有效期3秒；不等于默认60秒／5秒／130秒的目标性能或长时间测试。此前 Ruby 夹具通过不替代本次 Lua 结果，当前目标核心是 alpha-gbc76c13，也不能用本地v1.19.34证明其运行兼容。

## 目标实机记录与未完成项目

完整新脚本只读预检的用户回传已于2026-11-24确认：固定提交bb28b5b，Lua5.1／alpha-gbc76c13，readOnly=true、selectionApplied=false，当前日本专线02；candidateCompatible=false、nativeLockTested=false、formalAcceptance=false。false与仍使用旧手选方案相符，不能从这个布尔量独断具体不匹配项；既不代表Lua启动失败，也不等于自动控制通过。

用户随后允许仅一次[独立原生锁测试](../../../../scripts/LIANGXINYUN_NATIVE_LOCK.md)，2026-11-24已回传成功：parentLockAcquired、competingChildBlocked、childAcquiredAfterUnlock、descriptorClosed、nativeLockTested均true；API／测速请求均0，selectionApplied=false、formalAcceptance=false。本次隔离临时文件的原生锁占用互斥与释放后获取已验证，单次授权结束，不重测。它与既有70项替代nixio判定断言分别记录；不据此证明生产锁文件路径权限或完整控制器已启动。原控制器、覆写、本地模板及其catalog哈希均未改动。

仍待验证：生产路径权限、原子状态写入、Shell／procd 启停与有限重启；核心重启／订阅竞争；默认参数下的检测耗时与长期稳定性；应用候选后的 TikTok 播放、普通代理、直连与用户确认。建议下一项仅验证隔离临时目录内的状态文件写入与原子替换，不接入OpenClash API；尚未授权或执行。141／148条直连差异不在本轮应用，没有发布或合并正式方案。
