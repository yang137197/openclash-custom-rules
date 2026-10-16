# 仓库维护规范

## 当前正式基线

当前唯一支持方案是 `tiktok-router-loongproxy-jp-us v1.0.0`（J1–J11，stable），索引位于 `profiles/catalog.json`。用户于 2026-10-16 确认实机验收通过并授权正式发布；不补写用户未提供的逐项日志或指标。

**不可改变的链路前提：**路由器本地 Loongproxy 美国 SOCKS5 必须通过用户手选的 iKuuu 日本节点建立链式代理。`TikTok-ISP-Local` 必须保留 `dialer-proxy: 日本-入口` 与 `udp: false`。日本入口自动筛选已加载节点中名称含 `jp`、`日本`、`Japan` 或 🇯🇵 的节点（忽略大小写），但必须由用户选中实际 iKuuu 日本节点。日本节点缺失或不可用时失败关闭，严禁切换美国首跳、其他机场首跳、机场/DIRECT 回退。

Google/Google Play 与其他境外流量走用户手选的美国组；中国大陆域名和 IP 直连；保留完整 129 条 Manual-Direct。日本、美国和 ISP 组均须排除本地 ISP 节点以避免递归，空组保持 REJECT。

## 配置与凭据

- 单个配置仅启用一个完整云覆写及其配套本地节点模块。云模块管理规则；本地模块只追加精确名为 `TikTok-ISP-Local` 的 SOCKS5 节点。
- 更新规则只刷新正式云覆写模块并重启 OpenClash；机场节点订阅、GEO 数据各自更新。
- 修改 Loongproxy 密码时，只在路由器本地 `TikTok-ISP-Local` 模块改 `password`；按本地服务商提供的信息同步修改 `username`、`server`、`port`（如有变化）。保留节点名、`type: socks5`、`udp: false`、`dialer-proxy: 日本-入口`。详细 UI 路径见版本 `SETUP.md`。
- 真实 ISP 主机、账号和密码只存路由器本地模块，不进入仓库、云覆写、PR 或日志。公共仓库只保留 `.example` 占位模板。
- 所有模块仅含 `[YAML]`；OpenClash 插件选项由用户在 LuCI 手工设置，禁止覆写模块写入 `[General]`、UCI 或自动修改插件设置。

## 规则与版本

- 保持规则优先级：私网/局域网 → TikTok ISP → 同范围 TikTok REJECT → Google/Play → Manual-Direct → 中国大陆域名/IP → 美国 MATCH。
- `rules/manual-direct.yaml` 保留原始 129 条；`rules/manual-direct-isp.yaml` 按原顺序逐条转换为 `DOMAIN-SUFFIX` 并保留重复项。若授权改规则，须同步固定模块、滚动模块、inline payload、校验和与文档。
- 已发布版本目录和标签不可改写、移动或覆盖。行为变化须建立新候选版本及独立完整 URL；真实设备验收前保持 candidate。晋升 stable、创建正式标签和 GitHub Release 需用户明确授权。
- 已停用方案当前文件已清理；历史 Git 提交、标签和 Release 保留。不要为清理而重写历史。

## 每次变更门禁

阅读 `AGENTS.md`、`profiles/catalog.json` 和受影响版本的 `REQUIREMENTS.md`；标明需求编号与版本类型；完成对应文档和 `CHANGELOG.md`；检查凭据及完整差异；运行：

```text
python -m unittest discover -s scripts -p "test_*.py"
python scripts/validate_repository.py --base-ref origin/main
git diff --check
```

若没有可用 Git 比较基线，可省略 `--base-ref`，但不得声称历史保护校验已执行。静态检查、桌面核心夹具与真实设备验收必须分开记录。
