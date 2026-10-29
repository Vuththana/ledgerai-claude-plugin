---
name: setup-service
description: Set up a LedgerVision Spring Boot service repo for Claude Code and the team rules — .claude/settings.json, CLAUDE.md, .claude/rules/, a CI workflow that runs ./gradlew build on every pull request, and the docs submodule — filled in from docs/TRD.md §1a. Usage /sdd-spring:setup-service [service name].
argument-hint: "[identity-service | sales-service | finance-service | api-gateway]"
disable-model-invocation: true
---

Set up this repo as the LedgerVision service: **$ARGUMENTS** (if empty: work it out in step 1).

The files to install are in this skill's `template/` folder:

| Template file | Goes to |
|---|---|
| `template/settings.json` | `.claude/settings.json` |
| `template/CLAUDE.md` | `CLAUDE.md` |
| `template/rules/*.md` | `.claude/rules/*.md` |
| `template/ci/build.yml` | `.github/workflows/build.yml` |

## 1. Identify the service

- Check this is a Spring Boot repo with a Gradle wrapper (`build.gradle`, `gradlew`). If not, stop and say so.
- Service name: the argument, else `rootProject.name` in `settings.gradle`, else the folder name. Map it to one row of `docs/TRD.md` §1a: identity, sales or finance. `api-gateway` owns no tables. If it's ambiguous, ask.

## 2. Docs submodule

- No `docs/`: run `git submodule add https://github.com/Vuththana/ledgerai-project-docs.git docs`. If cloning fails (it's a private repo), give the user the command to run with `! <command>` and wait.
- `docs/` exists: report its version (`git -C docs log -1 --format='%h %s'`). If it's older than the latest `VERSION.md` entry on GitHub, suggest `/sdd:sync-docs`.
- Read `docs/TRD.md` (§1a, §2, §3), `docs/specs/README.md` and, for features not migrated yet, `docs/flow/README.md`. Everything you fill in below comes from them.

## 3. Install the files

For each template file:

- **Target missing:** copy it.
- **Target exists:** never overwrite it silently. Show what the template adds or changes, and ask whether to merge. Keep anything repo-specific the user already has.

## 4. Fill the placeholders

Replace every `<...>` in the installed `CLAUDE.md` and `.claude/rules/project.md`:

| Placeholder | Source |
|---|---|
| service name, display name | `docs/TRD.md` §1a |
| features and their specs | `docs/TRD.md` §1a + `docs/specs/README.md` (and `docs/flow/README.md` for unmigrated ones) |
| owned tables | `docs/TRD.md` §1a |
| base package | the existing `src/main/java` package, else `com.ledgervision.<service>` |
| port | `docs/TRD.md` §1b; if `server.port` in `application.yml` differs, report it |
| schema | the service's schema in `docs/TRD.md` §1a (`identity`, `sales`, `finance`) |
| compose command | the repo's own `docker-compose.yml`. The shared infrastructure is started from identity-service's `infra/` (`rules/infrastructure.md`) |
| events published / consumed | `docs/TRD.md` §1a rules (e.g. alerts and audit events). If nothing is decided, write "none yet" |
| extra compose services | none: shared containers live only in identity-service's `infra/` (`docs/TRD.md` §1b) |

Then delete the template comment at the top of `CLAUDE.md`. **Don't guess:** if a value isn't in the docs or the repo, ask.

## 5. Compare the repo with the TRD

Read `build.gradle`, `settings.gradle`, `gradle/wrapper/gradle-wrapper.properties`, `application.yml`, the Consul config files (`consul/*.yml`, `infra/consul/*.yml`) and the compose files. Report each difference from `docs/TRD.md` §2–§5:

- Java version, Spring Boot version, Groovy DSL
- Starters and libraries: JPA, **Flyway** (`flyway-core`, `flyway-database-postgresql`), PostgreSQL driver, Redis, **AMQP (RabbitMQ, not Kafka)**, Consul discovery + config, OpenFeign, Resilience4j, OAuth2 resource server, validation, Lombok, ModelMapper, AWS SDK S3, Micrometer tracing + Zipkin, springdoc, ShedLock, **Testcontainers** (+ `spring-boot-testcontainers`)
- Config: `ddl-auto: validate` (not `update`), schema settings, Flyway schema, Jackson `SNAKE_CASE`, UTC time zone
- Compose: in identity-service, `infra/` has `postgres:17`, RabbitMQ (not Kafka) and Mailpit. In any other service, the compose file has **only** the service and its Consul seed job on the external network `ledgervision-net`, with no shared containers and no copy of `infra/` (`docs/TRD.md` §1b)
- Port and Consul name match `docs/TRD.md` §1b and the gateway's routes
- `ApiResponse` has a `code` field, and `GlobalExceptionHandler` follows `spring.md` § Errors
- Package structure: by feature (`spring.md` § Packages), each service an interface in `service/` with its `…ServiceImpl` in `service/impl/`

**Don't change `build.gradle` here.** List the missing dependencies for the user. No package request is needed for backend repos (`.claude/rules/packages.md`): they're added by the feature that first needs them.

## 6. Report

- Files created, merged, or skipped.
- Placeholders still open, and why.
- Differences from the TRD, and the dependencies still missing.
- **Make CI required** on `dev` (where pull requests go) and `main` (the repo owner does this once, on GitHub). Until then the workflow only reports; it doesn't block merges:
  ```bash
  for b in dev main; do gh api -X PUT repos/<owner>/<repo>/branches/$b/protection --input - <<'EOF'
  {"required_status_checks":{"strict":true,"contexts":["build"]},"enforce_admins":true,
   "required_pull_request_reviews":{"required_approving_review_count":1},"restrictions":null}
  EOF
  done
  ```
  Branch protection on a **private** repo needs a paid GitHub plan (Pro, Team or an organization plan); on the free plan, say so and suggest making the check a team rule in the meantime.
- Next step: `/sdd:status`, then `/sdd:plan <feature>` for the first approved feature.

Don't commit unless the user asks.
