# implementation-plan.md: layout

The rules are in [SKILL.md](SKILL.md). The script writes the file; this page says what each section means and how to fill the sections marked `<!-- FILL: ... -->`.

| Section | Written by | What it holds |
|---|---|---|
| Header, "How to read it" | script | Build date, plan count, how to read waves, slack and AC |
| Start now | script | Plans not done whose plans in Depends on are all Done or Done (manual pending); plans In progress |
| Build waves | script | Diagram 1 |
| Builder lanes | script | Diagram 2, and how many builders are enough |
| Critical path | script | The plans with slack 0, wave by wave |
| Open manual checks and lead times | script lists open criteria of Done (manual pending) plans; you fill two tables | See below |
| Plans | script | One row per plan: wave, latest wave, slack, after, builder, AC, status |
| Parallel work: what collides | script lists the pairs; you fill the table | See below |
| How to run a wave | script | Branches, merge rule, rebuild, release checklist |
| Dependency findings | script lists what it can see; you add hidden dependencies | See below |
| Options the index names | you | See below |
| Owner notes | you | Copied from the previous file |

## The diagrams

Read them; never edit them. To change what they show, change the inputs (`--extra`) or the plans, and run the script again.

**Build waves.** One band per wave, top to bottom. Plans in one band do not depend on each other. Each box: line 1 is the plan number and name; line 2, `after`, lists the plans whose finish releases it (its Depends on, minus plans another of them already waits on); line 3 is its AC count and state: `slack n`, `waits on Q#`, `in progress`, `done` or `done, manual open`. A double border marks the critical path.

```text
WAVE 3 · 2 at once ───────────────────────────────────────────────────────────────────────────────
  ╔════════════════════════════╗   ┌────────────────────────────┐
  ║ 03 Cart                    ║   │ 05 Admin reports           │
  ║ after 02                   ║   │ after 02, 04               │
  ║ 6 AC · slack 0             ║   │ 4 AC · slack 1             │
  ╚════════════════════════════╝   └────────────────────────────┘
```

**Builder lanes.** Columns are waves, rows are builders. Lane 1 is the critical path (`━`). Every other plan sits in the lowest lane that has a free wave inside its slack (`─` joins one builder's plans in back-to-back waves). It is one valid schedule: a plan may move to any wave from its wave to its latest wave.

```text
          W1   W2   W3   W4   W5
builder 1 (01)━[02]━[03]━[06]━[07]
builder 2      [04]─[05]
```

## Open manual checks and lead times

Under the open criteria the script lists, one table. Read each criterion and its Check in the plan, then the later plans' criteria:

| Open criterion | What it proves | Later plans that rely on it | Do it before |
|---|---|---|---|
| AC-01.6 | The shop's pages show their text without JavaScript | 02: a "no" adds a browser crawler to its scope | 02 starts |
| AC-01.2 | Staff can log in with a real account | 05 (AC-05.4, manual part) | 05's manual check |
| AC-01.1 | The ports file rows, read by a person | None | – |

A later plan relies on an open check when its scope changes with the result, or when its own criteria need what the check proves (a real account, a deployed host). The row says when to do the check; it does not change the waves. If a review or note in the repo records a check's result, cite it with its file and line under the table.

Then the lead times: accounts, keys or access that take time to arrange. Take them from the plans and the index (its gaps often list them); never guess one.

| Item | First plan that needs it | Source |
|---|---|---|
| Payment provider test keys | 04 (manual check of AC-04.5) | 00-index.md, Gaps found |

None: "None found."

## Parallel work: what collides

Under the pairs the script lists, one table:

| Wave | Plans | Shared name | Kind | What to do |
|---|---|---|---|---|
| 2 | 02 + 04 | – | None found | – |
| 3 | 03 + 05 | `orders` table | Migration | The plan that merges second re-chains its migration onto the merged one |
| 3 | 03 + 05 | `OrderList` in `packages/ui` | Shared package | The second to merge rebases, runs the other plan's Checks and the package tests |

- One row per name that both plans of a pair add or change. Quote each plan's own words from its Scope In or What we build. A repo file the change lands in (a config module, a lock file) may go in "What to do", once you have checked that the file exists.
- A pair with no shared name gets one row: "–", "None found".

| Kind | Signs in the plans | What to do |
|---|---|---|
| Migration | Both add a migration, even for different tables: they share one migration head. Shared name: "migration head", then each plan's tables | The plan that merges second re-chains its migration onto the merged one, so there is one head |
| Same code | Both change one module, function or list of routes or tools (a turn task, a tool runner, a reducer, an admin menu) | The second to merge rebases and also runs the other plan's Checks. If both change how one function behaves (not just add an entry to a list), say so and suggest building them one after the other: the plan with more slack goes second, inside its slack |
| Shared package | Both change a shared package or component | As for same code, plus that package's tests |
| Config or manifest | Both add config keys, environment variables or dependencies | The second to merge regenerates the lock file; never merge it by hand |

## Dependency findings: hidden dependencies

Under the script's findings, one bullet per hidden dependency you passed with `--extra`:

    - Plan 05 needs plan 03: "totals per day from the `orders` table (plan 03)" (05-admin-reports.md:12). Added with --extra 05:03. Owner: add 03 to plan 05's Depends on.

None: "No hidden dependencies found."

## Options the index names

One bullet per order change that `00-index.md` offers but does not apply: what it is, quoted from the index; which plans would move to which wave and what would run beside them; and the cost the index names. Say that it is not applied. None: "None."

Take the waves from the script, never from your own arithmetic. Write the change as new Depends on values and run (it writes nothing):

    python <skill-dir>/scripts/build_order.py docs/plans --implied 01 --set 18=02-06

It prints the new finish wave, every plan whose wave or slack changes, and the new waves.

## Owner notes

The previous file's "Owner notes", word for word. First build: "None yet."
