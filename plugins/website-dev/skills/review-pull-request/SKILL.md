---
name: review-pull-request
description: Review a LedgerVision web-ui branch or pull request against the team rules and this repo's rules before merging. Usage /website-dev:review-pull-request [PR number | branch].
argument-hint: "[PR number | branch]"
disable-model-invocation: true
---

Review the changes in: **$ARGUMENTS** (if empty: the current branch against `main`).

This checks the changes against the **rules**: `docs/TEAM-RULES.md` and `.claude/rules/`. For a general bug hunt, also run `/code-review`. To check behaviour against the flow, run `/ledgerai:review-feature <feature>`.

## 1. Get the diff

- PR number: `gh pr view <n>` and `gh pr diff <n>`
- Branch, or empty: `git diff main...<branch>` and `git log --oneline main..<branch>`

Read changed files in full where the context matters.

## 2. Check

1. **The team checklist:** every item in `docs/TEAM-RULES.md` §9.
2. **This repo's rules:** for each changed file, the rules in `.claude/rules/` whose `paths` match it, plus the always-on rules.
3. **Mechanical checks:**

| Check | How |
|---|---|
| Data matches the dictionary | Run the `dictionary-checker` agent on changed types, forms, mock data and API files |
| `src/lib/api` matches the API reference | Each changed `src/lib/api` function and its mock use the method, path, fields and error codes of its endpoint in `docs/api/<service>.md`. An endpoint not listed there must be in the approved plan |
| Only `src/lib/api` imports `src/lib/mock` | `git diff main...HEAD --name-only \| xargs grep -ln "lib/mock"` |
| No dependency changes without an approved request | Any diff to `package.json` or `pnpm-lock.yaml` → ask for the request |
| `docs/` untouched | Any change under `docs/` (other than a deliberate submodule bump) is a blocker |
| Builds | Run `pnpm lint` and `pnpm build` |

## 3. Report

Each finding with `path:line`, the rule it breaks (file and section), and the fix:

- **Blocking:** role leaks, dictionary mismatches, `docs/` edits, unapproved packages, failing build
- **Should fix:** missing states, rule breaks
- **Nits**

End with a verdict: **Ready to merge**, **Merge after fixes**, or **Needs another review**.

Don't comment on GitHub, push or merge unless the user asks.
