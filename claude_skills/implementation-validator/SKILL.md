---
name: implementation-validator
description: Use when a finished implementation on a branch needs checking against its plan for over-engineering, security gaps, license problems, thin documentation, or tests that do not prove the task. Not for bug hunting (code-review) or design docs (validating-architecture)
---

# Implementation Validator

## Overview

Check the work on one branch against the plan it was meant to build, then report findings and a verdict in the chat. Read-only: change nothing and write no files.

**Core rule: every finding cites `file:line` and says why it matters. Every "passes" was run, or is reported as "not run".**

Covers five checks (below). Does not cover: bug hunting (use code-review), a deep vulnerability scan (use security-review), architecture or design docs (use validating-architecture), plans and specs (use verifying-plans).

## Process

1. **Ask for the branch and the plan.** Know both before anything else: the branch that holds the work, and the plan it builds (a file in `docs/plans/`). Use what the prompt names; ask for whatever it does not, and wait for the answer. Never guess, and never start validating before both are known.
   - If the AskUserQuestion tool is available, ask through it. Offer as answers the current branch and the `plan/*` branches (`git branch --list "plan/*"`), and the plan whose number matches the branch name (`plan/06-cart` → `docs/plans/06-cart.md`).
   - Otherwise, ask in the chat with the same likely answers.
   - No plan exists for the work: the owner may describe the task in words instead. Use that as the yardstick.
   - You are a subagent and either one is missing: report what is missing and end.
2. **Fix the target**: the branch's changes against `main` (or the repo's main branch if it has another name).
   - `git merge-base main <branch>` gives the base. `git diff --stat <base> <branch>` lists the committed changes.
   - Find where the branch is checked out: here (`git branch --show-current`), or in another worktree (`git worktree list`). Run every later command there. Also include the uncommitted and untracked files there: `git status --short` and `git diff <base>`. New files are part of the work even when nothing is committed.
   - Not checked out anywhere: ask the owner to check it out. Do not switch branches yourself: the working tree may hold other work.
   - The report says what you reviewed and what you did not.
3. **Find the yardstick.** The plan from step 1 first: its Scope, Decisions used and acceptance criteria. Then whatever else exists: the source's NFRs and security or data notes (`requirements/decision.md`); the project's own license and how it ships. For each item that does not exist, use a stated default and list it under "Assumed" in the report.
4. **Run the safety net.** Tests, lint and type check, using the commands the project already has (package scripts, Makefile, CI config). A failure is a finding. If a command cannot run, record "not run" and why. A repo with no tests or lint yet is "not run: no tooling": the verdict is Not verified, and a core requirement with no test is a High finding under task alignment.
5. **Run the five checks.**
6. **Re-check each finding** against the code. Drop any you cannot point to.
7. **Report** in the chat.

## The five checks

| Check | Look for | Measure against |
|---|---|---|
| Task alignment | Each requirement or criterion has a test that fails when the behaviour breaks. Proxy tests that only check internals (private methods, mocks of our own code). Failure paths and edge cases the task names with no test. | The plan's acceptance criteria, or the task the owner described |
| Over-engineering | Layers, abstractions, config or patterns with one user. Premature optimisation. Speculative generality. Anything the plan or source decided, or an NFR requires, is not over-engineering. | The plan's scope, scale and NFRs |
| Security, both ways | **Missing:** secrets in code or logs, injection, no input validation or access check at a boundary, PII in logs, unsafe deserialisation, a dependency with a known CVE. **Excess:** controls with no threat in the model, or friction that buys nothing. | The threat model: the source's security notes, else assumed from the data's sensitivity and exposure |
| Licences | Every direct and transitive dependency in the lockfile, and its licence. Flag: unknown or missing licence; copyleft that bites on how the project ships (AGPL and SSPL for network services, GPL for distributed code); a clash with the project's own licence; missing attribution. | The project's licence policy, else assumed: MIT, BSD, Apache-2.0 and ISC pass; anything else is flagged |
| Documentation | What a new reader needs for this change: the public interface, setup and run steps, config and env vars, decisions the code cannot show. Also flag docs the code contradicts, and docs far larger than the change. | The size of the change and who reads it |

Scan licences with a tool if one is installed (license-checker, pip-licenses, cargo-deny, go-licenses). Otherwise read the lockfile and package metadata. Say which you used.

## Severity and verdict

| Severity | Meaning |
|---|---|
| Blocker | The task is not met, a secret or personal data is exposed, or a dependency cannot be shipped under the project's licence |
| High | A missing control, a missing test for a core requirement, or a failing check |
| Medium | Over-engineering, a thin test, a documentation gap that slows a new reader |
| Low | Small and cosmetic |

- **Fail:** any Blocker or High.
- **Not verified:** the safety net could not run. Never report Pass in this case.
- **Pass:** everything else. List the Medium and Low findings.

## Report

The report goes in the chat only. Never write it to a file. In this order:

1. Verdict line.
2. Branch and plan reviewed; what was reviewed and what was not.
3. Safety net: each command and its result, or "not run" and why.
4. Findings, most severe first: `#`, severity, check, `file:line`, finding, fix. No findings: "No findings".
5. Assumed: every default from step 3.

A commit message only if the verdict is Pass: write it from the change in the style of the project's recent commits, mention no pull request, and do not commit.

## Common mistakes

| Mistake | Fix |
|---|---|
| Starting before the branch and plan are known | Ask for them first, and wait |
| Reviewing whatever branch is checked out | Check that it is the branch named in step 1 |
| Reviewing only `git diff`, so new untracked files are missed | Add `git status --short`; new files are part of the work |
| Switching branches to reach the work | Use its worktree, or ask the owner to check it out |
| Pass without running the checks | Report "Not verified" |
| A finding with no `file:line` | Find the line or drop it |
| Calling a planned or decided abstraction over-engineering | Read the plan and source first |
| Cutting security because "it is only a prototype" | Tie it to the stated threat model |
| Reporting bugs or style outside the five checks | Out of scope: name code-review in the report |
| "Docs are adequate" because a README exists | Name the reader need that is met, or the one that is not |
| Saving the report to a file | The report goes in the chat only |
