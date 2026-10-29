---
name: ship
description: Finish a LedgerVision feature — check every repo for hardcoded secrets, commit the docs branch (API reference entries, tasks, trace), summarise what's done and still open, and on the user's approval commit and push each repo and the docs branch. Usage /sdd:ship <feature>.
argument-hint: <feature>
disable-model-invocation: true
---

# Ship: $ARGUMENTS

Load the `sdd:conventions` skill first. Nothing is committed in a code repo or pushed anywhere without the user's explicit approval at the gate.

## 1. Checks

1. Run `python3 -I "${CLAUDE_SKILL_DIR}/../trace/scripts/sddtool.py" trace <docs> <feature> <repos…>`. Any ⛔ no task, ❌ QA failing or DRIFT: show them and ask whether to ship anyway — don't decide for the user.
2. In each repo, follow the `sdd:check-secrets` skill on the working tree and the commits on `feature/<feature>`. Show what it finds; fixes go to that repo's developer.

## 2. Docs branch

In the docs clone on `feature/<feature>`:

- API reference entries the developers wrote: add them to a `VERSION.md` entry with their **Impact** (new endpoints → MINOR), and commit (`API: <feature> endpoints (v<X.Y.Z>)`).
- `specs/README.md`: stage `shipped` once the user approves below; `tasks.md` and `trace.md` already committed by build / verify / qa.

## 3. Summary

Per repo: branch, files changed, checks with results (build, lint, tests), review verdicts, QA counts and report path. Then the trace summary, and what's still open: API entries not written, Minor findings, spec gaps, dictionary gaps, findings left after two rounds. Then the docs branch: its commits.

## 4. ⏸ Gate 2

Ask the user, per repo and for the docs branch, whether to **commit and push**. Do only what they approve:

- Code repos: commit on `feature/<feature>` with a message naming the feature and the task IDs (`Branch management: T01–T09 (BRN)`), then `git push -u origin feature/<feature>`.
- Docs branch: `git push -u origin feature/<feature>` (and `spec/<feature>` if it isn't merged yet).

Opening pull requests is a separate question. The docs PR merges no later than the code.
