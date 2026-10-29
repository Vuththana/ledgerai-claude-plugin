---
name: sync-docs
description: Check whether this repo's docs submodule (ledgerai-project-docs) is behind, report what changed (MAJOR / MINOR / PATCH, specs approved or amended, IDs withdrawn) and what it affects in this repo — including tests that name withdrawn IDs — and update it on request. Usage /sdd:sync-docs.
disable-model-invocation: true
---

Check and sync this repo's pinned copy of the docs (`docs/`, the `ledgerai-project-docs` submodule).

## 1. Where are we?

```bash
git submodule status docs
git -C docs describe --tags --always
git -C docs fetch --tags
git -C docs log --oneline HEAD..origin/main
```

`docs/` empty: the submodule isn't initialised — tell the user to run `git submodule update --init` (and once per machine `git config --global submodule.recurse true`). Nothing new: "Docs are up to date at <version>", stop.

## 2. What changed?

- The new `VERSION.md` entries on `origin/main` (`git -C docs show origin/main:VERSION.md`), from the current version up, and `git -C docs diff HEAD origin/main --stat`.
- **MAJOR** = breaking: a field or table renamed or removed, a type / length / enum changed, an approved spec amended (IDs withdrawn). **MINOR** = added: a table, field, endpoint, spec, or a spec approved. **PATCH** = wording, plans, migrations to SDD.
- **Specs:** for each changed `specs/<feature>/spec.md`, the IDs added and withdrawn (`git -C docs diff HEAD origin/main -- specs/<feature>/spec.md`, struck-through `~~**XXX-…**~~` lines).

## 3. What does it affect here?

- For every changed field, table or enum: `grep -rn "<old_name>"` over this repo (not `docs/`, `node_modules/`, `build/`). List the files.
- For every withdrawn ID: tests in this repo that still name it (`grep -rn "<ID>" src/test tests e2e src --include='*.test.*' --include='*.spec.*' --include='*IT.java' --include='*Test.java'`).
- Specs that went 📝 → ✅: their proposals are settled; they can be planned.

## 4. Report

| Version | Type | Change | Affects in this repo |
|---|---|---|---|

Recommend: PATCH / MINOR only → safe to update now. Any MAJOR → update in a PR together with the code (and test renames) it needs.

## 5. Update — only when the user says so

```bash
git submodule update --remote docs
git diff --submodule
git add docs
git commit -m "Update project docs to <version>"
```

Don't push unless asked. Never edit files inside `docs/` — spec changes go through `/sdd:amend` in a docs clone.
