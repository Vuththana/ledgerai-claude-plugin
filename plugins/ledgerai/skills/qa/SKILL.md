---
name: qa
description: QA a built LedgerVision feature end to end against its approved flow, in three kinds (correctness, validation, misuse). In web-ui it tests the app in the browser; in a Spring Boot service it tests the API through Swagger UI. Writes a report to qa-reports/ and returns a short summary.
argument-hint: <feature> [base-url]
disable-model-invocation: true
---

# QA: $0

## 1. Pick the tester for this repo

| This repo has | Tester (agent) | Default base URL |
|---|---|---|
| `package.json` with `next` (web-ui) | `website-dev:qa-web` | `http://localhost:3000` |
| `build.gradle` with `org.springframework.boot` (a service) | `springboot-dev:qa-api` | `http://localhost:<server.port>` from `src/main/resources/application.yml` |
| `pyproject.toml` with `fastapi` (ai-service) | `fastapi-dev:qa-ai` (placeholder) | `http://localhost:8000` (`docs/TRD.md` §1b) |

Use **$1** as the base URL if it's given. If the repo is none of these, or the tester's plugin isn't enabled here, stop and say which plugin to enable (`website-dev`, `springboot-dev` or `fastapi-dev`, see the plugin README).

## 2. Run it

Start the tester with the Agent tool, `subagent_type` set to the agent from the table, and this prompt:

> QA the **$0** feature at **<base-url>**. Follow the preloaded `qa-method` skill: find the spec, write every scenario first, run them, write the report to `qa-reports/`, and reply with the summary only.

Run one tester at a time: the Playwright browser is shared.

## 3. Reply

Pass on the tester's reply as it is: the counts table, one line per ❌ and per ⚠️, and the report path. Don't run anything again and don't add a summary of your own.
