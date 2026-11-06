import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import FILES_CHANGED, run, write


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class FilesChangedTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "app"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "Test")
        git(self.repo, "config", "core.autocrlf", "false")
        write(self.repo / "src" / "app.py", "".join(f"line {i}\n" for i in range(1, 21)))
        write(self.repo / "old_name.py", "a\nb\nc\nd\ne\nf\ng\nh\n")
        write(self.repo / "gone.txt", "bye\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "base")
        self.base = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip()

    def tearDown(self):
        self.tmp.cleanup()

    def table(self, *args):
        result = run(FILES_CHANGED, "--base", self.base, *args, cwd=self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_nothing_changed(self):
        self.assertEqual(self.table().strip(), "No files changed.")

    def test_every_kind_of_change(self):
        git(self.repo, "switch", "-q", "-c", "plan/01-setup")
        lines = (self.repo / "src" / "app.py").read_text().splitlines(keepends=True)
        lines[4] = "changed 5\n"  # line 5 modified
        del lines[9:11]  # old lines 10-11 removed
        (self.repo / "src" / "app.py").write_text("".join(lines), newline="\n")
        git(self.repo, "mv", "old_name.py", "new_name.py")
        git(self.repo, "rm", "-q", "gone.txt")
        write(self.repo / "committed_new.py", "x\ny\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "work")
        write(self.repo / "tests" / "test_app.py", "one\ntwo\nthree")  # untracked, no final newline
        out = self.table()
        self.assertIn("| `src/app.py` | modified | 5, removed (old lines 10-11) |  |", out)
        self.assertIn("| `new_name.py` | renamed from `old_name.py` | content unchanged |  |", out)
        self.assertIn("| `gone.txt` | deleted | all removed |  |", out)
        self.assertIn("| `committed_new.py` | new | all (2 lines) |  |", out)
        self.assertIn("| `tests/test_app.py` | new (untracked) | all (3 lines) |  |", out)

    def test_second_repo_gets_its_own_heading(self):
        other = Path(self.tmp.name) / "infra"
        other.mkdir()
        git(other, "init", "-q", "-b", "main")
        git(other, "config", "user.email", "test@example.com")
        git(other, "config", "user.name", "Test")
        write(other / "main.tf", "a\n")
        git(other, "add", ".")
        git(other, "commit", "-q", "-m", "base")
        write(other / "main.tf", "a\nb\n")
        out = self.table(str(other))
        self.assertIn("**Repo: app**", out)
        self.assertIn("**Repo: infra**", out)
        self.assertIn("| `main.tf` | modified | 2 |  |", out)


if __name__ == "__main__":
    unittest.main()
