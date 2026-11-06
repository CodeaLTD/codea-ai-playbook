# decision.md: exact section list

Write the sections in this order. The language and layout rules are in [SKILL.md](SKILL.md). The topic table in section 3, the scope line in section 1 and the glossary examples are the OpsFleet brief's. For another project, replace them and keep the other sections.

## Front matter

1. Title, then one line: `Status: draft built from requirements/ on <today's date>`. On a refresh write `Status: draft, refreshed from requirements/ on <today's date>`.
2. **Status tags** (the legend). A table (Tag | Meaning) with exactly these five rows:
   - [DECIDED]: a source says it is final, or the owner approved it
   - [PROPOSED]: a source suggests it, but nobody approved it yet
   - [OPEN]: a source raises it, and there is no answer yet
   - [NOT SPECIFIED]: no source says anything about it
   - [CONFLICT]: two sources disagree (quote both)

   Add one line under the table: "Where used: every decision heading, every NFR row, and any item that is missing or disputed."
3. **At a glance**: at most 10 short bullets (what we build, the architecture in 2 lines, prototype vs design-only, top 3 risks, top 3 open questions).
4. **Contents**: table of contents with links.
5. **Glossary**: a table (Term | Meaning), at most 25 rows, sorted A-Z, term at most 3 words, meaning at most 15 words. It covers every abbreviation and technical term used anywhere in the file, for example PII, Golden Bucket, Trios, Saved Reports, SQL Guard, Result Guard, Output Guard, k-anonymity, human-in-the-loop, checkpoint, idempotency key, dry-run, persona, learning loop, replan.

## 1. Problem framing and scope

- Users: table (Persona | Needs), at most 5 rows.
- What "good" looks like: 4-6 plain-language bullets. Put the numbers in section 4, not here.
- What makes it hard: table (Hard part | What we do about it).
- Scope: three short bullet groups (In scope / Out of scope / Prototype vs design-only), then one line of constraints: 6-12h time box, Gemini free-tier limits, CLI, must run on another machine, dataset `bigquery-public-data.thelook_ecommerce`. The brief says the prototype must cover Safety & PII, High-Stakes Oversight, Resilience and Observability. The other four requirements are design-only.

## 2. Architecture

- **Keep the diagram.** Copy the diagram from the main decisions file (today `Phase1-decisions.md`, section 2) VERBATIM into a fenced code block. Take everything from the line starting `[ Executive ]` through the line starting `[ CI ] ──> [ Eval Pipeline ]`. That covers the main flow, the LLM Gateway, Telemetry and the offline/control planes. Do not redraw, shorten or "improve" it. On a refresh, keep the existing diagram unless the source diagram changed.
- Under the diagram add "Differences from the diagram": bullets for components or arrows that other files or the PNGs show but the diagram does not (for example the shortcut from the Input Guard to the Tool Router for delete requests). Do not edit the diagram itself.
- Add a Mermaid flowchart of the main request path only (at most 20 nodes, same names as the diagram) so it renders visually in a preview. This is the one place Mermaid is allowed; architecture diagrams elsewhere use the text format in brainstorming-architecture.
- Then a step table (Step | What it does | Tech / model), one row per box in the diagram, at most 20 words per cell.

## 3. Key decisions

One block per topic, in EXACTLY this format, at most 6 lines per block:

    ### 3.x Topic [DECIDED | PROPOSED | OPEN | NOT SPECIFIED | CONFLICT]
    - **Choice:** ...
    - **Why:** ...
    - **Rejected:** option A; option B
    - **Revisit if:** ...
    - **Data lives in:** ... (only if the topic stores data)
    - **Source:** (file, section)

Topics, in this order. Add a topic only if the sources cover something that fits none of these:

| # | Topic |
|---|---|
| 3.1 | Agent framework |
| 3.2 | AI model choice and routing (a small table Step / Model is fine) |
| 3.3 | Golden Bucket: where it is stored, how we find examples at query time, how we update it over time |
| 3.4 | Who can see what: access rules and PII (a small table Layer / What it enforces) |
| 3.5 | SQL safety and checks |
| 3.6 | Destructive actions and user confirmation |
| 3.7 | Learning from each user: memory and personal style |
| 3.8 | Learning for the whole system: feedback, analyst review, failure mining |
| 3.9 | Changing the tone without redeploy (persona management) |
| 3.10 | Agent loop: planner, SQL repair loop, replan loop, limits, saved state, duplicate protection. Give the real numbers: retries, call limits, timeouts. |
| 3.11 | Resilience and cost control (a small table What happened / What the system does) |
| 3.12 | Observability, monitoring and logging: traces, agent-level metrics, audit log, alerts, how to debug one conversation, PII in logs, prompt and persona version stamping |
| 3.13 | Quality checks and evaluation: offline tests, golden test set, AI judge, UX evaluation, deploy gates (see `README-evaluation.md`) |
| 3.14 | Extensibility (tool registry: charts, email, web search) |

If the sources say nothing about a topic, keep the heading and tag it [NOT SPECIFIED].

## 4. Non-functional requirements

Quality targets for the system. A table: ID (NFR1, NFR2...) | Requirement | Target | Status tag | Source.

Cover, where the sources say anything: response time, cost limits, reliability and availability, security, privacy and PII, observability, audit, scale and number of users, how long data is kept, how easy it is to extend and change, usability. The main source is `loop-engineering-non-functional.PNG`. Then use the main decisions file (budgets, retry limits, timeouts, the section 6 defaults) and the brief.

Target = the exact number or limit from the source. If there is none, write [NOT SPECIFIED]. Do not invent targets.

## 5. Assumptions

Everything the design takes for granted. A table: ID (A1, A2...) | Assumption | Source | What happens if it is wrong | Linked question (Q number).

Include the assumptions the sources state (for example the "My default" rows in Phase 1 section 6) AND the hidden ones you find. For hidden ones write "Not stated" in the Source column. Every assumption links to a question in section 10, or says "None".

## 6. Where is the data?

One table, one row per data store or flow: Data | Stored in (production -> prototype) | Contains PII? | Written by -> read by | How long we keep it.

Include at least: BigQuery source tables, Golden Bucket (trios), glossary, search index, Saved Reports, user preferences and style, conversation state, persona config, traces/logs/metrics, audit log, evaluation data, caches, secrets.

If a source does not say, write [NOT SPECIFIED]. Do not guess. Under the table, 3-6 bullets on the data questions nobody has answered yet.

## 7. Fit against the original brief

- 7.1 Table: # | Brief requirement (at most 10 words) | Prototype or design-only | Covered in section | Fit (Full / Partial / Gap). One row per brief requirement, with R4 split into 4.1 and 4.2.
- 7.2 Deliverables checklist as bullets, each marked done / partial / missing: architecture diagram, technical explanation (items 2.1-2.5), working prototype, CLI, runs on another machine, framework choice plus experience statement, public GitHub repo.
- 7.3 Expected agent capabilities and dataset: bullets (customer behaviour, product performance, time-based metrics, questions about the data structure, multi-step questions, report with action items), each marked covered or not.
- 7.4 "Beyond or against the brief": bullets listing extra scope and contradictions.

## 8. Prototype vs production

Table: Production | Prototype stand-in. Include everything Phase 1 section 5 lists, plus anything the other files add.

## 9. Sanity check

- 9.1 Risks the documents already list: table Risk | How we reduce it | What remains, at most 10 rows, taken from the sources.
- 9.2 NEW findings (your own opinion, say so in one line): table ID (S1, S2...) | Severity (Blocker / High / Medium / Low) | Finding | Suggested fix. At most 15 rows, most severe first.

  What to look for (do NOT output one section per item):
  - Does the design really satisfy the brief, or only look like it does?
  - Do the files agree on components, data stores, flows and numbers (for example the call limit vs the number of SQL attempts)?
  - Is it possible in 6-12h, and what is the smallest version that still scores on the 4 prototype requirements?
  - Ways PII can leak (SQL results, logs, traces, memory, golden bucket, error messages) and ways a user can see another user's data
  - Can "products related to the user" really be found in `thelook_ecommerce`? Does the dataset support churn?
  - Prompt injection through data or trios, and ways to skip the delete confirmation
  - Runaway cost and retry storms (Gemini free-tier limits, BigQuery bytes billed)
  - Can we answer "what failed and why" for one conversation?
  - Risks in the learning loops (bad feedback, drift, one user's preferences reaching another user)
  - Do the targets in section 4 match what the design can deliver? Are any assumptions in section 5 risky?
- 9.3 Verdict: 3-5 bullets. Is this ready to become a PRD and an architecture document, and what must change first?

## 10. Open questions (last content section)

Collect EVERY unanswered question: the open points in the sources, the gaps from sections 4-9, and anything you notice yourself. Do not drop any question the sources already raise.

Table: ID (Q1, Q2...) | Question | Default if unanswered | Who answers (OpsFleet client / us) | Priority.

- Start each question with a bold area label, for example "**Data:** Where do saved reports live?"
- Priority: P0 = blocks the PRD or the build, P1 = blocks the architecture document, P2 = can wait.
- Sort by priority, then by area.
- On a refresh, when a question gets answered: set Priority to "Answered", write the answer in the Default cell starting with "Answer:", and update the affected decision, NFR or assumption.

Questions that must be covered (expand them, do not limit yourself to them):

- Where is every piece of data stored, who owns it, and how long is it kept (section 6)?
- The Golden Bucket is "theoretical": does it exist, in what format, and do we use fake data for the prototype?
- What does "products related to him" mean in `thelook_ecommerce` (there is no owner column)? What key limits what each user sees?
- How do users log in: in the CLI and in production?
- Which columns are PII, which are blocked in SQL, and which are masked in the output?
- Saved Reports: structure, storage, soft or hard delete, undo time
- Conversation history and user memory: where they live and how a user can delete them
- Persona config: who edits, who approves, versions, rollback
- Observability tool, exact metric definitions, alert limits, how long logs are kept, removing PII from logs
- Limits per question and per user (tokens, money, bytes), retry limits, which Gemini models, fallbacks, and how to handle rate-limit errors (429)
- Evaluation: who builds and labels the golden test set, what the pass/fail gates are, how we measure UX
- Definitions: churn, underspending, "last month", currency, timezone
- How we update the Golden Bucket safely
- How extensions (web, email, charts) stay inside the safety rules
- Production deployment target
- Every target in section 4 marked [NOT SPECIFIED]
- Everything Phase 1 lists as open or "not in the doc yet"

## 11. Next documents

At most 10 lines:

- The PRD (if the project wants one) should use: (sections of decision.md, including sections 4 and 5, and the product questions)
- The architecture document should use: (sections of decision.md, including sections 4 and 5)
- Questions to answer before the PRD: (Q numbers)
- Questions to answer before the architecture document: (Q numbers)
