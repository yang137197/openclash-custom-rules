# v1.8.0 本地验证与边界

**candidate，未部署、未实机验收。** 2026-11-23 准备 Lua＋curl 完整实现；目标此前单节点检测只证明已有组件能发起检测并读回正／负历史，不能证明本控制器长期稳定。

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

## 待目标验证

完整新脚本只读预检的用户回传已于2026-11-24确认：固定提交bb28b5b，Lua5.1／alpha-gbc76c13，readOnly=true、selectionApplied=false，当前日本专线02；candidateCompatible=false、nativeLockTested=false、formalAcceptance=false。false与仍使用旧手选方案相符，不能从这个布尔量独断具体不匹配项；既不代表Lua启动失败，也不等于自动控制通过。

用户随后允许仅一次[独立原生锁测试](../../../../scripts/LIANGXINYUN_NATIVE_LOCK.md)，目标尚未执行／回传；独立诊断70项实际Lua／替代nixio判定断言通过，含预期错误码、占用与释放、失败和超时清理逻辑，不算原生锁证明。原控制器、覆写、本地模板及其catalog哈希均未改动。

仍待验证：CatWrt 原生文件锁、原子状态写入、Shell／procd 启停与有限重启；核心重启／订阅竞争；默认参数下的检测耗时与长期稳定性；应用候选后的 TikTok 播放、普通代理、直连与用户确认。当前授权只涵盖上述独立锁测试，不涵盖其他待验证项目。141／148条直连差异不在本轮应用，没有发布或合并正式方案。
