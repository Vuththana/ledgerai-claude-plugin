---
name: setup-service
description: Set up a LedgerVision Spring Boot service repo for Claude Code and the team rules — .claude/settings.json, CLAUDE.md, .claude/rules/ and the docs submodule — filled in from docs/TRD.md §1a. Usage /springboot-dev:setup-service [service name].
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

## 1. Identify the service

- Check this is a Spring Boot repo with a Gradle wrapper (`build.gradle`, `gradlew`). If not, stop and say so.
- Service name: the argument, else `rootProject.name` in `settings.gradle`, else the folder name. Map it to one row of `docs/TRD.md` §1a: identity, sales or finance. `api-gateway` owns no tables. If it's ambiguous, ask.

## 2. Docs submodule

- No `docs/`: run `git submodule add https://github.com/Vuththana/ledgerai-project-docs.git docs`. If cloning fails (it's a private repo), give the user the command to run with `! <command>` and wait.
- `docs/` exists: report its version (`git -C docs log -1 --format='%h %s'`). If it's older than the latest `VERSION.md` entry on GitHub, suggest `/ledgerai:sync-project-specs`.
- Read `docs/TRD.md` (§1a, §2, §3) and `docs/flow/README.md`. Everything you fill in below comes from them.

## 3. Install the files

For each template file:

- **Target missing:** copy it.
- **Target exists:** never overwrite it silently. Show what the template adds or changes, and ask whether to merge. Keep anything repo-specific the user already has.

## 4. Fill the placeholders

Replace every `<...>` in the installed `CLAUDE.md` and `.claude/rules/project.md`:

| Placeholder | Source |
|---|---|
| service name, display name | `docs/TRD.md` §1a |
| features and their flow files | `docs/TRD.md` §1a + `docs/flow/README.md` |
| owned tables | `docs/TRD.md` §1a |
| base package | the existing `src/main/java` package, else `com.ledgervision.<service>` |
| port | `server.port` in `application.yml` / `application.properties`, else ask |
| Flyway history table | `flyway_schema_history_<service>` (`docs/TRD.md` §5) |
| events published / consumed | `docs/TRD.md` §1a rules (e.g. alerts and audit events). If nothing is decided, write "none yet" |
| extra compose services | only what this service needs, from the TRD |

Then delete the template comment at the top of `CLAUDE.md`. **Don't guess:** if a value isn't in the docs or the repo, ask.

## 5. Compare the repo with the TRD

Read `build.gradle`, `settings.gradle`, `gradle/wrapper/gradle-wrapper.properties` and `application.yml`, and report each difference from `docs/TRD.md` §2–§5:

- Java version, Spring Boot version, Groovy DSL
- Starters and libraries: JPA, Flyway, PostgreSQL driver, Redis, AMQP, Consul discovery, OAuth2 resource server, validation, Lombok, ModelMapper, ShedLock, Testcontainers
- Flyway history table, `ddl-auto=validate`, Jackson `SNAKE_CASE`, UTC time zone
- Package structure (by feature)

**Don't change `build.gradle`.** Missing dependencies need a package request (`.claude/rules/packages.md`), so list them for the user, and offer the `manage-dependencies` skill to draft the requests.

## 6. Report

- Files created, merged, or skipped.
- Placeholders still open, and why.
- Differences from the TRD, and the package requests needed.
- Next step: `/ledgerai:document-feature <feature>` for the first feature.

Don't commit unless the user asks.
