---
name: write-unit-tests
description: Unit tests for LedgerVision front-end logic (lib/api filtering, money conversion, layout normalizing, validation rules). Placeholder — no test runner is installed yet. Use when asked to write or run unit tests.
---

# Write unit tests (not set up yet)

**There is no test runner in this repo yet**: no test script, and no Vitest or Jest in `package.json`. Adding one needs an approved package request.

When asked for unit tests:

1. Say that no runner is set up. **Don't install one, and don't write test files** that assume a framework.
2. Offer to draft the package request with the `manage-dependencies` skill. A common choice for this stack is Vitest (dev dependency). The team decides.
3. Meanwhile, verify the logic another way: `pnpm lint`, `pnpm build`, and a short manual check of the cases below in the running app.

## What to cover once a runner is approved

Pure logic with real rules:

- `lib/api` role and branch filtering (manager locked to `users.branch_id`, owner "All branches" versus one branch, business-wide rows)
- Money: `usd_equivalent` from `original_amount`, `original_currency` and `exchange_rate`
- Validation rules shared by forms and Server Actions (dictionary lengths, enums, the password policy)
- Normalizing `users.dashboard_layout` (null, unknown ids, missing widgets)
- Expiry logic for OTP codes, invitations and ownership transfers

When a runner is approved, replace this skill with the real setup: commands, file naming, mock seeding.
