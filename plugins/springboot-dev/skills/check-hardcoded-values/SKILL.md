---
name: check-hardcoded-values
description: Before every git push in a Spring Boot service repo, scan the commits about to be pushed for hardcoded values (passwords, secrets, tokens, keys, URLs, hosts, ports, credentials) and tell the user each one must be put in the .env. Use whenever you are about to run `git push`, or when asked to check for hardcoded values or secrets.
---

# Check for hardcoded values before a push (Spring Boot service)

Run this **before** `git push`, every time. If it finds anything, **don't push**: report the findings and wait for the user.

The rule behind it is in `spring.md` (Configuration): settings live in Consul KV files, and secrets are only `${ENV_VAR}` references, listed in `.env.example`.

## 1. What is about to be pushed

```bash
git fetch -q origin
BASE=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo origin/main)
git log --oneline "$BASE"..HEAD          # the commits
git diff "$BASE"..HEAD --stat            # the files
git diff "$BASE"..HEAD -U0               # the lines; only added lines (+) matter
```

Check only what these commits **add**. A value that was already on the remote is not part of this push. Mention it at the end as "already pushed", but don't let it block the push.

## 2. What counts as hardcoded

Look at every added line in:
- `src/main/**`
- `src/main/resources/*.yml|*.properties`
- `consul/*.yml`, and `infra/consul/*.yml` in identity-service, which holds the shared infrastructure
- `docker-compose.yml`, `infra/docker-compose.yml`, `Dockerfile`
- scripts and `build.gradle`

| Kind | Examples | Must become |
|---|---|---|
| **Secret** | passwords, client secrets, API keys, tokens, access/secret keys, private keys (`-----BEGIN`), `AKIA…`, `ghp_…`, `sk-…`, JWTs (`eyJ…`) | `${VAR}` with **no** default |
| **Secret with a fallback** | `${DB_PASSWORD:qwer}`, `${KEYCLOAK_CLIENT_SECRET:dev-secret}` | `${VAR}`: drop the fallback, so a missing value fails at startup instead of using a known password |
| **URL, host or port** | `http://localhost:9090`, `http://rustfs:9000`, `host.docker.internal`, an IP, `smtp.gmail.com:587` in config | `${VAR:local-default}` (in compose files: `${VAR:-local-default}`) |
| **Account or identity** | usernames, real email addresses, bucket or realm names that differ per environment | `${VAR:local-default}` |
| **In Java** | any of the above as a string literal in `src/main/**` | a config property (Consul yml) that reads `${VAR}` |

**Not findings** (skip them):
- tests: `src/test/**`, `application-test.yml`, `application-it.yml`
- docs and comments, Javadoc, `README.md`, `*.md`
- `.env.example` placeholders
- values already written as `${VAR}` or `${VAR:default}` (except a secret with a fallback)
- `@Schema(example = …)` values
- Consul service names in `lb://` routes and `@FeignClient(name = …)`: discovery resolves them
- standard constants: XML namespaces, schema URLs, MIME types, HTTP header names

**Never** open `.env` or `infra/.env`: they hold the real secrets. Read only the `.env.example` files.

## 3. The fix for each finding

1. Replace the value with `${VAR}` (a secret) or `${VAR:local-default}` (anything else).
   - Use an UPPER_SNAKE name that says what the value is.
   - Reuse an existing variable if one exists (check `.env.example`, e.g. `KEYCLOAK_PUBLIC_URL`, `DB_PASSWORD`).
2. List the variable in the right `.env.example`:
   - `.env.example`: this service's own settings (`consul/*.yml`, `docker-compose.yml`).
   - `infra/.env.example` (identity-service only): the shared settings (`infra/consul/*.yml`, `infra/docker-compose.yml`).

   Give each one a comment and a safe placeholder, never the real value.
3. If Docker needs a different value, say where it is set: the compose file's `environment:`, or `consul/*-docker.yml`.
4. If the value is in shared Consul config, remind the user to re-seed it (`consul-seed` / `consul-seed-shared`).

## 4. Report

If there are findings, **stop before pushing** and tell the user:

> ⚠️ Found N hardcoded value(s) in the commits about to be pushed. **These must be put in the .env** before pushing:

| # | File:line | Value | Kind | Put in .env as | Replace with |
|---|---|---|---|---|---|
| 1 | `consul/sales-service.yml:12` | `http://localhost:9090` | URL | `KEYCLOAK_PUBLIC_URL` | `${KEYCLOAK_PUBLIC_URL:http://localhost:9090}` |

- Mask secrets in the report: show only the first 3 characters (`qwe***`).
- Name the commit that adds each value.
- Then ask: fix them now (a new commit, then check again), or push anyway.

If nothing is found, say "No hardcoded values in the N commits to push" and list the files checked, then continue with the push the user asked for.

This check doesn't replace the user's go-ahead for a push. Pushing still needs their explicit approval.
