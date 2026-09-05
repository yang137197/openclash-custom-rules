# OpenClash 自定义覆写规则

本仓库提供一份统一分流覆写：局域网/私有地址、手工直连域名和中国大陆网站走 `DIRECT`；其余所有流量统一使用“美国”策略组。当前配置不按设备、地区或应用拆分流量。

## 覆写地址

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/overwrite/openclash-overwrite.conf
```

在 OpenClash“覆写设置 → 模块设置”中只保留并启用本地址，更新覆写后应用配置并重启一次。

## 策略组

仅保留 `美国`：从订阅中筛选美国节点并自动测速选择。它是唯一的海外出口，不能手动切换到日本或其他地区。

覆写会强制替换订阅自带的策略组和规则，因此 AI、日本、GLOBAL、故障转移、自动选择等旧组不会继续显示或参与分流。未被美国组匹配的订阅节点仍会随订阅下载，但不会进入任何策略组或被使用。

## 分流顺序

1. 局域网、链路本地、组播和私有地址 → `DIRECT`
2. `rules/manual-direct.yaml` 中的手工直连域名 → `DIRECT`
3. 中国大陆域名（`GEOSITE,cn`）和中国大陆 IP（`GEOIP,CN`） → `DIRECT`
4. 其他所有连接（含 AI）→ `美国`

手工直连域名请使用 `DOMAIN-SUFFIX`，例如：

```yaml
payload:
  - DOMAIN-SUFFIX,example.cn
```

规则提供者每 60 秒检查更新。DNS 对中国大陆/私有域名使用国内 DNS，其余查询经“美国”策略组发送；IPv6 DNS 关闭以避免绕过上述 IPv4 分流。

## 文件

- `overwrite/openclash-overwrite.conf`：远程覆写模块。
- `rules/manual-direct.yaml`：手工直连域名。
- `docs/acceptance-log.md`：验收记录。
- `CHANGELOG.md`：更新日志。
