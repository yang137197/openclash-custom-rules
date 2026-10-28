# tiktok-router-loongproxy-jp-us v1.0.7 — 候选需求合同

状态：**candidate，等待用户验收**。本候选继承 v1.0.0 的 J1–J11 基础合同及 v1.0.6 的 J13–J17 已验收行为，只调整规则源与滚动覆写的同步架构，不改变分流出口、规则优先级、DNS、代理链路或 OpenClash 插件设置。Loongproxy 仍必须通过用户手选的 iKuuu 日本节点作为第一跳，不得换用美国首跳或其他机场首跳；链路缺失时仍失败关闭。候选模块的静态规则语义须与 v1.0.6 相同。

## 继承要求

继承当前稳定版 `v1.0.6` 的 J1–J11、J13–J17、规则顺序、iKuuu 日本首跳、失败关闭、本地凭据边界和 OpenClash 设置建议。需求原文与现有设置见 [v1.0.6 REQUIREMENTS.md](../v1.0.6/REQUIREMENTS.md) 和 [v1.0.6 SETUP.md](../v1.0.6/SETUP.md)。

## 本候选新增要求

- J18：`rules/manual-direct.yaml` 是手动直连规则唯一可编辑源。`payload` 中的 `DOMAIN-SUFFIX,example.com` 匹配主域名及其全部子域名；`DOMAIN,host.example.com` 只匹配该精确主机名。手动维护者可在该文件中添加、修改或删除条目，保留重复项不阻止同步。提交到 GitHub `main` 后，GitHub Actions 从此源生成滚动完整覆写中的 `Manual-Direct!` inline payload，并同步 `profiles/catalog.json` 的滚动模块 SHA-256；不要求逐条手改覆写模块或维护 `manual-direct-isp.yaml`。
- J19：手动源修改触发自动同步工作流；工作流必须先生成并验证滚动模块和哈希，成功后才提交生成文件。失败时不得将不同步的源文件状态视为已部署。该流程不创建版本或 Release，也不改写任何固定版本快照。
- J20：日常规则变更完成同步后，路由器继续使用同一个 `main` 远程完整覆写地址。用户在 OpenClash 远程覆写模块点击“更新”，然后重启 OpenClash；无需单独更新 Manual-Direct provider 或机场节点订阅。被源文件删除的条目须在新覆写应用后从滚动规则中消失。
- J21：本候选对当前 130 条记录的有效路由语义保持不变。历史 129 条在运行 provider 中均按 `DOMAIN-SUFFIX` 生效；其中源文件原标为 `DOMAIN` 的记录在本候选中统一规范为 `DOMAIN-SUFFIX`。`huzhou.host` 从独立规则移入同一 inline payload，仍在 Google 规则之后、CN 规则之前生效。源列表和候选模块必须通过回归检查证明这一等价关系。

## 验收条件

1. 候选版 inline payload 与 `rules/manual-direct.yaml` 的 `payload` 逐项、按顺序一致。
2. 添加、修改、删除源文件条目的生成器夹具分别确认滚动覆写同步；精确域名和后缀域名保持各自匹配类型，重复条目不丢失。
3. 候选滚动模块保留 v1.0.6 的其他 YAML 配置与规则优先级，唯一的规则结构差异为 J21 所述的 Manual-Direct 数据归一化和收拢。
4. GitHub Actions 在源文件提交后自动生成滚动模块及哈希；只有工作流成功后，用户才刷新远程覆写并重启 OpenClash。
5. 路由器侧候选更新、重启和现有流量验收由用户执行；目前尚未验收，须如实记录结果后再决定是否发布正式版。

## 边界

J18–J21 只规范手动域名数据的维护和同步，不授权修改其他策略规则、DNS、策略组、代理链路或插件设置。完整云覆写仍使用远程模块；唯一的本地模块仍为 `tiktok-router-loongproxy`。真实代理凭据不得进入仓库。
