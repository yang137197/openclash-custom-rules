# 良心云 Lua 控制器 v1.8.0 设置与验收

**candidate；本轮仅本地开发，不安装路由器服务或应用覆写。** 当前设备仍为 v1.5.0 手选方案，良心云日本专线02保持；正式滚动地址不变。

## 完整脚本只读预检已完成

2026-11-24 用户回传固定提交 `bb28b5bad20fd25dc2e2888f16d57e1cb22814b0` 的 `--preflight` 结果：Lua 5.1、核心 alpha-gbc76c13、readOnly=true、selectionApplied=false，当前良心云日本专线02，candidateCompatible=false、nativeLockTested=false、formalAcceptance=false。已证实完整脚本能完成基础读取；旧手选方案上的false与预期一致，但本摘要不含具体合同不匹配原因。没有应用候选或验收自动运行。

运行本目录 `liangxinyun-controller.lua --preflight`，也可不传模式参数。读取已有 UCI 中的 API 端口和 secret，只连接 `127.0.0.1`；检查 Lua／JSON／nixio 接口、时钟和版本、组与 provider 的一致性。无测速、PUT、锁／状态文件写入或服务操作。输出 `candidateCompatible: false` 在当前旧手选方案上是预期结果，不需要为了预检切换配置；`nativeLockTested: false` 表示只检查接口存在，未实际加锁。

`--dry-run` 也不测速、不写文件或选择，但要求严格候选形状；旧方案应拒绝模拟接管。`--once` 和 `--run` 有检测与切换副作用，当前不在路由器执行。

## 独立原生锁单次测试已通过

用户明确允许“仅原生锁测试”后，运行固定提交 `79f657d40b7ce6daaa02086f039698d7823f81c0` 的[独立诊断](../../../../scripts/LIANGXINYUN_NATIVE_LOCK.md)。2026-11-24回传确认原生父进程加锁、子进程抢锁受阻、释放后子进程取得锁、描述符关闭均通过；API／检测请求为0，选择未应用，正式验收仍为false。此单次授权已执行完毕，不自动重测；不涵盖状态文件写入、更名、控制器启停或完整自动运行。

下一项建议先验证隔离临时目录中的状态文件写入与原子替换，不接入OpenClash API。该项仅为建议，尚未授权或执行；不因此安装或启用服务。

## 后续部署草案（本轮不执行）

控制器为三个独立文件：Lua 主程序、`.run` Shell 停止监督、`.init` procd 服务模板。未来部署分别使用 `/usr/share/openclash/liangxinyun-controller.lua`、`/usr/share/openclash/liangxinyun-controller.run`、`/etc/init.d/liangxinyun-controller`。不自动安装依赖或更改插件选项。服务实际调用 Shell 父进程，再由它启动 `lua ... --run`；不能把直接向 Lua 发送 TERM 当作有清理保证的正常停止。

临时文件上的原生锁已单项通过；状态写入、监督退出、procd 启停／重启、目标核心的完整轮询仍须分步验证；未通过前不 enable。未来应用候选时，仍在 **服务 → OpenClash → 运行状态 → 覆写模块** 更换完整远程模块内容，匹配当前 iKuuu 配置完整路径，远程完整模块在原本地凭据模块上方，更新后重启 OpenClash。正式地址当前保持 v1.5.0，不发布未经验收的候选。

候选严格 Selector 的初始选择为 REJECT，未运行控制器时普通代理不能依靠它自动恢复。控制器只写良心云，TikTok 首跳和出口组仍按已验收值手选。默认 60 秒完整检测、2 秒轮询、130 秒记录有效期，不额外添加延迟容差或稳定等待；显示 select 仅作为自动控制入口，手工改动会被下一轮覆盖。

正常停止尽力 REJECT，无法访问 API 时状态明确未验证；强杀、掉电可能保留上次选择。procd `respawn 3600 5 5` 有限重试，`term_timeout 100` 后仍未退出可被强杀；没有承诺无中断迁移或永久失败关闭。回退应先恢复正式覆写并重启 OpenClash，确认控制器不再接管旧组，再停止／禁用服务并恢复良心云原手选值。不要在严格候选仍生效时单独停服务作为回退。

## OpenClash 独立手工设置

模块只含 `[YAML]`，保留 v1.5.0 建议，现有用户沿用当前值。本候选目标为已报告 OpenClash 0.48.002／alpha-gbc76c13／CatWrt OpenWrt 24.10.2 x86_64；已有 Lua 5.1 和 curl 8.11.1，完整控制器未实机验收。

| 页面（服务 → OpenClash 下） | 设置 | 建议与适用条件 |
| --- | --- | --- |
| 插件设置 → 模式设置 | 运行模式 / 代理模式 | 方案基线：Fake-IP（增强），非 TUN、非混合；规则模式 |
| 同上 | UDP 流量转发 | 开启；TikTok 本地 SOCKS5 仍必须 `udp: false` |
| 同上 | 旁路网关兼容 | 主路由或回程正常时关闭，仅依据旁路回程证据调整 |
| 插件设置 → 流量控制 | 路由器本机代理 | 开启 |
| 同上 | 实验性：绕过指定区域 IPv4 | 沿用绕过中国大陆，MetaCubeX `cn.mrs` |
| 同上 | 禁用 QUIC | 建议开启；当前实机停用，本候选不改现值 |
| 同上 | 绕过服务器地址 / 仅允许内网访问 | 开启 |
| 同上 | 仅允许常用端口流量 | 关闭 |
| 插件设置 → IPv6 设置 | IPv6 代理 / IPv6 DNS / 区域 IPv6 绕过 | 关闭，核对客户端没有独立 IPv6 出口 |
| 插件设置 → DNS 设置 | 本地 DNS 劫持 | Dnsmasq 转发 |
| 覆写设置 → DNS 设置 | 自定义上游 DNS / 遵守路由规则 / Fake-IP 持久化 | 方案必需：开启；界面需要条目时保留 HTTPS `223.5.5.5:443` |
| 同上 | 附加上游 DNS / 自动追加默认 DNS / Fallback | 关闭，由云模块管理解析器 |
| 同上 | 自定义 Fake-IP-Filter | 开启，rule 模式，不填旧黑名单列表 |
| 覆写设置 → Meta 设置 | 域名嗅探 / 纯 IP 嗅探 / 进程查找 | 嗅探开启，进程查找 off |
| 覆写设置 → 规则设置 | 仅代理命中规则流量 / 额外本地自定义规则 | 关闭 |
| 插件设置 → GEO 数据库订阅 / 大陆白名单订阅 | GeoSite、GeoIP、大陆 IPv4 列表 | 确认下载有效，保持更新 |

DNS、规则、TikTok 组及 148 条直连内容与 v1.7.0 有效 YAML 相同；本地凭据模板与 v1.5.0 逐字节相同。实际设备仍是 141 条直连，不能把仓库快照一致当作实机直连已更新；7 条既有维护差异在未来部署前单独核对，本轮不应用。客户端继续使用路由器 DNS；IPv6 代理关闭不等于全网 IPv6 关闭，QUIC 拒绝可能发生在内核之前。

## 验收记录

先核对新脚本只读预检，再单独安排原生运行测试。正式验收须覆盖普通代理、四档部分／整档故障与恢复、订阅变更、锁互斥、控制器与核心重启、正常停止、TikTok 播放和直连样例；记录时间与新连接实际出口。应用后在 **运行日志 → 调试日志 → 生成日志**取得对应脱敏证据，用户确认后才可发布。

正式回退入口：

https://raw.githubusercontent.com/yang137197/openclash-custom-rules/main/profiles/tiktok-router-loongproxy-jp-us-liangxinyun/overwrite/openclash-overwrite.conf

依据：[OpenClash API §15.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/15-api.md)、[覆写模块 §16.1、§16.2](https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/16-overwrite-module-format.md)、[OpenWrt procd 参数](https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/system/procd/files/procd.sh)。不得分享已填模块、原始调试日志或 secret。
