# Technical Requirements (TRD)

**Status:** 📝 Draft. Settle each 📝 and ❓ with the team; when everything is ✅, this status flips.

The technical requirements every <Project> repo builds to. Feature behaviour lives in [`specs/`](specs/README.md), fields in the [data dictionary](data-dictionary/README.md).

**Legend:** ✅ settled · 📝 proposed · ❓ open

## 1. System overview

### 1a. Parts and data ownership

Each table is written by exactly one service. Other services read it through that service's API or events.

| Part | Repo | Does | Owns tables | Status |
|---|---|---|---|---|
<parts>

## 2. Technology stack

| Area | Choice | Status |
|---|---|---|
<stack>

## 3. API

| Requirement | Status |
|---|---|
| REST with JSON bodies; every path starts with `/api/v1` | 📝 |
| Field names in payloads are the dictionary names (snake_case) | 📝 |
| One response envelope for every endpoint: `{ success, code, message, data, timestamp }` (see [`api/README.md`](api/README.md)) | 📝 |
| Every request is scoped on the server to what the caller may see; scope is never trusted from the client | 📝 |
| Pagination, filter and sort parameters | ❓ |

## 4. Security

| Requirement | Status |
|---|---|
| Sign-in method and identity provider | ❓ |
| Role and scope come from the user's record on the server, never from token claims or the request | 📝 |
| Secrets only in environment variables, listed in `.env.example`; never committed | 📝 |

## 5. Data

| Requirement | Status |
|---|---|
| Database and how schemas are split | ❓ |
| Primary keys `uuid`; timestamps stored in UTC; money as `numeric` (never float) | 📝 |
| Schema changes only through migrations; an applied migration is never edited | 📝 |

## 6. Background jobs

| Job | Schedule | Owner | Status |
|---|---|---|---|

## 7. Non-functional requirements

| Requirement | Status |
|---|---|
| Supported browsers / devices | ❓ |
| Accessibility target | ❓ |
| Languages | ❓ |

## 8. Delivery and environments

| Requirement | Status |
|---|---|
| CI runs the build and all tests on every pull request; a failing build can't merge | 📝 |
| Hosting | ❓ |

## 9. Open questions

Numbered; answered ones keep their number.
