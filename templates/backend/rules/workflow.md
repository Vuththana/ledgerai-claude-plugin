# Workflow: one feature at a time, plan first

## One feature at a time

- Work on **one feature at a time**, in the order the team agreed. Finish it (merged, reviewed, working) before starting the next.
- Keep each branch and pull request to that one feature. Don't mix in work for another feature, and don't start the next one in the same branch.
- Build shared pieces (error handling, security, money helpers) only when the current feature needs them. Build what this feature needs, not what a future feature might.
- If you find a bug or gap in another feature or another service, note it (an issue or a message to the team). Don't fix it in this feature's PR unless it blocks you.

## Plan first, then code

Don't write code for a feature until its plan is written and approved.

1. **Read** the feature's flow in `docs/flow/`, every `docs/data-dictionary/` table it lists, and the parts of `docs/TRD.md` that apply.
2. **Write the plan** and share it with the team. It covers:
   - the endpoints you will add or change (method, path under `/api/v1`, request and response, error codes)
   - the Flyway migrations, entities and repositories, for tables **this service owns** only (`docs/TRD.md` §1a)
   - calls to other services and RabbitMQ events published or consumed
   - Redis keys, scheduled jobs and emails, if any
   - the tables and fields you will use, by their dictionary names
   - who can do what (`BUSINESS_OWNER` / `BRANCH_MANAGER`) and how branch scope is applied
   - any new dependency you need, with its package request (see `packages.md`)
   - questions or conflicts you found in the flow, the dictionary or the TRD
3. **Get the plan approved**, then build it.
4. If the plan has to change partway through, update it and tell the team before you continue.

When Claude is asked to build a feature, it writes the plan first and waits for approval before editing code.

## Before opening a pull request

- `./gradlew build` passes (all unit and integration tests).
- The checklist in `docs/TEAM-RULES.md` §9 is met.
