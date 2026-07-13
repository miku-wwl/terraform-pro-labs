# Lab 28：Provider 版本约束

## 任务

这个 Lab 只练习版本约束，不创建任何资源。

根模块必须支持 Terraform `1.6` 起的 1.x 版本；AWS provider 只能使用 6.x，但要排除有问题的 `6.2.0`。在 `starter/examples/minimum` 中，AWS provider 需要接受 `6.0.0` 及以上版本；在 `starter/examples/exact` 中，则只能接受 `6.54.0`。

完成后，你会分别用到 `~>`、`>=`、`<`、`=`、`!=` 五种约束运算符。

## 约束

- provider source 必须保持为 `hashicorp/aws`。
- 不要添加资源、provider 配置或环境检查。
- 只能编辑以下文件：
  - `starter/versions.tf`
  - `starter/examples/minimum/versions.tf`
  - `starter/examples/exact/versions.tf`
