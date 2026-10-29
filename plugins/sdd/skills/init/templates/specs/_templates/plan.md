# Plan: <Feature title>

**Spec:** `XXX` v<X.Y.Z>, commit `<sha of the commit that approved spec.md>` · **Approved:** <date> by <name>
**Repos:** <repo> (<role>), <repo> (<role>)

<!--
HOW TO WRITE THIS FILE
- The plan says HOW. It never changes WHAT: anything the spec doesn't settle goes under §10 as a question
  and back to /sdd:amend or /sdd:clarify. Never decide it here.
- The **Spec:** commit is what sddtool.py compares against to detect spec drift. Get it with
  `git -C <docs> log -1 --format=%h -- specs/<feature>/spec.md` at approval time.
- Every section item lists the requirement / edge-case IDs it serves. Every live XXX-R and XXX-E must appear
  somewhere in §2–§8 (sddtool.py check enforces this through tasks.md).
- This template is the ONLY definition of a plan's contents (TEAM-RULES §3 points here).
-->

## 1. Scope

- **In:** <spec sections and IDs>
- **Out:** <…>

## 2. Repos and parts

| Repo | Role (agent) | Part | Order |
|---|---|---|---|
| <identity-service> | api-dev | <endpoints, migration> | first: web-ui needs the contract only, not the build |
| web-ui | web-dev | <screens on the mock> | parallel |

## 3. API contract

The contract every repo builds against. Taken from `api/<service>.md` where listed; otherwise marked **new**.

### `POST /path` — new · XXX-R01, XXX-R02

- **Who:** Owner (manager → `403 FORBIDDEN`)
- **Body:** `field` (dictionary `table.field`), …
- **201 CREATED** `data`: <shape>
- **Errors:** `409 <CODE>` (XXX-M01), `400 VALIDATION_ERROR` (fields …)

## 4. Screens, routes and states

| Route | Who | States (loading / empty / error / each status) | IDs |
|---|---|---|---|

## 5. Data

| Table.field (dictionary name) | Read / write | Repo | IDs |
|---|---|---|---|

## 6. Roles and branch scope

<How each repo enforces §2 of the spec: nav, route/layout, data layer, endpoint, query.>

## 7. Files

| Repo | Create / change | Why (IDs) |
|---|---|---|

## 8. Edge cases

| ID | Where it's handled (repo, layer) |
|---|---|

## 9. Packages and verification

- **Packages:** none / <package, why, request drafted (web-ui)>
- **Verification per repo:** <commands>, and per role what to check.

## 10. Questions and conflicts

<Anything the spec doesn't settle. Empty when approved.>

## Changes

| Date | Change | Why | Approved by |
|---|---|---|---|
