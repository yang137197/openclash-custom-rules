# v1.8.3 验证边界

最终CI结果以本PR最新提交的 **Validate repository** 运行及其v1.8.3报告附件为准。

已完成的功能验证：提交799ba333的[运行#89](https://github.com/yang137197/openclash-custom-rules/actions/runs/45360249651)中，官方合并／范围／缓存／回退48场景、600项Lua断言、21个HTTP/CLI场景、13个真实核心出口场景、67项Python单测及仓库校验通过；该次工作流最终因SETUP.md末尾多一空行失败，后续已修正。缓存差异夹具也改为独立合成148条，不依赖长期可变的滚动源。修正后的完整工作流结果另见最新提交，不把旧工作流写成整体成功。助手未在用户电脑执行测试，未连接路由器；原生服务、面板显示与本候选实机验收均待用户后续验证。

CI包含：固定官方YAML.overwrite合并、缓存148/运行141不一致拒绝、范围越界与内部组冲突拒绝、幂等、原直连原序、备份/回退原字节和漂移拒绝；实际Lua5.1完整策略/状态机与HTTP边界；下载并校验官方v1.19.34核心进行回环新连接出口测试，覆盖部分失败留档、全部失败逐档降级、恢复、订阅增删、全失败、单实例及正常停止，并逐次核对URLTest唯一内部成员与TikTok手选保持。

核心压缩包固定为官方v1.19.34 linux-amd64，SHA-256：223fab877e5795ce780ba39902e5f0b1113c1256ae244a7160f1165e017e9ccc。该核心不是设备alpha-gbc76c13；已静态核对设备对应提交bc76c1398c6e70089367a30169d0df7c7f77c42d的URLTest实现，单一成员没有其他候选出口，但不据此宣称目标实测通过。回环测试使用1秒检测/300ms超时及替代LuCI/nixio，不验证生产60秒/5秒或机场长期可靠性。

依据：
- [官方代理组](https://wiki.metacubex.one/config/proxy-groups/)与[URLTest](https://wiki.metacubex.one/config/proxy-groups/url-test/)
- [目标核心URLTest源码](https://github.com/MetaCubeX/mihomo/blob/bc76c1398c6e70089367a30169d0df7c7f77c42d/adapter/outboundgroup/urltest.go)
- [MetaCubeXD类型翻译](https://github.com/MetaCubeX/metacubexd/blob/main/packages/ui/i18n/locales/zh.json)：Selector为手动选择，URLTest为自动选择。实际使用的面板版本未知，必须用户核验。
- [OpenClash固定合并源码](https://github.com/vernesong/OpenClash/blob/e553e82e01c697aefbe1555261a503f425e00ccd/luci-app-openclash/root/usr/share/openclash/YAML.rb)

原141/148差异已由用户回传定位并修复；不把这些既有回传写作v1.8.3验收。
