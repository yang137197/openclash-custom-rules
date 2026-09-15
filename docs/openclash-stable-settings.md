# OpenClash 当前稳定配置参数表

> 快照时间：2026-09-15 17:40:37 +0800  
> 用途：记录当前已实机稳定运行的 OpenClash / Mihomo 设置，便于重装、恢复和后续 AI/Codex 维护。  
> 本文档只记录可公开的设置项，不保存订阅 URL、节点定义、用户名、密码、Dashboard Secret、Token 或本地代理凭证。

## 1. 当前环境

| 项目 | 当前值 |
|---|---|
| Linux 内核 | `6.12.38` |
| OpenClash 版本 | `0.47.156` |
| Mihomo 核心 | `Mihomo Meta alpha-ge183c58 linux amd64 with go1.26.5 Mon Aug 10 14:33:14 UTC 2026` |

## 2. 已实机验证的稳定基线

| 设置项目 | UCI 参数 | 当前稳定状态 | 保存值 |
|---|---|---|---|
| OpenClash 启用 | `openclash.config.enable` | **开启** | `1` |
| 核心类型 | `openclash.config.core_type` | **Meta** | `Meta` |
| 运行模式 | `openclash.config.en_mode` | **Fake-IP（TUN）** | `fake-ip-tun` |
| TUN 网络栈 | `openclash.config.stack_type` | **System** | `system` |
| 代理模式 | `openclash.config.proxy_mode` | **Rule** | `rule` |
| DNS 增强模式 | `openclash.config.operation_mode` | **Fake-IP** | `fake-ip` |
| 路由器本机代理 | `openclash.config.router_self_proxy` | **开启** | `1` |
| 绕过中国大陆 IPv4 | `openclash.config.china_ip_route` | **开启** | `1` |
| 禁用 QUIC（UDP/443） | `openclash.config.disable_udp_quic` | **开启** | `1` |
| 禁用 quic-go GSO | `openclash.config.disable_quic_go_gso` | **开启** | `1` |
| TCP 并发 | `openclash.config.enable_tcp_concurrent` | **开启** | `1` |
| 统一延迟 | `openclash.config.enable_unified_delay` | **开启** | `1` |
| 流量（域名）探测 / Sniffer | `openclash.config.enable_meta_sniffer` | **开启** | `1` |
| 探测（嗅探）纯 IP 连接 | `openclash.config.enable_meta_sniffer_pure_ip` | **开启** | `1` |
| 自定义嗅探设置 | `openclash.config.enable_meta_sniffer_custom` | **开启** | `1` |
| IPv6 代理 | `openclash.config.ipv6_enable` | **关闭** | `0` |
| IPv6 DNS | `openclash.config.ipv6_dns` | **关闭** | `0` |
| DNS 重定向 | `openclash.config.enable_redirect_dns` | **开启** | `1` |
| 自定义 DNS | `openclash.config.enable_custom_dns` | **开启** | `1` |
| DNS 遵循规则 | `openclash.config.enable_respect_rules` | **开启** | `1` |
| 追加 Default DNS | `openclash.config.append_default_dns` | **关闭** | `0` |
| 追加 WAN DNS | `openclash.config.append_wan_dns` | **最终未追加，以仓库覆写 `0` 为准** | `1`（本地 UCI 保存值） |
| Fake-IP 缓存 | `openclash.config.store_fakeip` | **开启** | `1` |
| 自定义 Fake-IP Filter | `openclash.config.custom_fakeip_filter` | **开启** | `1` |
| Fake-IP Filter 模式 | `openclash.config.custom_fakeip_filter_mode` | **blacklist（黑名单）** | `blacklist` |
| 仅代理命中规则流量 | `openclash.config.enable_rule_proxy` | **关闭** | `0` |
| 旁路网关兼容模式 | `openclash.config.bypass_gateway_compatible` | **关闭** | `0` |
| 跳过代理服务器地址 | `openclash.config.skip_proxy_address` | **关闭** | `0` |
| 自定义 Clash 规则 | `openclash.config.enable_custom_clash_rules` | **开启** | `1` |
| 禁用 MASQ 缓存 | `openclash.config.disable_masq_cache` | **开启** | `1` |

### 当前关键组合

```text
运行模式：Fake-IP（TUN）
TUN 网络栈：System
代理模式：Rule
DNS 增强模式：Fake-IP
绕过中国大陆 IPv4：开启
QUIC（UDP/443）：禁用
quic-go GSO：禁用
TCP 并发：开启
统一延迟：开启
域名嗅探：开启
纯 IP 嗅探：开启
自定义嗅探：开启
IPv6 代理：关闭
IPv6 DNS：关闭
DNS 重定向：开启
自定义 DNS：开启
DNS 遵循规则：开启
追加 Default DNS：关闭
追加 WAN DNS：最终不追加，以仓库覆写 APPEND_WAN_DNS=0 为准
Fake-IP 缓存：开启
Fake-IP Filter：开启 / blacklist
```

## 3. 已验证行为

- 中国大陆常规域名/IP：`DIRECT`。
- `Manual-Direct` 命中项：`DIRECT`。
- Google / GitHub / YouTube / ChatGPT 等未命中直连规则的海外流量：进入 `美国` 策略组。
- TikTok：按仓库规则进入 `TikTok-ISP`，本地 IPRoyal 凭证不进入 GitHub。
- OneDrive Consumer 网页/文件链路：按主覆写强制进入 `美国`。
- 2026-09-15 实机验证：京东商品图片正常、微信语音双向正常、企业微信语音双向正常、米家设备正常。

## 4. 历史不稳定组合（不要默认恢复）

| 组合 | 已观察到的问题 |
|---|---|
| Fake-IP（增强） | 京东商品图片加载卡顿/白屏 |
| Fake-IP（TUN-混合） | 微信/企业微信语音出现单向无声 |
| Fake-IP（TUN） + System | 当前稳定基线 |

## 5. “追加 WAN DNS”的最终记录

路由器 UCI 中曾读取到：

```text
append_wan_dns = 1
```

但实机最终生成的 `/etc/openclash/config.yaml` 中：

```yaml
nameserver:
  - https://1.1.1.1/dns-query#美国
  - https://8.8.8.8/dns-query#美国
```

没有出现上游网关 `192.168.5.1`，也没有出现 `dhcp://eth1`。因此当前实际运行结果是：**WAN DNS 没有被追加到 Mihomo 的 `nameserver`**。

仓库远程覆写当前为：

```text
APPEND_WAN_DNS = 0
```

所以以后重装或恢复时，**按仓库覆写的 `APPEND_WAN_DNS=0` 执行即可，不需要手工开启“追加 WAN DNS”**。UCI 中的 `1` 只作为当时本地保存值保留在原始快照中，不作为恢复目标。

## 6. 完整 OpenClash UCI 主设置快照（脱敏）

> 本节是 2026-09-15 当时路由器 UCI 的原始脱敏快照，用于追溯。恢复时优先参考上面的“稳定基线”，不要机械照抄与最终生效配置冲突的本地保存值。

```text
openclash.config.append_default_dns='0'
openclash.config.append_wan_dns='1'
openclash.config.auto_restart='0'
openclash.config.auto_restart_day_time='0'
openclash.config.auto_restart_week_time='1'
openclash.config.auto_smart_switch='0'
openclash.config.auto_update='1'
openclash.config.auto_update_time='0'
openclash.config.bypass_gateway_compatible='0'
openclash.config.cachesize_dns='1'
openclash.config.china_ip_route='1'
openclash.config.chnr6_custom_url='https://ispip.clang.cn/all_cn_ipv6.txt'
openclash.config.chnr_auto_update='1'
openclash.config.chnr_custom_url='https://ispip.clang.cn/all_cn.txt'
openclash.config.chnr_update_day_time='0'
openclash.config.chnr_update_week_time='1'
openclash.config.cn_port='9090'
openclash.config.config_auto_update_mode='0'
openclash.config.config_path='<LOCAL_CONFIG_PATH_REDACTED>'
openclash.config.config_update_week_time='1'
openclash.config.core_type='Meta'
openclash.config.core_version='linux-amd64-v1'
openclash.config.custom_fakeip_filter='1'
openclash.config.custom_fakeip_filter_mode='blacklist'
openclash.config.custom_fallback_filter='0'
openclash.config.custom_host='0'
openclash.config.custom_name_policy='0'
openclash.config.custom_proxy_server_policy='0'
openclash.config.dashboard_forward_ssl='0'
openclash.config.dashboard_password='<REDACTED>'
openclash.config.dashboard_type='Official'
openclash.config.default_resolvfile='/tmp/resolv.conf.d/resolv.conf.auto'
openclash.config.delay_start='0'
openclash.config.disable_masq_cache='1'
openclash.config.disable_quic_go_gso='1'
openclash.config.disable_udp_quic='1'
openclash.config.dns_port='7874'
openclash.config.dnsmasq_cachesize='0'
openclash.config.dnsmasq_noresolv='0'
openclash.config.dnsmasq_resolvfile='/tmp/resolv.conf.d/resolv.conf.auto'
openclash.config.en_mode='fake-ip-tun'
openclash.config.enable='1'
openclash.config.enable_custom_clash_rules='1'
openclash.config.enable_custom_dns='1'
openclash.config.enable_custom_domain_dns_server='0'
openclash.config.enable_geoip_dat='1'
openclash.config.enable_meta_sniffer='1'
openclash.config.enable_meta_sniffer_custom='1'
openclash.config.enable_meta_sniffer_pure_ip='1'
openclash.config.enable_redirect_dns='1'
openclash.config.enable_respect_rules='1'
openclash.config.enable_rule_proxy='0'
openclash.config.enable_tcp_concurrent='1'
openclash.config.enable_unified_delay='1'
openclash.config.fakeip_range='0'
openclash.config.filter_aaaa_dns='0'
openclash.config.find_process_mode='0'
openclash.config.geo_auto_update='1'
openclash.config.geo_custom_url='https://testingcf.jsdelivr.net/gh/alecthw/mmdb_china_ip_list@release/lite/Country.mmdb'
openclash.config.geo_update_day_time='0'
openclash.config.geo_update_week_time='1'
openclash.config.geoasn_auto_update='1'
openclash.config.geoasn_custom_url='https://testingcf.jsdelivr.net/gh/xishang0128/geoip@release/GeoLite2-ASN.mmdb'
openclash.config.geoasn_update_day_time='0'
openclash.config.geoasn_update_week_time='1'
openclash.config.geodata_loader='0'
openclash.config.geoip_auto_update='1'
openclash.config.geoip_custom_url='https://testingcf.jsdelivr.net/gh/Loyalsoldier/v2ray-rules-dat@release/geoip.dat'
openclash.config.geoip_update_day_time='0'
openclash.config.geoip_update_week_time='1'
openclash.config.geosite_auto_update='1'
openclash.config.geosite_custom_url='https://testingcf.jsdelivr.net/gh/Loyalsoldier/v2ray-rules-dat@release/geosite.dat'
openclash.config.geosite_update_day_time='0'
openclash.config.geosite_update_week_time='1'
openclash.config.github_address_mod='https://testingcf.jsdelivr.net/'
openclash.config.global_client_fingerprint='0'
openclash.config.global_ua='0'
openclash.config.http_port='7890'
openclash.config.interface_name='0'
openclash.config.intranet_allowed='1'
openclash.config.ipv6_dns='0'
openclash.config.ipv6_enable='0'
openclash.config.lan_interface_name='0'
openclash.config.lgbm_auto_update='0'
openclash.config.log_level='0'
openclash.config.log_size='1024'
openclash.config.mixed_port='7893'
openclash.config.operation_mode='fake-ip'
openclash.config.other_rule_auto_update='0'
openclash.config.proxy_mode='rule'
openclash.config.proxy_port='7892'
openclash.config.redirect_dns='1'
openclash.config.release_branch='master'
openclash.config.router_self_proxy='1'
openclash.config.rule_source='0'
openclash.config.servers_if_update='0'
openclash.config.servers_update='0'
openclash.config.skip_proxy_address='0'
openclash.config.small_flash_memory='0'
openclash.config.smart_collect='0'
openclash.config.smart_enable='0'
openclash.config.smart_enable_lgbm='0'
openclash.config.smart_prefer_asn='0'
openclash.config.smart_tolerance='0'
openclash.config.socks_port='7891'
openclash.config.stack_type='system'
openclash.config.store_fakeip='1'
openclash.config.stream_auto_select='1'
openclash.config.stream_auto_select_bilibili='1'
openclash.config.stream_auto_select_claude='0'
openclash.config.stream_auto_select_close_con='0'
openclash.config.stream_auto_select_dazn='0'
openclash.config.stream_auto_select_discovery_plus='0'
openclash.config.stream_auto_select_disney='1'
openclash.config.stream_auto_select_expand_group='0'
openclash.config.stream_auto_select_gemini='0'
openclash.config.stream_auto_select_google_not_cn='0'
openclash.config.stream_auto_select_group_key_disney='Disney|迪士尼'
openclash.config.stream_auto_select_group_key_hbo_max='HBO|HBO Max'
openclash.config.stream_auto_select_group_key_netflix='Netflix|奈飞'
openclash.config.stream_auto_select_hbo_max='1'
openclash.config.stream_auto_select_interval='10'
openclash.config.stream_auto_select_logic='urltest'
openclash.config.stream_auto_select_netflix='1'
openclash.config.stream_auto_select_openai='0'
openclash.config.stream_auto_select_paramount_plus='0'
openclash.config.stream_auto_select_prime_video='0'
openclash.config.stream_auto_select_region_key_bilibili='CN'
openclash.config.stream_auto_select_tvb_anywhere='0'
openclash.config.stream_auto_select_ytb='1'
openclash.config.tolerance='0'
openclash.config.tproxy_port='7895'
openclash.config.update='0'
openclash.config.urltest_address_mod='0'
openclash.config.urltest_interval_mod='0'
openclash.config.yacd_type='Meta'
```

## 7. 不应提交到公开仓库的内容

- `/etc/openclash/config/*.yaml` 原始订阅配置
- `/etc/openclash/proxy_provider/*`
- `IPRoyal-Local.conf` 的服务器、端口、用户名、密码
- 订阅 URL / Token / UUID / Password / Secret
- Dashboard 密码或认证信息
- OpenWrt / CatWrt 整机备份包

## 8. 恢复后的最低验收

1. OpenClash 正常启动，无 `Parse config error` / `not found rule-set`。
2. 国内站点命中 `DIRECT`。
3. Google / GitHub / ChatGPT 命中 `美国`。
4. 微信语音和企业微信语音双向正常。
5. 京东商品图片连续加载正常，无白屏/明显卡顿。
6. 米家设备在线可用。
7. TikTok（如启用本地 IPRoyal 模块）命中 `TikTok-ISP`。

## 9. 维护原则

- 以最新实机可复现结果为准，不因偶发 `i/o timeout` 大改规则/DNS/TUN。
- 新增普通“必须直连”域名优先维护 `rules/manual-direct.yaml`。
- 不把本地 IPRoyal 凭证提交到 GitHub。
- 修改关键运行模式、DNS、TUN、嗅探或 Fake-IP 设置后，必须重新完成第 8 节验收。
