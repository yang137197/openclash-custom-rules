# 仓库维护约束

本文件面向所有人工维护者、Codex 和其他自动化工具。仓库克隆到任何新电脑后，必须先阅读本文件，再阅读 `MAINTENANCE.md`、`profiles/catalog.json` 和当前版本的 `REQUIREMENTS.md`。

## 当前事实来源

- 当前方案：`tiktok-sockstun-us`
- 当前稳定版本：`v1.0.0`
- 当前需求：R1–R8
- 当前版本覆写：`profiles/tiktok-sockstun-us/versions/v1.0.0/openclash-overwrite.conf`
- 兼容覆写入口：`overwrite/openclash-overwrite.conf`
- 共享人工直连规则：`rules/manual-direct.yaml`

若上述信息与 `profiles/catalog.json` 不一致，以通过仓库校验的 `profiles/catalog.json` 为准，并修正文档漂移。

## 不得擅自改变

1. TikTok 只由手机 SocksTun 通过固定的 IPRoyal ISP SOCKS5 代理；OpenClash 必须拒绝泄漏的 TikTok，不得回退到机场、直连或 OpenClash 本地 IPRoyal 节点。
2. 除 TikTok 外的国外流量最终走用户手工选择的机场美国节点。
3. 中国大陆域名和 IP 直连；`rules/manual-direct.yaml` 的现有条目必须保留。
4. Google 和 Google Play 必须在中国规则之前走`美国`，不得破坏已经验证的下载路径。
5. 私网和局域网必须直连。
6. 插件运行选项由用户在中文界面手工设置；覆写中不得加入 `[General]`。
7. 当前“禁用 QUIC”必须不勾选；“绕过中国大陆 IPv4”必须不勾选。
8. 不得把凭据、真实代理用户名、密码或未脱敏的私密地址提交到仓库。

## 允许直接修改

- 修正文档错别字、链接和不改变行为的说明；
- 在用户明确要求后，向 `rules/manual-direct.yaml` 增加经过确认的人工直连域名；
- 增加不会改变已发布版本内容的新版本目录或新方案目录。

## 必须先获得用户明确同意

- 修改规则顺序、DNS、TikTok 路径、`美国`策略组、运行模式、QUIC、区域绕过、IPv6 或 TUN；
- 删除、改名、重新分类或批量改写人工直连域名；
- 修改已经发布的 `profiles/*/versions/*`；
- 提升当前稳定版本、移动兼容覆写入口、创建或移动 Git 标签；
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
