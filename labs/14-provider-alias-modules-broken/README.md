# Lab 14：将 Provider 别名传入子模块

## 任务

根模块配置了默认 AWS provider 和 `aws.secondary` 别名。子模块同时需要这两套 provider 配置来读取两个区域。

在根模块调用子模块时，通过 `providers` map 将默认 provider 和 `aws.secondary` 分别传给子模块中同名的 provider 配置。

Provider 配置应继续保留在根模块中，不要在子模块中新增 provider block。



## 约束

- 不要修改子模块。
- 不要删除 `configuration_aliases` 或子模块中 `aws.secondary` 的选择。
- 不要复制子模块来绕过 provider 映射。
- 不要添加凭据，也不要执行真实 AWS 查询。
- 只能编辑 `starter/main.tf`。
