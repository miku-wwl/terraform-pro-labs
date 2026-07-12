# Lab 16：过滤后的 for_each 与稳定的 map 输出

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



## 可编辑文件

- `starter/main.tf`
