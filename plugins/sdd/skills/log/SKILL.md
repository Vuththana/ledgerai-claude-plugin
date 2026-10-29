---
name: log
description: Show the SDD audit log — where you are now (project, branch, repos, the last SDD step per feature, spec status) and every prompt you typed, across all projects, with search. The log is written automatically by the sdd plugin's hooks to ~/.claude/sdd-audit/. Usage /sdd:log [today | week | <feature> | search <text> | actions].
argument-hint: "[today | week | <feature> | search <text> | actions]"
disable-model-invocation: true
---

# Log: $ARGUMENTS

The `sdd` plugin's hooks write every prompt you type (secrets masked) and every action Claude takes (tool and target, never file contents) to `~/.claude/sdd-audit/audit-YYYY-MM.jsonl`. This command only reads it. Run the script and show its output as it is; don't re-read the log files yourself.

The script: `python3 -I "${CLAUDE_SKILL_DIR}/../../hooks/audit.py" <command>`

| $ARGUMENTS | Command |
|---|---|
| empty | `where` |
| `today` | `show --days 1` |
| `week` | `show --days 7` |
| `actions` | `show --days 1 --tools` (prompts and the actions after each) |
| `search <text>` | `show --days 90 --grep "<text>"` |
| a feature slug (`branch-management`) | `show --days 90 --feature <slug>` |

After the output, add one line only: the most useful next step, from the "Your SDD work" table when there is one (e.g. "You were last on `/sdd:plan branch-management`; next is `/sdd:tasks branch-management`"). Use the next-step order in `sdd:conventions` (specify → clarify → plan → tasks → build → verify → qa → trace → ship).

The log holds what you typed, in plain text, on this computer only. It's never committed or sent anywhere. To start over, delete `~/.claude/sdd-audit/`.
