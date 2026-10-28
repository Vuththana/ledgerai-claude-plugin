---
name: review-pull-request
description: Review a LedgerVision web-ui branch or pull request against the team rules and this repo's rules before merging. Usage /website-dev:review-pull-request [PR number | branch].
argument-hint: "[PR number | branch]"
disable-model-invocation: true
---

Review the changes in: **$ARGUMENTS** (if empty: the current branch against `main`).

This checks the changes against the **rules**: `docs/TEAM-RULES.md` and `.claude/rules/`. For a general bug hunt, also run `/code-review`. To check behaviour against the flow, run `/ledgerai:review-feature <feature>`.

## 1. Run both reviewers at once

In one message, start two agents with the Agent tool, so they run in parallel:

| Agent (`subagent_type`) | Prompt |
|---|---|
| `website-dev:pr-reviewer-web` | Review **$ARGUMENTS** (empty: the current branch against `main`) in **<absolute path of this repo>**. |
| `ledgerai:dictionary-checker` | Check the changed types, forms, mock data and API files of **$ARGUMENTS** (empty: the current branch against `main`) in **<absolute path of this repo>**. |

## 2. Report

Merge the two replies into one: each finding with `path:line`, the rule it breaks (file and section), and the fix.

- **Blocking:** role leaks, dictionary mismatches, `docs/` edits, unapproved packages, failing build
- **Should fix:** missing states, rule breaks
- **Nits**

End with the reviewer's verdict (**Ready to merge**, **Merge after fixes**, or **Needs another review**), made stricter if the dictionary-checker found mismatches.

Don't comment on GitHub, push or merge unless the user asks.
