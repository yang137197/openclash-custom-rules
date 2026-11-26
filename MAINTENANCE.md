# 仓库维护规范

## 不可变版本规则

正式版本 `tiktok-router-loongproxy-jp-us v1.0.0` 是本仓库第一版正式版。此前的历史版本及 beta 版本已从当前文件树、Git 标签和 GitHub Releases 清理；Git 提交历史保留。

每个方案（profile）独立维护 SemVer：同一方案的新候选版和正式版必须严格高于该方案已记录最高版本；禁止回退、复用或覆盖。不同方案的版本号互不比较，例如 A v1.0.0 与 B v1.0.0 可以同时存在。每个新版本必须在 `CHANGELOG.md` 增加同方案、同版本标题和具体更新内容。已发布版本目录、标签和 Release 不得改写；更新一律在对应方案内创建递增版本。

`AGENTS.md` 开头的专家角色和官方指南入口，以及正式版 `SETUP.md` 中的 OpenClash 设置建议，都是不可删除的仓库前提；任何整理不得删除或削弱这些内容。

需要本地模块的 Release 只附一个与版本目录模板逐字节一致、扩展名为 `.conf` 的可导入文件；OpenClash 官方本地模块上传器支持 `.txt`、`.conf`，因此 `.example` 不能作为最终附件扩展名。字段填写说明和虚构示例直接写在 Release 正文，不另附注释模板或填写指南。GitHub 自动生成的源码归档不能代替模板附件。

已发布的 v1.0.4 Release 仍保留其 `.conf.example` 附件及内容，不改写历史；需要使用该历史附件时，先将文件名改为 `.conf`。v1.0.5 正式版已将本地模块模板修正为 `.conf`。本次未在路由器文件选择器上实测，不声称通过该项实机测试。

用户于 2026-10-17 明确授权整理 v1.0.0 Release：保留原始模板附件与标签源码不变，删除额外注释模板及独立填写指南附件，并把填写映射和示例直接写入 Release 正文。该授权不涉及版本目录、配置或 Git 标签。

用户于 2026-10-17 明确要求在 v1.0.0 Release 正文中完整、单独显示标签固定的覆写订阅 URL，并同步根 README、方案 README 和后续开发规则。本次仅整理发布说明文案，不改写版本目录、标签或附件。

## 当前正式基线

当前唯一支持方案是 `tiktok-router-loongproxy-jp-us v1.0.8`（D1–D13，stable）。当前正式版 v1.0.8在v1.0.7之上完成原生双订阅重构，用户于2026-11-26确认验收通过；本轮日志、截图和实际环境记录见本版ENVIRONMENT.json。先前正式版本、标签和Release保留原样。

四组及其检测/路由边界见[需求合同](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.8/REQUIREMENTS.md)。TikTok首跳和默认代理为iKuuu日本自动低延迟，TikTok固定Loongproxy美国出口；良心云日本专线/高速按编号顺序故障回退。四组和提供商60秒/5000毫秒/204检测；GLOBAL不检测。没有独立控制器或服务安装。

## 配置与凭据

一套完整云模块和一套本地模块配对使用；云模块在本地上方，匹配同一配置完整路径。完整云模块订阅原main滚动地址，本地模块保存两个机场订阅和ISP参数。TikTok-ISP-Local保留socks5、udp:false、dialer-proxy: TikTok首跳。

不能把v1.0.8本地模块与v1.0.7云模块混用；旧云只有日本-入口，会造成dialer-proxy找不到TikTok首跳。修改ISP密码仅改本地模块，保存后重启OpenClash。

真实订阅和凭据不入仓；Release只附一个.conf占位模板，字段映射和虚构示例写在正文。已发布快照及历史.conf.example保留不可改写。模块只含[YAML]，不写UCI或自动调整插件开关。

## 永久维护流程

流程A：日常只在rules/manual-direct.yaml的payload增删改合法DOMAIN/DOMAIN-SUFFIX规则，校验格式及逐项同步，不固定域名清单、条数或源哈希，保留重复项。GitHub Actions生成同一滚动模块和catalog哈希并提交，成功后用户更新同一订阅并重启。无需新版本、CHANGELOG或Release；不改固定快照。manual-direct-isp.yaml不是日常入口。

流程B：大版本更新/重构在同方案创建更高候选，完成测试和实机验收后正式发布，并同步已验收内容到同一滚动模块及哈希。用户明确指定沿用现有版本线时，不另建profile或从v1.0.0开始。固定候选/标签地址用于测试与回退，不替代日常滚动订阅。流程A/B不得因一般开发、候选或文档整理删除或绕过。

当前稳定版本为 `v1.0.8`。已取得本轮日期明确的调试日志和用户验收；日志经脱敏且隐藏节点凭据，不把采样当作所有业务场景的独立播放证明。原始日志不入仓。禁用QUIC在实机为停用，本次保留该设置偏差。

## 每次变更门禁

先读AGENTS.md、DEVELOPMENT_RULES.md、README.md、catalog及相关版本需求/设置/环境。按永久流程A或B分别维护，检查隐私、不可变快照、模块哈希及链接，并运行：

```text
python -m unittest discover -s scripts -p "test_*.py"
python scripts/validate_repository.py --base-ref origin/main
git diff --check
```

正式发布门禁仍要求真实环境记录、日期明确的候选日志、用户验收及配对模块/设置记录，不得用静态或桌面测试代替；跨工具接续见DEVELOPMENT_RULES.md。
