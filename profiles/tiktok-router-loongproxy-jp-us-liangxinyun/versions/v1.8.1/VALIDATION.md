# v1.8.1 验证记录

**candidate，未部署、完整控制器未实机验收。** 目标环境及只读／临时原生锁证据来自v1.8.0阶段；本阶段隔离状态文件和停止监督离线测试均已取得成功回传，见ENVIRONMENT.json。各单项通过不代表v1.8.1完整控制模式已经运行。

## 修正依据与边界

上游nixio源码确认权限数值按八进制形式的十进制数字解析，384无效。v1.8.0两处open误传384；其只读预检不创建文件，原生锁诊断使用mkstemp，均未覆盖此路径。之前本地替代模块忽略mode参数，记录为测试盲点，不能归因于CatWrt故障。

v1.8.1仅把两处实参改为 `rw-------`；旧版本运行文件、稳定版本、滚动模块、直连源不变。修正本地替代模块，拒绝384，并在实际本地文件上检查0600；仍不称为原生nixio C模块实测。

## 当前本地检查

- 新增状态诊断161项实际Lua／内存文件系统断言通过，覆盖短写、独占创建、权限、替换、旧打开描述符、读回、清理与失败路径。
- 6个实际Lua／本地POSIX场景通过：默认检查、显式检查、stdin单次测试、非法参数、权限格式回归、旧控制器错误参数回归。JSON及nixio由测试模块替代；本地使用真实文件、chmod和rename，验证读回及临时目录清理，不冒充目标C模块结果。
- 停止监督离线诊断372项实际Lua／替代接口断言通过；8项实际Shell／Lua／源文件场景通过，含立即和延迟清理退出、三个故障反例、自然退出码传递及内嵌Shell与候选逐字节一致。本地父进程接口为替代实现、Shell不是目标ash；目标的两个正常停止场景另见下方实机记录，三个故障反例仅在本地执行。候选监督运行文件未修改。
- 完整控制器358项实际Lua策略／状态机断言、19个curl／HTTP故障场景、13项真实Mihomo v1.19.34新连接出口夹具通过。新增权限检查同时确认本地锁／状态文件为0600；部分失败不提前降级、整档降级、恢复、订阅变更及正常停止继续通过。JSON／nixio在这些夹具中仍由替代模块提供，不能称目标原生运行通过。
- 63项Python仓库回归、版本／环境／哈希／不可变历史校验、Shell模板语法与 `git diff --check` 通过。正式模块、直连源、旧v1.8.0运行代码和catalog中的既有哈希未修改。
- 候选配置差异诊断101项实际Lua断言、8项实际Lua／curl／回环HTTP场景通过；逐段核对其合同与v1.8.1原文一致，GET读取器与既有只读工具一致，覆盖旧配置、全部兼容、快照变化、非公开URL脱敏、状态码及参数／路径拒绝。JSON／UCI为替代模块，目标差异输出待回传，不改运行文件或既有哈希。

真实核心夹具使用本机回环合成节点，1秒检测、300ms超时和3秒有效期；不等于目标alpha-gbc76c13或默认60秒／5秒／130秒参数的实机验证。

可复现：

```text
lua5.1 scripts/test_liangxinyun_lua_controller.lua profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.1/liangxinyun-controller.lua
python3 scripts/verify_liangxinyun_native_state.py --lua /path/to/lua5.1
python3 scripts/verify_liangxinyun_supervisor_offline.py --lua /path/to/lua5.1
python3 scripts/verify_liangxinyun_candidate_readonly.py --lua /path/to/lua5.1
python3 scripts/verify_liangxinyun_lua_controller.py --lua /path/to/lua5.1
python3 scripts/check_liangxinyun_controller.py --core /path/to/mihomo --lua /path/to/lua5.1
python -m unittest discover -s scripts -p "test_*.py"
python scripts/validate_repository.py --base-ref origin/main
git diff --check
```

## 目标单项结果与待验证范围

2026-11-24用户已回传[隔离状态文件单次测试](../../../../scripts/LIANGXINYUN_NATIVE_STATE.md)成功：初始写入／读回、0600文件权限、0700目录、独占创建、替换前原内容保持、同目录rename后的新内容／旧打开描述符读回及清理均通过。API／测速请求均0，selectionApplied=false、formalAcceptance=false。明确证明rw-------参数在当前目标本次临时文件操作中可用；未运行完整控制器、未使用生产文件路径。这次授权已完成，不重测。

2026-11-24用户回传固定提交 `7c1119cd6a962d2cfd21975a0f7f80a97c84e3b9` 的[停止监督离线测试](../../../../scripts/LIANGXINYUN_SUPERVISOR_OFFLINE.md)通过：supervisorTestPassed和cleanupComplete均true，forcedCleanupUsed=false；immediate、delayed两个case均passed，监督进程已回收、退出码0，worker正常停止并退出、工作文件和停止标记已清理。API／测速请求0、selectionApplied=false、formalAcceptance=false。仅确认本次原生诊断驱动与目标Shell的两个合成正常停止场景，这次单项授权已完成，不自动重测。

仍待验证：生产锁／状态路径权限、完整控制器正常停止时的API清理、procd启停、默认检测参数、重启和长期运行、实际流量及用户验收。未连接OpenClash API、未安装服务；TikTok、直连和节点选择未由本次诊断修改。完整控制器runtimeAcceptance仍为not-run、userConfirmed仍为false。

当前下一项为[只读配置差异核对](../../../../scripts/LIANGXINYUN_CANDIDATE_READONLY.md)：四次GET查询解释candidateCompatible=false，不测速、切换、写配置或安装服务；脚本及本地验证已准备，目标输出待回传。此前停止监督单项未连接API；本次独立脚本只读查询API，不运行控制模式。
