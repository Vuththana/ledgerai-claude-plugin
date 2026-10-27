---
name: review-pull-request
description: Review a LedgerVision Spring Boot service branch or pull request against the team rules, the TRD and this repo's rules before merging. Usage /springboot-dev:review-pull-request [PR number | branch].
argument-hint: "[PR number | branch]"
disable-model-invocation: true
---

Review the changes in: **$ARGUMENTS** (if empty: the current branch against `main`).

This checks the changes against the **rules**: `docs/TEAM-RULES.md`, `docs/TRD.md` and `.claude/rules/`. For a general bug hunt, also run `/code-review`. To check behaviour against the flow, run `/ledgerai:review-feature <feature>`.

## 1. Get the diff

- PR number: `gh pr view <n>` and `gh pr diff <n>`
- Branch, or empty: `git diff main...<branch>` and `git log --oneline main..<branch>`

Read changed files in full where the context matters.

## 2. Check

1. **The team checklist:** every item in `docs/TEAM-RULES.md` §9.
2. **This repo's rules:** for each changed file, the rules in `.claude/rules/` whose `paths` match it (mostly `spring.md`), plus the always-on rules.
3. **Mechanical checks:**

| Check | How |
|---|---|
| Schema and DTOs match the dictionary | Run the `dictionary-checker` agent on changed migrations, entities and DTOs |
| No applied migration edited | `git diff --name-status main...HEAD -- src/main/resources/db/migration/`: anything but `A` (added) is a blocker |
| Only this service's tables | Every table in new migrations and entities is this service's in `docs/TRD.md` §1a |
| Scope in every query | Repository methods on scoped tables filter by `business_id` (and `branch_id` for managers). No scope read from the request |
| No unapproved dependencies | Any diff to `build.gradle`, `settings.gradle` or `gradle/` → ask for the approved package request |
| No secrets | No real secrets in `application*.yml`, tests or compose files. `.env` isn't committed. No password/token/OTP in log statements (`grep -nE 'log\.(info\|debug\|warn\|error).*(password\|token\|otp\|secret)'`) |
| Error format | New failures use `ApiException` + `messages.properties`. No `ex.getMessage()` in responses |
| `docs/` untouched | Any change under `docs/` (other than a deliberate submodule bump) is a blocker |
| Tests | New endpoints have integration tests for each error code and each role (`write-tests`) |
| Builds | `./gradlew build` |

## 3. Report

Each finding with `path:line`, the rule it breaks (file and section), and the fix:

- **Blocking:** scope or role leaks, dictionary mismatches, edited migrations, other services' tables, secrets, `docs/` edits, unapproved dependencies, failing build
- **Should fix:** missing tests or states, rule breaks
- **Nits**

End with a verdict: **Ready to merge**, **Merge after fixes**, or **Needs another review**.

Don't comment on GitHub, push or merge unless the user asks.
