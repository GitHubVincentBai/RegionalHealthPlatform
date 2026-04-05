# FrontAgent 工作单

- 当前红黄绿灯状态: 进行中
- 派工状态: BLOCKED
- 工作目标: 完成 Elder 入住 MVP 前端 API 适配层与最小联调，不再停留在静态骨架。
- 写入范围: `apps/**`
- 依赖: PythonAgent

## 待办

- 在 `apps/web` 下新增 API adapter 目录与 elder-service 访问封装，只处理前端职责范围内的调用适配。
- 把列表、详情、创建入口与 elder-service 的最小 create/list/get 链路接通，保留 mock 兜底策略时要显式标注。
- 补充前端侧最小联调或调用层测试，避免页面骨架与真实接口脱节。

## 阻塞

- 等待 PythonAgent 提供稳定 API 契约。

## 回传对象

- `TestAgent`
- `MasterAgent`
