# MasterAgent 自动派工单

- 生成时间: 2026-04-05 20:12:59 CST
- 分支: `codex/elder-list-query`
- 派工目标: 基于 `docs/product/Elder入住首批任务包.md` 驱动各 Agent 继续收口 Elder 入住 MVP

## 派工总览

| Agent | 当前状态 | 派工状态 | 依赖 | 写入范围 |
|---|---|---|---|---|
| `ArchAgent` | 已完成 | DONE | 无 | `docs/architecture/**` |
| `PythonAgent` | 进行中 | ACTIVE | ArchAgent | `services/python/**` |
| `FrontAgent` | 进行中 | BLOCKED | PythonAgent | `apps/**` |
| `TestAgent` | 已完成 | DONE | PythonAgent、FrontAgent | `tests/**; apps/** 内测试文件; services/** 内测试文件` |
| `DevOpsAgent` | 进行中 | ACTIVE | 无 | `.github/**; deploy/**; scripts/**; Makefile; docs/governance/**` |
| `GoAgent` | 已完成 | DONE | 无 | `services/go/**` |
| `MasterAgent` | 进行中 | ACTIVE | ArchAgent、PythonAgent、FrontAgent、TestAgent、DevOpsAgent、GoAgent | `reports/master-agent/**; docs/product/**; docs/agents/**` |

## MasterAgent 调度顺序

1. 先驱动 `FrontAgent` 完成 API adapter 与最小联调。
2. 再驱动 `TestAgent` 将 P0 用例转成真实冒烟测试。
3. 最后驱动 `DevOpsAgent` 接入新的冒烟测试到 `Makefile` / CI。
4. `PythonAgent` 在本轮以支持态提供稳定接口契约，不越权修改前端和测试目录。
5. `ArchAgent` 与 `GoAgent` 保持边界审阅和支持态，不抢占主路径资源。

## 各 Agent 工单

### `ArchAgent`

- 派工状态: `DONE`
- 工作目标: 保持 Elder 入住 MVP 的字段边界稳定，不主动扩大范围。
- 写入范围: `docs/architecture/**`
- 依赖: 无
- 待办:
  - 审阅任何新增的入住状态、床位关联或家属关系字段，防止越界到合同/费用/护理计划。
  - 如果 FrontAgent 或 PythonAgent 提出模型扩展诉求，只输出边界约束，不直接代写其他栈代码。
- 阻塞:
  - 无
- 完成后回传给:
  - `PythonAgent`
  - `FrontAgent`
  - `MasterAgent`

### `PythonAgent`

- 派工状态: `ACTIVE`
- 工作目标: 确保 elder-service 既提供稳定 API 契约，也能在仓库级验证环境里稳定跑通 HTTP 测试。
- 写入范围: `services/python/**`
- 依赖: ArchAgent
- 待办:
  - 核对 `POST /elders`、`GET /elders`、`GET /elders/{elder_id}` 的请求/响应字段与任务包完全一致。
  - 为 FrontAgent 提供稳定示例 payload，重点覆盖 `family_contacts`、`stay_info`、`room_id`、`bed_id`。
  - 如联调发现字段缺口，只修改 Python 侧职责范围内的接口、模型和测试。
  - 补齐 `fastapi`/测试依赖的运行假设，确保 Python 服务依赖声明与测试入口一致。
- 阻塞:
  - 无
- 完成后回传给:
  - `DevOpsAgent`
  - `TestAgent`
  - `MasterAgent`

### `FrontAgent`

- 派工状态: `BLOCKED`
- 工作目标: 完成 Elder 入住 MVP 前端 API 适配层与最小联调，不再停留在静态骨架。
- 写入范围: `apps/**`
- 依赖: PythonAgent
- 待办:
  - 在 `apps/web` 下新增 API adapter 目录与 elder-service 访问封装，只处理前端职责范围内的调用适配。
  - 把列表、详情、创建入口与 elder-service 的最小 create/list/get 链路接通，保留 mock 兜底策略时要显式标注。
  - 补充前端侧最小联调或调用层测试，避免页面骨架与真实接口脱节。
- 阻塞:
  - 等待 PythonAgent 提供稳定 API 契约。
- 完成后回传给:
  - `TestAgent`
  - `MasterAgent`

### `TestAgent`

- 派工状态: `DONE`
- 工作目标: 把 Elder 入住 MVP 的 P0 用例落成真实可执行的自动化或冒烟资产。
- 写入范围: `tests/**; apps/** 内测试文件; services/** 内测试文件`
- 依赖: PythonAgent、FrontAgent
- 待办:
  - 新增一条前后端最小冒烟资产，覆盖创建档案后可查询列表/详情的主链路。
  - 把测试矩阵中的 P0 用例映射到实际文件与执行命令，避免只有文档没有结果。
  - 仅在测试目录或测试文件中补强，不直接改业务实现；若发现缺口，回传给对应 Agent。
- 阻塞:
  - 等待 FrontAgent 完成 API adapter / 最小联调接入。
- 完成后回传给:
  - `DevOpsAgent`
  - `MasterAgent`

### `DevOpsAgent`

- 派工状态: `ACTIVE`
- 工作目标: 修复仓库级验证环境，并在后续把联调冒烟检查纳入统一验证入口与持续监督链路。
- 写入范围: `.github/**; deploy/**; scripts/**; Makefile; docs/governance/**`
- 依赖: 无
- 待办:
  - 调整 Python 验证入口，使 `make verify` 在正确的依赖环境里执行 elder-service HTTP 测试。
  - 与 PythonAgent 对齐依赖声明和测试执行方式，避免 `fastapi` 等运行依赖在仓库级检查里缺失。
  - 在 TestAgent 提供真实冒烟资产后，将其接入 `Makefile` 和必要的 CI 流程。
  - 继续维护 `MasterAgent` 监督/派工脚本，让报告和派工单可持续运行。
  - 不修改 Front/Python/Go 业务代码，只处理流程、脚本和验证入口。
- 阻塞:
  - 无
- 完成后回传给:
  - `PythonAgent`
  - `MasterAgent`

### `GoAgent`

- 派工状态: `DONE`
- 工作目标: 保持 Go IoT gateway 在本波次中处于稳定支持态，不抢占 Elder 入住主路径资源。
- 写入范围: `services/go/**`
- 依赖: 无
- 待办:
  - 持续保持现有测试和构建通过。
  - 仅在 MasterAgent 明确引入设备/实时链路依赖时再进入活跃开发。
- 阻塞:
  - 无
- 完成后回传给:
  - `MasterAgent`

### `MasterAgent`

- 派工状态: `ACTIVE`
- 工作目标: 按依赖顺序驱动未完成 Agent 收口 Elder 入住 MVP，并避免互相越权改动。
- 写入范围: `reports/master-agent/**; docs/product/**; docs/agents/**`
- 依赖: ArchAgent、PythonAgent、FrontAgent、TestAgent、DevOpsAgent、GoAgent
- 待办:
  - 若 FrontAgent 尚未收口，优先派发 FrontAgent 的 API adapter / 最小联调工作。
  - 当前识别到 Python 依赖环境缺口时，同时驱动 PythonAgent 与 DevOpsAgent 修复仓库级验证入口。
  - 待 Python 验证环境与 FrontAgent 都收口后，再驱动 TestAgent 把 P0 用例转成真实冒烟测试。
  - 待 TestAgent 交付后，再通知 DevOpsAgent 把冒烟测试接入 `Makefile` 与 CI。
- 阻塞:
  - FrontAgent 尚未完成 API adapter 与最小联调。
  - PythonAgent / DevOpsAgent 尚未修复 Python HTTP 测试依赖环境。
- 完成后回传给:
  - `FrontAgent`
  - `PythonAgent`
  - `TestAgent`
  - `DevOpsAgent`

派工总表已写入: [reports/master-agent/elder_mvp_dispatch.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/reports/master-agent/elder_mvp_dispatch.md)
