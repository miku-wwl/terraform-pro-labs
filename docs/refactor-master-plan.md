# 任务：将 `lance0821/tfpro-labs` 整改为可盲刷、可重置、可自动评分的 Terraform Professional Starter 仓库

目标仓库：

```text
https://github.com/lance0821/tfpro-labs
```

## 一、你的角色

你是一名 Senior Terraform Engineer、Terraform 培训实验设计者和 Git 仓库维护者。

你的任务不是简单清理几行答案，而是把当前包含 32 个实验的仓库，整改为一套：

* 可以从零开始盲刷；
* starter 和 solution 严格隔离；
* 每题可以一键重置；
* 每题拥有确定性的验收方式；
* 默认不会产生云资源费用；
* state、import、moved、backend 等实验可以真正复现；
* README、代码、测试和成功标准完全一致；

的 Terraform Professional 实操训练仓。

不要假设当前 README、代码或测试一定正确。当前仓库是待审计的输入材料，不是权威答案。

---

# 二、禁止直接开始批量修改

首先执行只读审计。

在完成仓库级审计前，不得直接批量修改全部 32 个实验。

先检查：

1. 顶层 README；
2. 每个 lab 的 README；
3. 所有 `.tf`、`.tftest.hcl`、JSON、CSV、module 和 backend 配置；
4. 题目描述是否与实际代码一致；
5. 当前代码究竟是 starter、半成品，还是完整 solution；
6. 当前测试是否真正验证了题目要求；
7. 实验是否能够在没有真实 AWS 凭据的情况下执行；
8. state/refactor 实验是否具备可复现的初始 state；
9. conceptual lab 是否被错误包装成 Terraform configuration；
10. 不同实验之间是否存在复制粘贴、重复题或主题错位。

先生成：

```text
docs/audit-report.md
docs/lab-matrix.csv
docs/lab-standard.md
```

`lab-matrix.csv` 至少包含：

```text
lab_id
slug
declared_topic
actual_topic
lab_type
difficulty
execution_mode
cloud_requirement
state_requirement
current_status
readme_code_consistent
tests_present
tests_meaningful
solution_leakage
bootstrap_required
known_defects
recommended_action
```

---

# 三、已知高风险问题

审计时必须重点检查，但不要只检查以下问题：

1. 多个 README 的 Success Criteria 可能是复制粘贴模板，与实际题目无关。

2. 部分名称包含 `-broken` 的目录，实际已经包含完整或接近完整的答案。

3. Lab 07 的 validation、precondition、check block 和 Terraform Test 可能已经直接泄露答案。

4. Lab 28 的题目是 Provider Version Constraints，但 `main.tf` 可能属于另一个 validation 实验。

5. Lab 03、11、19、26 等 state/refactor 实验可能缺少：

   * bootstrap configuration；
   * 初始 state；
   * 可重复生成的旧资源地址；
   * reset 流程；
   * no-op plan 验证。

6. Lab 25 是 HCP Terraform 场景判断题，不应只用 locals 和 outputs 输出问题文本。

7. Lab 31 要求使用 `backend.hcl`，需要确认对应文件、模板和初始化流程是否真正存在。

8. 部分 Terraform Test 可能只检查 output 是否存在，而没有检查资源数量、地址、过滤逻辑、生命周期或失败场景。

9. 顶层可能缺少统一的：

   * reset 工具；
   * validate 工具；
   * CI；
   * lock file 策略；
   * Terraform 版本策略；
   * AWS mock/live 执行策略。

10. 检查仓库许可证。不要擅自为上游代码添加许可证。保留原作者 attribution；若没有明确许可证，在报告中标为发布风险。

---

# 四、Git 和分支策略

不得重写上游历史，不得 force-push。

建议采用以下结构：

```text
upstream-snapshot
solutions
refactor/starter-v1
main
```

执行方式：

1. 将原始 `main` 保存为不可修改的 `upstream-snapshot` 分支或 tag。

2. 把当前可能包含答案的代码保存到：

```text
legacy-solution-candidate
```

3. 在：

```text
refactor/starter-v1
```

完成整改。

4. 最终的 starter 分支不得包含完整 solution。

5. canonical solution、详细解析和强验收测试放在 `solutions` 分支。

6. 不要在同一个学习目录下放置显眼的 `solution/`，否则无法盲刷。

7. 每批实验使用独立 commit；不要把 32 个实验压成一个无法审核的大 commit。

建议 commit 范围：

```text
chore(audit): inventory and classify existing labs
refactor(labs-01-05): standardize starter structure
refactor(labs-06-10): standardize starter structure
test(state-labs): add reproducible state fixtures
docs(hcp-labs): convert conceptual labs to scored scenarios
ci: add repository-wide validation workflow
```

---

# 五、统一实验结构

每个实验最终应采用以下结构；不存在的目录可以省略：

```text
labs/NN-topic/
├── README.md
├── lab.yaml
├── starter/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── versions.tf
│   └── terraform.tfvars.example
├── tests/
│   └── public.tftest.hcl
├── fixtures/
│   ├── input.json
│   ├── input.csv
│   └── producer-state/
├── bootstrap/
│   ├── README.md
│   ├── main.tf
│   ├── seed.sh
│   ├── seed.ps1
│   ├── reset.sh
│   └── reset.ps1
└── scripts/
    ├── validate.sh
    └── validate.ps1
```

`solutions` 分支可以额外拥有：

```text
labs/NN-topic/
├── solution/
├── tests/grader.tftest.hcl
└── SOLUTION.md
```

`lab.yaml` 至少包含：

```yaml
id: 7
title: Validation, Preconditions, Checks, and Tests
type: correction
tier: quality
difficulty: medium
estimated_minutes: 20

execution:
  mode: local
  terraform_version: "..."
  requires_cloud_credentials: false
  creates_billable_resources: false
  backend: local

validation:
  starter_expected_result: fail
  expected_failure_stage: test
  solution_expected_result: pass

editable_paths:
  - starter/main.tf
  - starter/variables.tf

protected_paths:
  - tests/
  - fixtures/
```

---

# 六、Starter 设计规则

每个 starter 必须满足以下原则。

## 1. 必须是真正的起点

不要把完整答案留在 starter 中。

根据题型选择以下方式之一：

* 删除关键 block；
* 留下不完整表达式；
* 保留一个有意义的错误实现；
* 保留需要重构的旧实现；
* 删除部分测试所需行为；
* 提供结构，但不提供核心逻辑。

## 2. 不得过度泄露答案

允许：

```hcl
# TODO: Create a stable map suitable for for_each.
```

不允许：

```hcl
# TODO: Write:
# { for name, cfg in var.buckets : name => cfg if cfg.versioning }
```

任务说明应描述行为和约束，而不是把完整 HCL 表达式写出来。

## 3. Starter 的失败必须是可解释的

每个 starter 必须明确记录：

```text
expected_failure_stage
expected_error_category
expected_failing_test
```

不要制造随机错误或多个互不相关的错误。

除非题目本身是 syntax/debugging lab，否则 starter 最好满足：

```bash
terraform fmt -check
terraform init -backend=false
terraform validate
```

然后在 plan 或 test 阶段因为缺少目标行为而失败。

## 4. 避免无意义占位符

不要依赖：

```text
REPLACE-ME-WITH-A-GLOBALLY-UNIQUE-NAME
```

优先使用：

* `random_id`；
* 测试变量；
* mock provider；
* account/environment prefix；
* 可重复的 fixture；
* plan-only 验证。

## 5. 默认不产生费用

除非实验明确标记为 `aws-live`，否则：

* 不执行真实 apply；
* 不创建真实 AWS 资源；
* 不要求长期 AWS 凭据；
* 不让测试依赖外部账户状态。

---

# 七、Solution 规则

对每个 lab，先根据题目重新建立 canonical solution，不能盲目把当前代码当作正确答案。

Canonical solution 必须：

1. 与 README 的任务逐条对应；
2. 通过格式化、初始化、validate、test 和适用的 plan；
3. 不包含硬编码凭据；
4. 不依赖未知的外部资源；
5. 使用稳定、可维护的 Terraform 写法；
6. 不为了通过测试而写投机代码；
7. 对 refactor lab 保持 resource identity；
8. 对 sensitive lab 不把秘密写入输出、日志或 fixture；
9. 对 provider constraints lab 真正修改 `required_providers`；
10. 对 HCP conceptual lab 提供场景答案和评分依据，而不是伪造资源。

`SOLUTION.md` 应说明：

```text
问题根因
正确设计
关键 Terraform 语义
完成步骤
验证命令
常见错误
为什么其他实现不合适
```

---

# 八、自动验收要求

仓库级最少提供以下命令：

```bash
python tools/labctl.py list
python tools/labctl.py status 07
python tools/labctl.py reset 07
python tools/labctl.py check 07
python tools/labctl.py check --all
```

Windows 必须可用，因此不要只提供 Bash。

`labctl.py check` 根据 lab 类型选择执行：

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
terraform test
terraform plan
```

必要时额外执行：

```bash
terraform show -json plan.tfplan
terraform state list
terraform providers
terraform workspace show
```

验收必须是双向的：

## Starter gate

starter 必须：

* 在预期阶段失败；
* 失败原因与本题目标直接相关；
* 不能因为缺凭据、网络、无效 bucket name 或无关语法错误而失败。

## Solution gate

solution 必须：

* `terraform fmt -check` 通过；
* `terraform init` 通过；
* `terraform validate` 通过；
* 适用时 `terraform test` 全部通过；
* 适用时 plan 符合预期；
* refactor lab 不产生非预期 destroy/create；
* reset 后可以再次完整执行。

---

# 九、Terraform Test 质量要求

不要只测试：

```hcl
output.value != null
can(output.value)
```

测试应检查真正的行为，例如：

* resource 数量；
* `for_each` 的稳定 key；
* 过滤结果；
* map/list 类型和 key；
* merged tags；
* lifecycle 配置；
* versioning 是否只应用到指定资源；
* invalid variables 是否按预期失败；
* precondition 的失败对象；
* sensitive output 是否被正确标记；
* replacement 是否由正确 dependency 触发；
* moved block 后的地址；
* plan 中是否出现 delete/create；
* provider alias 是否正确传给 child module。

每题至少考虑：

1. 一个正常场景；
2. 一个边界场景；
3. 一个失败场景；
4. 适用时一个 refactor/state 场景。

公开测试不得直接泄露完整实现。

可以将更强的 grader tests 放在 `solutions` 或独立 grader 分支。

不要断言由 provider 在 apply 时才确定、容易漂移的值。

---

# 十、不同类型实验的专项处理

## A. Local authoring labs

优先使用：

```text
terraform_data
locals
variables
outputs
files
jsondecode
csvdecode
```

使其能够离线执行。

需要 AWS schema 时，可以使用当前 Terraform 版本支持的 provider mocking 能力，但必须确认语法真实可用。

## B. AWS wiring labs

分类为：

```text
aws-mock
aws-plan
aws-live
```

默认使用 `aws-mock` 或 `aws-plan`。

真实 AWS apply 只能是可选路径，并且必须提供：

```text
cost warning
prerequisites
bootstrap
cleanup
maximum expected cost
```

测试 AWS lab 时，应验证真实 Terraform graph 和资源配置，而不仅仅是 output。

## C. Import、moved、removed 和 refactor labs

这些实验必须具有明确阶段：

```text
bootstrap/old-config
starter/refactor-config
solution/final-config
```

完整流程应能自动执行：

```text
1. 创建或模拟旧资源
2. 使用旧 configuration 建立初始 state
3. 切换到 starter
4. 执行 import、moved 或 removed 操作
5. 验证 state address
6. 验证最终 plan
7. reset
```

不得仅在 README 中写：

```text
Assume the infrastructure already exists.
```

必须提供可复现 fixture。

验证时至少检查：

* refactor 前后的 resource address；
* 是否出现 unintended destroy/create；
* 最终是否为 no-op plan；
* import target 是否正确；
* moved block 是否覆盖所有旧地址；
* `count` 到 `for_each` 的 key 映射是否稳定。

## D. Backend、remote state 和 workspace labs

必须明确拆分：

```text
producer/
consumer/
backend-config/
fixtures/
```

提供：

```text
backend-dev.hcl.example
backend-test.hcl.example
backend-prod.hcl.example
```

不要尝试在 backend block 中使用普通 variables。

默认模式应能使用 local backend 或 fixture state 完成训练。

真实 S3 backend 只能作为可选扩展。

## E. HCP Terraform conceptual labs

不要伪装成普通 `.tf` 实验。

转换为：

```text
SCENARIO.md
QUESTIONS.md
rubric.yaml
student-answer.md
```

答案放在 solutions 分支：

```text
ANSWER_KEY.md
```

题目可以要求判断：

* VCS-driven 与 API-driven workflow；
* run trigger 拓扑；
* policy enforcement；
* cost estimation；
* workspace permissions；
* speculative plan；
* auto-apply；
* production approval boundary。

评分应基于关键决策点，而不是字符串完全匹配。

## F. Provider constraints labs

题目必须真正围绕：

```hcl
terraform {
  required_version = "..."

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "..."
    }
  }
}
```

不能混入无关的 environment、instance type、precondition 模板。

测试需要判断约束语义，而不仅是 `terraform validate`。

## G. Terraform Test labs

starter 应包含待修复或待补充的测试，而不是已经完成全部 test flow。

涵盖：

* `command = plan`；
* `command = apply`；
* sequential runs；
* `expect_failures`；
* setup state；
* meaningful assertions；
* cleanup behavior。

---

# 十一、README 统一模板

每个 README 必须包含：

```text
Title
Scenario
Skills tested
Difficulty
Estimated time
Execution mode
Cloud credentials required
Cost risk
Starting state
Files allowed to edit
Files not allowed to edit
Tasks
Constraints
Expected initial failure
Validation commands
Success criteria
Reset instructions
Hints
```

Success Criteria 必须针对当前实验逐条编写。

禁止复制无关的通用内容，例如每题都强制要求：

```text
variable validation
precondition
check block
```

除非这些确实是当前实验目标。

README 中的命令必须与实际实验一致。

例如 test lab 不能只写：

```bash
terraform plan
```

而应该包含：

```bash
terraform test
```

---

# 十二、仓库级 CI

增加 GitHub Actions，但区分本地测试和真实云测试。

默认 PR CI：

```text
terraform fmt -check -recursive
manifest validation
README/manifest consistency check
local lab init/validate/test
mock AWS lab tests
starter expected-failure checks
solution branch pass checks
```

真实 AWS 测试：

* 不在普通 PR 中自动执行；
* 使用手动 workflow；
* 需要明确 secrets；
* 必须自动 cleanup；
* 不得因凭据缺失导致普通 CI 失败。

CI 使用 matrix 执行各 lab，并输出明确的 lab ID 和失败阶段。

---

# 十三、分批执行，防止标准漂移

先整改以下代表题作为 pilot：

```text
Lab 01 — 简单 authoring/lifecycle
Lab 07 — validation/check/test，且可能泄露答案
Lab 11 — import/moved/refactor
Lab 25 — HCP conceptual
Lab 31 — partial backend configuration
```

Pilot 必须覆盖五种不同类型。

完成 pilot 后：

1. 验证目录结构；
2. 验证 reset；
3. 验证 starter expected failure；
4. 验证 solution pass；
5. 更新 `docs/lab-standard.md`；
6. 只有 pilot 全部通过后，才继续其余实验。

后续建议批次：

```text
Batch 1: 01–05
Batch 2: 06–10
Batch 3: 11–16
Batch 4: 17–22
Batch 5: 23–27
Batch 6: 28–32
```

每批结束时运行全仓回归，避免后续批次破坏前面的实验。

---

# 十四、最终交付物

必须交付：

```text
docs/audit-report.md
docs/lab-matrix.csv
docs/lab-standard.md
docs/migration-report.md
tools/labctl.py
.github/workflows/terraform-labs.yml
```

`migration-report.md` 必须说明：

* 每个 lab 原来的问题；
* 采取了什么修复；
* starter 如何失败；
* solution 如何验证；
* 是否需要 AWS；
* 是否需要 bootstrap；
* 是否仍有未解决问题；
* 哪些题目被合并、拆分或改为 conceptual scenario；
* 哪些内容可能受上游许可证限制。

最后输出汇总表：

```text
Lab
Original status
Final type
Starter verified
Solution verified
Reset verified
Cloud required
Remaining risk
```

---

# 十五、质量底线

不得：

* 把当前代码未经验证地认定为 canonical solution；
* 只删除几行代码就称为 starter；
* 为了让 CI 变绿而削弱测试；
* 用 output 非空代替行为验证；
* 在 starter 中泄露完整答案；
* 用真实 AWS apply 作为默认路径；
* 对 state lab 使用无法复现的人工前提；
* 把 conceptual question 伪装成无意义的 Terraform outputs；
* 保留 README 与代码主题错位；
* 擅自添加上游未授权的许可证；
* 声称某个实验通过，但没有实际执行对应验证。

当网络、provider、AWS 凭据或工具限制导致某项验证无法执行时，必须明确标注：

```text
NOT VERIFIED
```

并说明原因，不得猜测或伪造成功结果。
