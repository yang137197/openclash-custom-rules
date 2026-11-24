# v1.8.2 本地验证

**2026-11-24：本地通过，candidate，未部署／未实机验收。** 脱敏结果在[VALIDATION.json](VALIDATION.json)。所有配置和线路均为本机合成夹具；未连接CatWrt或真实订阅、未安装服务，没有使用私有历史日志补占位冒充当前配置。

| 验证 | 本轮结果 | 证明范围 |
| --- | --- | --- |
| 官方合并／范围检查／备份与回退副本 | 41场景通过 | 固定官方v0.48.002真实YAML.overwrite；唯一目标与合同、全树范围、141条原序、其他任意数量／重复规则、幂等、越界拒绝、损坏／缺失备份拒绝、CLI脱敏、漂移拒绝、原注释／CRLF字节回退 |
| 实际Lua5.1策略／状态机 | 358项断言通过 | 四档组合、最高档选优、部分故障、未知／过期、来源与快照保护；不用真实线路 |
| Lua＋curl本机HTTP／命令边界 | 19场景通过 | 只读、显式控制／读回、旧手选拒绝、HTTP／JSON／跳转／竞争故障及认证不入argv |
| Mihomo v1.19.34真实核心＋Lua控制器 | 13场景通过 | 新连接实际出口、同档选优、部分失败不提前降档、三次整档降级、全失败REJECT、恢复高档、同档重新选优、订阅增删、单实例及正常停止；同时保留TikTok组选择 |
| Shell模板 | sh -n通过 | 监督与procd模板语法，无安装／启动procd |
| 仓库回归 | 65个测试通过 | 含新候选清单、原运行文件一致、稳定入口／源与滚动同步保护；测试中的3条规则同步仅发生在隔离临时仓库 |
| 仓库验证／diff | 通过 | 版本递增、需求／环境、哈希、不可变发布快照与文档索引；相对origin/main保留历史保护 |

范围与回退测试调用的就是候选 `scope_guard.py`，不是只在测试中另写一套检查。完整参考快照与增量合并后的良心云受控字段一致；参考快照的148条不用于本次141条设备升级。保护比较逐项覆盖完整rules／rule-providers／DNS／TikTok／ISP／订阅和其他字段，包含布尔值与整数的类型差异；不是仅比较数量。

41场景中的核心语法检查把已检查合并结果放入本机合成配置：文件提供商、环回代理、禁用DNS且无GEO规则，避免拉真实订阅或数据。它证明受控组／提供商语法；完整规则／DNS的保留由全树检查证明，不声称这些外部功能在该语法夹具运行过。CI加入不含核心二进制的40场景及v1.8.2 Lua／HTTP检查；本轮没有推送或声称新CI已执行。

## 明确局限

- 本机使用已有Lua5.1.5、便携Ruby3.3.8和Mihomo1.19.34；目标仍为alpha-gbc76c13。LuCI JSON／nixio／UCI由本机替代模块提供，不能代替CatWrt原生兼容证明。
- 真实核心夹具仅环回地址，检测使用本地HTTP204、1秒间隔、300ms超时及短记录有效期；没有验证生产HTTPS204／60秒／5秒参数的长期运行。
- 旧单项原生锁、临时状态和停止监督结果没有自动重测，也没有扩大为v1.8.2完整控制／procd验收。
- 当前设备完整配置、原模块清单／绑定／顺序、核心内存一致性、真实ISP／订阅、实际应用／回退、服务自启和长期运行仍未验证。ENVIRONMENT保持pending、runtimeAcceptance=not-run、userConfirmed=false。
- 离线门禁不会被OpenClash自动调用。直接启用模块会绕过本工具，哈希不是签名；真实应用仍须取得新基线并复核实际合并结果。

## 复现

在仓库根目录、电脑已有对应依赖时执行（不在路由器运行）：

```sh
python scripts/verify_liangxinyun_v182.py --ruby-command '["ruby"]' --openclash-yaml /private/YAML.rb --core /private/mihomo
lua5.1 scripts/test_liangxinyun_lua_controller.lua profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.2/liangxinyun-controller.lua
python scripts/verify_liangxinyun_lua_controller.py --lua /usr/bin/lua5.1 --candidate-directory profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.2
python scripts/check_liangxinyun_controller.py --core /private/mihomo --lua /usr/bin/lua5.1 --candidate-directory profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.2
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/validate_repository.py --base-ref origin/main
git diff --check
```

不传--openclash-yaml时验证脚本仅从固定官方raw地址读取并校验源码；不传--core则跳过1个核心语法场景。用实际文件构造的私有备份只保存在Git外；本次公共VALIDATION.json不含任何私有配置。

依据：[官方固定合并实现](https://github.com/vernesong/OpenClash/blob/e553e82e01c697aefbe1555261a503f425e00ccd/luci-app-openclash/root/usr/share/openclash/YAML.rb)、[官方覆写16.2.3](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)、[API15.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/15-api.md)。
