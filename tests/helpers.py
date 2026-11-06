"""Shared helpers: run a skill script in a temporary folder and write fixture files."""
from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "claude_skills"
BUILD_ORDER = SKILLS / "implementation-planner" / "scripts" / "build_order.py"
FILES_CHANGED = SKILLS / "implementing-plans" / "scripts" / "files_changed.py"
CHECK_DECISION = SKILLS / "decision-record" / "scripts" / "check_decision.py"
CHECK_PLANS = SKILLS / "splitting-decisions-into-plans" / "scripts" / "check_plans.py"


def run(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(script), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip("\n"), encoding="utf-8", newline="\n")
    return path


def plan(pid: str, name: str, deps: str = "–", status: str = "Ready", group: str = "Main flow", acs: str = "") -> str:
    acs = acs or "\n".join(
        f"- [ ] **AC-{pid}.{k}** Given a user, when they act, then it works.\n"
        f"  - Check: `npm test` · Source: 3.1 [DECIDED]"
        for k in (1, 2, 3)
    )
    return (
        f"# Plan {pid} — {name}\n\n"
        f"Group: {group} · Depends on: {deps} · Status: {status} · Source: 3.1\n\n"
        f"## Goal\nSomeone can do something.\n\n## Acceptance criteria\n{acs}\n"
    )


def index(rows: list[tuple[str, str, str, str]], coverage: str = "| 3.1 Topic | 01 |", extra: str = "") -> str:
    table = "\n".join(
        f"| {pid} | [{name}]({pid}-{name.lower()}.md) | Main flow | x | {deps} | {status} |"
        for pid, name, deps, status in rows
    )
    return (
        "# Demo — plans\n\n## Plans\n\n"
        "| # | Plan | Group | Outcome | Depends on | Status |\n|---|---|---|---|---|---|\n"
        f"{table}\n\n## Coverage\n| Source item (§ or ID) | Lands in |\n|---|---|\n{coverage}\n{extra}"
    )
