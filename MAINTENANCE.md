# 版本与维护规范

> 独立候选 `tiktok-router-loongproxy-jp-us v1.0.0`：iKuu 日本入口、Loongproxy 美国 ISP 本地节点。历史稳定版本不改写；保留 129 条 Manual-Direct，滚动模块和规则源同次提交同步；公共仓库绝不存 ISP 凭据；远程覆写刷新后需重启 OpenClash。

## 维护模型

本仓库使用“方案 → 版本 → 完整覆写”的关系：

```text
一组完整需求
  → 一个方案 ID
    → 一个稳定版本
      → 一个完整覆写模块
```

一条需求不单独对应一个可叠加的完整覆写。规则和 DNS 存在顺序依赖，同时启用多个完整方案覆写可能相互覆盖。不同需求集合如果互斥，应建立不同方案；同一方案的兼容升级应建立新版本。

## 多方案隔离

仓库可以同时维护 A–D 等多个方案，但必须满足：

- 每个方案拥有唯一方案 ID，例如 `profile-a`、`profile-b`；
- 每个方案拥有独立需求合同、版本目录、完整覆写和固定 URL；
- Git 标签使用 `<方案ID>-v<版本号>`，避免不同方案都使用 `v1.0.0` 时冲突；
- 单个 OpenClash 配置只启用一个方案覆写，不得把 A、B 两个完整覆写同时启用；
- 根目录兼容覆写只对应 `profiles/catalog.json` 的 `currentProfile`；其他方案必须使用自己的固定 URL；
- 只有人工直连需求完全相同的方案才允许共享 `rules/manual-direct.yaml`，否则必须使用方案专属规则文件。

当前 `v1.0.0` 是首个方案已经发布的历史标签，继续保留且不得移动。后续版本和新方案一律使用方案专属标签，例如 `tiktok-sockstun-us-v1.0.1`、`profile-b-v1.0.0`。

## 版本号规则

技术依据为 OpenClash 用户指南及其路由子文档；仓库维护的是域名与出口意图、版本状态和验收事实，旧版运行设置不是新方案的永久技术约束。`v2.0.0` 是本次获授权且经用户确认验收的主版本架构正式版：启用大陆 IPv4 旁路、重写 DNS/Fake-IP 过滤；`v2.0.0` 现为当前稳定版并接管兼容入口，`v1.0.0` 保留不可变回退快照。

使用语义化版本：

- 修订号，例如 `v1.0.1`：保持需求不变的规则修复、人工直连规则调整或配置缺陷修复；
- 次版本，例如 `v1.1.0`：增加兼容的新需求，不改变已有需求；
- 主版本，例如 `v2.0.0`：改变既有核心需求、出口路径、运行架构或产生不兼容行为；
- 纯文档措辞修正且不改变配置、建议设置或验收要求时，可以只记录提交，不提升方案版本。

## 文件职责

- `profiles/catalog.json`：当前方案、版本、状态和文件映射的机器可读事实来源；
- `profiles/<方案>/versions/<版本>/openclash-overwrite.conf`：发布后不再修改的完整覆写；
- `profiles/<方案>/versions/<版本>/REQUIREMENTS.md`：该版本的冻结需求、界面设置和验收标准；
- `profiles/tiktok-hybrid-device-us/`：按设备区分 TikTok 出口的独立稳定方案；不得与 `tiktok-sockstun-us` 的覆写混用；
- `overwrite/openclash-overwrite.conf`：兼容入口，内容必须与当前稳定版本覆写一致；
- `rules/manual-direct.yaml`：当前生效的人工直连数据；每次修改都必须形成新版本，以便由 Git 标签恢复历史快照；
- `CHANGELOG.md`：版本级长期记录，不保存排查流水；
- `AGENTS.md`：未来维护者必须遵守的修改边界；
- `scripts/validate_repository.py`：版本与行为一致性检查；通过固定版本 PyYAML 实际解析全部覆写和规则源，拒绝重复映射键。首次执行前运行 `python -m pip install -r scripts/requirements-validation.txt`。重复的域名列表条目仍保留，不与重复 YAML 键混淆。

`tiktok-sockstun-us` 的既有覆写通过 HTTP Rule Provider 引用 `main/rules/manual-direct.yaml`。已弃用的 `tiktok-router-iproyal-us` beta.3 使用 inline payload，作为历史快照保留。当前 `tiktok-router-isp-us` 使用独立 `rules/manual-direct-isp.yaml`：完整保留共享源的 129 条规则并统一改为 `DOMAIN-SUFFIX`，覆盖条目及全部子域名；完整云覆写的 inline payload 和滚动模块必须与该方案专属规则源在同一提交同步，路由器只刷新该完整覆写并重启，不单独刷新 Rule Provider。不得因此改写其他方案共用的 `rules/manual-direct.yaml`。

## 覆写模块边界

- 覆写模块只能出现一个配置段：`[YAML]`；
- `[YAML]` 只维护 Mihomo 最终配置中的 DNS、策略组、规则集和规则；
- 绝对不得加入 `[General]`；
- 不得写入 UCI 命令、OpenClash 插件选项或自动改变运行模式、QUIC、区域绕过、IPv6、TUN 等界面设置的脚本；
- 所有 OpenClash 插件选项必须由用户依据 README 和版本 `REQUIREMENTS.md` 在中文界面手工设置。

该边界不因版本升级或方案新增而改变。若未来插件格式发生变化，也必须先由用户明确确认新的手工设置方式，不能默认改为自动写入。

## 状态定义

`developmentProfile` 指向最新授权开发方案，`currentProfile` 仍指向已发布稳定方案。新独立方案可以 `status=candidate`、`currentVersion=null`，在 `candidateVersions` 内声明合同与文件；不得为了通过旧校验而伪造稳定版本。当前 `tiktok-router-loongproxy-jp-us v1.0.0` 使用 J1–J12，旧 `tiktok-router-isp-us v1.0.0` 保留 C1–C11；两者不继承旧 R1 的手机 SocksTun 路径。只追加节点的本地凭据模块可与一套完整分流模块配合，不属于叠加两套完整方案；按用户授权生成的本机交付文件必须放在仓库外，凭据模块不得提交仓库。

历史：`tiktok-router-iproyal-us v1.0.1` 曾针对 IPRoyal 直连拨号超时尝试机场美国首跳；后续 IPRoyal beta 快照均保留，但用户现已明确弃用这条候选，不再用于测试或维护入口。

`tiktok-router-iproyal-us v1.0.2-beta.1` 在 v1.0.1 链式候选上新增精确直连域名 `d-gm.mmstat.com`，保持共享人工直连列表的其他条目。候选可使用语义化预发布版本号和 GitHub pre-release 标签供用户验收；仍保持 `candidate`，不得移动稳定入口。beta 版本目录与共享规则文件都纳入该标签，发布后不得改写。

`tiktok-router-iproyal-us v1.0.2-beta.2` 将 mmstat 直连扩展为 `DOMAIN-SUFFIX,mmstat.com`，覆盖主域名及全部子域名；已有阿里妈妈规则由 `DOMAIN-SUFFIX,alimama.com` 覆盖其子域名。beta.1 和 beta.2 均为不可改写的预发布快照，后续调整须新增版本目录和标签。

- `candidate`：配置已经进入仓库，但真实 OpenClash 或应用验收尚未完成；
- `stable`：配置加载成功，并完成该版本 `REQUIREMENTS.md` 中的实际验收；
- `deprecated`：仍保留用于恢复，但不再建议新安装使用。

同一方案可有互不合并的候选。目录索引中的 `kind=guide-mainland-bypass` 表示 v2.0.0 指南架构版本，需求为 R1–R8、R11–R12，不继承 v1.1.0 的 R9/R10 日本需求。校验器必须按对应版本合同检查，不得把所有候选都当成日本扩展。

覆写与插件手工设置必须成套验收和回退。v2 的 DNS `rule` 过滤、Google/TikTok 例外优先级、CN MRS 和大陆防火墙列表均须核对；核心面板看不到旁路连接不是失败证据。旧 README 设置归档在 `docs/legacy-v1-setup.md`，不作为 v2 设置标准。

只有一个版本可以作为某个方案的当前稳定版本。兼容覆写入口只能对应该版本。

## 新版本流程

1. 从当前稳定版本复制到新的版本目录，不修改旧目录。
2. 在新版本 `REQUIREMENTS.md` 中列出继承、增加、修改和删除的需求。
3. 修改新版本覆写；如果准备提升为当前版本，同时同步兼容覆写入口。
4. 如果修改人工直连规则，同时修改 `rules/manual-direct.yaml`。
5. 对 `tiktok-router-isp-us` 及后续版本，同一提交把 `rules/manual-direct-isp.yaml` 的 payload 同步到方案专属滚动模块及新候选模块；`validate_repository.py` 必须逐条检查一致，并保证每条都使用 `DOMAIN-SUFFIX`，确保用户只需刷新完整覆写模块。
6. 更新 `profiles/catalog.json` 和 `CHANGELOG.md`，先将新版本标记为 `candidate`。
7. 运行：

   ```text
   python scripts/validate_repository.py
   git diff --check
   ```

8. 由用户在真实环境完成版本需求中的验收。没有实际验收，不得写“稳定”或创建稳定标签。
9. 验收通过后改为 `stable`，提交并推送所有文件。
10. 创建 `<方案ID>-v<版本号>` 格式的 Git 标签并推送；回读远端分支和标签，确认都指向预期提交。

## 兼容覆写和固定版本覆写

- 固定版本 URL 适合稳定使用，不会自动跨版本升级；升级时需要用户主动换成新版本 URL。
- `main/overwrite/openclash-overwrite.conf` 是兼容入口，只在用户明确批准版本提升后更新。
- 两个 URL 不能同时作为模块启用。
- v2.0.0 正式发布已将兼容入口更新到新架构；仍使用远程兼容入口的旧设备须先按 v2 SETUP.md 核对插件设置，不能只刷新模块。已验收的本地 v2 候选无需重设开关。

## 回滚

1. 在 `CHANGELOG.md` 找到上一个稳定版本。
2. 使用该版本 Git 标签下的固定覆写 URL。
3. 如果需要恢复当时的人工直连列表，从同一标签读取 `rules/manual-direct.yaml`；恢复属于配置变更，必须先取得用户同意。
4. 重新执行该版本 `REQUIREMENTS.md` 中的验收。

禁止通过删除新版本、重写旧标签或修改旧版本目录来“回滚”。

## 按设备分流的版本边界

按来源 IP 放行 TikTok 属于路由行为，不是普通运行参数。设备必须先通过 DHCP 固定地址；增加、删除或更换授权 IP 时，必须创建该方案的新候选版本，更新需求合同、目录、目录索引和变更记录，再进行真实设备验收。不得直接改写已经发布的版本，也不得使用整个局域网网段替代精确 `/32` 地址。

## 更换开发电脑

新电脑只需要克隆仓库，不依赖旧电脑上的聊天、本地笔记或隐藏文件：

1. 阅读 `AGENTS.md`；
2. 阅读 `profiles/catalog.json`，确定当前方案和版本；
3. 阅读对应 `REQUIREMENTS.md` 和 `CHANGELOG.md`；
4. 运行 `python scripts/validate_repository.py`；
5. 检查当前分支、`git status`、最近提交和标签；
6. 在任何修改前列出受影响需求。

如果仓库文档与设备实际状态冲突，停止修改并以新的实时证据重新核对；不得用旧电脑上的未提交信息覆盖仓库。
