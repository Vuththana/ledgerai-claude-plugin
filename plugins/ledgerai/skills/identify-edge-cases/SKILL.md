---
name: identify-edge-cases
description: Find missing states, validations, permission cases and timing rules in a LedgerVision feature's flow, design or implementation. Use when planning a feature, reviewing a flow or design, or before calling a feature done.
---

# Identify edge cases

Go through each category for the feature. The **values** (limits, expiries, messages, allowed actions) come from the flow and the dictionary. This list only says what to look for.

For each case, record whether the flow covers it (and where), and whether the code or design handles it.

## States

- Loading, for each independently loaded part
- Empty: a brand-new business with no data, versus no results for the current filters
- Error on load and on save, with a retry and a user-safe message
- Every value of every status enum, with its allowed actions
- Partial or insufficient data

## Validation

- Every required field, length, enum value and default in the dictionary
- Unique fields, and the message when a value is taken
- Money: allowed currencies, where the exchange rate comes from, `usd_equivalent` computed rather than typed in, large KHR amounts
- Dates and time zones, and period boundaries (months, "same days of the previous month")
- Any extra rules the flow sets (passwords, codes, file types and sizes)

## Permissions

- What each role sees and can do, including through a hand-typed URL or a direct API call
- A manager never reaches another branch's data
- An owner in "All branches" versus a single branch
- Owner-only areas blocked in nav, route and data
- Business-wide rows (null `branch_id`)
- A user deactivated mid-session, a soft-deleted business, soft-deleted rows

## Time and limits

- Every expiry and limit in the flow: what happens just before, just after, and on reuse
- Resend cooldowns, attempt caps, lockouts

## Actions

- Double submit, navigating away mid-save, retrying
- An optimistic update that fails
- Destructive actions: confirmation, and whether they can be undone
- Two users changing the same record

## Text and layout

- Long names and long numbers on a phone
- Strings that will need translating (no text built by concatenation)

## Output

| # | Edge case | Category | Flow covers it? (§) | Handled? | Suggestion |
|---|---|---|---|---|---|

List gaps in the flow separately under **Flow gaps**, for the team to settle in the docs. Never edit `docs/`.
