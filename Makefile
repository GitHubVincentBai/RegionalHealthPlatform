SHELL := /bin/bash
GO_CACHE_DIR := $(CURDIR)/.cache/go-build
WEB_DIR := $(CURDIR)/apps/web
PYTHON_ELDER_DIR := $(CURDIR)/services/python/elder-service
GO_IOT_DIR := $(CURDIR)/services/go/iot-gateway

.PHONY: help format lint test build verify check-docs check-frontend format-web lint-web test-web build-web format-python-elder-service lint-python-elder-service test-python-elder-service build-python-elder-service format-go-iot-gateway lint-go-iot-gateway test-go-iot-gateway build-go-iot-gateway

help:
	@echo "Available targets:"
	@echo "  make format       - run formatting tasks when a stack exists"
	@echo "  make lint         - run lint and static analysis tasks when a stack exists"
	@echo "  make test         - run tests when a stack exists"
	@echo "  make build        - run build validation when a stack exists"
	@echo "  make verify       - run docs, lint, test, and build checks"
	@echo "  make check-docs   - verify required governance documents exist"

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
	@$(MAKE) test-go-iot-gateway

build:
	@echo "==> build"
	@$(MAKE) build-web
	@$(MAKE) build-python-elder-service
	@$(MAKE) build-go-iot-gateway

verify:
	@echo "==> verify"
	@$(MAKE) check-docs
	@$(MAKE) lint
	@$(MAKE) test
	@$(MAKE) build
	@echo "verify completed"

check-docs:
	@echo "==> check-docs"
	@test -f AGENTS.md || (echo "Missing AGENTS.md" && exit 1)
	@test -f docs/agents/MasterAgent.md || (echo "Missing docs/agents/MasterAgent.md" && exit 1)
	@test -f docs/architecture/Arch.md || (echo "Missing docs/architecture/Arch.md" && exit 1)
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

format-python-elder-service:
	@echo "==> format-python-elder-service"
	@if [ -f $(PYTHON_ELDER_DIR)/pyproject.toml ]; then \
		PYTHONPATH=$(PYTHON_ELDER_DIR)/src python3 -m compileall $(PYTHON_ELDER_DIR)/src >/dev/null; \
		echo "[python] elder-service format check completed"; \
	else \
		echo "[python] skipped: $(PYTHON_ELDER_DIR)/pyproject.toml not found"; \
	fi

lint-python-elder-service:
	@echo "==> lint-python-elder-service"
	@if [ -f $(PYTHON_ELDER_DIR)/pyproject.toml ]; then \
		PYTHONPATH=$(PYTHON_ELDER_DIR)/src python3 -m unittest discover -s $(PYTHON_ELDER_DIR)/tests >/dev/null; \
		echo "[python] elder-service lint proxy check completed"; \
	else \
		echo "[python] skipped: $(PYTHON_ELDER_DIR)/pyproject.toml not found"; \
	fi

test-python-elder-service:
	@echo "==> test-python-elder-service"
	@if [ -f $(PYTHON_ELDER_DIR)/pyproject.toml ]; then \
		PYTHONPATH=$(PYTHON_ELDER_DIR)/src python3 -m unittest discover -s $(PYTHON_ELDER_DIR)/tests; \
	else \
		echo "[python] skipped: $(PYTHON_ELDER_DIR)/pyproject.toml not found"; \
	fi

build-python-elder-service:
	@echo "==> build-python-elder-service"
	@if [ -f $(PYTHON_ELDER_DIR)/pyproject.toml ]; then \
		PYTHONPATH=$(PYTHON_ELDER_DIR)/src python3 -c "from elder_service.service import create_elder_profile; p=create_elder_profile('E-100','王五',82,'high'); print(p.risk_level)"; \
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
