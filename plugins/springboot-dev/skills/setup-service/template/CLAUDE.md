# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

<!-- Template from ledgerai-claude-plugin/templates/backend. Replace every <...> placeholder, then delete this comment. -->

LedgerVision **<service-name>** (<Service display name, e.g. "Identity & Notification">): a Spring Boot service of an AI-powered financial copilot for SME retail stores (multi-branch, USD/KHR). The project, its features and the team's rules are in `.claude/rules/project.md`.

## Where things are defined

| Layer | Where | Holds |
|---|---|---|
| **What to build** (source of truth) | `docs/` (the `ledgerai-project-docs` submodule): `docs/flow/`, `docs/data-dictionary/`, `docs/TRD.md`, `docs/TEAM-RULES.md` | Behaviour, messages, roles, every table and field, technical requirements, which service owns what |
| **Project instructions** | this file | Commands, stack, architecture |
| **Rules: coding standards and constraints** | `.claude/rules/` | Team rules (always loaded) and coding standards (loaded when matching files are touched) |
| **Workflows** | the `ledgerai` plugin | Step-by-step tasks: `/ledgerai:document-feature`, `/ledgerai:review-feature`, `/ledgerai:sync-project-specs`, ... |

Don't restate the docs in code, rules or skills. Point to the flow section instead (e.g. `docs/flow/authentication.md` §6c). If the docs don't say something, ask.

## Commands

```bash
# Shared infrastructure (Postgres, Keycloak, Consul, Redis, ..., api-gateway): one set for all services,
# started from identity-service's infra/. How: .claude/rules/infrastructure.md
docker compose up -d consul-seed   # load this service's config into Consul (after every Consul restart)
./gradlew bootRun             # run the service, http://localhost:<port> (reads .env)
./gradlew build               # compile + all tests (integration tests need Docker for Testcontainers)
./gradlew test --tests '<pattern>'   # one test class or method
```

## Stack

Java 21, Spring Boot 3.5.16, Spring Cloud, Gradle (Groovy DSL), Spring Data JPA + Flyway, PostgreSQL 17 (one database, schema `<schema>`), Redis, RabbitMQ, Consul (discovery + KV config), OpenFeign + Resilience4j, Keycloak (resource server), S3-compatible storage (RustFS), Zipkin, springdoc-openapi, Lombok, ModelMapper, JUnit 5 + Mockito + Testcontainers. Settled in `docs/TRD.md` §2. Coding standards: `.claude/rules/spring.md`.

## This service

- **Features:** <features from `docs/TRD.md` §1a, with their flow files>
- **Owns tables:** <tables from `docs/TRD.md` §1a>. Only these get migrations and writes here.
- **Base package:** `com.ledgervision.<service>`
- **Database schema:** `<schema>` (Flyway migrates it and keeps its history there)
- **Configuration:** Consul KV. Shared: `config/application/data`, from identity-service's `infra/consul/application.yml`. This service: `consul/<service>.yml` → `config/<service>/data` (+ `-docker`)
- **Consul service name:** `<service-name>`, port `<port>` (`docs/TRD.md` §1b). Behind the gateway at `/api/v1/<route>/**`.
- **Events:** publishes <...> · consumes <...>

## Architecture

- Package by feature: `com.ledgervision.<service>.<feature>.{controller,service,repository,dto,entity}`. Each service is an interface in `service/` with its `<Name>ServiceImpl` in `service/impl/`; inject the interface. Cross-cutting code in `com.ledgervision.<service>.common` until it moves to `ledgervision-common`.
- Every request: the JWT is validated (Keycloak), then the current user is loaded from `users`. Role, `business_id` and `branch_id` come from that row, never from token claims (`docs/TRD.md` §3b).
- Every response is the envelope `ApiResponse { success, code, message, data, timestamp }` (`docs/TRD.md` §3a).
- Other services are reached through OpenFeign clients by Consul name (the user's token forwarded; client credentials in jobs and listeners), or through RabbitMQ events (`docs/TRD.md` §3d).
