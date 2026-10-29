# Project: LedgerVision <service-name>

This repo is the **<service-name>** of LedgerVision, an AI-powered financial copilot for SME retail stores. A business can have several branches and works in two currencies, USD and KHR. Owners and branch managers use it to track money in and out, manage stock, reconcile bank statements, and get AI answers, reports and forecasts about their business.

The shared specs live in the `docs/` submodule (the `ledgerai-project-docs` repo). The full team rules are in `docs/TEAM-RULES.md`. The files in `.claude/rules/` are the backend version of those rules.

## The backend

| Repo | Owns |
|---|---|
| `api-gateway` | The single entry point for the web UI. Routes `/api/v1/{service}/**` through Consul |
| `identity-service` | Authentication, Profile & Business, Branch Management, Notifications, Telegram, audit log |
| `sales-service` | Item Management, Sales Management (incl. customers) |
| `finance-service` | Dashboard figures, Banking Statement, Financial Records (incl. invoices, receipts), Monthly AI Report, Integrations |
| `ai-service` (FastAPI) | AI Financial Advisor, Data Import & Cleanup, Forecasting, AI parts of other features |
| `ledgervision-common` | Shared Spring library: security, current user / scope, error format, money helpers, event contracts |

The exact table ownership is in `docs/TRD.md` §1a. **This repo writes only the tables it owns.** Anything else goes through the owner's API or a RabbitMQ event.

## This repo's features

<!-- Fill in from docs/TRD.md §1a. -->

| Feature | Flow |
|---|---|
| <Feature> | `docs/specs/<feature>/spec.md` |

Each spec's current status (✅ / 📝 / ⟳) and stage is in `docs/specs/README.md`. Check it there rather than trusting this table.
