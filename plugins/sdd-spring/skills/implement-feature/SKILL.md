---
name: implement-feature
description: Build the tasks of an approved LedgerVision SDD plan in a Spring Boot service step by step, from tasks.md to a working feature with tests named by requirement ID. Use when asked to implement, build or continue a backend feature, endpoint set or service behaviour.
---

# Implement a feature (Spring Boot)

**What** to build comes from the spec (`specs/<feature>/spec.md`), the data dictionary and `TRD.md`. **How** code is written comes from `CLAUDE.md` and `.claude/rules/` (`spring.md` loads when you touch `src/`). **Which work, in what order** comes from `tasks.md`. Paths like `specs/` and `api/` are in the docs root (`sdd:conventions` §1).

## 0. Gate

- The spec is ✅ and `specs/<feature>/plan.md` exists. No plan → `/sdd:plan` first, and wait for approval.
- You have task IDs from `tasks.md`. Skip ⟳ stale tasks.
- If the plan or spec must change, that happens first (`/sdd:plan` change mode, `/sdd:amend`), then the code.
- One feature at a time, on its own branch (`workflow.md`).
- **This service owns it** (`TRD.md` §1a). Writing another service's tables is an API call or an event instead — stop.
- Dependencies the plan needs: add a missing one in the task that first needs it (`packages.md`; no package request for backend repos).

## 1. Per task

Read the IDs the task covers in the spec — the requirement, its messages (`M`) and edge cases (`E`). Then, depending on the task:

- **Schema** — `add-migration` for the plan's tables.
- **Entities and repositories** — one entity per table in `<feature>/entity`; repositories in `<feature>/repository`, every finder on a scoped table taking `business_id` (and `branch_id` for managers).
- **Endpoints** — `add-endpoint` for each, exactly as the plan's §3 contract: DTOs and validation, service (rules, role, scope, transaction), controller, error codes with the `M` text in `messages.properties`, and the API reference entry once the user confirms (`add-endpoint` §6).
- **Everything else the plan lists** — Redis keys with the spec's names and TTLs; Feign + Resilience4j calls; events after commit with idempotent consumers; emails from `messages.properties`; jobs with ShedLock. Each per its `spring.md` section.
- **Edge cases** — the task's `E` IDs, checked with `identify-edge-cases` against the code.
- **Tests** — `write-tests`: every `@DisplayName` starts with the ID it proves (`"BRN-R03 rejects a taken name"`), so `/sdd:trace` counts it. Every endpoint × error code × role.

After each task: `./gradlew compileJava` (or the hook), and the task's "done when". Report `T02 done → files`.

## 2. Check, once the tasks are done

```bash
./gradlew build
```

Then run it for real:

1. Infrastructure per `CLAUDE.md`, then `./gradlew bootRun` in the background; wait for `GET /actuator/health` = `UP`.
2. `curl` each new endpoint as each role, directly and through the api-gateway. Check the envelope (`success`, `code`, `data`), the rows and any emails (Mailpit).
3. Stop the app.
4. Compare the controllers' `@*Mapping`s with `api/<service>.md`: any confirmed endpoint without an entry gets it now.

Then `/sdd:verify <feature>`.

## When the spec doesn't answer something

Stop and ask. It's a **spec gap** (→ `/sdd:amend`) or a TRD question. Don't invent behaviour, fields, error codes or events, and don't edit the docs.
