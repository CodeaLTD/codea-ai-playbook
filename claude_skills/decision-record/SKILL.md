---
name: decision-record
description: Use when creating or refreshing requirements/decision.md, the plain-English decision record built from everything in requirements/ before the PRD and architecture documents are written, or when files in requirements/ changed and decision.md may be out of date
---

# Decision Record (requirements/decision.md)

## Overview

`requirements/decision.md` is the one human-readable record of what the project has decided, how it fits the client's brief, and what is still unanswered. An architecture document, and a PRD if the project wants one, are written from it later, so it must be self-contained.

**Core rule: the file reports what the sources say.** Your own opinion lives in only two labelled places: the sanity check (section 9) and the open questions (section 10). Never invent a decision, a number or a target.

The exact section list is in [sections.md](sections.md). Read it before writing.

**Project profile.** The parts that belong to one project live in that project, in `.claude/decision-record-profile.md`: which file is the brief, rules for particular source files, the section 3 topics, scope constraints, glossary seed terms, the brief's requirements and the project's own questions. Its layout is in [profile-template.md](profile-template.md). This skill names no client, file or dataset. No profile: use the defaults here and in sections.md, say so in the reply, and offer to write a profile from what you learned.

**Script path:** `<skill-dir>` below is this skill's own folder, the "Base directory for this skill" Claude Code shows when the skill loads.

## When to Use

- The owner asks for `decision.md`, a decision record, or a summary of `requirements/`
- A file in `requirements/` was added or changed and `decision.md` may be stale
- Before writing the PRD or the architecture document

Do not use it to write the PRD, the architecture document, or code.

## Process

1. **Check the target.** Does `requirements/decision.md` exist?
   - **No:** build it new.
   - **Yes:** this is a refresh. Read the whole file first. Edit in place. Keep every ID stable (3.x, NFR1, A1, S1, Q1). Never renumber. Put new items at the end of their table. Keep the owner's edits: tags they changed to [DECIDED], notes, answered questions. Do not rebuild an existing file from scratch without the owner's OK. The folder may not be a git repo, so an overwrite cannot be undone.
2. **Read the profile** if `.claude/decision-record-profile.md` exists. Its rules add to the ones below and win where they differ.
3. **Read every source in full.** Every file in `requirements/` EXCEPT `decision.md` itself (it is the output, never a source).
   - Open image files (PNG, JPG) with the Read tool and treat what they show as a source.
   - Read code files as code: what they query or call, their cost and safety guards, their error handling, and which personal data they can touch.
   - File names may contain spaces. Quote them.
   - **The brief is the source of truth:** the file the profile names. No profile: the file the owner names, or the one that is plainly the client's original request. If that is unclear, ask.
4. **Apply these source rules:**
   - Decision files written in a chat often end with chat leftovers, for example "Want me to add this example to the doc as section 3.19?". Drop the chat wording but keep the content: walk-throughs, Q&A, "still not in the doc" lists and open points. They feed the open questions.
   - A decision a source only suggests is [PROPOSED] unless a file shows explicit approval.
   - If files disagree, do not pick a winner. Use [CONFLICT] and quote both sides.
5. **Write or update the file** following [sections.md](sections.md) and the rules below.
6. **Self-check** (below), fix, and check again.
7. **List the directory again** to confirm no source was missed. If a file is unreadable, say so.
8. **Reply** as described in "Final reply".

## Language: human-readable B2 English (most important rule)

Write plain English at CEFR level B2. A reader who is not a native speaker and is not an AI specialist must understand it on the first read.

- One idea per sentence. Average 12-15 words, never more than 20.
- Active voice: "The access check blocks the request", not "The request is blocked".
- Use common words:

| Instead of | Write |
|---|---|
| leverage, utilize | use |
| mitigate | reduce |
| rationale | why |
| residual | what remains |
| obtain | get |
| subsequently | then |
| prior to | before |
| in order to | to |
| ensure | make sure |
| facilitate | help |
| robust | reliable |
| comprehensive | full |

- No idioms, slang, jokes or marketing language.
- Never write "e.g.", "i.e." or "etc." Write "for example", "that is", or list the items.
- No stacked noun phrases and no long nested clauses. Split them into two sentences.
- Use a technical word only as defined in the Glossary. Use no abbreviation that is not in the Glossary. Product and library names (for example PostgreSQL, React, Stripe) stay as they are. Code names go in backticks.
- Use plain headings and column names: "Why", "How we reduce it", "What remains", "Who can see what". Avoid "tenancy", "traceability", "mitigation", "residual".
- Do not copy sentences from the sources. They are dense. Rewrite them in simple English and keep every exact number, limit, threshold, model name and service name.

| Bad | Good |
|---|---|
| Duplicate submissions are rejected through idempotency-key enforcement at the API layer. | Each request carries a key. The API drops a request whose key it has already seen. |
| Fail-closed on identity-provider outage. | If the login service is down, the system blocks every request. |

## Layout rules

1. Bullets and tables only. Target 400-500 lines. Hard maximum 550.
2. Tables: at most 5 columns, at most 20 words per cell, one idea per cell, no bullets inside cells, no multi-sentence cells.
3. Paragraphs: at most 2 lines. No nested bullets deeper than 2 levels.
4. Say each fact once. Elsewhere refer to it by section ("see 3.4") or ID ("see NFR3", "see Q7").
5. Labels: the five status tags in capitals in square brackets ([DECIDED], [PROPOSED], [OPEN], [NOT SPECIFIED], [CONFLICT]), plus P0 / P1 / P2, Blocker / High / Medium / Low, Full / Partial / Gap. No emojis.
6. IDs: only decision numbers (3.1...), NFR1..., A1..., S1..., Q1.... No other ID systems.
7. Cite sources briefly at the end of a decision, for example (decisions 3.4). In tables use the Source column.
8. Facts and opinion stay separate. Sections 1-8 contain only what the sources say. Sections 9.2, 9.3 and 10 may hold your judgement, and 9.2 must be labelled as opinion. Hidden assumptions in section 5 are marked "Not stated".

## Self-check

Run the checker, fix what it reports, and run it again until it reports nothing to fix. It writes nothing.

    python <skill-dir>/scripts/check_decision.py requirements/decision.md

It checks the line count, table columns, words per cell, multi-sentence cells, paragraph length, bullet depth, sentence length (longest and average), the words in the table above, "e.g./i.e./etc.", emojis, a status tag on every decision heading and NFR row, a linked question on every assumption, and abbreviations missing from the Glossary. It also lists possible passive sentences.

Then check by hand what a script cannot:
- Each "possible passive" line: rewrite it if it really is passive.
- Every technical term (not only abbreviations) is in the Glossary, or replaced by a plain phrase.
- No sentence is copied from a source, and each fact is said once.

## Common mistakes

| Mistake | Fix |
|---|---|
| Reading `decision.md` as a source | It is the output. Exclude it from the reading step. |
| Marking proposals [DECIDED] | Use [PROPOSED] unless a file shows approval. |
| Inventing an NFR target or a storage location | Write [NOT SPECIFIED]. |
| Redrawing or "improving" the diagram | Copy it verbatim. Put differences in bullets under it. |
| Dropping the chat leftovers at the end of a decision file | Keep their content as open questions and decisions. |
| Renumbering IDs on a refresh | IDs are stable. Add new ones at the end. |
| Overwriting an existing `decision.md` | Edit in place and keep the owner's edits. |
| Long cells, 6+ column tables, paragraphs over 2 lines | Split or cut. |
| Writing client names or file names into this skill | They belong in the project's profile. |

## Final reply

- The path of the file
- Whether it was created or refreshed, and for a refresh what changed (new, changed, removed items)
- Whether a project profile was used
- Line count; decisions by status tag; number of NFRs and assumptions; sanity-check findings by severity; open questions by priority
- Language check result from the checker: longest sentence in words, average sentence length, and how many sentences you split
- Conflicts found between the source files, one line each
- The 5 most critical P0 questions, one line each
- Any source file you could not fully read
