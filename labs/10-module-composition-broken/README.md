# Lab 10：根模块与子模块组合

## 场景

一个应用栈包含三个具有稳定契约的子模块：naming 生成前缀，identity 生成 profile 名称，compute 使用这两个值。修复根模块，使值通过显式输入和输出跨越模块边界。

## 考查技能

- 从根模块调用子模块
- 将根模块输入传递给模块
- 将一个子模块的输出连接到另一个子模块
- 在根模块中公开选定的子模块输出
- 理解基于引用形成的依赖边

## 难度与预计时间

- 难度：中等
- 预计时间：20 分钟

## 执行模式

仅使用内置资源在本地进行 Terraform 模块组合。

## 是否需要云凭据

不需要。模块使用 `terraform_data` 建模契约，不会访问任何服务。

## 成本风险

无。

## 初始状态

三个子模块均已存在并受到保护。根模块会调用它们，但其中一个输入和一个根输出绕过了预期的模块连接关系。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `starter/modules/`
- `tests/public.tftest.hcl`
- `scripts/verify_tests.py`
- `lab.yaml`

## 任务

1. 将根模块的 application 和 environment 值传递给 naming 模块。
2. 将 naming 的结果传递给 identity 模块。
3. 将 naming 结果和 identity profile 结果一并传递给 compute。
4. 从根模块公开 compute instance 引用和 identity profile 名称。

## 约束

- 不要在根模块中重复子模块的命名公式。
- 保留所有子模块接口，并使用引用建立依赖关系。
- 不要添加 provider 或云资源。
- 保持根输出的键和名称不变。

## 预期初始失败

`python tools/labctl.py check 10` 会在测试阶段报告 `EXPECTED_MODULE_COMPOSITION_INCOMPLETE`，因为 starter 绕过了必需的子模块输出。

## 验证命令

```bash
python tools/labctl.py check 10
python tools/labctl.py status 10
```

## 成功标准

- 默认输入生成前缀 `payments-dev`、profile `payments-dev-profile` 和 compute 引用 `payments-dev::payments-dev-profile`。
- 有效的替代输入必须流经每个子模块，不能使用硬编码的默认值。
- 不受支持的 environment 必须被受保护的 naming 模块契约拒绝。
- 对 plan 配置的检查必须证明 naming、identity 和 compute 模块参数使用了必需的上游引用。
- 根输出必须直接公开 naming、identity 和 compute 模块的输出，而不是重新构造内容相同的字符串。

## 重置说明

```bash
python tools/labctl.py reset 10
```

## 有限提示

- 沿着输出从生产者追踪到消费者，不要重新创建相同的字符串。
- 用作模块参数的引用也会创建依赖边。
