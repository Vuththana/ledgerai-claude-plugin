---
name: add-migration
description: Write a Flyway migration for LedgerVision tables straight from the data dictionary (types, lengths, NOT NULL, defaults, enums, unique, keys, indexes). Use when a feature needs new tables or columns, or when asked to create or change the schema.
argument-hint: "[table names]"
---

# Add a Flyway migration

Tables: **$ARGUMENTS** (if empty: the tables in the approved plan).

## 1. Check before writing

- **Ownership:** every table must belong to this service in `docs/TRD.md` §1a. If one doesn't, stop. Another service migrates it.
- **Schema:** everything goes in this service's schema (`identity`, `sales`, `finance`). Flyway is configured with `spring.flyway.schemas=<schema>`, so write unqualified names (`CREATE TABLE users …`), not `public.` or another schema.
- **Already there?** Search `src/main/resources/db/migration/` for the table. If it exists, this is a change: write a new `ALTER` migration.
- **Never edit a migration that has already run** (merged, or applied on any database). Always add a new file.
- The dictionary must already have the field. If the plan needs one that isn't there, stop and propose it in the docs repo (`data-dictionary.md`).

## 2. File

- Path: `src/main/resources/db/migration/V<n>__<snake_case_description>.sql`.
- `<n>` is the next number after the highest existing one.
- One migration per logical change, e.g. `V3__create_notifications.sql`.

## 3. Map the dictionary to DDL

Read the table in `docs/data-dictionary/<file>.md`, column by column, in the dictionary's order:

| Dictionary | Postgres |
|---|---|
| `uuid` PK, "auto generated" | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `uuid` PK set elsewhere (e.g. `users.user_id` = Keycloak id) | `uuid PRIMARY KEY` (no default) |
| `varchar` + Length | `varchar(<length>)` |
| `text`, `integer`, `boolean`, `date`, `jsonb` | the same name |
| `numeric` | `numeric`. Precision is still open (`docs/TRD.md` Q13): don't invent one |
| `timestamp` | `timestamp` (holds UTC) |
| `enum` + "values: A, B" | `CREATE TYPE <table>_<field> AS ENUM ('A', 'B');` in this schema, created before the table. Values exactly as written, in the same order |
| Required `Y` | `NOT NULL` |
| Default | `DEFAULT <value>`: `current_timestamp`, `true`/`false`, numbers, `'<enum value>'` |
| "unique" in Description | `UNIQUE` constraint (case-insensitive fields like email: store lowercased) |
| FK + Reference, **same service** | `REFERENCES <table>(<pk>)` |
| FK + Reference, **another service's table** (another schema) | Keep the `uuid` column and an index, but no `REFERENCES` across schemas unless the team has agreed it. List it under "Questions" |
| "one per …" rules (e.g. one main branch per business) | partial unique index, e.g. `CREATE UNIQUE INDEX … ON branches (business_id) WHERE is_main_branch` |

Also:

- Index every FK column and the scope columns (`business_id`, `branch_id`) used in queries.
- Name constraints and indexes predictably: `<table>_<column>_key`, `<table>_<column>_fkey`, `<table>_<column>_idx`.
- No tables or columns for Redis data (OTP codes, pending transfers): see `data-dictionary.md`.
- No seed data in schema migrations, except fixed reference rows the docs define (e.g. `roles`). Put those in their own migration.

## 4. Check

- Run the `dictionary-checker` agent on the new file.
- `./gradlew build`: the integration tests run Flyway on a real Postgres 17. With `ddl-auto=validate`, the entities must then match.

## 5. Report

The file name, the tables and columns created, any cross-service references left without a FK, and any dictionary gaps found.
