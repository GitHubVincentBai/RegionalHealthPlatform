# MasterAgent 工作单

- 当前红黄绿灯状态: 进行中
- 派工状态: ACTIVE
- 工作目标: 按依赖顺序驱动未完成 Agent 收口 Elder 入住 MVP，并避免互相越权改动。
- 写入范围: `reports/master-agent/**; docs/product/**; docs/agents/**`
- 依赖: ArchAgent、PythonAgent、FrontAgent、TestAgent、DevOpsAgent、GoAgent

## 待办

- 若 FrontAgent 尚未收口，优先派发 FrontAgent 的 API adapter / 最小联调工作。
- 当前识别到 Python 依赖环境缺口时，同时驱动 PythonAgent 与 DevOpsAgent 修复仓库级验证入口。
- 待 Python 验证环境与 FrontAgent 都收口后，再驱动 TestAgent 把 P0 用例转成真实冒烟测试。
- 待 TestAgent 交付后，再通知 DevOpsAgent 把冒烟测试接入 `Makefile` 与 CI。

## 阻塞

- FrontAgent 尚未完成 API adapter 与最小联调。
- PythonAgent / DevOpsAgent 尚未修复 Python HTTP 测试依赖环境。

## 回传对象

- `FrontAgent`
- `PythonAgent`
- `TestAgent`
- `DevOpsAgent`
