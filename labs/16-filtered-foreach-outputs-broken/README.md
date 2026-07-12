# Lab 16：过滤后的 for_each 与稳定的 map 输出

## 场景

一个 service catalog 同时包含已启用和已禁用的条目。当前 root 为每个条目创建 deployment record，并公开基于位置的 list。重构配置，使其只处理选定子集，同时在资源地址和输出中保留逻辑 service 名称。

## 考查技能

- 为 `for_each` 过滤 map
- 稳定的逻辑资源键
- 从托管资源派生 map 形态的输出
- 空选择的边界行为

## 难度与预计时间

- 难度：中等
- 预计时间：20 分钟

## 执行模式

使用 `terraform_data` 在本地进行 Terraform 配置编写。

## 是否需要云凭据

不需要。

## 成本风险

无。

## 初始状态

输入已经是 map，但 starter 也会部署已禁用的 service，并将结果转换为 list，从而丢失稳定的输出键。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `tests/public.tftest.hcl`
- `scripts/verify_tests.py`
- `lab.yaml`

## 任务

1. 从 service map 中派生已启用的子集。
2. 仅遍历该子集来创建 deployment record。
3. 将 deployment 标识符和端口作为以 service 名称为键的 map 返回。
4. 确保没有任何 service 启用时行为仍然安全。

## 约束

- 不要使用 `count` 或基于位置的索引。
- 不要为已禁用的 service 创建 deployment record。
- 保留输入 map 的键，不要生成数字键。
- 拒绝有效 TCP 范围之外的端口。

## 预期初始失败

`python tools/labctl.py check 16` 会在测试阶段报告 `EXPECTED_FILTERED_FOREACH_INCOMPLETE`，因为 starter 包含一个已禁用的键并返回 list。

## 验证命令

```bash
python tools/labctl.py check 16
python tools/labctl.py status 16
```

## 成功标准

- 默认资源键和输出键必须恰好为 `api` 和 `worker`；不能包含已禁用的记录。
- 精确端口必须继续与其逻辑名称关联。
- 无论声明顺序如何，替代逻辑名称都必须保留为精确的资源标识。
- 输入全部禁用时必须创建零个资源，并生成空 map。
- 无效端口必须在规划资源前被拒绝。

## 重置说明

```bash
python tools/labctl.py reset 16
```

## 有限提示

- 在将 collection 分配给资源之前先进行过滤。
- 生成输出时保留 `for_each` 键。
