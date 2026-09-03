# 项目更新日志

本文件随每次发布或功能更新同步维护，记录实际行为变化和 OpenClash 应用要求。详细验证证据见 [`docs/acceptance-log.md`](docs/acceptance-log.md)。

## 2026-09-03

### 修复未登记设备无法访问 Docker Hub

- 新增独立 `Linyang-Docker` 规则集，覆盖 `docker.io`、Docker 官方当前使用的 CloudFront 下载域名，以及现场出现的 Cloudflare/Cloudflare Storage 镜像链路。
- 新增 `Docker-自动`，仅收集日本、美国、新加坡节点并按 Docker Registry 实际可达性选择，不改变设备地区规则或最终 `MATCH,DIRECT`。
- Docker 规则集强制通过海外 DoH 解析，避免直连解析路径返回与 Docker 无关的异常地址。
- Docker 自动测速改用 Registry `/v2/`，并将其正常的 HTTP 401 设为预期状态，避免根路径 HTTP 404 把可用节点误判为失败。
- README 的一次性恢复地址固定到包含完整 Docker 修复的提交 `edb4098`，避免继续加载旧提交 `aea596f`。
- 此为覆写模块变更；更新覆写订阅后必须应用配置或重启一次 OpenClash。

## 2026-09-02

### 修复 GitHub 被第三方 Microsoft 规则直连

- 在所有第三方订阅规则之前增加 `GEOSITE,github` 分流，避免 GitHub 被订阅的 `GEOSITE,microsoft,DIRECT` 提前命中。
- 已登记设备分别跟随日本、美国、新加坡；未登记设备默认“日本”，确保 GitHub 不会直连。
- README 的一次性恢复地址固定到当前已验收提交 `aea596f`，避免旧运行配置下载 GitHub Raw 时再次被直连阻断。
- 此为覆写模块变更。更新覆写订阅后，必须应用配置或重启一次 OpenClash；日志应显示 `GeoSite(github)`，而不是 `GeoSite(microsoft) using DIRECT`。

### 补充 GitHub 应急规则与默认直连兜底

- 将 GitHub 核心域名加入 `rules/manual-jp.yaml`。即使路由器仍运行旧覆写，只要规则提供者刷新，手工日本规则也会先于第三方 Microsoft 直连规则命中。
- 在覆写规则结尾新增 `MATCH,DIRECT`，使未登记设备和未列出域名默认直连，不再使用第三方“漏网之鱼”节点。
- `Linyang-Manual-JP` 可手动刷新或等待约 60 秒；`MATCH,DIRECT` 仍需更新覆写订阅并应用/重启才生效。

## 2026-09-01

### 更正 Kimi：保持中国大陆直连

- 撤回上一版把 `platform.kimi.com` 分配到“日本”的临时绕行规则。
- 在手工直连规则加入 `DOMAIN-SUFFIX,kimi.com` 和 `DOMAIN-SUFFIX,moonshot.cn`，覆盖 Kimi 官网、开放平台及官方 API。
- 多个公共 DNS 均返回同一 CNAME 和 IPv4 地址，且目标 TCP 443 可建立连接；当前故障发生在直连 TLS 握手阶段，不应通过海外代理掩盖。
- 直连规则发布并刷新后，开放平台首页、控制台和文档均返回 HTTP 200；无需修改 MTU、IPv6、证书校验或 Fake-IP 设置。
- 本次只修改规则提供者文件；OpenClash 最迟约 60 秒自动更新，也可手动更新 `Linyang-Manual-Direct` 和 `Linyang-Manual-JP`，无需更新覆写模块或重启。

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
