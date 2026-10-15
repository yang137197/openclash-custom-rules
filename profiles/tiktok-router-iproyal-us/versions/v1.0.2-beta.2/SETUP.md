# 所有手机经 OpenClash → 机场首跳 → IPRoyal → TikTok

适用：`tiktok-router-iproyal-us v1.0.2-beta.2` **beta/candidate**。这是 v1.0.1 链式拨号候选的规则修订，新增 `DOMAIN-SUFFIX,mmstat.com`，覆盖主域名及所有子域名；TikTok 最终出口仍须为 IPRoyal，其他国外流量仍由手选机场美国节点处理。手机无需 SocksTun。

## 已有安装的规则更新

本次新增项位于共享 `Manual-Direct` 规则集；完整覆写继续从 `main/rules/manual-direct.yaml` 更新该规则集。已使用 v1.0.0/v1.0.1 完整模块的用户，无需再叠加一套完整覆写或重复上传相同链式补丁；在 OpenClash 更新 `Manual-Direct` 规则集后，确认 `mmstat.com`、`d-gm.mmstat.com` 和另一个 `mmstat.com` 子域名均命中该规则集并走 `DIRECT`。下方 beta 完整模块链接供新部署或有意整体切换版本的用户使用。

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

重启后先在运行配置中确认 `IPRoyal-US-ISP` 具有 `dialer-proxy: 美国`，且`美国`组不包含该 IPRoyal 节点；再确认 `mmstat.com`、`d-gm.mmstat.com` 及另一个 `mmstat.com` 子域名均命中 `Manual-Direct` 并走 `DIRECT`。之后用一台手机关闭 SocksTun、移动数据和其他 VPN 后打开 TikTok，观察新连接。若 IPRoyal 端口超时消失、TikTok 连接成功，且目标出口确认是 IPRoyal，说明此双跳路径有效。若超时仍在，保留脱敏日志，不改 TikTok 到机场或 DIRECT；首跳能否访问 IPRoyal 端口需另行核实。

回退只需**停用 `iproyal-chain-hop.conf` 并重启 OpenClash**；原有本地节点将恢复 `dialer-proxy: DIRECT`。全新部署并直接填写上述链式节点模板者，回退时需在本地节点中改回 `DIRECT` 后重启。未经真实路由器与手机验收，v1.0.2-beta.2 仍是候选，不发布稳定版。
