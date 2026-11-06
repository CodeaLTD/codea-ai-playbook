#!/usr/bin/env python3
"""Check docs/plans/ against the splitting-decisions-into-plans rules.

    python check_plans.py docs/plans --source requirements/decision.md

Checks each plan's title and header, its acceptance criteria (3-8, AC-NN.k IDs, a Check and
a Source on each), the three Signals lines of feature plans, and Depends on; the index's plan
table, Coverage table and Not planned triggers. With --source, also checks that every tagged
decision heading and NFR row of the source is in Coverage, and that every number in the plans
appears in the source. Prints file:line: problem. Writes nothing.

Exit codes: 0 nothing found, 1 problems found, 2 bad input.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ID = r"\d{2}[a-z]?"
PLAN_FILE = re.compile(rf"^({ID})-.+\.md$")
ID_WORD = re.compile(rf"\b({ID})\b")
RANGE = re.compile(rf"\b({ID})\s*[–—-]\s*({ID})\b")
AC_ITEM = re.compile(rf"^\s*- \[[ xX]\] \*\*AC-({ID})\.(\d+)\*\*")
TAGS = ("[DECIDED]", "[PROPOSED]", "[OPEN]", "[NOT SPECIFIED]", "[CONFLICT]")
SEPARATOR = re.compile(r"^\|?\s*:?-{2,}")
PLACES = ("not planned", "design only", "release checklist")
# Stripped before numbers are compared with the source: references, not claims.
REFS = [
    re.compile(r"\]\([^)]*\)"),  # link targets
    re.compile(rf"\b{ID}-[\w.-]+\.md\b"),  # plan file names
    re.compile(rf"\b[Pp]lans?\s+{ID}(?:\s*(?:,|and|or|[–—-])\s*{ID})*"),  # "plan 03", "plans 02-06"
    re.compile(rf"^\s*\|\s*{ID}(?:\s*(?:,|and|[–—-])\s*{ID})*\s*(?=\|)"),  # a table row keyed by plan number
    re.compile(rf"(?:→|->)\s*{ID}(?:\s*\([^)]*\))?(?:\s*(?:,|and|or|[–—-])\s*{ID}(?:\s*\([^)]*\))?)*"),  # "→ 08 (same page), 09"
    re.compile(r"\b(?:AC|Q-NS|[A-Z]{1,4})-?\d+(?:\.\d+)*[a-z]?\b"),  # AC-01.2, Q-NS-1, NFR3, A1, Q7
    re.compile(r"§\s*\d+(?:\.\d+)*"),  # § references
    re.compile(r"^\s*\d+[.)]\s"),  # numbered-list markers
]
NUMBER = re.compile(r"(?<![\w.,§/-])\d+(?:[.,]\d+)*")


def key(pid: str) -> tuple[int, str]:
    return int(pid[:2]), pid[2:]


def ids_in(text: str, known: set[str]) -> set[str]:
    found = set()
    for a, b in RANGE.findall(text):
        found |= {p for p in known if key(a) <= key(p) <= key(b)}
    return found | set(ID_WORD.findall(RANGE.sub(" ", text)))


def cells(row: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<!\\)\|", row.strip().strip("|"))]


def section(lines: list[str], title: str) -> list[tuple[int, str]]:
    """Lines of the '## <title>' section, numbered from 1."""
    out, inside = [], False
    for n, line in enumerate(lines, 1):
        if line.startswith("## "):
            inside = line[3:].strip().lower().startswith(title.lower())
            continue
        if inside:
            out.append((n, line))
    return out


def table_rows(lines: list[tuple[int, str]]) -> list[tuple[int, list[str]]]:
    rows = [(n, cells(s)) for n, s in lines if s.strip().startswith("|") and not SEPARATOR.match(s.strip())]
    return rows[1:]  # drop the header row


def in_source(num: str, source: str, flat: str) -> bool:
    pattern = rf"(?<![\d.,]){re.escape(num)}(?![\d]|[.,]\d)"
    return bool(re.search(pattern, source) or re.search(pattern.replace(",", ""), flat))


def check_plan(path: Path, pid: str, known: set[str], out: list[str]) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    name = path.name

    def problem(n: int, msg: str) -> None:
        out.append(f"{name}:{n}: {msg}")

    title = next((n for n, l in enumerate(lines, 1) if re.match(rf"^# Plan {ID}\s*[—–-]", l)), None)
    if title is None:
        problem(1, 'no title "# Plan NN — <Name>"')
    elif not lines[title - 1].startswith(f"# Plan {pid} ") and not lines[title - 1].startswith(f"# Plan {pid}—"):
        problem(title, f"title number does not match the file name ({pid})")
    header = next(((n, l) for n, l in enumerate(lines, 1) if l.startswith("Group:")), None)
    fields = {}
    if header is None:
        problem(1, "no header line (Group: · Depends on: · Status: · Source:)")
    else:
        for part in header[1].split("·"):
            k, _, v = part.partition(":")
            fields[k.strip()] = v.strip()
        for k in ("Group", "Depends on", "Status", "Source"):
            if not fields.get(k):
                problem(header[0], f"header has no {k}")
        for d in sorted(ids_in(fields.get("Depends on", ""), known | {pid}), key=key):
            if d not in known:
                problem(header[0], f"depends on plan {d}, which has no file")
            elif key(d) >= key(pid):
                problem(header[0], f"depends on plan {d}, not a lower number")
    group = fields.get("Group", "")

    acs, seen = [], set()
    for i, line in enumerate(lines):
        if not (m := AC_ITEM.match(line)):
            continue
        n, ac = i + 1, f"AC-{m.group(1)}.{m.group(2)}"
        acs.append(ac)
        if m.group(1) != pid:
            problem(n, f"{ac} does not carry the plan number {pid}")
        if ac in seen:
            problem(n, f"{ac} appears twice")
        seen.add(ac)
        rest = []
        for follow in lines[i + 1 :]:
            if AC_ITEM.match(follow) or follow.startswith("#"):
                break
            rest.append(follow)
        check_line = next((l for l in rest if re.match(r"\s*- Check:", l)), None)
        if check_line is None:
            problem(n, f"{ac} has no Check line")
        elif "Source:" not in check_line:
            problem(n, f"{ac} has no Source on its Check line")
    if not group.startswith("Signals") and not 3 <= len(acs) <= 8:
        problem(title or 1, f"{len(acs)} acceptance criteria (3-8 per plan)")

    if group.startswith("Feature"):
        signals = " ".join(l for _, l in section(lines, "Signals"))
        for part in ("Observability", "Evaluation", "Monitoring"):
            if f"**{part}:**" not in signals:
                problem(title or 1, f"feature plan has no **{part}:** line under Signals")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("plans_dir", nargs="?", default="docs/plans")
    ap.add_argument("--source", help="the decision record the plans were built from")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")

    plans_dir = Path(a.plans_dir)
    index_path = plans_dir / "00-index.md"
    if not index_path.is_file():
        print(f"No {index_path}", file=sys.stderr)
        return 2
    files = {m.group(1): f for f in sorted(plans_dir.iterdir()) if (m := PLAN_FILE.match(f.name)) and m.group(1) != "00"}
    known = set(files)
    out: list[str] = []
    texts = {pid: check_plan(f, pid, known, out) for pid, f in sorted(files.items(), key=lambda x: key(x[0]))}

    index = index_path.read_text(encoding="utf-8").splitlines()
    in_table = set()
    for n, line in table_rows(section(index, "Plans")):
        if len(line) >= 6 and re.fullmatch(ID, line[0]):
            in_table.add(line[0])
            if line[0] not in known:
                out.append(f"00-index.md:{n}: plan {line[0]} is in the table but has no file")
    for pid in sorted(known - in_table, key=key):
        out.append(f"00-index.md:1: plan {pid} ({files[pid].name}) is not in the Plans table")

    coverage, items = table_rows(section(index, "Coverage")), {}
    if not coverage:
        out.append("00-index.md:1: no Coverage table")
    for n, row in coverage:
        item, lands = row[0], (row[1] if len(row) > 1 else "")
        if item in items:
            out.append(f"00-index.md:{n}: \"{item}\" is in Coverage twice (also line {items[item]})")
        items.setdefault(item, n)
        target = re.match(ID, lands)
        if target and target.group(0) not in known:
            out.append(f"00-index.md:{n}: \"{item}\" lands in plan {target.group(0)}, which has no file")
        elif not target and not lands.lower().startswith(PLACES):
            out.append(f'00-index.md:{n}: "{item}" lands in "{lands}": not a plan, Not planned, Design only or Release checklist')
    for n, row in table_rows(section(index, "Not planned")):
        if len(row) < 2 or not row[1]:
            out.append(f"00-index.md:{n}: Not planned row \"{row[0]}\" has no trigger (write \"None given\")")

    if a.source:
        src_path = Path(a.source)
        if not src_path.is_file():
            print(f"No {src_path}", file=sys.stderr)
            return 2
        source = src_path.read_text(encoding="utf-8")
        flat = source.replace(",", "")
        wanted = {}
        for n, line in enumerate(source.splitlines(), 1):
            if (m := re.match(r"^#{2,4}\s+(\d+\.\d+[a-z]?)\b", line)) and any(t in line for t in TAGS):
                wanted.setdefault(m.group(1), n)
            if m := re.match(r"^\|\s*(NFR\d+)\s*\|", line):
                wanted.setdefault(m.group(1), n)
        covered = set()
        for _, row in coverage:
            covered |= set(re.findall(r"\bNFR\d+\b|(?<![\d.])\d+\.\d+[a-z]?\b", row[0]))
        if not wanted:
            out.append(f"{src_path.name}:1: no tagged decision headings or NFR rows found; check Coverage by hand")
        for item, n in sorted(wanted.items(), key=lambda x: x[1]):
            if item not in covered:
                out.append(f"00-index.md:1: source item {item} ({src_path.name}:{n}) is not in the Coverage table")
        for pid, lines in sorted(texts.items(), key=lambda x: key(x[0])):
            in_out = False  # the Scope "Out" list only points to other plans
            for n, line in enumerate(lines, 1):
                s = line.strip()
                if line.startswith("## ") or re.match(r"\s*- \*\*In:\*\*", line):
                    in_out = False
                if re.match(r"\s*- \*\*Out:\*\*", line):
                    in_out = True
                elif in_out and s and not line[:1].isspace() and not line.startswith(("-", "*")):
                    in_out = False  # the Out list ended
                if in_out or not s or s.startswith(("# Plan", "Group:")) or SEPARATOR.match(s):
                    continue
                text = line
                for ref in REFS:
                    text = ref.sub(" ", text)
                for num in NUMBER.findall(text):
                    if not in_source(num, source, flat):
                        added = " (line tagged [ADDED])" if "[ADDED]" in line else ""
                        out.append(f"{files[pid].name}:{n}: number {num} is not in the source{added}")

    for line in out:
        print(line)
    print(f"Summary: {len(files)} plans · {len(out)} problem(s)")
    return 1 if out else 0


if __name__ == "__main__":
    sys.exit(main())
