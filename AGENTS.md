# 仓库维护约束

本文件面向所有人工维护者、Codex 和其他自动化工具。仓库克隆到任何新电脑后，必须先阅读本文件，再阅读 `MAINTENANCE.md`、`profiles/catalog.json` 和当前版本的 `REQUIREMENTS.md`。

## 当前事实来源

- 当前方案：`tiktok-sockstun-us`
- 当前稳定版本：`v1.0.0`
- 当前需求：R1–R8
- 当前版本覆写：`profiles/tiktok-sockstun-us/versions/v1.0.0/openclash-overwrite.conf`
- 当前候选版本：`v1.1.0`（R1–R10，日本策略组与人工日本规则，尚未经过真实设备验收）
- 当前候选覆写：`profiles/tiktok-sockstun-us/versions/v1.1.0/openclash-overwrite.conf`
- 独立稳定方案：`tiktok-hybrid-device-us v1.0.0`（H1–H9，`192.168.100.248/32` 的 TikTok 走机场`美国`，2026-09-22 已完成真实设备验收）
- 独立稳定覆写：`profiles/tiktok-hybrid-device-us/versions/v1.0.0/openclash-overwrite.conf`
- 独立稳定标签：`tiktok-hybrid-device-us-v1.0.0`
- 兼容覆写入口：`overwrite/openclash-overwrite.conf`
- 共享人工直连规则：`rules/manual-direct.yaml`
- 候选人工日本规则：`rules/manual-japan.yaml`

若上述信息与 `profiles/catalog.json` 不一致，以通过仓库校验的 `profiles/catalog.json` 为准，并修正文档漂移。

## 不得擅自改变

1. TikTok 只由手机 SocksTun 通过固定的 IPRoyal ISP SOCKS5 代理；OpenClash 必须拒绝泄漏的 TikTok，不得回退到机场、直连或 OpenClash 本地 IPRoyal 节点。
2. 除 TikTok 外的国外流量最终走用户手工选择的机场美国节点。
3. 中国大陆域名和 IP 直连；`rules/manual-direct.yaml` 的现有条目必须保留。
4. Google 和 Google Play 必须在中国规则之前走`美国`，不得破坏已经验证的下载路径。
5. 私网和局域网必须直连。
6. 所有 OpenClash 插件运行选项都由用户在中文界面手工设置。覆写只能包含 `[YAML]` 这一种配置段；绝对不得加入 `[General]`、UCI 命令或其他自动修改 OpenClash 插件配置的内容。
7. 当前“禁用 QUIC”必须不勾选；“绕过中国大陆 IPv4”必须不勾选。
8. 不得把凭据、真实代理用户名、密码或未脱敏的私密地址提交到仓库。
9. 不同需求方案必须使用不同的方案 ID、版本目录、完整覆写和固定 URL；单个 OpenClash 配置只能启用一个方案覆写，禁止叠加或混用。
10. 根目录兼容覆写只对应 `profiles/catalog.json` 的 `currentProfile`，不得作为 A–D 多个方案的共用入口。
11. `rules/manual-direct.yaml` 只允许需求完全一致的方案共享；直连范围不同必须拆分为方案专属规则文件。
12. `tiktok-hybrid-device-us` 只能放行需求合同中明确列出的固定来源 IP；未列出的设备必须继续命中 TikTok 拒绝规则。不得把整个网段、所有设备或 TikTok 直连作为回退。

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
