#!/usr/bin/env python3
"""Build order for the plans in docs/plans/: waves, slack, critical path, builder lanes.

Reads 00-index.md and every NN-*.md plan, and writes a draft of implementation-plan.md
with two Unicode box-art diagrams. Sections the skill fills by judgment are marked
<!-- FILL: ... -->.

    python build_order.py docs/plans --implied 01 --extra 15:10 --out docs/plans/implementation-plan.md

--implied  a plan every later plan depends on, when 00-index.md says so
--extra    a hidden dependency found by reading the plans: PLAN:NEEDS (repeatable)
--set      what if a plan's Depends on were replaced: PLAN=DEPS, e.g. 18=02-06
           (repeatable); prints the changed waves and writes nothing
--verify   check a filled file: every line the script writes is still there, no FILL left

Exit codes: 0 ok, 1 bad input or failed --verify, 2 dependency cycle (nothing written).
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import re
import sys
from pathlib import Path

ID = r"\d{2}[a-z]?"
PLAN_FILE = re.compile(rf"^({ID})-.+\.md$")
ID_WORD = re.compile(rf"\b({ID})\b")
RANGE = re.compile(rf"\b({ID})\s*[–—-]\s*({ID})\b")
AC_LINE = re.compile(r"^\s*- \[[ xX]\] \*\*AC-", re.M)
AC_ITEM = re.compile(r"^\s*- \[([ xX])\] \*\*(AC-[\w.]+)\*\*\s*(.*)$")
QUESTION = re.compile(r"\bQ[\w-]*\d")
MENTION = re.compile(rf"\bplans?\s+({ID}(?:\s*(?:,|and|or|[–—-])\s*{ID})*)", re.I)

BOX_W = 30  # outer width of one plan box
PER_ROW = 3  # boxes side by side in a wave band
GAP = 3
INDENT = 2
MAX_COLS = 100


def key(pid: str) -> tuple[int, str]:
    return int(pid[:2]), pid[2:]


def ids_in(text: str, known: set[str]) -> set[str]:
    """Plan ids named in a "Depends on" value; ranges such as 01–16 expand to known plans."""
    found = set()
    for a, b in RANGE.findall(text):
        found |= {p for p in known if key(a) <= key(p) <= key(b)}
    return found | set(ID_WORD.findall(RANGE.sub(" ", text)))


def read_index(path: Path) -> tuple[str, dict]:
    project, rows = path.parent.name, {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# ") and project == path.parent.name:
            project = re.sub(r"\s+[—–-]\s+plans\s*$", "", line[2:]).strip()
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # Plan table: | # | Plan | Group | Outcome | Depends on | Status |
        if len(cells) >= 6 and re.fullmatch(ID, cells[0]):
            name = re.match(r"\[([^\]]+)\]", cells[1])
            rows[cells[0]] = {
                "name": name.group(1) if name else cells[1],
                "deps": cells[-2],
                "status": cells[-1],
            }
    return project, rows


def read_plan(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    title = re.search(rf"^# Plan {ID}\s*[—–-]\s*(.+)$", text, re.M)
    header = re.search(r"^Group:.*Depends on:.*$", text, re.M)
    fields = {}
    if header:
        for part in header.group(0).split("·"):
            name, _, value = part.partition(":")
            fields[name.strip()] = value.strip()
    # Lines that name other plans, outside the header and the Scope "Out" list; and the
    # unticked criteria, with whether their Check needs a person. A Check line belongs to
    # the criterion just above it, so a ticked criterion's Check never marks an open one.
    mentions, open_acs, in_out, last_open = [], [], False, False
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("## ") or re.match(r"\s*- \*\*In:\*\*", line):
            in_out = False
        if re.match(r"\s*- \*\*Out:\*\*", line):
            in_out = True
        if not in_out and not line.startswith("Group:"):
            mentions += [(n, m) for m in MENTION.findall(line)]
        if ac := AC_ITEM.match(line):
            last_open = ac.group(1) == " "
            if last_open:
                open_acs.append({"id": ac.group(2), "text": ac.group(3), "manual": False})
        elif last_open and re.match(r"\s*- Check:", line) and "(manual)" in line:
            open_acs[-1]["manual"] = True
    return {
        "name": title.group(1).strip() if title else path.stem,
        "deps": fields.get("Depends on"),
        "status": fields.get("Status"),
        "ac": len(AC_LINE.findall(text)),
        "file": path.name,
        "mentions": mentions,
        "open_acs": open_acs,
    }


def state_of(status: str) -> str:
    s = (status or "").strip()
    if s.startswith("Done"):
        return "done-manual" if "manual" in s else "done"
    if s.startswith("In progress"):
        return "building"
    if s.startswith("Blocked"):
        return "blocked"
    return "ready"


def fit(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1] + "…"


def find_cycle(rest: set[str], deps: dict) -> list[str]:
    p, seen = min(rest, key=key), []
    while p not in seen:
        seen.append(p)
        p = min(deps[p] & rest, key=key)
    return seen[seen.index(p):] + [p]


def schedule(deps: dict) -> tuple[list, dict, dict, dict]:
    """Topological order, wave, latest wave and dependants; a cycle raises ValueError."""
    succ = {p: set() for p in deps}
    for p, ds in deps.items():
        for d in ds:
            succ[d].add(p)
    indegree = {p: len(deps[p]) for p in deps}
    ready = sorted((p for p in deps if not indegree[p]), key=key)
    order = []
    while ready:
        p = ready.pop(0)
        order.append(p)
        for s in succ[p]:
            indegree[s] -= 1
            if not indegree[s]:
                ready.append(s)
        ready.sort(key=key)
    if len(order) < len(deps):
        raise ValueError(" needs ".join(find_cycle(set(deps) - set(order), deps)))
    wave, latest = {}, {}
    for p in order:
        wave[p] = 1 + max((wave[d] for d in deps[p]), default=-1)
    last = max(wave.values())
    for p in reversed(order):
        latest[p] = min((latest[s] - 1 for s in succ[p]), default=last)
    return order, wave, latest, succ


def what_if(deps: dict, changes: list[str], known: set[str], implied: str | None = None) -> int:
    """Print how the waves change if some plans' Depends on were replaced. Writes nothing.

    The --implied plan stays a dependency of every later plan, as in the real build."""
    new = {p: set(ds) for p, ds in deps.items()}
    for item in changes:
        p, _, value = item.partition("=")
        if p not in known:
            print(f"--set {item}: unknown plan", file=sys.stderr)
            return 1
        new[p] = ids_in(value, known) & known
        if implied and implied in known and key(implied) < key(p):
            new[p].add(implied)
    try:
        _, wave, latest, _ = schedule(deps)
        _, wave2, latest2, _ = schedule(new)
    except ValueError as cycle:
        print(f"Dependency cycle, no order possible: {cycle}", file=sys.stderr)
        return 2
    last, last2 = max(wave.values()), max(wave2.values())
    print(f"What if {'; '.join(changes)} (nothing written)")
    print(f"Finish: wave {last2 + 1} (now {last + 1})")
    moved = [
        f"{p}: wave {wave[p] + 1} → {wave2[p] + 1}, slack {latest[p] - wave[p]} → {latest2[p] - wave2[p]}"
        for p in sorted(deps, key=key)
        if (wave[p], latest[p]) != (wave2[p], latest2[p])
    ]
    print("Changed: " + ("; ".join(moved) if moved else "none"))
    for w in range(last2 + 1):
        print(f"Wave {w + 1}: " + ", ".join(sorted((p for p in new if wave2[p] == w), key=key)))
    return 0


def verify(path: Path, text: str) -> int:
    """Check a filled file still holds every line the script writes, in order, and no FILL.

    Blank lines are not compared: deleting a FILL comment leaves two in a row, and a
    Markdown formatter may merge them."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if left := [n for n, line in enumerate(lines, 1) if "FILL:" in line]:
        print(f"{path}: FILL left on line(s) {', '.join(map(str, left))}")
        return 1
    it = iter(lines)
    for line in text.splitlines():
        if line.startswith("<!-- FILL:") or not line.strip():
            continue
        if not any(line == got for got in it):
            print(f"{path}: changed or missing script line: {line!r}")
            return 1
    print(f"{path}: OK, every script line is there and no FILL is left")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("plans_dir", nargs="?", default="docs/plans")
    ap.add_argument("--implied", help="plan every later plan depends on (e.g. 01)")
    ap.add_argument("--extra", action="append", default=[], metavar="PLAN:NEEDS")
    ap.add_argument("--set", action="append", default=[], metavar="PLAN=DEPS")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--out", help="file to write; default stdout")
    ap.add_argument("--verify", metavar="FILE")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    if a.verify:
        built = re.search(r"^Built on (\d{4}-\d{2}-\d{2})", Path(a.verify).read_text(encoding="utf-8"), re.M)
        a.date = built.group(1) if built else a.date

    plans_dir = Path(a.plans_dir)
    index_path = plans_dir / "00-index.md"
    if not index_path.is_file():
        print(f"No {index_path}", file=sys.stderr)
        return 1
    project, index = read_index(index_path)
    plans = {
        m.group(1): read_plan(f)
        for f in sorted(plans_dir.iterdir())
        if (m := PLAN_FILE.match(f.name)) and m.group(1) != "00"
    }
    if not plans:
        print(f"No NN-*.md plans in {plans_dir}", file=sys.stderr)
        return 1
    known = set(plans)
    findings = []

    for p in sorted(set(index) - known, key=key):
        findings.append(f"Plan {p} is in the index table but has no file; left out.")
    deps, status = {}, {}
    for p in sorted(plans, key=key):
        plan, row = plans[p], index.get(p)
        if row is None:
            findings.append(f"Plan {p} ({plan['file']}) is not in the index table.")
        from_index = ids_in(row["deps"], known) if row else set()
        from_header = ids_in(plan["deps"], known) if plan["deps"] is not None else set()
        if row and plan["deps"] is not None and from_index != from_header:
            findings.append(
                f"Plan {p}: the index says Depends on {row['deps']}, the plan header says "
                f"{plan['deps']}. Both are used."
            )
        deps[p] = from_index | from_header
        if a.implied and a.implied in known and key(a.implied) < key(p):
            deps[p].add(a.implied)
        status[p] = row["status"] if row else (plan["status"] or "Ready")
        if row and plan["status"] and state_of(row["status"]) != state_of(plan["status"]):
            findings.append(
                f"Plan {p}: the index says Status {row['status']}, the plan header says "
                f"{plan['status']}. The index is used."
            )
    for item in a.extra:
        p, _, d = item.partition(":")
        if p not in known or d not in known:
            print(f"--extra {item}: unknown plan", file=sys.stderr)
            return 1
        if d not in deps[p]:
            deps[p].add(d)
            findings.append(f"Plan {p} needs plan {d}, which its Depends on leaves out (added).")
    for p in sorted(plans, key=key):
        for d in sorted(deps[p] - known, key=key):
            findings.append(f"Plan {p} depends on plan {d}, which does not exist; ignored.")
        deps[p] &= known
        for d in sorted(deps[p], key=key):
            if key(d) >= key(p):
                findings.append(f"Plan {p} depends on plan {d}, a later number.")

    if a.set:
        return what_if(deps, a.set, known, a.implied)
    try:
        order, wave, latest, succ = schedule(deps)
    except ValueError as cycle:
        print(f"Dependency cycle, no order possible: {cycle}", file=sys.stderr)
        return 2

    state = {p: state_of(status[p]) for p in plans}
    done = {p for p in plans if state[p] in ("done", "done-manual")}
    ancestors, waits = {}, {}
    for p in order:
        ancestors[p] = set(deps[p]).union(*(ancestors[d] for d in deps[p]))
        own = set(QUESTION.findall(status[p])) if state[p] == "blocked" else set()
        waits[p] = own.union(*(waits[d] for d in deps[p] if d not in done))
    last = max(wave.values())
    slack = {p: latest[p] - wave[p] for p in plans}
    after = {
        p: {d for d in deps[p] if not any(d in ancestors[e] for e in deps[p] if e != d)}
        for p in plans
    }

    # Builder lanes: lane 1 holds the critical path; every other plan takes the lowest
    # lane with a free wave between its earliest start and its latest wave.
    lanes, slot_of = [{}], {}
    for w in range(last + 1):
        p = min((q for q in plans if wave[q] == w and slack[q] == 0), key=key)
        lanes[0][w], slot_of[p] = p, w
    for p in sorted((q for q in plans if q not in slot_of), key=lambda q: (latest[q], key(q))):
        lo = 1 + max((slot_of[d] for d in deps[p]), default=-1)
        hi = wave[p] if p in done else latest[p]
        lo = min(lo, hi) if p in done else lo
        for lane in lanes:
            free = [w for w in range(lo, hi + 1) if w not in lane]
            if free:
                lane[free[0]], slot_of[p] = p, free[0]
                break
        else:
            lanes.append({lo: p})
            slot_of[p] = lo

    def name(p: str) -> str:
        return index[p]["name"] if p in index else plans[p]["name"]

    def state_text(p: str) -> str:
        if state[p] == "done":
            return "done"
        if state[p] == "done-manual":
            return "done, manual open"
        if state[p] == "building":
            return "in progress"
        if waits[p]:
            return "waits on " + ", ".join(sorted(waits[p]))
        return f"slack {slack[p]}"

    def ids(items) -> str:
        return ", ".join(sorted(items, key=key)) or "–"

    # Diagram 1: build waves.
    band = INDENT + PER_ROW * BOX_W + (PER_ROW - 1) * GAP
    inner = BOX_W - 4

    def box(p: str) -> list[str]:
        crit = slack[p] == 0
        h, v, tl, tr, bl, br = ("═", "║", "╔", "╗", "╚", "╝") if crit else ("─", "│", "┌", "┐", "└", "┘")
        lines = [f"{p} {name(p)}", f"after {ids(after[p])}", f"{plans[p]['ac']} AC · {state_text(p)}"]
        return (
            [tl + h * (BOX_W - 2) + tr]
            + [f"{v} {fit(line, inner):<{inner}} {v}" for line in lines]
            + [bl + h * (BOX_W - 2) + br]
        )

    d1 = [
        f"BUILD WAVES · {len(plans)} plans · {last + 1} waves",
        "╔═╗ critical path (slack 0)   ┌─┐ can wait <slack> waves   after = plans done first",
        "",
    ]
    for w in range(last + 1):
        members = sorted((p for p in plans if wave[p] == w), key=lambda p: (slack[p] != 0, key(p)))
        label = f"WAVE {w + 1}" + (f" · {len(members)} at once" if len(members) > 1 else "")
        d1.append(label + " " + "─" * (band - len(label) - 1))
        for i in range(0, len(members), PER_ROW):
            row = [box(p) for p in members[i : i + PER_ROW]]
            for j in range(len(row[0])):
                d1.append(" " * INDENT + (" " * GAP).join(b[j] for b in row))
        if w < last:
            d1.append(" " * (band // 2) + "▼")

    # Diagram 2: builder lanes.
    idw = max(len(p) for p in plans)
    slot = idw + 3  # bracket, id, bracket, connector
    label_w = len(f"builder {len(lanes)}") + 1
    per_chunk = max(1, (MAX_COLS - label_w) // slot)
    d2 = [
        f"BUILDER LANES · {len(lanes)} builders · finish in wave {last + 1}",
        "[NN] to build   (NN) done   ━ critical path   ─ same builder, next wave",
        "",
    ]
    for start in range(0, last + 1, per_chunk):
        ws = range(start, min(last + 1, start + per_chunk))
        d2.append(" " * label_w + "".join(f"W{w + 1}".ljust(slot) for w in ws).rstrip())
        for i, lane in enumerate(lanes):
            row = ""
            for w in ws:
                p = lane.get(w)
                cell = (f"({p:<{idw}})" if p in done else f"[{p:<{idw}}]") if p else " " * (idw + 2)
                joined = p and lane.get(w + 1) and w + 1 in ws
                row += cell + (("━" if i == 0 else "─") if joined else " ")
            d2.append(f"builder {i + 1}".ljust(label_w) + row.rstrip())
        d2.append("")
    d2.pop()

    # Plans that can be built at the same time: same wave, or same column in the lanes.
    def pairs(groups) -> list[str]:
        out = []
        for members in groups:
            todo = sorted((p for p in members if p not in done), key=key)
            out += [f"{x} + {y}" for x, y in itertools.combinations(todo, 2)]
        return out

    wave_pairs = {w: pairs([[p for p in plans if wave[p] == w]]) for w in range(last + 1)}
    lane_pairs = {w: pairs([[lane[w] for lane in lanes if w in lane]]) for w in range(last + 1)}
    pair_lines = []
    for w in range(last + 1):
        extra = [x for x in lane_pairs[w] if x not in wave_pairs[w]]
        parts = []
        if wave_pairs[w]:
            parts.append("same wave: " + ", ".join(wave_pairs[w]))
        if extra:
            parts.append("builder lanes: " + ", ".join(extra))
        if parts:
            pair_lines.append(f"- Wave {w + 1}: " + "; ".join(parts))

    building = sorted((p for p in plans if state[p] == "building"), key=key)
    start_now = [
        p
        for p in order
        if p not in done and state[p] == "ready" and not waits[p] and deps[p] <= done
    ]
    crit_chain = " → ".join(
        " + ".join(sorted((p for p in plans if wave[p] == w and slack[p] == 0), key=key))
        for w in range(last + 1)
    )

    md = [
        f"# {project} — implementation plan",
        "",
        f"Built on {a.date} from `00-index.md` and {len(plans)} plan files by the "
        "implementation-planner skill. Rebuild it when a plan's Depends on or Status changes; "
        'edit only "Owner notes" by hand.',
        "",
        "How to read it: a wave is a step, not a length of time. Plans in the same wave do not "
        "depend on each other and can be built at the same time. A plan can start as soon as "
        "every plan in its *after* list is done, and can wait up to its slack (in waves) without "
        "moving the finish. Plans differ in size: AC is the number of acceptance criteria.",
        "",
        "## Start now",
        "",
    ]
    if building:
        md.append("In progress: " + ", ".join(f"**{p}** {name(p)}" for p in building) + ".")
        md.append("")
    if start_now:
        md += [f"- **{p}** {name(p)} · wave {wave[p] + 1} · slack {slack[p]}" for p in start_now]
    else:
        md.append("Nothing: every plan not done waits on a plan in progress, or on an open question.")
    md += ["", "## Build waves", "", "```text", *d1, "```", ""]
    md += ["## Builder lanes", "", "```text", *d2, "```", ""]
    md.append(
        f"{len(lanes)} builders are enough to finish in wave {last + 1}. More builders do not "
        f"finish sooner: the critical path is {last + 1} plans in a row. With fewer builders, "
        "build the critical path first and fit the other plans into the waves their slack allows."
    )
    if all(key(d) < key(p) for p in plans for d in deps[p]):
        md[-1] += " One builder: plan-number order works, since every plan depends only on lower numbers."
    md += ["", "## Critical path", "", crit_chain, "", "A delay on any of these plans delays the finish.", ""]
    md += ["## Open manual checks and lead times", ""]
    manual_open = [
        (p, ac)
        for p in order
        if state[p] == "done-manual"
        for ac in plans[p]["open_acs"]
    ]
    if manual_open:
        md.append(
            "Plans marked Done (manual pending) count as done for the plans after them, unless a "
            "later plan relies on what an open check proves. Open criteria:"
        )
        md.append("")
        md += [
            f"- **{ac['id']}** ({name(p)}): {fit(ac['text'], 140)}"
            + ("" if ac["manual"] else " · Check has no (manual) part")
            for p, ac in manual_open
        ]
        md.append("")
        md.append(
            "<!-- FILL: for each open criterion above, the later plans that rely on what it "
            "proves, and by when it must be done (see output-format.md). Then delete this comment. -->"
        )
    else:
        md.append("No plan is Done (manual pending).")
    md += [
        "",
        "<!-- FILL: lead times: accounts, keys or access the plans need that take time to "
        'arrange, with the first plan that needs each, or "None found." Then delete this comment. -->',
        "",
    ]
    md += [
        "## Plans",
        "",
        "| Plan | Wave | Latest wave | Slack | After | Builder | AC | Status |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for p in order:
        lane_no = next(i + 1 for i, lane in enumerate(lanes) if lane.get(slot_of[p]) == p)
        md.append(
            f"| [{p} {name(p)}]({plans[p]['file']}) | {wave[p] + 1} | {latest[p] + 1} | {slack[p]} "
            f"| {ids(after[p])} | {lane_no} (wave {slot_of[p] + 1}) | {plans[p]['ac']} | {status[p]} |"
        )
    md += ["", "## Parallel work: what collides", ""]
    if pair_lines:
        md += ["Plans that can be built at the same time:", "", *pair_lines, ""]
        md.append(
            "<!-- FILL: one table row per name two plans of a pair above both add or change "
            "(see output-format.md). No shared name: write that. Then delete this comment. -->"
        )
    else:
        md.append("None: no two plans that are not done can be built at the same time.")
    md += [
        "",
        "## How to run a wave",
        "",
        "- One builder per plan: run implementing-plans with the plan named. It pulls `main` and "
        "builds on its own branch, `plan/NN-<name>`. Builders working at the same time each need "
        "their own worktree (superpowers:using-git-worktrees).",
        "- Merge each plan when it is done. The plan that merges second rebases first; if both "
        "add a schema migration, it re-chains its migration onto the one already merged, so "
        "there is one head.",
        "- Run the full suite after each merge. Then the owner sets the plan's Status in "
        "`00-index.md` and in the plan header (builders never write Status), and rebuilds this file.",
        "- After the last wave, work the Release checklist in `00-index.md`.",
        "",
        "## Dependency findings",
        "",
    ]
    md += [f"- {f}" for f in findings] or ["- Index and plan headers agree on every Depends on and Status."]
    candidates = [
        f"{plans[p]['file']}:{n} names plan {d}"
        for p in sorted(plans, key=key)
        for n, text in plans[p]["mentions"]
        for d in sorted(ids_in(text, known), key=key)
        if key(d) < key(p) and d not in ancestors[p]
    ]
    md += [
        "",
        "<!-- FILL: each hidden dependency, with the plan sentence that shows it, or "
        '"No hidden dependencies found." Then delete this comment. '
        "Lines that name a lower plan this plan does not wait on: "
        + ("; ".join(candidates) if candidates else "none")
        + ". -->",
        "",
        "## Options the index names",
        "",
        "<!-- FILL: order changes 00-index.md offers but does not apply, and what each would "
        'change in the waves, or "None." Then delete this comment. -->',
        "",
        "## Owner notes",
        "",
        '<!-- FILL: this section from the previous file, word for word, or "None yet." '
        "Then delete this comment. -->",
        "",
    ]
    text = "\n".join(md)
    if a.verify:
        return verify(Path(a.verify), text)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8", newline="\n")
        print(f"Wrote {a.out}: {len(plans)} plans, {last + 1} waves, {len(lanes)} builders")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
