# Plan files: layout

The rules are in [SKILL.md](SKILL.md). Write to `docs/plans/` unless the owner names another folder.

File names: `00-index.md`, then `NN-<name>.md` in kebab-case, numbered in build order. Main-flow plans come first, then feature plans, then `observability`, `evaluation` and `monitoring` as the last three (unless the source places one earlier; see "Signals: where they go" in SKILL.md). A plan added on a refresh takes a letter after the plan it follows: `17a-<name>.md`.

## 00-index.md

```markdown
# <Project> — plans

Source: <path> (<its date or status line>). Built on <today's date>.
Tags: from the source | mapped by us (stated choice = [DECIDED], listed open point = [OPEN]). Added by us: [ADDED].

## Plans

| # | Plan | Group | Outcome: what someone can do or see after it | Depends on | Status |
|---|---|---|---|---|---|
| 01 | [Edge & ingress](01-edge-and-ingress.md) | Main flow | ... | – | Ready |
| 04 | [UI foundation](04-ui-foundation.md) | Main flow | ... | 03 | Ready |
| 06 | [<Feature>](06-<feature>.md) | Feature | ... | 05 | Blocked by Q3 |
| 18 | [Observability](18-observability.md) | Signals | ... | 05–17 | Ready |

Status: Ready · Blocked by Q# · In progress · Done · Done (manual pending). The builder updates it as work moves.

## Why this order
3-6 bullets. Name where the order differs from the source's own phases, and what that costs.

## Coverage
| Source item (§ or ID) | Lands in |
|---|---|
| §4 Offline crawl | 02 |
| §12 Reranker | Not planned |
| §9 Old export | 06 (removed from source, <date>) |
| §10 Nightly check: job | 18 |
| §10 Nightly check: alert | 19 |

## Release checklist
System-wide checks the source demands before launch, each with its source and how it is checked (a skill, a script or a person). "None" if the source has none.

## Design only
| Item | Where its design lives (§ or ID) | What the design document must show, if the source says |
|---|---|---|
"None" if the source builds everything it designs.

## Not planned
| Item | Add it when (trigger from the source) | Source |
|---|---|---|
If the source gives no trigger, write "None given" and add a line to "Gaps found".

## Gaps found
Our own findings, not the source's. One line each: the gap, the plan it affects, a suggested default tagged [ADDED].
```

## NN-<name>.md

```markdown
# Plan NN — <Name>

Group: Main flow | Feature | Signals · Depends on: <plan numbers or –> · Status: Ready | Blocked by Q# | In progress | Done | Done (manual pending) · Source: <§ list or IDs>

## Goal
1-2 sentences: who can now do or see what, that they could not before.

## Scope
- **In:** bullets with the concrete names from the source (endpoints, tables, tools, components)
- **Out:** each item with the plan it goes to, or "Not planned"

## Decisions used
| Source ID or § | Decision or assumption, in a few words | Tag |
|---|---|---|

## What we build
Bullets grouped by part (data, backend, UI, jobs). Refer to the source by § for detail; do not copy it.

## Signals
- **Observability:** the log fields, events or spans this feature needs
- **Evaluation:** the test cases or suite this feature needs
- **Monitoring:** the metric and alert this feature needs
(Feature plans only. Write "None, because ..." if a line truly has nothing.)

## Acceptance criteria
- [ ] **AC-NN.1** Given ..., when ..., then ....
  - Check: ... · Source: ... [TAG]
  (Add "(manual)" after the check if no machine can run it, and say what it needs, for example a real account.)

## Open questions
| Q (source ID) | Question | Default we assume until answered | Blocks the plan? |
|---|---|---|---|
"Blocks" = yes when the source gives no default, or says the question blocks the build (for example P0). "None" if the plan uses no [OPEN] or [CONFLICT] item. Q is the source's ID. A point the source does not state, or a conflict we find between its sections, gets our own ID Q-NS-n (see SKILL.md).
```

Main-flow plans and the three Signals plans leave out the Signals section. The Signals plans list the feature plans' Signals lines in their scope instead.
