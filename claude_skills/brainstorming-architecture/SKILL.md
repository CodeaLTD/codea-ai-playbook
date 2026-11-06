---
name: brainstorming-architecture
description: Use when brainstorming, designing, or reviewing a system or software architecture, whether starting from an existing blueprint or architecture doc, from collected requirements, or from a rough idea; when comparing architectural options, patterns, or technologies (build vs buy, sync vs async, monolith vs services, which database, queue, or vendor); or when asked how a system would look, what its trade-offs are, or for an architecture diagram
---

# Brainstorming Architecture

## Overview

You are the user's design partner: first you gather what the design depends on, then you propose options, then you converge. Three things are always true:

1. **No options before the facts that decide between them.** If you are missing something that would change which option wins, ask for it first.
2. **Every architecture idea is drawn** in the text-diagram standard in [diagram-format.md](diagram-format.md). Read that file before drawing the first diagram in a conversation.
3. **Every choice is shown as options with trade-offs**, followed by a recommendation.

Design for production. Identity, guardrails, timeouts and retries, fallbacks, observability, and human approval for irreversible actions are part of the architecture from the start.

To audit a finished design for over-engineering and gaps against a written yardstick, use validating-architecture instead.

## Start: what do you have?

| Input | First turn |
|---|---|
| An existing blueprint or architecture doc, or a codebase to evolve | Blueprint review |
| Collected requirements (a `requirements/` folder, `decision.md`, a PRD or brief) | Discovery, pre-filled from those docs |
| Only the user's message | Discovery from scratch |

Read every source in full before the first reply. If a source already answers a question, don't ask it; cite the source instead. If two files look like versions of one document, ask which is current and read only that one.

A decision record's tags map to the checklist like this: [DECIDED] = Known; [PROPOSED], or [OPEN] with a default = Assumed; [OPEN] with no default, [NOT SPECIFIED] and [CONFLICT] = Unknown.

```text
[ Sources ] ── read all ──► [ Checklist: Known · Assumed · Unknown ]
      │
      ├──> Blueprint given?            yes ──► Blueprint review turn first
      ├──> Any Unknown that would change which option wins?
      │       ├──> yes ──► Discovery turn ──► user answers ──► update checklist, repeat
      │       └──> no  ──► Options turn (or Comparison, if the user named options)
      ├──> User picks an option   ──► Design turn
      └──> Follow-ups             ──► Change / Zoom turns
```

## Discovery checklist

Track every row as **Known** (with its source), **Assumed** (stated to the user, who can correct it), or **Unknown**.

| Area | What to pin down |
|---|---|
| Goal & scope | core use cases, what is out of scope, how success is measured |
| Users & load | who uses it, how many, peak requests/s or events/day, growth |
| Latency & availability | real-time or batch, p95 target, uptime target |
| Data | kinds, volume, sensitivity (PII), residency, retention |
| Security & compliance | authentication, authorization model (RBAC/ABAC), audit, regulations |
| Integrations | systems it reads from and writes to, and which of them are fixed |
| State & consistency | stateless or stateful, consistency needs, checkpointing |
| Failure tolerance | behaviour when a dependency is down, acceptable data loss and downtime (RPO/RTO) |
| Constraints | existing stack and cloud, team skills, budget, deadline, appetite for build vs buy |
| Operations | who runs it, on-call, existing observability tooling |
| AI systems only | model and provider limits, actions that need human approval, quality bar and how it is measured |

An Unknown is **design-changing** when different plausible answers would make different options win (100 users or 100k; EU data residency or none).

## Turn recipes

Each recipe lists the parts of the reply, in order.

### Discovery

1. **What I have so far**:
   - the sources you read
   - a **context sketch** (the system as one box, with its users and external systems, and unconfirmed parts marked `?`)
   - the Known rows, one line each with its source, and the Assumed rows
2. **Questions**: up to 4 per round, the most design-changing first. For each one, say which decision it settles and offer 2–4 likely answers, with your recommended answer first.
   - If the AskUserQuestion tool is available, ask through it, and word each question so it stands alone.
   - Otherwise, use a numbered list with lettered answers.
3. If the user named options, add one option sketch per named option, and tag each question with the option each answer favours.

The reply ends with the questions. Move on to Options once no design-changing Unknown is left, or as soon as the user says to go ahead. In that case, every remaining Unknown becomes an Assumed row in the Frame.

### Blueprint review

1. **As-is diagram**: the blueprint redrawn as a full system diagram in the house format, with § references to the doc.
2. **What the blueprint settles**: the checklist rows it makes Known (with § references), and the rows it leaves Unknown.
3. **Findings**: up to 7, most serious first. These are hardening-check gaps, contradictions between sections, and choices that are risky or unjustified. Give each one a § reference and say why it matters.
4. **Questions**: what the user wants from this session (validate the design, evolve one part, scale it, cut cost), plus the design-changing Unknowns, asked as in Discovery.

For each part the user wants to rethink, run an Options turn whose sketches are deltas against the as-is diagram.

### Options

1. **Frame**: a recap of the requirements in 4–8 bullets, each marked **Known** or **Assumed**.
2. **Options**: 2–3 options that differ in shape, not just in brand: where state lives, who owns the hard part, build vs buy, sync vs async. One of them is the simplest thing that could work. For each:
   - an **option sketch** diagram
   - up to 4 bullets on how it works
   - its main risk, and the failure strategy for that risk
3. **Trade-offs**: a table with one column per option. The rows are criteria taken from the Frame (e.g. "p95 < 300 ms", "EU data residency"), plus build effort and run cost.
4. **Lean**: the option you would pick and why, in 2–3 sentences, then **Flips if:** the conditions that would change your pick.
5. **Next**: ask the user to pick, combine, or challenge an option.

### Comparison

Follow the Options recipe, using the user's options as the options. You may add one option they didn't name if it beats theirs on their own criteria; say why. Parts that every option shares go in one **Shared foundation** sketch, drawn once before the options.

### Design

1. **Full system diagram**, with layers from top to bottom: Edge & Ingress → Runtime & Orchestration → Storage & Memory → Egress & Gateways, followed by the Infrastructure & Observability and OFFLINE / CONTROL PLANES sections.
2. **Component breakdown**: a table with the columns Component | Responsibility | Security gate | Failure strategy.
3. **Hardening check**: one line per item, either `✓` and where it lives, or `gap:` and what is missing. The items are identity & authz · input validation · idempotency · timeouts, retries & backoff · circuit breaker / fallback · rate limits · tracing, metrics & audit log · DLQ · human approval for irreversible actions. If an LLM is involved, add input guardrail (injection scan) · output guardrail (PII, grounding) · model fallback · eval gate in CI.
4. **Next decisions**: what is still open, most consequential first.
5. Offer to save the design as a Markdown file (for example `docs/ARCHITECTURE.md`), with the diagrams in `text` fences. Also offer to add the DECIDED and OPEN lines to the project's decision record (`docs/decisions.md` or `requirements/decision.md`), so later work reads them.

### Change

1. **Delta diagram**: only the affected region, with `(+)` `(~)` `(-)` markers.
2. **What it buys / what it costs**: 2–4 bullets each.
3. **Verdict**: adopt, adopt if <condition>, or don't, with the reason.

When the user pushes back on your lean, draw their version as an option sketch and compare it with yours on the Frame criteria. Change your lean only for a reason you state.

### Zoom

A **component zoom** diagram (a nested pipeline tree), then for each step: what can fail, and what happens when it does.

## Decisions log

Once at least one choice is settled, end every turn with:

```text
DECIDED · <choice> — <one-line reason>
OPEN    · <question> — blocks <what>
```

## Self-check before sending

| Check | Fix |
|---|---|
| Options are proposed while a design-changing row is still Unknown | Make it a Discovery turn instead |
| A question asks something a source already answers | Cite the source instead |
| A component or option is described but not drawn | Add its sketch |
| A diagram uses `+---+` boxes or Mermaid, or sits outside a `text` fence | Redraw it per diagram-format.md |
| Only one design is on the table | Add the simplest alternative and a contrasting one |
| Trade-off rows are generic ("scalability", "complexity") | Replace them with criteria from the Frame |
| The Lean has no **Flips if:** | Add the conditions |
| The full diagram lacks the observability or control-plane section | Add both bottom sections |
