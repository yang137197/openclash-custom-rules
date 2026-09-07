# OpenClash 通用分流覆写

本仓库用于 OpenClash Meta/Mihomo，目标是保持规则简单、可验证、多人多设备可复用。

当前策略有四类：

1. 中国大陆域名/IP → `DIRECT`
2. 手工指定的额外直连域名 → `DIRECT`
3. TikTok → `TikTok-ISP` → 本地 IPRoyal ISP 节点
4. 其他所有流量 → `美国`

`美国` 为手动选择策略组，只展示订阅中的美国节点，并明确排除 IPRoyal 节点。`TikTok-ISP` 只接受本地模块注入、名称为 `IPRoyal-US-ISP` 的节点；该节点缺失时 TikTok 失败关闭，不回落到机场节点。

---

## 1. 覆写地址

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/overwrite/openclash-overwrite.conf
```

OpenClash 中：

1. 进入“覆写设置 → 模块设置”
2. 保留并启用上面的远程覆写地址
3. 如果使用 TikTok 专用出口，再启用下一节的一个本地 IPRoyal 节点模块
4. 更新覆写模块
5. 应用配置并重启 OpenClash

远程模块和本地 IPRoyal 模块可以叠加，不是二选一：远程模块负责 `proxy-groups!`、`rules!`、DNS 和规则提供者；本地模块只用 `proxies+` 添加保密节点。不要再叠加其他会修改 `proxy-groups`、`rules`、`rule-providers` 的完整覆写模块，否则执行顺序可能改变最终结果。

### 本地 IPRoyal 模块

在 OpenClash 新建一个本地覆写模块，内容如下。服务器、端口、用户名和密码只填写在路由器本地，禁止提交到 GitHub：

```yaml
[YAML]

proxies+:
  - name: IPRoyal-US-ISP
    type: socks5
    server: "你的 IPRoyal 服务器"
    port: 你的端口
    username: "你的用户名"
    password: "你的密码"
    udp: true
    ip-version: ipv4
```

节点名称 `IPRoyal-US-ISP` 必须完全一致，包括大小写和连字符。保存后同时启用远程模块和这个本地模块，再应用配置并重启。

本地模块不要添加 `rules!`、`proxy-groups!`、DNS 或 `rule-providers!`。这些内容由远程模块统一维护。

---

## 2. 最终分流逻辑

规则按从上到下顺序匹配，第一条命中后停止。

```text
局域网 / 私有域名 / RFC1918 私有 IP
        ↓ 命中
      DIRECT

未命中
        ↓
TikTok 域名
        ↓ 命中
TikTok-ISP → IPRoyal-US-ISP

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

  # RFC1918 私网显式直连，不只依赖 GEOIP,private
  - IP-CIDR,10.0.0.0/8,DIRECT,no-resolve
  - IP-CIDR,172.16.0.0/12,DIRECT,no-resolve
  - IP-CIDR,192.168.0.0/16,DIRECT,no-resolve

  - IP-CIDR,127.0.0.0/8,DIRECT,no-resolve
  - IP-CIDR,169.254.0.0/16,DIRECT,no-resolve
  - IP-CIDR,224.0.0.0/4,DIRECT,no-resolve
  - IP-CIDR6,::1/128,DIRECT,no-resolve
  - IP-CIDR6,fc00::/7,DIRECT,no-resolve
  - IP-CIDR6,fe80::/10,DIRECT,no-resolve
  - IP-CIDR6,ff00::/8,DIRECT,no-resolve

  - RULE-SET,TikTok-IPRoyal,TikTok-ISP
  - GEOSITE,tiktok,TikTok-ISP
  - RULE-SET,Manual-Direct,DIRECT
  - GEOSITE,cn,DIRECT
  - GEOIP,CN,DIRECT,no-resolve
  - MATCH,美国
```

为什么显式写 `10/8`、`172.16/12`、`192.168/16`：实际运行日志曾出现 `192.168.100.1:53` 没有命中 `GEOIP,private`，最终落入 `MATCH,美国`。因此现在对 RFC1918 私网采用明确 CIDR 规则，确保局域网 DNS、PVE、NAS、WireGuard 等私网目标必定 `DIRECT`。

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

## 5. TikTok 与美国策略组

### TikTok-ISP

`TikTok-ISP` 通过精确节点名只收集 `IPRoyal-US-ISP`。它不包含 `美国` 作为备用；IPRoyal 不可用时 TikTok 会失败，避免同一个账号在 IPRoyal 和机场出口之间切换。

TikTok 同时使用：

- `GEOSITE,tiktok`
- `rules/tiktok-iproyal.yaml` 补充域名
- TikTok 专用海外 DNS，并通过 `TikTok-ISP` 发出查询

路由器只能看到来源设备、目标域名/IP和端口，看不到安卓内部的应用包名。因此这里的“TikTok 专用”是域名级分流：命中 TikTok 域名的所有设备都会走 IPRoyal；其他应用如果调用同一个字节海外共享域名，也会走 IPRoyal。若要求严格按安卓包名隔离，只能在安卓设备上使用支持按应用选择的 VPN/代理客户端。

### 美国

当前策略组：

```yaml
- name: 美国
  type: select
  include-all: true
```

`select` 表示手动选择节点。这样可以固定出口，不会因为延迟波动自动切换美国节点。

适合 Google、ChatGPT 和其他海外服务。TikTok 不再进入本组。

本仓库采用：

```text
可以测速
但不自动切换
```

订阅中日本、香港、新加坡、台湾、欧洲等节点仍保留在底层 `proxies`，但不进入 `美国` 策略组、不被规则引用、实际不会产生流量。`IPRoyal-US-ISP` 虽然名称含 `US`，也通过 `exclude-filter` 从本组排除。

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

如果机场未来修改美国节点命名，只需要修改 `overwrite/openclash-overwrite.conf` 中的 `filter`。

---

## 7. 中国大陆直连

域名：

```yaml
- GEOSITE,cn,DIRECT
```

IP：

```yaml
- GEOIP,CN,DIRECT,no-resolve
```

中国大陆常规网站无需重复加入 `manual-direct.yaml`。

---

## 8. 局域网与回流

局域网/私网规则优先于所有代理规则。

### RFC1918 IPv4 私网

```yaml
- IP-CIDR,10.0.0.0/8,DIRECT,no-resolve
- IP-CIDR,172.16.0.0/12,DIRECT,no-resolve
- IP-CIDR,192.168.0.0/16,DIRECT,no-resolve
```

分别覆盖：

```text
10.0.0.0 - 10.255.255.255
172.16.0.0 - 172.31.255.255
192.168.0.0 - 192.168.255.255
```

这些规则确保：

- 路由器/DNS 私网地址直连
- PVE / NAS / Home Assistant 等内网服务直连
- WireGuard 私网地址直连
- 跨网段访问不会落入美国代理
- 降低 NAT 回流和局域网访问异常概率

同时继续保留：

```yaml
- GEOSITE,private,DIRECT
- GEOIP,private,DIRECT,no-resolve
```

它们作为额外的私有域名/地址识别层，但不再作为 RFC1918 的唯一保障。

---

## 9. Fake-IP 与回流域名

当前 `fake-ip-filter+` 追加：

```text
+.lan
+.local
+.home.arpa
localhost
pve.yangnas.cn
auth.yangnas.cn
nexus.yangnas.cn
```

这些域名返回真实 IP。

其中自建域名同时存在于 `Manual-Direct` 时，即实现：

```text
真实 DNS + 明确 DIRECT
```

`fake-ip-filter` 解决的是“返回真实 IP”问题，是否 `DIRECT` 仍由主规则决定。

---

## 10. `oc-cn-domain` 为什么不能删除

OpenClash 某些设置会自动生成：

```text
oc-cn-domain
```

并在 Fake-IP 过滤中引用：

```yaml
rule-set:oc-cn-domain
```

因此本仓库只增加 `Manual-Direct`，不会整体覆盖 `rule-providers`，避免再次出现：

```text
Parse config error: not found rule-set: oc-cn-domain
```

---

## 11. DNS 策略

中国大陆 / 私有域名使用：

```text
223.5.5.5
1.12.12.12
```

国外域名使用：

```text
1.1.1.1
8.8.8.8
```

普通国外 DNS 连接通过 `美国`；TikTok 域名的 DNS 查询单独通过 `TikTok-ISP`，使解析和业务连接保持同一 IPRoyal 出口。

`respect-rules: true` 表示 DNS 上游连接本身也遵循分流规则。

---

## 12. 多人多设备复用原则

本仓库不按设备 IP、手机型号、用户名、MAC 地址、个人策略写死规则，因此同一局域网中的手机、Windows、Mac、平板、NAS、PVE 虚拟机、智能设备都可共用。凡是通过这台 OpenClash 网关联网并命中 TikTok 域名的设备，都会使用同一个 IPRoyal ISP。

以下流量不受保证：设备改用移动数据、另一个默认网关、设备自己的 VPN/代理或未被 OpenClash 接管的加密 DNS；以及规则库尚未识别的新 TikTok 域名。

如果以后确实需要某台设备固定日本或固定美国，应单独设计设备分流层，不污染当前通用主规则。

---

## 13. 日常维护

### 新增必须直连的网站

只修改：

```text
rules/manual-direct.yaml
```

优先：

```yaml
- DOMAIN-SUFFIX,example.com
```

### 美国节点没有被识别

修改主覆写中的 `filter`。

### TikTok 没有走 IPRoyal

依次检查：本地模块已启用、节点名称严格等于 `IPRoyal-US-ISP`、`TikTok-ISP` 组中只有该节点、日志命中 `TikTok-IPRoyal` 或 `GeoSite(tiktok)`。不要把 IPRoyal 用户名或密码发到 GitHub Issue、截图或日志中。

### 新增局域网回流域名

加入 `fake-ip-filter+`；如果要求无论解析到内网还是公网都必须直连，同时加入 `Manual-Direct`。

不要随意整体替换：

```text
rule-providers
rules!
proxy-groups!
DNS 主结构
```

---

## 14. 验收方法

更新覆写并重启 OpenClash 后：

1. 日志不能出现 `Parse config error` / `not found rule-set`。
2. `TikTok-ISP` 中只能出现 `IPRoyal-US-ISP`；`美国` 组不得出现它。
3. TikTok 域名应命中 `TikTok-IPRoyal` 或 `GeoSite(tiktok)` → `TikTok-ISP[IPRoyal-US-ISP]`。
4. `美国` 策略组只展示机场美国节点，并由用户手工选择。
5. 中国网站应命中 `GeoSite(cn)` 或 `GeoIP(cn)` → `DIRECT`。
6. 其他国外网站应命中 `MATCH` → `美国`。
7. `manual-direct.yaml` 域名应命中 `Manual-Direct` → `DIRECT`。
8. 局域网 DNS、路由器、PVE、NAS、WireGuard 私网地址必须 `DIRECT`。

特别检查：

```text
192.168.x.x:53
10.x.x.x
172.16-31.x.x
```

这些目标不应再显示 `Match using 美国`。

---

## 15. 仓库文件

```text
openclash-custom-rules/
├── README.md
├── CHANGELOG.md
├── overwrite/
│   └── openclash-overwrite.conf
├── rules/
│   ├── manual-direct.yaml
│   └── tiktok-iproyal.yaml
└── docs/
    ├── CODEX-HANDOFF.md
    └── acceptance-log.md
```

参考：[OpenClash YAML 覆写操作符](https://github.com/vernesong/OpenClash/blob/master/luci-app-openclash/root/etc/openclash/overwrite/default)、[Mihomo 代理组](https://wiki.metacubex.one/config/proxy-groups/)、[Mihomo SOCKS5 节点](https://wiki.metacubex.one/config/proxies/socks/)、[Mihomo DNS](https://wiki.metacubex.one/config/dns/)、[MetaCubeX 规则数据库](https://github.com/MetaCubeX/meta-rules-dat)、[V2Fly TikTok 域名](https://github.com/v2fly/domain-list-community/blob/master/data/tiktok)、[IPRoyal 协议支持](https://help.iproyal.com/en/articles/7222799-which-internet-protocols-does-iproyal-support)。
