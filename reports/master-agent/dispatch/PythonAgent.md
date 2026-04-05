# PythonAgent 工作单

- 当前红黄绿灯状态: 已完成
- 派工状态: SUPPORT
- 工作目标: 确保 elder-service 既提供稳定 API 契约，也能在仓库级验证环境里稳定跑通 HTTP 测试。
- 写入范围: `services/python/**`
- 依赖: ArchAgent

## 待办

- 核对 `POST /elders`、`GET /elders`、`GET /elders/{elder_id}` 的请求/响应字段与任务包完全一致。
- 为 FrontAgent 提供稳定示例 payload，重点覆盖 `family_contacts`、`stay_info`、`room_id`、`bed_id`。
- 如联调发现字段缺口，只修改 Python 侧职责范围内的接口、模型和测试。
- 补齐 `fastapi`/测试依赖的运行假设，确保 Python 服务依赖声明与测试入口一致。

## 阻塞

- 无

## 回传对象

- `DevOpsAgent`
- `TestAgent`
- `MasterAgent`
