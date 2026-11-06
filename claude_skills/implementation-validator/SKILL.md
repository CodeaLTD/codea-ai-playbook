---
name: implementation-validator
description: Use when a finished implementation needs checking for over-engineering, security gaps, license problems, thin documentation, or tests that do not prove the task
---

# Implementation Validator

## Overview

Check finished work against the task it was meant to do, then report findings and a verdict. Read-only: change nothing.

**Core rule: every finding cites `file:line` and says why it matters. Every "passes" was run, or is reported as "not run".**

Covers five checks (below). Does not cover: bug hunting (use code-review), a deep vulnerability scan (use security-review), architecture or design docs (use validating-architecture), plans and specs (use verifying-plans).

## Process

1. **Fix the target.** What the owner names, else the files changed for the task (the git diff if the folder is a git repo; if not, ask which files). Say in the report what you reviewed and what you did not.
2. **Find the yardstick.** Take it from whatever exists: the request or user story; a plan in `docs/plans/` (Scope, Decisions used, acceptance criteria); the source's NFRs and security or data notes (`requirements/decision.md`); the project's own license and how it ships. For each item that does not exist, use a stated default and list it under "Assumed" in the report.
3. **Run the safety net.** Tests, lint and type check, using the commands the project already has (package scripts, Makefile, CI config). A failure is a finding. If a command cannot run, record "not run" and why. A repo with no tests or lint yet is "not run: no tooling": the verdict is Not verified, and a core requirement with no test is a High finding under task alignment.
4. **Run the five checks.**
5. **Re-check each finding** against the code. Drop any you cannot point to.
6. **Report.**

## The five checks

| Check | Look for | Measure against |
|---|---|---|
| Task alignment | Each requirement or criterion has a test that fails when the behaviour breaks. Proxy tests that only check internals (private methods, mocks of our own code). Failure paths and edge cases the task names with no test. | The task's requirements or criteria |
| Over-engineering | Layers, abstractions, config or patterns with one user. Premature optimisation. Speculative generality. Anything the plan or source decided, or an NFR requires, is not over-engineering. | The task's scope, scale and NFRs |
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

1. Verdict line.
2. Reviewed and not reviewed.
3. Safety net: each command and its result, or "not run" and why.
4. Findings, most severe first: `#`, severity, check, `file:line`, finding, fix.
5. Assumed: every default from step 2.
6. Reply in chat with the verdict line, then every finding from item 4 with the same `#`, severity, check, `file:line`, finding and fix as in the file. If there are no findings, the reply says "No findings".

A commit message only if the verdict is Pass: write it from the change in the style of the project's recent commits, mention no pull request, and do not commit.

## Common mistakes

| Mistake | Fix |
|---|---|
| Pass without running the checks | Report "Not verified" |
| A finding with no `file:line` | Find the line or drop it |
| Calling a planned or decided abstraction over-engineering | Read the plan and source first |
| Cutting security because "it is only a prototype" | Tie it to the stated threat model |
| Reporting bugs or style outside the five checks | Out of scope: name code-review in the report |
| "Docs are adequate" because a README exists | Name the reader need that is met, or the one that is not |
| Replying with only the report path | Put the verdict and every finding in the reply, then the path |
