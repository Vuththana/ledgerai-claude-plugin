---
name: mock-api-layer
description: How LedgerVision web repos get data before the backend exists — types from the data dictionary, mock fixtures and fake services, and the lib/api functions pages call, with role and branch filtering. Use when adding or changing a domain's types, mock data, API functions, or any page that loads or saves data.
---

# Mock API layer

There is no backend yet. Everything is built against an in-memory mock that has the same shape as the future REST API. Swapping to the real backend later must only touch `src/lib/api/`.

## The three layers

```
page / feature component
        │  calls
        ▼
src/lib/api/<domain>.ts     async functions; role + branch filtering happens here
        │  calls
        ▼
src/lib/mock/               seed fixtures + in-memory fake services
        │  typed by
        ▼
src/lib/types/<domain>.ts   mirrors one docs/data-dictionary/<domain>.md file
```

- **Pages and components never import `src/lib/mock`.** Only `src/lib/api` does.
- Every `lib/api` function is `async` and returns plain data, so it's a drop-in for a `fetch` later.

## Adding a domain

1. **Read the dictionary file** for the domain in `docs/data-dictionary/` (see its `README.md` for which file holds which tables), and the feature's flow in `docs/flow/`.
2. **Types** (`src/lib/types/<domain>.ts`): one type per table.
   - Field names are copied exactly, in snake_case (`transaction_date`, `usd_equivalent`).
   - `Required = Y` → non-optional. Otherwise `field?: T | null`.
   - `enum` → a string-literal union with the exact values (`"BUSINESS_OWNER" | "BRANCH_MANAGER"`).
   - `uuid`, `varchar`, `text` → `string`. `timestamp` / `date` → ISO `string`. `numeric` / `integer` → `number`. `boolean` → `boolean`. `jsonb` → a typed object.
   - Keep lengths in mind for form validation (`varchar 50` → max 50).
3. **Fixtures** (`src/lib/mock/`): seed rows that satisfy every rule, use the dictionary's defaults, and cover both roles and more than one branch.
4. **API** (`src/lib/api/<domain>.ts`): list/get/create/update functions that take the current user (or read the session) and filter.
5. If the flow and the dictionary disagree, **stop and raise it**. Don't pick one. Never edit `docs/data-dictionary/` yourself.

## Role and branch filtering (inside `lib/api`)

- Roles: `BUSINESS_OWNER` and `BRANCH_MANAGER` (`roles.role_name`).
- **Manager:** always filtered to `users.branch_id`, whatever the UI asks for.
- **Owner:** `users.branch_id` is null. Sees "All branches" or the single branch chosen in the branch-switcher cookie.
- Rows with a nullable `branch_id` can be business-wide (e.g. `financial_accounts.is_business_wide`). Show them to every branch view.
- Owner-only areas (branch management, integrations, business settings, reconciliation sign-off) also reject managers here, not just in the nav and the layout.

## Money

Amounts are never a bare number. Store and pass all four fields:

| Field | Meaning |
|---|---|
| `original_amount` | amount in the original currency |
| `original_currency` | `USD` or `KHR` |
| `exchange_rate` | KHR per 1 USD, from `businesses.exchange_rate` (default `4100`) |
| `usd_equivalent` | the amount in USD, used for totals and reports |

Totals and KPIs add up `usd_equivalent`. Show the original amount and currency where a single row is displayed.

## Short-lived codes

OTP codes (email verification, password reset, email change: 5-minute expiry) and pending ownership transfers (24-hour expiry) are not tables. On the backend they live in Redis. In the mock they are in-memory values with the same expiries.

## Session

Mock auth sets a session cookie holding a seeded `user_id`. `lib/api` resolves the current user from it.
