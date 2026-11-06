# codea-ai-playbook
Practical AI engineering playbook by Codea: reusable Claude skills, learning materials, and production-tested patterns for LLM, RAG, and agent systems.

The skills are in [claude_skills/](claude_skills/). [claude_skills/README.md](claude_skills/README.md) describes what each one does, the order they run in, and what they need installed.

## Using the skills in another project

Claude Code looks for skills in two places:

- `~/.claude/skills/`: available in every project you open
- `<project>/.claude/skills/`: available only in that project

Pick one of these three setups:

| Setup | Who gets the skills | How they stay up to date |
|---|---|---|
| [Link them globally](#option-1-link-globally) | You, in every project | `git pull` in this repo |
| [Link them into one project](#option-2-link-into-one-project) | You, in that project only | `git pull` in this repo |
| [Copy them into the project and commit](#option-3-copy-into-the-project) | Everyone who clones the project | Copy them again |

Put each skill in one place only, either global or in the project. If it's in both, you can't tell which version runs.

### Option 1: link globally

Windows (PowerShell; directory junctions need no admin rights):

```powershell
$repo = "C:\path\to\codea-ai-playbook\claude_skills"   # your clone
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Get-ChildItem $repo -Directory | ForEach-Object {
  New-Item -ItemType Junction -Path "$HOME\.claude\skills\$($_.Name)" -Target $_.FullName
}
```

macOS or Linux:

```bash
repo=~/code/codea-ai-playbook/claude_skills   # your clone
mkdir -p ~/.claude/skills
for d in "$repo"/*/; do ln -s "${d%/}" ~/.claude/skills/"$(basename "$d")"; done
```

If an older copy of a skill is already there (for example `~/.claude/skills/brainstorming-architecture`), remove or rename it first.

### Option 2: link into one project

A link points to a folder on your own machine, so it must not be committed. The scripts below add each link to the project's `.git/info/exclude`. That file works like `.gitignore` but is never committed, so the project's own files stay unchanged.

Windows (PowerShell):

```powershell
$repo    = "C:\path\to\codea-ai-playbook\claude_skills"   # your clone
$project = "C:\path\to\other-project"                     # the project that will use the skills
New-Item -ItemType Directory -Force "$project\.claude\skills" | Out-Null
Get-ChildItem $repo -Directory | ForEach-Object {
  New-Item -ItemType Junction -Path "$project\.claude\skills\$($_.Name)" -Target $_.FullName
  Add-Content "$project\.git\info\exclude" "/.claude/skills/$($_.Name)"
}
```

macOS or Linux:

```bash
repo=~/code/codea-ai-playbook/claude_skills   # your clone
project=~/code/other-project                  # the project that will use the skills
mkdir -p "$project/.claude/skills"
for d in "$repo"/*/; do
  name=$(basename "$d")
  ln -s "${d%/}" "$project/.claude/skills/$name"
  echo "/.claude/skills/$name" >> "$project/.git/info/exclude"
done
```

To link only some skills, replace `Get-ChildItem $repo -Directory` with a list of folders, for example `Get-Item "$repo\decision-record", "$repo\implementing-plans"`. In bash, replace `"$repo"/*/` with `"$repo"/decision-record/ "$repo"/implementing-plans/`.

### Option 3: copy into the project

Use this when the whole team should get the skills from the project's repo. Copy the skill folders into the project, delete Python's `__pycache__` folders, then commit `.claude/skills/`.

Windows (PowerShell):

```powershell
$repo    = "C:\path\to\codea-ai-playbook\claude_skills"
$project = "C:\path\to\other-project"
New-Item -ItemType Directory -Force "$project\.claude\skills" | Out-Null
Get-ChildItem $repo -Directory | ForEach-Object {
  Copy-Item -Recurse -Force $_.FullName "$project\.claude\skills\"
}
Get-ChildItem "$project\.claude\skills" -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

macOS or Linux:

```bash
repo=~/code/codea-ai-playbook/claude_skills
project=~/code/other-project
mkdir -p "$project/.claude/skills"
for d in "$repo"/*/; do cp -R "${d%/}" "$project/.claude/skills/"; done
find "$project/.claude/skills" -name __pycache__ -type d -prune -exec rm -rf {} +
```

A copy doesn't update itself. To update it, delete the copied skill folders and copy them again. Make fixes to a skill here in the playbook, not in a project's copy. Otherwise the next copy overwrites the fix.

### Check that Claude Code sees the skills

1. Start a new Claude Code session in the project.
2. Type `/`. The skill names (`decision-record`, `implementing-plans`, …) should be in the list.

If a skill is missing, check that its folder sits directly inside `.claude/skills/` and contains a `SKILL.md`. A folder nested one level deeper, such as `.claude/skills/claude_skills/decision-record/`, isn't found.

### Run a skill

You can start a skill in two ways:

- **By name:** type `/` and the skill name, with any details after it.

  ```text
  /decision-record
  /implementing-plans docs/plans/03-auth.md
  /implementation-validator branch plan/03-auth against docs/plans/03-auth.md
  ```

- **In plain words:** describe the task. Claude loads the skill whose description matches it, for example "turn the requirements into a decision record" or "split decision.md into build plans".

### Prepare the project

The skills read and write fixed paths inside the project:

| Path | What goes there |
|---|---|
| `requirements/` | The client's inputs: briefs, call notes, emails, specs. You add these. |
| `.claude/decision-record-profile.md` | Optional. Rules for this client that decision-record follows. Copy it from [profile-template.md](claude_skills/decision-record/profile-template.md). |
| `requirements/decision.md` | Written by decision-record |
| `docs/plans/` | Written by splitting-decisions-into-plans and implementation-planner |
| `docs/reviews/` | Written by validating-architecture and verifying-plans |

Client details stay in the client's project. This playbook is public, so don't put client names, files or data in it.

Before the first run, install the tools in [Prerequisites](claude_skills/README.md#prerequisites): git, Python 3.8 or later, and the superpowers plugin.

### A typical run, start to finish

| Step | Example prompt |
|---|---|
| 1. Build the decision record | `/decision-record` |
| 2. Design the architecture, or audit an existing design | `/brainstorming-architecture` or `/validating-architecture docs/architecture.md` |
| 3. Split the decision record into plans | `/splitting-decisions-into-plans` |
| 4. Fact-check the plans | `/verifying-plans docs/plans/` |
| 5. Work out the build order | `/implementation-planner` |
| 6. Build one plan on its own branch | `/implementing-plans docs/plans/01-<name>.md` |
| 7. Check the branch against its plan | `/implementation-validator branch plan/01-<name> against docs/plans/01-<name>.md` |

Repeat steps 6 and 7 for each plan. Run `/skill-evaluator` after any step to grade how closely that run followed its skill.
