---
name: debug-backend
description: Investigate and fix LedgerVision Spring Boot service bugs — startup and Flyway failures, schema validation, 401/403 from Keycloak tokens, JSON naming, lazy loading, ModelMapper, Postgres enums, time zones, Consul, RabbitMQ, ShedLock, Testcontainers and branch-scope leaks. Use when the service errors, a test fails, or behaviour differs from the docs.
---

# Debug the backend

## Approach

1. **Reproduce.** Note the endpoint, the role, the request body and the exact response, or the failing test.
2. **Read the actual error:**
   - the first `Caused by:` in the `./gradlew bootRun` log or the test report (`build/reports/tests/test/index.html`)
   - `docker compose logs <service>` for Postgres, Keycloak, RabbitMQ and Consul
3. **Check versions** against the real jars (`./gradlew dependencies`). Spring Boot 3.5 / Hibernate 6 APIs differ from older examples.
4. **Fix the cause.** Don't catch and ignore, don't loosen `ddl-auto`, don't disable security, and don't add a library to work around it.
5. **Not sure what's correct?** The flow doc and `docs/TRD.md` define the expected behaviour.

## Common causes in this stack

| Symptom | Likely cause | Rule |
|---|---|---|
| `FlywayValidateException: checksum mismatch` / "applied migration not resolved" | A migration that already ran was edited or renamed. Restore it and add a new one | `spring.md` § Persistence |
| Flyway: "non-empty schema without schema history table" | Shared DB: `baseline-on-migrate` missing, or the history table isn't `flyway_schema_history_<service>` | `spring.md` § Persistence |
| `Schema-validation: missing column` / `wrong column type` | Entity and migration disagree. The dictionary decides which one is wrong | `data-dictionary.md` |
| `column "x" is of type <enum> but expression is of type character varying` | Postgres enum not mapped: add `@JdbcType(PostgreSQLEnumJdbcType.class)` | `spring.md` § Persistence |
| Times off by 7 hours | `hibernate.jdbc.time_zone=UTC` missing, or `LocalDateTime` used with the server's zone (Asia/Phnom_Penh is UTC+7) | `spring.md` § Persistence |
| `401` on every request | The token's `iss` (e.g. `localhost:8080`) differs from the configured `issuer-uri` (e.g. `keycloak:8080` inside Docker), or the audience is missing | `spring.md` § Security |
| `401 SESSION_REVOKED` straight after sign-in | The token's `iat` is in the same second as the revocation time: compare with `>=`, or check clock skew | `docs/flow/authentication.md` §11 |
| `403` on `POST` with no message | CSRF is on: disable it for the stateless API | `spring.md` § Security |
| Manager sees another branch's data | A repository method without `branch_id`, or the scope taken from the request instead of the current user | `data-dictionary.md` § Roles |
| JSON has camelCase keys or `null` fields | The global `SNAKE_CASE` naming isn't applied (a custom `ObjectMapper` replaced Boot's), or the DTO field name isn't the dictionary's | `spring.md` § JSON |
| `LazyInitializationException` | A lazy relation read outside the transaction: map to a DTO in the service, or use a fetch join | `spring.md` § Persistence |
| ModelMapper copies the wrong field, or reports ambiguous matches | Not using the `STRICT` strategy, or an explicit `TypeMap` is needed | `spring.md` § ModelMapper |
| A protected field changed through a request | A request DTO mapped onto the entity. Set protected fields explicitly | `spring.md` § ModelMapper |
| `lb://<service>` → 503 / no instances | Not registered in Consul, its health check is failing, or the service name differs | `spring.md` § Transactions, other services and events |
| Event consumed but data missing, or consumed twice | Published before commit, or the consumer isn't idempotent | `spring.md` § Transactions, other services and events |
| Scheduled job runs on every instance | `@EnableSchedulerLock` or `@SchedulerLock` missing | `spring.md` § Jobs |
| Testcontainers: "Could not find a valid Docker environment" | Docker isn't running, or the user can't reach the socket | — |
| An error message leaks SQL or a stack trace | The handler returns `ex.getMessage()`. Use `messages.properties` and log the details | `spring.md` § Errors |

## After the fix

- `./gradlew build` passes.
- If the bug touched data access, add a test that would have caught it, including the role/scope case.
- If the bug came from the docs being unclear, note it as a flow gap or TRD question.
