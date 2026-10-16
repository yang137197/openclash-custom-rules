# OpenClash 分流配置

## 新开发候选：iKuu 日本 → Loongproxy 美国 ISP

独立方案 `tiktok-router-loongproxy-jp-us v1.0.0` 见[方案文档](profiles/tiktok-router-loongproxy-jp-us/README.md)。尚未路由器验收，原有稳定入口保持不变；完整云覆写内嵌 Manual-Direct，刷新后重启生效。

[本轮部署步骤与验收](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/SETUP.md)。候选远程覆写使用独立开发分支，当前可用地址：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/feature/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

仅配套一个本地 ISP 凭据模块。选择 PC 上已测试成功的同一 iKuu 日本节点，不把“日本”名称匹配当作连通性证明。

本次重构以 [OpenClash 用户指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md) 为技术基准，仓库提供域名及业务出口意图。旧版设置只用于旧版本回退，不约束当前正式版。

## 保留的旧候选：手机 → OpenClash → 美国机场首跳 → 本地 ISP → TikTok

**tiktok-router-isp-us v1.0.0（candidate）** 保留原美国首跳设计，本轮不使用其入口。其完整云覆写和本地节点文件独立保存，不代表 Loongproxy 已在路由器完成验收。

- [完整云覆写候选](profiles/tiktok-router-isp-us/versions/v1.0.0/openclash-overwrite.conf)
- [候选方案专属滚动订阅文件](profiles/tiktok-router-isp-us/overwrite/openclash-overwrite.conf)
- [本地 TikTok 节点模板（无凭据）](profiles/tiktok-router-isp-us/versions/v1.0.0/local-tiktok-proxy.conf.example)
- [OpenClash 上传顺序、手机验收与回退](profiles/tiktok-router-isp-us/versions/v1.0.0/SETUP.md)
- [C1–C11 需求合同](profiles/tiktok-router-isp-us/versions/v1.0.0/REQUIREMENTS.md)
- 方案专属人工直连数据：`rules/manual-direct-isp.yaml`。完整保留原 129 条条目，并统一为 `DOMAIN-SUFFIX`，覆盖每个条目及其子域名；不修改其他方案的共享规则源。

旧美国首跳候选 URL（非本轮测试）：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-isp-us/overwrite/openclash-overwrite.conf
```

`tiktok-router-iproyal-us` 已弃用，历史版本目录与 beta 快照保留、不再用于本轮测试。

## 保留的当前正式版：tiktok-sockstun-us v2.0.0

**状态：stable。2026-10-15 用户确认候选已验证并批准正式发布。** 适用于所有手机 TikTok 使用 SocksTun/IPRoyal；不包含按设备 TikTok 或日本候选。

- [完整正式覆写](profiles/tiktok-sockstun-us/versions/v2.0.0/openclash-overwrite.conf)
- [OpenClash 中文界面设置、安装、验收与回退](profiles/tiktok-sockstun-us/versions/v2.0.0/SETUP.md)
- [需求与架构变化](profiles/tiktok-sockstun-us/versions/v2.0.0/REQUIREMENTS.md)

| 技术项 | v2.0.0 正式版 |
| --- | --- |
| 运行路径 | Fake-IP 非 TUN＋规则模式 |
| 大陆 IPv4 绕过 | 开启，CN 域名使用 cn.mrs 返回真实 IP |
| Google/Play | 优先 Fake-IP＋美国专用 DNS＋美国路由，先于 CN 分类 |
| TikTok | SocksTun/IPRoyal；核心拒绝可识别泄漏，IPRoyal 入口单独旁路 |
| 人工直连 | v2.0.0 验收时为原有 124 条；当前共享数据为 129 条，含 `DOMAIN-SUFFIX,mmstat.com` |
| DNS | 国内 Nameserver，无 Fallback，独立节点解析，显式替换策略 |
| 禁用 QUIC | 按指南默认开启，具体业务兼容边界见设置说明 |
| 插件设置 | 用户手工配置，覆写只有 [YAML] |

模块与界面设置构成一套完整方案；只导入模块不会自动启用大陆防火墙绕过。普通国内旁路连接不一定出现在核心面板。

## 版本与入口

| 方案 | 状态 | 用途 |
| --- | --- | --- |
| tiktok-sockstun-us v1.0.0 | 历史稳定快照 | 旧设置回退 |
| tiktok-sockstun-us v1.1.0 | 旧日本候选，未实机验收 | 独立保留，不与 v2 混用 |
| tiktok-sockstun-us v2.0.0 | 当前稳定版，用户已确认验收 | 新的大陆旁路架构 |
| tiktok-hybrid-device-us v1.0.1 | 独立稳定版，授权来源 192.168.100.198/32 | 与主方案互斥 |
| tiktok-router-iproyal-us v1.0.0 | 直连 IPRoyal 的历史候选 | 实机日志出现 IPRoyal SOCKS5 端口超时 |
| tiktok-router-iproyal-us v1.0.1 | 前序链式拨号候选 | 机场美国首跳连接本地 IPRoyal 节点，TikTok 最终出口仍为 IPRoyal |
| tiktok-router-iproyal-us v1.0.2-beta.1 | 已发布 beta 快照 | mmstat 精确规则，仅 d-gm.mmstat.com |
| tiktok-router-iproyal-us v1.0.2-beta.2 / beta.3 | 已弃用候选快照 | 保留用于历史核对，不再作为测试路径 |
| tiktok-router-isp-us v1.0.0 | 保留的美国首跳候选 | 云端分流 + 路由器本地 ISP 节点 |
| tiktok-router-loongproxy-jp-us v1.0.0 | 当前开发候选，待手机实测 | 已验证的 iKuu 日本首跳 + 本地 Loongproxy 美国 ISP |

[profiles/catalog.json](profiles/catalog.json) 记录状态和文件映射。兼容入口 `overwrite/openclash-overwrite.conf` 现对应 v2.0.0；旧标签和已发布目录不改写。单个机场配置只启用一套完整覆写。

正式固定地址（只启用一套模块）：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-sockstun-us-v2.0.0/profiles/tiktok-sockstun-us/versions/v2.0.0/openclash-overwrite.conf
```

[GitHub Release](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-sockstun-us-v2.0.0)。已使用本地候选且配置正常的设备，无需为了版本名称重设开关；正式版仅更新文件头注释，配置正文相同。

## 维护

[AGENTS.md](AGENTS.md) · [MAINTENANCE.md](MAINTENANCE.md) · [CHANGELOG.md](CHANGELOG.md)

人工域名源保持 [rules/manual-direct.yaml](rules/manual-direct.yaml)，不要删除、扩大或重新分类已有条目。行为变更进入新版本，并更新相应需求、设置和验收说明。

首次安装校验依赖：`python -m pip install -r scripts/requirements-validation.txt`。静态门禁：`python scripts/validate_repository.py`、`python -m unittest discover -s scripts -p 'test_*.py'`、`git diff --check`。校验现在实际解析 YAML 并拒绝重复键，另需内核配置检查；静态通过不等于路由器、Google Play、TikTok 或国内 App 验收通过。

[v1 旧版完整说明归档](docs/legacy-v1-setup.md) 仅用于历史查询和回退，不是 v2.0.0 设置标准。
