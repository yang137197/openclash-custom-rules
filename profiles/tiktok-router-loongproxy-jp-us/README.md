# tiktok-router-loongproxy-jp-us

**v1.0.8 stable**：用户于2026-11-26确认达到验收标准；本轮调试日志及模块顺序截图已核对。四组原生自动策略，无独立控制器、服务安装或面板定制。

## 当前正式版

- [v1.0.8 GitHub Release](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-v1.0.8)
- [v1.0.8 正式需求与验收范围](versions/v1.0.8/REQUIREMENTS.md)
- [v1.0.8 设置、应用与完整回退](versions/v1.0.8/SETUP.md)
- [v1.0.8 环境记录](versions/v1.0.8/ENVIRONMENT.json)
- [v1.0.8 本地和实机验证](versions/v1.0.8/VALIDATION.md)
- [v1.0.8 唯一本地占位模板](versions/v1.0.8/local-tiktok-proxy.conf)
- [v1.0.8 固定完整云覆写](versions/v1.0.8/openclash-overwrite.conf)

v1.0.8 固定完整云覆写：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.8/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.8/openclash-overwrite.conf

## 日常滚动订阅

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf

云模块使用原main远程订阅，配对本地模块保存两个机场订阅及原Loongproxy美国ISP参数。已验收候选的云/本地模板与正式运行文件逐字节相同，只需把云订阅改回原main地址并更新、重启；不重填凭据。

## 业务边界

TikTok首跳：仅iKuuu日本Z数字IEPL自动低延迟；Tiktok美国出口测速：固定本地TikTok-ISP-Local，socks5/udp:false/dialer-proxy: TikTok首跳；良心云-日本专线流媒体：日本专线与高速01–99编号顺序fallback；ikuuu-默认代理：iKuuu日本自动低延迟。四组/提供商60秒/5秒/204检测，GLOBAL不检测。

TikTok UDP进入核心时按保护规则REJECT，不因此更换美国ISP出口。Claude/AI和普通网页/API默认iKuuu，指定流媒体及下载走良心云。健康204不代表带宽或解锁，具体名单和限制见合同。

手动直连唯一源仍为rules/manual-direct.yaml，不锁定域名清单、数量或源哈希；工作流生成同一滚动模块和哈希。先确认同步成功，再更新并重启。已发布版本不随日常源修改。

## 历史版本

v1.0.7：自动化手动直连生成和滚动同步，用户于2026-10-28验收。v1.0.6及更早发布快照保留。原方案早期Claude经ISP、默认美国和手选首跳要求由v1.0.8明确重构替代，旧合同不改写。

- v1.0.1 candidate：历史未验收的Samsung更新域名直连候选。
- v1.0.2 candidate：历史未验收的Claude Code端点候选。
- v1.0.3 candidate：历史未验收的Claude/Anthropic第一方域名候选。
