---
paths:
  - "src/**"
  - "build.gradle"
  - "docker-compose.yml"
---

# Spring Boot coding standards

Stack and versions are settled in `docs/TRD.md` §2. This file is *how* we write the code.

If the repo already has a class for something below (`ApiResponse`, `GlobalExceptionHandler`, `FeignConfig`, `ModelMapperConfig`, `FileStorageService`, …), extend it. Don't create a second one.

## Packages: by feature

identity-service is the reference: when in doubt, do what it does.

```
com.ledgervision.<service>
├── <feature>/            e.g. auth, business, user, branch
│   ├── controller/       REST controllers (only features with endpoints)
│   ├── dto/              request records and response classes (only features with endpoints)
│   ├── entity/           JPA entities
│   ├── repository/       Spring Data JPA repositories
│   ├── client/           OpenFeign clients to other services (only when the feature calls one)
│   └── service/          service interfaces, plus the helpers they share (<X>ResponseMapper, PasswordPolicy)
│       └── impl/         <Name>ServiceImpl: business rules, @Transactional, role and scope checks
└── common/               config, exception, i18n, response, security, keycloak, mail, otp, storage
                          (moves to ledgervision-common)
```

- **Only the folders a feature needs.** A feature other features call but that has no endpoints of its own (`branch`, `auditlog`, `invitation` in identity-service) has just `entity/`, `repository/` and `service/`.
- **One service interface per area of work**, not one per feature: `auth` has `AuthService`, `SessionService`, `PasswordResetService`, `EmailVerificationService`, and so on. Each is implemented by `<Name>ServiceImpl` in `service/impl/` (`@Service`, `@RequiredArgsConstructor`, `implements <Name>Service`). Inject the **interface**, never the `…Impl`. Services in `common/` (`MailService`, `OtpService`, `FileStorageService`, `TokenRevocationService`) follow the same interface + `impl/` pattern.
- A feature uses another feature's **service interface**, never its repository or `…Impl`. A service that only other features call may take and return entities (`BranchService.createMainBranch(...)` returns a `Branch`). What a controller gets back is always a DTO.
- Controllers never return or accept entities.
- Entities and service interfaces start with a one-line Javadoc naming their dictionary table or flow section (`/** {@code branches} (docs/data-dictionary/business-and-branches.md#branches). */`).

## Lombok

- Entities: `@Getter`, `@Setter`, `@NoArgsConstructor`. **Never `@Data`, `@EqualsAndHashCode` or `@ToString` on entities**: they break with lazy relations and JPA identity.
- Services and components: `@RequiredArgsConstructor` with `private final` fields (constructor injection). No `@Autowired` on fields.
- Request DTOs: Java **records** with Bean Validation whose messages are keys (`@NotBlank(message = "{validation.required}")`, `@Size(max = 50, message = "{validation.max_length}")`) and `@Schema(example = ...)`. Nested parts are nested records (`BusinessSetupRequest.MainBranch`).
- Response DTOs: **classes** with `@Getter`, `@Setter`, `@NoArgsConstructor` (plus `@AllArgsConstructor` on a wrapper), so ModelMapper can fill them. Nested parts are nested `static` classes (`BusinessSetupResponse.BranchResponse`).
- `is_*` columns: the Java field drops the prefix (`active`, `mainBranch`), with `@Column(name = "is_active")` on the entity and `@JsonProperty("is_active")` on the response DTO.
- Logging: `@Slf4j`.

## ModelMapper

- One `ModelMapper` bean in `common/config`, with `MatchingStrategies.STRICT`.
- Map entity → response DTO in the service layer: `modelMapper.map(branch, BranchResponse.class)`.
- A mapping that needs more than matching names gets its own `<X>ResponseMapper` class in `service/`, built on a ModelMapper `TypeMap` (`ProfileResponseMapper`, `MeResponseMapper`), with a unit test.
- **Never map a request DTO straight onto an entity for protected fields**: `user_id`, `business_id`, `branch_id`, `role_id`, `is_active`, `created_at`, money conversions. Set those explicitly in the service.

## JSON and API

- Jackson uses `PropertyNamingStrategies.SNAKE_CASE` globally, so Java `usdEquivalent` is `usd_equivalent` on the wire. Each JSON name must be the dictionary name (`data-dictionary.md`).
- Every path starts with `/api/v1` (`docs/TRD.md` §3a).
- **Every response is the envelope** `ApiResponse { success, code, message, data, timestamp }` (`docs/TRD.md` §3a). `ApiResponse.ok(...)` and `ApiResponse.created(...)` set `code` to the HTTP status name (`OK`, `CREATED`; docs v4.3.0). Never a bare DTO or a different wrapper.
- Controllers: `@RestController`, `@RequestMapping("/api/v1/<resource>")`, `@RequiredArgsConstructor`, injecting the service interfaces and `Messages`. The signed-in user is a parameter, `@AuthenticationPrincipal CurrentUser currentUser`, passed on to the service.
  - `200`: return `ApiResponse<T>` directly: `return ApiResponse.ok(messages.get("user.profile.success"), profileService.get(currentUser));`
  - `201`: `return ResponseEntity.status(HttpStatus.CREATED).body(ApiResponse.created(messages.get("business.setup.success"), ...));`
  - The success message is a `messages.properties` key, `<feature>.<action>.success`.
- API docs: springdoc-openapi. Give each controller a `@Tag` and each endpoint an `@Operation` summary, so the web UI team can read the contract in Swagger UI.
- Status codes: `200` OK, `201` created (no `204`: every endpoint returns the envelope), `400` validation, `401` not signed in / revoked / deactivated, `403` wrong role, `404` not found **or outside the caller's scope**, `409` conflict, `410` expired link, `429` limits and cooldowns.
- Timestamps are ISO-8601 in UTC.

## Errors

- Throw `ApiException(HttpStatus, code, messageKey, args...)` for every expected failure. `code` is a stable UPPER_SNAKE string from the flow or the plan (`EMAIL_ALREADY_REGISTERED`).
- A failure thrown in more than one place gets a private static factory in the `…Impl` (`private static ApiException emailTaken()`). Checks Bean Validation can't do (the password policy) throw `ApiException.validationFailed(fieldErrors)`; extra details go in `.withData(...)`.
- One `@RestControllerAdvice` (`GlobalExceptionHandler`) turns every exception into the envelope with `success = false` and the right HTTP status:
  - `ApiException`: its `code`, and its message from `messages.properties`. `data` is `null`, or the extra details the flow needs (e.g. `retry_after_seconds`).
  - Bean Validation errors become `400 VALIDATION_FAILED`, with `data` = the field errors keyed by the JSON (dictionary) field name, e.g. `user_name`, not `userName`.
  - `AccessDeniedException` becomes `403 ACCESS_DENIED`. Spring MVC errors (unknown path, wrong method) keep their status, with a generic code and message.
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
- **One schema per service** (`docs/TRD.md` §5): this service's tables live only in its schema (`identity`, `sales`, `finance`).
  - In the service's Consul config: the datasource URL has `currentSchema=<schema>`, `spring.flyway.schemas=<schema>` (Flyway creates the schema and keeps its history table there), and `spring.jpa.properties.hibernate.default_schema=<schema>`.
  - Migrate and write only this schema.
- `spring.jpa.hibernate.ddl-auto=validate`. The schema comes from Flyway only. Never `update` or `create`.
- Primary keys are `uuid` (`gen_random_uuid()` default, `UUID` in Java).
- Dictionary `enum` columns become Postgres enum types, mapped with `@Enumerated(EnumType.STRING)` + `@JdbcType(PostgreSQLEnumJdbcType.class)`.
- `timestamp` columns hold UTC (`spring.jpa.properties.hibernate.jdbc.time_zone=UTC`) and map to `Instant`. Use `@CreationTimestamp` and `@UpdateTimestamp` for `created_at` / `updated_at`.
- Money is `numeric` ↔ `BigDecimal`.
- `@ManyToOne(fetch = LAZY)` everywhere. Use fetch joins or projections for lists, never N+1 loops.
- Soft-deleted rows (`deleted_at` set) are excluded in queries unless the flow says otherwise.

## Transactions, other services and events

- `@Transactional` on the `…Impl` methods that write. Keep remote calls (Keycloak, other services, SMTP, S3) out of open transactions. When a remote step must come first, do it before the transaction, run the database part in `transactionTemplate.execute(...)`, and undo the remote step if that fails (`BusinessSetupServiceImpl`: upload the logo, create the business in the template, delete the logo on failure).
- Other services (`docs/TRD.md` §3d):
  - Call them through an **OpenFeign** client in `<feature>/client`, by Consul service name: `@FeignClient(name = "finance-service")`.
  - Every client has a Resilience4j circuit breaker and time limiter (configured in Consul) and a fallback or a clear `ApiException` when the other service is down. Never hang or return a fake success.
  - Auth: during a user request, the shared `FeignConfig` interceptor forwards the user's `Authorization` header. In jobs and message listeners there is no user, so use this service's own Keycloak client-credentials token, and send the `business_id` / `branch_id` scope explicitly.
- Events:
  - Publish to RabbitMQ **after commit** (`@TransactionalEventListener(phase = AFTER_COMMIT)` → `RabbitTemplate`).
  - Payloads are JSON in snake_case, defined in `ledgervision-common` (or `common/event` until then).
  - Consumers must be idempotent.
- Alerts and audit entries for identity-service are events, not direct inserts (`docs/TRD.md` §1a).

## Jobs

- `@Scheduled` + ShedLock `@SchedulerLock(name = "...", lockAtMostFor = "...")` (`docs/TRD.md` §6).
- Jobs only find the due work. Heavy or AI work goes to RabbitMQ.

## Configuration, files, tracing and logging

- **Configuration lives in Consul KV** (`docs/TRD.md` §2):
  - `application.yml` only bootstraps: service name, Consul host and port, `spring.config.import: "consul:"`, discovery and `server.port`.
  - Settings shared by every Spring service go in `config/application/data`. In the repo that's `infra/consul/application.yml`, plus `application-docker.yml` for Docker.
  - This service's own settings go in `config/<service>/data` (`consul/<service>.yml`), and in `config/<service>,docker/data` (`consul/<service>-docker.yml`) for Docker.
  - Put a new setting in the most specific file that fits. Secrets are only `${ENV_VAR}` references. List every variable in `.env.example`, and never commit a real secret.
- **Files** go to S3-compatible storage (RustFS locally) through the shared `FileStorageService`, under this service's folder in the one bucket. Store the object key or URL in the dictionary field (e.g. `businesses.logo`). Never store file bytes in Postgres.
- **Tracing:** Micrometer → Zipkin is already configured. Don't add tracing code by hand. Pass the trace context along on Feign and RabbitMQ calls (the default instrumentation does this).
- Log with ids (`user_id`, `business_id`, trace id). **Never log passwords, tokens, OTP codes, secrets or full request bodies.**

## Tests

- Unit tests: JUnit 5 + Mockito, for services and helpers (`<X>ResponseMapper`, `PasswordPolicy`, an `…Impl`). Name them `<Class>Test`, in the same package as the class.
- Integration tests:
  - One per controller, `<Controller>IT`, extending `support/IntegrationTest` (`@SpringBootTest`, MockMvc, profile `it`, Testcontainers `postgres:17` and Redis via `@ServiceConnection`; add RabbitMQ when a feature needs it). Shared helpers (sign-up, tokens, codes) live in that base class.
  - Test methods say who does what and what happens: `owner_seesProfileWithoutBranch`, `manager_seesOwnBranch`, `withoutToken_returns401`.
  - Tests run without Consul: turn off Consul config and discovery in the `test` profile (`spring.cloud.consul.enabled=false`, `spring.config.import=optional:consul:`), and set the schema and Flyway settings there.
  - Fake the external parts (Keycloak, SMTP, other services' Feign clients, S3). Don't call real ones.
- For every endpoint, test:
  - the happy path,
  - each error code in the plan,
  - **each role**, including a manager trying another branch's data (expect `404` or `403`).
- `./gradlew build` must pass before a PR.
