# Lab 28：Provider 版本约束语义

## 场景

某团队对 Terraform 和 AWS provider 的版本要求过于宽泛。请定义三种有明确意图的策略：排除一个版本的有界生产范围、只有最低版本的模块范围，以及用于精确复现的固定版本，并证明每种策略会接受哪些版本。

## 考查技能

- `required_version` 与 `required_providers`
- 悲观约束 `~>` 的边界
- 显式运行时 `>=`/`<` 边界、精确 `=` 和排除 `!=` 的语义
- 根模块与可复用模块的约束意图
- 超越 `terraform validate` 的候选版本求值

## 难度与预计时间

- 难度：中等
- 预计时间：20 分钟

## 执行模式

本地初始化、验证和确定性语义评分。

## 是否需要云凭据

不需要。安装 provider 时可能会访问 registry 或使用现有缓存，但配置中没有 provider 配置或 API 调用。

## 成本风险

无。

## 初始状态

运行时和 provider 的版本范围过于宽泛，而精确版本示例固定到了错误版本。此前无关的环境验证练习已被移除。

## 允许编辑的文件

- `starter/versions.tf`
- `starter/examples/minimum/versions.tf`
- `starter/examples/exact/versions.tf`

## 禁止编辑的文件

- `fixtures/`
- `scripts/`
- `lab.yaml`

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

## 预期初始失败

`python tools/labctl.py check 28` 会报告 `EXPECTED_CONSTRAINT_SEMANTICS_INCOMPLETE`，因为不受支持的主版本仍被允许，而且精确版本示例指向了错误版本。

## 验证命令

```text
python tools/labctl.py check 28
python tools/labctl.py status 28
```

## 成功标准

- 允许 Terraform 1.6 到未来较高的 1.x 候选版本，同时拒绝较早的 1.x、与 1.6 相邻但更早的版本、2.0.x 及更高主版本。
- 有界根模块策略允许当前和未来较高的安全 6.x 候选版本，拒绝 5.x/7.x，并且只排除 6.2.0。
- 最低版本策略允许 6.0.0 和更高主版本。
- 精确版本策略只允许 6.54.0。
- 每种策略都使用预期的运算符，语义评分覆盖全部候选版本。

## 重置说明

```text
python tools/labctl.py reset 28
```

## 有限提示

- 由两个版本分量组成的悲观约束与三个版本分量组成的悲观约束具有不同的上界。
- 多个以逗号分隔的约束取交集。
