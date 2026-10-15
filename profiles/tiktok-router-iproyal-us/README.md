# tiktok-router-iproyal-us

当前候选：**v1.0.0 / candidate**，尚未进行真实路由器及手机验收。

所有接入本路由器、由 OpenClash 接管的手机，其可识别 TikTok 流量使用路由器本地 `IPRoyal-US-ISP`；手机无需 SocksTun。其他国外流量走手选机场美国节点，国内、局域网及原有 124 条人工规则直连。

- [完整候选覆写](versions/v1.0.0/openclash-overwrite.conf)
- [中文设置、应用及回退](versions/v1.0.0/SETUP.md)
- [P1–P9 需求和验收](versions/v1.0.0/REQUIREMENTS.md)

IPRoyal 只有名称引用，地址与凭据保存在路由器本地。该方案独立于 `tiktok-sockstun-us v2.0.0`，不能叠加；旧稳定版和根兼容入口仍保留原义。
