# Lab 10：组合多个子模块

## 任务

根模块负责连接三个子模块：`naming`、`identity` 和 `compute`。

将根模块的 `application`、`environment` 传给 `naming`。`naming` 生成的名称前缀需要传给 `identity`；`compute` 同时需要名称前缀和 `identity` 生成的 Instance Profile 名称。

通过根模块的 `stack` 输出公开 compute 的实例引用和 Instance Profile 名称。



## 约束

- 根模块只负责传递输入、输出和依赖关系，不要重复子模块中的命名逻辑。
- 保留所有子模块的变量和输出接口。
- 不要添加 provider 或云资源。
- 保持 `stack` 输出的键和名称不变。
- 只能编辑 `starter/main.tf`。
