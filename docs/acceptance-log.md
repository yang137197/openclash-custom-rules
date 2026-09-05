# 验收记录

## 2026-09-05：通用多人多设备重构

### 配置目标

- 中国大陆域名/IP → `DIRECT`
- `Manual-Direct` 手工规则 → `DIRECT`
- 局域网/私有地址 → `DIRECT`
- 其他全部 → `美国`
- `美国` 类型为 `select`，用户手工选择节点
- 非美国节点保留在订阅底层，但不进入任何策略组
- 不按设备、人员、MAC、固定 IP 拆分规则
- 不整体覆盖 OpenClash 自动生成的 `rule-providers`

### 必须通过的启动检查

更新覆写后，OpenClash 必须能正常启动。

日志中不得出现：

```text
Parse config error
not found rule-set: oc-cn-domain
not found rule-set
```

### 最终配置检查

1. `fake-ip-filter` 中如果 OpenClash 自动加入 `rule-set:oc-cn-domain`，最终 `rule-providers` 中必须仍存在对应 `oc-cn-domain`。
2. `rule-providers` 中应同时保留 OpenClash 内部 provider 与本仓库的 `Manual-Direct`。
3. 主规则最后一条必须是：

```text
MATCH,美国
```

4. `美国` 必须为 `select`，不是 `url-test`。
5. `美国` 策略组中只应出现美国节点。

### 流量验收

#### 中国大陆网站

访问常见中国大陆网站，连接日志应显示 `DIRECT`。

#### 国外网站

访问 Google、ChatGPT 等未列入直连规则的国外站点，应命中 `美国`。

#### 手工直连

访问 `rules/manual-direct.yaml` 中的域名，应命中 `Manual-Direct` 后直连。

#### 局域网 / WireGuard

访问 PVE、NAS、路由器、WireGuard 私网地址时不应进入美国代理。

#### 自建回流域名

`pve.yangnas.cn`、`auth.yangnas.cn`、`nexus.yangnas.cn` 应返回真实 IP 而不是 Fake-IP；实际是否访问内网地址取决于当前 DNS/回流解析环境。

### DNS 验收

- 大陆/私有域名使用国内 DNS 策略。
- 国外 DNS 上游连接遵循 `美国` 策略。
- `respect-rules` 保持开启。

### 维护验收

以后新增普通“必须直连”的网站，只修改：

```text
rules/manual-direct.yaml
```

优先写：

```yaml
- DOMAIN-SUFFIX,example.com
```

不要为了新增一个直连网站修改主 `rules!`。

---

## 历史说明

2026-09-05 早期版本曾增加 `[Overwrite]` Ruby 兼容逻辑，并整体替换 `rule-providers`。该方式删除了 OpenClash 自动生成的 `oc-cn-domain`，但 `fake-ip-filter` 仍引用它，导致 Mihomo 报：

```text
Parse config error: not found rule-set: oc-cn-domain
```

该设计已废弃，不应恢复。
