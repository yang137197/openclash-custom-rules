# tiktok-router-loongproxy-jp-us v1.0.8 — 候选需求合同

状态：**candidate，待实机验证**。继承 v1.0.7 的 J1–J11、J13–J21；日本首跳、TikTok 失败关闭和 GitHub 走美国组的约定继续有效。

- J22：仅对精确主机名 `api.github.com` 增加 Fake-IP 规则模式的 `real-ip` 例外，使需要校验公网解析结果的 NEXUS 版本发现可以取得非 Fake-IP 地址。该 DNS 规则不改变 GitHub 已有的美国组连接规则；不把该域名加入 Manual-Direct 源。

## 验收条件

1. 候选模块相对 v1.0.7 固定快照，仅新增一条 `DOMAIN,api.github.com,real-ip` DNS 规则；其余 DNS 条目、分流规则、代理组及本地节点模板保持不变。
2. 候选在路由器应用后，NEXUS API 容器解析该域名应返回通过 NEXUS 公网地址校验的 IPv4；随后只检查独立的版本通知测试服务，验证发现版本及微信实际收件。DNS 上游返回无效地址或访问失败时停止，不更改 NEXUS 的地址安全检查。
3. 核对 GitHub 新连接仍命中美国组，TikTok 使用原有链路；不能以静态测试代替路由器实测。
4. 测试通过并由本人确认前保持 candidate；不改写 v1.0.7 标签、文件或 Release。调试日志仅摘录非敏感事实，不提交原始日志。

候选以 v1.0.7 固定快照为基线，与本人日志中的固定版本下载入口一致。当前 GitHub `main` 的动态 Manual-Direct 源包含后续维护变更；正式发布或同步滚动入口前必须重新核对并合并该源，不能用旧快照覆盖它。
