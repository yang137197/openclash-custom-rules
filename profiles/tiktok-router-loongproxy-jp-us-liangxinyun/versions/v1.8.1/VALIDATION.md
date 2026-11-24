# v1.8.1 验证记录

**candidate，未部署、未实机验收。** 目标版本和此前已完成的只读／临时原生锁证据来自v1.8.0阶段，见ENVIRONMENT.json；不代表v1.8.1完整控制模式已经运行。

## 修正依据与边界

上游nixio源码确认权限数值按八进制形式的十进制数字解析，384无效。v1.8.0两处open误传384；其只读预检不创建文件，原生锁诊断使用mkstemp，均未覆盖此路径。之前本地替代模块忽略mode参数，记录为测试盲点，不能归因于CatWrt故障。

v1.8.1仅把两处实参改为 `rw-------`；旧版本运行文件、稳定版本、滚动模块、直连源不变。修正本地替代模块，拒绝384，并在实际本地文件上检查0600；仍不称为原生nixio C模块实测。

## 当前本地检查

- 新增状态诊断161项实际Lua／内存文件系统断言通过，覆盖短写、独占创建、权限、替换、旧打开描述符、读回、清理与失败路径。
- 6个实际Lua／本地POSIX场景通过：默认检查、显式检查、stdin单次测试、非法参数、权限格式回归、旧控制器错误参数回归。JSON及nixio由测试模块替代；本地使用真实文件、chmod和rename，验证读回及临时目录清理，不冒充目标C模块结果。
- 完整控制器358项实际Lua策略／状态机断言、19个curl／HTTP故障场景、13项真实Mihomo v1.19.34新连接出口夹具通过。新增权限检查同时确认本地锁／状态文件为0600；部分失败不提前降级、整档降级、恢复、订阅变更及正常停止继续通过。JSON／nixio在这些夹具中仍由替代模块提供，不能称目标原生运行通过。
- 63项Python仓库回归、版本／环境／哈希／不可变历史校验、Shell模板语法与 `git diff --check` 通过。正式模块、直连源、旧v1.8.0运行代码和catalog中的既有哈希未修改。

真实核心夹具使用本机回环合成节点，1秒检测、300ms超时和3秒有效期；不等于目标alpha-gbc76c13或默认60秒／5秒／130秒参数的实机验证。

可复现：

```text
lua5.1 scripts/test_liangxinyun_lua_controller.lua profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.1/liangxinyun-controller.lua
python3 scripts/verify_liangxinyun_native_state.py --lua /path/to/lua5.1
python3 scripts/verify_liangxinyun_lua_controller.py --lua /path/to/lua5.1
python3 scripts/check_liangxinyun_controller.py --core /path/to/mihomo --lua /path/to/lua5.1
python -m unittest discover -s scripts -p "test_*.py"
python scripts/validate_repository.py --base-ref origin/main
git diff --check
```

## 目标待验证

当前仅准备用户已要求的[隔离状态文件单次测试](../../../../scripts/LIANGXINYUN_NATIVE_STATE.md)，无目标结果。生产锁／状态路径权限、停止监督、procd启停、默认检测参数、重启和长期运行、实际流量及用户验收仍未通过；不扩大本次授权。状态测试不会接入OpenClash API或改变TikTok、直连和节点选择。
