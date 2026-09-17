# tiktok-sockstun-us

当前稳定版本：`v1.0.0`

对应需求：R1–R8

本方案用于：

- TikTok 由手机 SocksTun 通过专用 IPRoyal ISP SOCKS5 代理；
- OpenClash 拒绝 TikTok 泄漏；
- 其他国外流量走手工选择的机场美国节点；
- 中国大陆、局域网和人工维护域名直连；
- Google Play 使用经过验证的美国路由和 DNS；
- OpenClash 使用 Fake-IP（增强）模式，中文界面手工设置。

## 固定版本文件

- 需求和验收：[`versions/v1.0.0/REQUIREMENTS.md`](versions/v1.0.0/REQUIREMENTS.md)
- 覆写模块：[`versions/v1.0.0/openclash-overwrite.conf`](versions/v1.0.0/openclash-overwrite.conf)

固定版本 URL：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/v1.0.0/profiles/tiktok-sockstun-us/versions/v1.0.0/openclash-overwrite.conf
```

共享人工直连规则继续从 `main/rules/manual-direct.yaml` 更新。固定版本 Git 标签保存发布当时的完整规则快照。

不要同时启用本方案的固定版本 URL 和根目录兼容 URL。
