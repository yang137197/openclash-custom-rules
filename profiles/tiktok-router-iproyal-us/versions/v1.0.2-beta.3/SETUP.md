# 所有手机经 OpenClash → 机场首跳 → IPRoyal → TikTok

适用：tiktok-router-iproyal-us v1.0.2-beta.3 beta/candidate。本版保留 v1.0.2-beta.2 的分流、链式拨号与人工直连域名，并将 Manual-Direct 全部规则内嵌到完整覆写模块。真实 OpenClash 与设备验收仍需完成；手机无需 SocksTun。

## 一次切换到单模块同步

Manual-Direct 使用 Mihomo type: inline，其 129 条 payload 与仓库 rules/manual-direct.yaml 一致。以后仓库更新人工直连规则时，模块正文也随同更新；用户只需刷新这个覆写模块并重启 OpenClash，不需要单独更新 Rule Provider 或调用 API。刷新后重启是 OpenClash 应用覆写正文的要求。

方案专属滚动订阅地址（后续仓库规则更新后仍使用同一地址刷新）：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-iproyal-us/overwrite/openclash-overwrite.conf

beta.3 固定快照地址（仅用于复现本候选，后续规则更新不会改变该 URL 的内容）：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/v1.0.2-beta.3/profiles/tiktok-router-iproyal-us/versions/v1.0.2-beta.3/openclash-overwrite.conf

已有订阅模块需要一次性把模块订阅 URL 改为上面的方案专属滚动地址，然后点该模块的刷新按钮并重启 OpenClash。不要启用第二份完整分流模块；已有本地 IPRoyal 节点和链式补丁按本文件后续步骤保留。若当前是本地模块，它没有远程订阅 URL，需上传新的完整模块，之后才能按订阅刷新。

仓库维护时仍以 rules/manual-direct.yaml 为规则源；同一提交更新滚动模块的 inline payload，仓库校验会阻止两份规则不一致。

## 依据和边界

用户的脱敏实机日志已显示 TikTok 域名命中 `TikTok-ISP`，但直连 IPRoyal SOCKS5 端口反复出现 `dial tcp ... i/o timeout`；这证明拨号失败，不证明域名分流错误，也不足以确定是大陆封锁、运营商路由或 IPRoyal 服务端故障。[IPRoyal 官方 Shadowrocket 故障教程](https://help.iproyal.com/zh-CN/articles/10667956-%E5%A6%82%E4%BD%95%E4%B8%BA-shadowrocket-%E4%BD%BF%E7%94%A8-iproyal-%E4%BB%A3%E7%90%86)先建议把该客户端的 Proxy Method 从 Auto 改为 Random，仍失败再通过其 Shadowsocks 服务器连接 IPRoyal。该教程只说明 Shadowrocket，且对其提供的 Shadowsocks 服务器有限定；不能将它说成官方 OpenClash 或第三方机场配置。

本候选是基于官方双跳思路的 **OpenClash/Mihomo 适配试验**：`dialer-proxy: 美国` 让 IPRoyal 节点通过现有机场美国策略组建立连接。Mihomo 的[官方 `dialer-proxy` 文档](https://wiki.metacubex.one/config/proxies/dialer-proxy/)明确支持将代理节点连接交给另一节点或策略组。第一跳和 IPRoyal 的兼容性尚未实机验证；机场若不允许访问 IPRoyal 端口，仍会失败。

## 已有本地节点：直接上传无凭据补丁

1. 在 **服务 → OpenClash → 运行状态 → 顶部「覆写模块」** 打开模块窗口，选择 **添加新模块 → 本地模块**，上传同目录的 [iproyal-chain-hop.conf](iproyal-chain-hop.conf)。匹配配置填写当前机场配置的**完整路径**；只写文件名不会匹配。
2. 启用新模块，把它拖到现有本地 IPRoyal 节点模块的**上方**。模块列表越靠上越晚合并；补丁必须在原节点追加之后执行。保留现有唯一的 `v1.0.0` 完整分流模块，勿再叠加一份完整分流模块。
3. 先在仪表盘确认`美国`组已手选一个可用机场美国节点，且组内不含 `IPRoyal-US-ISP`。保存后到运行状态页点 **重启 OpenClash**，不是仅重载防火墙。

补丁只对顶层 `proxies` 中精确名为 `IPRoyal-US-ISP` 的节点写入 `dialer-proxy: 美国`，不含地址、账号、密码、规则或插件开关。节点缺失时补丁无操作；完整分流模块中的 TikTok 空组拒绝与同类拒绝规则仍须保留。

## 新建节点的情况

若本地 IPRoyal 节点尚未创建，需在路由器本地建立只追加节点的模块。下方是**待填写模板，不能原样上传启用**；地址、SOCKS5 端口、代理用户名和新密码由用户在本机填写。凭据中的单引号要写成两个单引号。使用本模板时**不要同时启用上面的无凭据补丁**。

```ini
[YAML]
proxies+:
  - name: IPRoyal-US-ISP
    type: socks5
    server: '填写订单服务器地址'
    port: 填写订单SOCKS5端口整数
    username: '填写代理用户名'
    password: '填写新代理密码'
    udp: false
    dialer-proxy: 美国
```

此前截图中曾出现代理凭据，建议在 IPRoyal 后台重置后只更新路由器本地模块；不要上传含凭据的文件到 GitHub、订阅转换站或聊天。

## 完整分流与插件设置

全新部署时同目录 [openclash-overwrite.conf](openclash-overwrite.conf) 是唯一的完整分流模块。它与 v1.0.0 的 DNS、规则和策略组正文相同；只启用本版一份完整模块，以及一个本地节点模块。已有 v1.0.0 完整模块的用户本次无需替换它。**根目录兼容入口仍是旧 SocksTun 正式方案，不适用于本方案。**

插件中文界面设置沿用 [v1.0.0 的 §3 插件手工设置](../v1.0.0/SETUP.md#3-插件手工设置)：Fake-IP（增强）与规则模式、绕过中国大陆 IPv4、Dnsmasq 转发、DNS 规则过滤、禁用 QUIC、IPv6 代理关闭等，由用户手工保持，不由模块改写。原有本地 IPv4 绕过列表保持；链式拨号首先连接机场节点，原 IPRoyal `/32` 条目不负责建立第一跳。

## 当前唯一验收步骤与回退

刷新滚动模块并重启后，先在运行配置中确认 `Manual-Direct` 为 `type: inline`，payload 有仓库当前 129 条规则且没有独立 HTTP URL/path/interval；抽查 `one.alimama.com`、`d-gm.mmstat.com` 和其他人工直连域名命中 `Manual-Direct` 并走 `DIRECT`。这一步验证模块和规则一起更新，不操作单独的 Rule Provider。再确认 `IPRoyal-US-ISP` 具有 `dialer-proxy: 美国`，且`美国`组不包含该 IPRoyal 节点。之后用一台手机关闭 SocksTun、移动数据和其他 VPN 后打开 TikTok，观察新连接。若 IPRoyal 端口超时消失、TikTok 连接成功，且目标出口确认是 IPRoyal，说明此双跳路径有效。若超时仍在，保留脱敏日志，不改 TikTok 到机场或 DIRECT；首跳能否访问 IPRoyal 端口需另行核实。

回退只需**停用 `iproyal-chain-hop.conf` 并重启 OpenClash**；原有本地节点将恢复 `dialer-proxy: DIRECT`。全新部署并直接填写上述链式节点模板者，回退时需在本地节点中改回 `DIRECT` 后重启。未经真实路由器与手机验收，v1.0.2-beta.3 仍是候选，不发布稳定版。
