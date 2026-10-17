## 正式版 v1.0.0

TikTok 的 Loongproxy 美国 SOCKS5 出口必须经用户手选的 iKuuu 日本节点建立链式代理。iKuuu 日本节点是强制首跳；不得换用美国或其他机场首跳，也不得在节点缺失时回退机场或 DIRECT。

用户于 2026-10-16 确认 CatWrt/OpenClash 实机验收通过并授权正式发布，目标版本为 OpenClash v0.48.002 / alpha-gbc76c13。验收按用户总体确认记录，不补造逐项日志或指标。

### 配置内容

- 唯一当前正式方案：**tiktok-router-loongproxy-jp-us v1.0.0**。
- 日本入口自动纳入已加载节点中名称含 **jp**、**日本**、**Japan** 或 🇯🇵 的节点；部署时需手动选实际 iKuuu 日本节点。
- TikTok 仅走本地 **TikTok-ISP-Local** SOCKS5，固定 **dialer-proxy: 日本-入口**、**udp: false**；缺少首跳时失败关闭。
- 保留 129 条 Manual-Direct；Google/Play 与其他境外流量走手选美国组；中国大陆域名/IP 直连。
- 本地 ISP 密码修改说明见[标签固定部署与验收说明](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/SETUP.md)。真实代理凭据只存路由器本地模块。

### 验证

- GitHub Actions PR 校验通过。
- 6 个 Python 回归测试通过。
- 仓库验证通过：稳定版本合同、强制 iKuuu 首跳、129 条规则、模块哈希、凭据占位符、历史保护和本地文档链接。
- git diff --check 通过。

### 本地节点模板下载与填写

建议下载带逐字段提示的模板和说明：

- [下载带字段注释的本地模块模板](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.0/tiktok-router-loongproxy-jp-us-v1.0.0-local-module-with-field-comments.conf.example)
- 带注释模板 SHA-256：724f031f49d3018244540f99cfe8d6bfa484040effd6ee9838e465d3e90c9b21
- [下载逐字段填写说明](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.0/tiktok-router-loongproxy-jp-us-v1.0.0-local-module-filling-guide.md)；说明包含一组虚构 ISP 面板数据及对应填写结果，特别区分代理地址与出口 IP。
- 填写说明 SHA-256：ab90c557e1295569ffbaa12b1df2d759b7569ab9e186f3e80c0087953f9817dc

字段对应关系：

- server 填 ISP 信息中的“代理地址 / Proxy Address”所给的服务器 IP，保留左右单引号。它是连接代理服务器的地址；如果与“出口 IP”不同，不要填“出口 IP”。
- port 填 ISP 信息中的“代理端口 / Proxy Port”数字，不加引号。
- username、password 分别填 ISP 提供的用户名和密码，保留左右单引号。
- name: TikTok-ISP-Local、type: socks5、udp: false 和 dialer-proxy: 日本-入口 必须保持不变；还须在运行面板中手动选择 iKuuu 日本节点。
- 填好后仅导入路由器本地 OpenClash 模块。不要公开或提交包含真实 ISP 地址、用户名或密码的文件。

原始标签占位模板仍可单独下载，且与 v1.0.0 标签内的文件逐字节一致：

- [下载原始本地模块模板](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.0/tiktok-router-loongproxy-jp-us-v1.0.0-local-module.conf.example)
- 原始模板 SHA-256：d7639bd7ac733c2312103bcb8e73764b2b354b3ccb7bcb578f7ee5d3706da522

完整操作步骤见[标签固定部署与验收说明](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/SETUP.md)。
