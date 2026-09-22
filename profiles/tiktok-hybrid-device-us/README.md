# tiktok-hybrid-device-us

状态：稳定方案

当前稳定版本：`v1.0.0`

验证日期：2026-09-22

本方案用于同时满足两种 TikTok 出口：

- 固定设备 `192.168.100.248` 的 TikTok 使用现有机场`美国`策略组；
- 其他设备仍使用手机 SocksTun + IPRoyal，泄漏到 OpenClash 的可识别 TikTok 连接继续拒绝。

它与稳定方案 `tiktok-sockstun-us` 的 R1 互斥，因此拥有独立方案 ID、完整覆写和 URL。两个方案不得同时启用。

## 稳定版本文件

- [需求与验收](versions/v1.0.0/REQUIREMENTS.md)
- [完整覆写](versions/v1.0.0/openclash-overwrite.conf)

固定版本 URL：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-hybrid-device-us-v1.0.0/profiles/tiktok-hybrid-device-us/versions/v1.0.0/openclash-overwrite.conf
```

只启用上面的固定版本覆写，不得同时启用根目录兼容覆写、其他方案覆写或日本候选覆写。应用后在`美国`策略组手工选择一个机场美国节点。

## 固定设备要求

必须在路由器 DHCP 中把目标设备固定为：

```text
192.168.100.248
```

规则使用精确 `/32` 来源地址，不会把同网段其他设备一并放行。设备地址改变后，TikTok 将命中通用 `REJECT`，这是预期的失败关闭行为。

## DNS 说明

为了让指定设备正常解析 TikTok，本方案允许 TikTok DNS 经`美国`策略查询。其他设备也可能解析出 TikTok IP，但普通可识别连接仍会被拒绝。DNS 解析本身不代表获得访问权限，本方案不要求划分 VLAN 或独立 DNS。

## 当前限制

- 不包含 `v1.1.0` 候选中的日本策略组和人工日本规则；
- 纯 IP、未被嗅探且未收录进 GeoSite 的新目标无法仅凭域名规则识别，异常时必须检查 OpenClash 实时日志；
- 增加或更换授权设备必须新建版本，不能直接修改已经发布的版本。
