---
name: trace
description: Build the traceability matrix for a LedgerVision feature — every requirement and edge case ID against the plan, its tasks, the tests that name it and the latest QA result — and report drift (spec changed after the plan, tests or QA naming unknown or withdrawn IDs). Writes specs/<feature>/trace.md. Usage /sdd:trace <feature>.
argument-hint: <feature slug or prefix>
disable-model-invocation: true
---

# Trace: $ARGUMENTS

Load the `sdd:conventions` skill. The script does the work; don't re-derive the matrix by reading files.

1. Find the docs clone (writable, on `feature/<feature>`) and the feature. The code repos: every repo the plan's §2 names, at their absolute paths in the workspace.
2. Run:

   ```bash
   python3 -I "${CLAUDE_SKILL_DIR}/scripts/sddtool.py" trace <docs> <feature> <repo> <repo>…
   ```

3. Report: the summary line, then the **OPEN** lines grouped by status, then **DRIFT** lines. For each kind, the action:

   | Status / drift | Next step |
   |---|---|
   | ⛔ no task | `/sdd:tasks <feature>` |
   | 🔨 in progress, ⟳ stale | `/sdd:build <feature>` |
   | ⚠️ untested | a test named with the ID (the developer), or a QA scenario (`/sdd:qa`) |
   | ❌ QA failing | `/sdd:verify <feature>` fix round |
   | spec changed after the plan | `/sdd:plan <feature>` (change mode) |
   | tests / QA name unknown or withdrawn IDs | rename or remove the test; if the behaviour is real, it's a spec gap → `/sdd:amend` |

4. Commit `trace.md` on the docs branch (`Trace: <title>`), no VERSION entry. Don't push.

The script only sees IDs that tests and QA reports name (conventions §3). If a team's tests don't name IDs yet, everything reads ⚠️ untested — say so instead of calling the feature uncovered.
