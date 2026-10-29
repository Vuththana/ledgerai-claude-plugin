---
name: check-secrets
description: Before every git push in a LedgerVision repo (web-ui, a Spring Boot service, ai-service), scan the commits about to be pushed for hardcoded secrets, tokens, keys, URLs, hosts, ports and credentials — plus secrets in NEXT_PUBLIC_ variables and secrets with a fallback — and tell the user each one must go in the .env. Use whenever you are about to run `git push`, or when asked to check for hardcoded values or secrets.
---

# Check for hardcoded values before a push

Run this **before** `git push`, every time. If it finds anything, **don't push**: report and wait for the user. It doesn't replace the user's go-ahead for the push.

**Never** open `.env`, `.env.local`, `infra/.env` or any `.env*` except `.env.example`: they hold the real values.

## 1. What is about to be pushed

```bash
git fetch -q origin
BASE=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo origin/dev)   # code repos work on dev
git log --oneline "$BASE"..HEAD
git diff "$BASE"..HEAD --stat
git diff "$BASE"..HEAD -U0        # only added (+) lines matter
```

A value already on the remote isn't part of this push: list it at the end as "already pushed", don't block on it.

## 2. What counts — every stack

| Kind | Examples |
|---|---|
| **Secret** | passwords, client secrets, API keys, tokens, private keys (`-----BEGIN`), `AKIA…`, `ghp_…`, `sk-…`, JWTs (`eyJ…`) |
| **Secret with a fallback** | `process.env.X ?? "dev-secret"`, `${DB_PASSWORD:qwer}`, `os.getenv("KEY", "changeme")` — a missing value must fail, not fall back to a known one |
| **URL, host or port** | `http://localhost:8080`, `http://rustfs:9000`, `host.docker.internal`, an IP, another service's origin |
| **Account or identity** | OAuth client IDs, realm or bucket names, real email addresses used as config |

**Never findings:** tests, `qa-reports/`, `docs/`, `*.md`, comments, `.env.example` placeholders, values already read from the environment (except a secret with a fallback), standard constants (namespaces, schema URLs, MIME types, header names, public doc links).

## 3. Per stack

Find the stack as in `/sdd:build` (`package.json` with `next` → web-ui; `build.gradle` with Spring Boot → service; `pyproject.toml` with `fastapi` → ai-service).

**web-ui** — scan `src/**`, `next.config.*`, `middleware.*` / `proxy.*`, `package.json` scripts, shell and CI scripts. Skip `src/lib/mock/**` (fake data), relative app routes, `public/` paths.
- A secret → server-only `process.env.NAME`, never `NEXT_PUBLIC_`. **A secret in `NEXT_PUBLIC_` is always a finding**: Next.js ships it to the browser.
- Other values → `process.env.NAME` in server code (the BFF talks to the backend), `NEXT_PUBLIC_NAME` only if a client component needs it and it's safe to show. Reuse `API_BASE_URL`, `MOCK_API` etc.
- Remind: restart `pnpm dev` after `.env` changes; `NEXT_PUBLIC_` is fixed at build time.

**Spring Boot service** — scan `src/main/**`, `src/main/resources/*.yml|*.properties`, `consul/*.yml`, `infra/consul/*.yml` (identity-service holds the shared infra), compose files, `Dockerfile`, scripts, `build.gradle`. Skip `src/test/**`, `application-test.yml`, `application-it.yml`, `@Schema(example=…)`, `lb://` names and `@FeignClient(name=…)`.
- A secret → `${VAR}` with **no** default. Anything else → `${VAR:local-default}` (compose: `${VAR:-local-default}`). A literal in Java → a config property reading `${VAR}`. Rule: `spring.md` → Configuration.
- List it in `.env.example` (service settings) or `infra/.env.example` (shared, identity-service only). Shared Consul config → remind to re-seed (`consul-seed` / `consul-seed-shared`).

**ai-service** — scan `app/**` (or the package root), `pyproject.toml`, compose, `Dockerfile`. Skip `tests/**`.
- Read settings through the app's settings object (`pydantic-settings`) from env; a secret has no default. LLM provider keys are always secrets.

For every stack: an UPPER_SNAKE name that says what it is, reuse existing variables, add it to `.env.example` with a comment and a safe placeholder (never the real value).

## 4. Report

> ⚠️ Found N hardcoded value(s) in the commits about to be pushed. **These must be put in the .env** before pushing:

| # | File:line | Commit | Value | Kind | Put in .env as | Replace with |
|---|---|---|---|---|---|---|

Mask secrets (first 3 characters: `sk-***`). Then ask: fix now (new commit, then check again), or push anyway.

Nothing found: "No hardcoded values in the N commits to push", with the files checked, then go on with the push the user approved.
