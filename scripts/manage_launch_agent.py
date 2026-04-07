#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
LABEL = "com.regionalhealth.masteragent.autowatch"
LAUNCH_AGENTS_DIR = Path.home() / "Library/LaunchAgents"
PLIST_PATH = LAUNCH_AGENTS_DIR / f"{LABEL}.plist"
LOG_DIR = REPO_ROOT / "reports/master-agent/launchd"
STDOUT_LOG = LOG_DIR / "stdout.log"
STDERR_LOG = LOG_DIR / "stderr.log"
CODEX_HOME_DIR = REPO_ROOT / ".codex-runtime"
DEFAULT_CODEX_CANDIDATES = (
    "/Applications/Codex.app/Contents/Resources/codex",
    "/opt/homebrew/bin/codex",
    "/usr/local/bin/codex",
)


def resolve_codex_bin(codex_bin: str = "codex") -> str:
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
        "Set `CODEX_BIN`, or install Codex CLI in PATH."
    )


def build_plist() -> dict[str, object]:
    codex_bin = resolve_codex_bin()
    codex_bin_dir = str(Path(codex_bin).parent)
    command = (
        f'export PATH="{codex_bin_dir}:$PATH"; '
        f'export CODEX_BIN="{codex_bin}"; '
        f'export CODEX_HOME="{CODEX_HOME_DIR}"; '
        f'mkdir -p "{CODEX_HOME_DIR}" "{LOG_DIR}"; '
        f'cd "{REPO_ROOT}" && exec /usr/bin/make auto-watch'
    )
    return {
        "Label": LABEL,
        "WorkingDirectory": str(REPO_ROOT),
        "ProgramArguments": ["/bin/bash", "-lc", command],
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": str(STDOUT_LOG),
        "StandardErrorPath": str(STDERR_LOG),
        "EnvironmentVariables": {
            "PATH": f"{codex_bin_dir}:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "CODEX_BIN": codex_bin,
            "CODEX_HOME": str(CODEX_HOME_DIR),
        },
        "ProcessType": "Background",
    }


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def install() -> int:
    LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    CODEX_HOME_DIR.mkdir(parents=True, exist_ok=True)

    with PLIST_PATH.open("wb") as handle:
        plistlib.dump(build_plist(), handle, sort_keys=False)

    lint = run_command(["plutil", "-lint", str(PLIST_PATH)])
    if lint.returncode != 0:
        sys.stderr.write(lint.stdout + lint.stderr)
        return lint.returncode

    run_command(["launchctl", "bootout", f"gui/{os.getuid()}", str(PLIST_PATH)])
    bootstrap = run_command(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(PLIST_PATH)])
    if bootstrap.returncode != 0:
        sys.stderr.write(bootstrap.stdout + bootstrap.stderr)
        return bootstrap.returncode

    enable = run_command(["launchctl", "enable", f"gui/{os.getuid()}/{LABEL}"])
    if enable.returncode != 0:
        sys.stderr.write(enable.stdout + enable.stderr)
        return enable.returncode

    kickstart = run_command(["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/{LABEL}"])
    if kickstart.returncode != 0:
        sys.stderr.write(kickstart.stdout + kickstart.stderr)
        return kickstart.returncode

    print(f"Installed launch agent: {PLIST_PATH}")
    return 0


def uninstall() -> int:
    run_command(["launchctl", "bootout", f"gui/{os.getuid()}", str(PLIST_PATH)])
    if PLIST_PATH.exists():
        PLIST_PATH.unlink()
    print(f"Removed launch agent: {PLIST_PATH}")
    return 0


def status() -> int:
    print(f"Label: {LABEL}")
    print(f"Plist: {PLIST_PATH}")
    print(f"Exists: {'yes' if PLIST_PATH.exists() else 'no'}")
    result = run_command(["launchctl", "print", f"gui/{os.getuid()}/{LABEL}"])
    if result.returncode == 0:
        print(result.stdout)
        return 0

    sys.stderr.write(result.stdout + result.stderr)
    return result.returncode


def print_plist() -> int:
    plistlib.dump(build_plist(), sys.stdout.buffer, sort_keys=False)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage the MasterAgent auto-watch launchd agent.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--install", action="store_true", help="Install and start the launch agent.")
    group.add_argument("--uninstall", action="store_true", help="Unload and remove the launch agent.")
    group.add_argument("--status", action="store_true", help="Print launchctl status for the agent.")
    group.add_argument("--print-plist", action="store_true", help="Print the generated plist to stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        resolve_codex_bin()
    except FileNotFoundError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1
    if args.install:
        return install()
    if args.uninstall:
        return uninstall()
    if args.status:
        return status()
    return print_plist()


if __name__ == "__main__":
    raise SystemExit(main())
