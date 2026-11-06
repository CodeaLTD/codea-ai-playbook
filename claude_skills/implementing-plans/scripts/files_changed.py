#!/usr/bin/env python3
"""Files changed since a base commit, as the rows of the implementing-plans report table.

    python files_changed.py --base <start commit>            # the repo in the current folder
    python files_changed.py --base abc123 ../infra=def456     # also another repo, own base

Compares the working tree with the base, so committed and uncommitted changes both count,
and adds untracked files. Line ranges are the new-file lines of each `git diff -U0` hunk.
The What column is left empty for you to fill. Reads git only; writes nothing.

Without --base, each repo's base is its merge-base with main (or master), else HEAD.
Exit codes: 0 ok, 1 git error or not a repo.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
STATUS = {"M": "modified", "A": "new", "D": "deleted", "R": "renamed", "C": "copied", "T": "type changed"}


class GitError(Exception):
    pass


def git(repo: Path, *args: str) -> str:
    run = subprocess.run(
        ["git", "-C", str(repo), "-c", "core.quotepath=off", *args],
        capture_output=True,
    )
    if run.returncode:
        raise GitError(run.stderr.decode("utf-8", "replace").strip() or f"git {' '.join(args)} failed")
    return run.stdout.decode("utf-8", "replace")


def default_base(repo: Path) -> str:
    for branch in ("main", "master"):
        try:
            return git(repo, "merge-base", "HEAD", branch).strip()
        except GitError:
            continue
    return git(repo, "rev-parse", "HEAD").strip()


def span(start: int, count: int) -> str:
    end = start + count - 1
    return str(start) if count == 1 else f"{start}-{end}"


def ranges(diff: str) -> str:
    """Line ranges from a -U0 diff: new-file lines, or the old lines of a pure deletion."""
    if re.search(r"^Binary files .* differ$", diff, re.M):
        return "binary"
    out = []
    for line in diff.splitlines():
        if m := HUNK.match(line):
            a, b = int(m.group(1)), int(m.group(2) or 1)
            c, d = int(m.group(3)), int(m.group(4) or 1)
            out.append(f"removed (old lines {span(a, b)})" if d == 0 else span(c, d))
    return ", ".join(out) or "content unchanged"


def count_lines(path: Path) -> str:
    data = path.read_bytes()
    if b"\0" in data:
        return "all (binary)"
    n = data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
    return f"all ({n} line{'s' if n != 1 else ''})"


def rows(repo: Path, base: str) -> list[tuple[str, str, str]]:
    found = []
    entries = git(repo, "diff", "--name-status", "-z", "--find-renames", base).split("\0")
    i = 0
    while i < len(entries) and entries[i]:
        code = entries[i]
        kind = code[0]
        if kind in "RC":
            old, new = entries[i + 1], entries[i + 2]
            i += 3
            diff = git(repo, "diff", "-U0", "--no-color", "--no-ext-diff", "--find-renames", base, "--", old, new)
            found.append((new, f"{STATUS[kind]} from `{old}`", ranges(diff)))
            continue
        path = entries[i + 1]
        i += 2
        if kind == "D":
            found.append((path, "deleted", "all removed"))
        elif kind == "A":
            found.append((path, "new", count_lines(repo / path)))
        else:
            diff = git(repo, "diff", "-U0", "--no-color", "--no-ext-diff", base, "--", path)
            found.append((path, STATUS.get(kind, kind), ranges(diff)))
    for path in git(repo, "ls-files", "--others", "--exclude-standard", "-z").split("\0"):
        if path:
            found.append((path, "new (untracked)", count_lines(repo / path)))
    return sorted(found)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--base", help="commit the work started from, for the repo in the current folder")
    ap.add_argument("repos", nargs="*", metavar="PATH[=BASE]", help="other repos you touched")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")

    targets = [(Path("."), a.base)]
    for item in a.repos:
        path, _, base = item.partition("=")
        targets.append((Path(path), base or None))

    blocks, any_rows = [], False
    for repo, base in targets:
        try:
            top = Path(git(repo, "rev-parse", "--show-toplevel").strip())
            base = base or default_base(top)
            short = git(top, "rev-parse", "--short", base).strip()
            found = rows(top, base)
        except GitError as e:
            print(f"{repo}: {e}", file=sys.stderr)
            return 1
        lines = [f"**Repo: {top.name}** (since `{short}`)", ""] if len(targets) > 1 else []
        if found:
            any_rows = True
            lines += ["| File | Status | Lines changed | What |", "|---|---|---|---|"]
            lines += [f"| `{p}` | {s} | {r} |  |" for p, s, r in found]
        else:
            lines.append("No files changed.")
        blocks.append("\n".join(lines))
    print("\n\n".join(blocks) if any_rows or len(targets) > 1 else "No files changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
