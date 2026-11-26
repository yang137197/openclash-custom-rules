# tiktok-router-dual-subscription-jp

当前版本 **v1.0.0 / candidate**，等待用户实机测试。独立的新需求方案；不复用已移除的控制器，不替换原 `tiktok-router-loongproxy-jp-us v1.0.7` 正式入口。

- [需求合同](versions/v1.0.0/REQUIREMENTS.md)
- [部署、验收和回退](versions/v1.0.0/SETUP.md)
- [环境记录](versions/v1.0.0/ENVIRONMENT.json)
- [本地验证及局限](versions/v1.0.0/VALIDATION.md)
- [完整云覆写](versions/v1.0.0/openclash-overwrite.conf)
- [路由器本地占位模板](versions/v1.0.0/local-tiktok-proxy.conf)

四个显式组为 `TikTok首跳`、`Tiktok美国出口测速`、`良心云-日本专线流媒体`、`ikuuu-默认代理`。保留内核 GLOBAL，不为它配置定时检测。

iKuuu 日本节点提供自动低延迟首跳和默认代理；Loongproxy 美国出口仅供 TikTok；良心云日本专线/高速按编号顺序故障回退，用于指定流媒体和下载。不能同时启用新旧两份完整方案。

完整云覆写通过远程模块使用；两条真实订阅地址和 ISP 凭据仅填入本地模块，禁止提交到 GitHub。手动直连唯一源仍是 `rules/manual-direct.yaml`；候选文件为生成时的完整快照，正式发布后才建立本方案独立滚动入口及日常源同步。

原生检测不是带宽测试或流媒体解锁证明。桌面合成网络验证不能替代 CatWrt 实机验收；正式发布须取得对应版本调试日志及用户业务确认。
