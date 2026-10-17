# tiktok-router-loongproxy-jp-us v1.0.0 本地 ISP 模块填写说明

本说明配合 Release 中的带注释模板使用。模板是 OpenClash 的本地覆写模块，只为本地 SOCKS5 节点填入 ISP 连接信息。

## 应下载哪个文件

- 推荐下载 [带字段注释的本地模块模板](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.0/tiktok-router-loongproxy-jp-us-v1.0.0-local-module-with-field-comments.conf.example)。注释标明每个字段应从 ISP 信息中取哪一项。
- [原始标签占位模板](https://github.com/yang137197/openclash-custom-rules/releases/download/tiktok-router-loongproxy-jp-us-v1.0.0/tiktok-router-loongproxy-jp-us-v1.0.0-local-module.conf.example)与 v1.0.0 标签中的文件逐字节一致，不带逐字段注释。

下载后另存为本地配置文件，按下表修改占位字段。上传前检查文件中只包含你自己 ISP 的连接信息。

## ISP 信息与模板字段对照

| 模板字段 | 填写来源 | 如何填写 |
| --- | --- | --- |
| server | ISP 信息中的“代理地址”或“Proxy Address” | 填 ISP 提供的代理服务器 IP 地址；如果 ISP 提供的是主机名，就按其提供的主机名填写。保留左右单引号。这里填连接代理服务器的地址，不要根据“出口 IP”一栏猜填；两项只有在 ISP 给出的值相同时才相同。 |
| port | ISP 信息中的“代理端口”或“Proxy Port” | 填代理端口的数字，不加引号。 |
| username | ISP 信息中的“用户名”或“Username” | 原样填写，保留左右单引号。 |
| password | ISP 信息中的“密码”或“Password” | 原样填写，保留左右单引号。 |
| name | 不从 ISP 信息填写 | 必须保持 TikTok-ISP-Local。策略组按此精确名称找到本地节点。 |
| type | 不从 ISP 信息填写 | 必须保持 socks5。 |
| udp | 不从 ISP 信息填写 | 必须保持 false。 |
| dialer-proxy | 不从 ISP 信息填写 | 必须保持 日本-入口。它指定链式代理的日本入口组；在运行面板中还必须手动选中实际的 iKuuu 日本节点。 |

## 示例：从 ISP 信息填写模板

下面的 ISP 面板数据和结果都只是格式示例，不能用于连接。示例中的两个 IP 属于文档专用地址段，用户名和密码也是虚构值。

假设 ISP 面板显示：

| ISP 面板项目 | 示例值 |
| --- | --- |
| 代理地址 | `198.51.100.27` |
| 代理端口 | `20001` |
| 用户名 | `EXAMPLE_USER` |
| 密码 | `EXAMPLE_PASSWORD` |
| 出口 IP | `203.0.113.8` |

填写模板时，`server` 取“代理地址”一栏的 `198.51.100.27`，不要取“出口 IP”一栏的 `203.0.113.8`；出口 IP 是代理连接成功后的出口信息，不是要连接的代理服务器地址。对应填写结果如下：

```yaml
name: TikTok-ISP-Local
type: socks5
server: '198.51.100.27'
port: 20001
username: 'EXAMPLE_USER'
password: 'EXAMPLE_PASSWORD'
udp: false
dialer-proxy: 日本-入口
```

实际使用时，把示例值逐项替换为 ISP 提供的真实值：`server`、`username`、`password` 保留左右单引号，`port` 填纯数字且不加引号。若密码本身含单引号，在 YAML 单引号字符串中将密码里的每个单引号写成两个连续单引号。`name`、`type`、`udp` 和 `dialer-proxy` 按示例保持不变。

## 填写和导入

1. 先复制下载的模板，再编辑副本；只替换 FILL_ME_PROXY_HOST、FILL_ME_PROXY_PORT、FILL_ME_USERNAME 和 FILL_ME_PASSWORD。
2. 保留 [YAML] 段头、proxies+、缩进、节点名称、SOCKS5 协议、udp: false 和 dialer-proxy: 日本-入口。
3. 将填好的副本只导入路由器的 OpenClash 本地模块，然后按 [v1.0.0 部署与验收说明](https://github.com/yang137197/openclash-custom-rules/blob/tiktok-router-loongproxy-jp-us-v1.0.0/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0/SETUP.md)操作并重启 OpenClash。
4. 在 日本-入口 策略组中手动选择 iKuuu 日本节点。Loongproxy 美国 SOCKS5 必须经该日本节点作为链式首跳。

填写后的文件含真实 ISP 地址、用户名或密码，只能保存在路由器本地。不要把它提交到仓库、上传到 Release、发到聊天中或放入公开日志。公共模板始终只使用 FILL_ME_* 占位值。
