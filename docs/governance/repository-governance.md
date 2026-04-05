# Repository Governance Standard

## Branch Protection

Recommended protection rules for `main`:

- Require pull requests before merging
- Require at least 1 approval for normal changes
- Require at least 2 approvals for architecture, security, CI/CD, or data model changes
- Dismiss stale approvals when new commits are pushed
- Require all conversations to be resolved before merging
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Restrict direct pushes to administrators only if your governance model allows it
- Disable force pushes
- Disable branch deletion

Recommended required checks:

- `Verify Repository`
- Any future stack-specific jobs added for frontend, python, go, security, or deployment gates

## Label Standard

Use a small, predictable label set.

### Type labels

- `type:feature`
- `type:bug`
- `type:task`
- `type:docs`
- `type:refactor`
- `type:test`
- `type:devops`

### Priority labels

- `priority:P0`
- `priority:P1`
- `priority:P2`
- `priority:P3`

### Status labels

- `status:triage`
- `status:ready`
- `status:in-progress`
- `status:blocked`
- `status:review`
- `status:done`

### Area labels

- `area:architecture`
- `area:frontend`
- `area:go`
- `area:python`
- `area:devops`
- `area:test`
- `area:data`

### Risk labels

- `risk:high`
- `risk:medium`
- `risk:low`

## PR Governance

- Use Draft PR first for AI-assisted development
- PR description must include summary, verification, risk, and rollback notes
- Behavior changes require test updates or an explicit reason why tests were not added
- Cross-cutting changes should request the relevant code owners
- CI failures must be fixed before converting to ready for review

## Agent Workflow Guidance

- Use `docs/agents/MasterAgent.md` for cross-functional requests
- Route implementation work to the specialized agent documents
- Use GitHub issue templates to provide enough context for Codex and human reviewers
- Keep issue acceptance criteria concrete and testable

## Repository Skeleton Notes

- `apps/web` is the current frontend bootstrap workspace
- `services/python/elder-service` is the current Python service bootstrap workspace
- `services/go/iot-gateway` is the current Go service bootstrap workspace
- `make verify` is expected to validate the active skeletons without requiring future code to exist yet
- GitHub Actions should use the same conditional skeleton checks as the local Makefile
- The Python verification path should install `elder-service` into `services/python/elder-service/.venv` with its `test` extra, reuse already-synced packages in offline runs when possible, verify `fastapi/httpx/uvicorn` imports there, and run the elder-service service tests, HTTP tests, and the first supported Elder MVP smoke asset discovered under `tests/integration/`
- CI should publish the generated `reports/master-agent/*` dispatch artifacts so MasterAgent supervision remains visible after each unified verification run
