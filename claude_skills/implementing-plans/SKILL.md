---
name: implementing-plans
description: Use when the prompt names a plan from docs/plans/ to build, or gives a spec or small change with acceptance criteria, and it must become working, tested code
---

# Implementing a Plan

## Overview

Build the one plan the prompt names, on a new branch made from an up-to-date `main`. The plan says what to build; the existing code says how. A plan is done when every acceptance criterion's Check has run and passed.

**Core rule: build only the plan the prompt names, on its own branch, in the style of the code already there. "Passes" means you ran the Check and read the output.**

Plans come from splitting-decisions-into-plans; implementation-planner sets their order. For test-first and verification detail, use superpowers:test-driven-development and superpowers:verification-before-completion. When the build is finished, implementation-validator checks it.

**Script path:** `<skill-dir>` below is this skill's own folder, the "Base directory for this skill" Claude Code shows when the skill loads.

## Process

1. **Pull `main` and start a new branch.** This is always the first step.
   - The plan is the one the prompt names: a number such as `06`, a file name, or a path. No plan named and no change described: ask which plan, and wait. Never pick one yourself.
   - `git status --short` must be empty. If it is not, stop and ask the owner: those changes would follow you to the new branch. Not a git repo: stop and ask.
   - Update `main`: `git switch main`, then `git pull --ff-only`. If `main` is checked out in another worktree, run `git fetch origin main` instead and branch from `origin/main`. No remote: use local `main` and say so in the report. A pull that fails: stop and report it. If the repo's main branch has another name (`master`), use that.
   - Create the branch: `git switch -c plan/NN-<name>` (add `origin/main` when you fetched instead of pulling). `<name>` comes from the plan's file name, for example `plan/06-cart`. If the branch exists, stop and ask: it may hold earlier work.
   - Note the commit you started from (`git rev-parse --short HEAD`). Every later step happens on this branch.
2. **Check the plan can start.** Read its row in `docs/plans/00-index.md` and its header. Stop and tell the owner which plan or question blocks it when:
   - its Status is "Blocked by Q#";
   - a plan in its Depends on is not Done or Done (manual pending);
   - `docs/plans/implementation-plan.md` exists and its "Dependency findings" name a plan this one needs that is not done;
   - its criteria rely on what a pending manual check of an earlier plan proves (a real account, a real deployment).

   When you stop here, switch back to `main` and delete the empty branch with `git branch -d`. You read Status; you never write it.
3. **Read.** The whole plan: Scope (In and Out), Decisions used, Open questions, criteria. For each open question, use the default the plan assumes and note it for the report. Read the source § the plan cites if something is unclear. Then read the code: layout, conventions, and how tests, lint and type checks run (package scripts, Makefile, CI config, README). Run them once before changing anything to see the baseline. Failures that exist already are not yours: list them in the report. An empty repo, or no tooling yet: the first plan creates it from the source's stack. Build that first, skip the baseline, and run the commands from then on.
4. **Fit the structure.** Follow the architecture the code or the source already has. Add the smallest structure the criteria need: no layer, interface or pattern a criterion does not ask for. One idea from DDD and hexagonal design is worth keeping: business rules live in plain code that tests can run without the database, network or model; the code that talks to those sits at the edge. Use DDD or ports-and-adapters names only where the project already does.
5. **Build in slices, one criterion at a time.**
   - Write the criterion's Check first (the test, query or script it names) and watch it fail.
   - Write the least code that makes it pass. Then tidy.
   - Make each slice a change you can describe in one sentence and run.
   - A "(manual)" Check: do it if you can (it may need a real account or a person). Note what you saw, or exactly what the owner must run, and leave the box for the owner.
   - Build Signals work (observability, evaluation, monitoring) only when it is under "What we build". A feature plan's Signals section is input for the Signals plans, not work for this plan.
6. **Run the safety net after every change.** The Check you are working on, then lint and the type check on the files you touched. Run the full suite whenever you change shared code, and at step 8. Fix every failure or warning you caused. Do not fix old ones.
7. **Checkpoint.** If the owner is in the conversation, stop and show the change and the Check output before: a decision the plan does not make, work outside the plan's In scope, a new dependency, a schema or public-interface change. Also stop at the end of the plan. If you are a subagent, or were told not to ask, do not stop: take the smallest option and list it under "Decisions outside the plan" in the report.
8. **Close the plan.** Run every Check in the plan, then the full suite, lint and type check. Tick each box whose Check passed; leave every other tick as you found it. Do not write Status, in the plan header or in `00-index.md`: the report says which Status the owner should set. Build the Files changed table (see Report). Do not commit or push unless the owner asks; the work stays on the branch.

## Stop and ask

Stop, say why, and wait (a subagent reports it and ends) when:

- The prompt names no plan and describes no change.
- The working tree is not clean, the pull fails, or the branch name is taken.
- The plan is Blocked by Q#, or a plan it depends on is not done.
- A criterion cannot be met as written: it contradicts the source or another criterion, or its Check cannot run here.
- A failure you did not cause blocks you.
- The plan looks wrong or out of date. Do not edit plan files except to tick boxes. The owner updates the source first; then the plans are refreshed with splitting-decisions-into-plans.

## Release checklist

When the owner says every plan is Done, work through the Release checklist in `00-index.md`, one item at a time, on a branch made as in step 1 and named `release/checklist`. Run what can be run (use security-review for a security review; write a script for a load test). Report the items only a person can do, such as a signed agreement or going live. Tick nothing you did not see pass.

## No plan

Small change: use the request as the spec. Do step 1 with a branch named `change/<short-name>`, state the check that proves the change, then do steps 3-6 and 8. Larger work: suggest splitting-decisions-into-plans first.

## Common mistakes

| Mistake | Fix |
|---|---|
| Building on whatever branch was checked out | Step 1 first: pull `main`, then a new branch |
| Picking the next plan yourself | Build only the plan the prompt names; ask if it names none |
| Setting a plan's Status | Say in the report which Status to set; the owner sets it |
| "Tests pass" without a run | Run them and read the output |
| Tests written after the code | Check first, watch it fail, then code |
| Building it another way because the plan looks wrong | Stop and report; never deviate silently |
| An abstraction "for later" | Build what the criteria need |
| Fixing unrelated warnings on the way | List them in the report |
| Ticking a (manual) criterion | Leave it for the owner |
| A files-changed list written from memory | Run `files_changed.py` (below), in every repo you touched |

## Report

The report goes in the chat. In this order:

1. Plan number and name.
2. A table of criteria: ID, Check, result (pass, fail, manual).
3. Pending manual checks, each with what the owner must run.
4. **Status to set:** Done, or Done (manual pending) and which boxes are open. The owner sets it.
5. Defaults used for open questions. Decisions outside the plan. Failures seen that were already there.
6. **Files changed:** every file you changed, so the owner can review each one by hand.
7. **Last line:** `Branch: plan/NN-<name>` (from `main` at `<start commit>`), and "nothing committed" unless the owner asked you to commit.

Build the Files changed table with the script, never from memory. Run it from the repo root, with the commit you started from:

    python <skill-dir>/scripts/files_changed.py --base <start commit>

It lists every changed, new, deleted and renamed file, untracked files included, with the line ranges from `git diff -U0`. Fill in the What column. For another repo you touched (for example the shared `infra` repo), pass it as `<path>=<its start commit>`; the script names the repo above its rows. Plan files count: list the lines where you ticked a box. Nothing changed: "No files changed."

| File | Status | Lines changed | What |
|---|---|---|---|
| `backend/app/api/v1/auth.py` | modified | 12-18, 40, 55-61 | callback refuses a wrong `state` |
| `backend/tests/test_auth.py` | new | all (84 lines) | tests for AC-01.4 |
| `docs/plans/01-edge-and-ingress.md` | modified | 57 | AC-01.2 ticked |

No Python: build it by hand from `git status --short` and `git diff -U0 <start commit>`. Each `@@ -a,b +c,d @@` header gives new lines c to c+d-1 (a missing `,d` means 1); `d` of 0 is a pure deletion: `removed (old lines a-a+b-1)`.
