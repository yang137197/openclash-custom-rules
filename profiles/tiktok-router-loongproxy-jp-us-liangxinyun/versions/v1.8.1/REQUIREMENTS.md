# 良心云 Lua 权限兼容修正 v1.8.1

**candidate，未部署、未验收。** 方案 `tiktok-router-loongproxy-jp-us-liangxinyun`，继承[v1.8.0的L23–L27](../v1.8.0/REQUIREMENTS.md)及v1.5.0已验收的TikTok链路，仅修正待部署Lua控制器的权限参数。

- L28：nixio.open的权限参数统一使用 `rw-------`，覆盖生产锁文件创建和状态临时文件创建。上游 `nixio__check_mode` 的数值接口按八进制形式的十进制数字解析，600合法而384含非法数字8；v1.8.0误用了POSIX位值384，旧本地替代模块未校验，因而未检出。旧版本文件和哈希保留，停止部署v1.8.0，不能把此前只读／mkstemp锁测试当作这两处open通过。
- L29：用户在原生锁单项通过后要求“下一步”，按上一条已提出的范围准备一次隔离 `/tmp` 状态文件写入、替换、读回与清理测试。只使用合成内容、新建私有目录和两个固定临时文件名，不访问UCI／OpenClash API、不测速、不选择节点、不安装／启用服务。不重测已完成的原生锁；这次授权不涵盖完整控制器运行、真实状态文件或配置。

与v1.8.0相比，运行Lua仅替换两处权限实参；策略算法、探测参数、超时、服务模板及停止监督脚本不变。覆写有效YAML相同，本地凭据模板逐字节相同，TikTok仍手选iKuuu日本Z01–Z04 → Loongproxy美国，DNS、路由、直连和正式滚动入口不变。设备141条与候选148条直连的既有差异未部署，后续应用前仍需单独核对。

本地验收须复现旧权限值被拒绝、确认新值创建实际0600文件，并保留四档选路及故障恢复回归。隔离状态测试只核对正常写入／同目录rename替换与读回，不证明掉电持久性、崩溃一致性、生产路径权限或长期稳定性。完整候选仍须另行安排目标控制模式、服务启停及TikTok／直连等验收后才能发布。

依据：[nixio权限解析](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/fs.c#L28-L95)、[nixio.open](https://github.com/openwrt/luci/blob/master/libs/luci-lib-nixio/src/file.c#L29-L60)。实际目标的状态测试结果待回传，不将本地替代模块结果当作CatWrt原生通过。
