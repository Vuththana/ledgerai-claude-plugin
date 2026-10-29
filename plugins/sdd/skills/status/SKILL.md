---
name: status
description: Show where every LedgerVision feature is in the SDD lifecycle — spec status, open questions, plan (and whether the spec changed since), task progress, trace coverage — plus v1 flows not migrated yet. Usage /sdd:status.
disable-model-invocation: true
---

# SDD status

Load the `sdd:conventions` skill. Find the docs root (conventions §1; read-only is fine).

1. Run `python3 -I "${CLAUDE_SKILL_DIR}/../trace/scripts/sddtool.py" status <docs-root>` and show its table as it is.
2. Below it, the v1 flows in `flow/README.md` with no `specs/<feature>/` folder: name and status, as "not migrated".
3. One line of **next steps**, most useful first: a ✅ spec with no plan → `/sdd:plan`; a plan with "⚠️ spec changed" → `/sdd:plan` (change mode); tasks open → `/sdd:build`; trace older than the latest task tick or not run → `/sdd:trace`; a 📝 spec with open questions → `/sdd:clarify`.

Read-only. Don't run anything else.
