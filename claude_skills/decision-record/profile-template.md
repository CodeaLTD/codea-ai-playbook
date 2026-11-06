# Decision record profile: layout

A profile holds the parts of a decision record that belong to one project. Save it in that project as `.claude/decision-record-profile.md`, never in the playbook: it names the client, its files and its data. The rules are in [SKILL.md](SKILL.md) and [sections.md](sections.md).

Every section is optional. A section you leave out uses the default in sections.md. A rule here wins over the skill's default where they differ.

```markdown
# Decision record profile: <project>

## Sources
- Brief (source of truth): `<file in requirements/>`
- Main decisions file: `<file>`
- File rules, one bullet per file that needs special handling, for example:
  - `<file>` ends with chat leftovers: keep <which lists> as open questions.
  - `<file>` is code: read what it queries, its guards and which personal data it touches.
  - `<file name with a space>` has a space in its name.

## Diagram (section 2)
Copy from `<file>`, section <n>, from the line starting `<text>` through the line starting `<text>`.

## Scope (section 1)
- Constraints line: <time box, limits, interface, where it must run, dataset>
- The prototype must cover: <brief requirements>. The others are design-only.

## Glossary seed terms
<term>, <term>, ...

## Section 3 topics
Replaces the default topic list. Same table shape:

| # | Topic |
|---|---|
| 3.1 | <topic> |

## NFR sources (section 4)
- Main source: `<file>`; then <other files and sections>.

## Data stores to include (section 6)
- <store>, <store>, ...

## Brief fit (section 7)
- Requirements to split: <for example "R4 into 4.1 and 4.2">
- Deliverables: <list from the brief>
- Capabilities: <list from the brief>

## Prototype vs production (section 8)
- Stand-ins listed in: `<file>`, section <n>

## Project questions
- For 9.2: <questions about this project's data, design or brief>
- For section 10: <questions that must be covered>
- Who answers: <client name> / us
```
