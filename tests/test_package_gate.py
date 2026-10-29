"""Tests for plugins/sdd-web/hooks/package-gate.py.  Run: python3 -I -m unittest discover -s tests"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "..", "plugins", "website-dev", "hooks", "package-gate.py")

SHEET = """\
Next.js Project – Package Installation Request Form,,,,,,,,,,,,
How to use,,,,,,,,,,,,
"REQUEST — filled by team member",,,,,,,,,,APPROVAL,,
No.,Date Requested,Requested By,1. Package Name,2. Package Resource Link,3. Package Registry Link,4. Purpose,5. Reason for Adding,6. Usage Location,7. Proposed Version,Status,Decision Date,Approver Comments
Auto-numbered,dd/mm/yyyy,Choose your name,Exact name,Docs,npm page,What,Why,Where,Version,Approver only,Approver only,Approver only
3,26/10/2026,Keo Vuththana,dndkit,https://dndkit.com/,pnpm add @dnd-kit/react,Drag and drop,Dashboard,Dashboard,0.5.1,Approved,,
4,29/10/2026,Keo Vuththana,recharts,https://recharts.org,https://www.npmjs.com/package/recharts,Charts,Dashboard,Dashboard,2.15.0,Pending,,
5,29/10/2026,Try Limhai,zod,https://zod.dev,https://www.npmjs.com/package/zod,Validation,Forms,Forms,3.25.0,Approved,,
,,,,,,,,,,Approved,,
"""


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.web = os.path.join(self.tmp, "web-ui")
        self.api = os.path.join(self.tmp, "identity-service")
        os.makedirs(os.path.join(self.web, "src"))
        os.makedirs(self.api)
        with open(os.path.join(self.web, "package.json"), "w") as f:
            json.dump({"dependencies": {"next": "16.0.0"}}, f)
        with open(os.path.join(self.api, "package.json"), "w") as f:
            json.dump({"dependencies": {"express": "5"}}, f)
        self.sheet = os.path.join(self.tmp, "sheet.csv")
        with open(self.sheet, "w", encoding="utf-8") as f:
            f.write(SHEET)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def gate(self, command, cwd=None, sheet=True):
        env = {**os.environ}
        env["SDD_PACKAGE_SHEET_FILE"] = self.sheet if sheet else os.path.join(self.tmp, "missing.csv")
        p = subprocess.run([sys.executable, "-I", HOOK], capture_output=True, text=True, env=env,
                           input=json.dumps({"tool_name": "Bash", "cwd": cwd or self.web,
                                             "tool_input": {"command": command}}))
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout)["hookSpecificOutput"] if p.stdout.strip() else None

    def test_new_package_is_blocked_with_filing_instructions(self):
        out = self.gate("pnpm add date-fns")
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("No request yet for: date-fns", out["permissionDecisionReason"])
        self.assertIn("the team member using Claude", out["permissionDecisionReason"])

    def test_approved_by_name_or_registry_link_passes(self):
        self.assertIsNone(self.gate("pnpm add zod@3.25.0"))
        self.assertIsNone(self.gate("pnpm add @dnd-kit/react"))     # matched through the registry column

    def test_pending_request_is_blocked_without_refiling(self):
        out = self.gate("pnpm add recharts")
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("recharts (row 7: Pending)", out["permissionDecisionReason"])
        self.assertNotIn("No request yet", out["permissionDecisionReason"])

    def test_other_managers_flags_and_chains(self):
        for cmd in ("npm install --save-dev date-fns", "yarn add date-fns", "bun add date-fns",
                    "pnpm --filter web add -D date-fns", "cd src && pnpm i date-fns@^4",
                    "pnpm install zod date-fns"):
            out = self.gate(cmd)
            self.assertIsNotNone(out, cmd)
            self.assertIn("date-fns", out["permissionDecisionReason"], cmd)
            self.assertNotIn("zod", out["permissionDecisionReason"], cmd)

    def test_not_an_install(self):
        for cmd in ("pnpm install", "pnpm install --frozen-lockfile", "pnpm lint", "pnpm build",
                    "pnpm dlx shadcn@latest add button", "npm run dev", "git commit -m 'pnpm add x'",
                    "echo pnpm add x", "pnpm remove zod", "pnpm add ./local-pkg"):
            self.assertIsNone(self.gate(cmd), cmd)

    def test_only_in_web_ui(self):
        self.assertIsNone(self.gate("npm install date-fns", cwd=self.api))
        self.assertIsNone(self.gate("npm install date-fns", cwd=self.tmp))
        self.assertIsNotNone(self.gate(f"cd {self.web} && pnpm add date-fns", cwd=self.tmp))

    def test_sheet_unreachable_asks(self):
        out = self.gate("pnpm add date-fns", sheet=False)
        self.assertEqual(out["permissionDecision"], "ask")


if __name__ == "__main__":
    unittest.main()
