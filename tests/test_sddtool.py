"""Tests for plugins/sdd/skills/trace/scripts/sddtool.py.  Run: python3 -I -m unittest discover -s tests"""
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "plugins", "sdd", "skills", "trace", "scripts", "sddtool.py")

SPEC = """\
# Spec: Branch Management

**Prefix:** `BRN` · **Status:** {status} · **Version:** v5.2.0 · **Author:** test

## 3. Decisions

| ID | Topic | Decision |
|---|---|---|
| **BRN-D01** | Names | Unique per business |

## 5. Requirements

- **BRN-R01** · Owner · §4a — An owner can create a branch.
- **BRN-R02** · Owner · §4a — A taken name is rejected with BRN-M01.
- ~~**BRN-R03**~~ withdrawn in v5.2.0 — merged into BRN-R02.

## 6. Messages

| ID | HTTP · code | Text | Used by |
|---|---|---|---|
| **BRN-M01** | `409 · BRANCH_NAME_TAKEN` | "Taken" | BRN-R02 |

## 7. Edge cases

- **BRN-E01** · Permissions — A manager can't create a branch → 403.

## 10. Questions

{questions}
"""

TASKS = """\
# Tasks: Branch Management

- [x] **T01** `identity-service` — migration · covers BRN-R01 · done when: applies · files: `V1.sql`
- [ ] **T02** `identity-service` — endpoint · covers BRN-R02, BRN-E01 · after T01 · done when: tests
{extra}
"""


def run(*args):
    p = subprocess.run([sys.executable, "-I", TOOL, *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def git(cwd, *args):
    subprocess.run(["git", "-C", cwd, *args], check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.docs = os.path.join(self.tmp, "docs")
        self.fdir = os.path.join(self.docs, "specs", "branch-management")
        os.makedirs(self.fdir)
        self.repo = os.path.join(self.tmp, "identity-service")
        os.makedirs(os.path.join(self.repo, "src", "test", "java"))
        os.makedirs(os.path.join(self.repo, "qa-reports"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, rel, text, root=None):
        path = os.path.join(root or self.fdir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(text))

    def spec(self, status="✅ Approved", questions="- **BRN-Q01** · §2 — Limit? → BRN-D01 (answered)"):
        self.write("spec.md", SPEC.format(status=status, questions=questions))


class CheckTests(Fixture):
    def test_clean(self):
        self.spec()
        self.write("tasks.md", TASKS.format(extra=""))
        code, out = run("check", self.docs, "branch-management")
        self.assertEqual(code, 0, out)
        self.assertIn("2 requirements, 1 edge cases, 0 open questions, 2 tasks", out)

    def test_open_question_on_approved_spec(self):
        self.spec(questions="- **BRN-Q01** · §2 — Limit? *Options:* (a) 10; (b) none.")
        code, out = run("check", self.docs, "branch-management")
        self.assertEqual(code, 1)
        self.assertIn("approved but questions still open: BRN-Q01", out)

    def test_draft_open_question_is_only_a_warning(self):
        self.spec(status="📝 Draft", questions="- **BRN-Q01** · §2 — Limit?")
        code, out = run("check", self.docs, "branch-management")
        self.assertEqual(code, 0, out)
        self.assertIn("WARN  open questions: BRN-Q01", out)

    def test_requirement_without_task(self):
        self.spec()
        self.write("tasks.md", TASKS.format(extra="").replace(", BRN-E01", ""))
        code, out = run("check", self.docs, "branch-management")
        self.assertEqual(code, 1)
        self.assertIn("BRN-E01 has no task", out)

    def test_task_covers_withdrawn_unknown_and_missing_dep(self):
        self.spec()
        extra = ("- [ ] **T03** `web-ui` — old · covers BRN-R03 · after T09\n"
                 "- [ ] **T04** `web-ui` — ghost · covers BRN-R99\n"
                 "- [ ] **T05** `web-ui` — scaffolding\n")
        self.write("tasks.md", TASKS.format(extra=extra))
        code, out = run("check", self.docs, "branch-management")
        self.assertEqual(code, 1)
        self.assertIn("T03 covers withdrawn BRN-R03", out)
        self.assertIn("T03 is after unknown T09", out)
        self.assertIn("T04 covers unknown BRN-R99", out)
        self.assertIn("T05 covers no requirement", out)

    def test_duplicate_and_undefined_reference(self):
        self.spec()
        with open(os.path.join(self.fdir, "spec.md"), "a", encoding="utf-8") as f:
            f.write("- **BRN-R01** · Owner — again\n\nSee BRN-R42.\n")
        code, out = run("check", self.docs, "branch-management")
        self.assertEqual(code, 1)
        self.assertIn("BRN-R01 defined twice", out)
        self.assertIn("BRN-R42 is referenced but never defined", out)

    def test_spec_drift_after_plan(self):
        self.spec()
        git(self.docs, "init", "-q")
        git(self.docs, "add", ".")
        git(self.docs, "commit", "-qm", "approve")
        sha = subprocess.run(["git", "-C", self.docs, "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True).stdout.strip()
        self.write("plan.md", f"# Plan\n\n**Spec:** `BRN` v5.2.0, commit `{sha}` · **Approved:** today\n")
        self.write("tasks.md", TASKS.format(extra=""))
        _, out = run("check", self.docs, "branch-management")
        self.assertNotIn("changed since", out)
        with open(os.path.join(self.fdir, "spec.md"), "a", encoding="utf-8") as f:
            f.write("\n- **BRN-R04** · Owner — new rule\n")
        git(self.docs, "commit", "-qam", "sneaky change")
        _, out = run("check", self.docs, "branch-management")
        self.assertIn("spec.md changed since the plan was approved", out)
        self.assertIn("sneaky change", out)
        self.assertIn("BRN-R04 has no task", out)


class TraceTests(Fixture):
    def test_matrix_and_drift(self):
        self.spec()
        self.write("tasks.md", TASKS.format(extra="").replace("- [ ] **T02**", "- [x] **T02**"))
        self.write("src/test/java/BranchTest.java", """\
            @DisplayName("BRN-R01 creates a branch")
            void a() {}
            @DisplayName("BRN-R03 old behaviour")
            void b() {}
            @DisplayName("BRN-R77 invented")
            void c() {}
            """, root=self.repo)
        self.write("src/main/java/Branch.java", 'String s = "BRN-E01";\n', root=self.repo)
        self.write("qa-reports/2026-11-01-branch-management.md", """\
            | Id | Kind | Scenario | Expected (§) | Result | Note |
            |---|---|---|---|---|---|
            | BRN-R02-V1 | V | taken name | §4a | ❌ | got 500 |
            | BRN-E01-M1 | M | manager | §2 | ✅ | |
            """, root=self.repo)
        code, out = run("trace", self.docs, "branch-management", self.repo)
        self.assertEqual(code, 1, out)
        with open(os.path.join(self.fdir, "trace.md"), encoding="utf-8") as f:
            trace = f.read()
        self.assertIn("do not edit by hand", trace)
        row = {l.split("|")[1].strip(): l for l in trace.splitlines() if l.startswith("| BRN-")}
        self.assertIn("✅ covered", row["BRN-R01"])
        self.assertIn("BranchTest.java:1", row["BRN-R01"])
        self.assertIn("❌ QA failing", row["BRN-R02"])
        self.assertIn("✅ covered", row["BRN-E01"])           # QA pass, no test
        self.assertNotIn("Branch.java", row["BRN-E01"])       # production code isn't a test
        self.assertNotIn("BRN-R03", row)                      # withdrawn: not in the matrix
        self.assertIn("still name withdrawn BRN-R03", trace)
        self.assertIn("BRN-R77, which the spec doesn't define", trace)

    def test_latest_qa_report_wins(self):
        self.spec()
        self.write("tasks.md", TASKS.format(extra="").replace("[ ]", "[x]"))
        row = "| BRN-R01-C1 | C | create | §4a | {} | |\n"
        self.write("qa-reports/2026-11-01-branch-management.md", row.format("❌"), root=self.repo)
        self.write("qa-reports/2026-11-01-branch-management-2.md", row.format("✅"), root=self.repo)
        self.write("qa-reports/2026-11-02-branch-management-managers.md", row.format("❌"), root=self.repo)
        run("trace", self.docs, "branch-management", self.repo)
        with open(os.path.join(self.fdir, "trace.md"), encoding="utf-8") as f:
            trace = f.read()
        self.assertIn("2026-11-01-branch-management-2.md", trace)
        self.assertNotIn("QA failing", trace)

    def test_untested_and_no_task(self):
        self.spec()
        self.write("tasks.md", "- [x] **T01** `x` — all · covers BRN-R01, BRN-R02\n")
        code, out = run("trace", self.docs, "branch-management", self.repo, "--no-write")
        self.assertEqual(code, 1)
        self.assertFalse(os.path.exists(os.path.join(self.fdir, "trace.md")))
        self.assertIn("OPEN  BRN-R01 ⚠️ untested", out)
        self.assertIn("OPEN  BRN-E01 ⛔ no task", out)

    def test_pytest_style_names(self):
        self.spec()
        self.write("tasks.md", TASKS.format(extra="").replace("[ ]", "[x]"))
        self.write("tests/test_branches.py", "def test_brn_r01_creates(): pass\n"
                   "def test_brn_r02_taken(): pass\ndef test_brn_e01_manager(): pass\n", root=self.repo)
        code, out = run("trace", self.docs, "branch-management", self.repo)
        self.assertEqual(code, 0, out)
        self.assertIn("✅ covered 3", out)


class StatusTests(Fixture):
    def test_status_table(self):
        self.spec(status="📝 Draft", questions="- **BRN-Q01** · §2 — Limit?")
        self.write("tasks.md", TASKS.format(extra=""))
        os.makedirs(os.path.join(self.docs, "specs", "_templates"))
        code, out = run("status", self.docs)
        self.assertEqual(code, 0, out)
        self.assertIn("| branch-management | BRN | 📝 | 1 | — | 1/2 | — |", out)
        self.assertNotIn("_templates", out)


if __name__ == "__main__":
    unittest.main()
