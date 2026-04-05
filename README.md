# 区域康养平台仓库说明

本仓库用于沉淀“沈阳市和平区全域综合养老服务项目（一期）”区域康养平台的架构设计、模块规划、Agent 协作规范、GitHub 治理模板和后续工程交付标准。

当前仓库重点不是业务代码本身，而是先建立一套适合 `Codex + GitHub` 协同开发的标准化入口，确保后续前端、Go、Python、测试、DevOps 可以在统一规则下协作推进。

如果你是第一次进入这个仓库，建议按这个顺序开始：

1. 阅读 [README.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/README.md)
2. 阅读 [MasterAgent.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/agents/MasterAgent.md) 和 [AGENTS.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/AGENTS.md)
3. 根据任务类型进入对应专项 Agent 文档
4. 发起 Issue 或直接使用 [CodexTaskPrompt.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/governance/CodexTaskPrompt.md) 派发任务
5. 在本地运行 `make verify`
6. 通过 PR 进入 GitHub 协作流程

## 仓库目标

- 沉淀区域康养平台的一期架构与模块设计
- 建立 Master Agent 到各子 Agent 的统一调度机制
- 建立标准化的本地验证、PR、CI、Review 闭环
- 为后续多技术栈工程落仓提供统一治理骨架

## 文档导航

### 核心入口

- [README.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/README.md)
  仓库入口说明
- [MasterAgent.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/agents/MasterAgent.md)
  总控调度规则、质量门禁和 GitHub 闭环
- [AGENTS.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/AGENTS.md)
  仓库级 Agent 入口说明

### 业务与架构文档

- [PRD.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/product/PRD.md)
  产品需求说明
- [Modules.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/product/Modules.md)
  模块拆分说明
- [Arch.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/architecture/Arch.md)
  总体架构设计和 Arch Agent 约束

### 专项 Agent 文档

- [FrontAgent.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/agents/FrontAgent.md)
  前端智能体规则
- [GoAgent.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/agents/GoAgent.md)
  Go 后端智能体规则
- [PythonAgent.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/agents/PythonAgent.md)
  Python 后端智能体规则
- [DevOpsAgent.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/agents/DevOpsAgent.md)
  DevOps、CI/CD、仓库治理规则
- [TestAgent.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/agents/TestAgent.md)
  测试与质量保障规则

### GitHub 与任务模板

- [docs/governance/AGENTS.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/governance/AGENTS.md)
  通用 Agent 执行模板
- [CodexTaskPrompt.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/governance/CodexTaskPrompt.md)
  发起 Codex 任务的标准 prompt
- [.github/pull_request_template.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/.github/pull_request_template.md)
  PR 模板
- [repository-governance.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/governance/repository-governance.md)
  分支保护、标签和 PR 治理建议
- [.github/CODEOWNERS](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/.github/CODEOWNERS)
  代码所有者模板
- [.github/ISSUE_TEMPLATE/feature_request.yml](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/.github/ISSUE_TEMPLATE/feature_request.yml)
  Feature Issue 模板
- [.github/ISSUE_TEMPLATE/bug_report.yml](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/.github/ISSUE_TEMPLATE/bug_report.yml)
  Bug Issue 模板
- [.github/ISSUE_TEMPLATE/task_request.yml](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/.github/ISSUE_TEMPLATE/task_request.yml)
  工程任务 Issue 模板
- [.github/workflows/ci.yml](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/.github/workflows/ci.yml)
  最小可用 CI 模板

## Agent 协作模型

本仓库采用“Master Agent 统一调度，专项 Agent 分工执行”的方式：

- `MasterAgent`
  负责识别任务类型、拆分任务、协调边界、监督质量门禁和 GitHub 闭环
- `ArchAgent`
  负责架构边界、服务职责、数据流和跨模块约束
- `FrontAgent`
  负责 Web、H5、小程序前端实现
- `GoAgent`
  负责设备接入、实时链路、高并发服务
- `PythonAgent`
  负责后台 API、规则引擎、分析报表、任务编排
- `DevOpsAgent`
  负责仓库治理、分支规范、CI/CD、环境与发布
- `TestAgent`
  负责测试策略、自动化测试、回归与质量结论

跨端、跨服务、跨流程任务，默认优先由 [MasterAgent.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/agents/MasterAgent.md) 统筹。

## 标准开发闭环

所有 AI 或人工协作任务，默认遵循以下闭环：

1. 阅读任务背景、文档和现有实现
2. 明确影响范围、依赖和验收标准
3. 选择合适的专项 Agent 执行
4. 做最小可行改动
5. 更新文档和测试
6. 运行本地验证
7. 提交分支和 Commit
8. 创建 Draft PR
9. 处理 CI 失败和 Review 评论
10. 达到可合并状态后再进入主分支流程

## 本地验证入口

仓库统一使用 [Makefile](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/Makefile) 作为验证入口：

```bash
make format
make lint
make test
make build
make verify
```

当前仓库仍以文档和治理模板为主，因此如果还没有 `package.json`、`pyproject.toml`、`requirements*.txt`、`go.mod`，对应检查会被显式跳过，不会误报失败。

如果需要由 `MasterAgent` 做 Elder 入住首批 MVP 的红黄绿灯监督汇报，可使用：

```bash
make status-report
make dispatch-report
make status-watch
```

其中：

- `make status-report`
  生成一次监督报告，同时生成自动派工板，并写入 `reports/master-agent/elder_mvp_status.md`
- `make dispatch-report`
  快速刷新自动派工板与各 Agent 工单，不重复跑一次 `make verify`
- `make status-watch`
  每 300 秒刷新一次监督报告和派工单，适合项目例会或跟踪收口阶段使用

自动派工产物包括：

- `reports/master-agent/elder_mvp_dispatch.md`
  MasterAgent 总派工板
- `reports/master-agent/dispatch/*.md`
  各 Agent 的独立工作单，只描述各自职责范围内的待办、阻塞和回传对象

如果需要把这套监督/派工继续接入本地 Codex 自动执行，可使用：

```bash
make auto-drive
make auto-exec
make auto-watch
```

其中：

- `make auto-drive`
  只刷新监督/派工结果，并生成当前下一个可执行 Agent 的 Codex prompt，不直接调用 AI 执行
- `make auto-exec`
  调用本地 `codex exec` 自动执行一轮当前可执行 Agent
- `make auto-watch`
  每 300 秒自动执行一轮，形成“刷新状态 -> 选中 Agent -> 生成 prompt -> Codex 执行 -> 再次刷新状态”的闭环骨架
- 连续失败熔断
  自动执行器默认在同一 Agent 连续失败 3 次后打开熔断，30 分钟内不再继续重试该 Agent，避免无限打转

自动执行器产物包括：

- `reports/master-agent/executor/state.json`
  当前被选中的 Agent 与执行上下文
- `reports/master-agent/executor/next_agent_prompt.md`
  当前轮次发给本地 Codex 的执行 prompt
- `reports/master-agent/executor/prompts/*.md`
  历史 prompt
- `reports/master-agent/executor/runs/*/`
  每次 `codex exec` 的 stdout / stderr / last message 记录

如果需要清空熔断状态并重新放行 Agent，可使用：

```bash
make auto-reset-circuits
```

如果希望在 macOS 上把 `make auto-watch` 做成用户级常驻任务，可使用：

```bash
make launchd-install
make launchd-status
make launchd-uninstall
```

其中：

- `make launchd-install`
  安装并启动 `com.regionalhealth.masteragent.autowatch` LaunchAgent
- `make launchd-status`
  查看当前 LaunchAgent 的 `launchctl` 状态
- `make launchd-uninstall`
  停止并移除该 LaunchAgent

LaunchAgent 会把日志写到：

- `reports/master-agent/launchd/stdout.log`
- `reports/master-agent/launchd/stderr.log`

## 仓库目录结构

当前仓库建议按以下方式理解：

```text
RegionalHealthPlatform/
├── README.md
├── AGENTS.md
├── Makefile
├── .github/
│   ├── workflows/ci.yml
│   ├── pull_request_template.md
│   ├── CODEOWNERS
│   └── ISSUE_TEMPLATE/
├── apps/
│   ├── web/
│   ├── h5/
│   └── miniprogram/
├── docs/
│   ├── agents/
│   │   ├── MasterAgent.md
│   │   ├── FrontAgent.md
│   │   ├── GoAgent.md
│   │   ├── PythonAgent.md
│   │   ├── DevOpsAgent.md
│   │   └── TestAgent.md
│   ├── architecture/
│   │   ├── Arch.md
│   │   ├── 接口级详细设计.md
│   │   └── 部署拓扑图与数据库设计文档.md
│   ├── product/
│   │   ├── PRD.md
│   │   └── Modules.md
│   └── governance/
│       ├── AGENTS.md
│       ├── CodexTaskPrompt.md
│       └── repository-governance.md
├── services/
│   ├── go/
│   └── python/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── deploy/
├── scripts/
└── 需求输入文档/
```

目录职责可以简单理解为：

- 根目录：仓库入口和统一校验入口
- `apps/`：前端应用目录，面向 Web、H5、小程序等客户端实现
- `docs/agents/`：各 Agent 的职责、约束和技能边界
- `docs/architecture/`：总体架构和专项架构设计
- `docs/product/`：产品与模块定义
- `docs/governance/`：Agent 执行模板、任务 prompt、仓库治理规范
- `services/`：后端服务目录，按 Go 和 Python 技术栈分层承载
- `tests/`：跨服务、跨端的统一测试资产目录
- `deploy/`：部署、环境、IaC 和发布相关资产
- `scripts/`：工程脚本、辅助工具、初始化和迁移脚本
- `.github/`：GitHub 协作和自动化模板
- `需求输入文档/`：原始需求输入和外部资料

## 未来代码目录约定

为了让当前文档治理仓自然演进为可交付工程仓，建议后续代码按以下方式落位：

### `apps/`

- `apps/web/`
  后台管理端或运营端 Web 应用
- `apps/h5/`
  护理员、运营人员使用的移动 H5 或 App 内嵌页面
- `apps/miniprogram/`
  家属端微信小程序或轻应用端

### `services/`

- `services/go/`
  适合设备接入、实时链路、网关、高并发事件处理
- `services/python/`
  适合后台 API、规则引擎、分析报表、任务编排和集成适配

随着系统演进，可以继续在这两个目录下细分，例如：

```text
services/go/iot-gateway/
services/go/call-event-service/
services/python/elder-service/
services/python/rule-engine/
```

### `tests/`

- `tests/unit/`
  跨模块共享的单元测试资产或公共 fixture
- `tests/integration/`
  服务联调、接口、数据库、消息链路集成测试
- `tests/e2e/`
  端到端流程测试、关键业务冒烟测试

### `deploy/`

建议放置：

- Docker 或容器编排文件
- 环境部署说明
- Helm、Kustomize、Terraform 或其他 IaC 资产
- 发布和回滚脚本

### `scripts/`

建议放置：

- 项目初始化脚本
- 本地开发辅助脚本
- 数据准备、迁移、导入导出脚本
- CI/CD 辅助脚本

## 目录落地建议

当前这些目录已经预留，但仍为空骨架。后续落地时建议遵循：

1. 先在 `docs/` 中定义边界和约束，再在 `apps/`、`services/` 中实现
2. 前端和后端分别在各自目录内维护独立工程配置
3. 跨模块测试优先沉淀到 `tests/`
4. 部署与发布资产统一放到 `deploy/`
5. 临时脚本不要散落在根目录，统一收敛到 `scripts/`

## 推荐提交示例

建议统一使用 Conventional Commits，例如：

```text
docs: add master agent workflow and repository governance templates
```

```text
feat: add initial frontend module contract for elder profile management
```

```text
fix: align call event status transition rules in python service
```

```text
test: add regression cases for alert escalation workflow
```

建议分支命名示例：

```text
docs/agent-governance-bootstrap
feat/elder-profile-module
fix/call-event-timeout-rule
test/alert-regression-cases
```

## 从 Issue 到 PR 的标准操作示例

推荐流程如下：

1. 在 GitHub 中使用 Issue 模板创建 `Feature`、`Bug` 或 `Task`
2. 在 Issue 中写清背景、目标、范围、验收标准和推荐 Agent
3. 由 Master Agent 或对应专项 Agent 读取 Issue 上下文
4. 创建分支并实施最小改动
5. 更新测试或说明为何暂不补测
6. 在本地执行 `make verify`
7. 提交 Commit 并创建 Draft PR
8. 按 PR 模板填写摘要、验证、风险和回滚方案
9. 处理 GitHub Actions、review comments 和 requested changes
10. 确认通过后再转为 Ready for Review 或合并

一个简化示例如下：

```text
Issue:
[Task] 补充呼叫中心工作流状态定义

Branch:
feat/call-workflow-state-model

Commit:
feat: add call workflow state model and validation rules

Verification:
make verify

PR:
Draft PR -> CI 通过 -> review comments 修复 -> Ready for Review
```

## GitHub 协作约定

- 通过 PR 合并，不直接推送主分支
- 建议分支前缀：`feat/*`、`fix/*`、`refactor/*`、`docs/*`、`chore/*`
- PR 默认先开 Draft
- 所有变更都要写清楚验证方式、风险和回滚思路
- 主分支建议启用分支保护、状态检查和 review 要求

详细规则见：

- [repository-governance.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/governance/repository-governance.md)
- [.github/pull_request_template.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/.github/pull_request_template.md)

## Codex 使用方式

如果要把一个 GitHub Issue 或需求直接交给 Codex，建议：

1. 先在 Issue 中写清楚背景、目标、范围、验收标准
2. 标明推荐 Agent
3. 使用 [CodexTaskPrompt.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/governance/CodexTaskPrompt.md) 中的模板发起任务
4. 要求 Codex 在完成后说明修改文件、验证方式和剩余风险

适用的 GitHub 技能包括：

- `github:github`
- `github:yeet`
- `github:gh-fix-ci`
- `github:gh-address-comments`

## 可直接复制给 Codex 的任务示例

下面这段可以直接作为任务起点使用：

```text
你是区域康养平台仓库中的 Codex 执行智能体。

请先阅读并遵守：
- README.md
- docs/agents/MasterAgent.md
- AGENTS.md
- docs/architecture/Arch.md
- 与本任务最相关的专项文档

请完成任务：补充区域康养平台“呼叫中心工作台”模块的任务拆分与交付约束文档，并同步更新相关治理文档中的引用。

任务背景：
当前仓库已经建立了 Master Agent 和专项 Agent 规则，但针对呼叫中心工作台的任务拆分说明还不够清晰，需要补充外部协作者可理解的交付约束。

任务目标：
1. 梳理呼叫中心工作台相关的模块职责
2. 明确 FrontAgent、GoAgent、PythonAgent、TestAgent 的协作边界
3. 如有必要，补充 README 或相关文档引用

影响范围：
- README.md
- docs/architecture/Arch.md
- docs/agents/FrontAgent.md
- docs/agents/GoAgent.md
- docs/agents/PythonAgent.md
- docs/agents/TestAgent.md

验收标准：
1. 文档引用一致
2. 职责边界清晰
3. make verify 通过
4. 输出修改文件、验证结果和剩余风险

额外约束：
采用最小可行改动，不做无关重构。
```

## 当前状态

仓库当前已经具备以下治理基础：

- Agent 总控和专项规则文档
- PR 模板
- Issue 模板
- CODEOWNERS 模板
- GitHub Actions 最小 CI 模板
- `make verify` 统一验证入口
- `.gitignore` 通用忽略规则

## 后续建议

后续当真实工程代码落仓后，建议继续补齐：

- 前端工程脚手架与真实 lint、test、build 命令
- Python 服务骨架与真实 format、lint、test 流程
- Go 服务骨架与真实 fmt、vet、test、build 流程
- `apps/`、`services/`、`tests/` 的首批真实工程初始化
- GitHub Labels 初始化脚本
- 主分支保护规则的实际仓库配置
- 各目录对应的启动说明和开发手册
