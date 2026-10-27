---
name: review-feature
description: Review a LedgerVision feature's implementation against its flow doc and the data dictionary. Usage /ledgerai:review-feature <feature>.
argument-hint: <feature name, e.g. "authentication">
disable-model-invocation: true
---

Review the implementation of the LedgerVision feature: **$ARGUMENTS**

This checks **behaviour against the requirements**, not code style. For a code-level review of a branch or PR, use the repo's PR review skill (e.g. `/website-dev:review-pull-request`) or `/code-review`.

## 1. Requirements

Follow the `analyze-requirements` skill for "$ARGUMENTS": the flow doc, its status, and every dictionary table it uses. If the flow is a 📝 draft, say so and review against its proposed decisions, marking them "not settled".

## 2. Requirement-by-requirement check

Make a list of every decision, rule, state, message and role rule in the flow. For each one, find where the code implements it.

| # | Requirement (flow §) | Where in code | Status |
|---|---|---|---|

Status is ✅ done, ❌ missing, ⚠️ different from the flow (explain how), or 🔒 role leak.

## 3. Data

Run the `dictionary-checker` agent on the feature's types, forms, mock data and API code. Include its findings.

## 4. Roles

Check, with both seeded users where possible:

- `BRANCH_MANAGER` only ever gets their own branch's data, in the UI and in the data layer.
- Owner-only parts are blocked in all three places: nav, route/layout, data.
- The owner's "All branches" and single-branch views both work.

## 5. States and edge cases

Run the `identify-edge-cases` checklist against the implementation, not just the flow.

## Report

1. **Summary:** done / missing / different counts.
2. **Blocking:** missing requirements, role leaks, dictionary mismatches.
3. **Should fix:** missing states, messages that differ from the flow.
4. **Flow gaps:** things the code had to decide that the flow doesn't cover, for the team.

Report only. Don't change code unless the user asks.
