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
- Every dependency the plan needs is in `build.gradle`, or listed in the plan. Add a missing one in the step that first needs it (`packages.md`): no package request for backend repos.

## 1. Schema

Follow the `add-migration` skill for the plan's tables. Then run the `dictionary-checker` agent on the migration.

## 2. Entities and repositories

- One entity per table in `<feature>/entity`. Column names, nullability and lengths come from the migration and the dictionary.
- Repositories in `<feature>/repository`. Every finder on a scoped table takes `business_id` (and `branch_id` for managers).
- Run the `dictionary-checker` agent on the entities.

## 3. Endpoints

Follow the `add-endpoint` skill for each endpoint in the plan: DTOs and validation, service method (rules, role, scope, transaction), controller, error codes and messages, and its entry in `docs/api/<service>.md`.

## 4. Everything else the plan lists

- **Redis keys** with the flow's names and TTLs.
- **Calls to other services** through OpenFeign clients with Resilience4j (token forwarding, or client credentials in jobs and listeners).
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

1. Start the infrastructure with the compose command in `CLAUDE.md`, then `./gradlew bootRun` (in the background).
2. Wait for `GET /actuator/health` to report `UP`.
3. Call each new endpoint with `curl` as each role, directly and through the api-gateway. Seeded users or tokens come from the repo's README or the plan. Check the response envelope (`success`, `code`, `data`).
4. Check the responses, the database rows and any emails (Mailpit).
5. Stop the app afterwards.

Then:

- Run `/ledgerai:review-feature <feature>` against the flow.
- Check that every endpoint of the feature is in `docs/api/<service>.md` (the docs PR from `add-endpoint` step 6).
- Run `/springboot-dev:review-pull-request` before opening the PR.

## When the docs don't answer something

Stop and ask. Note it as a flow gap or TRD question. Don't invent behaviour, fields, error codes or events, and don't edit `docs/`.
