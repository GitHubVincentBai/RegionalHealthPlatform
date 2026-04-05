SHELL := /bin/bash
GO_CACHE_DIR := $(CURDIR)/.cache/go-build
WEB_DIR := $(CURDIR)/apps/web
PYTHON_ELDER_DIR := $(CURDIR)/services/python/elder-service
GO_IOT_DIR := $(CURDIR)/services/go/iot-gateway
VERIFY_STATUS ?= 通过
VERIFY_SUMMARY ?= 本次已完成 make verify。

.PHONY: help format lint test build verify refresh-supervision check-docs check-frontend status-report dispatch-report status-watch auto-drive auto-exec auto-watch auto-reset-circuits launchd-install launchd-uninstall launchd-status prepare-python-elder-service init-elder-db format-web lint-web test-web build-web format-python-elder-service lint-python-elder-service test-python-elder-service build-python-elder-service test-elder-integration-smoke format-go-iot-gateway lint-go-iot-gateway test-go-iot-gateway build-go-iot-gateway

help:
	@echo "Available targets:"
	@echo "  make format       - run formatting tasks when a stack exists"
	@echo "  make lint         - run lint and static analysis tasks when a stack exists"
	@echo "  make test         - run tests when a stack exists"
	@echo "  make build        - run build validation when a stack exists"
	@echo "  make verify       - run docs, lint, test, and build checks"
	@echo "  make refresh-supervision - refresh MasterAgent supervision artifacts after a completed verify run"
	@echo "  make prepare-python-elder-service - bootstrap the elder-service verify virtualenv"
	@echo "  make init-elder-db - initialize elder-service PostgreSQL tables from SQL schema"
	@echo "  make test-elder-integration-smoke - run the first supported Elder MVP smoke asset under tests/integration"
	@echo "  make check-docs   - verify required governance documents exist"
	@echo "  make status-report - generate the MasterAgent elder MVP progress report"
	@echo "  make dispatch-report - generate the MasterAgent work dispatch board"
	@echo "  make status-watch - regenerate the MasterAgent report every 300 seconds"
	@echo "  make auto-drive   - refresh reports and generate the next Codex execution prompt"
	@echo "  make auto-exec    - run one eligible agent automatically through codex exec"
	@echo "  make auto-watch   - run the auto executor every 300 seconds"
	@echo "  make auto-reset-circuits - clear executor circuit breakers"
	@echo "  make launchd-install - install auto-watch as a macOS LaunchAgent"
	@echo "  make launchd-uninstall - remove the macOS LaunchAgent"
	@echo "  make launchd-status - inspect the macOS LaunchAgent status"

format:
	@echo "==> format"
	@$(MAKE) format-web
	@$(MAKE) format-python-elder-service
	@$(MAKE) format-go-iot-gateway

lint:
	@echo "==> lint"
	@$(MAKE) check-docs
	@$(MAKE) lint-web
	@$(MAKE) lint-python-elder-service
	@$(MAKE) lint-go-iot-gateway

test:
	@echo "==> test"
	@$(MAKE) test-web
	@$(MAKE) test-python-elder-service
	@$(MAKE) test-elder-integration-smoke
	@$(MAKE) test-go-iot-gateway

build:
	@echo "==> build"
	@$(MAKE) build-web
	@$(MAKE) build-python-elder-service
	@$(MAKE) build-go-iot-gateway

verify:
	@echo "==> verify"
	@status="通过"; \
	summary="本次已完成 make verify，已覆盖 elder-service HTTP 测试与已接入的 Elder 冒烟检查。"; \
	if ! $(MAKE) check-docs || ! $(MAKE) lint || ! $(MAKE) test || ! $(MAKE) build; then \
		status="失败"; \
		summary="本次 make verify 失败；监督报告已刷新，请继续根据失败阶段处理。"; \
	fi; \
	$(MAKE) refresh-supervision VERIFY_STATUS="$$status" VERIFY_SUMMARY="$$summary"; \
	if [ "$$status" != "通过" ]; then \
		exit 2; \
	fi; \
	echo "verify completed"

refresh-supervision:
	@echo "==> refresh-supervision"
	@python3 scripts/master_status_report.py --skip-verify --verify-status "$(VERIFY_STATUS)" --verify-summary "$(VERIFY_SUMMARY)"

check-docs:
	@echo "==> check-docs"
	@test -f AGENTS.md || (echo "Missing AGENTS.md" && exit 1)
	@test -f docs/agents/MasterAgent.md || (echo "Missing docs/agents/MasterAgent.md" && exit 1)
	@test -f docs/agents/Arch.md || (echo "Missing docs/agents/Arch.md" && exit 1)
	@test -f docs/agents/DevOpsAgent.md || (echo "Missing docs/agents/DevOpsAgent.md" && exit 1)
	@test -f docs/agents/FrontAgent.md || (echo "Missing docs/agents/FrontAgent.md" && exit 1)
	@test -f docs/agents/GoAgent.md || (echo "Missing docs/agents/GoAgent.md" && exit 1)
	@test -f docs/agents/PythonAgent.md || (echo "Missing docs/agents/PythonAgent.md" && exit 1)
	@test -f docs/agents/TestAgent.md || (echo "Missing docs/agents/TestAgent.md" && exit 1)
	@test -f docs/product/PRD.md || (echo "Missing docs/product/PRD.md" && exit 1)
	@test -f docs/product/Modules.md || (echo "Missing docs/product/Modules.md" && exit 1)
	@test -f docs/governance/AGENTS.md || (echo "Missing docs/governance/AGENTS.md" && exit 1)
	@test -f docs/governance/CodexTaskPrompt.md || (echo "Missing docs/governance/CodexTaskPrompt.md" && exit 1)
	@test -f docs/governance/repository-governance.md || (echo "Missing docs/governance/repository-governance.md" && exit 1)
	@test -d .github || (echo "Missing .github directory" && exit 1)
	@test -f .github/pull_request_template.md || (echo "Missing PR template" && exit 1)
	@test -f .github/CODEOWNERS || (echo "Missing CODEOWNERS" && exit 1)
	@test -f .github/workflows/ci.yml || (echo "Missing GitHub Actions workflow" && exit 1)
	@echo "documentation and governance files are present"

check-frontend:
	@echo "==> check-frontend"
	@if [ -f $(WEB_DIR)/package.json ]; then \
		echo "[frontend] apps/web detected"; \
	else \
		echo "[frontend] skipped: $(WEB_DIR)/package.json not found"; \
	fi

status-report:
	@echo "==> status-report"
	@python3 scripts/master_status_report.py

dispatch-report:
	@echo "==> dispatch-report"
	@python3 scripts/master_status_report.py --skip-verify

status-watch:
	@echo "==> status-watch"
	@python3 scripts/master_status_report.py --watch --interval 300

auto-drive:
	@echo "==> auto-drive"
	@python3 scripts/master_auto_executor.py

auto-exec:
	@echo "==> auto-exec"
	@python3 scripts/master_auto_executor.py --execute

auto-watch:
	@echo "==> auto-watch"
	@python3 scripts/master_auto_executor.py --watch --execute --interval 300

auto-reset-circuits:
	@echo "==> auto-reset-circuits"
	@python3 scripts/master_auto_executor.py --reset-all-circuits

launchd-install:
	@echo "==> launchd-install"
	@python3 scripts/manage_launch_agent.py --install

launchd-uninstall:
	@echo "==> launchd-uninstall"
	@python3 scripts/manage_launch_agent.py --uninstall

launchd-status:
	@echo "==> launchd-status"
	@python3 scripts/manage_launch_agent.py --status

format-web:
	@echo "==> format-web"
	@if [ -f $(WEB_DIR)/package.json ]; then \
		npm --prefix $(WEB_DIR) run format; \
	else \
		echo "[frontend] skipped: $(WEB_DIR)/package.json not found"; \
	fi

lint-web:
	@echo "==> lint-web"
	@if [ -f $(WEB_DIR)/package.json ]; then \
		npm --prefix $(WEB_DIR) run lint; \
	else \
		echo "[frontend] skipped: $(WEB_DIR)/package.json not found"; \
	fi

test-web:
	@echo "==> test-web"
	@if [ -f $(WEB_DIR)/package.json ]; then \
		npm --prefix $(WEB_DIR) run test; \
	else \
		echo "[frontend] skipped: $(WEB_DIR)/package.json not found"; \
	fi

build-web:
	@echo "==> build-web"
	@if [ -f $(WEB_DIR)/package.json ]; then \
		npm --prefix $(WEB_DIR) run build; \
	else \
		echo "[frontend] skipped: $(WEB_DIR)/package.json not found"; \
	fi

prepare-python-elder-service:
	@echo "==> prepare-python-elder-service"
	@if [ -f $(PYTHON_ELDER_DIR)/pyproject.toml ]; then \
		bash scripts/run_python_elder_checks.sh prepare; \
	else \
		echo "[python] skipped: $(PYTHON_ELDER_DIR)/pyproject.toml not found"; \
	fi

init-elder-db:
	@echo "==> init-elder-db"
	@if [ -f $(PYTHON_ELDER_DIR)/scripts/init_postgres_schema.sh ]; then \
		bash $(PYTHON_ELDER_DIR)/scripts/init_postgres_schema.sh; \
	else \
		echo "[python] skipped: $(PYTHON_ELDER_DIR)/scripts/init_postgres_schema.sh not found"; \
	fi

format-python-elder-service:
	@echo "==> format-python-elder-service"
	@if [ -f $(PYTHON_ELDER_DIR)/pyproject.toml ]; then \
		bash scripts/run_python_elder_checks.sh format; \
	else \
		echo "[python] skipped: $(PYTHON_ELDER_DIR)/pyproject.toml not found"; \
	fi

lint-python-elder-service:
	@echo "==> lint-python-elder-service"
	@if [ -f $(PYTHON_ELDER_DIR)/pyproject.toml ]; then \
		bash scripts/run_python_elder_checks.sh lint; \
	else \
		echo "[python] skipped: $(PYTHON_ELDER_DIR)/pyproject.toml not found"; \
	fi

test-python-elder-service:
	@echo "==> test-python-elder-service"
	@if [ -f $(PYTHON_ELDER_DIR)/pyproject.toml ]; then \
		bash scripts/run_python_elder_checks.sh test; \
	else \
		echo "[python] skipped: $(PYTHON_ELDER_DIR)/pyproject.toml not found"; \
	fi

test-elder-integration-smoke:
	@echo "==> test-elder-integration-smoke"
	@if [ -f $(PYTHON_ELDER_DIR)/pyproject.toml ]; then \
		bash scripts/run_python_elder_checks.sh smoke; \
	else \
		echo "[smoke] skipped: $(PYTHON_ELDER_DIR)/pyproject.toml not found"; \
	fi

build-python-elder-service:
	@echo "==> build-python-elder-service"
	@if [ -f $(PYTHON_ELDER_DIR)/pyproject.toml ]; then \
		bash scripts/run_python_elder_checks.sh build; \
	else \
		echo "[python] skipped: $(PYTHON_ELDER_DIR)/pyproject.toml not found"; \
	fi

format-go-iot-gateway:
	@echo "==> format-go-iot-gateway"
	@if [ -f $(GO_IOT_DIR)/go.mod ]; then \
		mkdir -p $(GO_CACHE_DIR); \
		(cd $(GO_IOT_DIR) && GOCACHE=$(GO_CACHE_DIR) gofmt -w $$(find . -name '*.go' -type f)); \
		echo "[go] iot-gateway format check completed"; \
	else \
		echo "[go] skipped: $(GO_IOT_DIR)/go.mod not found"; \
	fi

lint-go-iot-gateway:
	@echo "==> lint-go-iot-gateway"
	@if [ -f $(GO_IOT_DIR)/go.mod ]; then \
		mkdir -p $(GO_CACHE_DIR); \
		(cd $(GO_IOT_DIR) && GOCACHE=$(GO_CACHE_DIR) go vet ./...); \
	else \
		echo "[go] skipped: $(GO_IOT_DIR)/go.mod not found"; \
	fi

test-go-iot-gateway:
	@echo "==> test-go-iot-gateway"
	@if [ -f $(GO_IOT_DIR)/go.mod ]; then \
		mkdir -p $(GO_CACHE_DIR); \
		(cd $(GO_IOT_DIR) && GOCACHE=$(GO_CACHE_DIR) go test ./...); \
	else \
		echo "[go] skipped: $(GO_IOT_DIR)/go.mod not found"; \
	fi

build-go-iot-gateway:
	@echo "==> build-go-iot-gateway"
	@if [ -f $(GO_IOT_DIR)/go.mod ]; then \
		mkdir -p $(GO_CACHE_DIR); \
		(cd $(GO_IOT_DIR) && GOCACHE=$(GO_CACHE_DIR) go build ./...); \
		echo "[go] iot-gateway build completed"; \
	else \
		echo "[go] skipped: $(GO_IOT_DIR)/go.mod not found"; \
	fi
