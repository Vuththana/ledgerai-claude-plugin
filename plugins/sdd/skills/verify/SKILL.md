---
name: verify
description: Review a built LedgerVision feature in every repo it touches — spec-reviewer (behaviour, ID by ID), dictionary-checker and the stack reviewer per repo, in parallel — send Blocker and Major findings back to the developers for at most two fix rounds, then refresh the trace. Usage /sdd:verify <feature>.
argument-hint: <feature>
disable-model-invocation: true
---

# Verify: $ARGUMENTS

Load the `sdd:conventions` skill first and follow it. You are the lead.

## 1. Inputs

The docs clone (branch `feature/<feature>`), the feature's spec / plan / tasks, and the repos the plan's §2 names (absolute paths). Each repo should be on `feature/<feature>` (web-ui's M2: `feature/<feature>-integration`), branched from `dev`, with the work in its tree. If web-ui is involved, the current milestone (conventions §1c): add "Milestone: **M1** | **M2**" to every prompt below.

## 2. Review — all in one message

- `sdd:spec-reviewer` once: *Review the **<feature>** feature. Docs root: **<abs>**. Spec / plan / tasks: **<abs paths>**. Repos: **<abs paths>**.*
- Per repo, `sdd:dictionary-checker`: *Check the files changed in **<repo>** (working tree against `origin/dev`). Docs root: **<abs>**.*
- Per repo, its stack reviewer — `sdd-web:web-reviewer` or `sdd-spring:api-reviewer`: *Review the working tree of **<repo>** against `origin/dev`. Docs root: **<abs>**. Plan: **<abs plan.md>**.*

## 3. Fix — at most two rounds

1. Sort the findings by repo (and task ID where given). Send each developer its **Blocker** and **Major** findings word for word with SendMessage — the same developer agent from `/sdd:build` if it's in this session, else start that repo's developer (as in `/sdd:build` §1) with the findings and the task IDs they belong to.
2. Keep **Minor** and **Spec gaps** for the summary. Don't send them.
3. When the fixes are in, re-run only the reviewers that had Blockers.
4. After two rounds, list what's left for the user.

**Spec gaps** never get "fixed" in code: they go to the user for `/sdd:amend`.

## 4. Trace

Run `python3 -I "${CLAUDE_SKILL_DIR}/../trace/scripts/sddtool.py" trace <docs> <feature> <repos…>` and commit `trace.md` (`Trace: <feature>`). Don't push.

## 5. Reply

Per repo: verdicts, fixes made, findings left by severity. Then the trace summary line and its OPEN / DRIFT lines, spec gaps, and the next step: `/sdd:qa <feature>` (or `/sdd:amend` first for spec gaps that block).
