# Regional Health Platform Agent Execution Template

## Purpose

This file defines the operational contract for AI agents working in this repository. It should be read together with:

- `docs/agents/MasterAgent.md`
- `docs/agents/Arch.md`
- `docs/agents/DevOpsAgent.md`
- `docs/agents/FrontAgent.md`
- `docs/agents/GoAgent.md`
- `docs/agents/PythonAgent.md`
- `docs/agents/TestAgent.md`

The goal is to ensure every agent follows the same execution loop, quality gates, and GitHub delivery process.

## Default Execution Loop

Every agent must follow this sequence:

1. Read the relevant documents and existing files first.
2. Clarify the task scope, impacted modules, acceptance criteria, and requirement source markdown.
3. For requirement-driven work, decompose the input requirement markdown into executable task items before coding.
4. Make the smallest useful change that satisfies the task.
5. Update or add tests when the change affects behavior.
6. Run the relevant local checks.
7. Fix failures before proposing submission.
8. Summarize requirement-to-task decomposition and requirement-to-code/test traceability.
9. Summarize what changed, how it was verified, and what risks remain.
10. Submit through branch, commit, PR, CI, and review feedback loops.

## Requirement Traceability Gate

For AI automated coding, Master Agent must enforce two mandatory checks:

1. Decomposition correctness check
   - Input requirement markdown is decomposed into complete, non-overlapping executable task items.
   - Each task item has owner, boundary, and acceptance criteria.
2. Task-match completion check
   - Implemented code/tasks map back to requirement items one by one.
   - No missing required item, and no out-of-scope implementation without explicit approval.
   - Each completed requirement item has verification evidence.

If either check fails, the task must be routed back for rework instead of being marked complete.

## Agent Routing

Use the most suitable specialized agent first:

- Architecture and boundaries: `docs/agents/Arch.md`
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
- `make refresh-supervision`

If a stack is not yet present in the repository, the target may skip it explicitly. Skips must be transparent, not hidden.

## Current Skeleton Targets

The repository now has three bootstrap workspaces with explicit per-stack targets:

- `format-web`, `lint-web`, `test-web`, `build-web`
- `format-python-elder-service`, `lint-python-elder-service`, `test-python-elder-service`, `build-python-elder-service`
- `format-go-iot-gateway`, `lint-go-iot-gateway`, `test-go-iot-gateway`, `build-go-iot-gateway`
- `test-elder-integration-smoke`

Use these targets when working on a single stack. Use `make verify` when you need the whole repository checked end to end.

For `services/python/elder-service`, the repository-level checks bootstrap an isolated service-local virtualenv at `services/python/elder-service/.venv` and install dependencies from `pyproject.toml` with the `test` extra before running the service tests, HTTP tests, and the first supported Elder MVP smoke asset found under `tests/integration/` (`elder_mvp_smoke.py`, `elder_mvp_smoke.sh`, then `elder_create_query_smoke.sh`). The current shared smoke bridge is `tests/integration/elder_mvp_smoke.sh`, which delegates to the concrete P0 flow asset. The bootstrap script should prefer `python3.11` when available so local verification stays close to CI, fall back to the local default `python3` only when `3.11` is unavailable, and recreate `.venv` when the interpreter changes or the environment was created with system site packages. It should reuse already-synced packages from that `.venv` when possible and only fall back to `pip install --no-build-isolation -e ...[test]` when the required runtime imports (`fastapi/httpx/uvicorn`) are missing. `make verify` and CI must use that isolated environment consistently instead of falling back to host Python packages, so missing runtime dependencies such as `fastapi` are caught in the unified gate.

`lint-python-elder-service` should stay a real lint/import gate and must not silently rerun the full test suite. `test-python-elder-service` remains the only repository-level target that executes the elder-service unit and HTTP tests.

`make verify` should refresh the MasterAgent dispatch artifacts through `make refresh-supervision` even when one of the aggregated stages fails, so local automation keeps a current supervision snapshot alongside the latest validation result. CI should still call `make refresh-supervision` in an `always()` step after `make verify`, so failed runs also publish an updated status and dispatch board for MasterAgent follow-up.

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
2. Requirement decomposition check result
3. Requirement-to-code/test match result
4. Files changed
5. Verification performed
6. Remaining risks or assumptions
