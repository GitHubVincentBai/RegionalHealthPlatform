#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
TASK_PACKAGE = REPO_ROOT / "docs/product/Elder入住首批任务包.md"
DEFAULT_OUTPUT = REPO_ROOT / "reports/master-agent/elder_mvp_status.md"
DEFAULT_DISPATCH_OUTPUT = REPO_ROOT / "reports/master-agent/elder_mvp_dispatch.md"
DEFAULT_DISPATCH_DIR = REPO_ROOT / "reports/master-agent/dispatch"
EXECUTOR_RUNS_DIR = REPO_ROOT / "reports/master-agent/executor/runs"
EXECUTOR_STATE_FILE = REPO_ROOT / "reports/master-agent/executor/state.json"
SUPPORTED_SMOKE_ASSETS = [
    "tests/integration/elder_mvp_smoke.py",
    "tests/integration/elder_mvp_smoke.sh",
    "tests/integration/elder_create_query_smoke.sh",
]


@dataclass(slots=True)
class AgentReport:
    name: str
    task: str
    status: str
    completed: str
    risk: str
    next_action: str


@dataclass(slots=True)
class WorkOrder:
    agent_name: str
    dispatch_state: str
    write_scope: str
    dependencies: list[str]
    objective: str
    todo_items: list[str]
    blockers: list[str]
    handoff_to: list[str]


@dataclass(slots=True)
class AgentExecutionStatus:
    agent_name: str
    status: str
    detail: str
    latest_run_dir: str | None
    latest_run_at: str | None


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def file_exists(path: str) -> bool:
    return (REPO_ROOT / path).exists()


def file_contains(path: str, snippets: list[str]) -> bool:
    content = read_text(REPO_ROOT / path)
    return all(snippet in content for snippet in snippets)


def file_contains_any(path: str, snippets: list[str]) -> bool:
    content = read_text(REPO_ROOT / path)
    return any(snippet in content for snippet in snippets)


def run_command(args: list[str]) -> tuple[int, str]:
    completed = subprocess.run(
        args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = (completed.stdout + completed.stderr).strip()
    return completed.returncode, output


def collect_execution_statuses() -> dict[str, AgentExecutionStatus]:
    state = read_json(EXECUTOR_STATE_FILE)
    selected_agents = state.get("selected_agents")
    if not isinstance(selected_agents, list):
        selected_agent = state.get("selected_agent")
        selected_agents = [selected_agent] if isinstance(selected_agent, str) and selected_agent else []

    latest_dirs: dict[str, tuple[str, Path]] = {}
    if EXECUTOR_RUNS_DIR.exists():
        for run_dir in EXECUTOR_RUNS_DIR.iterdir():
            if not run_dir.is_dir():
                continue
            name = run_dir.name
            if "-" not in name:
                continue
            try:
                timestamp_part, agent_name = name.rsplit("-", 1)
                dt.datetime.strptime(timestamp_part, "%Y%m%d-%H%M%S")
            except ValueError:
                continue
            current = latest_dirs.get(agent_name)
            if current is None or timestamp_part > current[0]:
                latest_dirs[agent_name] = (timestamp_part, run_dir)

    statuses: dict[str, AgentExecutionStatus] = {}
    for agent_name, (timestamp_part, run_dir) in latest_dirs.items():
        last_message = run_dir / "last_message.txt"
        stdout_log = run_dir / "stdout.log"
        stderr_log = run_dir / "stderr.log"
        latest_run_at = timestamp_part
        latest_run_dir = str(run_dir)

        if last_message.exists():
            statuses[agent_name] = AgentExecutionStatus(
                agent_name=agent_name,
                status="执行成功",
                detail="最近一轮 Codex 执行有有效回传结果。",
                latest_run_dir=latest_run_dir,
                latest_run_at=latest_run_at,
            )
            continue

        if agent_name in selected_agents and not stdout_log.exists() and not stderr_log.exists():
            statuses[agent_name] = AgentExecutionStatus(
                agent_name=agent_name,
                status="执行中",
                detail="已被选中且当前轮次日志尚未落完，视为仍在执行。",
                latest_run_dir=latest_run_dir,
                latest_run_at=latest_run_at,
            )
            continue

        if stdout_log.exists() or stderr_log.exists():
            statuses[agent_name] = AgentExecutionStatus(
                agent_name=agent_name,
                status="执行失败",
                detail="最近一轮 Codex 执行未产出有效回传结果。",
                latest_run_dir=latest_run_dir,
                latest_run_at=latest_run_at,
            )
            continue

        statuses[agent_name] = AgentExecutionStatus(
            agent_name=agent_name,
            status="已派工",
            detail="已生成运行目录，但尚未看到明确执行结果。",
            latest_run_dir=latest_run_dir,
            latest_run_at=latest_run_at,
        )

    return statuses


def git_branch() -> str:
    code, output = run_command(["git", "branch", "--show-current"])
    if code != 0:
        return "unknown"
    return output or "detached"


def git_status_lines() -> list[str]:
    code, output = run_command(["git", "status", "--short"])
    if code != 0 or not output:
        return []
    return [line for line in output.splitlines() if line.strip()]


def evaluate_verify(run_verify: bool) -> tuple[str, str]:
    if not run_verify:
        return "未执行", "本次巡检未运行 `make verify`。"

    code, output = run_command(["make", "verify"])
    summary = output.splitlines()[-1] if output else "未获取到输出"
    if code == 0:
        return "通过", summary
    return "失败", summary


def evaluate_agents(verify_status: str) -> list[AgentReport]:
    makefile_content = read_text(REPO_ROOT / "Makefile")
    ci_content = read_text(REPO_ROOT / ".github/workflows/ci.yml")
    python_check_script = read_text(REPO_ROOT / "scripts/run_python_elder_checks.sh")

    task_package_content = read_text(TASK_PACKAGE)
    field_catalog_reference_needed = "功能页面字段集清单.md" in task_package_content
    field_catalog_product_ready = file_exists("docs/product/功能页面字段集清单.md")
    arch_ready = (
        file_exists("docs/agents/Arch.md")
        and file_contains(
            "docs/product/Elder入住首批任务包.md",
            ["家属关系", "入住信息", "房间与床位关联", "风险等级"],
        )
        and (not field_catalog_reference_needed or field_catalog_product_ready)
    )

    python_ready = all(
        [
            file_contains(
                "services/python/elder-service/src/elder_service/domain/models.py",
                ["class FamilyContact", "class StayInfo", "class ElderProfile"],
            ),
            file_contains(
                "services/python/elder-service/src/elder_service/http/server.py",
                ['@app.get("/elders"', '@app.post(', '"/elders/{elder_id}"'],
            ),
            file_contains(
                "services/python/elder-service/tests/test_http.py",
                ["family_contacts", "stay_info", "test_create_list_and_fetch_profile"],
            ),
        ]
    )
    python_dependency_declared = file_contains(
        "services/python/elder-service/pyproject.toml",
        ['"fastapi>=0.115,<1"', '"uvicorn>=0.30,<1"'],
    )
    python_http_tests_require_fastapi = file_contains(
        "services/python/elder-service/tests/test_http.py",
        ["from fastapi.testclient import TestClient"],
    )
    python_make_targets_aligned = all(
        [
            "prepare-python-elder-service" in makefile_content,
            "test-python-elder-service" in makefile_content,
            "test-elder-integration-smoke" in makefile_content,
            "run_python_elder_checks.sh test" in makefile_content,
            "run_python_elder_checks.sh smoke" in makefile_content,
        ]
    )
    python_verification_bootstrapped = (
        python_make_targets_aligned
        and ".venv" in python_check_script
        and "pick_python_bin" in python_check_script
        and "python3.11" in python_check_script
        and 'pip install --disable-pip-version-check --no-build-isolation -e ".[test]"' in python_check_script
        and "reusing elder-service dependencies" in python_check_script
        and "dependency stamp matches, but runtime imports are missing" in python_check_script
        and "import fastapi, httpx, uvicorn" in python_check_script
        and "tests.test_service tests.test_http" in python_check_script
        and "ensure_shell_smoke_uses_venv_python" in python_check_script
        and "dependency sync unavailable; falling back to host runtime packages" not in python_check_script
        and "--system-site-packages" not in python_check_script
    )
    python_ci_aligned = all(
        [
            'python-version: "3.11"' in ci_content,
            "run: make verify" in ci_content,
            "Refresh MasterAgent supervision reports" in ci_content,
            "if: always()" in ci_content,
        ]
    )
    python_env_gap = python_dependency_declared and python_http_tests_require_fastapi and not (
        python_verification_bootstrapped and python_ci_aligned
    )

    front_pages_ready = all(
        [
            file_exists("apps/web/src/views/elder/ElderArchivePage.vue"),
            file_exists("apps/web/src/views/elder/ElderDetailPage.vue"),
            file_exists("apps/web/src/views/elder/ElderIntakePage.vue"),
            file_contains(
                "apps/web/src/navigation/appViews.js",
                ["elder-list", "elder-intake", "长者入住办理"],
            ),
        ]
    )
    front_adapter_ready = (
        file_exists("apps/web/src/api/adapters/elder-service/index.js")
        or file_exists("apps/web/src/modules/elder/api/client.js")
        or file_exists("apps/web/src/services")
    )
    front_api_module_ready = all(
        [
            file_exists("apps/web/src/api/adapters/elder-service/httpClient.js"),
            file_exists("apps/web/src/api/adapters/elder-service/mapper.js"),
            file_exists("apps/web/src/api/adapters/elder-service/archiveService.js"),
            file_exists("apps/web/src/api/adapters/elder-service/httpClient.spec.mjs"),
            file_exists("apps/web/src/api/adapters/elder-service/mapper.spec.mjs"),
            file_exists("apps/web/src/api/adapters/elder-service/archiveService.spec.mjs"),
            file_exists("apps/web/src/api/adapters/elder-service/flow.spec.mjs"),
        ]
    )
    front_ready = front_pages_ready and front_adapter_ready and front_api_module_ready

    test_plan_ready = file_exists("tests/integration/elder_checkin_test_matrix.md")
    frontend_tests_ready = all(
        [
            file_contains(
                "apps/web/scripts/test.mjs",
                ["elderArchiveVue", "elderIntakeVue", "createElderArchiveService"],
            ),
            file_contains_any(
                "apps/web/scripts/test.mjs",
                ["flow.spec.mjs", "elder archive flow"],
            ),
        ]
    )
    backend_tests_ready = file_contains(
        "services/python/elder-service/tests/test_http.py",
        ["test_list_endpoint_supports_filters_and_pagination", "test_create_list_and_fetch_profile"],
    )
    integration_smoke_ready = any(file_exists(path) for path in SUPPORTED_SMOKE_ASSETS)
    integration_smoke_hooked = "test-elder-integration-smoke" in makefile_content and (
        "run_python_elder_checks.sh smoke" in ci_content or "make verify" in ci_content
    )

    devops_ready = all(
        [
            file_exists(".github/workflows/ci.yml"),
            file_exists("Makefile"),
            verify_status == "通过",
        ]
    )

    go_ready = all(
        [
            file_exists("services/go/iot-gateway/go.mod"),
            file_exists("services/go/iot-gateway/internal/gateway/server.go"),
            file_exists("services/go/iot-gateway/internal/gateway/server_test.go"),
        ]
    )

    reports = [
        AgentReport(
            name="ArchAgent",
            task="架构与数据约束校验",
            status="已完成" if arch_ready else "风险",
            completed="已定义长者、家属、入住、床位关联的首批边界，并对齐任务包引用字段清单。"
            if arch_ready
            else "任务包或架构边界文档不完整，或任务包引用的字段清单路径未对齐。",
            risk="后续若扩展合同、费用、护理计划，仍需追加状态机与边界约束。"
            if arch_ready
            else (
                "任务包已引用 `docs/product/功能页面字段集清单.md`，当前路径尚未满足。"
                if field_catalog_reference_needed and not field_catalog_product_ready
                else "缺少架构边界依据，后续实现容易越界。"
            ),
            next_action="保持审阅状态，等待二期扩展再细化。"
            if arch_ready
            else (
                "先补齐 `docs/product/功能页面字段集清单.md`（可由架构字段清单映射产出），再回传 MasterAgent。"
                if field_catalog_reference_needed and not field_catalog_product_ready
                else "补齐架构约束文档与字段边界。"
            ),
        ),
        AgentReport(
            name="PythonAgent",
            task="长者档案领域模型与 API",
            status="进行中" if python_env_gap else ("已完成" if python_ready else "进行中"),
            completed="已具备 create/list/get API、家属关系、入住信息和基础自动化测试。"
            if python_ready
            else "FastAPI 骨架已在，但 MVP 字段模型、接口或测试尚未完全对齐任务包。",
            risk="仓库级验证入口没有为 FastAPI 测试准备依赖环境，`make verify` 仍可能卡在 Python HTTP 测试。"
            if python_env_gap
            else ("后续仍需与前端联调，验证真实交互链路。" if python_ready else "后端闭环不足会阻塞前端联调和 MVP 验收。"),
            next_action="补齐 Python 服务依赖声明与测试运行假设，配合 DevOpsAgent 修复验证环境。"
            if python_env_gap
            else ("配合 FrontAgent 做最小创建/查询联调。" if python_ready else "继续补齐 family/stay/room/bed 模型、接口校验和测试。"),
        ),
        AgentReport(
            name="FrontAgent",
            task="长者档案前端列表与详情骨架",
            status="已完成" if front_ready else ("进行中" if front_pages_ready else "风险"),
            completed="列表页、详情页、入住办理页、API adapter 和调用层测试已具备。"
            if front_ready
            else ("列表页、详情页、入住办理页和导航入口已具备。" if front_pages_ready else "MVP 页面骨架尚未齐备。"),
            risk="仓库级验证仍受 Python 依赖环境影响，前端改动的全仓门禁尚未完全绿灯。"
            if front_ready
            else ("任务包要求为真实 API 预留适配层，当前仓库还未看到明确的 API adapter 目录。" if front_pages_ready and not front_adapter_ready else "主要页面缺失，无法进入联调。"),
            next_action="回传给 TestAgent 和 MasterAgent，进入后续联调与冒烟测试阶段。"
            if front_ready
            else ("补齐 API adapter 占位，并联调 elder-service。" if front_pages_ready and not front_adapter_ready else "继续完成列表、详情、创建页骨架。"),
        ),
        AgentReport(
            name="TestAgent",
            task="测试矩阵与回归策略",
            status="已完成"
            if test_plan_ready and integration_smoke_ready and frontend_tests_ready and backend_tests_ready
            else ("进行中" if test_plan_ready else "风险"),
            completed="已产出 Elder 入住首批测试矩阵；前后端也已有基础自动化测试。"
            if test_plan_ready
            else "测试矩阵文档尚未落地。",
            risk=""
            if test_plan_ready and integration_smoke_ready and frontend_tests_ready and backend_tests_ready
            else (
                "文档不等于执行结果，当前还缺少明确的跨前后端 MVP 联调冒烟资产。"
                if test_plan_ready and not integration_smoke_ready
                else ("前端或后端基础自动化不足。" if test_plan_ready else "没有测试矩阵会导致验收口径不清。")
            ),
            next_action="回传给 DevOpsAgent 和 MasterAgent，继续纳入周期巡检。"
            if test_plan_ready and integration_smoke_ready and frontend_tests_ready and backend_tests_ready
            else ("把 P0 用例落成一条真实联调冒烟测试，并纳入周期巡检。" if test_plan_ready else "先补测试矩阵，再补自动化。"),
        ),
        AgentReport(
            name="DevOpsAgent",
            task="CI/CD 与治理模板适配",
            status="进行中"
            if python_env_gap or (integration_smoke_ready and not integration_smoke_hooked)
            else ("已完成" if devops_ready else "进行中"),
            completed="统一 Make 校验入口和 CI 模板可用，仓库级验证可运行。"
            if devops_ready
            else "CI 或统一校验入口还未达到稳定状态。",
            risk="Python HTTP 测试依赖还没有被仓库级验证环境正确准备，导致 `make verify` 无法稳定代表真实状态。"
            if python_env_gap
            else (
                "TestAgent 已提供可执行冒烟资产，但尚未接入 Makefile / CI 的统一巡检链路。"
                if integration_smoke_ready and not integration_smoke_hooked
                else ("随着联调测试引入，CI 仍要继续补强。" if devops_ready else "没有稳定治理入口会让 MasterAgent 无法持续监督。")
            ),
            next_action="修复 Python 依赖准备和验证入口，让 `make verify` 能真实覆盖 elder-service HTTP 测试。"
            if python_env_gap
            else (
                "把真实冒烟测试接入 `Makefile` 与 CI。"
                if integration_smoke_ready and not integration_smoke_hooked
                else ("配合接入后续联调冒烟测试。" if devops_ready else "先修复 CI / Make 入口直到 `make verify` 稳定。")
            ),
        ),
        AgentReport(
            name="GoAgent",
            task="Go IoT 网关首批骨架",
            status="已完成" if go_ready else "进行中",
            completed="IoT gateway 骨架、接口与测试已就位，但不是 Elder 入住 MVP 关键路径。"
            if go_ready
            else "Go 首批骨架仍在推进，但不阻塞 Elder 入住 MVP。",
            risk="当前对 Elder 入住 MVP 影响较低。"
            if go_ready
            else "若后续引入设备联动，再提升优先级。",
            next_action="保持支持态，无需占用当前主路径资源。"
            if go_ready
            else "按 bootstrap 波次继续推进即可。",
        ),
    ]

    all_core_green = all(
        report.status == "已完成"
        for report in reports
        if report.name in {"ArchAgent", "PythonAgent", "FrontAgent", "TestAgent", "DevOpsAgent"}
    )
    reports.append(
        AgentReport(
            name="MasterAgent",
            task="集成验收与协同推进",
            status="已完成" if all_core_green else "进行中",
            completed="已建立任务拆分、监督板和统一质量门禁。"
            if not all_core_green
            else "各关键 Agent 已达到 Elder 入住 MVP 收口条件。",
            risk="只要 FrontAgent 或 TestAgent 仍未收口，MVP 就还不能宣告完成。"
            if not all_core_green
            else "后续进入 Draft PR 和 Review 闭环。",
            next_action="持续每 5 分钟刷新一次状态，盯紧未完成项。"
            if not all_core_green
            else "发起最终集成验收并准备提交。",
        )
    )
    return reports


def report_map(reports: list[AgentReport]) -> dict[str, AgentReport]:
    return {report.name: report for report in reports}


def dependency_complete(report_lookup: dict[str, AgentReport], names: list[str]) -> bool:
    return all(report_lookup.get(name) and report_lookup[name].status == "已完成" for name in names)


def build_work_orders(reports: list[AgentReport]) -> list[WorkOrder]:
    lookup = report_map(reports)
    front_ready = lookup["FrontAgent"].status == "已完成"
    python_ready = lookup["PythonAgent"].status == "已完成"
    python_env_fix_needed = "依赖环境" in lookup["PythonAgent"].risk or "验证环境" in lookup["PythonAgent"].next_action
    test_ready = lookup["TestAgent"].status == "已完成"

    orders = [
        WorkOrder(
            agent_name="ArchAgent",
            dispatch_state="ACTIVE" if lookup["ArchAgent"].status != "已完成" else "DONE",
            write_scope="docs/architecture/**; docs/product/**",
            dependencies=[],
            objective="保持 Elder 入住 MVP 的字段边界稳定，并对齐任务包引用的字段清单路径。",
            todo_items=[
                "审阅任何新增的入住状态、床位关联或家属关系字段，防止越界到合同/费用/护理计划。",
                "若任务包引用 `docs/product/功能页面字段集清单.md`，补齐该路径下的字段清单（可基于架构字段清单映射产出）。",
                "如果 FrontAgent 或 PythonAgent 提出模型扩展诉求，只输出边界约束，不直接代写其他栈代码。",
            ],
            blockers=[],
            handoff_to=["PythonAgent", "FrontAgent", "MasterAgent"],
        ),
        WorkOrder(
            agent_name="PythonAgent",
            dispatch_state="ACTIVE" if python_env_fix_needed else ("SUPPORT" if python_ready else ("ACTIVE" if dependency_complete(lookup, ["ArchAgent"]) else "BLOCKED")),
            write_scope="services/python/**",
            dependencies=["ArchAgent"],
            objective="确保 elder-service 既提供稳定 API 契约，也能在仓库级验证环境里稳定跑通 HTTP 测试。",
            todo_items=[
                "核对 `POST /elders`、`GET /elders`、`GET /elders/{elder_id}` 的请求/响应字段与任务包完全一致。",
                "为 FrontAgent 提供稳定示例 payload，重点覆盖 `family_contacts`、`stay_info`、`room_id`、`bed_id`。",
                "如联调发现字段缺口，只修改 Python 侧职责范围内的接口、模型和测试。",
                "补齐 `fastapi`/测试依赖的运行假设，确保 Python 服务依赖声明与测试入口一致。",
            ],
            blockers=[] if dependency_complete(lookup, ["ArchAgent"]) else ["等待 ArchAgent 提供字段边界确认。"],
            handoff_to=["DevOpsAgent", "TestAgent", "MasterAgent"],
        ),
        WorkOrder(
            agent_name="FrontAgent",
            dispatch_state="ACTIVE" if dependency_complete(lookup, ["PythonAgent"]) and lookup["FrontAgent"].status != "已完成" else ("DONE" if lookup["FrontAgent"].status == "已完成" else "BLOCKED"),
            write_scope="apps/**",
            dependencies=["PythonAgent"],
            objective="完成 Elder 入住 MVP 前端 API 适配层与最小联调，不再停留在静态骨架。",
            todo_items=[
                "在 `apps/web` 下新增 API adapter 目录与 elder-service 访问封装，只处理前端职责范围内的调用适配。",
                "把列表、详情、创建入口与 elder-service 的最小 create/list/get 链路接通，保留 mock 兜底策略时要显式标注。",
                "补充前端侧最小联调或调用层测试，避免页面骨架与真实接口脱节。",
            ],
            blockers=[] if dependency_complete(lookup, ["PythonAgent"]) else ["等待 PythonAgent 提供稳定 API 契约。"],
            handoff_to=["TestAgent", "MasterAgent"],
        ),
        WorkOrder(
            agent_name="TestAgent",
            dispatch_state="ACTIVE" if dependency_complete(lookup, ["PythonAgent", "FrontAgent"]) and lookup["TestAgent"].status != "已完成" and not python_env_fix_needed else ("DONE" if lookup["TestAgent"].status == "已完成" else "BLOCKED"),
            write_scope="tests/**; apps/** 内测试文件; services/** 内测试文件",
            dependencies=["PythonAgent", "FrontAgent"],
            objective="把 Elder 入住 MVP 的 P0 用例落成真实可执行的自动化或冒烟资产。",
            todo_items=[
                "新增一条前后端最小冒烟资产，覆盖创建档案后可查询列表/详情的主链路。",
                "把测试矩阵中的 P0 用例映射到实际文件与执行命令，避免只有文档没有结果。",
                "仅在测试目录或测试文件中补强，不直接改业务实现；若发现缺口，回传给对应 Agent。",
            ],
            blockers=(
                ["等待 FrontAgent 完成 API adapter / 最小联调接入。"]
                if not front_ready
                else (["等待 PythonAgent / DevOpsAgent 先修复 Python HTTP 测试依赖环境。"] if python_env_fix_needed else [])
            ),
            handoff_to=["DevOpsAgent", "MasterAgent"],
        ),
        WorkOrder(
            agent_name="DevOpsAgent",
            dispatch_state="ACTIVE"
            if python_env_fix_needed
            else (
                "DONE"
                if lookup["DevOpsAgent"].status == "已完成"
                else ("WAITING" if not dependency_complete(lookup, ["TestAgent"]) else "ACTIVE")
            ),
            write_scope=".github/**; deploy/**; scripts/**; Makefile; docs/governance/**",
            dependencies=[] if python_env_fix_needed else ["TestAgent"],
            objective="修复仓库级验证环境，并在后续把联调冒烟检查纳入统一验证入口与持续监督链路。",
            todo_items=[
                "调整 Python 验证入口，使 `make verify` 在正确的依赖环境里执行 elder-service HTTP 测试。",
                "与 PythonAgent 对齐依赖声明和测试执行方式，避免 `fastapi` 等运行依赖在仓库级检查里缺失。",
                "在 TestAgent 提供真实冒烟资产后，将其接入 `Makefile` 和必要的 CI 流程。",
                "继续维护 `MasterAgent` 监督/派工脚本，让报告和派工单可持续运行。",
                "不修改 Front/Python/Go 业务代码，只处理流程、脚本和验证入口。",
            ],
            blockers=[]
            if python_env_fix_needed
            else ([] if dependency_complete(lookup, ["TestAgent"]) else ["等待 TestAgent 先产出可执行的冒烟测试资产。"]),
            handoff_to=["PythonAgent", "MasterAgent"],
        ),
        WorkOrder(
            agent_name="GoAgent",
            dispatch_state="DONE",
            write_scope="services/go/**",
            dependencies=[],
            objective="保持 Go IoT gateway 在本波次中处于稳定支持态，不抢占 Elder 入住主路径资源。",
            todo_items=[
                "持续保持现有测试和构建通过。",
                "仅在 MasterAgent 明确引入设备/实时链路依赖时再进入活跃开发。",
            ],
            blockers=[],
            handoff_to=["MasterAgent"],
        ),
    ]

    master_blockers: list[str] = []
    if lookup["ArchAgent"].status != "已完成":
        master_blockers.append("ArchAgent 尚未完成任务包字段边界/字段清单路径对齐。")
    if lookup["FrontAgent"].status != "已完成":
        master_blockers.append("FrontAgent 尚未完成 API adapter 与最小联调。")
    if python_env_fix_needed:
        master_blockers.append("PythonAgent / DevOpsAgent 尚未修复 Python HTTP 测试依赖环境。")
    if lookup["TestAgent"].status != "已完成":
        master_blockers.append("TestAgent 尚未形成可执行的 P0 联调冒烟资产。")

    orders.append(
        WorkOrder(
            agent_name="MasterAgent",
            dispatch_state="ACTIVE" if master_blockers else "DONE",
            write_scope="reports/master-agent/**; docs/product/**; docs/agents/**",
            dependencies=["ArchAgent", "PythonAgent", "FrontAgent", "TestAgent", "DevOpsAgent", "GoAgent"],
            objective="按依赖顺序驱动未完成 Agent 收口 Elder 入住 MVP，并避免互相越权改动。",
            todo_items=[
                "若 FrontAgent 尚未收口，优先派发 FrontAgent 的 API adapter / 最小联调工作。",
                "当前识别到 Python 依赖环境缺口时，同时驱动 PythonAgent 与 DevOpsAgent 修复仓库级验证入口。",
                "待 Python 验证环境与 FrontAgent 都收口后，再驱动 TestAgent 把 P0 用例转成真实冒烟测试。",
                "待 TestAgent 交付后，再通知 DevOpsAgent 把冒烟测试接入 `Makefile` 与 CI。",
            ],
            blockers=master_blockers,
            handoff_to=["FrontAgent", "PythonAgent", "TestAgent", "DevOpsAgent"],
        )
    )
    return orders


def summarize_pending_agents(reports: list[AgentReport]) -> list[str]:
    return [
        report.name
        for report in reports
        if report.name in {"PythonAgent", "FrontAgent", "TestAgent", "DevOpsAgent", "MasterAgent"}
        and report.status != "已完成"
    ]


def render_dispatch_report(
    orders: list[WorkOrder],
    reports: list[AgentReport],
    output_path: Path,
) -> str:
    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    report_lookup = report_map(reports)
    python_env_fix_needed = "依赖环境" in report_lookup["PythonAgent"].risk or "验证环境" in report_lookup["PythonAgent"].next_action
    front_pending = report_lookup["FrontAgent"].status != "已完成"
    test_pending = report_lookup["TestAgent"].status != "已完成"
    devops_pending = report_lookup["DevOpsAgent"].status != "已完成"
    lines = [
        "# MasterAgent 自动派工单",
        "",
        f"- 生成时间: {now}",
        f"- 分支: `{git_branch()}`",
        f"- 派工目标: 基于 `{TASK_PACKAGE.relative_to(REPO_ROOT)}` 驱动各 Agent 继续收口 Elder 入住 MVP",
        "",
        "## 派工总览",
        "",
        "| Agent | 当前状态 | 派工状态 | 依赖 | 写入范围 |",
        "|---|---|---|---|---|",
    ]

    for order in orders:
        current_status = report_lookup.get(order.agent_name, AgentReport(order.agent_name, "", "未知", "", "", "")).status
        dependency_text = "、".join(order.dependencies) if order.dependencies else "无"
        lines.append(
            f"| `{order.agent_name}` | {current_status} | {order.dispatch_state} | {dependency_text} | `{order.write_scope}` |"
        )

    dispatch_order = ["## MasterAgent 调度顺序", ""]
    step_index = 1
    if python_env_fix_needed:
        dispatch_order.append(f"{step_index}. 先驱动 `DevOpsAgent` 修复 Python 隔离依赖环境，确保 `make verify` 真实覆盖 elder-service HTTP 测试。")
        step_index += 1
    if report_lookup["ArchAgent"].status != "已完成":
        dispatch_order.append(f"{step_index}. 驱动 `ArchAgent` 先完成任务包字段边界与字段清单路径对齐。")
        step_index += 1
    if front_pending:
        dispatch_order.append(f"{step_index}. 驱动 `FrontAgent` 完成 API adapter 与最小联调。")
        step_index += 1
    if test_pending:
        dispatch_order.append(f"{step_index}. 驱动 `TestAgent` 将 P0 用例转成真实冒烟测试，并验证已接入统一入口。")
        step_index += 1
    if devops_pending and not python_env_fix_needed:
        dispatch_order.append(f"{step_index}. 驱动 `DevOpsAgent` 继续维护 `Makefile` / CI / 监督链路，避免入口漂移。")
        step_index += 1
    dispatch_order.extend(
        [
            f"{step_index}. `PythonAgent` 在本轮以支持态提供稳定接口契约，不越权修改前端和测试目录。",
            f"{step_index + 1}. `ArchAgent` 与 `GoAgent` 保持边界审阅和支持态，不抢占主路径资源。",
            "",
            "## 各 Agent 工单",
            "",
        ]
    )
    lines.extend([""])
    lines.extend(dispatch_order)

    for order in orders:
        lines.append(f"### `{order.agent_name}`")
        lines.append("")
        lines.append(f"- 派工状态: `{order.dispatch_state}`")
        lines.append(f"- 工作目标: {order.objective}")
        lines.append(f"- 写入范围: `{order.write_scope}`")
        dependency_text = "、".join(order.dependencies) if order.dependencies else "无"
        lines.append(f"- 依赖: {dependency_text}")
        lines.append("- 待办:")
        for item in order.todo_items:
            lines.append(f"  - {item}")
        lines.append("- 阻塞:")
        if order.blockers:
            for blocker in order.blockers:
                lines.append(f"  - {blocker}")
        else:
            lines.append("  - 无")
        lines.append("- 完成后回传给:")
        for handoff in order.handoff_to:
            lines.append(f"  - `{handoff}`")
        lines.append("")

    lines.append(f"派工总表已写入: [{output_path.relative_to(REPO_ROOT)}]({output_path})")
    return "\n".join(lines) + "\n"


def write_dispatch_orders(dispatch_dir: Path, orders: list[WorkOrder], reports: list[AgentReport]) -> None:
    dispatch_dir.mkdir(parents=True, exist_ok=True)
    report_lookup = report_map(reports)

    for order in orders:
        current_status = report_lookup.get(order.agent_name, AgentReport(order.agent_name, "", "未知", "", "", "")).status
        lines = [
            f"# {order.agent_name} 工作单",
            "",
            f"- 当前红黄绿灯状态: {current_status}",
            f"- 派工状态: {order.dispatch_state}",
            f"- 工作目标: {order.objective}",
            f"- 写入范围: `{order.write_scope}`",
            f"- 依赖: {'、'.join(order.dependencies) if order.dependencies else '无'}",
            "",
            "## 待办",
            "",
        ]
        for item in order.todo_items:
            lines.append(f"- {item}")

        lines.extend(["", "## 阻塞", ""])
        if order.blockers:
            for blocker in order.blockers:
                lines.append(f"- {blocker}")
        else:
            lines.append("- 无")

        lines.extend(["", "## 回传对象", ""])
        for handoff in order.handoff_to:
            lines.append(f"- `{handoff}`")

        (dispatch_dir / f"{order.agent_name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_report(
    reports: list[AgentReport],
    verify_status: str,
    verify_summary: str,
    output_path: Path,
) -> str:
    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    branch = git_branch()
    dirty_files = git_status_lines()
    pending_agents = summarize_pending_agents(reports)
    execution_statuses = collect_execution_statuses()

    lines = [
        "# MasterAgent 5 分钟监督汇报",
        "",
        f"- 生成时间: {now}",
        f"- 分支: `{branch}`",
        f"- 任务包: [{TASK_PACKAGE.relative_to(REPO_ROOT)}]({TASK_PACKAGE})",
        f"- `make verify`: {verify_status}",
        f"- 校验摘要: {verify_summary}",
        f"- 工作树变更数: {len(dirty_files)}",
        "",
        "## 双层状态总览",
        "",
        "| Agent | 当前任务 | 工程状态 | Codex 最新状态 | 工程结论 | 动态结论 | 下一动作 |",
        "|---|---|---|---|---|---|---|",
    ]

    for report in reports:
        execution = execution_statuses.get(
            report.name,
            AgentExecutionStatus(
                agent_name=report.name,
                status="未执行",
                detail="还没有找到该 Agent 的 Codex 运行记录。",
                latest_run_dir=None,
                latest_run_at=None,
            ),
        )
        dynamic_detail = execution.detail
        if execution.latest_run_at:
            dynamic_detail += f" 最近运行: `{execution.latest_run_at}`。"
        lines.append(
            f"| `{report.name}` | {report.task} | {report.status} | {execution.status} | {report.completed} | {dynamic_detail} | {report.next_action} |"
        )

    lines.extend(
        [
            "",
            "## 动态执行摘要",
            "",
        ]
    )

    any_execution = False
    for agent_name in sorted(execution_statuses):
        execution = execution_statuses[agent_name]
        any_execution = True
        run_suffix = f" 路径: `{execution.latest_run_dir}`" if execution.latest_run_dir else ""
        lines.append(f"- `{agent_name}`: {execution.status}。{execution.detail}{run_suffix}")

    if not any_execution:
        lines.append("- 当前还没有任何 Agent 的 Codex 运行记录。")

    lines.extend(
        [
            "",
            "## 工程未完成 Agent",
            "",
        ]
    )

    if pending_agents:
        for name in pending_agents:
            lines.append(f"- `{name}`")
    else:
        lines.append("- 当前关键 Agent 均已达到 MVP 收口条件。")

    lines.extend(
        [
            "",
            "## 当前工作树",
            "",
        ]
    )

    if dirty_files:
        for line in dirty_files[:20]:
            lines.append(f"- `{line}`")
    else:
        lines.append("- 工作树干净。")

    lines.extend(
        [
            "",
            f"报告已写入: [{output_path.relative_to(REPO_ROOT)}]({output_path})",
        ]
    )
    return "\n".join(lines) + "\n"


def write_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate MasterAgent elder MVP progress reports.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Markdown output path.")
    parser.add_argument("--dispatch-output", default=str(DEFAULT_DISPATCH_OUTPUT), help="Dispatch board output path.")
    parser.add_argument("--dispatch-dir", default=str(DEFAULT_DISPATCH_DIR), help="Per-agent dispatch order directory.")
    parser.add_argument("--interval", type=int, default=300, help="Watch interval in seconds.")
    parser.add_argument("--watch", action="store_true", help="Regenerate the report on a fixed interval.")
    parser.add_argument("--skip-verify", action="store_true", help="Do not run make verify for this cycle.")
    parser.add_argument("--verify-status", help="Override the displayed make verify status.")
    parser.add_argument("--verify-summary", help="Override the displayed make verify summary.")
    return parser.parse_args()


def generate_once(
    output_path: Path,
    dispatch_output_path: Path,
    dispatch_dir: Path,
    run_verify: bool,
    verify_status_override: str | None = None,
    verify_summary_override: str | None = None,
) -> str:
    if verify_status_override:
        verify_status = verify_status_override
        verify_summary = verify_summary_override or "校验结果由外部执行链路提供。"
    else:
        verify_status, verify_summary = evaluate_verify(run_verify)
    reports = evaluate_agents(verify_status)
    status_content = render_report(reports, verify_status, verify_summary, output_path)
    write_report(output_path, status_content)

    orders = build_work_orders(reports)
    dispatch_content = render_dispatch_report(orders, reports, dispatch_output_path)
    write_report(dispatch_output_path, dispatch_content)
    write_dispatch_orders(dispatch_dir, orders, reports)
    return status_content + "\n" + dispatch_content


def main() -> int:
    args = parse_args()
    output_path = Path(args.output).resolve()
    dispatch_output_path = Path(args.dispatch_output).resolve()
    dispatch_dir = Path(args.dispatch_dir).resolve()

    if not TASK_PACKAGE.exists():
        print(f"Missing task package: {TASK_PACKAGE}", file=sys.stderr)
        return 1

    if args.watch:
        try:
            while True:
                content = generate_once(
                    output_path,
                    dispatch_output_path,
                    dispatch_dir,
                    run_verify=not args.skip_verify,
                    verify_status_override=args.verify_status,
                    verify_summary_override=args.verify_summary,
                )
                print(content, end="")
                sys.stdout.flush()
                time.sleep(max(args.interval, 1))
        except KeyboardInterrupt:
            return 0

    content = generate_once(
        output_path,
        dispatch_output_path,
        dispatch_dir,
        run_verify=not args.skip_verify,
        verify_status_override=args.verify_status,
        verify_summary_override=args.verify_summary,
    )
    print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
