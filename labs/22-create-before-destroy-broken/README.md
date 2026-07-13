# Lab 22：替换资源时先创建再销毁

## 任务

`service_name` 是服务的可原地更新属性，`release` 是不可变发布标识。当前资源会在 `release` 变化时替换，但默认替换顺序可能先删除旧实例。

保留现有资源地址和 `triggers_replace`，让 `release` 变化时先创建新实例、再销毁旧实例。服务名称单独变化时仍应是原地更新；输入完全不变时应保持 no-op。

## 约束

- 不移除或削弱 `triggers_replace`。
- 不把发布版本变化改为原地更新。
- 不编辑验证脚本。
- 不添加 provider。
- 只能编辑 `starter/main.tf`。
