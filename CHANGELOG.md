# 项目更新日志

本文件随每次发布或功能更新同步维护，记录实际行为变化和 OpenClash 应用要求。详细验证证据见 [`docs/acceptance-log.md`](docs/acceptance-log.md)。

## 2026-09-01

### 修复 Kimi API 开放平台无法访问

- 将 `platform.kimi.com` 精确加入手工日本规则，并保持在中国大陆直连规则之前。
- 仅调整 Kimi API 开放平台，不扩大到整个 `kimi.com`，避免影响当前可正常直连的 Kimi 其他服务。
- 本次只修改规则提供者文件；OpenClash 最迟约 60 秒自动更新，也可手动更新 `Linyang-Manual-JP`，无需重新更新覆写模块或重启。

### 删除 Microsoft 与 GitHub 专用分流

- 删除 `GEOSITE,microsoft,DIRECT`、`GEOSITE,onedrive,DIRECT`、`GEOSITE,xbox,DIRECT`。
- 删除 GitHub 按设备地区代理和未登记设备默认走“美国”的专用规则。
- Microsoft、GitHub 及相关域名现在不再由本模块特殊处理，依次按手工域名规则、中国大陆规则、设备地区规则及第三方订阅原规则匹配。
- GitHub Raw 仍作为覆写模块和规则提供者的下载地址；这些 URL 是更新来源，不是 GitHub 流量分流规则。
- 本次修改涉及覆写模块，更新后必须在 OpenClash 应用配置或重启一次。

### 部署更正：禁止使用 jsDelivr `@main` 获取实时覆写

- 实测 jsDelivr `@main` 仍返回旧覆写，其中含 7 条已删除的 Microsoft/GitHub 规则；固定提交 `@f78b82c` 与 GitHub Raw 主分支均为正确的新覆写。
- GitHub Raw 无法访问时，先用 README 中的固定提交地址恢复；应用并重启后再改回 GitHub Raw 主地址。
- OpenClash 中只保留一个本仓库覆写订阅，避免 Raw、jsDelivr 或旧缓存模块同时启用。
