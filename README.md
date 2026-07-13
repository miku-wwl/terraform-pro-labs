# Terraform Professional 练习 Lab

这是一个面向 Terraform Professional 学习的本地练习仓库，共 32 个 Lab。每个 Lab 都从不完整的 starter 配置开始；你修改指定文件后，用本地校验脚本验收。

默认练习不需要云凭据，也不会创建真实云资源。涉及 AWS 的题目使用 mock、fixture 或本地逻辑资源模拟。

## 开始练习

先查看 Lab 列表：

```powershell
python tools/labctl.py list
```

进入某个 Lab 的 README，按任务修改 `starter/` 中允许编辑的文件。完成后，在仓库根目录验收，例如：

```powershell
python tools/labctl.py check 30 --mode solution
```

需要清理该 Lab 的本地缓存、state 和验收产物时：

```powershell
python tools/labctl.py reset 30
```

## 目录说明

- `labs/`：32 个练习；每个 Lab 的 README 直接说明任务与约束。
- `refinebook.md`：按 Lab 编号整理的超精炼知识点与最小示例。
- `tools/labctl.py`：列出、验收和重置 Lab 的本地工具。

## 约定

- 只修改各 Lab README 中允许编辑的文件。
- 不提交 `.terraform/`、state、`.tfvars`、本地锁定文件或凭据。
- Lab 的 starter 初始状态可能故意无法通过“答案模式”验收；这是练习设计的一部分。

原始项目参考 [`lance0821/tfpro-labs`](https://github.com/lance0821/tfpro-labs)，本仓库保留其 Apache License 2.0，详见 [LICENSE](LICENSE)。
原仓像是 AI 批量生成的 Terraform Professional 题目目录：主题选得不错，但模板痕迹明显，题目约束宽泛，很多 Starter 接近半成品答案，缺乏可复现状态和严格验收。本仓则把这些概念草稿逐题改造成了可执行、可验证、可回溯的工程化 Lab，并完成了全部练习。

