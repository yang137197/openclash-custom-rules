# {profileId} v{version}

状态：candidate / stable

## 适用需求

说明此方案解决什么需求，以及不适用的需求。

## 规则与流量路径

按优先级列出关键分流、出口和失败时行为。

## OpenClash 环境与设置

- OpenClash 版本/构建：
- Mihomo 版本/构建：
- OpenWrt 版本/设备架构：
- 设置建议及操作路径：`profiles/{profileId}/versions/v{version}/SETUP.md`
- 验收记录：`profiles/{profileId}/versions/v{version}/ENVIRONMENT.json`

## 部署

- 本版本固定覆写链接：`https://raw.githubusercontent.com/yang137197/openclash-custom-rules/{profileId}-v{version}/profiles/{profileId}/versions/v{version}/openclash-overwrite.conf`
- 需求合同：`profiles/{profileId}/versions/v{version}/REQUIREMENTS.md`
- 本地凭据占位模板（如适用）：
- 本地模板唯一的 Release 附件下载链接（需要本地模块时必填；否则注明“不适用”）：
- 附件 SHA-256：
- 在 Release 正文中说明服务商字段对应关系、填写格式、必须保留的节点/链路字段，并提供明确标为虚构的填写示例：
- 真实配置的安全保存位置及不得公开的内容：
- 模块 SHA-256：

> 需要本地模块的方案只上传一个与标签文件一致的占位模板作为 Release 附件；不要另附注释模板或填写指南。GitHub 自动生成的 `Source code (zip)` / `Source code (tar.gz)` 是标签源码快照，不能代替模板附件。不得在模板、Release 或公开仓库中加入真实凭据。

## 验收与限制

分别说明静态校验、实机测试、用户确认和未验证事项；不得把候选标作 stable。

## 更新内容

列出本版本相对同一方案前一版本的具体变化。
