# v1.8.4 验证记录

状态：candidate。GitHub CI结果以本候选提交对应工作流为准；本文件不预填成功结果。本版未部署到CatWrt，targetRouterTested=false、formalAcceptance=false。

验证内容：固定OpenClash v0.48.002合并实现；增量/完整参考合同一致和幂等；只允许TikTok五项检测字段；完整规则/直连原序/ISP全字段/DNS保护；私有原字节备份/回退副本；Ruby YAML只读工具；严格四档Lua和HTTP边界；真实Mihomo v1.19.34回环节点选择与四档故障；新增无需delay/healthcheck API触发的TikTok定时历史更新、手选保持和内部节点可见性。

真实核心测试仍是合成HTTP回环节点，时序缩短为1秒/300ms，Lua原生模块为CI替代；不代替目标的5秒/60秒、真实SOCKS5链路、CatWrt原生库和前端展示。旧v1.8.3的实机业务结果只作前版证据，不能使本版自动验收。

本版控制器/监督脚本/本地占位模板/官方合并桥均沿用前版原字节。前版测量复核变化切REJECT的机制保留，未声称无中断、长期稳定或服务安装成功。

CI入口：scripts/verify_liangxinyun_v184.py、scripts/test_liangxinyun_v184.lua、scripts/verify_liangxinyun_v184_http.py、scripts/check_liangxinyun_v184.py、scripts/test_liangxinyun_v184_runtime_scope.py，以及仓库完整单测/版本/隐私/不可变快照校验。报告存为GitHub Actions artifact。
