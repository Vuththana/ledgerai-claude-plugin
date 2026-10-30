---
name: qa
description: QA a built LedgerVision feature end to end against its approved spec — one scenario set per requirement and edge-case ID, in three kinds (correctness, validation, misuse). Picks the tester per repo (web-qa in the browser, api-qa through Swagger UI), runs them one at a time, sends Blocker and Major failures back for a fix round, and refreshes the trace. Usage /sdd:qa <feature> [base-url].
argument-hint: <feature> [base-url, when testing one repo]
disable-model-invocation: true
---

# QA: $ARGUMENTS

Load the `sdd:conventions` skill first. The spec must be ✅ (`qa-method` requires it).

## 1. Repos and testers

The repos the plan's §2 names (or the current repo), services first, web-ui last — **one tester at a time**: they share the Playwright browser.

| Repo | Tester | Default base URL |
|---|---|---|
| web-ui (`package.json` with `next`) | `sdd-web:web-qa` | `http://localhost:3000` — in M2, with `API_BASE_URL` pointing at the running services and no `MOCK_API`; if it isn't, ask the user to start it |
| Spring service | `sdd-spring:api-qa` | `http://localhost:<server.port>` from `src/main/resources/application.yml` |
| ai-service | `sdd-fastapi:qa-ai` (placeholder) | `http://localhost:8000` (`TRD.md` §1b) |

A base URL in $ARGUMENTS applies when testing one repo. A tester whose plugin isn't enabled: say which plugin to enable.

**web-ui milestone** (conventions §1c): in M1, web-qa runs a **screen check** of the static UI (any running app will do); in M2, the full `qa-method` run against the real services. Tell it which.

## 2. Run each

> QA the **<feature>** feature at **<base-url>**. Work in **<abs repo path>**. Docs root: **<abs>**. Plan: **<abs plan.md>**. <web-ui: "Milestone: **M1 static UI** (screen check) | **M2 integration**."> Follow the preloaded `qa-method` skill: find the spec, write a scenario set for every requirement and edge-case ID first, run them, write the report to `qa-reports/`, and reply with the summary only.

Each **Blocker** and **Major** ❌ goes to its repo's developer (SendMessage to the same one if it's in this session, else start it as in `/sdd:build` §1) — that's a fix round, at most two in total with `/sdd:verify`'s — then run that tester once more. **Spec gaps** (⚠️) go to the summary for `/sdd:amend`.

## 3. Trace

Run `python3 -I "${CLAUDE_SKILL_DIR}/../trace/scripts/sddtool.py" trace <docs> <feature> <repos…>` — it reads the newest report in each repo's `qa-reports/`. Commit `trace.md` in the docs clone (`Trace: <feature>`). Don't push.

## 4. Reply

Each tester's reply as it is (counts, ❌ and ⚠️ lines, report path), the fix rounds, then the trace summary with its OPEN and DRIFT lines, and the next step: `/sdd:ship <feature>`.
