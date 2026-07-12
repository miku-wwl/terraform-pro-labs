# Lab 14：将带 alias 的 provider 传入子模块

## 任务

1. 检查子模块声明的 provider alias 及其 provider 用法。
2. 修正根模块调用，使每个子模块 provider 名称都收到与之匹配的根模块配置。
3. 将 provider 配置保留在根模块中，不要向子模块添加 provider block。
4. 使用两个可区分的 mock provider 结果验证映射。



## 约束

- 不要修改受保护的子模块。
- 不要删除 `configuration_aliases` 或 secondary data source 的 provider 选择。
- 不要通过复制子模块来规避 provider 映射。
- 不要使用凭据或真实 AWS data lookup。



## 可编辑文件

- `starter/main.tf`
