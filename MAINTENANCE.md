# 版本与维护规范

## 当前维护范围

当前开发方案 `tiktok-router-loongproxy-jp-us v1.0.0`（J1–J12，candidate），另保留独立美国首跳候选 `tiktok-router-isp-us v1.0.0`（C1–C11）。清理旧方案后的文件树不含稳定入口，`profiles/catalog.json` 的 `currentProfile` 为 null；`developmentProfile` 指向日本首跳候选。

2026-10-16 用户授权删除停用旧方案的当前文件及引用；删除范围对应清理前提交 `dc39b92933164f71a4660321dfb5b62d7b172101` 中除上述两个保留方案外的 profile，以及其专用文档、规则和根兼容模块。Git 历史、标签、Release 不动。校验只对这批整体退役目录豁免删除，禁止借此修改或删改其他已发布快照。

## 方案和版本

每个方案使用独立 ID、需求合同、版本目录、完整覆写及 URL。候选在实机验收前保持 candidate、currentVersion=null；清理旧目录不构成稳定晋升。新稳定发布必须有明确授权，提交、推送并创建 `<profileId>-v<version>` 标签，标签指向包含完整配置和文档的提交；不可移动旧标签。

单个机场配置只启用一个完整云模块与一个配套本地节点模块；本地模块仅追加代理节点，不管理规则或插件选项。真实凭据只存用户授权的仓库外文件和路由器，公共库仅存 `.example` 占位模板。

## 规则与节点

`rules/manual-direct.yaml` 保留原 129 条记录。`rules/manual-direct-isp.yaml` 是按原顺序将每条 DOMAIN 转为 DOMAIN-SUFFIX 的副本，已有重复记录不合并。变更域名需明确授权，并同步两个保留候选的固定模块、滚动模块、inline payload 和 catalog 哈希。用户仅刷新所用云覆写并重启，不单独刷新 Manual-Direct provider。

日本组通过 `include-all: true` 从已加载的 proxies/proxy-providers 选择名称含 `jp`、`日本`、`Japan`、🇯🇵 的节点，忽略大小写；不要求完整节点名。匹配自动完成，实际使用哪个节点仍手选。筛选不代替机场订阅，不证明供应商身份或连通性；无匹配节点保持 REJECT。不得加入 DIRECT 或其他地区作 TikTok 回退。

模块只能有 `[YAML]`。OpenClash 插件开关由用户在中文 LuCI 界面手工设置；按官方指南路由子文档核对路径及含义。不得写入 `[General]`、UCI 或自动插件设置逻辑。

## 变更门禁

1. 阅读 AGENTS、索引和对应 REQUIREMENTS，标明影响需求和候选/稳定类型。
2. 更新设置说明、需求合同与 CHANGELOG；核对规则源、inline、滚动和固定模块一致。
3. 安装 `scripts/requirements-validation.txt` 的依赖后，运行 `python -m unittest discover -s scripts -p "test_*.py"`、`python scripts/validate_repository.py --base-ref origin/main`、`git diff --check`，审查全部差异。无 Git 比较基线时可省略 `--base-ref`，但不能据此声称历史保护校验已运行。
4. 不把 YAML/静态/桌面内核夹具结果当作目标 OpenClash 实机验收。真实链路、出口、App 行为及失败关闭仍需手机证据。
5. 提交前检查凭据；PR 保持 draft/candidate，除非已完成实机验收且得到发布授权。

只记录长期有效的合同、限制、版本与验证结论，不保留冗长试错记录。
