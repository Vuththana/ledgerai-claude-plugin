# The data dictionary is the source of truth

`docs/data-dictionary/` defines every table and field (40 tables, one file per domain; see its `README.md`). **If the code and the dictionary disagree, the dictionary wins.**

- **Use the names exactly**, including snake_case: `transaction_date`, `usd_equivalent`, `original_currency`. This applies to table and column names in migrations, `@Table` / `@Column` names, JSON field names in requests and responses, and event payloads. Java fields may be camelCase, but the column and JSON names they map to must be the dictionary names. Don't rename, shorten, or "improve" a name.
- **Match the rules too:** types, lengths, required flags (`NOT NULL`), defaults, enum values, unique constraints and foreign keys. Bean Validation on request DTOs follows them (`@NotNull`, `@Size(max = …)`, …).
- **Only this service's tables.** Migrate and write only the tables `docs/TRD.md` §1a gives to this service.
- **JSONB columns:** the keys inside each one are in `docs/data-dictionary/jsonb-shapes.md`, and the same rules apply to them: exact names, types, allowed values, and amounts as `BigDecimal` in the stated currency. A 📝 shape is a draft spec's proposal: don't build on it until that spec is approved.
- **Need a field that isn't there, or think one is wrong?** Don't add or change it in code, and don't edit `docs/data-dictionary/` from this repo. Propose the change in the docs repo (`docs/GUIDE.md` §7). The code follows once it's merged and the submodule is updated.
- **A spec and the dictionary disagree?** Raise it (`/sdd:clarify` or `/sdd:amend`). Don't pick one yourself.

## Roles

There are two roles (`roles.role_name`):

| Role | Branch scope |
|---|---|
| `BUSINESS_OWNER` | Has no `users.branch_id`. Sees every branch, or one branch when the request selects it. |
| `BRANCH_MANAGER` | Has `users.branch_id` and is **locked to that branch**. Never sees another branch's data. |

- Most domain rows carry `branch_id`. Some are nullable when they apply business-wide, e.g. `financial_accounts.is_business_wide`.
- Owner-only areas: branch management, integrations (Shopify, WeBill365), business settings, reconciliation sign-off.
- **Enforce it on the server, in every query:** filter by the current user's `business_id`, and by `branch_id` for a manager. Never trust a `business_id` or `branch_id` sent by the client without checking it against the current user.

## Money

Every amount is four fields, never a single number:

| Field | Meaning |
|---|---|
| `original_amount` | The amount as entered |
| `original_currency` | `USD` or `KHR` |
| `exchange_rate` | KHR per 1 USD, from `businesses.exchange_rate` (default `4100`) at the time of the record |
| `usd_equivalent` | The amount in USD, used for totals and reports |

- Use `BigDecimal` for amounts, never `double` or `float`.
- Totals, KPIs, charts and reports add up `usd_equivalent`. Never add USD and KHR amounts together.
- Keep the original amount and currency. Don't convert and throw them away.

## Redis

Short-lived codes and requests live in **Redis, not in any table**:

| What | Expiry |
|---|---|
| OTP codes: owner email verification, password reset, email change | 5 minutes |
| Pending ownership transfers | 24 hours |

- Don't add columns or tables for these.
- Use the key names suggested in `docs/flow/authentication.md` and `docs/flow/profile-and-business.md`.
