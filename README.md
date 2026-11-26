# OpenClash 远程覆写规则

当前正式方案为 **tiktok-router-loongproxy-jp-us v1.0.8 / stable**。用户于2026-11-26确认验收通过，原生双订阅方案沿原版本线迭代，无独立控制器或安装服务。

## 方案目录

| 方案 | 适用需求 | 稳定版本 | Release | 固定覆写链接 | 部署与设置 |
|---|---|---|---|---|---|
| [tiktok-router-loongproxy-jp-us](profiles/tiktok-router-loongproxy-jp-us/README.md) | iKuuu日本自动首跳/默认代理、Loongproxy美国TikTok出口、良心云日本顺序流媒体、国内及手动直连 | v1.0.8 | [Release](https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-v1.0.8) | [v1.0.8 YAML](https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.8/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.8/openclash-overwrite.conf) | [设置与回退](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.8/SETUP.md) |

## 日常滚动覆写订阅

继续使用原地址，正式发布后包含v1.0.8；以后手动直连域名仍通过此地址更新：

```text
https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf
```

已完成候选测试的用户保留配对本地模块，把云模块的候选固定提交URL改回上面main地址，更新并重启OpenClash。v1.0.8云、本地模块必须配套；不要混用旧的日本-入口引用。

## 四组分工

| 策略组 | 选择与用途 |
|---|---|
| TikTok首跳 | 仅iKuuu日本Z数字IEPL，自动检测并选最低延迟 |
| Tiktok美国出口测速 | 固定原Loongproxy美国ISP，经TikTok首跳检测完整代理链 |
| 良心云-日本专线流媒体 | 仅良心云日本专线流媒体/高速CUCM，按两位编号专线→高速顺序故障切换和恢复 |
| ikuuu-默认代理 | 仅iKuuu日本节点，最低延迟；Google、AI/Claude、网页/API等默认代理 |

四组及提供商60秒/5000毫秒/204检测；GLOBAL不定时检测。不改面板。指定流媒体、网盘、游戏平台和专用下载域名走良心云，国内/局域网和手动直连保留；TikTok不回退普通机场或DIRECT。完整平台名单、排序及限制见[合同](profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.8/REQUIREMENTS.md)。

## 手动直连与版本维护

rules/manual-direct.yaml是唯一手动直连源。payload中的合法DOMAIN/DOMAIN-SUFFIX可任意增删，不固定清单、数量或源哈希；保留语法和逐项同序同步校验及重复项。提交main后等待Sync manual direct rules工作流和生成提交成功，再更新同一滚动云模块并重启。日常数据维护不创建版本/Release，不改已发布快照。

v1.0.8 是当前正式版；v1.0.7及更早发布快照、标签和Release保留且不可改写。大版本更新/重构创建递增候选，实机验收后同步原滚动地址。开发与发布门禁见[DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md)。更换工具时在已打开仓库中说“请你先读取仓库，我们继续开发”。

## 固定版本

标签固定覆写不会随日常直连源更新：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.8/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.8/openclash-overwrite.conf

Release只附一个.conf本地占位模板；两个订阅和ISP真实值仅保存在用户本地，禁止提交Git/GitHub。字段说明和虚构示例写在Release正文。
