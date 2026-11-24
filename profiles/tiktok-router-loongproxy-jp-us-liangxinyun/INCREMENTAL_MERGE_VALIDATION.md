# 增量草案的真实OpenClash本地合并验证

**2026-11-24，本地验证通过，未部署。** 用户要求使用真实OpenClash合并实现确认改动仅限良心云，保持TikTok和当前直连，不接触路由器、不安装服务。本轮没有新建运行版本或可导入模块，正式入口、原运行文件及哈希不变。

## 实现与结果

直接加载官方v0.48.002的 `YAML.overwrite`，不是自写合并模拟。标签提交为 `e553e82e01c697aefbe1555261a503f425e00ccd`；`YAML.rb` SHA-256为 `1249abf411e1df9e8fe542fb3584f34a27e6e3a587942e5d9f759a32b1bd8261`，下载后及执行前校验。使用本机已有便携Ruby3.3.8，未安装依赖或服务。被测输入是[方案](APPLY_ROLLBACK_PLAN.md)中的INI结构草案，其SHA-256见[脱敏报告](INCREMENTAL_MERGE_VALIDATION.json)。

本地18个场景通过，包含17个可公开复现的合成／保护检查，加1个私有历史配置夹具。正常基线的变化只有：

- `/proxy-groups/良心云/proxies`
- `/proxy-groups/良心云/default-selected`
- `/proxy-groups/良心云/filter`
- `/proxy-providers/liangxinyun/filter`
- `/proxy-providers/liangxinyun/health-check`

完整rules、全部rule-providers、Manual-Direct逐项与原顺序、DNS、TikTok两组及其他组／提供商保持一致。稳定版占位模板合成夹具中的本地ISP节点全字段保持一致，包括dialer-proxy和udp。提供商URL、headers、path和prefix等不在允许字段内，必须原值保留。旧include-all等字段在另一个夹具中按草案移除，改动仍限良心云组。

另外验证同前缀组／提供商不受影响、任意直连数量／逆序／重复项保持、重复合并幂等及内存备份恢复。测试层对缺失／重复目标、非法补丁根／目标和范围外变化执行拒绝检查；故意修改DNS、TikTok或直连顺序均被识别。共享引用夹具会使官方合并连带改变其他路径，范围检查将其拒绝。**这些拒绝条件来自验证器的前后条件，不表示OpenClash模块自行具备相同门禁**；未来应用工具仍须实现并测试它们。

官方实现会修改部分传入的嵌套对象。测试保留独立原基线，并在屏蔽允许路径时打断共享引用，避免比较过程掩盖范围外变化。私有YAML若含锚点／别名则拒绝经JSON传输，不能静默丢失其引用关系。

## 私有基线与限制

只在本机内存读取11月23日实机日志的配置段，文件未修改，原文和完整配置未复制进仓库。其141条Manual-Direct及TikTok组在合并后保持；11月24日只读文件回传已另外确认该141条基线同序相同。

**日志配置段没有可用的liangxinyun提供商定义，也没有本地ISP节点定义。** 私有夹具以占位提供商补齐后进行合并，报告明确标记 `providerReconstructedWithSyntheticFields:true`、`ispNodePresentInHistoricalLog:false`。本地ISP字段的保持由稳定版占位模板合成夹具验证。不能将此结果称作真实订阅、真实ISP凭据、当前整份设备配置或核心内存状态已验证。

没有启动核心、控制器或服务，没有联网拉取订阅／节点检测，也没有访问路由器。内存备份恢复不是设备回退演练。目标核心语法、实际合并顺序／模块注册、实际应用／回退、控制器及长期运行仍待后续候选与实机验证；运行落地仍须高于v1.8.1新候选，不据此发布或启用。

## 本地复现

仓库根目录已有Python、PyYAML和Ruby时执行：

```sh
python3 scripts/verify_liangxinyun_incremental_merge.py
```

默认只从上述固定官方提交下载源码并校验哈希，跑17个公开场景；也可用 `--openclash-yaml` 指定已有同哈希文件，或 `--ruby-command '["ruby"]'` 指定本机解释器。可选 `--debug-log` 只读仓库外私有历史日志，增加本地夹具；CI不使用私有日志。`--report` 只保存脱敏汇总，禁止覆盖私有输入。失败不输出私有原文／值／异常栈。CI已增加公开场景验证。

依据：[官方合并源码](https://github.com/vernesong/OpenClash/blob/e553e82e01c697aefbe1555261a503f425e00ccd/luci-app-openclash/root/usr/share/openclash/YAML.rb#L735)、[官方覆写指南16.2.3](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)。
