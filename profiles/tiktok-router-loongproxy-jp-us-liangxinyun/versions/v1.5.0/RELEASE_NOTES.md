# tiktok-router-loongproxy-jp-us-liangxinyun v1.5.0

适用于 TikTok 手选 iKuuu 日本首跳、使用 Loongproxy 美国静态出口，同时将其他代理流量交给良心云的路由器。

- 规则顺序为私网直连 → GitHub 走良心云 → TikTok 经 iKuuu 日本首跳和 Loongproxy → TikTok REJECT → Google／Google Play 走良心云 → 手动直连 → 大陆域名和 IP 直连 → 良心云默认代理。
- `TikTok首跳` 仅纳入 iKuuu 日本 Z01–Z04。首次无手选记录或所选节点消失时使用 REJECT。
- 正式版含 141 条手动直连规则。更新手动直连走仓库的统一同步流程。

## 固定与滚动覆写

标签固定地址

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-liangxinyun-v1.5.0/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.5.0/openclash-overwrite.conf

滚动地址

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/overwrite/openclash-overwrite.conf

固定覆写 SHA-256 为 `c85392a352914b988e879d12d3dc12ee20f87a6442c5c2abed5070345fbc88b1`。

## 路由器设置及验收

OpenClash 规则模式与 Fake-IP，UDP 转发开启，TikTok 的本地 SOCKS5 保持 `udp: false`。实机验收时「禁用 QUIC」开关处于停用状态。目标环境为 OpenClash v0.48.002、Mihomo alpha-gbc76c13、OpenWrt 24.10.2 r7492-3fda82b52、x86_64。

用户于 2026-11-16 确认 v1.5.0 实机验收通过。对应日志记录成功的 TikTok TCP 和良心云普通代理连接，首跳选择由运行规则限定在指定日本节点。日志未记录本地模板文件选择器或具体日本节点编号。

- [设置、部署与回退](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-liangxinyun-v1.5.0/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.5.0/SETUP.md)
- [需求合同](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-liangxinyun-v1.5.0/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.5.0/REQUIREMENTS.md)
- [环境与验收证据](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-liangxinyun-v1.5.0/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.5.0/ENVIRONMENT.json)

## 唯一本地覆写模板

[下载 local-tiktok-proxy.conf](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-liangxinyun-v1.5.0/local-tiktok-proxy.conf)。SHA-256 为 `71379bfe031c43953029336dd6e177bfa075b2aa33d1609559f114aa718af7a2`。

- `FILL_ME_PROXY_HOST` 填 Loongproxy SOCKS5 主机或 IP，`FILL_ME_PROXY_PORT` 填数值端口。
- `FILL_ME_USERNAME` 和 `FILL_ME_PASSWORD` 填 Loongproxy 账密。
- `FILL_ME_LIANGXINYUN_MIHOMO_URL` 填良心云 Clash/Mihomo 订阅地址，路由器须能直连拉取。
- 保留 `TikTok-ISP-Local`、`type: socks5`、`udp: false`、`dialer-proxy: TikTok首跳`，以及提供商键名 `liangxinyun` 和 `LXY: ` 节点前缀。真实值仅填在路由器本地模块。

以下是虚构填写示例。

```yaml
[YAML]
proxies+:
  - name: TikTok-ISP-Local
    type: socks5
    server: '198.51.100.10'
    port: 1080
    username: 'example-user'
    password: 'example-password'
    udp: false
    dialer-proxy: TikTok首跳
proxy-providers:
  liangxinyun:
    type: http
    url: 'https://subscription.example.invalid/mihomo'
    path: ./proxy_provider/liangxinyun.yaml
    interval: 3600
    proxy: DIRECT
    override:
      additional-prefix: 'LXY: '
```
