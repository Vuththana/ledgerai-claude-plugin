---
name: review-pr
description: Review a LedgerVision pull request, branch or working tree in this repo — the stack reviewer (web-ui or Spring service) and dictionary-checker in parallel, plus spec-reviewer when the branch belongs to a feature with an SDD spec. Read-only; never comments on GitHub. Usage /sdd:review-pr [PR number | branch].
argument-hint: [PR number | branch — default: current branch + working tree]
disable-model-invocation: true
---

# Review: $ARGUMENTS

Load the `sdd:conventions` skill first.

1. **Stack:** `package.json` with `next` → `sdd-web:web-reviewer`; `build.gradle` with Spring Boot → `sdd-spring:api-reviewer`. Neither: say this repo has no stack reviewer and run only the dictionary check.
2. **Feature:** from the branch name (`feature/<feature>`) or the PR title, look for `specs/<feature>/` in the docs root (conventions §1). If it exists, the review includes the spec.
3. **In one message:**
   - the stack reviewer: *Review **<PR n | branch | the working tree>** in **<abs repo path>**. Docs root: **<abs>**. Plan: **<abs plan.md, if any>**.*
   - `sdd:dictionary-checker`: *Check the files changed in **<repo>** by **<target>**. Docs root: **<abs>**.*
   - with a spec, `sdd:spec-reviewer`: *Review the **<feature>** feature. Docs root, spec / plan / tasks: **<abs>**. Repos: **<this repo>** (only this repo's part).*
4. **Reply:** one list, **Blocker / Major / Minor / Spec gaps**, each finding once (drop duplicates between reviewers, keeping the most precise), with `path:line`; then each reviewer's verdict.

Read-only: no edits, no GitHub comments, no pushes. Offer to fix the findings only if the user asks.
