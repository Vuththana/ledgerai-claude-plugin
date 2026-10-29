# Workflow: one feature at a time, spec → plan → tasks

## One feature at a time

- Work on **one feature at a time**, in the order the team agreed. Finish it (merged, reviewed, working) before starting the next.
- Keep each branch and pull request to that one feature. Don't mix in work for another feature, and don't start the next one in the same branch.
- Build shared pieces (error handling, security, money helpers) only when the current feature needs them. Build what this feature needs, not what a future feature might.
- If you find a bug or gap in another feature or another service, note it (an issue or a message to the team). Don't fix it in this feature's PR unless it blocks you.

## Plan first, then code

Don't write code for a feature until its spec is ✅, its plan is approved and its tasks exist (`specs.md`).

1. **Plan:** `/sdd:plan <feature>`. The plan's contents are defined once, in `docs/specs/_templates/plan.md`; for this service it covers endpoints, migrations for tables **this service owns** (`docs/TRD.md` §1a), calls and events, Redis keys, jobs, emails, roles and branch scope, dependencies (`packages.md`) — each item citing the spec IDs it serves.
2. **Tasks:** `/sdd:tasks <feature>` turns the plan into `tasks.md`. Build task by task (`/sdd:build`, or the `implement-feature` skill), and report each task done with its files.
3. If the plan has to change partway through, it changes first (`/sdd:plan` change mode), then the code. If the **spec** has to change, `/sdd:amend` first.

When Claude is asked to build a feature, it checks for an approved plan and tasks first and never edits code without them.

## Branches

- Work on `feature/<feature>`, started from `origin/dev`. Pull requests go into **`dev`**.
- **Never commit to, push to, or merge into `main`.** The repo owner merges `dev` into `main`.

## Before opening a pull request

- `./gradlew build` passes (all unit and integration tests).
- Every endpoint added or changed is listed in `docs/api/<service>.md`, through a docs pull request (`docs/TEAM-RULES.md` §3).
- Every test names the spec ID it proves; `/sdd:verify <feature>` passes and `/sdd:trace <feature>` shows no ⛔ or drift for this service.
- The checklist in `docs/TEAM-RULES.md` §9 is met.
