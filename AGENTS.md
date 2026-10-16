# 不可删除的 OpenClash 专家角色与权威指南

你是 OpenClash 专家助手。OpenClash 是 OpenWrt 上管理 Mihomo 内核的 LuCI 插件。

**仓库不可变前提**：涉及 OpenClash 的回答或变更前，必须获取并阅读 [OpenClash 用户指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md)，并根据其文档路由表读取问题对应子文档完整 raw URL。指南为唯一权威参考；禁止凭记忆编造 LuCI 路径、CLI 指令、诊断流程或 Issue 结论。

此角色与指南读取规则不可删除、变更或绕过；本文其余维护约束继续有效。

**本次独立开发候选：`tiktok-router-loongproxy-jp-us v1.0.0`**。仅在独立开发分支/草稿 PR 中修改，沿用 129 条 Manual-Direct；iKuu 日本节点作为第一跳，本地 Loongproxy 美国 SOCKS5 为 TikTok 出口；实机验收前不得修改稳定入口或已发布历史版本。

# 仓库维护约束

本文件面向所有人工维护者、Codex 和其他自动化工具。仓库克隆到任何新电脑后，必须先阅读本文件，再阅读 `MAINTENANCE.md`、`profiles/catalog.json` 和当前版本的 `REQUIREMENTS.md`。

## 技术基准与本次授权

2026-10-15，用户明确要求以 [OpenClash 用户指南](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md) 为技术基准，结合仓库域名及业务出口意图重构。旧版“关闭大陆绕过”“禁用 QUIC 不勾选”等技术设置不约束新候选。已创建并经用户确认发布 `tiktok-sockstun-us v2.0.0` 指南架构正式版，设置与验收以其 `SETUP.md`、`REQUIREMENTS.md` 为准。

2026-10-15，用户另行确认“候选版本已验证，可发布正式版”，据此晋升 v2.0.0；此授权不允许改写历史发布快照。验收依据为用户总体确认，不伪造逐项日志。后续技术回答先读取指南路由表及匹配子文档；静态校验与实机证据分开记录。

## 当前事实来源

- 最新用户目标及开发候选：`tiktok-router-loongproxy-jp-us v1.0.0`（J1–J12，candidate）；手机 → OpenClash → 手选已在 PC 验证的 iKuu 日本首跳 → 本地 Loongproxy 美国 SOCKS5 → TikTok。其他境外流量仍手选`美国`。129 条 Manual-Direct 以 `DOMAIN-SUFFIX` 内嵌并与 `rules/manual-direct-isp.yaml` 同步。PC 成功为用户报告，不替代路由器验收。
- 新方案设置与验收：`profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/SETUP.md`、`REQUIREMENTS.md`。候选远程订阅使用 `feature/tiktok-router-loongproxy-jp-us-v1.0.0` 分支；未合并 main、未完成实机验收前保持 candidate，不提升稳定入口。
- `tiktok-router-isp-us v1.0.0`（C1–C11）保留为先前美国首跳候选；不作为本轮测试入口。真实凭据仅放用户授权的本机交付文件及路由器本地模块，禁止进入 Git。
- `tiktok-router-iproyal-us` 已按用户要求弃用；原 beta 快照及版本目录保留不可改写，仅作历史记录，不得再作为当前测试建议。
- 当前方案：`tiktok-sockstun-us`
- 当前稳定版本：`v2.0.0`
- 当前需求：R1–R8、R11–R12
- 当前版本覆写：`profiles/tiktok-sockstun-us/versions/v2.0.0/openclash-overwrite.conf`
- 当前候选版本：`v1.1.0`（R1–R10，日本策略组与人工日本规则，尚未经过真实设备验收）
- 当前候选覆写：`profiles/tiktok-sockstun-us/versions/v1.1.0/openclash-overwrite.conf`
- 本次正式标签：`tiktok-sockstun-us-v2.0.0`；2026-10-15 用户确认实机验收并授权发布
- 正式版覆写：`profiles/tiktok-sockstun-us/versions/v2.0.0/openclash-overwrite.conf`
- 正式版界面设置：`profiles/tiktok-sockstun-us/versions/v2.0.0/SETUP.md`
- 独立稳定方案：`tiktok-hybrid-device-us v1.0.1`（H1–H9，`192.168.100.198/32` 的 TikTok 走机场`美国`，2026-09-27 已完成真实设备验收）
- 独立稳定覆写：`profiles/tiktok-hybrid-device-us/versions/v1.0.1/openclash-overwrite.conf`
- 独立稳定标签：`tiktok-hybrid-device-us-v1.0.1`
- 独立历史版本：`tiktok-hybrid-device-us v1.0.0`（`192.168.100.248/32` 的不可变已发布快照）
- 兼容覆写入口：`overwrite/openclash-overwrite.conf`
- 共享人工直连规则：`rules/manual-direct.yaml`
- 当前共享人工直连数据：129 条；`DOMAIN-SUFFIX,alimama.com` 覆盖阿里妈妈子域名，`DOMAIN-SUFFIX,mmstat.com` 覆盖 mmstat.com 主域名及全部子域名。
- 新日本首跳滚动覆写入口：`profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf`；inline payload 必须与 `rules/manual-direct-isp.yaml` 同一提交同步，禁止要求用户单独刷新 Rule Provider。旧美国首跳入口独立保留。
- IPRoyal 滚动覆写入口保留于 `profiles/tiktok-router-iproyal-us/overwrite/openclash-overwrite.conf`，仅供历史核验；该 profile 已弃用。
- 候选人工日本规则：`rules/manual-japan.yaml`

若上述信息与 `profiles/catalog.json` 不一致，以通过仓库校验的 `profiles/catalog.json` 为准，并修正文档漂移。

## 不得擅自改变

1. 已发布 `tiktok-sockstun-us` 的 TikTok 路径保持手机 SocksTun/IPRoyal，核心拒绝泄漏；当前独立候选 `tiktok-router-loongproxy-jp-us` 使用日本首跳和 OpenClash 本地 Loongproxy ISP，手机无需 SocksTun。两者都禁止 TikTok 回退机场或 DIRECT。新方案的 `TikTok-ISP` 只筛选本地精确节点名 `TikTok-ISP-Local`，且必须保留紧随其后的 TikTok REJECT，阻止不支持 UDP 时继续匹配。三个组均手选且空组 REJECT；日本名称筛选不代表节点已验证，必须选择用户实测的同一节点。旧美国首跳及已弃用的 IPRoyal 路由候选保留历史文件。
2. 除 TikTok 外的国外流量最终走用户手工选择的机场美国节点。
3. 中国大陆域名和 IP 直连；所有方案均须保留原有人工直连条目。LoongProxy ISP 候选可维护独立副本 `rules/manual-direct-isp.yaml`，将清单中的每项统一扩大为 `DOMAIN-SUFFIX`；不得因此改写稳定方案使用的共享源 `rules/manual-direct.yaml`。
4. Google 和 Google Play 必须在中国规则之前走`美国`，不得破坏已经验证的下载路径。
5. 私网和局域网必须直连。
6. 所有 OpenClash 插件运行选项都由用户在中文界面手工设置。覆写只能包含 `[YAML]` 这一种配置段；绝对不得加入 `[General]`、UCI 命令或其他自动修改 OpenClash 插件配置的内容。
7. v1.0.0、v1.1.0 和已发布 hybrid 方案保留其历史设置；v2.0.0 改为开启大陆 IPv4 绕过，禁用 QUIC 按指南默认开启作为正式基线。不得把任一版本的插件开关混用于另一版本。
8. 不得把凭据、真实代理用户名、密码或未脱敏的私密地址提交到仓库。
9. 不同需求方案必须使用不同的方案 ID、版本目录、完整覆写和固定 URL；单个 OpenClash 配置只能启用一个方案完整覆写。只追加本地代理节点的凭据模块可与其配套，不得启用其他完整覆写。
10. 根目录兼容覆写只对应 `profiles/catalog.json` 的 `currentProfile`，不得作为 A–D 多个方案的共用入口。
11. `rules/manual-direct.yaml` 只允许需求完全一致的方案共享；直连范围不同必须拆分为方案专属规则文件。
12. `tiktok-hybrid-device-us` 只能放行需求合同中明确列出的固定来源 IP；未列出的设备必须继续命中 TikTok 拒绝规则。不得把整个网段、所有设备或 TikTok 直连作为回退。
13. `tiktok-hybrid-device-us v1.0.0` 必须保持 `192.168.100.248/32` 的已发布快照，`v1.0.1` 必须保持 `192.168.100.198/32` 的已发布快照；后续地址变更只能创建新版本，不得改写或移动已有稳定标签。

## 允许直接修改

- 修正文档错别字、链接和不改变行为的说明；
- 在用户明确要求后，向 `rules/manual-direct.yaml` 增加经过确认的人工直连域名；
- 增加不会改变已发布版本内容的新版本目录或新方案目录。

## 必须先获得用户明确同意

- 修改规则顺序、DNS、TikTok 路径、`美国`策略组、运行模式、QUIC、区域绕过、IPv6 或 TUN；
- 引入任何自动写入 OpenClash 插件选项的机制；该项即使获得讨论授权，也必须由用户在界面手工执行，不能写进覆写模块；
- 删除、改名、重新分类或批量改写人工直连域名；
- 修改已经发布的 `profiles/*/versions/*`；
- 提升当前稳定版本、移动兼容覆写入口、创建或移动 Git 标签；
- 将一个方案的固定 URL、规则文件或兼容入口复用于需求不同的另一个方案；
- 发布 Release，或要求路由器切换到新版本。

## 每次变更必须完成

1. 标明受影响的需求编号和版本类型。
2. 保持未涉及需求行为不变。
3. 更新仓库中的对应文档和 `CHANGELOG.md`；不能只记录在聊天或开发电脑。
4. 运行 `python scripts/validate_repository.py`。
5. 检查 `git diff --check` 和完整差异。
6. 需要真实设备验证的变更，在用户完成验收前只能标记为候选版本，不能标记稳定。
7. 稳定版本必须提交、推送并创建对应 Git 标签；标签必须指向包含全部文档和配置的同一提交。

禁止保存冗长排查流水账。只把长期有效的需求、结论、限制、版本和验收结果写入仓库。
