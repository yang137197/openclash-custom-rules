# 版本记录

## tiktok-router-loongproxy-jp-us v1.0.0 — 2026-10-16

状态：candidate，影响 J3/J4/J6/J8–J12；未完成目标 OpenClash 与手机验收。

- 日本第一跳、本地 Loongproxy 美国 SOCKS5 出口；TikTok 不回退机场或 DIRECT，其他境外流量仍手选美国。
- 用户要求自动纳入日本节点。名称筛选放宽为任意位置的 `jp`、`日本`、`Japan`、🇯🇵，忽略大小写，覆盖已加载的顶层节点和代理提供商；仍手选首跳、空组 REJECT，不索要完整节点名。
- 按用户明确授权，移除停用旧方案及关联按设备方案、兼容入口、专用规则、文档、catalog 和校验依赖。当前文件树不再提供稳定入口；Git 历史、已有标签和 Release 保留，候选未晋升。
- 保留不可删除的 OpenClash 专家角色和官方指南入口。保留全部 129 条原始人工规则及后缀副本，云模块 inline 与源一致，刷新一个模块并重启即可更新。
- 接续审查修复候选 YAML 未闭合引号和重复块，新增严格 YAML/重复键解析与回归检查。校验按保留的两个候选检查规则顺序、DNS、节点模板、哈希与单模块刷新。
- 私有交付文件放仓库外；未合并 main、未发布稳定版、未操作路由器配置。验证结果与限制见本候选 REQUIREMENTS。

## tiktok-router-isp-us v1.0.0 — 2026-10-15

状态：candidate，C1–C11。独立的机场美国首跳 → 路由器本地 Loongproxy SOCKS5 → TikTok，尚未通过手机实机验收。

- 完整云覆写只匹配精确本地节点 `TikTok-ISP-Local`，专用 DNS、专属组及紧邻 REJECT 保持失败关闭。
- Google/Play 先于中国分类走美国；私网、已知大陆域名/IP 和 Manual-Direct 直连。
- 从原始 129 条记录生成完整 DOMAIN-SUFFIX 副本并内嵌；真实代理地址与账号密码只在本地模块保存。

退役方案的旧版本记录可从原 Git 历史与标签核验。
