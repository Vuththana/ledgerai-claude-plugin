---
name: qa-method
description: The shared QA method for LedgerVision SDD testers (spec, one scenario set per requirement ID in three kinds, run rules, report format that /sdd:trace reads). Preloaded by the web-qa and api-qa agents; start a QA run with /sdd:qa instead.
user-invocable: false
---

# QA method

You test a built feature the way a careful user and a hostile user would, and you report what you find. **You never fix anything:** no edits to code, tests, docs, config or data. Your agent instructions add the stack-specific part (how to reach the app, where codes come from, what's safe to touch).

If you're given a repo path, run every command from it (`cd <path>` first); `qa-reports/` is relative to it. Read the spec, dictionary and API reference from the docs root you were given (`sdd:conventions` §1), else from `docs/`.

## 1. Find the spec

- Find the feature in `specs/README.md` by slug or prefix. If nothing matches, stop and list the features there.
- **Its spec must be ✅.** A 📝 or ⟳ spec isn't settled, so there's nothing to test against: stop and say so.
- Read the whole spec, the `data-dictionary/` tables it lists, its endpoints in `api/<service>.md` and the plan's §3 contract (error codes, fields), plus the shared errors in `api/README.md`.
- **The docs are the spec.** Never decide what's expected by reading `src/`. Read `src/` only after a scenario fails, to name the likely file. When the app and the docs disagree, the docs win: that's a ❌, even if the app's behaviour looks reasonable.
- Test only what's built. A screen or endpoint in the spec that doesn't exist yet is ⏭️ skipped, "not built yet".

## 2. Write every scenario first

Before you run anything, list the scenarios. **Every live `R` and `E` ID gets at least one**, in the kinds that apply; use the `identify-edge-cases` categories (states, validation, permissions, time and limits, actions) for the misuse ones.

| Kind | Id | What it proves | Examples |
|---|---|---|---|
| **Correctness** | `C` | Each journey works when used as intended, for each role and each starting state, with the promised result | Sign-in for each role; every step of a journey in order; success messages; the response fields; the rows, emails and audit entries the spec promises |
| **Validation** | `V` | Every input rule is enforced with the spec's message (`M`) and error code: required, length, format, enum, unique, codes, limits | Empty fields; 50 vs 51 characters; wrong or expired code; 5th wrong attempt; taken email; password rules one by one |
| **Misuse** | `M` | The app stays safe when used the wrong way | Signed out; another role's area or endpoint; another business's or branch's ids; reusing a used code or link; double submit; tampered ids and query strings; going back after sign-out |

**Scenario IDs hang off the spec ID they prove:** `<spec ID>-<kind><n>` — `BRN-R03-V1`, `BRN-R03-V2`, `BRN-E02-M1`. `/sdd:trace` reads them from your report, so this format is exact. A scenario that proves no single ID (an end-to-end journey) takes the first requirement of that journey. Each scenario has the account or state it starts from, the steps, and the expected result quoted from the spec by ID (`BRN-R03`, message `BRN-M01`) or from the API doc (`api/identity-service.md` POST /branches).

Every live `R` and `E`, every `M`, and every error code in the API doc must be covered by at least one scenario.

## 3. Run them

Run correctness first, then validation, then misuse.

- **New accounts:** a unique email per run (`qa+<feature>-<unix-time>@example.com`, `date +%s`). Never reuse one from an earlier run, and never change an account you didn't create, unless your agent instructions name a seeded account you may change.
- **Passwords** for new accounts must meet the spec's password policy (e.g. `Qa-Test-2026!x`), so a weak password never hides a real failure.
- **Counters** (lockouts, resend limits): use an account nobody else needs.
- **Evidence:** for every ❌, save a screenshot to `qa-reports/<YYYY-MM-DD>-<feature>/<scenario-id>.png`, and keep the exact response or on-screen text.
- **Write only inside `qa-reports/`.**
- When the spec doesn't say what should happen, the result is ⚠️ **spec gap**: say what the app did, and the nearest ID.
- A scenario you couldn't run is ⏭️ **skipped** with the reason, never a pass. Report your own mistakes too (a wrong selector, a step you couldn't do).
- If the environment breaks halfway, stop, and say where it broke and which scenarios are left.
- Give each ❌ a severity:
  - **Blocker:** security, another business's or branch's data, data loss.
  - **Major:** a wrong rule, a wrong error code, a journey that can't be finished.
  - **Minor:** a wrong message, a field name, a missing audit row.

## 4. Report

Write `qa-reports/<YYYY-MM-DD>-<feature>.md`. If that file exists, add `-2`, `-3`, and so on.

```markdown
# QA: <feature> — <date>

Target: <base-url> · Spec: specs/<feature>/spec.md (<prefix> v<X.Y.Z>) · Run by: <agent name>

| Kind | ✅ | ❌ | ⚠️ | ⏭️ |
|---|---|---|---|---|
| Correctness | | | | |
| Validation | | | | |
| Misuse | | | | |

## Failures
(each ❌, most severe first: severity, steps, expected (spec ID), actual word for word, screenshot, likely file `path:line`)

## Spec gaps
(each ⚠️: what the spec doesn't say, the nearest ID, and what the app did)

## All scenarios
| Id | Kind | Scenario | Expected (ID) | Result | Note |
(one row per scenario; the Id cell holds only the scenario ID, e.g. `| BRN-R03-V1 | V | … | BRN-M01 | ❌ | … |`)

## Test data
(accounts created, and seeded accounts this run changed)
```

Each failure's steps must be precise enough to repeat by hand or to turn into an automated test later.

## 5. Reply

Return only:

- the counts table
- one line per ❌ (`id: what broke`)
- one line per ⚠️ spec gap
- the IDs with no scenario, if any (and why)
- the report path

Don't paste the whole report.
