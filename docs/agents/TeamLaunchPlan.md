# Multi-Agent Team Launch Plan

## Purpose

This document is the initial operating board for running a multi-agent development team in the Regional Health Platform repository.

It complements:

- `docs/agents/MasterAgent.md`
- `docs/governance/AGENTS.md`
- `docs/governance/CodexTaskPrompt.md`

## Team Topology

### Master Session

- Role: `MasterAgent`
- Responsibility:
  - break down work
  - assign ownership
  - watch dependency boundaries
  - collect progress and risks
  - run final validation and merge readiness checks

### Specialist Sessions

- `FrontAgent`
  - Primary write scope: `apps/**`
- `PythonAgent`
  - Primary write scope: `services/python/**`
- `GoAgent`
  - Primary write scope: `services/go/**`
- `TestAgent`
  - Primary write scope: `tests/**`
  - Secondary collaborative scope: test files inside `apps/**` and `services/**`
- `DevOpsAgent`
  - Primary write scope: `.github/**`, `deploy/**`, `scripts/**`, `Makefile`, `docs/governance/**`
- `ArchAgent`
  - Primary write scope: `docs/architecture/**`
  - Cross-cutting responsibility: service boundaries and integration contracts

## First Delivery Wave

The current bootstrap wave is split into these work packets:

1. Frontend bootstrap refinement
   - owner: `FrontAgent`
   - scope: `apps/web/**`
   - expected result: dashboard-style skeleton and clearer modular structure

2. Python elder service bootstrap refinement
   - owner: `PythonAgent`
   - scope: `services/python/elder-service/**`
   - expected result: cleaner application structure and a minimal HTTP API

3. Go IoT gateway bootstrap refinement
   - owner: `GoAgent`
   - scope: `services/go/iot-gateway/**`
   - expected result: health endpoint, register device flow, and tests

4. DevOps and repository validation refinement
   - owner: `DevOpsAgent`
   - scope: `.github/**`, `Makefile`, `docs/governance/**`
   - expected result: validation flow aligned with the new code skeleton

## Coordination Rules

- Each session must stay within its owned write scope unless the master explicitly reassigns ownership.
- Shared contracts must be documented before large behavior changes.
- When a worker depends on another area, it should report the dependency rather than editing another worker's files.
- The master session is responsible for integration, conflict handling, and final acceptance.

## Reporting Format

Each specialist session should report:

1. Scope completed
2. Files changed
3. Verification run
4. Remaining assumptions or blockers

## Validation Gate

No work is considered integration-ready until:

- local checks pass for the owned scope
- `make verify` passes at the repository level
- any cross-cutting assumptions are recorded

## Near-Term Next Step

After the first delivery wave, the next recommended wave is:

1. initialize a real Vue frontend under `apps/web`
2. upgrade elder-service to FastAPI
3. add configuration and HTTP server structure to iot-gateway
4. expand `tests/` into shared integration and end-to-end suites
