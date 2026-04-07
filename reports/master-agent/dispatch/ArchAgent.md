# ArchAgent 工作单

- 当前红黄绿灯状态: 风险
- 派工状态: DONE
- 工作目标: 保持 Elder 入住 MVP 的字段边界稳定，不主动扩大范围。
- 写入范围: `docs/architecture/**`
- 依赖: 无

## 待办

- 审阅任何新增的入住状态、床位关联或家属关系字段，防止越界到合同/费用/护理计划。
- 如果 FrontAgent 或 PythonAgent 提出模型扩展诉求，只输出边界约束，不直接代写其他栈代码。

## 阻塞

- 无

## 回传对象

- `PythonAgent`
- `FrontAgent`
- `MasterAgent`
