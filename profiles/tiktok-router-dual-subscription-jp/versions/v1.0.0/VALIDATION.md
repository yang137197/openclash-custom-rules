# v1.0.0 验证范围

状态：candidate。没有连接用户路由器、真实机场或Loongproxy；没有安装服务或修改系统代理。

本地 Windows 使用官方 Mihomo v1.19.34 amd64 ZIP，下载SHA-256为 `cd6738d4648cc1a5f48049a1343b697ab510889d648f045c5c780fc1ab443a79`；Ruby使用官方RubyInstaller便携包。通过官方 OpenClash `e553e82e01c697aefbe1555261a503f425e00ccd` 的 `YAML.rb` 进行实际合并，源文件哈希 `1249abf411e1df9e8fe542fb3584f34a27e6e3a587942e5d9f759a32b1bd8261`。

## 可重现检查

```text
python -m unittest discover -s scripts -p "test_*.py"
python scripts/validate_repository.py --base-ref origin/main
git diff --check
```

CI另外下载哈希固定的Linux v1.19.34并执行 `scripts/verify_dual_subscription_native.py`。脚本要求Ruby、已校验的官方YAML.rb及核心路径；所有测试监听127.0.0.1，使用合成HTTP首跳、SOCKS5 ISP、DNS、GeoSite/GeoIP、服务规则列表和HTTP目标。完整配置先经官方Ruby合并，再进入实际Mihomo解析和连接流程；不是自写选择算法的模拟。

覆盖：四组替换及基础字段保留、完整手动直连源逐项同序、缺失DNS父块的合并、订阅乱序、新增Z12/专线05/高速06、两供应商隔离、ISP组成员限定、专线A故障到B、全部专线失败到高速、B及A恢复返回、iKuuu最低延迟选择、各服务/默认/下载/国内/手动直连的实际规则命中和合成完整ISP链。

静态测试还拒绝：混入错误供应商、ISP添加普通机场回退、良心云改最低延迟、直连列表删除或重排、删除TikTok紧邻REJECT、新分类截走直连、开启懒检测。合法订阅示例与新编号边界有正反例。

平台分类已在MetaCubeX官方规则产物目录核对，Apple TV+实际分类名是 `apple-tvplus`。本地合成测试验证路由结构，不代表真实规则集覆盖所有域名；运行时规则会随上游更新。订阅拉取可达性、TLS、SS协议、平台解锁和带宽均未由这些夹具验证。

## 实机待验

用户报告环境为OpenClash v0.48.002、alpha-gbc76c13、CatWrt.v25.8.amd64 / LEDE R25.7.7、内核6.12.38。桌面v1.19.34不是这台设备的二进制；审阅bc76c13源码不等于该设备已实测兼容。需要新候选日志、实际节点与模块顺序、TikTok播放、真实分类命中、自动切换及完整回退结果。

本候选不宣称正式验收通过。通过上述静态与CI后交付用户测试；ENVIRONMENT.json的runtimeAcceptance仍为not-run。
