# tiktok-router-iproyal-us

当前 beta 候选：**v1.0.2-beta.1 / candidate**。它沿用 v1.0.1 的机场美国首跳 → 本地 IPRoyal 链式拨号，新增精确直连规则 `DOMAIN,d-gm.mmstat.com`；全方案仍待真实路由器和手机验收。该 OpenClash 适配不等同于 IPRoyal 官方 Shadowrocket 教程。

所有接入本路由器、由 OpenClash 接管的手机，其可识别 TikTok 流量使用路由器本地 `IPRoyal-US-ISP`；手机无需 SocksTun。其他国外流量走手选机场美国节点，国内、局域网及当前 129 条人工规则直连。

- [v1.0.0 直连候选覆写与回退资料](versions/v1.0.0/SETUP.md)
- [v1.0.1 完整候选覆写：仅新部署时使用](versions/v1.0.1/openclash-overwrite.conf)
- [v1.0.1 无凭据链式补丁，可直接上传](versions/v1.0.1/iproyal-chain-hop.conf)
- [v1.0.1 上传、顺序、验收与回退](versions/v1.0.1/SETUP.md)
- [v1.0.1 P1–P10 需求](versions/v1.0.1/REQUIREMENTS.md)
- [v1.0.2-beta.1 完整覆写](versions/v1.0.2-beta.1/openclash-overwrite.conf)
- [v1.0.2-beta.1 链式补丁](versions/v1.0.2-beta.1/iproyal-chain-hop.conf)
- [v1.0.2-beta.1 设置与验收](versions/v1.0.2-beta.1/SETUP.md)
- [v1.0.2-beta.1 P1–P10 需求](versions/v1.0.2-beta.1/REQUIREMENTS.md)

IPRoyal 只有名称引用，地址与凭据保存在路由器本地。该方案独立于 `tiktok-sockstun-us v2.0.0`，不能叠加；旧稳定版和根兼容入口仍保留原义。
