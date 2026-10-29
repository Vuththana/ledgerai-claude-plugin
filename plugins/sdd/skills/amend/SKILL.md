---
name: amend
description: Change an approved (✅) LedgerVision spec the SDD way — before any code changes. Records the change with new or withdrawn IDs, settles its questions, marks the affected plan items and tasks stale, lists the tests and QA scenarios it invalidates, and re-approves the spec. Usage /sdd:amend <feature> <what should change>.
argument-hint: <feature> <the change, e.g. "branch names may repeat across businesses but not within one">
disable-model-invocation: true
---

# Amend: $ARGUMENTS

Load the `sdd:conventions` skill first. The first word of **$ARGUMENTS** is the feature; the rest is the change. If the change is missing, ask for it.

`TEAM-RULES.md` §6: when the code must behave differently from an approved spec, **the spec changes first**, then the code. This is that step. Spec gaps raised by reviewers and QA come here too.

## 1. Start

Find a **writable** docs clone (conventions §1) and the feature; the spec must be ✅. Switch to `spec/<feature>`, created from `origin/main` if needed (ask first if the clone has uncommitted changes). Set the status to **⟳ Amending** and commit (`Spec: <title> amending`), so `/sdd:build` pauses the stale tasks.

## 2. Write the change

- **New behaviour** → new `R` / `E` / `M` with the next free numbers.
- **Changed meaning** → strike the old ID through (`~~**BRN-R04**~~ withdrawn in v<X.Y.Z> — replaced by BRN-R12`) and add the new one. Never edit an approved meaning in place: tests and QA name the old ID and must show up as drift.
- **Wording only** → edit in place.
- A decision behind the change → a new `D`. Anything unsettled → a `Q`.
- Dictionary or endpoint changes → §8 / §9 as `proposed` / `📝 planned`.

## 3. Settle it

Start `sdd:spec-auditor` (mode `audit`) on the feature, telling it which IDs are new or withdrawn. Then ask, apply and re-audit exactly as `/sdd:clarify` §2–§5 (load that skill's steps if you need them).

## 4. Impact

Run `python3 -I "${CLAUDE_SKILL_DIR}/../trace/scripts/sddtool.py" trace <docs> <feature> <repos…> --no-write`, with every code repo in the workspace. From it and the files:

- **Tasks:** in `tasks.md`, mark every task covering a withdrawn or changed ID with `⟳` after its ID (`- [ ] **T07** ⟳ …`); reopen done ones (`[x]` → `[ ]`). Don't add tasks for new IDs here — `/sdd:tasks` does that.
- **Plan:** list the plan sections that mention those IDs. Don't edit `plan.md` here.
- **Tests and QA:** list the tests and scenarios that name withdrawn IDs (the trace's DRIFT lines).

## 5. ⏸ Re-approve

Show the user: the change (IDs added / withdrawn / reworded), the shared-doc edits, and the impact. On an explicit yes:

1. Status ✅. Version: **MAJOR** if an approved behaviour changed or was withdrawn, **MINOR** if it only adds.
2. `VERSION.md` entry with **Impact** per repo (the impact list from §4).
3. `sddtool.py check` (tasks may now show "has no task" for new IDs — expected until `/sdd:tasks`), then commit `Spec: <title> amended (v<X.Y.Z>)`. Don't push.

## 6. Reply

The change by ID, version, impact, and next steps: `/sdd:plan <feature>` to update the plan (change mode), then `/sdd:tasks <feature>` for the new and stale tasks.
