# Terraform Professional 练习 Lab

这是一个面向 Terraform Professional 学习的本地练习仓库，共 32 个 Lab。每个 Lab 都从不完整的 starter 配置开始；你修改指定文件后，用本地校验脚本验收。

默认练习不需要云凭据，也不会创建真实云资源。涉及 AWS 的题目使用 mock、fixture 或本地逻辑资源模拟。

## 使用方式

打开目标 Lab 的 README，直接让 AI 协作完成学习。例如：

```text
开始 Lab 30：先解释任务，再让我自己修改；完成后帮我验收。
```

写完后只需告诉 AI：

```text
验收 Lab 30；通过后推送到 GitHub main。
```

AI 会执行本地校验、解释失败原因、复验，并在通过后提交；你不需要手动运行验收指令。

每次推送的 Git 提交都是一个 checkpoint。想从某个节点开始全新的 Lab 时，告诉 AI 对应的提交 ID 与目标 Lab，例如：

```text
以 8bebc 为 checkpoint 创建新分支，从 Lab 31 开始练习。
```

建议从 checkpoint 创建分支，而不是直接 checkout 到旧提交，以免进入 detached HEAD。或者每次练习完，抛弃掉更改，直接checkout到其他的Hash，进行练习。

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

