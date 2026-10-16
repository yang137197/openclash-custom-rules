# tiktok-router-loongproxy-jp-us v1.0.0 — 部署与验收

**状态：candidate，未在 CatWrt/OpenClash 实机验证。**

## 前提
- 先在「服务 → OpenClash → 配置管理」备份当前配置；确认 Mihomo/Meta 内核。
- 停用其他完整分流覆写；不要同时启用两套完整规则。
- 机场订阅中需要存在可手选的 iKuu 日本节点，名称包括「日本」/「🇯🇵」/「Japan」或独立 JP 标记；美国组继续手选美国节点。
- 规则模式、Fake-IP/DNS、大陆 IPv4 绕过、IPv6 等 LuCI 选项由用户手动按仓库已验收 `tiktok-sockstun-us v2.0.0` 的 SETUP 第 3～5 节核对；不自动改变插件设置。

## 添加远程覆写与本地节点

入口：「服务 → OpenClash → 运行状态 → 顶部覆写模块按钮」，不是「覆写设置」菜单。

1. 「+ 添加新模块 → 本地模块」上传本目录的 `local-tiktok-proxy.conf.example` 的**本地副本**，替换所有 `FILL_ME` 为自己的 Loongproxy SOCKS5 凭据；不要上传公共仓库。启用模块，匹配配置设 `all` 或当前配置的完整路径（例如 `/etc/openclash/config/ikuu.yaml`）。
2. 再新建「订阅链接」模块，正式合并到 main 后的滚动覆写 URL：
   `https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf`
   **合并前此 URL 尚不存在**；候选验收可先上传当前分支同名覆写文件作为本地模块。
3. 模块列表中完整云覆写排在本地节点模块**上方**（列表越靠上执行越晚）。开启二者后，必须「重启 OpenClash」，仅保存/刷新不立即生效。
4. Dashboard 中手选 `日本-入口` 的 iKuu 日本节点、`美国` 的美国节点，确认 `TikTok-ISP` 只含 `TikTok-ISP-Local`。检查运行 YAML 含 `dialer-proxy: 日本-入口`，无递归或缺少节点。

## 单次刷新自定义规则

仓库维护者同一提交同步 `rules/manual-direct-isp.yaml` 的所有 129 条及本方案滚动模块的 inline payload。路由器仅需刷新本远程覆写模块，然后**重启 OpenClash**；不需要单独刷新 Manual-Direct Rule Provider。GEO 数据库、机场订阅仍独立维护。

## 手机验收与回退

1. 手机连接路由器 Wi-Fi，关闭移动数据、SocksTun、第三方 VPN；重新打开 TikTok，确认连接规则命中 `TikTok-ISP` 并经 `TikTok-ISP-Local` 美国 ISP 出口；观察视频播放稳定性，不能只看节点测速值。
2. 验证 Google/Play 经美国组、国内域名与 IP 走 DIRECT、129 条 Manual-Direct 中的典型域名走直连。
3. 停用本地 ISP 模块并重启，TikTok 新连接应命中 REJECT，不能回退美国或直连；然后恢复。测试失败先用「运行日志 → 调试日志 → 生成日志」，禁止连续猜测配置。
4. 仅保证进入 Mihomo 且匹配 TikTok 规则的流量；不保证设备其他网络路径、未知域名、IPv6 或应用侧行为。
5. 回退时关闭**本方案两个模块**，重启 OpenClash，再启用原来的单一已验证完整覆写；未验收不得发布稳定标签。

技术依据：OpenClash 用户指南 `16-overwrite-module-format.md` §16.1、§16.2.3；`08-settings-mode-traffic.md` §8.3。
