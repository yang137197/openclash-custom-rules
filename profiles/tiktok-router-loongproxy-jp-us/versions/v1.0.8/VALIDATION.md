# v1.0.8 验证范围

状态：stable。代理运行文件保持已验收字节；用户已确认验收标准通过并提供本轮日志。桌面验证没有连接用户路由器、真实机场或Loongproxy，没有安装服务或修改系统代理。

本地 Windows 使用官方 Mihomo v1.19.34 amd64 ZIP，下载SHA-256为 `cd6738d4648cc1a5f48049a1343b697ab510889d648f045c5c780fc1ab443a79`；Ruby使用官方RubyInstaller便携包。通过官方 OpenClash `e553e82e01c697aefbe1555261a503f425e00ccd` 的 `YAML.rb` 进行实际合并，源文件哈希 `1249abf411e1df9e8fe542fb3584f34a27e6e3a587942e5d9f759a32b1bd8261`。

本次发布检查：55项Python测试及36项原生合成网络场景通过；代码/包验证与实机用户确认分开记录。

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

## 实机记录与用户验收

本轮日志生成于2026-11-26 15:28:14：OpenClash 0.48.002、实际运行alpha-gbc76c13、OpenWrt 24.10.2 r7492-3fda82b52、QEMU x86_64、内核6.12.38。用户称其CatWrt.v25.8.amd64 / LEDE R25.7.7。模式fake-ip/rule；禁用QUIC停用，与原建议不同但本次保留。

四个组的定义与候选一致；37条路由列表中仅9条IP规则受日志脱敏影响，其余完全一致；148条直连列表内容、顺序及重复项与唯一源一致。日志隐藏proxies/proxy-providers，模块列表段为空；用户另附截图补证云在本地上方且两者启用。不能由被脱敏的IP字符串重建运行文件。

用户明确表示“达到验收标准”，并授权正式发布。TikTok播放、平台访问、顺序切换和回退的业务通过来自该确认；不声称日志采样单独覆盖所有场景。用户实际采用57217e8旧候选地址，其云/本地模板与迁移后的v1.0.8已逐字节核验相同，因此测试证据适用于本次发布内容。原始日志及私有凭据不进入Git/GitHub。

桌面原生v1.19.34合成网络结果与实际alpha-gbc76c13日志/用户验收分别记录，详见VALIDATION.json与ENVIRONMENT.json。
