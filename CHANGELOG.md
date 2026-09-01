# 项目更新日志

本文件随每次发布或功能更新同步维护，记录实际行为变化和 OpenClash 应用要求。详细验证证据见 [`docs/acceptance-log.md`](docs/acceptance-log.md)。

## 2026-09-01

### 删除 Microsoft 与 GitHub 专用分流

- 删除 `GEOSITE,microsoft,DIRECT`、`GEOSITE,onedrive,DIRECT`、`GEOSITE,xbox,DIRECT`。
- 删除 GitHub 按设备地区代理和未登记设备默认走“美国”的专用规则。
- Microsoft、GitHub 及相关域名现在不再由本模块特殊处理，依次按手工域名规则、中国大陆规则、设备地区规则及第三方订阅原规则匹配。
- GitHub Raw 仍作为覆写模块和规则提供者的下载地址；这些 URL 是更新来源，不是 GitHub 流量分流规则。
- 本次修改涉及覆写模块，更新后必须在 OpenClash 应用配置或重启一次。
