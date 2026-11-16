# 良心云 v1.1.1 候选启动修复

状态为 **candidate**。继承 [v1.1.0 路由需求](../v1.1.0/REQUIREMENTS.md)。

- L8：当已有配置缺少 `proxy-providers` 或 `rule-providers` 父级映射时，合并后的代理提供商名为 `liangxinyun`，直连规则集名为 `Manual-Direct`，与现有引用一致。继续使用路由器本地订阅地址和 Loongproxy 凭据。

2026-11-16，用户报告 v1.1.0 启动时找不到 `liangxinyun`。OpenClash v0.48.002 在覆写新增整个映射时直接复制子键，嵌套的 `!` 后缀会保留。实机核对修复后能启动并继续执行 v1.1.0 验收。 [OpenClash v0.48.002 合并源码](https://github.com/vernesong/OpenClash/blob/v0.48.002/luci-app-openclash/root/usr/share/openclash/YAML.rb#L912-L954)

本地以 OpenClash v0.48.002 的 Ruby 合并函数和 Mihomo v1.19.34 核对。v1.1.0 合并结果复现同一报错。v1.1.1 在两个父级映射均缺失时通过核心配置检查，保留 141 条手动直连。对含已有提供商的底稿，验证原提供商同时保留。
