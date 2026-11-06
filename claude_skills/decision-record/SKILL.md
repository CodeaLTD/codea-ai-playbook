---
name: decision-record
description: Use when creating or refreshing requirements/decision.md, the plain-English decision record built from everything in requirements/ before the PRD and architecture documents are written, or when files in requirements/ changed and decision.md may be out of date
---

# Decision Record (requirements/decision.md)

## Overview

`requirements/decision.md` is the one human-readable record of what the project has decided, how it fits the client's brief, and what is still unanswered. An architecture document, and a PRD if the project wants one, are written from it later, so it must be self-contained.

**Core rule: the file reports what the sources say.** Your own opinion lives in only two labelled places: the sanity check (section 9) and the open questions (section 10). Never invent a decision, a number or a target.

The exact section list is in [sections.md](sections.md). Read it before writing.

**Which project this is for:** the source rules (steps 2 and 3) and the topic list in sections.md are written for the OpsFleet BigQuery analytics-agent brief. For another project, keep the process, language rules, layout rules and self-check, replace those two project parts, and say so in the reply.

## When to Use

- The owner asks for `decision.md`, a decision record, or a summary of `requirements/`
- A file in `requirements/` was added or changed and `decision.md` may be stale
- Before writing the PRD or the architecture document

Do not use it to write the PRD, the architecture document, or code.

## Process

1. **Check the target.** Does `requirements/decision.md` exist?
   - **No:** build it new.
   - **Yes:** this is a refresh. Read the whole file first. Edit in place. Keep every ID stable (3.x, NFR1, A1, S1, Q1). Never renumber. Put new items at the end of their table. Keep the owner's edits: tags they changed to [DECIDED], notes, answered questions. Do not rebuild an existing file from scratch without the owner's OK. The folder may not be a git repo, so an overwrite cannot be undone.
2. **Read every source in full.** Every file in `requirements/` EXCEPT `decision.md` itself (it is the output, never a source). Open the PNG files with the Read tool and treat what they show as a source. Read `bq_client.py` as code: what it queries, its cost guards, its error handling, which PII it can touch. The brief is `Original_Requirements.md` and it is the source of truth. The filename `Result_Guard _PII_mask.md` contains a space.
3. **Apply these source rules** (the file names are the OpsFleet brief's; for another project, list its own files and their rules):
   - The main decisions file (today `Phase1-decisions.md`) ends with chat leftovers, for example "Want me to add this example to the doc as section 3.19?". Drop the chat wording but keep the content: the replan walk-through, the turn-context, glossary and idempotency Q&A, the "Still not in the doc" list, the "Questions before I start Phase 2" list and the "Open for Phase 2" points. They feed the open questions.
   - Most decisions there are proposals awaiting approval. Use [PROPOSED] unless a file shows explicit approval.
   - If files disagree, do not pick a winner. Use [CONFLICT] and quote both sides.
4. **Write or update the file** following [sections.md](sections.md) and the rules below.
5. **Self-check** (below), fix, and check again.
6. **List the directory again** to confirm no source was missed. If a file is unreadable, say so.
7. **Reply** as described in "Final reply".

## Language: human-readable B2 English (most important rule)

Write plain English at CEFR level B2. A reader who is not a native speaker and is not an AI specialist must understand it on the first read.

- One idea per sentence. Average 12-15 words, never more than 20.
- Active voice: "The SQL Guard blocks the query", not "The query is blocked".
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
- Use a technical word only as defined in the Glossary. Use no abbreviation that is not in the Glossary. Product and library names (BigQuery, LangGraph, sqlglot, Gemini) stay as they are. Code names go in backticks.
- Use plain headings and column names: "Why", "How we reduce it", "What remains", "Who can see what". Avoid "tenancy", "traceability", "mitigation", "residual".
- Do not copy sentences from the sources. They are dense. Rewrite them in simple English and keep every exact number, limit, threshold, model name and service name.

| Bad | Good |
|---|---|
| Deterministic code enforces every security property, treating the LLM as an untrusted proposer. | The AI model only suggests. Our code checks every suggestion and enforces the security rules. |
| Fail-closed on policy-store outage. | If the access-rules database is down, the system blocks the request. |

## Layout rules

1. Bullets and tables only. Target 400-500 lines. Hard maximum 550.
2. Tables: at most 5 columns, at most 20 words per cell, one idea per cell, no bullets inside cells, no multi-sentence cells.
3. Paragraphs: at most 2 lines. No nested bullets deeper than 2 levels.
4. Say each fact once. Elsewhere refer to it by section ("see 3.4") or ID ("see NFR3", "see Q7").
5. Labels: the five status tags in capitals in square brackets ([DECIDED], [PROPOSED], [OPEN], [NOT SPECIFIED], [CONFLICT]), plus P0 / P1 / P2, Blocker / High / Medium / Low, Full / Partial / Gap. No emojis.
6. IDs: only decision numbers (3.1...), NFR1..., A1..., S1..., Q1.... No other ID systems.
7. Cite sources briefly at the end of a decision, for example (Phase1 3.4). In tables use the Source column.
8. Facts and opinion stay separate. Sections 1-8 contain only what the sources say. Sections 9.2, 9.3 and 10 may hold your judgement, and 9.2 must be labelled as opinion. Hidden assumptions in section 5 are marked "Not stated".

## Self-check

Layout:
- Count the lines. Find the longest table row and the longest paragraph.
- No table has more than 5 columns.
- Every decision heading and every NFR row has a status tag.
- Every assumption has a linked question, or "None".

Language (a one-off command that writes no files is fine):
- Find every sentence longer than 20 words and split it.
- Find passive sentences, idioms, "e.g./i.e./etc." and any word from the table above, and rewrite them.
- Find every abbreviation or technical term that is not in the Glossary. Add it to the Glossary or use a plain phrase.

## Common mistakes

| Mistake | Fix |
|---|---|
| Reading `decision.md` as a source | It is the output. Exclude it from the reading step. |
| Marking Phase 1 proposals [DECIDED] | Use [PROPOSED] unless a file shows approval. |
| Inventing an NFR target or a storage location | Write [NOT SPECIFIED]. |
| Redrawing or "improving" the diagram | Copy it verbatim. Put differences in bullets under it. |
| Dropping the Phase 1 chat leftovers | Keep their content as open questions and decisions. |
| Renumbering IDs on a refresh | IDs are stable. Add new ones at the end. |
| Overwriting an existing `decision.md` | Edit in place and keep the owner's edits. |
| Long cells, 6+ column tables, paragraphs over 2 lines | Split or cut. |

## Final reply

- The path of the file
- Whether it was created or refreshed, and for a refresh what changed (new, changed, removed items)
- Line count; decisions by status tag; number of NFRs and assumptions; sanity-check findings by severity; open questions by priority
- Language check result: longest sentence in words, and how many sentences you split
- Conflicts found between the source files, one line each
- The 5 most critical P0 questions, one line each
- Any source file you could not fully read
