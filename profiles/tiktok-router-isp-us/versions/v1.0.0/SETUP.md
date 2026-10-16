# tiktok-router-isp-us v1.0.0 — OpenClash 候选测试

**状态：candidate，未完成实机验收。** 本测试在手机上经 OpenClash 验证 TikTok；无需在 PC 配置代理或做网络测试。此方案由一份完整云覆写和一份只追加本地 TikTok SOCKS5 节点的模块组成。

## 文件

- 完整分流覆写：[openclash-overwrite.conf](openclash-overwrite.conf)。发布后滚动订阅地址为：
  `https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-isp-us/overwrite/openclash-overwrite.conf`
- 本地节点模板：[local-tiktok-proxy.conf.example](local-tiktok-proxy.conf.example)，仅供参考，不能填入占位符后直接启用。
- 含你已提供测试凭据的本地文件：`C:\Users\yang1\AppData\Local\Temp\openclash-loongproxy-tiktok-local.conf`。只上传到路由器，不要提交到仓库、云订阅或其他网站。

## 安装前

1. 在 OpenClash「配置管理」备份当前配置。
2. 在「运行状态 → 覆写模块」里停用其他 TikTok 完整覆写，停用旧本地 ISP 节点及其链式补丁。保留文件即可，不要把两套完整方案同时启用。
3. 确认当前`美国`策略组已手动选中一个可用机场节点。

## 添加两个模块

入口是 **服务 → OpenClash → 运行状态 → 顶部「覆写模块」按钮**，不是「覆写设置」。

1. 点击「+ 添加新模块 → 本地模块」，上传上述本地文件。模块名可用 `TikTok-ISP-Local`；匹配配置填写完整路径 `/etc/openclash/config/ikuu.yaml`（如果实际启用的文件名不同，按「配置管理」显示的文件名替换）。启用模块。
2. 再点击「+ 添加新模块 → 订阅链接」，填上方云覆写 URL。若订阅暂时无法下载，先用本目录 `openclash-overwrite.conf` 作为本地模块上传；确认滚动 URL 可访问后再换为订阅模块。匹配配置使用同一完整路径。
3. 确认模块列表中**完整云覆写在本地节点模块上方**。OpenClash 按列表从下向上执行；这样本地 `proxies+` 节点先进入配置，云模块再建立只匹配该节点名的 TikTok 组。
4. 两个模块都启用后，点运行状态页的 **重启 OpenClash**。保存或启用模块本身不会立即重建运行配置。

本地文件的节点名必须精确为 `TikTok-ISP-Local`，且 `dialer-proxy` 指向 `美国`。不要把节点名改成含美国节点筛选关键字的名字；`美国`组排除该精确本地节点，防止链式拨号回环。

## 插件界面设置

本方案只在 YAML 中改路由，不写 OpenClash UCI 开关。Fake-IP 增强、规则模式、大陆 IPv4 绕过、DNS 转发、DNS/Meta 选项和 Geo 数据更新，参照 [日本首跳候选设置说明](../../../tiktok-router-loongproxy-jp-us/versions/v1.0.0/SETUP.md#独立手工设置) 的「独立手工设置」表（仅共享插件开关；本方案节点仍经美国组）。若你的界面或 Mihomo 内核不支持规则型 Fake-IP 过滤或 CN MRS，先停在此处，不要凭猜测换选项。

本候选不要求手工添加 ISP 服务器到“本地 IPv4 网络绕过列表”。这里的本地 TikTok 节点显式配置 `dialer-proxy: 美国`，设计目标是由机场美国节点链式拨号。

## 启动后核对

在「运行状态」的运行配置或仪表盘确认：

- `TikTok-ISP` 组只含 `TikTok-ISP-Local`，手动选择该节点；组状态应为 `1/1`，当前选中节点不能是 `REJECT`。
- `美国`组仍能手选机场美国节点，且不含 `TikTok-ISP-Local`。
- `TikTok-ISP-Local` 的 SOCKS5 节点有 `dialer-proxy: 美国`；TikTok 规则之后紧跟 `GEOSITE,tiktok,REJECT`。
- `Manual-Direct` 是 `type: inline`，共 129 条，均为 `DOMAIN-SUFFIX`，无独立 URL/path/interval。
- 没有 YAML、DNS、未知字段或代理组缺失错误。

如果 `TikTok-ISP` 面板再次显示 `REJECT` 或不是 `1/1`，先停止 TikTok 测试：这表明运行配置没有把精确本地节点纳入组；此时尚未证明 LoongProxy 端点连接成功或失败。

## 手机验收

1. 手机连 OpenClash 路由器 Wi-Fi，关闭移动数据和手机 VPN；关闭并重新打开 TikTok，产生新连接。
2. 连续刷新推荐页、打开视频播放至少数分钟。在 OpenClash 连接/运行日志中确认 TikTok 域名命中 `TikTok-ISP` 且实际使用 `TikTok-ISP-Local`；观察流量计数是否增长。无需用代理测速值判断 SOCKS5/TikTok 是否正常。
3. 在同一手机检查一个常用中国大陆网站和一个境外网站：前者应命中 CN/`Manual-Direct` 并走 `DIRECT`，后者应走手选的`美国`机场节点。Google Play 下载仍走`美国`。
4. 若日志显示 `TikTok-ISP[REJECT]`，优先检查模块是否都启用、完整路径是否匹配、模块顺序与节点名是否精确。若显示 `dial TikTok-ISP-Local ... timeout`，说明规则已选本地节点但链路未连通；保留该条脱敏日志。若命中本地节点、连接成功且 TikTok 可播放，才算本次业务路径通过。
5. 验收失败关闭：停用本地节点模块并重启，TikTok 新连接应命中紧随规则的 `REJECT`，不得转到`美国`或 `DIRECT`；随后恢复模块并重启。

## 回退

停用这两个候选模块并重启 OpenClash，再启用原来的一套完整稳定方案。不要同时启用候选完整覆写和其他完整覆写。实机验收完成前，本方案保持 candidate，不创建稳定标签、不替换兼容入口。
