# 问题与选项 ID

在 `student-answer.md` 中，每个问题只能使用一个选项 ID，并在对应理由部分解释取舍。

## 1. 常规 run 工作流（`routine_run_workflow`）

- `vcs_default`：将每个 workspace 连接到经过评审的仓库，由所选分支的变更启动标准 run。
- `api_default`：让工程师通过自定义 API 客户端上传每一个常规 configuration version，并创建每一个 run。
- `ui_default`：断开源代码管理，要求 workspace 管理员在 UI 中启动所有常规 run。

## 2. API 驱动 run 的边界（`api_run_boundary`）

- `never_use_api`：即使是已批准的机器到机器发布流程，也禁止 API 驱动的 run。
- `approved_automation_only`：将 API 上传 configuration 和创建 run 限定为例外的发布服务流程，使用范围受限且可审计的凭据。
- `developer_tokens`：为每位开发人员发放权限宽泛的 token，将 API 驱动 run 用于普通 Pull Request 工作。

## 3. Pull Request 反馈（`pull_request_feedback`）

- `standard_apply_run`：为每个 Pull Request 启动普通的 plan-and-apply run。
- `speculative_plan`：使用 VCS 的 Pull Request 集成生成仅 plan、不可 apply 的 run。
- `skip_plan`：合并后才生成 Terraform 反馈。

## 4. Workspace 依赖（`workspace_dependency`）

- `network_to_application`：将 `network-prod` 配为来源，在网络成功 apply 后排队 `application-prod`。
- `application_to_network`：将 `application-prod` 配为来源，在应用成功 apply 后排队 `network-prod`。
- `pull_request_trigger`：每当 `network-prod` 打开一次 speculative Pull Request plan 时，都排队 `application-prod`。

## 5. 生产策略（`production_policy`）

- `advisory_only`：对公开可访问数据库报告警告，但允许 run 自动继续。
- `mandatory_no_routine_override`：阻止生产 run，要求修复违规；对此规则不提供常规绕过路径。
- `post_apply_audit`：仅在基础设施 apply 后检查该规则。

## 6. 成本估算（`cost_estimation`）

- `exact_invoice_gate`：将估算视为完整的未来账单，低于估算时自动批准 run。
- `review_signal_with_limits`：在评审期间展示估算和差异，同时保留审批控制，并承认不受支持或外部计价项目的局限。
- `disable_estimation`：因为估算无法绝对完整而禁用估算。

## 7. 团队权限（`team_permissions`）

- `developers_plan_release_apply`：给予应用开发人员 plan 权限，给予发布管理团队 apply 权限；workspace 管理权单独保留。
- `developers_apply`：给予所有应用开发人员 apply 和 workspace-admin 权限，确保评审永不阻塞交付。
- `admins_only`：只允许组织所有者查看、plan 和 apply workspace run。

## 8. 生产 auto-apply（`production_auto_apply`）

- `all_runs_auto_apply`：所有生产 run（包括依赖触发的 run）在检查完成后立即 auto-apply。
- `manual_production_boundary`：生产 apply 保持人工审批，包括 run-triggered 的生产 run；可让单独治理的低风险开发 workspace auto-apply。
- `no_automation_anywhere`：要求组织所有者团队手动 apply 每一个开发和生产 run。
