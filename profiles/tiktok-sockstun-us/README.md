# tiktok-sockstun-us

当前稳定版本：`v1.0.0`

当前候选版本：`v1.1.0`（待真实设备验收）

稳定版对应需求：R1–R8

本方案用于：

- TikTok 由手机 SocksTun 通过专用 IPRoyal ISP SOCKS5 代理；
- OpenClash 拒绝 TikTok 泄漏；
- 其他国外流量走手工选择的机场美国节点；
- 中国大陆、局域网和人工维护域名直连；
- Google Play 使用经过验证的美国路由和 DNS；
- OpenClash 使用 Fake-IP（增强）模式，中文界面手工设置。

`v1.1.0` 候选在上述稳定行为不变的基础上，新增`日本`手选策略组和 `Manual-Japan` 人工规则集。候选不会自动替换当前稳定版本。

## 固定版本文件

- 需求和验收：[`versions/v1.0.0/REQUIREMENTS.md`](versions/v1.0.0/REQUIREMENTS.md)
- 覆写模块：[`versions/v1.0.0/openclash-overwrite.conf`](versions/v1.0.0/openclash-overwrite.conf)

固定版本 URL：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/v1.0.0/profiles/tiktok-sockstun-us/versions/v1.0.0/openclash-overwrite.conf
```

共享人工直连规则继续从 `main/rules/manual-direct.yaml` 更新。固定版本 Git 标签保存发布当时的完整规则快照。

不要同时启用本方案的固定版本 URL 和根目录兼容 URL。

## 候选版本文件

- 需求和验收：[`versions/v1.1.0/REQUIREMENTS.md`](versions/v1.1.0/REQUIREMENTS.md)
- 覆写模块：[`versions/v1.1.0/openclash-overwrite.conf`](versions/v1.1.0/openclash-overwrite.conf)
- 人工日本规则：[`../../rules/manual-japan.yaml`](../../rules/manual-japan.yaml)

候选版本保持 `candidate`；真实 OpenClash 验收通过并获得明确批准前，不更新兼容覆写入口，不创建稳定标签。

## 互斥的按设备方案

若需要让指定设备的 TikTok 使用机场`美国`策略组，应改用独立候选方案 [`tiktok-hybrid-device-us`](../tiktok-hybrid-device-us/README.md)。该方案与本方案的 TikTok 唯一路径要求互斥，两个完整覆写不能同时启用。
