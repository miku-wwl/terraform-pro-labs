# Lab 10：根模块与子模块组合

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



## 可编辑文件

- `starter/main.tf`
