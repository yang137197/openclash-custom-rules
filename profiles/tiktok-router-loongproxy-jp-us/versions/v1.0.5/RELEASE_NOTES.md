# tiktok-router-loongproxy-jp-us v1.0.5

**正式版（stable）**，由用户于 2026-10-24 明确授权发布。此版本只修正本地节点模板的下载扩展名为 `.conf`；云覆写、分流规则、ISP 凭据字段和链路与 v1.0.4 完全相同。

## 适用规则

- Loongproxy 美国 SOCKS5 必须通过用户手选的 iKuuu 日本节点建立链式代理，`dialer-proxy: 日本-入口`。这是强制第一跳；不允许替换首跳，也不允许在链路不可用时回退到其他机场或 `DIRECT`。
- 规则优先级：私网/局域网直连 → Claude Code 与 Claude/Anthropic 第一方域名走 `TikTok-ISP`、GitHub 指定域名走 `美国` → 通用 TikTok 规则及紧邻拒绝规则 → Google/Google Play 走 `美国` → 129 条 Manual-Direct → 中国大陆域名/IP 直连 → 其余流量走 `美国`。
- 日本入口从已加载节点中自动筛选名称含 `jp`、`日本`、`Japan` 或 🇯🇵 的节点；部署时仍须手动选择 iKuuu 日本节点。未发现可用首跳时失败关闭。

## OpenClash 环境与设置

- OpenClash：0.48.002；提供的版本标签未单独标出插件构建号。
- Mihomo：alpha-gbc76c13。
- OpenWrt：24.10.2 r7492-3fda82b52；x86_64；QEMU Standard PC (2C2T)。
- 环境和运行配置快照复用 v1.0.4 已验收记录；v1.0.5 不改变运行行为。此版本没有重新采集调试日志，也未在路由器本地文件选择器实测模板。
- OpenClash 手工设置建议、LuCI 路径、前提和限制见 [SETUP.md](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.5/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.5/SETUP.md)。设置基线继承 v1.0.4，未声称本次重新验收运行配置。
- 需求边界见 [REQUIREMENTS.md](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.5/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.5/REQUIREMENTS.md)；环境复用及未验证项见 [ENVIRONMENT.json](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.5/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.5/ENVIRONMENT.json)。

## 固定覆写订阅

将以下标签固定链接填入 OpenClash 云覆写订阅：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.5/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.5/openclash-overwrite.conf

云覆写 SHA-256：`22f932afbc328e1d0d2188519378032e4db0b9cbbb9ce4ed7a8433f585741e6a`

把云覆写模块放在本地 TikTok-ISP 模块上方；两个模块匹配同一配置。更新仓库规则时刷新云覆写模块并重启 OpenClash，无需单独更新 Manual-Direct。日本入口仍须手选 iKuuu 日本节点。完整 LuCI 设置、部署和回退步骤见上方 `SETUP.md`。

## 本地节点模板

下载此 Release 唯一提供的本地模块模板：

[下载 tiktok-router-loongproxy-jp-us-v1.0.5-local-module.conf](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.5/tiktok-router-loongproxy-jp-us-v1.0.5-local-module.conf)

附件 SHA-256：`d7639bd7ac733c2312103bcb8e73764b2b354b3ccb7bcb578f7ee5d3706da522`

根据 Loongproxy 提供的 SOCKS5 信息填写：

- `FILL_ME_PROXY_HOST`：填写服务商给出的代理服务器地址或 IP，不是“出口 IP”栏；保留左右单引号，例如 `server: '203.0.113.10'`。
- `FILL_ME_PROXY_PORT`：填写服务商给出的代理端口数字，例如 `20000`；不加引号。
- `FILL_ME_USERNAME`：填写服务商提供的用户名，保留左右单引号。
- `FILL_ME_PASSWORD`：填写服务商提供的密码，保留左右单引号。
- 保留节点名 `TikTok-ISP-Local`、`type: socks5`、`udp: false` 和 `dialer-proxy: 日本-入口`。该链路必须由手选的 iKuuu 日本节点作为第一跳。

以下示例中的地址、用户名和密码均为虚构值：

```ini
[YAML]
proxies+:
  - name: TikTok-ISP-Local
    type: socks5
    server: '203.0.113.10'
    port: 20000
    username: 'demo_user'
    password: 'demo_password'
    udp: false
    dialer-proxy: 日本-入口
```

真实凭据只保存在路由器本地节点模块中。不要将填好的文件提交到仓库、上传到 GitHub 或发送到聊天中。v1.0.4 的历史附件扩展名是 `.conf.example`，使用前须改名为 `.conf`；v1.0.5 附件使用 `.conf`。本次未在目标路由器文件选择器实际选择或读取该附件。文件类型依据 [OpenClash 官方覆写模块指南 §16.1.1](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)：本地上传支持 `.txt`、`.conf`。

## 验证与变更

- 静态验证检查版本合同、云覆写一致性、本地模板扩展名/段头/占位字段、文件哈希、129 条规则和历史版本保护。
- 本地验证结果：29 个 Python 单元测试通过；仓库验证器与 `git diff --check` 通过。
- 本版本不修改运行配置，因此环境快照复用 v1.0.4。没有新的路由器运行验收或文件选择器测试记录。
- 相较 v1.0.4，唯一变化是本地模块模板附件从 `.conf.example` 改为 `.conf`。v1.0.4 的目录、标签、Release 和附件保持不变。
