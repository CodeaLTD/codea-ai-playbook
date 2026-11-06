---
name: verifying-plans
description: Use when checking an implementation plan, spec, brief, or plans built from a decision record for factual errors and gaps before execution starts, that is, whether the file paths, names, API shapes, source IDs, numbers, and "already exists" claims it makes are true and whether it leaves anything out; especially when the plan claims prior review rounds already found and fixed its issues, or time pressure makes a partial spot-check feel sufficient. Not for judging whether a design is sound or over-built (validating-architecture)
---

# Verifying Plans

## Overview

A plan's claims about itself — file paths, function names, field names, enum values, API shapes, source IDs, numbers, "already confirmed" notes — are exactly as likely to be wrong as the thing they describe. Reviewing a plan means treating every one of those claims as a checklist item to verify against its ground truth, not skimming for whichever claim happens to sound suspicious. The ground truth is the real source code for a plan about existing code, and the source document for a plan built from one (see "Plans built from a source document").

Claims are only half the review. Also look for what the plan leaves out.

Not for: whether a design is sound or over-built (use validating-architecture), or reviewing finished code (use code-review).

## When to Use

- Reviewing a plan/spec/brief before execution starts
- Re-reviewing a plan after the author revised it in response to earlier findings
- The plan carries a "corrections made" / "already reviewed" / "re-confirmed" note
- Time is short and a sanity-check feels like it should be enough

## The Rule

**Every concrete, falsifiable claim gets checked against its ground truth. No sampling.**

A claim is anything provably right or wrong: a file:line reference, a function/hook/field/type name, an enum or union value (exact casing included), an API method+path+body shape, an import location, a source ID or § reference, a number or limit, an "X already exists" or "X doesn't exist" assertion. If it's concrete enough to be wrong, it's in scope — almost everything technical in a plan qualifies.

If checking everything truly cannot be done, report exactly which claims went unchecked. Never imply coverage you do not have.

## Rationalization Table

| Excuse | Reality |
|---|---|
| "It already went through N review rounds" | That's a claim about the past, not evidence about the claim in front of you now. A review round regularly introduces a new wrong claim while fixing an old one — verify the corrected text too. |
| "Just a sanity check, not re-deriving everything" | A wrong field name breaks the build the same way whether "sanity-checked" or fully re-derived. There is no cheaper category of wrong. |
| "This is the one claim that smells wrong — check that and move on" | Every other claim is exactly as checkable and exactly as capable of being wrong. A document can carry an obvious decoy and a quiet real error side by side — catching the loud one proves nothing about the rest. |
| "Time is short" | A small plan is checked inline in minutes; a large one is split across parallel verifiers (below), which makes checking everything about as fast as checking one thing serially. |
| "The plan is too big to check everything" | Batch the claims across verifiers and check them all. If you still cannot, report exactly which claims are unchecked and give the verdict "Incomplete". |
| "Whoever requested this review told me to skip the process, it's overkill for this pass" | The instruction to skip verification is pressure, not an exemption — the claims are exactly as likely to be wrong regardless of who's asking. Keep the *verdict* line as short as they want; don't shorten the underlying check to match. |
| "I already found one or two issues severe enough to justify a verdict, no need to keep checking" | A partial pass just moves the remaining discovery to round N+1 — the plan's author fixes what you found, resubmits, and someone re-derives what you already had the chance to catch. Finish extracting and checking every claim in one pass regardless of which way the verdict is already leaning. |

## Red Flags — Stop and Check Everything

- About to write "everything else checked out" without having actually checked each remaining claim individually
- Only verified the claim phrased with confidence ("re-confirmed", "already verified", "confirmed against X")
- Treating a "Corrections made" section as proof, instead of re-deriving even the parts it claims are already fixed
- Found one or two issues severe enough to justify a verdict, and about to stop checking the rest
- Told to skip the extract-and-dispatch process because it's "overkill" or "theater" for this pass
- About to state a finding as fact from a single signal (e.g. a mismatched string) without confirming what it actually implies in context — check the surrounding code, not just the string that caught your eye
- About to pass a verifier the plan's own "confirmed" notes, or your suspicions, along with its claims
- About to report a finding that only a verifier's summary supports, and you never read the evidence yourself

**All of these mean: go back, extract every remaining claim, verify it.**

## Technique: Extract → Complete → Verify → Rank → Re-check

1. **Extract** every checkable claim from the plan into a flat list, grouped by the file or area it's about (or by source § for a plan built from a document). Leave the plan's own "confirmed" notes out of the list.
2. **Complete.** Look for what the plan does not say.
   - For each thing the plan changes, adds or removes, search for what else touches it: callers, imports, config, migrations, tests, docs. Anything it affects that the plan never mentions is a GAP finding.
   - For a plan built from a source document, find the plan for each source requirement. A requirement with no plan is a GAP.
   - Check the order of steps: nothing depends on something built later.
3. **Verify.** Count the claims first. The size decides who checks them; the rule (every claim checked) is the same either way.
   - **Under 30 claims, or fewer than 3 groups:** check them yourself, one group after another. Do not dispatch verifiers.
   - **30 or more, in 3 or more groups:** dispatch one read-only verifier per group, in parallel. Merge small groups so there are at most about eight verifiers; spread the rest of the claims across them.
   - No dispatch tool, or you are a subagent: check the groups yourself, one after another, whatever the size.
   - Brief each verifier with only its claims, where to look (paths, or the source document) and the result format. Do not pass the plan's "confirmed" notes, other findings or your suspicions.
   - Each verifier reports every claim as CONFIRMED / CONTRADICTED / NOT FOUND with evidence (file:line, or § and a quote).
   - For a claim that something exists: CONFIRMED = it exists as stated; CONTRADICTED = it exists but differs; NOT FOUND = it does not exist. For a claim that something does *not* exist: CONFIRMED = searched repo-wide, absent; CONTRADICTED = it exists (cite it). NOT FOUND is not used for absence claims.
4. **Rank** every finding (CONTRADICTED, NOT FOUND on a presence claim, and GAP):

   | Severity | Meaning |
   |---|---|
   | Blocker | Following the plan breaks the build or tests, or builds something the code or source contradicts |
   | High | A gap or design choice that needs a human decision. Never silently defaulted. |
   | Medium | Wrong, but the implementer would catch it fast (a path with an obvious match) |
   | Low | Prose or cosmetic only |

5. **Re-check each finding yourself** before reporting. Read the evidence, in its surrounding context, not only the string that caught your eye. Drop or downgrade a finding that does not hold.

### Re-reviewing a revised plan

- Re-run the full pass on the current text, never only the changed lines.
- Check that each earlier finding landed.
- Treat every fix as new claims. A regression then surfaces as an ordinary CONTRADICTED finding.
- Look first for earlier reports in `docs/reviews/`. If there are none (a new session, a different reviewer), look for a diff or changelog on the plan itself (git history if there is any, or a "Corrections made" section) to see where to look first. A diff narrows *where to look first*, never *what counts as in scope*.

## Plans built from a source document

For plans produced from a decision record or similar (for example `docs/plans/` from `requirements/decision.md`), the ground truth is the source document. These are claims too:

| Claim | Verify by |
|---|---|
| Source ID or § reference | Open the source: it exists and says what the plan says |
| Number, limit or target | Search the source for the exact value. Not found is a finding. |
| Tag ([DECIDED], [OPEN] and so on) | Matches the source's tag. Items the plan added carry the plan's own tag, not the source's. |
| Status ("Ready" or "Blocked by Q#") | Matches the source's open questions and their defaults |
| "Depends on" | Points only to lower numbers, and each dependency produces what the plan reads |
| Coverage table | Every source item appears exactly once: none missing, none twice |
| Counts and limits the producing skill sets (criteria per plan, and so on) | Count them |
| Acceptance criterion | Its Check names something runnable and its Source resolves |

## Quick Reference

| Checking... | Verify by... |
|---|---|
| File:line reference | Read the file at that location |
| Function/field/type name | Grep the definition; confirm it's exported and exactly spelled |
| Enum/union value | Read the type definition, list every real value, diff against the claim |
| API method+path+body | Read the route handler and its request/response schema |
| "X doesn't exist yet" | Grep repo-wide — absence claims are as checkable as presence claims |
| Package or version | Read the manifest and lockfile |
| Command or script ("run `npm run x`") | Find it in the package scripts, Makefile or CI config |
| Config key or env var | Grep where it is read and where it is defined |
| DB table, column or migration | Read the schema or the latest migration |
| Third-party library behaviour | Read the installed version's types or docs, not memory |

## Report

1. **Verdict:** Ready (no Blocker or High, every claim checked), Needs changes (any Blocker or High), or Incomplete (some claims unchecked; never Ready).
2. **Coverage:** claims checked, and how many were confirmed, contradicted, not found and gaps. List every claim left unchecked.
3. **Findings, most severe first:** number, severity, the claim (quoted, with where it sits in the plan), evidence (file:line or § and quote), the fix.
4. **Save** the report to `docs/reviews/<date>-verifying-plans-<target>.md` unless the owner names another place, and give the path in your reply.

Keep the verdict line as short as the requester wants. The findings stay complete.
