# decision.md: exact section list

Write the sections in this order. The language and layout rules are in [SKILL.md](SKILL.md). Where a section says **profile**, the project's `.claude/decision-record-profile.md` supplies the detail (see [profile-template.md](profile-template.md)). Without a profile, use the default given here.

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
5. **Glossary**: a table (Term | Meaning), at most 25 rows, sorted A-Z, term at most 3 words, meaning at most 15 words. It covers every abbreviation and technical term used anywhere in the file: abbreviations such as PII, NFR or SLA, and the names the project gives its own components. **Profile:** seed terms.

## 1. Problem framing and scope

- Users: table (Persona | Needs), at most 5 rows.
- What "good" looks like: 4-6 plain-language bullets. Put the numbers in section 4, not here.
- What makes it hard: table (Hard part | What we do about it).
- Scope: three short bullet groups (In scope / Out of scope / Prototype vs design-only, if the brief separates them), then one line of constraints from the brief: for example the time box, model or API limits, the interface, where it must run, the dataset. If the brief says which requirements a prototype must cover, name them; the others are design-only. **Profile:** the constraints line and the prototype requirements.

## 2. Architecture

- **Keep the diagram.** Copy the main architecture diagram VERBATIM into a fenced code block. Do not redraw, shorten or "improve" it. **Profile:** which file holds it, and the lines where it starts and ends. Default: the architecture diagram in the main decisions file; if there are several, ask. On a refresh, keep the existing diagram unless the source diagram changed.
- Under the diagram add "Differences from the diagram": bullets for components or arrows that other files or images show but the diagram does not (for example a shortcut one image shows between two steps). Do not edit the diagram itself.
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

Topics, in this order. **Profile:** its own topic list replaces this one. Add a topic only if the sources cover something that fits none of them.

| # | Topic |
|---|---|
| 3.1 | Framework and main stack |
| 3.2 | AI model choice and routing (a small table Step / Model is fine) |
| 3.3 | Main data and knowledge stores: what lives where, how it is found at query time, how it is updated |
| 3.4 | Who can see what: access rules and personal data (a small table Layer / What it enforces) |
| 3.5 | Input and output safety checks |
| 3.6 | Destructive actions and user confirmation |
| 3.7 | Learning from each user: memory and personal style |
| 3.8 | Learning for the whole system: feedback, human review, failure mining |
| 3.9 | Changing behaviour or tone without redeploy |
| 3.10 | Main processing loop: planner, repair and retry loops, limits, saved state, duplicate protection. Give the real numbers: retries, call limits, timeouts. |
| 3.11 | Resilience and cost control (a small table What happened / What the system does) |
| 3.12 | Observability, monitoring and logging: traces, metrics, audit log, alerts, how to debug one request, personal data in logs, version stamping |
| 3.13 | Quality checks and evaluation: offline tests, test sets, AI judge, UX evaluation, deploy gates |
| 3.14 | Extensibility (new tools or integrations) |

If the sources say nothing about a topic, keep the heading and tag it [NOT SPECIFIED]. Drop a default topic only when the brief rules it out (for example 3.2 when there is no AI model), and say so in one line at the top of section 3.

## 4. Non-functional requirements

Quality targets for the system. A table: ID (NFR1, NFR2...) | Requirement | Target | Status tag | Source.

Cover, where the sources say anything: response time, cost limits, reliability and availability, security, privacy and personal data, observability, audit, scale and number of users, how long data is kept, how easy it is to extend and change, usability. **Profile:** the main NFR sources. Default: the budgets, retry limits, timeouts and defaults in the decision files, then the brief.

Target = the exact number or limit from the source. If there is none, write [NOT SPECIFIED]. Do not invent targets.

## 5. Assumptions

Everything the design takes for granted. A table: ID (A1, A2...) | Assumption | Source | What happens if it is wrong | Linked question (Q number).

Include the assumptions the sources state (for example rows marked "My default") AND the hidden ones you find. For hidden ones write "Not stated" in the Source column. Every assumption links to a question in section 10, or says "None".

## 6. Where is the data?

One table, one row per data store or flow: Data | Stored in (production -> prototype) | Contains PII? | Written by -> read by | How long we keep it.

Include every data store and flow the sources name, and at least: the source data, stored examples or knowledge, search indexes, saved user content, user preferences and memory, conversation or session state, configuration, traces, logs and metrics, the audit log, evaluation data, caches, secrets. **Profile:** more stores to include.

If a source does not say, write [NOT SPECIFIED]. Do not guess. Under the table, 3-6 bullets on the data questions nobody has answered yet.

## 7. Fit against the original brief

- 7.1 Table: # | Brief requirement (at most 10 words) | Prototype or design-only | Covered in section | Fit (Full / Partial / Gap). One row per brief requirement, numbered as the brief numbers them. **Profile:** requirements to split into parts.
- 7.2 Deliverables checklist as bullets: every deliverable the brief lists, each marked done / partial / missing.
- 7.3 Expected capabilities: bullets for every capability or example question the brief lists, each marked covered or not.
- 7.4 "Beyond or against the brief": bullets listing extra scope and contradictions.

## 8. Prototype vs production

Table: Production | Prototype stand-in. Include everything the decision files list as a prototype stand-in, plus anything the other files add. No prototype in scope: one line saying so.

## 9. Sanity check

- 9.1 Risks the documents already list: table Risk | How we reduce it | What remains, at most 10 rows, taken from the sources.
- 9.2 NEW findings (your own opinion, say so in one line): table ID (S1, S2...) | Severity (Blocker / High / Medium / Low) | Finding | Suggested fix. At most 15 rows, most severe first.

  What to look for (do NOT output one section per item):
  - Does the design really satisfy the brief, or only look like it does?
  - Do the files agree on components, data stores, flows and numbers (for example a call limit vs the number of retry attempts)?
  - Is it possible in the time box, and what is the smallest version that still meets the brief's must-haves?
  - Ways personal data can leak (query results, logs, traces, memory, stored examples, error messages) and ways a user can see another user's data
  - Can the data the brief names really support what the brief asks for?
  - Prompt injection through data or stored examples, and ways to skip a confirmation step
  - Runaway cost and retry storms (model and API limits, data scanned or billed)
  - Can we answer "what failed and why" for one request?
  - Risks in the learning loops (bad feedback, drift, one user's preferences reaching another user)
  - Do the targets in section 4 match what the design can deliver? Are any assumptions in section 5 risky?
  - **Profile:** the project's own questions.
- 9.3 Verdict: 3-5 bullets. Is this ready to become a PRD and an architecture document, and what must change first?

## 10. Open questions (last content section)

Collect EVERY unanswered question: the open points in the sources, the gaps from sections 4-9, and anything you notice yourself. Do not drop any question the sources already raise.

Table: ID (Q1, Q2...) | Question | Default if unanswered | Who answers (client / us) | Priority. **Profile:** the client's name for the "Who answers" column.

- Start each question with a bold area label, for example "**Data:** Where do uploaded files live?"
- Priority: P0 = blocks the PRD or the build, P1 = blocks the architecture document, P2 = can wait.
- Sort by priority, then by area.
- On a refresh, when a question gets answered: set Priority to "Answered", write the answer in the Default cell starting with "Answer:", and update the affected decision, NFR or assumption.

Questions that must be covered (expand them, do not limit yourself to them):

- Where is every piece of data stored, who owns it, and how long is it kept (section 6)?
- Any data or example set the design relies on: does it exist, in what format, and do we use fake data for a prototype?
- What limits what each user can see, and which key or column enforces it?
- How do users log in: in the prototype and in production?
- Which fields are personal data, which are blocked in queries, and which are masked in the output?
- Saved user content: structure, storage, soft or hard delete, undo time
- Conversation history and user memory: where they live and how a user can delete them
- Configuration that changes behaviour: who edits, who approves, versions, rollback
- Observability tool, exact metric definitions, alert limits, how long logs are kept, removing personal data from logs
- Limits per request and per user (tokens, money, data scanned), retry limits, which models, fallbacks, and how to handle rate-limit errors (429)
- Evaluation: who builds and labels the test set, what the pass/fail gates are, how we measure UX
- Business terms the brief uses but does not define (for example time periods, currency, timezone)
- How we update stored examples or knowledge safely
- How extensions stay inside the safety rules
- Production deployment target
- Every target in section 4 marked [NOT SPECIFIED]
- Everything the decision files list as open or "not in the doc yet"
- **Profile:** the project's must-cover questions

## 11. Next documents

At most 10 lines:

- The PRD (if the project wants one) should use: (sections of decision.md, including sections 4 and 5, and the product questions)
- The architecture document should use: (sections of decision.md, including sections 4 and 5)
- Questions to answer before the PRD: (Q numbers)
- Questions to answer before the architecture document: (Q numbers)
