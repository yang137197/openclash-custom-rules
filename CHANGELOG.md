# 项目更新日志

## 2026-09-08：“电脑远程开机卡控制”微信小程序直连

- 根据实机日志，将误入 `MATCH → 美国` 的 `api.rmtsw.siwiot.com` 识别为小程序业务接口。
- 四个独立 DNS 查询源一致返回中国大陆阿里云 IP；新增 `DOMAIN-SUFFIX,siwiot.com` 到 `Manual-Direct`。
- 不写死当前 IP，确保服务端地址变化后仍按域名直连。
- 未修改主规则、DNS、OneDrive、TikTok 或其他策略组。

## 2026-09-08：TikTok / IPRoyal 实机验收

- OpenClash 实机日志确认 TikTok 命中 `TikTok-IPRoyal → TikTok-ISP[IPRoyal-US-ISP]`。
- CatWrt 对 IPRoyal SOCKS5 服务端口连续 5 次 TCP 建连成功，用户实测 TikTok 可正常联网。
- 将当天早些时候的 `i/o timeout` 定性为已恢复的短暂建连波动；当前不增加链式代理，也不修改远程分流规则。
- 真实 IPRoyal 端点及凭证仍只保存在 OpenClash 本地模块，未写入仓库。

## 2026-09-07：TikTok 固定使用本地 IPRoyal ISP

- 新增 `TikTok-ISP` 手选组，只收集名称严格等于 `IPRoyal-US-ISP` 的本地 SOCKS5 节点。
- `TikTok-ISP` 无节点时使用 `REJECT` 失败关闭，不回落到机场美国节点，避免 TikTok 账号混用出口。
- `美国` 组显式排除 `IPRoyal-US-ISP`，普通 Google、GitHub、ChatGPT 等海外流量继续使用机场美国节点。
- 新增 `TikTok-IPRoyal` 远程规则集，并同时保留 `GEOSITE,tiktok`，两者都位于 `Manual-Direct` 和中国大陆规则之前。
- TikTok 域名的 Cloudflare/Google DoH 查询也通过 `TikTok-ISP`，使 DNS 与业务连接保持同一 IPRoyal 出口。
- README 增加本地保密模块模板、双模块叠加边界、全设备适用范围和域名级分流限制。
- IPRoyal 服务器、端口、用户名和密码不进入 GitHub；用户仅在 OpenClash 本地模块中维护。

## 2026-09-05：通用多人多设备重构

- 将整体策略收敛为：局域网/私有地址直连、手工规则直连、中国大陆域名/IP直连、其余全部进入 `美国`。
- `美国` 从 `url-test` 改为 `select`，由用户手动选择美国节点，不再自动切换出口。
- 非美国节点仍保留在订阅底层，但不进入任何策略组，也不会被规则使用。
- 将手工直连规则集统一命名为 `Manual-Direct`，对应 `rules/manual-direct.yaml`。
- 删除会整体覆盖 `rule-providers` 的 `[Overwrite]` Ruby 逻辑，避免删除 OpenClash 自动生成的 `oc-cn-domain` 等内部 provider。
- 保留 Fake-IP，并通过 `fake-ip-filter+` 追加局域网、本地域名和自建回流域名，降低内网/NAT 回流异常概率。
- DNS 按大陆/私有域名与其他域名分流；国外 DNS 连接通过 `美国` 策略组。
- 规则不再绑定设备 IP、手机型号、MAC、人员或国家专用设备，便于多人多设备复用。
- README 与 `manual-direct.yaml` 增加完整维护说明、语法示例、错误写法和验收方法。

## 2026-09-05：单一美国策略组（已被本次重构替代）

- 曾将 `美国` 改为自动测速组。
- 曾增加 `[Overwrite]` 兼容覆写并整体替换 `rule-providers`。
- 该方式会删除 OpenClash 自动生成的 provider，最终触发 `not found rule-set: oc-cn-domain`，已在本次重构中移除。

## 2026-09-04：统一美国出口

- 删除按设备、地区和应用拆分的策略组及规则提供者。
- 保留局域网/私有地址、手工直连和中国大陆域名/IP直连。
- 其余所有流量统一命中 `美国` 策略组。
