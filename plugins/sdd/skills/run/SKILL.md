---
name: run
description: Run the whole LedgerVision SDD lifecycle for one approved feature with agents — plan (you approve) → tasks → build in parallel per repo → verify → QA → trace → ship (you approve the push). Replaces v1's /ledgerai:dev-team. Usage /sdd:run <feature>.
argument-hint: <feature>
disable-model-invocation: true
---

# Run: $ARGUMENTS

Load the `sdd:conventions` skill first. You are the **lead** for the whole feature. You step in for the user at two gates: the plan, and the push.

Each stage is defined once, in its own skill. For each one below, **read that skill's file and follow its steps** with feature = **$ARGUMENTS**, skipping its "Reply" section (you report at the end) and its "load conventions" line (already loaded):

| # | Stage | File | Skip when |
|---|---|---|---|
| 1 | Plan — ⏸ Gate 1 | `${CLAUDE_SKILL_DIR}/../plan/SKILL.md` | `plan.md` exists and `sddtool.py check` shows no spec drift |
| 2 | Tasks | `${CLAUDE_SKILL_DIR}/../tasks/SKILL.md` | `tasks.md` exists and `check` is clean |
| 3 | Build | `${CLAUDE_SKILL_DIR}/../build/SKILL.md` | no open tasks |
| 4 | Verify | `${CLAUDE_SKILL_DIR}/../verify/SKILL.md` | |
| 5 | QA | `${CLAUDE_SKILL_DIR}/../qa/SKILL.md` | |
| 6 | Ship — ⏸ Gate 2 | `${CLAUDE_SKILL_DIR}/../ship/SKILL.md` | |

Those files aren't loaded as skills, so their skill-folder placeholder isn't filled in. Wherever one of them runs `sddtool.py`, use this path: `${CLAUDE_SKILL_DIR}/../trace/scripts/sddtool.py`.

Stop and hand back to the user when:

- the spec is 📝 (→ `/sdd:clarify`) or ⟳ (→ finish `/sdd:amend`);
- Gate 1 isn't approved;
- a spec gap blocks a task the rest depends on (→ `/sdd:amend`, then `/sdd:run` again — done stages are skipped);
- a developer or tester fails twice.

**Keep agents alive across stages:** the planner from stage 1 writes the tasks in stage 2; the developers from stage 3 take the fixes in stages 4 and 5 (SendMessage), so they keep their context. Fix rounds are at most two across verify and QA together.

Keep the user posted in one line per step. At the end, reply with `/sdd:ship`'s summary and the trace summary line.
