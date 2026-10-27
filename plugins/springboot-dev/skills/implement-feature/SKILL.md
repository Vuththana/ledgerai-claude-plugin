---
name: implement-feature
description: Build an approved LedgerVision feature in a Spring Boot service step by step, from the approved plan to a working, tested feature. Use when asked to implement, build or continue a backend feature, endpoint set or service behaviour.
---

# Implement a feature (Spring Boot)

**What** to build comes from the docs (`docs/flow/<feature>.md`, `docs/data-dictionary/`, `docs/TRD.md`). **How** code is written comes from `CLAUDE.md` and `.claude/rules/` (`spring.md` loads when you touch `src/`). This skill is the order of work.

## 0. Gate

- The feature has an **approved plan** (`/ledgerai:document-feature`). No plan → write one first and wait for approval.
- Its flow is ✅ approved, or the parts you build are settled (`feature-flows.md`).
- It's the one feature being worked on (`workflow.md`), on its own branch.
- **This service owns it** (`docs/TRD.md` §1a). If the plan writes another service's tables, stop: that's an API call or an event instead.
- Every dependency the plan needs is already in `build.gradle`. If one is missing, stop: it needs a package request (`packages.md`).

## 1. Schema

Follow the `add-migration` skill for the plan's tables. Then run the `dictionary-checker` agent on the migration.

## 2. Entities and repositories

- One entity per table in `<feature>/entity`. Column names, nullability and lengths come from the migration and the dictionary.
- Repositories in `<feature>/repository`. Every finder on a scoped table takes `business_id` (and `branch_id` for managers).
- Run the `dictionary-checker` agent on the entities.

## 3. Endpoints

Follow the `add-endpoint` skill for each endpoint in the plan: DTOs and validation, service method (rules, role, scope, transaction), controller, error codes and messages.

## 4. Everything else the plan lists

- **Redis keys** with the flow's names and TTLs.
- **Calls to other services** through Consul with client credentials.
- **Events** published after commit, and idempotent consumers.
- **Emails** whose text lives in `messages.properties`.
- **Scheduled jobs** with ShedLock.

Each follows its section in `spring.md`.

## 5. States, messages and edge cases

Every rule, limit, state and message the flow defines, with its wording and its error `code`. Go through the `identify-edge-cases` checklist against the code.

## 6. Tests

Follow the `write-tests` skill: unit tests for the rules, and integration tests for every endpoint × error code × role.

## 7. Check

```bash
./gradlew build
```

Then run it for real:

1. `docker compose up -d`, then `./gradlew bootRun` (in the background).
2. Wait for `GET /actuator/health` to report `UP`.
3. Call each new endpoint with `curl` as each role. Seeded users or tokens come from the repo's README or the plan.
4. Check the responses, the database rows and any emails (Mailpit).
5. Stop the app afterwards.

Then:

- Run `/ledgerai:review-feature <feature>` against the flow.
- Run `/springboot-dev:review-pull-request` before opening the PR.

## When the docs don't answer something

Stop and ask. Note it as a flow gap or TRD question. Don't invent behaviour, fields, error codes or events, and don't edit `docs/`.
