# Regional Health Platform Agent Execution Template

## Purpose

This file defines the operational contract for AI agents working in this repository. It should be read together with:

- `docs/agents/MasterAgent.md`
- `docs/architecture/Arch.md`
- `docs/agents/DevOpsAgent.md`
- `docs/agents/FrontAgent.md`
- `docs/agents/GoAgent.md`
- `docs/agents/PythonAgent.md`
- `docs/agents/TestAgent.md`

The goal is to ensure every agent follows the same execution loop, quality gates, and GitHub delivery process.

## Default Execution Loop

Every agent must follow this sequence:

1. Read the relevant documents and existing files first.
2. Clarify the task scope, impacted modules, and acceptance criteria.
3. Make the smallest useful change that satisfies the task.
4. Update or add tests when the change affects behavior.
5. Run the relevant local checks.
6. Fix failures before proposing submission.
7. Summarize what changed, how it was verified, and what risks remain.
8. Submit through branch, commit, PR, CI, and review feedback loops.

## Agent Routing

Use the most suitable specialized agent first:

- Architecture and boundaries: `docs/architecture/Arch.md`
- Frontend and client UX: `docs/agents/FrontAgent.md`
- Go services and realtime pipelines: `docs/agents/GoAgent.md`
- Python services, rules, and data processing: `docs/agents/PythonAgent.md`
- DevOps, CI/CD, repo governance, and delivery: `docs/agents/DevOpsAgent.md`
- Testing, coverage, regression, and quality gates: `docs/agents/TestAgent.md`

Use `docs/agents/MasterAgent.md` when the task crosses multiple areas or requires coordination.

## Required Checks

Agents should prefer the unified Make targets below:

- `make format`
- `make lint`
- `make test`
- `make build`
- `make verify`

If a stack is not yet present in the repository, the target may skip it explicitly. Skips must be transparent, not hidden.

## Current Skeleton Targets

The repository now has three bootstrap workspaces with explicit per-stack targets:

- `format-web`, `lint-web`, `test-web`, `build-web`
- `format-python-elder-service`, `lint-python-elder-service`, `test-python-elder-service`, `build-python-elder-service`
- `format-go-iot-gateway`, `lint-go-iot-gateway`, `test-go-iot-gateway`, `build-go-iot-gateway`

Use these targets when working on a single stack. Use `make verify` when you need the whole repository checked end to end.

## Submission Rules

- Never commit directly to the protected main branch.
- Prefer branch names like `feat/*`, `fix/*`, `refactor/*`, `docs/*`, `chore/*`.
- Prefer Conventional Commits.
- Do not submit code that has not passed relevant local validation.
- Open a Draft PR first unless the change is already fully reviewed and stable.

## GitHub Skills

Preferred GitHub workflows for agents:

- `github:github` for repo, PR, and issue context
- `github:yeet` for commit, push, and draft PR creation
- `github:gh-fix-ci` for failed Actions checks
- `github:gh-address-comments` for review comments and requested changes

## Safety Rules

- Never invent secrets, configs, APIs, or infrastructure that are not grounded in the repo or task.
- Never store tokens, passwords, or private keys in tracked files.
- Never claim a release is safe without verification evidence.
- Escalate cross-cutting risks to the master agent instead of silently working around them.

## Output Template

When completing a task, agents should report:

1. Task understanding
2. Files changed
3. Verification performed
4. Remaining risks or assumptions
