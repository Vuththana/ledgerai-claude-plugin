"""Tests for plugins/sdd/hooks/audit.py.  Run: python3 -I -m unittest discover -s tests"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIT = os.path.join(HERE, "..", "plugins", "sdd", "hooks", "audit.py")


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.logs = os.path.join(self.tmp, "logs")
        self.repo = os.path.join(self.tmp, "web-ui")
        os.makedirs(self.repo)
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        subprocess.run(["git", "init", "-q", "-b", "feature/branch-management", self.repo], check=True, env=env)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_audit(self, *args, stdin=None, cwd=None):
        env = {**os.environ, "SDD_AUDIT_DIR": self.logs}
        p = subprocess.run([sys.executable, "-I", AUDIT, *args], input=stdin, capture_output=True,
                           text=True, env=env, cwd=cwd or self.tmp)
        return p.returncode, p.stdout, p.stderr

    def entries(self):
        out = []
        for f in glob.glob(os.path.join(self.logs, "*.jsonl")):
            with open(f, encoding="utf-8") as fh:
                out += [json.loads(l) for l in fh]
        return out

    def prompt(self, text, cwd=None):
        return self.run_audit("hook-prompt", stdin=json.dumps(
            {"session_id": "abcdef123456", "cwd": cwd or self.repo, "prompt": text}))

    def test_prompt_logged_with_project_branch_and_sdd_step(self):
        code, out, _ = self.prompt("/sdd:plan branch-management please")
        self.assertEqual((code, out), (0, ""))
        [e] = self.entries()
        self.assertEqual(e["event"], "prompt")
        self.assertEqual(e["project"], "web-ui")
        self.assertEqual(e["branch"], "feature/branch-management")
        self.assertEqual(e["command"], "/sdd:plan")
        self.assertEqual(e["feature"], "branch-management")
        self.assertEqual(e["session"], "abcdef12")

    def test_secrets_are_masked(self):
        self.prompt("use password=hunter2 and key sk-abcdefghijklmnopqrstuvwxyz123 and AKIAABCDEFGHIJKLMNOP")
        text = self.entries()[0]["prompt"]
        self.assertNotIn("hunter2", text)
        self.assertNotIn("sk-abcdefghij", text)
        self.assertNotIn("AKIAABCDEFGHIJKLMNOP", text)
        self.assertIn("password=[masked]", text)

    def test_plain_prompt_has_no_step(self):
        self.prompt("what does this function do?")
        e = self.entries()[0]
        self.assertNotIn("command", e)
        self.assertNotIn("feature", e)

    def test_tool_logs_target_never_contents(self):
        self.run_audit("hook-tool", stdin=json.dumps({"tool_name": "Write", "cwd": self.repo,
            "tool_input": {"file_path": "/x/a.ts", "content": "SECRET BODY"}, "tool_response": {"ok": 1}}))
        self.run_audit("hook-tool", stdin=json.dumps({"tool_name": "Bash", "tool_input": {"command": "pnpm build"}}))
        a, b = self.entries()
        self.assertEqual((a["tool"], a["target"]), ("Write", "/x/a.ts"))
        self.assertNotIn("SECRET BODY", json.dumps(a))
        self.assertEqual(b["target"], "pnpm build")

    def test_bad_input_never_fails(self):
        for hook in ("hook-prompt", "hook-tool", "hook-start"):
            code, out, err = self.run_audit(hook, stdin="not json")
            self.assertEqual(code, 0, (hook, err))

    def test_session_start_says_where_you_were(self):
        code, out, _ = self.run_audit("hook-start", stdin=json.dumps({"cwd": self.repo, "source": "startup"}))
        self.assertEqual(out, "")                      # nothing logged yet: no message
        self.prompt("/sdd:tasks branch-management")
        self.prompt("thanks")
        code, out, _ = self.run_audit("hook-start", stdin=json.dumps({"cwd": self.repo, "source": "startup"}))
        msg = json.loads(out)["systemMessage"]
        self.assertIn("web-ui (feature/branch-management)", msg)
        self.assertIn("/sdd:tasks branch-management", msg)

    def test_where_and_show(self):
        self.prompt("/sdd:migrate branch-management")
        self.prompt("/sdd:clarify banking-statement")
        self.prompt("fix the | pipe in this table")
        self.run_audit("hook-tool", stdin=json.dumps({"tool_name": "Edit", "tool_input": {"file_path": "/y/b.md"}}))
        code, out, _ = self.run_audit("where", cwd=self.tmp)
        self.assertEqual(code, 0)
        self.assertIn("`web-ui` on `feature/branch-management`", out)
        self.assertIn("| banking-statement | `/sdd:clarify` |", out)
        self.assertIn("| branch-management | `/sdd:migrate` |", out)
        code, out, _ = self.run_audit("show", "--days", "1", "--feature", "banking-statement")
        self.assertIn("/sdd:clarify banking-statement", out)
        self.assertNotIn("migrate", out)
        code, out, _ = self.run_audit("show", "--grep", "pipe")
        self.assertIn("fix the \\| pipe", out)
        code, out, _ = self.run_audit("show", "--tools")
        self.assertIn("↳ Edit /y/b.md", out)


if __name__ == "__main__":
    unittest.main()
