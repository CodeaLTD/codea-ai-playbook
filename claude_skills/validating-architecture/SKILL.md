---
name: validating-architecture
description: Use when auditing a finished architecture, design doc, or technical plan for soundness and size; when asked whether a design is over-engineered, too complex, or bigger than its scale, team, or deadline need, or what it is missing or contradicts; or when looking for ways to simplify it, cut components, defer scope, or reduce moving parts without losing required capabilities. Not for designing options with the user (brainstorming-architecture) or checking a plan's facts against code (verifying-plans)
---

# Validating Architecture

## Overview

A validation answers two questions against one yardstick: **is anything wrong or missing**, and **is anything bigger than it needs to be**. The yardstick is the design's own capabilities and drivers (load, team, deadline, compliance, existing stack). Every finding and every cut cites it.

The two questions pull in opposite directions. Fixing gaps adds parts, and "simpler, nothing lost" is easy to claim without showing it. So in this report, each cut traces the capabilities it touches, and a before/after count shows whether the design got smaller or bigger.

For interactive redesign or choosing between options, use brainstorming-architecture instead. When the doc makes claims about existing code, check them the way verifying-plans describes.

## Process

1. **Read every source in full**: the doc, the code or sibling repos it says it reuses, and the infra docs it depends on. Open the code behind each "reuse X" claim. Overstated reuse hides work and makes the estimates too low.
2. **Build the yardstick** before judging anything:
   - **Capabilities** C1…Cn: what the system must do, taken from the doc. These are what "without losing anything" protects.
   - **Drivers** D1…Dn: load and data volume, team size, deadline, compliance, existing stack, budget. Mark each Known (with its source) or Assumed. When a driver is missing, assume the value the evidence points to, and say which verdicts flip if it is wrong. A decision record's tags map like this: [DECIDED] = Known; [PROPOSED], or [OPEN] with a default = Assumed; [OPEN] with no default, [NOT SPECIFIED] and [CONFLICT] = not known yet, so ask or assume.
3. **Inventory every component**: deployables, data stores, external services, queues, background jobs, model-visible tools, endpoint groups, shared packages, generated artifacts, and LLM calls on the request path. For each, name the capability it serves and the driver that justifies its size. A component that serves no capability, or exists only because another component does, is a cut candidate.
4. **Check each component** against the smells and the non-negotiables below.
5. **Validate**: contradictions between sections, correctness bugs (races, missing idempotency), failure modes, and security and compliance gaps. For each, give the smallest fix that closes it. Prefer a fix that removes a part over one that adds a part.
6. **Count** before and after, including the parts your fixes add.
7. **Write the report** in the order below.

## Over-engineering smells

| Smell | Ask | Usual simplification |
|---|---|---|
| Built for a driver that isn't here yet (more tenants, 100× load, many vendors) | Which driver justifies it today? | Keep the cheap seam (a column, an interface); defer the machinery and name what brings it back |
| Two mechanisms for one job (state in two stores, two templates, two transports) | Which one is the source of truth? | Keep one |
| A part that exists only to support another part | Which root decision forces it? | Change that decision; the support part disappears |
| An LLM call that code or the next LLM call could do | What does it decide that nothing else can? | Fold it into the next call, or make it a rule |
| A commodity built in-house (scheduling, auth, email, analytics) | Does building it set the product apart? | Buy or embed it until it does |
| Generality no one configures (rule engines, plugin registries, override layers) | Who sets this, and how often? | Hard-code the one case until a second appears |
| Near-duplicate tools, endpoints or reports | Do they differ by one parameter? | Merge them |
| A dedicated store or broker for small data | What are the real volumes? | Use the database already running |
| Several output formats where one would do | Who asked for each? | One format; add others on request |
| Phases that build late features before the core is proven | What does each phase prove? | Reorder by value and by riskiest assumption |

## Non-negotiables

A simplification never removes any of these. A cut that would is a gap, not a simplification:

- identity and authorization checks
- idempotent side effects, and no check-then-act races
- human confirmation before irreversible actions
- one source of truth for each piece of state
- failures someone will see
- backups of anything that can't be rebuilt
- legal duties that apply (privacy, consent, AI disclosure)

"Right-sized" is a valid verdict. A design built on the existing stack with no speculative parts gets **Keep**, plus its real gaps.

## Report

The reply has these parts, in this order:

1. **Verdict**, 2–4 sentences: right-sized, over-engineered in <areas>, and/or under-engineered in <areas>, with the headline counts (for example "7 → 4 containers, 16 → 7 model tools").
2. **Yardstick**: one line per capability and driver, with Known/Assumed and the source.
3. **Keep**: one line per area (for example backend, protocol, knowledge, business flows), naming its right-sized parts and the reason.
4. **Must fix**: one item per contradiction, bug or gap, with a § reference, why it fails, the smallest fix, and what that fix adds.
5. **Simplify**: one table row per cut.

   | # | Today (§) | Simpler | Removes | Capabilities kept: ID → how | Lost or traded | Easy to add back? |
   |---|---|---|---|---|---|---|

   Fill the capabilities column for every row. "Nothing" in the Lost column requires every capability the removed part served to be listed with how it is still met.
6. **Defer**: parts built for a driver that isn't here yet, each with the trigger that brings it back.
7. **Net complexity**: a before/after table counting deployables, data stores, external services, LLM calls per request, model-visible tools, public endpoints, background jobs, and build effort. Leave out any row that is zero both before and after. Include what the must-fix items add. If a total goes up, say why it is worth it. When components were removed, draw the resulting shape in the format from [diagram-format.md](../brainstorming-architecture/diagram-format.md).
8. **Decisions for the user**: cuts that trade a capability, contradict a stated principle, or depend on an Assumed driver. Give your recommendation for each.

Every inventoried component lands in exactly one of Keep, Must fix, Simplify or Defer.

Save the report to `docs/reviews/<date>-validating-architecture-<doc>.md` unless the owner names another place, and give the path in your reply. When the owner decides the items under Decisions for the user, offer to record each outcome in the decision record, so later work reads it.

## Self-check before sending

| Check | Fix |
|---|---|
| A Simplify row has no capability IDs | Trace them, or move the row to Decisions |
| A cut touches a non-negotiable | Drop it, or report it as a gap |
| A component from the doc appears in no section | Place it in Keep, Must fix, Simplify or Defer |
| Must-fix additions outnumber cuts and Net complexity doesn't explain it | Find smaller fixes, or explain the increase |
| A recommendation rests on a fact from memory (vendor limit, regulation, price, date) | Verify it, or mark it unverified and move it to Decisions |
| The verdict is not first, or has no counts | Rewrite it with the numbers |
