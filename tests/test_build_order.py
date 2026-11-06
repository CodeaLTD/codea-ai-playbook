import tempfile
import unittest
from pathlib import Path

from helpers import BUILD_ORDER, index, plan, run, write


class BuildOrderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.plans = self.root / "docs" / "plans"

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, rows, bodies=None):
        write(self.plans / "00-index.md", index(rows))
        for pid, name, deps, status in rows:
            body = (bodies or {}).get(pid) or plan(pid, name, deps, status)
            write(self.plans / f"{pid}-{name.lower()}.md", body)

    def build(self, *args):
        return run(BUILD_ORDER, "docs/plans", *args, cwd=self.root)

    def test_ticked_manual_check_does_not_mark_open_criterion_manual(self):
        acs = (
            "- [ ] **AC-01.1** Given a repo, when CI runs, then it passes.\n"
            "  - Check: `npm test` · Source: 3.1 [DECIDED]\n"
            "- [x] **AC-01.2** Given staff, when they log in, then they see the dashboard.\n"
            "  - Check: log in with a real account (manual) · Source: 3.2 [DECIDED]\n"
            "- [ ] **AC-01.3** Given a host, when deployed, then health is green.\n"
            "  - Check: open /health on the deployed host (manual) · Source: 3.3 [DECIDED]\n"
        )
        rows = [("01", "Setup", "–", "Done (manual pending)"), ("02", "Cart", "01", "Ready")]
        self.make(rows, {"01": plan("01", "Setup", "–", "Done (manual pending)", acs=acs)})
        out = self.build().stdout
        self.assertIn("**AC-01.1** (Setup): Given a repo, when CI runs, then it passes. · Check has no (manual) part", out)
        self.assertRegex(out, r"\*\*AC-01\.3\*\* \(Setup\): Given a host, when deployed, then health is green\.\n")
        self.assertNotIn("AC-01.2", out.split("## Open manual checks")[1].split("## Plans")[0])

    def test_waves_ranges_and_lettered_plans(self):
        rows = [
            ("01", "Setup", "–", "Ready"),
            ("02", "Api", "01", "Ready"),
            ("03", "Ui", "01", "Ready"),
            ("03a", "Search", "03", "Ready"),
            ("04", "Signals", "02–03a", "Ready"),
        ]
        self.make(rows)
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("01 → 03 → 03a → 04", result.stdout)
        self.assertIn("- Wave 2: same wave: 02 + 03", result.stdout)

    def test_cycle_exits_2_and_writes_nothing(self):
        self.make([("01", "Setup", "02", "Ready"), ("02", "Api", "01", "Ready")])
        out = self.plans / "implementation-plan.md"
        result = self.build("--out", str(out))
        self.assertEqual(result.returncode, 2)
        self.assertIn("Dependency cycle", result.stderr)
        self.assertFalse(out.exists())

    def test_set_keeps_the_implied_plan(self):
        rows = [("01", "Setup", "–", "Ready"), ("02", "Api", "01", "Ready"), ("03", "Ui", "02", "Ready")]
        self.make(rows)
        result = self.build("--implied", "01", "--set", "03=")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Wave 1: 01\n", result.stdout)
        self.assertIn("Wave 2: 02, 03", result.stdout)

    def test_verify_flags_fill_left_and_changed_lines(self):
        self.make([("01", "Setup", "–", "Ready"), ("02", "Api", "01", "Ready")])
        out = self.plans / "implementation-plan.md"
        self.assertEqual(self.build("--out", str(out)).returncode, 0)
        self.assertEqual(self.build("--verify", str(out)).returncode, 1)
        filled = "\n".join(l for l in out.read_text(encoding="utf-8").splitlines() if "FILL:" not in l)
        out.write_text(filled, encoding="utf-8")
        ok = self.build("--verify", str(out))
        self.assertEqual(ok.returncode, 0, ok.stdout)
        collapsed = filled.replace("\n\n\n", "\n\n")  # a formatter merged the blank lines
        out.write_text(collapsed, encoding="utf-8")
        self.assertEqual(self.build("--verify", str(out)).returncode, 0)
        out.write_text(filled.replace("## Critical path", "## Critical route"), encoding="utf-8")
        self.assertEqual(self.build("--verify", str(out)).returncode, 1)

    def test_wave_instructions_name_the_branch_and_the_owner(self):
        self.make([("01", "Setup", "–", "Ready")])
        out = self.build().stdout
        self.assertIn("run implementing-plans with the plan named", out)
        self.assertIn("builders never write Status", out)


if __name__ == "__main__":
    unittest.main()
