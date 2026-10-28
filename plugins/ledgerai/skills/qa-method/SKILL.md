---
name: qa-method
description: The shared QA method for LedgerVision testers (spec, three kinds of scenarios, run rules, report format). Preloaded by the qa-web and qa-api agents; start a QA run with /ledgerai:qa instead.
user-invocable: false
---

# QA method

You test a built feature the way a careful user and a hostile user would, and you report what you find. **You never fix anything:** no edits to code, tests, docs, config or data. Your agent instructions add the stack-specific part (how to reach the app, where codes come from, what's safe to touch).

## 1. Find the spec

- Find the feature in `docs/flow/README.md` by its name or file (`authentication`, `profile-and-business`, ...). If nothing matches, stop and list the features there.
- **Its status must be ✅.** A 📝 draft flow isn't settled, so there's nothing to test against: stop and say so (`.claude/rules/feature-flows.md`).
- Read the whole flow, the `docs/data-dictionary/` tables it lists, and its endpoints in `docs/api/<service>.md` (error codes, fields) plus the shared errors in `docs/api/README.md`.
- **The docs are the spec.** Never decide what's expected by reading `src/`. Read `src/` only after a scenario fails, to name the likely file.
- Test only what's built. A screen or endpoint in the flow that doesn't exist yet is ⏭️ skipped, "not built yet".

## 2. Write every scenario first

Before you run anything, list the scenarios in three kinds. Use the categories of the preloaded `identify-edge-cases` skill (states, validation, permissions, time and limits, actions) and go through every section of the flow.

| Kind | Id | What it proves | Examples |
|---|---|---|---|
| **Correctness** | `C` | Each journey works when used as intended, for each role and each starting state, with the promised result | Sign-in for each role; every step of a flow in order; success messages; the response fields; the rows, emails and audit entries the flow promises |
| **Validation** | `V` | Every input rule is enforced with the flow's message and error code: required, length, format, enum, unique, codes, limits | Empty fields; 50 vs 51 characters; wrong or expired code; 5th wrong attempt; taken email; password rules one by one |
| **Misuse** | `M` | The app stays safe when used the wrong way | Signed out; another role's area or endpoint; another business's or branch's ids; reusing a used code or link; double submit; tampered ids and query strings; going back after sign-out |

Number them `<PREFIX>-<kind>-<nn>` with a short feature prefix (`AUTH-V-07`). Each scenario has the account or state it starts from, the steps, and the expected result quoted from the docs with its § (`docs/flow/authentication.md` §4a, `docs/api/identity-service.md` POST /auth/sign-in).

Aim for every rule in the flow and every error code in the API doc to be covered by at least one scenario.

## 3. Run them

Run correctness first, then validation, then misuse.

- **New accounts:** a unique email per run (`qa+<feature>-<unix-time>@example.com`, `date +%s`). Never reuse one from an earlier run, and never change an account you didn't create, unless your agent instructions name a seeded account you may change.
- **Counters** (lockouts, resend limits): use an account nobody else needs.
- **Evidence:** for every ❌, save a screenshot to `qa-reports/<YYYY-MM-DD>-<feature>/<scenario-id>.png`, and keep the exact response or on-screen text.
- **Write only inside `qa-reports/`.**
- When the docs don't say what should happen, the result is ⚠️ **flow gap**: say what the app did.
- A scenario you couldn't run is ⏭️ **skipped** with the reason, never a pass. Report your own mistakes too (a wrong selector, a step you couldn't do).

## 4. Report

Write `qa-reports/<YYYY-MM-DD>-<feature>.md`. If that file exists, add `-2`, `-3`, and so on.

```markdown
# QA: <feature> — <date>

Target: <base-url> · Flow: docs/flow/<file>.md · Run by: <agent name>

| Kind | ✅ | ❌ | ⚠️ | ⏭️ |
|---|---|---|---|---|
| Correctness | | | | |
| Validation | | | | |
| Misuse | | | | |

## Failures
(each ❌, most severe first: steps, expected (doc §), actual word for word, screenshot, likely file `path:line`)

## Flow gaps
(each ⚠️: what the docs don't say, and what the app did)

## All scenarios
| Id | Kind | Scenario | Expected (§) | Result | Note |

## Test data
(accounts created, and seeded accounts this run changed)
```

Each failure's steps must be precise enough to repeat by hand or to turn into an automated test later.

## 5. Reply

Return only:

- the counts table
- one line per ❌ (`id: what broke`)
- one line per ⚠️ flow gap
- the report path

Don't paste the whole report.
