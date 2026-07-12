# Lab 28：Provider 版本约束语义

## 任务

1. 将 Terraform CLI 兼容范围限制为从 1.6 开始、受支持的 1.x 系列。
2. 将根模块的 AWS provider 限制为 6.x 系列，同时排除已知存在问题的 6.2.0。
3. 让可复用的最低版本示例接受 AWS provider 6.0.0 及以上版本。
4. 让复现示例只接受 AWS provider 6.54.0。
5. 使用并理解全部五种目标运算符：`~>`、`>=`、`<`、`=` 和 `!=`。



## 约束

- 所有 provider 的 source 均保持为 `hashicorp/aws`。
- 不要添加资源、provider 配置或环境验证。
- 不要编辑受保护的候选版本矩阵或评分器。
- 只要行为和运算符覆盖符合要求，可以使用等价的逗号分隔约束。



## 可编辑文件

- `starter/versions.tf`
- `starter/examples/minimum/versions.tf`
- `starter/examples/exact/versions.tf`
