# v1.8.4 验证记录

状态：candidate。功能验证已在下列提交完成；最终工作流状态以当前提交检查为准。本版未部署到CatWrt，targetRouterTested=false、formalAcceptance=false。

验证内容：固定OpenClash v0.48.002合并实现；增量/完整参考合同一致和幂等；只允许TikTok五项检测字段；完整规则/直连原序/ISP全字段/DNS保护；私有原字节备份/回退副本；Ruby YAML只读工具；严格四档Lua和HTTP边界；真实Mihomo v1.19.34回环节点选择与四档故障；新增无需delay/healthcheck API触发的TikTok定时历史更新、手选保持和内部节点可见性。

真实核心测试仍是合成HTTP回环节点，时序缩短为1秒/300ms，Lua原生模块为CI替代；不代替目标的5秒/60秒、真实SOCKS5链路、CatWrt原生库和前端展示。旧v1.8.3的实机业务结果只作前版证据，不能使本版自动验收。

本版控制器/监督脚本/本地占位模板/官方合并桥均沿用前版原字节。前版测量复核变化切REJECT的机制保留，未声称无中断、长期稳定或服务安装成功。

CI入口：scripts/verify_liangxinyun_v184.py、scripts/test_liangxinyun_v184.lua、scripts/verify_liangxinyun_v184_http.py、scripts/check_liangxinyun_v184.py、scripts/test_liangxinyun_v184_runtime_scope.py，以及仓库完整单测/版本/隐私/不可变快照校验。报告存为GitHub Actions artifact。

## 已取得的合成功能验证

2026-11-25，[CI #96](https://github.com/yang137197/openclash-custom-rules/actions/runs/45532140984)（提交a35ed57920ac6208ed74771bcffe22428ad27d56）完成51项官方合并/范围/回退场景、600项Lua断言、21项HTTP/CLI场景、15项真实核心回环用例、80项仓库单测及版本/隐私/历史保护检查。真实核心用例包括无测速API触发的定时历史刷新、TikTok手选保持和内部节点可见性。

该次总工作流仅在最后的文档EOF空行检查失败，后续提交只移除该空行并记录本证据；运行模块字节未因此修改。最终完整工作流仍以当前提交检查为准，不能把这些合成结果当作目标实机验收。
