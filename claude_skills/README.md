# Codea Claude skills

Skills that take a project from the client's requirements to validated code. Each skill does one step and hands a file, or a branch, to the next. Every skill folder holds a `SKILL.md`; some also hold reference pages and a `scripts/` folder.

## Pipeline

```text
[ requirements/ ] ── decision-record ──► [ requirements/decision.md ]
                                                        │
          ┌─────────────────────────────────────────────┤
          ▼                                             ▼
[ brainstorming-architecture ]              [ validating-architecture ]
  design options with the user                audit a finished design ──► [ docs/reviews/ ]
          │ DECIDED / OPEN lines go back into decision.md
          ▼
[ splitting-decisions-into-plans ] ──► [ docs/plans/00-index.md · NN-<name>.md ]
                                                        │
          ┌─────────────────────────────────────────────┤
          ▼                                             ▼
[ verifying-plans ]                         [ implementation-planner ]
  fact-check the plans ──► [ docs/reviews/ ]  ──► [ docs/plans/implementation-plan.md ]
                                                        │
                                                        ▼  the prompt names one plan
                                            [ implementing-plans ]
                                              pulls main ──► [ branch plan/NN-<name> ]
                                                        │
                                                        ▼  the owner gives branch + plan
                                            [ implementation-validator ] ──► verdict in chat

[ skill-evaluator ]  grades any skill's finished run · read-only · report in chat
```

| Skill | Use it to | Reads | Writes |
|---|---|---|---|
| decision-record | Turn everything in `requirements/` into one plain-English decision record | `requirements/`, `.claude/decision-record-profile.md` | `requirements/decision.md` |
| brainstorming-architecture | Design or evolve an architecture with the user: options, trade-offs, diagrams | requirements, blueprints, the decision record | The design, if the owner asks |
| validating-architecture | Audit a finished design for gaps and over-engineering | The design doc and the code it claims to reuse | `docs/reviews/` |
| splitting-decisions-into-plans | Split the decision record into numbered build plans with acceptance criteria | `requirements/decision.md` | `docs/plans/` |
| verifying-plans | Check every factual claim in a plan against the code or the source | Plans, code, source | `docs/reviews/` |
| implementation-planner | Compute build waves, the critical path and what collides in parallel work | `docs/plans/` | `docs/plans/implementation-plan.md` |
| implementing-plans | Build the one plan the prompt names, test-first, on a new branch from `main` | One plan, the code | Code on `plan/NN-<name>`; the report in chat |
| implementation-validator | Check a branch against its plan: task fit, over-engineering, security, licences, docs | The branch and plan the owner names | Nothing; the report in chat |
| skill-evaluator | Grade how well a finished skill run followed its skill | The run's record, the skill | Nothing; the report in chat |

## Rules that span skills

- **Status in `docs/plans/` is the owner's.** splitting-decisions-into-plans writes the first Status. After that only the owner changes it. Builders tick acceptance-criteria boxes, never Status.
- **One plan, one branch.** implementing-plans always pulls `main` first and builds on `plan/NN-<name>`. The last line of its reply names the branch.
- **Reports:** validating-architecture and verifying-plans save to `docs/reviews/`. implementation-validator and skill-evaluator reply in the chat only.
- **Project details stay in the project.** decision-record reads client-specific rules from `.claude/decision-record-profile.md` in the client's repo (layout: [decision-record/profile-template.md](decision-record/profile-template.md)). This playbook is public: never put client names, files or data in it.

## Install

Claude Code loads skills from `~/.claude/skills/` (all your projects) or `<project>/.claude/skills/` (one project). See [Using the skills in another project](../README.md#using-the-skills-in-another-project) for the install scripts (global link, per-project link, or a committed copy), how to run a skill, and the folders a project needs.

## Prerequisites

| Needed | Used by |
|---|---|
| Claude Code | All skills |
| git | implementing-plans (branches, Files changed table), implementation-validator |
| Python 3.8 or later, standard library only | The scripts below |
| The **superpowers** plugin (install it through `/plugin` in Claude Code) | superpowers:writing-plans (splitting-decisions-into-plans), superpowers:test-driven-development and superpowers:verification-before-completion (implementing-plans), superpowers:using-git-worktrees (the wave steps in `implementation-plan.md`) |
| Claude Code's built-in **security-review** and **code-review** | implementing-plans' release checklist; verifying-plans and implementation-validator hand bug hunting and deep security scans to them |
| The AskUserQuestion tool (optional) | brainstorming-architecture and implementation-validator ask through it when it is there, and in the chat otherwise |

## Scripts

Each skill runs its scripts from its own folder, the "Base directory for this skill" Claude Code shows when the skill loads. Every script reads only and writes nothing, except `build_order.py --out`.

| Script | What it does |
|---|---|
| `decision-record/scripts/check_decision.py` | Checks a `decision.md` against the layout and language rules |
| `splitting-decisions-into-plans/scripts/check_plans.py` | Checks `docs/plans/`: criteria, Coverage, Depends on, and every number against the source |
| `implementation-planner/scripts/build_order.py` | Computes waves, slack, the critical path and builder lanes; draws both diagrams |
| `implementing-plans/scripts/files_changed.py` | Builds the Files changed table from git, untracked files included |

Run the tests from the repo root:

```bash
python -B -m unittest discover -s tests
```
