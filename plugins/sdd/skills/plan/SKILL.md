---
name: plan
description: Write and approve the plan for an approved LedgerVision spec — the planner agent writes specs/<feature>/plan.md across every repo involved (API contract, screens, data, roles, files, edge cases, verification), every item citing requirement IDs; the user approves it before any code. Also updates a plan after /sdd:amend. Usage /sdd:plan <feature>.
argument-hint: <feature slug or prefix>
disable-model-invocation: true
---

# Plan: $ARGUMENTS

Load the `sdd:conventions` skill first and follow it.

## 1. Spec and repos

1. Find a **writable** docs clone and the feature (conventions §1–2). The spec must be ✅. 📝 → suggest `/sdd:clarify` and stop. ⟳ → suggest finishing `/sdd:amend` and stop.
2. **Repos:** the owning service of each table and endpoint the spec writes (`TRD.md` §1a) plus web-ui if it has routes. In a workspace folder they're subfolders; in a single repo, it's this one. A repo the feature needs that isn't here: say so and stop.
3. `plan.md` already exists and `sddtool.py check` says the spec changed since → **change** mode. Exists and no change → show it and ask what to change (change mode) or stop.
4. Switch the clone to `feature/<feature>`, created from `origin/main`, or from `spec/<feature>` while that isn't merged (or the existing branch; ask first if there are uncommitted changes).

## 2. Plan

Start `sdd:planner`:

> Mode `<plan | change>`, feature **<feature>**. Docs root: **<abs>**. Repos: **<abs path — role>** for each. <change mode: "Amended IDs: … / Requested change: …">

If it replies with open questions (§10, or a 📝 spec): ask the user with AskUserQuestion; questions the spec should settle go to `/sdd:amend` — stop and say so. Otherwise continue **the same** planner with the answers.

## 3. ⏸ Gate 1 — approve the plan

Show the plan as it is, and its IDs line. Ask the user to approve it or ask for changes; changes go back to the same planner with SendMessage. **Don't save or continue without an explicit approval.**

## 4. Save

1. Get the spec's commit: `git -C <docs> log -1 --format=%h -- specs/<feature>/spec.md`. Put it in the header's **Spec:** line with the date and approver.
2. Write `specs/<feature>/plan.md`. In change mode keep the old Changes rows and add the planner's line with the approver filled in.
3. `specs/README.md`: stage `tasks`. `VERSION.md`: PATCH, "Plan: <feature>".
4. `sddtool.py check` — no ERROR about the plan. Commit `Plan: <title> (v<X.Y.Z>)`. Don't push.

## 5. Reply

The plan path, repos and roles, and the next step: `/sdd:tasks <feature>` (or `/sdd:run <feature>` to go on through build, review, QA and ship).
