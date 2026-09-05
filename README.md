# OpenClash 通用分流覆写

本仓库用于 OpenClash Meta/Mihomo，目标是保持规则简单、可验证、多人多设备可复用。

当前策略只有三类：

1. 中国大陆域名/IP → `DIRECT`
2. 手工指定的额外直连域名 → `DIRECT`
3. 其他所有流量 → `美国`

`美国` 为手动选择策略组，只展示订阅中的美国节点。其他国家节点仍保留在订阅底层，但不会进入任何策略组，也不会被任何规则使用。

---

## 1. 覆写地址

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/overwrite/openclash-overwrite.conf
```

OpenClash 中：

1. 进入“覆写设置 → 模块设置”
2. 只保留并启用上面的远程覆写地址
3. 更新覆写模块
4. 应用配置并重启 OpenClash

不要同时叠加其他会修改 `proxy-groups`、`rules`、`rule-providers` 的覆写模块，否则可能产生冲突。

---

## 2. 最终分流逻辑

规则按从上到下顺序匹配，第一条命中后停止。

```text
局域网 / 私有域名 / 私有 IP
        ↓ 命中
      DIRECT

未命中
        ↓
Manual-Direct 手工直连规则
        ↓ 命中
      DIRECT

未命中
        ↓
中国大陆域名 GEOSITE,cn
        ↓ 命中
      DIRECT

未命中
        ↓
中国大陆 IP GEOIP,CN
        ↓ 命中
      DIRECT

仍未命中
        ↓
     MATCH,美国
        ↓
手工选择的美国节点
```

主规则：

```yaml
rules:
  - GEOSITE,private,DIRECT
  - GEOIP,private,DIRECT,no-resolve
  - IP-CIDR,127.0.0.0/8,DIRECT,no-resolve
  - IP-CIDR,169.254.0.0/16,DIRECT,no-resolve
  - IP-CIDR,224.0.0.0/4,DIRECT,no-resolve
  - IP-CIDR6,::1/128,DIRECT,no-resolve
  - IP-CIDR6,fc00::/7,DIRECT,no-resolve
  - IP-CIDR6,fe80::/10,DIRECT,no-resolve
  - IP-CIDR6,ff00::/8,DIRECT,no-resolve
  - RULE-SET,Manual-Direct,DIRECT
  - GEOSITE,cn,DIRECT
  - GEOIP,CN,DIRECT,no-resolve
  - MATCH,美国
```

---

## 3. `RULE-SET,Manual-Direct,DIRECT` 是什么

这一条：

```yaml
- RULE-SET,Manual-Direct,DIRECT
```

意思是：

- `RULE-SET`：调用一个规则集
- `Manual-Direct`：规则集名称
- `DIRECT`：命中后直接连接，不经过代理

`Manual-Direct` 对应本仓库：

```text
rules/manual-direct.yaml
```

以后想增加“必须直连”的网站，只修改这个文件，不需要改主配置。

---

## 4. 如何新增手工直连域名

文件：

```text
rules/manual-direct.yaml
```

### 推荐写法：`DOMAIN-SUFFIX`

```yaml
payload:
  - DOMAIN-SUFFIX,example.com
```

会匹配：

```text
example.com
www.example.com
api.example.com
任意其他子域名.example.com
```

这是最推荐的写法。

### 只匹配一个完整域名：`DOMAIN`

```yaml
payload:
  - DOMAIN,api.example.com
```

只匹配：

```text
api.example.com
```

不会匹配：

```text
www.example.com
example.com
```

### 关键词匹配：`DOMAIN-KEYWORD`

```yaml
payload:
  - DOMAIN-KEYWORD,example
```

域名中包含 `example` 就可能被匹配。

这种方式容易误伤，不建议日常使用。

### 错误写法

不要写：

```text
https://example.com
http://example.com/path
example.com:443
https://example.com?a=1
```

规则中只写域名，不写协议、路径、端口和参数。

---

## 5. 美国策略组

当前策略组：

```yaml
- name: 美国
  type: select
  include-all: true
```

### 为什么使用 `select`

`select` 表示手动选择节点。

这样可以固定出口，不会因为延迟波动自动切换美国节点。

适合：

- TikTok
- Google
- ChatGPT
- 海外社媒账号
- 需要相对稳定出口 IP 的长期登录环境

### 为什么不用 `url-test`

`url-test` 会自动选择延迟较低的节点，网络波动时可能自动切换出口。

对于普通浏览没有问题，但对于长期登录海外账号，稳定出口比不断自动换节点更重要。

因此本仓库采用：

```text
可以测速
但不自动切换
```

### 非美国节点如何处理

订阅中日本、香港、新加坡、台湾、欧洲等节点：

- 仍会随订阅下载
- 保留在底层 `proxies`
- 不进入 `美国` 策略组
- 不被任何规则引用
- 实际不会产生流量

这样比直接删除订阅节点更稳定，也更容易兼容机场订阅更新。

---

## 6. 美国节点筛选

当前通过节点名称筛选美国节点，匹配常见名称：

```text
美国
美國
US
USA
United States
America
Los Angeles
San Jose
Seattle
New York
Chicago
Dallas
```

如果机场未来修改美国节点命名，但美国策略组里没有出现节点，只需要修改：

```yaml
filter:
```

不要新增日本、香港等其他策略组。

---

## 7. 中国大陆直连

### 域名

```yaml
- GEOSITE,cn,DIRECT
```

作用：

中国大陆常见域名数据库命中后直接连接。

例如正常情况下：

```text
baidu.com
qq.com
taobao.com
jd.com
```

无需逐个写入 `manual-direct.yaml`。

### IP

```yaml
- GEOIP,CN,DIRECT,no-resolve
```

作用：

目标 IP 属于中国大陆时直接连接。

主要用于：

- 直接访问 IP
- 域名规则未命中但最终解析到中国大陆 IP
- 部分没有完整域名规则的数据流

---

## 8. 局域网与回流

以下规则优先于所有代理规则：

```yaml
- GEOSITE,private,DIRECT
- GEOIP,private,DIRECT,no-resolve
```

以及常见本地网络段：

```text
127.0.0.0/8
169.254.0.0/16
224.0.0.0/4
::1/128
fc00::/7
fe80::/10
ff00::/8
```

目的：

- 局域网设备访问不送入美国代理
- PVE / NAS / 路由器等内网资源直连
- WireGuard 私网地址直连
- 降低 NAT 回流和局域网访问异常概率

---

## 9. Fake-IP 与回流域名

OpenClash/Mihomo 使用 Fake-IP 时，一些内部服务域名不应该返回 `198.18.x.x` Fake-IP。

当前覆写通过：

```yaml
fake-ip-filter+:
```

追加以下本地域名：

```text
+.lan
+.local
+.home.arpa
localhost
```

并保留当前环境的自建服务：

```text
pve.yangnas.cn
auth.yangnas.cn
nexus.yangnas.cn
```

这些域名返回真实 IP，更适合局域网访问和 NAT 回流。

### 新增回流域名

如果以后增加：

```text
nas.example.com
```

且该域名需要在内网解析到真实 IP，可以在 `fake-ip-filter+` 中增加：

```yaml
- 'nas.example.com'
```

注意：

`fake-ip-filter` 解决的是“返回真实 IP”问题，是否 `DIRECT` 仍由主规则决定。

---

## 10. `oc-cn-domain` 为什么不能删除

OpenClash 某些设置会自动生成内部 rule-provider，例如：

```text
oc-cn-domain
```

并在 Fake-IP 过滤中引用：

```yaml
rule-set:oc-cn-domain
```

因此本仓库只增加自己的：

```text
Manual-Direct
```

不会再用 Ruby 或其他方式整体覆盖 `rule-providers`。

否则会出现：

```text
Parse config error: not found rule-set: oc-cn-domain
```

这也是 2026-09-05 这次重构重点修复的问题。

---

## 11. DNS 策略

### 中国大陆 / 私有域名

使用：

```text
223.5.5.5
1.12.12.12
```

### 国外域名

使用：

```text
1.1.1.1
8.8.8.8
```

并要求 DNS 连接通过：

```text
美国
```

### 为什么开启 `respect-rules`

```yaml
respect-rules: true
```

意味着 DNS 上游连接本身也遵循分流规则，减少“流量走美国，但 DNS 走错误出口”的情况。

---

## 12. 多人多设备复用原则

本仓库不按以下内容写死规则：

- 设备 IP
- 手机型号
- 用户名
- MAC 地址
- 某个人专用策略
- 某个设备专用国家节点

因此同一个局域网内多台：

- 手机
- Windows
- Mac
- 平板
- NAS
- PVE 虚拟机
- 智能设备

都可以共用同一套规则。

如果未来确实需要“某台设备固定日本 / 某台设备固定美国”，应单独设计设备分流层，不建议直接污染当前通用主规则。

---

## 13. 日常维护只需要做什么

### 新增必须直连的网站

只修改：

```text
rules/manual-direct.yaml
```

优先使用：

```yaml
- DOMAIN-SUFFIX,example.com
```

### 美国节点没有被识别

修改：

```text
overwrite/openclash-overwrite.conf
```

中的：

```yaml
filter:
```

### 新增局域网回流域名

修改：

```yaml
fake-ip-filter+:
```

### 其他情况

不要随意修改：

```text
rule-providers
rules!
proxy-groups!
DNS 主结构
```

先确认问题根因再改。

---

## 14. 更新后的验收方法

更新覆写并重启 OpenClash 后检查：

### 1. OpenClash 必须成功启动

日志不能出现：

```text
Parse config error
not found rule-set
```

### 2. 策略组

界面应只有核心海外策略：

```text
美国
```

进入 `美国` 后只应看到美国节点，并由用户手工选择。

### 3. 中国网站

访问：中国大陆网站。

日志应命中：

```text
DIRECT
```

### 4. 国外网站

访问 Google / ChatGPT 等。

日志应最终命中：

```text
MATCH,美国
```

### 5. 手工直连

访问 `manual-direct.yaml` 中的域名。

应命中：

```text
Manual-Direct → DIRECT
```

### 6. 局域网

访问 PVE、NAS、路由器和 WireGuard 私网地址，不应进入美国代理。

---

## 15. 仓库文件

```text
openclash-custom-rules/
├── README.md
├── CHANGELOG.md
├── overwrite/
│   └── openclash-overwrite.conf
├── rules/
│   └── manual-direct.yaml
└── docs/
    └── acceptance-log.md
```

### `overwrite/openclash-overwrite.conf`

OpenClash 远程覆写主配置。

### `rules/manual-direct.yaml`

用户长期维护的额外直连规则。

### `docs/acceptance-log.md`

每次重大修改后的验收要求与记录。

### `CHANGELOG.md`

记录架构和行为变更。
