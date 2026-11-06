import tempfile
import unittest
from pathlib import Path

from helpers import CHECK_DECISION, run, write

GOOD = """
# Decision record

Status: draft built from requirements/ on 2026-11-06

## Glossary

| Term | Meaning |
|---|---|
| API | A way for programs to talk to each other |
| CLI | A program you use by typing commands |

## 3. Key decisions

### 3.1 Web framework [PROPOSED]
- **Choice:** We use Django for the web app.
- **Why:** It comes with login and an admin screen.
- **Source:** (decisions 3.1)

## 4. Non-functional requirements

| ID | Requirement | Target | Status tag | Source |
|---|---|---|---|---|
| NFR1 | Page load time | 2 seconds | [DECIDED] | Brief |

## 5. Assumptions

| ID | Assumption | Source | What happens if it is wrong | Linked question |
|---|---|---|---|---|
| A1 | Users work in the CLI | Not stated | We need a web screen | Q1 |

```text
[ Web app ] ──> [ API ] this diagram is copied verbatim and is not checked at all, e.g. here
```
"""


class CheckDecisionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, text):
        write(self.root / "decision.md", text)
        return run(CHECK_DECISION, "decision.md", cwd=self.root)

    def test_good_file_passes(self):
        result = self.check(GOOD)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("0 problem(s)", result.stdout)

    def test_each_rule_is_reported(self):
        bad = GOOD + """
## 6. Bad

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| one | two | three | four | five | six |

| NFR | Cell |
|---|---|
| NFR2 | One sentence here. Another sentence here. |

| ID | Assumption | Source | What happens if it is wrong | Linked question |
|---|---|---|---|---|
| A2 | Something | Not stated | Bad things | |

### 3.2 Tone without a tag
- We leverage the SLA to ensure uptime, e.g. at night.
- This sentence is far too long because it keeps going and going with many extra words for no reason at all here.
  - Level two is fine.
    - Level three is too deep.
- The query is blocked by the guard.
- Login works ✓ and `CODE_NAME` stays in code.

This paragraph has one line.
And a second line.
And a third line, which is one too many.
"""
        out = self.check(bad).stdout
        for expected in [
            "table has 6 columns (max 5)",
            "table cell has 2 sentences",
            "NFR2 has no status tag",
            'A2: last column must be a Q number or "None"',
            "decision heading has no status tag",
            'plain-English word: "leverage"',
            'plain-English word: "ensure"',
            '"e.g.": write "for example"',
            "abbreviation SLA is not in the Glossary",
            "sentence over 20 words",
            "bullet nested 3 levels deep",
            "paragraph over 2 lines",
            'possible passive (check by hand): "is blocked"',
            'emoji or symbol "✓"',
        ]:
            self.assertIn(expected, out)
        self.assertNotIn("abbreviation CLI", out)
        self.assertNotIn("abbreviation CODE", out)  # inline code is never an abbreviation
        self.assertNotIn("decision.md:39:", out.split("Summary")[0])  # the code fence line

    def test_missing_glossary_and_too_many_lines(self):
        text = "# Decision record\n" + "- A short line.\n" * 560
        out = self.check(text).stdout
        self.assertIn("no Glossary section found", out)
        self.assertIn("561 lines (hard maximum 550)", out)


if __name__ == "__main__":
    unittest.main()
