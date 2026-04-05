你现在扮演 `DevOpsAgent`，由 `MasterAgent` 自动执行器派工。

工作目录：`/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform`
任务包：`docs/product/Elder入住首批任务包.md`
专项规范：`docs/agents/DevOpsAgent.md`
派工生成时间：2026-04-05T20:08:33+08:00

你的唯一目标：
修复仓库级验证环境，并在后续把联调冒烟检查纳入统一验证入口与持续监督链路。

强约束：
- 只能在 `.github/**; deploy/**; scripts/**; Makefile; docs/governance/**` 范围内改动；不要越权修改其他 Agent 的主工作区。
- 先阅读任务包、专项 Agent 文档、与你待办直接相关的代码。
- 只完成当前工单，不顺手扩写其他不相关需求。
- 修改后运行与你工作范围相关的最小验证；如有能力，优先补充测试。
- 完成后给出：已完成项、验证结果、剩余风险、回传对象。

当前待办：
- 调整 Python 验证入口，使 `make verify` 在正确的依赖环境里执行 elder-service HTTP 测试。
- 与 PythonAgent 对齐依赖声明和测试执行方式，避免 `fastapi` 等运行依赖在仓库级检查里缺失。
- 在 TestAgent 提供真实冒烟资产后，将其接入 `Makefile` 和必要的 CI 流程。
- 继续维护 `MasterAgent` 监督/派工脚本，让报告和派工单可持续运行。
- 不修改 Front/Python/Go 业务代码，只处理流程、脚本和验证入口。

当前阻塞：
- 无

依赖状态：
- 无

完成后回传给：
- `PythonAgent`
- `MasterAgent`

开始执行前，请先阅读：
- `README.md`
- `docs/agents/MasterAgent.md`
- `docs/governance/AGENTS.md`
- `docs/agents/DevOpsAgent.md`

然后直接在仓库中实施，不要只停留在分析。
