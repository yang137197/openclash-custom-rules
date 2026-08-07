# OpenClash 自定义覆写规则

本仓库为第三方订阅转换模板追加统一分流，不接管或替换模板本身：

- 霖洋 A 手机（`192.168.100.173`）：中国大陆直连，其余服务固定走 `社媒-日本`，包括 AI、TikTok、WhatsApp、Facebook 和 Google。
- 霖洋 B 手机（`192.168.100.238`）：中国大陆直连，其余服务固定走 `社媒-美国`，包括 AI、TikTok、WhatsApp、Facebook 和 Google。
- ChatGPT、OpenAI、Claude、Gemini、AI Studio、Flow 等 AI 服务在其他设备上走 `AI-日本`。
- Ozon、Wildberries 等俄罗斯电商服务在其他设备上走 `俄罗斯电商`。
- 自定义策略组自动排除免费、公益、试用、测试及订阅信息节点。
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

## 使用要求

- OpenClash 使用规则模式、Fake-IP、IPv6 流量代理、IPv6 DNS 解析和 UDP 流量转发。
- IPv6 代理模式使用 TProxy，并将“实验性：绕过指定区域 IPv6”设为“绕过中国大陆”。
- A、B 手机的网关和 DNS 必须是 CatWrt，并通过 DHCP 静态租约保持上述 IPv4 地址。
- `社媒-日本`和`社媒-美国`是手动选择组。首次启用后必须分别选择稳定的日本、美国节点；未选择可用节点时默认 `REJECT`，避免意外直连。
- 手机需要保持固定 Wi-Fi MAC 或确保静态租约匹配当前 Wi-Fi 使用的 MAC。

## IPv6 行为

- 中国大陆域名和中国大陆 IPv4/IPv6 直连。
- 国外 IPv6 在内核中拒绝，客户端回落到 IPv4 后再按设备来源地址进入日本或美国组。
- 不要将 `::/0` 加入 OpenClash 的“本地 IPv6 绕过地址”，否则所有 IPv6 都会绕过内核。

## 当前策略优先级

1. 局域网地址直连。
2. A/B 手机访问 Google Play 中国域名时按各自地区代理。
3. 中国大陆域名和 IP 直连。
4. 国外 IPv6 拒绝。
5. A 手机国外 IPv4 走日本，B 手机国外 IPv4 走美国。
6. 其他设备依次使用俄罗斯电商、AI 日本及第三方模板规则。

## 文件

- `overwrite/openclash-overwrite.conf`：远程覆写模块。
- `rules/device-jp.yaml`：A 手机日本分流来源地址。
- `rules/device-us.yaml`：B 手机美国分流来源地址。
- `rules/ai.yaml`：AI 服务 classical 规则集。
- `rules/ru-commerce.yaml`：Ozon / Wildberries classical 规则集。

仓库不得提交机场订阅链接、Sub-Store 地址、令牌或其他密钥。
