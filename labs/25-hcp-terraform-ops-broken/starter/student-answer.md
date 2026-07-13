# 学员作答

保留每个决策 ID，并将 `undecided` 替换为 `QUESTIONS.md` 中的一个选项 ID。

## 决策

- routine_run_workflow: undecided
- api_run_boundary: undecided
- pull_request_feedback: undecided
- workspace_dependency: undecided
- production_policy: undecided
- cost_estimation: undecided
- team_permissions: undecided
- production_auto_apply: undecided

## 理由

### routine_run_workflow

说明为什么这是常规配置来源与 run 路径。

### api_run_boundary

说明例外自动化路径的边界和凭据影响。

### pull_request_feedback

说明评审者能获得什么反馈，以及该 run 是否能改变基础设施。

### workspace_dependency

说明生产方与消费者方向，以及排队依赖 run 的事件。

### production_policy

说明违规是否阻止 run，以及是否有人可以绕过。

### cost_estimation

说明评审者如何使用估算，以及为何它不是完整账单保证。

### team_permissions

说明谁可以提出、查看、审批和管理生产 run。

### production_auto_apply

说明生产审批边界，以及低风险环境可如何不同。
