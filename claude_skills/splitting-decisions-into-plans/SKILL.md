---
name: splitting-decisions-into-plans
description: Use when turning decision.md, decisions.md, an architecture plan or another design record into ordered feature plans, a build order, delivery steps or phases, or when each step of the build needs its own acceptance criteria, or when the plans in docs/plans/ may be out of date after the decision record changed
---

# Splitting Decisions into Plans

## Overview

Turn one decision record into numbered build plans, in this order:

1. **Main flow:** one plan per architecture part on the main user's path, then one plan that completes the flow. If the product has a UI, one part is the UI foundation.
2. **Features:** one plan per feature.
3. **Signals, last unless the source says otherwise:** Observability, then Evaluation, then Monitoring.

**Core rule: plans report what the source says.** Every number and decision comes from the source. Anything you add is tagged [ADDED] and listed under "Gaps found" in the index. [PROPOSED] stays the source's own tag (a suggestion nobody has approved); never use it for something we added. Every plan builds something that runs.

Layouts: [plan-template.md](plan-template.md). Read it before writing. Not for task-by-task steps: for one approved plan, use superpowers:writing-plans.

## Process

1. **Find the source:** the path the owner gave, else `requirements/decision.md`, else `decision*.md`. None or several: ask. None at all: offer the decision-record skill. Name any other design file in the folder that you did not use (for example an older plan) in the index. Only the owner can mark a file superseded.
2. **Check the target.** If `docs/plans/` has files, this is a refresh: edit in place; keep plan numbers, AC IDs, the owner's edits, ticked boxes and progress statuses (In progress, Done). A new plan takes a letter after the plan it follows (`17a`). Never rebuild or renumber without the owner's OK: the folder may not be in git. Follow Refreshing below.
3. **Read the source in full.** Keep its IDs and tags ([DECIDED], [PROPOSED], [OPEN], [NOT SPECIFIED], [CONFLICT]). No tags: a stated choice is [DECIDED], a listed open point is [OPEN]; say so in the index. No IDs: use § numbers.
4. **Draft `00-index.md`.** If the owner is in the conversation, show the plan table and wait. If you are a subagent, or were told not to ask, go on.
5. **Write each plan**, self-check, fix, and reply.

## Refreshing

The Coverage table in `00-index.md` is the change detector. Compare the source's current items against it, then:

| Finding | Do |
|---|---|
| New source item | Place it in the plan it belongs to. If none fits, add a lettered plan (`17a`). Add a Coverage row. |
| Item changed | Update the plan in place: scope, decisions used, criteria. Keep every AC ID. |
| Ticked criterion whose source line changed | Leave the owner's tick. Add "Source changed: re-check" after it. |
| Item gone from the source | Keep the plan text and its AC IDs. Mark its Coverage row "removed from source" and tell the owner. Never delete. |
| Open question now answered in the source | Drop it from the plan's open questions, update the Status, keep the Q ID in "Decisions used". |

Update the index's source line and "Built on" date.

## Slicing rules

| Rule | What it means |
|---|---|
| Main flow by architecture | One plan per diagram part on the main user's path, named after it. Each comes after the parts whose output it reads, whatever the diagram's order. Setup (repo, CI, deploy) goes in the first. Each has a criterion on its own interface: endpoint, script, test search. No diagram: take the parts from the source's component or data-flow section; if it has neither, ask the owner (a subagent derives them from the data flow, tags them [ADDED] and lists them in "Gaps found"). Main user = the user whose path the source calls primary; if it names several with no priority, ask, or take the one with the most requirements and say so in "Why this order". |
| UI foundation | If there is a UI (a CLI counts): the shared UI stack, app shells and the first screen the main flow needs. Features add their screens to it. |
| Main flow complete | The last main-flow plan adds the source's limits, errors and edge cases for the main path. |
| One feature per plan | Afterwards someone can do or see something new, in a demo. It cuts through every layer it needs. No feature plan per layer ("database", "API"), and no plan for hardening, tuning or launch. |
| Dependencies | A plan depends only on lower numbers. Ties: the source's own phases. |
| Signals: where they go | Default: last, each covering the main flow plus every feature plan's Signals line. The source decides first. If it puts a signals deliverable in an earlier phase or exit criterion (for example "eval suites and baselines in phase 1"), or a choice depends on one (for example "pick the model by running the phase-1 eval"), place that plan where the source puts it, or just before the first plan that needs it, so dependencies still point to lower numbers. A plan placed early covers only the plans before it; later feature plans list their own Signals work under "What we build". State every placement and its cost in "Why this order". If the source is silent on Observability or Monitoring, still write them: [NOT SPECIFIED] content, gaps as open questions. Write Evaluation only when the product produces output someone must judge (model answers, rankings, generated text). If it does not and the source is silent, list Evaluation under "Not planned", with that as its trigger. |
| NFRs | A limit or target becomes a criterion of the plan it constrains. System-wide pre-launch checks (security review, load test) go in the release checklist. |
| Design-only vs deferred | Design-only items go in the "Design only" table. Deferred items go in "Not planned", with their trigger. |
| Each item lands once | Each source item lands in one plan, the release checklist, "Design only" or "Not planned". The coverage table proves it. An item that spans two plans gets one row per part, each naming its part (for example "Nightly check: job" in 18 and "Nightly check: alert" in 19). |

| Signals plan | Answers | Owns |
|---|---|---|
| Observability | What happened in this one request or job, and why? | Logs with a correlation ID, traces, PII removed from logs, model and prompt versions |
| Evaluation | Is the output good? Did a change make it worse? | Test sets, offline suites, AI judge, CI gate, model choice, checks on real samples, feedback turned into test cases |
| Monitoring | Is the live system healthy? Who is told when it is not? | Metrics, dashboards, alerts with thresholds, health checks, runbooks |

## Acceptance criteria

3-8 per plan. Over 8: split along a demoable boundary (something new someone can do or see), never by layer; on a refresh the new half takes a letter. Under 3: if it is only part of a feature, merge it into that feature's plan. A Signals plan on a silent source may have fewer: its open questions carry the rest.

    - [ ] **AC-NN.k** Given <state>, when <actor or event>, then <observable result>.
      - Check: <test, suite, query or script; anything else ends with "(manual)"> · Source: <ID or §> [TAG]

- **Numbers come only from the source.** No target given: the criterion is "measured and recorded as a baseline", linked to the open question that sets the target.
- **Derived** (no source line states it): Source "derived from <§>", tagged [ADDED].
- **Manual checks:** end the Check with "(manual)" and say what it needs (a real account, a person, a deployed host) and what to look at. Use it only where no script could run the check.
- The first plan where the whole journey works has an end-to-end criterion on the deployed system.
- A failure path the source defines (an error, a limit, a service that is down) gets a criterion.
- Acceptance criteria the source already lists are reused: keep the wording, number them AC-NN.k like the rest, and cite the source's own ID in Source.

**Status:** every [OPEN] or [CONFLICT] item a plan uses goes in its open questions, with the source's default. "Blocked by Q#" only when the source gives no default, or says the question blocks the build (for example P0). Otherwise "Ready". Assumptions a plan relies on go in its "Decisions used".

**Our own IDs:** a point the source does not state, or a conflict we find between two sections of the source, gets the ID Q-NS-n. Number them once, in the index under "Gaps found", and reuse the number in every plan that uses it. Tag a conflict [CONFLICT] and a missing point [NOT SPECIFIED]. Each carries a default.

**Progress:** the builder sets a plan's Status to In progress when it starts, and to Done when every criterion is ticked (Done (manual pending) when only manual ones remain). Keep these on a refresh.

## Self-check

- Coverage table: nothing missing, nothing twice.
- Each Signals plan sits where the source's phases, exit criteria and defaults put it; "Why this order" says where and what it costs.
- Every "Not planned" row has a trigger from the source, or "None given" with a line in "Gaps found".
- Search every number in the plans against the source; fix or remove the ones not found.
- Every criterion has Check and Source. Every feature plan has three Signals lines.
- Plain English, as in the source: short sentences, active voice, its glossary terms.

## Common mistakes

| Mistake | Fix |
|---|---|
| Feature plans per layer; plans for hardening or launch | Vertical feature slices; launch checks in the release checklist |
| An invented threshold in a criterion | A baseline plus an open question, or [ADDED] in "Gaps found" |
| "Later" items silently dropped | "Not planned", with their trigger |
| Overwriting or renumbering existing plans | Edit in place; a new plan takes a letter |
| All three Signals plans last although the source's phase 1 includes them | Place them as the source does; state the cost in "Why this order" |
| An invented trigger for a "Not planned" item | "None given", plus a line in "Gaps found" |

## Final reply

The folder path, and created or refreshed. The plan table: number, name, group, outcome, depends on, status. Criteria per plan, and how many are derived. Gaps found, and the questions that block a plan. On a refresh: what was added, changed and removed.
