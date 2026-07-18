# OpenClash 自定义覆写与规则

适用于 OpenClash `v0.47.116 alpha`（Meta/Mihomo 内核）的远程覆写配置。

目标：

- `AI`：自动收集所有日本节点，供 ChatGPT、Claude/Claude Code、Gemini、Nano Banana 使用。
- `俄罗斯`：自动收集所有俄罗斯节点，供 Ozon、Wildberries 等俄罗斯电商使用。
- `美国`：自动收集所有美国节点，暂时不绑定业务规则。
- 中国大陆域名和 IP 直连，其余流量进入 `默认代理` 手动选择。
- 多个订阅先在 Sub-Store 合并；机场订阅地址只保存在本地，不提交到本仓库。

> 原始需求中的“美国策略组包含所有俄罗斯节点”按笔误修正为“包含所有美国节点”。

## 文件

- `overwrite/openclash-overwrite.conf`：OpenClash 覆写模块远程订阅文件。
- `rules/ai.yaml`：AI 服务规则集。
- `rules/ru-commerce.yaml`：俄罗斯电商规则集。

## 使用地址

仓库发布到 `yang137197/openclash-custom-rules` 后：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/overwrite/openclash-overwrite.conf
```

在 OpenClash 的“覆写设置 / 模块设置”中新建远程订阅，填入上面的地址并启用。覆写文件会继续远程引用本仓库中的两个规则集。

## Sub-Store 建议流程

1. 在 PVE 上单独创建一个轻量 Debian LXC，安装 Docker 后运行 Sub-Store；不要把 Docker 直接装在 PVE 宿主机或路由器里。
2. Sub-Store 仅在局域网开放前端端口，后端路径使用随机字符串；不要把后端 `3000` 端口暴露到公网。
3. 把三个以上机场订阅分别添加到 Sub-Store，再创建“组合订阅”。
4. 组合订阅目标格式选择 `Mihomo`，OpenClash 只订阅这个本地组合地址。
5. 机场订阅链接、Sub-Store 后端路径和令牌都不要写入公开 GitHub 仓库。

推荐的容器环境变量示例（把占位符换成随机字符串和实际局域网地址）：

```yaml
services:
  sub-store:
    image: xream/sub-store:latest
    restart: always
    volumes:
      - ./data:/opt/app/data
    environment:
      SUB_STORE_FRONTEND_BACKEND_PATH: /你的随机后端路径
      SUB_STORE_CORS_ALLOWED_ORIGINS: http://你的局域网IP:3001
    ports:
      - "3001:3001"
```

浏览器访问：

```text
http://你的局域网IP:3001?api=http://你的局域网IP:3001/你的随机后端路径
```

## 节点命名与自动分组

分组依靠节点名称匹配国家/城市。推荐让节点名称保留地区信息，例如：

```text
JP日本东京1号
RU俄罗斯莫斯科1号
USA美国洛杉矶1号
```

规则已经兼容国旗、中文国家名、英文国家名、常见城市名以及独立的 `JP`、`RU`、`US/USA` 标识。特别避免用裸 `US` 匹配，防止把 `Russia` 误识别为美国节点。

## 规则顺序

规则从上往下匹配：

1. 局域网与私有地址直连。
2. 俄罗斯电商走 `俄罗斯`。
3. AI 服务走 `AI`。
4. 中国大陆域名/IP 直连。
5. 其余进入 `默认代理`。

业务规则放在中国大陆直连之前，可以避免某些服务的 CDN 或解析结果被过早归入大陆直连。

## 更新与回滚

- 修改规则后提交到 `main`，OpenClash/Mihomo 会按 `interval` 自动更新远程规则集。
- 立即生效可在 OpenClash 中手动更新规则提供者，或重启 OpenClash。
- 修改策略组或覆写文件后，应手动更新覆写订阅并重启 OpenClash。
- 回滚时在 GitHub 恢复到上一个可用提交即可。

## 注意事项

- 不建议把整个 `.ru`、Google、GitHub 或 Cloudflare 都强制到某一策略组；范围过大会误伤无关网站。
- AI 服务的登录、风控和会话通常要求出口地区相对稳定。先在 `AI` 组手动选择一个稳定日本节点，不要频繁自动切换。
- 如果某个节点名称无法被自动收集，优先统一重命名；也可再补充 `filter` 正则。
- 若规则命中不符合预期，请先查看 OpenClash 连接记录中的“规则/策略组”，再按实际域名增补，避免凭猜测扩大规则范围。
