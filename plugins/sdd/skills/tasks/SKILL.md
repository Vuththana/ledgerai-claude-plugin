---
name: tasks
description: Break an approved LedgerVision plan into specs/<feature>/tasks.md — ordered, per-repo, checkable tasks with dependencies and parallel markers, each covering requirement IDs — and prove every requirement and edge case has a task. Also adds tasks for amended specs. Usage /sdd:tasks <feature>.
argument-hint: <feature slug or prefix>
disable-model-invocation: true
---

# Tasks: $ARGUMENTS

Load the `sdd:conventions` skill first and follow it.

1. Find a **writable** docs clone and the feature. It needs a ✅ spec and a `plan.md` whose **Spec:** commit is current — if `sddtool.py check` warns "spec.md changed since the plan was approved", stop and suggest `/sdd:plan <feature>` first. Use the `feature/<feature>` branch.
2. Start `sdd:planner`:

   > Mode `tasks`, feature **<feature>**. Docs root: **<abs>**. Repos: **<abs path — role>** for each. <If tasks.md exists: "Update the existing tasks.md: stale tasks are marked ⟳.">

   When you started the planner in this session for `/sdd:plan`, continue that one with SendMessage instead: it already has the context.
3. Write its content to `specs/<feature>/tasks.md` and run `python3 -I "${CLAUDE_SKILL_DIR}/../trace/scripts/sddtool.py" check <docs> <feature>`. Any ERROR → send the lines word for word to the same planner and write its corrected version. At most two rounds; then show the user what's left.
4. Show the user the task list grouped by phase, with counts per repo and which run in parallel. It's derived from the approved plan, so it needs no separate approval — but take any changes they ask for (through the planner).
5. `specs/README.md`: stage `build`. Commit `Tasks: <title>` (no VERSION entry: tasks are working state). Don't push.

Reply: the path, task count per repo, the first tasks that can start now, and the next step: `/sdd:build <feature>`.
