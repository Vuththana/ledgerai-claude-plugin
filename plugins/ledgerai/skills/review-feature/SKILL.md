---
name: review-feature
description: Review a LedgerVision feature's implementation against its flow doc and the data dictionary. Usage /ledgerai:review-feature <feature>.
argument-hint: <feature name, e.g. "authentication">
disable-model-invocation: true
---

Review the implementation of the LedgerVision feature: **$ARGUMENTS**

This checks **behaviour against the requirements**, not code style. For a code-level review of a branch or PR, use the repo's PR review skill (e.g. `/website-dev:review-pull-request`) or `/code-review`.

## 1. Run both reviewers at once

In one message, start two agents with the Agent tool, so they run in parallel:

| Agent (`subagent_type`) | Prompt |
|---|---|
| `ledgerai:feature-reviewer` | Review the **$ARGUMENTS** feature in **<absolute path of this repo>**. |
| `ledgerai:dictionary-checker` | Check the **$ARGUMENTS** feature's code in **<absolute path of this repo>** against the dictionary: its types, forms, mock data and API code, or its migrations, entities and DTOs. |

## 2. Report

Merge the two replies into one report:

1. **Summary:** done / missing / different counts, and the dictionary-checker's mismatch count.
2. **Blocking:** missing requirements, role leaks, dictionary mismatches.
3. **Should fix:** missing states, messages that differ from the flow.
4. **Flow gaps** and **Dictionary gaps:** for the team.

Keep each finding's `path:line` and doc reference. Report only. Don't change code unless the user asks.
