---
name: implementation-planner
description: Use when deciding the order to build the plans in docs/plans/, which plans can be built at the same time or by several builders, what the critical path is, or when docs/plans/implementation-plan.md is missing or out of date after a plan's Depends on or Status changed
---

# Planning the Build Order

## Overview

Read every plan in `docs/plans/` and write `docs/plans/implementation-plan.md`: which plan comes after which, which plans can be built at the same time, the critical path, and what collides when two plans are built at once. Two Unicode box-art diagrams show it.

**Core rule: the order is computed from the plans' Depends on lines, never chosen.** The script computes waves, slack, the critical path and builder lanes, and draws both diagrams. You add what needs reading: hidden dependencies, collisions, the options the index offers. You never edit a plan file, and never draw or touch a diagram by hand.

Plans come from splitting-decisions-into-plans; each one is built by implementation-agent. The output's sections and how to fill them: [output-format.md](output-format.md). Read it before step 4.

## Process

1. **Read `docs/plans/00-index.md` in full.** Note a plan it says every plan relies on (for example "the stack from plan 01 is implied for every plan"), and every order change it offers but does not apply (for example "plan 18 can move to just after 06").
2. **Run the script** from the repo root. On a refresh, first copy the old file's "Owner notes".

       python .claude/skills/implementation-planner/scripts/build_order.py docs/plans --implied 01 --out docs/plans/implementation-plan.md

   Leave out `--implied` if the index names no such plan. Exit 2 is a dependency cycle: the script writes nothing; stop and report the cycle to the owner.
3. **Read every plan**: header, Scope In, What we build, acceptance criteria. Find hidden dependencies (below). Run the script again with `--extra PLAN:NEEDS` for each one (repeat the flag), until you find no new ones.
4. **Fill each FILL section** as output-format.md says: open manual checks and lead times, collisions for every pair the script lists, hidden dependencies, options the index names, owner notes. Delete each FILL comment.
5. **Self-check**, then reply.

## Hidden dependencies

A plan has a hidden dependency when it uses something a lower plan builds (a table, column, endpoint, event or event field, component, tool, script or config key) and that plan is not among the plans it waits on, directly or through another plan.

- The script's FILL comment lists every line that names such a plan. A line that uses what that plan builds is a hidden dependency. A line that only points to where other work goes, or where a default comes from, is not.
- Names with no plan number: for each name in a plan's Scope In and What we build that the plan does not build itself, find the plan that does (the index's Coverage table and its notes on where tables land help). Not one the plan waits on: hidden dependency.
- Each hidden dependency: `--extra`, plus a finding that quotes the sentence and names the file and line.
- A line naming a higher plan is a pointer, never a dependency. If a criterion can only pass once that higher plan lands, add it as a finding.

## Self-check

- The script's own check passes. Use the same `--implied` and `--extra` flags as for the build: it fails on a FILL left, or on any script line (diagram, table, number) that was changed or dropped.

      python .claude/skills/implementation-planner/scripts/build_order.py docs/plans --implied 01 --verify docs/plans/implementation-plan.md

- Every `--extra` you passed has a finding with its sentence. Every collision row names a pair the script listed. Every option's waves come from a `--set` run.
- Only `implementation-plan.md` changed in `docs/plans/` (`git status docs/plans`).

## Common mistakes

| Mistake | Fix |
|---|---|
| Ordering by plan number, one long chain | Waves: plans in one wave can be built at the same time |
| Drawing or fixing a diagram by hand | Run the script again; boxes and waves come from it |
| "Can run in parallel" with no word on what collides | A collisions row for every shared name |
| Applying an order change the index only offers | List it under "Options the index names" |
| Days or weeks per plan | Waves are steps; the AC count shows size |
| Editing a plan's Depends on to fix a finding | Report it; the owner refreshes plans with splitting-decisions-into-plans |
| A hidden dependency judged from the plan number alone | Read the sentence: a use is a dependency, a pointer is not |
| Done (manual pending) treated as fully done | Say which later plans rely on each open check, and by when |
| Starting part of a plan early, or splitting one, to shorten the critical path | Keep the declared order; the owner splits plans with splitting-decisions-into-plans |

## Final reply

The path, and created or refreshed. Start now. Number of waves, the critical path, builders needed. Each wave with two or more plans, with its collisions. Findings and hidden dependencies, each with what the owner should change in which plan.
