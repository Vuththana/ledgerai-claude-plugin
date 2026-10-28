---
name: check-hardcoded-values
description: Before every git push in web-ui, scan the commits about to be pushed for hardcoded values (API and Keycloak URLs, hosts, ports, client IDs, secrets, tokens, keys) and secrets in NEXT_PUBLIC_ variables, and tell the user each one must be put in the .env. Use whenever you are about to run `git push`, or when asked to check for hardcoded values or secrets.
---

# Check for hardcoded values before a push (web-ui)

Run this **before** `git push`, every time. If it finds anything, **don't push**: report the findings and wait for the user.

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

Look at every added line in `src/**` (except the mock fixtures below), `next.config.*`, `middleware.*` / `proxy.*`, `package.json` scripts and any shell or CI scripts.

| Kind | Examples | Must become |
|---|---|---|
| **Secret** | passwords, client secrets, API keys, tokens, cookie or session secrets, private keys (`-----BEGIN`), `AKIA…`, `ghp_…`, `sk-…`, JWTs (`eyJ…`) | a **server-only** `process.env.NAME`, never `NEXT_PUBLIC_` |
| **Secret in `NEXT_PUBLIC_`** | `NEXT_PUBLIC_CLIENT_SECRET`, `NEXT_PUBLIC_API_KEY` | a server-only variable. Next.js copies every `NEXT_PUBLIC_` value into the browser's JavaScript, so anyone can read it |
| **Secret with a fallback** | `process.env.SESSION_SECRET ?? "dev-secret"`, `\|\| "changeme"` | no fallback: fail clearly when it's missing |
| **URL, host or port** | `http://localhost:8080`, the gateway or Keycloak address, `http://localhost:9000/...`, an IP, another service's origin | `process.env.NAME` (server code) or `NEXT_PUBLIC_NAME` (only if the browser needs it and it isn't secret), with the local value in `.env.example` |
| **Account or identity** | Google or other OAuth client IDs, realm names, real email addresses used as config | `process.env.NAME` / `NEXT_PUBLIC_NAME` |

**Not findings** (skip them):
- mock fixtures and seeded mock accounts: `src/lib/mock/**` (fake data, not configuration)
- tests, `qa-reports/**`, `docs/**`, `package-requests/**`, `*.md`, comments
- `.env.example` placeholders
- values already read from `process.env` (except a secret with a fallback or a secret in `NEXT_PUBLIC_`)
- relative app routes (`/sign-in`, `/api/...` of this app), `public/` asset paths
- standard constants: XML or SVG namespaces, schema URLs, MIME types, HTTP header names, links to public docs

**Never** open `.env`, `.env.local` or any other `.env*` file except `.env.example`: they hold the real values.

## 3. The fix for each finding

1. Read the value from `process.env.NAME` in server code (route handlers, server components, server actions, `src/lib/api`). The BFF holds the tokens and talks to the backend, so most values belong on the server.
   - Use `NEXT_PUBLIC_NAME` only if a client component really needs the value and it's safe for anyone to see.
   - Reuse an existing variable if there is one (e.g. `API_BASE_URL`, `MOCK_API`).
2. List the variable in `.env.example`, with a comment and a safe placeholder (the local value, never a real secret).
3. Remind the user:
   - Restart `pnpm dev` after changing `.env`.
   - `NEXT_PUBLIC_` values are fixed at build time, so a deployed build needs them when it's built.

## 4. Report

If there are findings, **stop before pushing** and tell the user:

> ⚠️ Found N hardcoded value(s) in the commits about to be pushed. **These must be put in the .env** before pushing:

| # | File:line | Value | Kind | Put in .env as | Replace with |
|---|---|---|---|---|---|
| 1 | `src/lib/api/client.ts:12` | `http://localhost:8080` | URL | `API_BASE_URL` | `process.env.API_BASE_URL` |

- Mask secrets in the report: show only the first 3 characters (`sk-***`).
- Name the commit that adds each value.
- Then ask: fix them now (a new commit, then check again), or push anyway.

If nothing is found, say "No hardcoded values in the N commits to push" and list the files checked, then continue with the push the user asked for.

This check doesn't replace the user's go-ahead for a push. Pushing still needs their explicit approval.
