# Codex Task Prompt Template

Use this template when assigning a concrete task to Codex. Replace placeholders with project-specific details.

## Standard Prompt

```text
你是区域康养平台仓库中的 Codex 执行智能体。

请按以下规则完成任务：

1. 先阅读并遵守以下文档：
   - docs/agents/MasterAgent.md
   - AGENTS.md
   - 与任务相关的专项文档，如 docs/agents/Arch.md / docs/agents/FrontAgent.md / docs/agents/GoAgent.md / docs/agents/PythonAgent.md / docs/agents/DevOpsAgent.md / docs/agents/TestAgent.md
2. 先理解现有代码和文档，再实施修改。
3. 采用最小可行改动，不做无边界重构。
4. 如果改动影响行为、接口、规则或页面，补充或更新测试。
5. 在开始编码前先做“输入需求 md 分解正确性检查”，输出“需求点 -> 子任务 -> 负责人 -> 验收标准”映射。
6. 修改完成后做“任务匹配完成度检查”，输出“需求点 -> 代码文件/测试文件/验证结果”映射，明确是否有漏项或越界项。
7. 修改完成后执行相关验证，优先使用：
   - make lint
   - make test
   - make build
   - make verify
8. 如果检查失败，先修复再继续。
9. 输出时必须说明：
   - 任务理解
   - 输入需求 md 分解正确性检查结论
   - 代码任务与输入需求 md 匹配完成度结论
   - 实际修改了哪些文件
   - 做了哪些验证
   - 还剩哪些风险或假设

输入需求 md：
<请填写需求 markdown 文件路径，例如 docs/product/Elder入住首批任务包.md>

任务背景：
<请填写业务背景、Issue 或需求链接>

任务目标：
<请填写要实现的目标>

影响范围：
<请填写涉及的模块、端、服务、接口、数据或配置>

验收标准：
<请填写可测试的完成标准>

额外约束：
<请填写性能、安全、兼容性、上线窗口等约束；没有可写“无”>
```

## Quick Variants

### Frontend Task

```text
重点关注页面路由、组件拆分、状态建模、异常态和接口映射，遵守 docs/agents/FrontAgent.md。
```

### Go Task

```text
重点关注幂等、超时、并发安全、日志和可观测性，遵守 docs/agents/GoAgent.md。
```

### Python Task

```text
重点关注领域模型、规则边界、幂等、审计和测试覆盖，遵守 docs/agents/PythonAgent.md。
```

### DevOps Task

```text
重点关注仓库治理、CI/CD、环境配置、安全和回滚策略，遵守 docs/agents/DevOpsAgent.md。
```

### Test Task

```text
重点关注风险分析、测试矩阵、自动化补充和回归影响评估，遵守 docs/agents/TestAgent.md。
```

## Issue To Codex Mapping

When creating a GitHub issue for Codex-driven work, try to include:

- Business background
- Clear objective
- Explicit acceptance criteria
- A recommended agent
- Validation expectations
- Known dependencies or blockers
