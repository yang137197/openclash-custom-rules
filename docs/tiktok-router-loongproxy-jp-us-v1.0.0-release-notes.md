## 正式版 v1.0.0

TikTok 的 Loongproxy 美国 SOCKS5 出口必须经用户手选的 iKuuu 日本节点建立链式代理。日本节点是强制首跳；不得改用美国或其他机场首跳，也不得在首跳缺失时回退机场或 DIRECT。

用户于 2026-10-16 确认 CatWrt/OpenClash 实机验收通过并授权正式发布。验收环境为 OpenClash v0.48.002 / alpha-gbc76c13；不补造未提供的逐项日志或指标。

### 规则与配置

- 日本入口自动纳入已加载节点中名称包含 `jp`、`日本`、`Japan` 或 🇯🇵 的节点；实际使用时手动选择 iKuuu 日本节点。
- TikTok 仅走本地 `TikTok-ISP-Local` SOCKS5，固定 `dialer-proxy: 日本-入口`、`udp: false`；链路缺少日本首跳时失败关闭。
- 保留 129 条 Manual-Direct；Google/Play 与其他境外流量走手选美国组；中国大陆域名/IP 直连。
- 固定版本覆写：[v1.0.0 配置](https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/openclash-overwrite.conf)，SHA-256：`e930c44c6bd06ea6d819f8d86b91efc5786dd63a26aec41fff0b218053d6ce30`。
- LuCI 设置建议、部署、验收与回退步骤见[部署说明](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/SETUP.md)。

### 本地模块模板和填写

只需下载这一个模板：[本地 SOCKS5 模块模板](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.0/tiktok-router-loongproxy-jp-us-v1.0.0-local-module.conf.example)。SHA-256：`d7639bd7ac733c2312103bcb8e73764b2b354b3ccb7bcb578f7ee5d3706da522`。

把模板中的 `FILL_ME_PROXY_HOST`、`FILL_ME_PROXY_PORT`、`FILL_ME_USERNAME`、`FILL_ME_PASSWORD` 替换为 ISP 提供的信息：`server` 填“代理地址”，不要填“出口 IP”；`port` 填代理端口数字；`username` 和 `password` 填对应账号密码。字符串保留单引号，端口不加引号。保持 `name: TikTok-ISP-Local`、`type: socks5`、`udp: false` 和 `dialer-proxy: 日本-入口` 不变。

例如，假设 ISP 信息为代理地址 `198.51.100.27`、端口 `20001`、用户名 `EXAMPLE_USER`、密码 `EXAMPLE_PASSWORD`，而出口 IP 为 `203.0.113.8`，模板中的对应内容应为：

```ini
[YAML]
proxies+:
  - name: TikTok-ISP-Local
    type: socks5
    server: '198.51.100.27'
    port: 20001
    username: 'EXAMPLE_USER'
    password: 'EXAMPLE_PASSWORD'
    udp: false
    dialer-proxy: 日本-入口
```

以上 IP 是文档专用地址，账号和密码是虚构值，不能用于连接。真实地址和凭据只填入路由器本地模块，切勿提交或公开填好的文件。

### 验证

GitHub Actions、24 项 Python 测试、仓库校验和 `git diff --check` 均通过。实机验收依据用户确认记录。
