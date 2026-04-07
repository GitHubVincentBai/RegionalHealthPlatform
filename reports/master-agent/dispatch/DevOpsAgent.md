# DevOpsAgent 工作单

- 当前红黄绿灯状态: 已完成
- 派工状态: DONE
- 工作目标: 修复仓库级验证环境，并在后续把联调冒烟检查纳入统一验证入口与持续监督链路。
- 写入范围: `.github/**; deploy/**; scripts/**; Makefile; docs/governance/**`
- 依赖: TestAgent

## 待办

- 调整 Python 验证入口，使 `make verify` 在正确的依赖环境里执行 elder-service HTTP 测试。
- 与 PythonAgent 对齐依赖声明和测试执行方式，避免 `fastapi` 等运行依赖在仓库级检查里缺失。
- 在 TestAgent 提供真实冒烟资产后，将其接入 `Makefile` 和必要的 CI 流程。
- 继续维护 `MasterAgent` 监督/派工脚本，让报告和派工单可持续运行。
- 不修改 Front/Python/Go 业务代码，只处理流程、脚本和验证入口。

## 阻塞

- 无

## 回传对象

- `PythonAgent`
- `MasterAgent`
