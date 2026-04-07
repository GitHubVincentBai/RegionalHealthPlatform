# MasterAgent GitHub 闭环准备

- 生成时间: 2026-04-05 19:20:00 CST
- 基线验证: `make verify` 已通过
- 目标分支: `codex/elder-list-query`

## 建议排除项

以下内容不建议进入提交：

- `.codex-runtime/**`
- `~$*` Office 临时锁文件
- `__pycache__/`、`.venv/`、SQLite 状态文件等本地运行产物

## 建议分组提交

### Commit 1: FrontAgent

建议范围：

- `apps/web/README.md`
- `apps/web/package-lock.json`
- `apps/web/scripts/format.mjs`
- `apps/web/scripts/lint.mjs`
- `apps/web/scripts/test.mjs`
- `apps/web/src/App.vue`
- `apps/web/src/api/**`
- `apps/web/src/modules/elder/mock.js`
- `apps/web/src/modules/elder/mock.spec.mjs`
- `apps/web/src/navigation/**`
- `apps/web/src/styles.css`
- `apps/web/src/views/elder/**`

建议 commit message：

```text
feat(web): wire elder intake pages to elder-service adapter
```

### Commit 2: PythonAgent

建议范围：

- `services/python/elder-service/README.md`
- `services/python/elder-service/pyproject.toml`
- `services/python/elder-service/src/elder_service/application/service.py`
- `services/python/elder-service/src/elder_service/domain/models.py`
- `services/python/elder-service/src/elder_service/http/examples.py`
- `services/python/elder-service/src/elder_service/http/schemas.py`
- `services/python/elder-service/src/elder_service/http/server.py`
- `services/python/elder-service/src/elder_service/service.py`
- `services/python/elder-service/src/pytest.py`
- `services/python/elder-service/tests/test_http.py`
- `services/python/elder-service/tests/test_service.py`

建议 commit message：

```text
feat(python): complete elder intake api fields and tests
```

### Commit 3: TestAgent

建议范围：

- `tests/integration/elder_checkin_test_matrix.md`
- `tests/integration/elder_create_query_smoke.sh`
- `tests/integration/elder_mvp_smoke.sh`

如果希望把前端和 Python 的测试文件拆到这个 commit，也可以把以下文件并入本组：

- `apps/web/src/api/**/*.spec.mjs`
- `services/python/elder-service/tests/**`

建议 commit message：

```text
test(elder): add intake smoke coverage and regression matrix
```

### Commit 4: DevOpsAgent + MasterAgent

建议范围：

- `.github/workflows/ci.yml`
- `.gitignore`
- `Makefile`
- `README.md`
- `docs/governance/AGENTS.md`
- `docs/governance/repository-governance.md`
- `docs/product/Elder入住首批任务包.md`
- `scripts/manage_launch_agent.py`
- `scripts/master_auto_executor.py`
- `scripts/master_status_report.py`
- `scripts/run_python_elder_checks.sh`
- `reports/master-agent/elder_mvp_status.md`
- `reports/master-agent/elder_mvp_dispatch.md`
- `reports/master-agent/elder_mvp_delivery_closeout.md`
- `reports/master-agent/elder_mvp_git_prep.md`
- `reports/master-agent/dispatch/*.md`
- `reports/master-agent/executor/*.json`
- `reports/master-agent/executor/*.md`

建议 commit message：

```text
chore(agent): add elder mvp supervision and delivery automation
```

## 建议执行顺序

1. 先检查并决定是否正式删除已跟踪的 `~$...pptx` 临时文件
2. 按上述 4 组范围逐组 `git add`
3. 每组执行一次相关最小验证
4. 生成 4 个 commit
5. 推送当前分支
6. 创建 Draft PR

## Draft PR 标题建议

```text
[MVP] Complete elder archive and intake first-batch workflow
```

## Draft PR 描述建议

```text
## Summary
- complete elder archive create/list/detail MVP across web and Python service
- add elder intake fields for family contacts and stay info
- add smoke coverage and regression matrix for the first-batch workflow
- add MasterAgent supervision, dispatch, and auto-execution tooling

## Verification
- make verify
- make test-elder-integration-smoke

## Risks
- current automation and reports are repo-local and should remain excluded from runtime-only artifacts
- Office temporary files and local Codex runtime files must stay out of version control
```
