---
name: implementation-agent
description: Use when implementing a plan file from docs/plans/ or any spec with acceptance criteria, building the next plan in order, or turning a plan's acceptance criteria into working, tested code
---

# Implementing a Plan

## Overview

Build one plan at a time, in number order. The plan says what to build; the existing code says how. A plan is done when every acceptance criterion's Check has run and passed.

**Core rule: build what the plan says, in the style of the code already there. "Passes" means you ran the Check and read the output.**

Plans come from splitting-decisions-into-plans. For test-first and verification detail, use superpowers:test-driven-development and superpowers:verification-before-completion.

## Process

0. **Branch first.** Before any change, including the Status edit in step 1: check out `main`, pull it (`git pull`), then create and switch to a new branch from it (`git checkout -b <name>`). Name it after the work, for example `plan-03-auth-flow` or `fix-short-description`. Never work on `main` or on an old branch. If the pull fails or the working tree has uncommitted changes that block the checkout, stop and tell the owner. In a multi-repo job, do this in every repo you will change. If you do not yet know the plan name, do the pick (read-only) first, then branch before editing anything.
1. **Pick the plan.** The one the owner names, else the lowest-numbered plan in `docs/plans/00-index.md` with Status Ready whose "Depends on" plans are all Done or Done (manual pending). Set its Status to In progress. Not ready, or "Blocked by Q#": stop and tell the owner which plan or which question. Do not guess. A pending manual check does not stop a dependent plan, unless the dependent's criteria rely on what that check proves (a real account, a real deployment): then stop and ask.
2. **Read.** The whole plan: Scope (In and Out), Decisions used, Open questions, criteria. For each open question, use the default the plan assumes and note it for the report. Read the source § the plan cites if something is unclear. Then read the code: layout, conventions, and how tests, lint and type checks run (package scripts, Makefile, CI config, README). Run them once before changing anything to see the baseline. Failures that exist already are not yours: list them in the report. An empty repo, or no tooling yet: the first plan creates it from the source's stack. Build that first, skip the baseline, and run the commands from then on.
3. **Fit the structure.** Follow the architecture the code or the source already has. Add the smallest structure the criteria need: no layer, interface or pattern a criterion does not ask for. One idea from DDD and hexagonal design is worth keeping: business rules live in plain code that tests can run without the database, network or model; the code that talks to those sits at the edge. Use DDD or ports-and-adapters names only where the project already does.
4. **Build in slices, one criterion at a time.**
   - Write the criterion's Check first (the test, query or script it names) and watch it fail.
   - Write the least code that makes it pass. Then tidy.
   - Make each slice a change you can describe in one sentence and run.
   - A "(manual)" Check: do it if you can (it may need a real account or a person). Note what you saw, or exactly what the owner must run, and leave the box for the owner.
   - Build Signals work (observability, evaluation, monitoring) only when it is under "What we build". A feature plan's Signals section is input for the Signals plans, not work for this plan.
5. **Run the safety net after every change.** The Check you are working on, then lint and the type check on the files you touched. Run the full suite whenever you change shared code, and at step 7. Fix every failure or warning you caused. Do not fix old ones.
6. **Checkpoint.** If the owner is in the conversation, stop and show the change and the Check output before: a decision the plan does not make, work outside the plan's In scope, a new dependency, a schema or public-interface change. Also stop at the end of the plan. If you are a subagent, or were told not to ask, do not stop: take the smallest option and list it under "Decisions outside the plan" in the report.
7. **Close the plan.** Run every Check in the plan, then the full suite, lint and type check. Tick each box whose Check passed; leave every other tick as you found it. Set the plan's Status, in `00-index.md` and in the plan header, to Done, or to Done (manual pending) if any manual box is open. Write the report. Do not commit unless the owner asks.

## Stop and ask

Stop, say why, and wait (a subagent reports it and ends) when:

- The plan is Blocked by Q#, or a plan it depends on is not done.
- A criterion cannot be met as written: it contradicts the source or another criterion, or its Check cannot run here.
- A failure you did not cause blocks you.
- The plan looks wrong or out of date. Do not edit plan files except to tick boxes and set the Status. The owner updates the source first; then the plans are refreshed with splitting-decisions-into-plans.

## Release checklist

When every plan is Done, work through the Release checklist in `00-index.md`, one item at a time. Run what can be run (use security-review for a security review; write a script for a load test). Report the items only a person can do, such as a signed agreement or going live. Tick nothing you did not see pass.

## No plan

Small change: use the request as the spec. Do step 0 (new branch from a freshly pulled `main`), state the check that proves it first, then do steps 2-5 and 7. Larger work: suggest splitting-decisions-into-plans first.

## Common mistakes

| Mistake | Fix |
|---|---|
| "Tests pass" without a run | Run them and read the output |
| Tests written after the code | Check first, watch it fail, then code |
| Building it another way because the plan looks wrong | Stop and report; never deviate silently |
| An abstraction "for later" | Build what the criteria need |
| Fixing unrelated warnings on the way | List them in the report |
| Ticking a (manual) criterion | Leave it for the owner |
| Editing on `main` or a stale branch | Checkout `main`, pull, branch, then change anything |
| Branch name missing from the report | Put it at the top of the report |
| A files-changed list written from memory, or without line numbers | Build it from `git status` and `git diff -U0`, in every repo you touched |

## Report

Plan number and name. **Branch name** (and the repo, if more than one), created from an up-to-date `main`. A table of criteria: ID, Check, result (pass, fail, manual). Pending manual checks, each with what the owner must run. Defaults used for open questions. Decisions outside the plan. Failures seen that were already there. Last, **Files changed**: every file you changed, so the owner can review each one by hand. One row per file, grouped by area, in this form:

| File | Status | Lines changed | What |
|---|---|---|---|
| `backend/app/api/v1/auth.py` | modified | 12-18, 40, 55-61 | callback refuses a wrong `state` |
| `backend/tests/test_auth.py` | new | all (84 lines) | tests for AC-01.4 |
| `docs/plans/01-edge-and-ingress.md` | modified | 7, 57 | Status set, AC-01.2 ticked |

Build the table from git, not from memory:
- **Files:** `git status --short`. Run it in every repo you touched and name the repo above its rows (for example the shared `infra` repo). Plan and index files count: list the lines where you ticked a box or set the Status.
- **Lines:** `git diff -U0`. Each `@@ -a,b +c,d @@` header gives the new-file lines c to c+d-1 (a missing `,d` means 1); a header with `d` of 0 is a pure deletion, so write `removed (old lines a-a+b-1)`. A new (untracked) file is `all (N lines)`; a deleted file is `all removed`. If you committed at the owner's request, diff against the commit you started from.
- Nothing changed: write "No files changed."
