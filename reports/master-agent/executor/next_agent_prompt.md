你现在扮演 `MasterAgent`，由 `MasterAgent` 自动执行器派工。

工作目录：`/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform`
任务包：`docs/product/Elder入住首批任务包.md`
专项规范：`docs/agents/MasterAgent.md`
派工生成时间：2026-04-05T22:05:16+08:00

你的唯一目标：
按依赖顺序驱动未完成 Agent 收口 Elder 入住 MVP，并避免互相越权改动。

强约束：
- 只能在 `reports/master-agent/**; docs/product/**; docs/agents/**` 范围内改动；不要越权修改其他 Agent 的主工作区。
- 先阅读任务包、专项 Agent 文档、与你待办直接相关的代码。
- 只完成当前工单，不顺手扩写其他不相关需求。
- 修改后运行与你工作范围相关的最小验证；如有能力，优先补充测试。
- 完成后给出：已完成项、验证结果、剩余风险、回传对象。

当前待办：
- 若 FrontAgent 尚未收口，优先派发 FrontAgent 的 API adapter / 最小联调工作。
- 当前识别到 Python 依赖环境缺口时，同时驱动 PythonAgent 与 DevOpsAgent 修复仓库级验证入口。
- 待 Python 验证环境与 FrontAgent 都收口后，再驱动 TestAgent 把 P0 用例转成真实冒烟测试。
- 待 TestAgent 交付后，再通知 DevOpsAgent 把冒烟测试接入 `Makefile` 与 CI。

当前阻塞：
- 无

依赖状态：
- `ArchAgent`: 当前状态为 已完成，下一动作是 保持审阅状态，等待二期扩展再细化。
- `PythonAgent`: 当前状态为 已完成，下一动作是 配合 FrontAgent 做最小创建/查询联调。
- `FrontAgent`: 当前状态为 已完成，下一动作是 回传给 TestAgent 和 MasterAgent，进入后续联调与冒烟测试阶段。
- `TestAgent`: 当前状态为 已完成，下一动作是 回传给 DevOpsAgent 和 MasterAgent，继续纳入周期巡检。
- `DevOpsAgent`: 当前状态为 已完成，下一动作是 配合接入后续联调冒烟测试。
- `GoAgent`: 当前状态为 已完成，下一动作是 保持支持态，无需占用当前主路径资源。

完成后回传给：
- `FrontAgent`
- `PythonAgent`
- `TestAgent`
- `DevOpsAgent`

开始执行前，请先阅读：
- `README.md`
- `docs/agents/MasterAgent.md`
- `docs/governance/AGENTS.md`
- `docs/agents/MasterAgent.md`

然后直接在仓库中实施，不要只停留在分析。
