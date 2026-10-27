---
paths:
  - "src/**"
  - "build.gradle"
  - "docker-compose.yml"
---

# Spring Boot coding standards

Stack and versions are settled in `docs/TRD.md` §2. This file is *how* we write the code.

## Packages: by feature

```
com.ledgervision.<service>
├── <feature>/            e.g. auth, branch, notification
│   ├── controller/       REST controllers only: validate, call the service, return DTOs
│   ├── service/          business rules, @Transactional, role and scope checks
│   ├── repository/       Spring Data JPA repositories
│   ├── dto/              request and response DTOs
│   └── entity/           JPA entities
└── common/               error handling, security, config, mail, events (moves to ledgervision-common)
```

- A feature uses another feature's **service**, never its repository.
- Controllers never return or accept entities. Always DTOs.

## Lombok

- Entities: `@Getter`, `@Setter`, `@NoArgsConstructor`. **Never `@Data`, `@EqualsAndHashCode` or `@ToString` on entities**: they break with lazy relations and JPA identity.
- Services and components: `@RequiredArgsConstructor` with `private final` fields (constructor injection). No `@Autowired` on fields.
- DTOs: `@Getter` / `@Setter` / `@NoArgsConstructor` (or `@Data`).
- Logging: `@Slf4j`.

## ModelMapper

- One `ModelMapper` bean in `common/config`, with `MatchingStrategies.STRICT`.
- Map entity → response DTO in the service layer.
- **Never map a request DTO straight onto an entity for protected fields**: `user_id`, `business_id`, `branch_id`, `role_id`, `is_active`, `created_at`, money conversions. Set those explicitly in the service.

## JSON and API

- Jackson uses `PropertyNamingStrategies.SNAKE_CASE` globally, so Java `usdEquivalent` is `usd_equivalent` on the wire. Each JSON name must be the dictionary name (`data-dictionary.md`).
- Every path starts with `/api/v1` (`docs/TRD.md` §3a).
- Status codes: `201` created, `204` no body, `400` validation, `401` not signed in / revoked / deactivated, `403` wrong role, `404` not found **or outside the caller's scope**, `409` conflict, `410` expired link, `429` limits and cooldowns.
- Timestamps are ISO-8601 in UTC.

## Errors

- Throw `ApiException(HttpStatus, code, messageKey, args...)` for every expected failure. `code` is a stable UPPER_SNAKE string from the flow or the plan (`EMAIL_ALREADY_REGISTERED`).
- One `@RestControllerAdvice` turns everything into `{ status, code, message, field_errors }` (`docs/TRD.md` §3a):
  - Bean Validation errors become `400 VALIDATION_FAILED`, with `field_errors` keyed by the JSON (dictionary) field name.
  - Any unexpected exception becomes `500 INTERNAL_ERROR` with a generic message. The details go to the log only.
- `message` comes from `messages.properties` (`language.md`). Never put exception text, SQL or stack traces in a response.

## Security and scope

- The service is an OAuth2 resource server: JWT from Keycloak (issuer and audience from config).
- A filter loads the current user from `users` by the token's `sub` on **every request**. It rejects:
  - a missing or `deleted_at` user,
  - `is_active = false` (`401 ACCOUNT_DEACTIVATED`),
  - a token issued before the Redis revocation time (`401 SESSION_REVOKED`).

  See `docs/TRD.md` §3b and `docs/flow/authentication.md` §11.
- Take role, `business_id` and `branch_id` **from that user row**, never from token claims or the request.
- Every query on a scoped table filters by `business_id`, and by `branch_id` for `BRANCH_MANAGER`. Put the scope in the repository method (`findByIdAndBusinessId`), not in a later `if`.
- Role checks go in the service (or `@PreAuthorize`). Hiding a button in the UI is not a check.

## Persistence

- Migrations: Flyway, `src/main/resources/db/migration/V<n>__<description>.sql`. **Never edit a migration that has run anywhere.** Add a new one.
- Shared database:
  - `spring.flyway.table=flyway_schema_history_<service>` and `spring.flyway.baseline-on-migrate=true`.
  - Migrate only the tables this service owns (`docs/TRD.md` §1a).
- `spring.jpa.hibernate.ddl-auto=validate`. The schema comes from Flyway only.
- Primary keys are `uuid` (`gen_random_uuid()` default, `UUID` in Java).
- Dictionary `enum` columns become Postgres enum types, mapped with `@Enumerated(EnumType.STRING)` + `@JdbcType(PostgreSQLEnumJdbcType.class)`.
- `timestamp` columns hold UTC (`spring.jpa.properties.hibernate.jdbc.time_zone=UTC`) and map to `Instant`. Use `@CreationTimestamp` and `@UpdateTimestamp` for `created_at` / `updated_at`.
- Money is `numeric` ↔ `BigDecimal`.
- `@ManyToOne(fetch = LAZY)` everywhere. Use fetch joins or projections for lists, never N+1 loops.
- Soft-deleted rows (`deleted_at` set) are excluded in queries unless the flow says otherwise.

## Transactions, other services and events

- `@Transactional` on service methods that write. Keep remote calls (Keycloak, other services, SMTP) out of open transactions where possible. If a remote step and a DB step must both succeed, undo the remote one when the DB step fails.
- Other services:
  - Call them with a `@LoadBalanced` `RestClient` (Consul discovery) and this service's own Keycloak client-credentials token.
  - Always send the `business_id` / `branch_id` scope explicitly (`docs/TRD.md` §3d).
- Events:
  - Publish to RabbitMQ **after commit** (`@TransactionalEventListener(phase = AFTER_COMMIT)` → `RabbitTemplate`).
  - Payloads are JSON in snake_case, defined in `ledgervision-common` (or `common/event` until then).
  - Consumers must be idempotent.
- Alerts and audit entries for identity-service are events, not direct inserts (`docs/TRD.md` §1a).

## Jobs

- `@Scheduled` + ShedLock `@SchedulerLock(name = "...", lockAtMostFor = "...")` (`docs/TRD.md` §6).
- Jobs only find the due work. Heavy or AI work goes to RabbitMQ.

## Configuration and logging

- `application.yml` reads everything environment-specific as `${ENV_VAR:local-default}`. List every variable in `.env.example`. Never commit a real secret.
- Log with ids (`user_id`, `business_id`, request id). **Never log passwords, tokens, OTP codes, secrets or full request bodies.**

## Tests

- Unit tests: JUnit 5 + Mockito, for services and helpers. Name them `<Class>Test`.
- Integration tests:
  - `@SpringBootTest` + Testcontainers (`postgres:17`, Redis, RabbitMQ) via `@ServiceConnection`. Name them `<Class>IT`.
  - Fake the external parts (Keycloak, SMTP, other services). Don't call real ones.
- For every endpoint, test:
  - the happy path,
  - each error code in the plan,
  - **each role**, including a manager trying another branch's data (expect `404` or `403`).
- `./gradlew build` must pass before a PR.
