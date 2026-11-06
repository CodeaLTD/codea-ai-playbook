import tempfile
import unittest
from pathlib import Path

from helpers import CHECK_PLANS, index, plan, run, write

SOURCE = """
# Decision record

### 3.1 Agent framework [PROPOSED]
- **Choice:** retries at most 3 times, timeout 300 ms.

### 3.2 Safety checks [DECIDED]
- **Choice:** block 1,000 rows or more.

| ID | Requirement | Target | Status tag | Source |
|---|---|---|---|---|
| NFR1 | Answer time | 10 seconds | [DECIDED] | Brief |
"""

FEATURE_SIGNALS = """
## Signals
- **Observability:** log the cart ID
- **Evaluation:** None, because nothing is judged
- **Monitoring:** alert on errors
"""


class CheckPlansTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.plans = self.root / "docs" / "plans"
        write(self.root / "requirements" / "decision.md", SOURCE)

    def tearDown(self):
        self.tmp.cleanup()

    def check(self):
        return run(CHECK_PLANS, "docs/plans", "--source", "requirements/decision.md", cwd=self.root)

    def good(self):
        rows = [("01", "Setup", "–", "Ready"), ("02", "Cart", "01", "Ready")]
        coverage = "| 3.1 Agent framework | 01 |\n| 3.2 Safety checks | 02 |\n| NFR1 Answer time | Release checklist |"
        not_planned = "\n## Not planned\n| Item | Add it when | Source |\n|---|---|---|\n| Reranker | More than 1,000 rows | 3.2 |\n"
        write(self.plans / "00-index.md", index(rows, coverage, not_planned))
        write(self.plans / "01-setup.md", plan("01", "Setup") + "\nRetry at most 3 times with a 300 ms timeout.\n")
        write(self.plans / "02-cart.md", plan("02", "Cart", "01", group="Feature") + FEATURE_SIGNALS)

    def test_good_plans_pass(self):
        self.good()
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_problems_are_reported(self):
        self.good()
        acs = (
            "- [ ] **AC-03.1** Given a cart, when paid, then it is saved.\n"
            "  - Check: `npm test pay`\n"
            "- [ ] **AC-01.2** Given a cart, when paid twice, then one charge is made.\n"
        )
        write(self.plans / "03-pay.md", plan("03", "Pay", "04", group="Feature", acs=acs) + "\nCharge within 45 seconds.\n")
        coverage = "| 3.1 Agent framework | 01 |\n| 3.1 Agent framework | 02 |\n| Old thing | 09 |"
        not_planned = "\n## Not planned\n| Item | Add it when | Source |\n|---|---|---|\n| Reranker |  | 3.2 |\n"
        rows = [("01", "Setup", "–", "Ready"), ("02", "Cart", "01", "Ready")]
        write(self.plans / "00-index.md", index(rows, coverage, not_planned))
        out = self.check().stdout
        for expected in [
            "03-pay.md:3: depends on plan 04, which has no file",
            "AC-03.1 has no Source on its Check line",
            "AC-01.2 does not carry the plan number 03",
            "AC-01.2 has no Check line",
            "2 acceptance criteria (3-8 per plan)",
            "feature plan has no **Observability:** line under Signals",
            "number 45 is not in the source",
            "plan 03 (03-pay.md) is not in the Plans table",
            '"3.1 Agent framework" is in Coverage twice',
            '"Old thing" lands in plan 09, which has no file',
            "has no trigger",
            "source item 3.2 (decision.md:6) is not in the Coverage table",
            "source item NFR1 (decision.md:11) is not in the Coverage table",
        ]:
            self.assertIn(expected, out)
        self.assertNotIn("number 300", out)
        self.assertNotIn("number 3 ", out)


if __name__ == "__main__":
    unittest.main()
