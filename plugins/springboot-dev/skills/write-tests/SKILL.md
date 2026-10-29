---
name: write-tests
description: Write unit and integration tests for a LedgerVision Spring Boot service — JUnit 5 + Mockito for rules, Testcontainers (Postgres 17, Redis, RabbitMQ) for endpoints, with every error code and every role covered. Use when asked to write, add, fix or run backend tests.
---

# Write tests (Spring Boot)

Tools are settled in `docs/TRD.md` §8: **JUnit 5 + Mockito** for unit tests, **Testcontainers** for integration tests. If `build.gradle` doesn't have them yet (`spring-boot-starter-test`, `spring-security-test`, `spring-boot-testcontainers`, `org.testcontainers:postgresql`, `org.testcontainers:junit-jupiter`, plus the Redis/RabbitMQ containers you need), add them (no package request for backend repos, `packages.md`), and mention them in the PR.

## What goes where

| Kind | Name | Covers | Runs with |
|---|---|---|---|
| Unit | `<Class>Test` | Pure rules: validation helpers, password policy, money conversion, OTP and expiry logic, service branches with mocked repositories and clients | JUnit 5 + Mockito, no Spring context |
| Integration | `<Class>IT` | Each endpoint end to end: HTTP → security → service → real Postgres/Redis/RabbitMQ | `@SpringBootTest` + MockMvc + Testcontainers |

Put tests in the same package as the code they test, under `src/test/java`.

Integration tests extend the repo's `support/IntegrationTest` base class (containers, MockMvc, sign-up and token helpers): one `<Controller>IT` per controller. Reuse its helpers before writing new ones, and add new shared ones there. Test methods say who does what and what happens: `manager_seesOwnBranch`, `withoutToken_returns401`.

## Integration test setup

Create these once per repo and reuse them:

- **`AbstractIT`:**
  - Containers `postgres:17`, Redis and RabbitMQ (only those the service uses), static so all tests share them, wired with `@ServiceConnection` (or `@DynamicPropertySource` for Redis if needed).
  - A `test` profile (`src/test/resources/application-test.yml`) with Consul turned off (`spring.cloud.consul.enabled=false`, `spring.config.import=optional:consul:`), the service's schema and Flyway schema, and `ddl-auto: validate`.
  - Flyway runs the real migrations, so `ddl-auto=validate` is tested too.
  - Clean up between tests: truncate this service's tables and flush Redis in `@BeforeEach`. Don't rely on test order.
- **Fakes for the outside world:** `@MockitoBean` for other services' Feign clients and the S3 client, and a `@TestConfiguration` with `@Primary` beans for Keycloak and SMTP (capture the sent mails). Tests never call real external systems.
- **Signed-in requests:** `spring-security-test`'s `jwt()` post-processor with `sub` = the seeded user's `user_id` (and the issued-at time when testing revocation). The current-user filter then loads the real `users` row, so `is_active`, scope and role are tested for real.
- **Seed helpers:** small builders that insert an owner, a manager per branch, a business with two branches, and so on, using the dictionary's defaults.

## What every endpoint needs

For each endpoint in the plan:

1. **Happy path:** check the status, the envelope (`success = true`, `code = null`), `data` (dictionary field names, snake_case) and the database rows.
2. **Validation:** `400`, `success = false`, `code = VALIDATION_FAILED`, with `data` keyed by the right field.
3. **Every error `code`** in the plan, each with its status and `success = false`.
4. **Roles and scope:**
   - owner, all branches
   - owner, one branch (where it applies)
   - manager of the same branch
   - manager of **another** branch (`404` or `403`, and no data in the body)
   - no token (`401`)
   - deactivated user (`401 ACCOUNT_DEACTIVATED`)
5. **Side effects:**
   - events published (RabbitMQ test listener, or a spy on the publisher)
   - emails captured
   - Redis keys and TTLs
   - `change_logs` / audit events where the flow requires them
6. **Limits and expiries** from the flow: just before, at, and after (cooldowns, attempt caps, link expiry). Control time with an injected `Clock`, not `Thread.sleep`.

Use the `identify-edge-cases` checklist for anything the plan doesn't list.

## Run

```bash
./gradlew test                         # everything (Docker must be running)
./gradlew test --tests '*SignInIT'     # one class
./gradlew test --tests '*SignInIT.locksAfterFiveFailures'
```

A failing test means the code or the test is wrong. Find out which against the flow. Never weaken an assertion to make it pass.
