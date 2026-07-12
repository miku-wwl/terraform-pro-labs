# Lab 31：S3 Backend 部分配置

## 场景

Northstar 在开发、测试和生产环境中使用同一个 Terraform 根模块。backend 类型和组织级安全控制保持静态，而状态 bucket、对象 key 和 AWS 区域则在每个环境执行 `terraform init` 时选择。

starter 当前将一个环境专属设置放在静态 backend 块中。请正确拆分这些设置，同时不要初始化或连接真实的 S3 backend。

## 考查技能

- 声明采用部分配置的静态 backend 块
- 区分 backend 配置与普通 Terraform 输入变量
- 在初始化时提供环境专属的 backend 设置
- 识别 backend 块中的表达式和不当硬编码
- 安全重置 backend 初始化元数据

## 难度与预计时间

- 难度：中等
- 预计时间：20 分钟

## 执行模式

- 默认模式：本地格式检查、`init -backend=false`、验证、静态检查，以及在临时的无 backend 副本中对普通配置表达式执行 plan
- 可选模式：经明确授权后初始化真实 S3 backend

## 是否需要云凭据

默认验证路径不需要也不会读取任何凭据。可选的真实 backend 路径需要单独配置 AWS 身份验证，并使用学习者自己拥有的 bucket。

## 成本风险

- 默认路径：无
- 可选真实 S3 backend：存在少量存储和请求成本；不属于验证流程

## 初始状态

- `starter/main.tf` 包含一个有效的 S3 backend 块，其中有共享的静态安全设置，以及一个被故意放错位置、应在初始化时提供的设置。
- `backend-dev.hcl.example`、`backend-test.hcl.example` 和 `backend-prod.hcl.example` 包含安全占位值，不含凭据。
- `starter/variables.tf` 用于说明 `var.environment` 是普通模块输入，而不是 backend 输入。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/variables.tf`
- `starter/versions.tf`
- `backend-dev.hcl.example`
- `backend-test.hcl.example`
- `backend-prod.hcl.example`
- `tests/`
- `scripts/verify_backend.py`
- `lab.yaml`
- `.gitignore`

## 任务

1. 将所有 backend 共用的安全行为保留在静态 `backend "s3"` 块中。
2. 从该块中移除应在初始化时提供的环境专属设置。
3. 不要在 backend 块中引用 `var`、`local`、`module`、data source、resource 或插值语法。
4. 确认每个示例文件都提供了初始化时所需的环境专属 backend 值。
5. 让普通 `environment` 变量只供根模块使用。

## 约束

- 默认练习不要执行真实的 S3 backend 初始化。
- 不要在示例中放置 access key、secret key、令牌、profile、角色凭据或真实 bucket 名称。
- 不要让 backend 值依赖普通输入变量。
- 不要将 S3 backend 设置移动到 provider 配置或 `.tfvars` 文件。

## 预期初始失败

从仓库根目录运行时，未经修改的 starter 会通过格式检查、离线初始化和 Terraform 验证，随后在静态行为阶段以 `EXPECTED_PARTIAL_BACKEND_INCOMPLETE` 失败，因为 backend 块中仍硬编码了一个应在初始化时提供的参数。

## 验证命令

在仓库根目录运行完整的安全门禁：

```bash
python tools/labctl.py check 31
```

manifest 会执行以下命令，且不会连接 S3：

```bash
terraform -chdir=labs/31-partial-backend-config-broken/starter fmt -check -recursive
terraform -chdir=labs/31-partial-backend-config-broken/starter init -backend=false -input=false
terraform -chdir=labs/31-partial-backend-config-broken/starter validate
python labs/31-partial-backend-config-broken/scripts/verify_backend.py --starter labs/31-partial-backend-config-broken/starter --examples labs/31-partial-backend-config-broken
```

可选的真实 backend 演示：仅在创建被忽略的 `backend-dev.hcl`、填写自己拥有且不是占位值的 bucket，并明确授权 AWS 访问后运行：

```bash
terraform -chdir=labs/31-partial-backend-config-broken/starter init -reconfigure -backend-config=../backend-dev.hcl
```

该可选命令不属于 `labctl check`，不得直接使用未经修改的 `.example` 文件。

可选路径的安全边界：

- 前置条件：学习者自己拥有的 S3 bucket、单独配置的 AWS 身份验证，以及确认所选 key 未与其他技术栈共享。
- 文档所述仅初始化演示的预期最高成本：正常使用时低于 0.01 美元；该操作不会创建基础设施，但当前 S3 请求价格和账户策略仍由学习者负责。
- 清理：运行 `python tools/labctl.py reset 31` 删除本地 backend 元数据。文档所述仅初始化路径没有需要销毁的托管资源。如果之后向 bucket 写入状态，请检查所有权，并通过正常的 S3 流程只删除自己的状态/锁对象；本 Lab 永远不会自动删除远程对象。
- 已知风险：错误的 bucket 或 key 可能选中共享状态；backend 状态可能包含敏感信息；中断或未授权的初始化可能留下本地元数据，在切换环境前必须重置。

## 成功标准

- 静态配置恰好包含一个 S3 backend 块。
- 共享加密和 S3 状态锁安全设置保持静态。
- backend 块中不包含 bucket、key、region、身份验证信息及其他环境专属初始化参数。
- backend 块中不使用任何 Terraform 表达式。
- 三个示例文件互不相同，只包含 backend 占位值，并且不含凭据。
- `var.environment` 只影响普通配置求值。
- 默认验证器只在临时副本中移除 backend，并证明 dev、test 和 prod 会在没有任何 provider 配置的情况下分别产生匹配的部署标签。
- 格式检查、离线初始化、Terraform 验证、检查器自测以及实际静态检查全部通过。

## 重置说明

```bash
python tools/labctl.py reset 31
```

重置会删除 Lab 自有的 `.terraform/` 目录，包括 S3 backend 初始化元数据、锁文件、计划、状态产物和记录的结果。它不会删除学习者创建的 backend 配置文件。

## 有限提示

- backend 初始化发生在普通 Terraform 变量求值之前。
- dev、test 和 prod 之间不同的值应放入通过 `-backend-config` 传递的文件。
- 每个环境都相同的静态安全行为可以保留在 backend 块中。
