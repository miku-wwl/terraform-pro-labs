# Lab 08：从 IAM Role 到 EC2 的依赖链

## 场景

应用实例需要 EC2 信任策略、托管权限策略、role attachment、instance profile，以及 EC2 对该 profile 的引用。starter 创建了所有对象，但破坏了这条链中的两个连接。

## 考查技能

- IAM 信任策略和权限策略结构
- 将托管策略附加到 role
- 连接 IAM role 与 instance profile
- 集成 EC2 instance profile
- 使用 AWS mock provider 测试依赖图

## 难度与预计时间

- 难度：中等
- 预计时间：20 分钟

## 执行模式

`aws-mock`。配置使用确定性的仅计划 AMI ID，绝不会查询 AWS，也不会向 AWS apply。

## 是否需要云凭据

不需要。

## 成本风险

无；不会创建真实的 EC2 或 IAM 对象。

## 初始状态

信任文档和权限文档是确定性的。策略 attachment 指向另一个 role 名称，EC2 实例也没有引用 instance profile。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## 任务

1. 保留 EC2 信任关系和范围受限的 S3 权限文档。
2. 将托管策略附加到已声明的应用 role。
3. 保留 role 到 instance profile 的引用。
4. 将 EC2 实例连接到该 instance profile。
5. 保持所有名称均由 `name_prefix` 驱动。

## 约束

- 不得引入 AMI、VPC、subnet 或 account data lookup。
- 不得使用重复硬编码的名称替代引用。
- 不得添加凭据或执行真实 apply。
- 不得编辑受保护的测试。

## 预期初始失败

`python tools/labctl.py check 08` 会报告 `EXPECTED_IAM_EC2_CHAIN_INCOMPLETE`，因为 attachment 和 instance-profile 连接没有形成完整的依赖链。

## 验证命令

```text
python tools/labctl.py check 08
python tools/labctl.py status 08
```

## 成功标准

- 精确的单语句 `Allow` 信任策略允许 `ec2.amazonaws.com` 调用 `sts:AssumeRole`。
- 精确的单语句 `Allow` 托管策略包含两个必需的 S3 action 和精确的 bucket/object ARN 范围。
- 源代码检查证明 policy attachment、role、profile 和 EC2 使用直接 Terraform 引用，而不是重复的相等字符串。
- 替代前缀会传递到每个命名对象。
- 不使用 AWS 凭据、lookup 或 API 调用。

## 重置说明

```text
python tools/labctl.py reset 08
```

## 有限提示

- instance profile 是连接 IAM role 与 EC2 的桥梁。
- 引用上游资源属性也会建立依赖图关系。
