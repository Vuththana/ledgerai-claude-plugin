# Team Rules

The rules every <Project> team member follows, in every repo. They are short on purpose. If a rule gets in your way, raise it with the team; don't work around it.

**Status:** 📝 Starting point from `/sdd:init`. Change anything the team disagrees with, in a docs pull request.

## 1. The project

<One-line description.>

| Role | Can |
|---|---|
<roles>

Feature specs and their status: [specs/README.md](specs/README.md).

## 2. One feature at a time

- Build **one feature at a time**. Finish it (merged, reviewed, working) before starting the next.
- One feature per branch and per pull request. Shared pieces are fine when the current feature needs them.
- In the code repos, branches start from `dev` and pull requests go into `dev`. Nobody commits to `main`; the repo owner merges `dev` into `main`.
- A bug or gap in another feature: note it (issue or message). Don't fix it in this feature's PR unless it blocks you.

## 3. Spec first, then plan, then code

No code is written for a feature until its spec is approved and its plan is agreed.

1. **Spec:** `/sdd:specify` writes it, `/sdd:clarify` settles its questions. A spec is ✅ only when nothing is open.
2. **Plan:** `/sdd:plan`. Its contents are defined once, in [`specs/_templates/plan.md`](specs/_templates/plan.md). The team approves it.
3. **Tasks and build:** `/sdd:tasks`, then `/sdd:build` (or `/sdd:run` for everything up to the push).
4. If the plan must change, it changes first, then the code. If the **spec** must change: `/sdd:amend`, then the code.

## 4. The data dictionary is the source of truth

Every table and field is in [`data-dictionary/`](data-dictionary/README.md). Code uses the same names, types, lengths, required flags, defaults and enum values. A spec never changes a field silently: proposed changes go in its §8 and are applied after the team agrees.

## 5. Specs: approved vs draft

| Status | Meaning | What you may do |
|---|---|---|
| ✅ Approved | Settled | Plan and build against it |
| 📝 Draft | Open questions or proposals | Read it and raise its questions. **Don't build on a guess** |
| ⟳ Amending | An approved spec being changed | The stale tasks wait |

Requirement IDs (`ABC-R01`) are never renumbered or reused. Tests name the ID they prove first, so `/sdd:trace` can count them.

## 6. Packages

Prefer what the repo already has, or what the platform provides. A new dependency is named in the plan, with the reason. <Add a stricter rule here if the team wants one, e.g. a package request for the web front end.>

## 7. Before a pull request

- [ ] The feature's spec is ✅ and its plan approved
- [ ] Only this feature's work is in the branch
- [ ] Field names match the data dictionary
- [ ] Every endpoint is listed in `api/`
- [ ] Tests name their requirement IDs; the build passes
- [ ] No secrets or hardcoded URLs (the `check-secrets` skill runs before every push)
