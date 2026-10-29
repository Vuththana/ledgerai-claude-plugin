---
name: build
description: Build a LedgerVision feature from its tasks.md — starts one developer agent per repo (Spring services, web-ui, ai-service) on their task IDs in dependency order, routes their questions, endpoint confirmations and package requests to the user, and ticks each task done with its files. Usage /sdd:build <feature> [task IDs].
argument-hint: <feature> [T01 T02 … to build only those]
disable-model-invocation: true
---

# Build: $ARGUMENTS

Load the `sdd:conventions` skill first and follow it. You are the **lead**: you don't write feature code. Developers build; you pass work, ask the user, and are the only one who edits `tasks.md`.

## 0. Ready?

1. Find the **writable** docs clone, the feature and its `feature/<feature>` branch (conventions §1–2).
2. Run `python3 -I "${CLAUDE_SKILL_DIR}/../trace/scripts/sddtool.py" check <docs> <feature>`. Stop on:
   - a 📝 spec → `/sdd:clarify`; no plan → `/sdd:plan`; no tasks or "has no task" errors → `/sdd:tasks`;
   - "spec.md changed since the plan was approved" → `/sdd:plan` (change mode), then `/sdd:tasks`.
   - A ⟳ spec: go on, but only with tasks not marked ⟳.
3. **Repos and developers.** Each task's repo, at its absolute path (workspace subfolder, or the current repo):

   | The repo has | Developer | Tester |
   |---|---|---|
   | `package.json` with `next` | `sdd-web:web-dev` | `sdd-web:web-qa` |
   | `build.gradle` with `org.springframework.boot` | `sdd-spring:api-dev` | `sdd-spring:api-qa` |
   | `pyproject.toml` with `fastapi` | `sdd-fastapi:ai-dev` (placeholder) | `sdd-fastapi:qa-ai` (placeholder) |

   A developer whose plugin isn't enabled: stop and say which plugin to enable (or start from the workspace folder with `templates/workspace-settings.json`). An ai-service task: `ai-dev` is a placeholder — say the AI part isn't ready and what it waits on, and build the rest.
4. **Which tasks:** the IDs in $ARGUMENTS after the feature, else every open task (`[ ]`, not ⟳).

## 1. Start the developers

One developer per repo, **in one message** so they work in parallel, each with its own tasks in file order:

> Build tasks **<T ids>** of the **<feature>** feature in **<abs repo path>**. Docs root: **<abs>**. Spec: **<abs spec.md>** · Plan: **<abs plan.md>** · Tasks: **<abs tasks.md>**. Read the plan in full and your tasks before you start, and again whenever I say they changed. Work on `feature/<feature>` from `origin/dev`; never on `main`.

- A task `after` another repo's open task: hold that developer's dependent tasks back and send them when the dependency reports done (SendMessage). web-ui builds on the mock against the plan's §3 contract, so it rarely waits.
- Keep the user posted in one line per step: who's running, what came back.

## 2. While they work

- **`T07 done → files`:** tick it in `tasks.md` (`- [x] **T07** … · files: \`path\`, \`path\``) and update the **Progress** line.
- **Questions:** ask the user (AskUserQuestion when they're choices), then SendMessage the answers to **the same** developer.
- **Spec gaps:** don't let anyone decide them. Ask the user whether to `/sdd:amend` now (the tasks wait) or note them for later.
- **A plan change** (from an answer, or the user asks): continue or start `sdd:planner` in `change` mode, show the user the change; on approval, save `plan.md` (Changes row, new **Spec:** commit if the spec moved) and tell every developer to re-read it.
- **Endpoints to confirm** (`add-endpoint` §6): show each endpoint and its draft API reference entry. When the user confirms, tell that developer to write it in the docs clone on `feature/<feature>`, uncommitted. You commit them in `/sdd:ship`.
- **Package requests** (web-ui): show the draft, then file it with the user as `sdd:manage-dependencies` §4 says: who's asking, which browser, confirm the row, fill the team sheet, check it saved. Nothing is installed until the sheet says **Approved** (`TEAM-RULES.md` §7). Ask the user how to go on without it.
- A developer that fails twice: tell the user; don't do its work yourself.

## 3. Record

When every developer has replied: run `sddtool.py check`, commit `tasks.md` on the docs branch (`Tasks: <feature> T01–T07 done`). Don't push.

Reply per repo: tasks done / blocked / skipped, branch, checks run, questions still open, spec gaps; then the next step: `/sdd:verify <feature>`.
