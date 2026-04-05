#!/usr/bin/env python3

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import master_status_report as status_report


REPO_ROOT = Path(__file__).resolve().parent.parent
EXECUTOR_DIR = REPO_ROOT / "reports/master-agent/executor"
PROMPT_DIR = EXECUTOR_DIR / "prompts"
RUN_DIR = EXECUTOR_DIR / "runs"
AGENT_RUNTIME_DIR = EXECUTOR_DIR / "agents"
MASTER_TRACE_DIR = EXECUTOR_DIR / "master-agent-traces"
MASTER_TRACE_INDEX = MASTER_TRACE_DIR / "timeline.jsonl"
STATE_FILE = EXECUTOR_DIR / "state.json"
LAST_PROMPT_FILE = EXECUTOR_DIR / "next_agent_prompt.md"
LAST_RESULT_FILE = EXECUTOR_DIR / "last_result.json"
CODEX_HOME_DIR = REPO_ROOT / ".codex-runtime"
DEFAULT_USER_CODEX_HOME = Path.home() / ".codex"
DEFAULT_FAILURE_THRESHOLD = 3
DEFAULT_COOLDOWN_SECONDS = 1800
DEFAULT_CODEX_CANDIDATES = (
    "/Applications/Codex.app/Contents/Resources/codex",
    "/opt/homebrew/bin/codex",
    "/usr/local/bin/codex",
)

AGENT_GUIDES = {
    "ArchAgent": "docs/agents/Arch.md",
    "PythonAgent": "docs/agents/PythonAgent.md",
    "FrontAgent": "docs/agents/FrontAgent.md",
    "TestAgent": "docs/agents/TestAgent.md",
    "DevOpsAgent": "docs/agents/DevOpsAgent.md",
    "GoAgent": "docs/agents/GoAgent.md",
    "MasterAgent": "docs/agents/MasterAgent.md",
}


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def ensure_dirs() -> None:
    for path in [EXECUTOR_DIR, PROMPT_DIR, RUN_DIR, AGENT_RUNTIME_DIR, MASTER_TRACE_DIR, CODEX_HOME_DIR]:
        path.mkdir(parents=True, exist_ok=True)
    sync_codex_runtime_seed()


def copy_if_present(source: Path, target: Path) -> None:
    if not source.exists():
        return
    if target.exists():
        source_stat = source.stat()
        target_stat = target.stat()
        if (
            int(source_stat.st_mtime) <= int(target_stat.st_mtime)
            and source_stat.st_size == target_stat.st_size
        ):
            return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def sync_codex_runtime_seed(target_dir: Path = CODEX_HOME_DIR) -> None:
    mappings = [
        ("auth.json", 0o600),
        ("config.toml", 0o600),
    ]
    for relative_name, mode in mappings:
        source = DEFAULT_USER_CODEX_HOME / relative_name
        target = target_dir / relative_name
        copy_if_present(source, target)
        if target.exists():
            target.chmod(mode)

    for relative_dir in ["memories", "rules", "skills", "plugins"]:
        (target_dir / relative_dir).mkdir(parents=True, exist_ok=True)


def agent_runtime_dir(agent_name: str) -> Path:
    return AGENT_RUNTIME_DIR / agent_name


def agent_codex_home(agent_name: str) -> Path:
    runtime_dir = agent_runtime_dir(agent_name)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    sync_codex_runtime_seed(runtime_dir)
    return runtime_dir


def resolve_codex_bin(codex_bin: str) -> str:
    candidate = Path(codex_bin).expanduser()
    if candidate.is_file():
        return str(candidate)

    resolved = shutil.which(codex_bin)
    if resolved:
        return resolved

    if codex_bin == "codex":
        env_candidate = os.environ.get("CODEX_BIN")
        if env_candidate:
            env_path = Path(env_candidate).expanduser()
            if env_path.is_file():
                return str(env_path)
            resolved = shutil.which(env_candidate)
            if resolved:
                return resolved

        for default_candidate in DEFAULT_CODEX_CANDIDATES:
            if Path(default_candidate).is_file():
                return default_candidate

    search_path = os.environ.get("PATH", "")
    raise FileNotFoundError(
        "Unable to locate the Codex CLI binary. "
        f"Tried `{codex_bin}` with PATH={search_path!r}. "
        "Set `--codex-bin` or `CODEX_BIN`, or install Codex CLI in PATH."
    )


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def parse_iso_datetime(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value)
    except ValueError:
        return None


def load_runtime_state() -> dict[str, object]:
    return read_json(STATE_FILE)


def get_failure_agents(runtime_state: dict[str, object]) -> dict[str, dict[str, object]]:
    failure_control = runtime_state.get("failure_control")
    if not isinstance(failure_control, dict):
        return {}
    agents = failure_control.get("agents")
    if not isinstance(agents, dict):
        return {}
    return agents


def update_failure_control(runtime_state: dict[str, object], threshold: int, cooldown_seconds: int) -> None:
    runtime_state["failure_control"] = {
        "threshold": threshold,
        "cooldown_seconds": cooldown_seconds,
        "agents": get_failure_agents(runtime_state),
    }


def reconcile_circuit_breakers(runtime_state: dict[str, object], threshold: int, cooldown_seconds: int) -> None:
    agents = get_failure_agents(runtime_state)
    now = dt.datetime.now().astimezone()

    for agent_name, info in list(agents.items()):
        if not isinstance(info, dict):
            agents[agent_name] = {}
            continue

        if info.get("breaker_state") != "open":
            continue

        open_until = parse_iso_datetime(info.get("open_until"))
        if open_until and now >= open_until:
            agents[agent_name] = {
                "consecutive_failures": 0,
                "breaker_state": "closed",
                "cooldown_seconds": cooldown_seconds,
                "recovered_at": now_iso(),
                "last_failure_at": info.get("last_failure_at"),
                "last_failure_reason": info.get("last_failure_reason"),
            }

    update_failure_control(runtime_state, threshold, cooldown_seconds)


def circuit_breaker_open(runtime_state: dict[str, object], agent_name: str) -> tuple[bool, str | None]:
    info = get_failure_agents(runtime_state).get(agent_name, {})
    if not isinstance(info, dict) or info.get("breaker_state") != "open":
        return False, None
    open_until = info.get("open_until")
    return True, open_until if isinstance(open_until, str) else None


def record_agent_success(
    runtime_state: dict[str, object],
    agent_name: str,
    threshold: int,
    cooldown_seconds: int,
) -> None:
    agents = get_failure_agents(runtime_state)
    agents[agent_name] = {
        "consecutive_failures": 0,
        "breaker_state": "closed",
        "cooldown_seconds": cooldown_seconds,
        "last_success_at": now_iso(),
    }
    update_failure_control(runtime_state, threshold, cooldown_seconds)


def record_agent_failure(
    runtime_state: dict[str, object],
    agent_name: str,
    threshold: int,
    cooldown_seconds: int,
    reason: str,
) -> dict[str, object]:
    agents = get_failure_agents(runtime_state)
    info = agents.get(agent_name, {})
    if not isinstance(info, dict):
        info = {}

    consecutive_failures = int(info.get("consecutive_failures", 0)) + 1
    updated = {
        "consecutive_failures": consecutive_failures,
        "breaker_state": "closed",
        "cooldown_seconds": cooldown_seconds,
        "last_failure_at": now_iso(),
        "last_failure_reason": reason,
    }

    if consecutive_failures >= threshold:
        open_until = dt.datetime.now().astimezone() + dt.timedelta(seconds=cooldown_seconds)
        updated["breaker_state"] = "open"
        updated["open_until"] = open_until.isoformat(timespec="seconds")

    agents[agent_name] = updated
    update_failure_control(runtime_state, threshold, cooldown_seconds)
    return updated


def refresh_dispatch(run_verify: bool) -> tuple[list[status_report.AgentReport], list[status_report.WorkOrder]]:
    status_report.generate_once(
        status_report.DEFAULT_OUTPUT,
        status_report.DEFAULT_DISPATCH_OUTPUT,
        status_report.DEFAULT_DISPATCH_DIR,
        run_verify=run_verify,
    )
    verify_status = "通过" if run_verify else "未执行"
    reports = status_report.evaluate_agents(verify_status)
    orders = status_report.build_work_orders(reports)
    return reports, orders


def dependencies_ready(
    order: status_report.WorkOrder,
    report_lookup: dict[str, status_report.AgentReport],
) -> bool:
    return all(
        report_lookup.get(dep) and report_lookup[dep].status == "已完成"
        for dep in order.dependencies
    )


def blockers_clear(order: status_report.WorkOrder) -> bool:
    return not order.blockers


def write_scope_tokens(write_scope: str) -> set[str]:
    tokens: set[str] = set()
    for raw_part in write_scope.split(";"):
        part = raw_part.strip()
        if not part:
            continue
        normalized = part.replace("`", "")
        if "/**" in normalized:
            normalized = normalized.split("/**", 1)[0]
        if(" 内测试文件" in normalized):
            normalized = normalized.split(" 内测试文件", 1)[0]
        tokens.add(normalized)
    return tokens


def scopes_conflict(left: str, right: str) -> bool:
    left_tokens = write_scope_tokens(left)
    right_tokens = write_scope_tokens(right)
    for left_token in left_tokens:
        for right_token in right_tokens:
            if left_token == right_token:
                return True
            if left_token.startswith(right_token.rstrip("/")) or right_token.startswith(left_token.rstrip("/")):
                return True
    return False


def select_runnable_orders(
    reports: list[status_report.AgentReport],
    orders: list[status_report.WorkOrder],
    runtime_state: dict[str, object],
    max_parallel: int,
    master_fallback_interval_seconds: int,
) -> list[status_report.WorkOrder]:
    report_lookup = status_report.report_map(reports)
    selected: list[status_report.WorkOrder] = []
    master_order: status_report.WorkOrder | None = None
    for order in orders:
        if order.agent_name == "MasterAgent":
            master_order = order
            continue
        if order.dispatch_state != "ACTIVE":
            continue
        if not dependencies_ready(order, report_lookup):
            continue
        if not blockers_clear(order):
            continue
        is_open, _ = circuit_breaker_open(runtime_state, order.agent_name)
        if is_open:
            continue
        if any(scopes_conflict(order.write_scope, existing.write_scope) for existing in selected):
            continue
        selected.append(order)
        if len(selected) >= max(max_parallel, 1):
            break

    if selected:
        return selected

    # Fallback: when no specialized ACTIVE agent can run, allow MasterAgent to
    # execute one orchestration round so supervision can continue progressing.
    if master_order:
        is_open, _ = circuit_breaker_open(runtime_state, master_order.agent_name)
        if is_open:
            return selected
        last_master_fallback_at = parse_iso_datetime(
            runtime_state.get("last_master_fallback_at")
            if isinstance(runtime_state.get("last_master_fallback_at"), str)
            else None
        )
        now = dt.datetime.now().astimezone()
        if (
            last_master_fallback_at is None
            or (now - last_master_fallback_at).total_seconds() >= max(master_fallback_interval_seconds, 1)
        ):
            return [master_order]

    return selected


def write_master_trace(
    *,
    agent_result: dict[str, object],
    prompt: str,
    prompt_path: Path,
) -> None:
    if agent_result.get("agent_name") != "MasterAgent":
        return

    run_dir = Path(str(agent_result.get("run_dir", "")))
    if not run_dir.exists():
        return

    trace_stamp = dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    trace_dir = MASTER_TRACE_DIR / trace_stamp
    trace_dir.mkdir(parents=True, exist_ok=True)

    (trace_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    if prompt_path.exists():
        shutil.copy2(prompt_path, trace_dir / "prompt.source.md")

    for name in ["stdout.log", "stderr.log", "last_message.txt"]:
        src = run_dir / name
        if src.exists():
            shutil.copy2(src, trace_dir / name)

    summary = {
        "captured_at": now_iso(),
        "agent_name": "MasterAgent",
        "run_dir": str(run_dir),
        "trace_dir": str(trace_dir),
        "prompt_file": str(prompt_path),
        "return_code": agent_result.get("return_code"),
        "last_message_preview": agent_result.get("last_message_preview", ""),
    }
    write_json(trace_dir / "summary.json", summary)
    with MASTER_TRACE_INDEX.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(summary, ensure_ascii=False) + "\n")


def build_prompt(
    order: status_report.WorkOrder,
    report_lookup: dict[str, status_report.AgentReport],
) -> str:
    guide = AGENT_GUIDES.get(order.agent_name)
    dependency_lines = []
    for dependency in order.dependencies:
        dependency_report = report_lookup.get(dependency)
        if dependency_report:
            dependency_lines.append(
                f"- `{dependency}`: 当前状态为 {dependency_report.status}，下一动作是 {dependency_report.next_action}"
            )

    todo_lines = "\n".join(f"- {item}" for item in order.todo_items)
    blocker_lines = "\n".join(f"- {item}" for item in order.blockers) if order.blockers else "- 无"
    handoff_lines = "\n".join(f"- `{item}`" for item in order.handoff_to)

    return f"""你现在扮演 `{order.agent_name}`，由 `MasterAgent` 自动执行器派工。

工作目录：`{REPO_ROOT}`
任务包：`docs/product/Elder入住首批任务包.md`
专项规范：`{guide}`{"" if guide else ""}
派工生成时间：{now_iso()}

你的唯一目标：
{order.objective}

强约束：
- 只能在 `{order.write_scope}` 范围内改动；不要越权修改其他 Agent 的主工作区。
- 先阅读任务包、专项 Agent 文档、与你待办直接相关的代码。
- 只完成当前工单，不顺手扩写其他不相关需求。
- 修改后运行与你工作范围相关的最小验证；如有能力，优先补充测试。
- 完成后给出：已完成项、验证结果、剩余风险、回传对象。

当前待办：
{todo_lines}

当前阻塞：
{blocker_lines}

依赖状态：
{chr(10).join(dependency_lines) if dependency_lines else "- 无"}

完成后回传给：
{handoff_lines}

开始执行前，请先阅读：
- `README.md`
- `docs/agents/MasterAgent.md`
- `docs/governance/AGENTS.md`
- `{guide}`{"" if guide else ""}

然后直接在仓库中实施，不要只停留在分析。
"""


def write_prompt(order: status_report.WorkOrder, prompt: str) -> Path:
    timestamp = dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    prompt_path = PROMPT_DIR / f"{timestamp}-{order.agent_name}.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    LAST_PROMPT_FILE.write_text(prompt, encoding="utf-8")
    return prompt_path


def run_codex_exec(
    codex_bin: str,
    agent_name: str,
    prompt: str,
    run_root: Path,
    model: str | None,
) -> tuple[int, str, str]:
    resolved_codex_bin = resolve_codex_bin(codex_bin)
    codex_home = agent_codex_home(agent_name)
    command = [
        resolved_codex_bin,
        "exec",
        "--cd",
        str(REPO_ROOT),
        "--sandbox",
        "workspace-write",
        "--full-auto",
        "--skip-git-repo-check",
        "-",
    ]
    if model:
        command.extend(["--model", model])

    stdout_path = run_root / "stdout.log"
    stderr_path = run_root / "stderr.log"
    last_message_path = run_root / "last_message.txt"
    command.extend(["--output-last-message", str(last_message_path)])

    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        input=prompt,
        capture_output=True,
        env={
            **os.environ,
            "CODEX_HOME": str(codex_home),
        },
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    last_message = ""
    if last_message_path.exists():
        last_message = last_message_path.read_text(encoding="utf-8")
    return completed.returncode, completed.stdout, last_message


def execute_one_cycle(
    codex_bin: str,
    run_verify: bool,
    execute: bool,
    model: str | None,
    failure_threshold: int,
    cooldown_seconds: int,
    max_parallel: int,
) -> dict[str, object]:
    ensure_dirs()
    runtime_state = load_runtime_state()
    reconcile_circuit_breakers(runtime_state, failure_threshold, cooldown_seconds)
    reports, orders = refresh_dispatch(run_verify=run_verify)
    report_lookup = status_report.report_map(reports)
    selected_orders = select_runnable_orders(
        reports,
        orders,
        runtime_state,
        max_parallel,
        master_fallback_interval_seconds=max(cooldown_seconds, 1),
    )

    result: dict[str, object] = {
        "generated_at": now_iso(),
        "run_verify": run_verify,
        "execute": execute,
        "selected_agent": None,
        "selected_agents": [],
        "prompt_file": None,
        "prompt_files": [],
        "dispatch_file": str(status_report.DEFAULT_DISPATCH_OUTPUT),
        "status_file": str(status_report.DEFAULT_OUTPUT),
        "execution": "idle",
        "failure_threshold": failure_threshold,
        "cooldown_seconds": cooldown_seconds,
        "max_parallel": max_parallel,
    }

    if not selected_orders:
        open_circuits = {
            agent_name: info.get("open_until")
            for agent_name, info in get_failure_agents(runtime_state).items()
            if isinstance(info, dict) and info.get("breaker_state") == "open"
        }
        result["execution"] = "circuit-open" if open_circuits else "no-eligible-agent"
        if open_circuits:
            result["open_circuits"] = open_circuits
        runtime_state.update(
            {
                "updated_at": now_iso(),
                "selected_agent": None,
                "dispatch_state": None,
                "write_scope": None,
                "dependencies": [],
                "prompt_file": None,
                "selected_agents": [],
                "prompt_files": [],
                "execute_mode": "codex-exec" if execute else "dry-run",
            }
        )
        update_failure_control(runtime_state, failure_threshold, cooldown_seconds)
        write_json(STATE_FILE, runtime_state)
        write_json(LAST_RESULT_FILE, result)
        return result

    prompts: list[tuple[status_report.WorkOrder, str, Path]] = []
    for order in selected_orders:
        prompt = build_prompt(order, report_lookup)
        prompt_path = write_prompt(order, prompt)
        prompts.append((order, prompt, prompt_path))

    result["selected_agent"] = selected_orders[0].agent_name
    result["selected_agents"] = [order.agent_name for order in selected_orders]
    result["prompt_file"] = str(prompts[0][2])
    result["prompt_files"] = [str(prompt_path) for _, _, prompt_path in prompts]
    result["execution"] = "prompt-generated"

    runtime_state.update(
        {
            "updated_at": now_iso(),
            "selected_agent": selected_orders[0].agent_name,
            "selected_agents": [order.agent_name for order in selected_orders],
            "dispatch_state": ",".join(order.dispatch_state for order in selected_orders),
            "write_scope": "; ".join(order.write_scope for order in selected_orders),
            "dependencies": [dependency for order in selected_orders for dependency in order.dependencies],
            "prompt_file": str(prompts[0][2]),
            "prompt_files": [str(prompt_path) for _, _, prompt_path in prompts],
            "execute_mode": "codex-exec" if execute else "dry-run",
            "last_master_fallback_at": now_iso() if selected_orders[0].agent_name == "MasterAgent" else runtime_state.get("last_master_fallback_at"),
        }
    )
    update_failure_control(runtime_state, failure_threshold, cooldown_seconds)
    write_json(STATE_FILE, runtime_state)

    if not execute:
        write_json(LAST_RESULT_FILE, result)
        return result

    def execute_order(order: status_report.WorkOrder, prompt: str, prompt_path: Path) -> dict[str, object]:
        run_stamp = dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
        run_root = RUN_DIR / f"{run_stamp}-{order.agent_name}"
        run_root.mkdir(parents=True, exist_ok=True)
        return_code, stdout, last_message = run_codex_exec(codex_bin, order.agent_name, prompt, run_root, model)
        agent_result = {
            "agent_name": order.agent_name,
            "return_code": return_code,
            "run_dir": str(run_root),
            "prompt_file": str(prompt_path),
            "last_message_preview": last_message[:1000],
        }
        write_master_trace(agent_result=agent_result, prompt=prompt, prompt_path=prompt_path)
        return agent_result

    per_agent_results: list[dict[str, object]] = []
    max_workers = max(1, min(max_parallel, len(prompts)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(execute_order, order, prompt, prompt_path)
            for order, prompt, prompt_path in prompts
        ]
        for future in futures:
            per_agent_results.append(future.result())

    per_agent_results.sort(key=lambda item: item["agent_name"])
    any_failed = False
    for agent_result in per_agent_results:
        if int(agent_result["return_code"]) == 0:
            record_agent_success(runtime_state, agent_result["agent_name"], failure_threshold, cooldown_seconds)
        else:
            any_failed = True
            agent_result["failure_info"] = record_agent_failure(
                runtime_state,
                agent_result["agent_name"],
                failure_threshold,
                cooldown_seconds,
                reason=f"codex exec returned {agent_result['return_code']}",
            )

    result["execution"] = "failed" if any_failed else "completed"
    result["agent_results"] = per_agent_results
    if per_agent_results:
        result["return_code"] = max(int(item["return_code"]) for item in per_agent_results)
        result["run_dir"] = per_agent_results[0]["run_dir"]
        result["last_message_preview"] = per_agent_results[0].get("last_message_preview", "")
    runtime_state.update(
        {
            "updated_at": now_iso(),
            "selected_agent": selected_orders[0].agent_name,
            "selected_agents": [order.agent_name for order in selected_orders],
            "dispatch_state": ",".join(order.dispatch_state for order in selected_orders),
            "write_scope": "; ".join(order.write_scope for order in selected_orders),
            "dependencies": [dependency for order in selected_orders for dependency in order.dependencies],
            "prompt_file": str(prompts[0][2]),
            "prompt_files": [str(prompt_path) for _, _, prompt_path in prompts],
            "execute_mode": "codex-exec",
            "last_master_fallback_at": now_iso() if selected_orders[0].agent_name == "MasterAgent" else runtime_state.get("last_master_fallback_at"),
        }
    )
    write_json(STATE_FILE, runtime_state)
    write_json(LAST_RESULT_FILE, result)

    refresh_dispatch(run_verify=run_verify)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the MasterAgent auto executor for local Codex automation.")
    parser.add_argument("--watch", action="store_true", help="Run the executor repeatedly.")
    parser.add_argument("--interval", type=int, default=300, help="Loop interval in seconds when --watch is used.")
    parser.add_argument("--skip-verify", action="store_true", help="Do not rerun make verify before scheduling.")
    parser.add_argument("--execute", action="store_true", help="Actually invoke `codex exec` for the selected agent.")
    parser.add_argument("--codex-bin", default="codex", help="Codex CLI binary path.")
    parser.add_argument("--model", default=None, help="Optional model override for `codex exec`.")
    parser.add_argument("--failure-threshold", type=int, default=DEFAULT_FAILURE_THRESHOLD, help="Open the circuit after N consecutive failures for the same agent.")
    parser.add_argument("--cooldown-seconds", type=int, default=DEFAULT_COOLDOWN_SECONDS, help="Cooldown before retrying an agent with an open circuit.")
    parser.add_argument("--max-parallel", type=int, default=2, help="Maximum number of disjoint ACTIVE agents to drive in one cycle.")
    parser.add_argument("--reset-circuit", default=None, help="Reset the circuit breaker for one agent and exit.")
    parser.add_argument("--reset-all-circuits", action="store_true", help="Reset all circuit breakers and exit.")
    return parser.parse_args()


def print_result(result: dict[str, object]) -> None:
    print("# MasterAgent 自动执行器")
    print()
    print(f"- 时间: {result['generated_at']}")
    print(f"- 执行模式: {'execute' if result['execute'] else 'dry-run'}")
    print(f"- 选中 Agent: {result['selected_agent'] or '无'}")
    if result.get("selected_agents"):
        print(f"- 并发 Agent: {', '.join(result['selected_agents'])}")
    print(f"- 执行结果: {result['execution']}")
    if result.get("prompt_file"):
        print(f"- Prompt: `{result['prompt_file']}`")
    if result.get("run_dir"):
        print(f"- Run Dir: `{result['run_dir']}`")
    if result.get("return_code") is not None:
        print(f"- Return Code: {result['return_code']}")
    if result.get("open_circuits"):
        print(f"- Open Circuits: {result['open_circuits']}")
    if result.get("failure_info"):
        print(f"- Failure Info: {result['failure_info']}")
    if result.get("agent_results"):
        for agent_result in result["agent_results"]:
            print(
                f"- Agent Result: {agent_result['agent_name']} return_code={agent_result['return_code']} run_dir={agent_result['run_dir']}"
            )


def reset_circuits(agent_name: str | None, reset_all: bool, threshold: int, cooldown_seconds: int) -> int:
    ensure_dirs()
    runtime_state = load_runtime_state()
    agents = get_failure_agents(runtime_state)

    if reset_all:
        agents = {}
    elif agent_name:
        agents.pop(agent_name, None)

    runtime_state["failure_control"] = {
        "threshold": threshold,
        "cooldown_seconds": cooldown_seconds,
        "agents": agents,
    }
    runtime_state["updated_at"] = now_iso()
    write_json(STATE_FILE, runtime_state)
    return 0


def main() -> int:
    args = parse_args()
    if args.reset_all_circuits or args.reset_circuit:
        return reset_circuits(
            agent_name=args.reset_circuit,
            reset_all=args.reset_all_circuits,
            threshold=max(args.failure_threshold, 1),
            cooldown_seconds=max(args.cooldown_seconds, 1),
        )
    try:
        args.codex_bin = resolve_codex_bin(args.codex_bin)
    except FileNotFoundError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    def run_once() -> int:
        result = execute_one_cycle(
            codex_bin=args.codex_bin,
            run_verify=not args.skip_verify,
            execute=args.execute,
            model=args.model,
            failure_threshold=max(args.failure_threshold, 1),
            cooldown_seconds=max(args.cooldown_seconds, 1),
            max_parallel=max(args.max_parallel, 1),
        )
        print_result(result)
        return 0 if result.get("execution") != "failed" else 1

    if args.watch:
        try:
            while True:
                run_once()
                time.sleep(max(args.interval, 1))
        except KeyboardInterrupt:
            return 0

    return run_once()


if __name__ == "__main__":
    raise SystemExit(main())
