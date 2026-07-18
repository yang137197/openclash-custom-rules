# OpenClash 自定义覆写规则

本仓库用于给第三方订阅转换模板追加两类分流，不接管或替换模板本身：

- ChatGPT、OpenAI、Claude、Gemini、AI Studio、Flow 等 AI 服务走 `AI-日本`。
- Ozon、Wildberries 等俄罗斯电商服务走 `俄罗斯电商`。
- 第三方模板原有策略组、DNS 和其他规则保持不变。

## 覆写订阅地址

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/overwrite/openclash-overwrite.conf
```

备用地址：

```text
https://cdn.jsdelivr.net/gh/yang137197/openclash-custom-rules@main/overwrite/openclash-overwrite.conf
```

在 OpenClash 的“覆写设置 → 模块设置”中新建远程订阅，填入主地址并启用，然后更新配置订阅并应用。

## 当前行为

- `AI-日本` 自动收集节点名中带日本、东京、大阪、Japan、Tokyo、Osaka 或 JP 的节点，并按延迟自动选择。
- `俄罗斯电商` 自动收集俄罗斯节点。当前机场没有俄罗斯节点时只显示 `DIRECT`，不会生成空策略组；后续加入俄罗斯节点后会自动出现。
- 两条业务规则会插入到第三方模板规则最前面，优先于模板的 CN 和 MATCH 规则。

## 文件

- `overwrite/openclash-overwrite.conf`：远程覆写模块。
- `rules/ai.yaml`：AI 服务 classical 规则集。
- `rules/ru-commerce.yaml`：Ozon / Wildberries classical 规则集。

仓库不得提交机场订阅链接、Sub-Store 地址、令牌或其他密钥。
