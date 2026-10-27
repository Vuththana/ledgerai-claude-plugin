---
name: sync-project-specs
description: Check whether this repo's docs submodule (ledgerai-project-docs) is behind, report what changed and what it affects in this repo, and update it on request. Usage /ledgerai:sync-project-specs.
disable-model-invocation: true
---

Check and sync this repo's copy of the central project docs (`docs/`, the `ledgerai-project-docs` submodule). The process follows `docs/GUIDE.md` §3.4 and §6.

## 1. Where are we?

```bash
git submodule status docs
git -C docs describe --tags --always
git -C docs fetch --tags
git -C docs log --oneline HEAD..origin/main
```

If `docs/` is empty, the submodule isn't initialised. Tell the user to run `git submodule update --init` (and once per machine, `git config --global submodule.recurse true`).

If there's nothing new, say "Docs are up to date at <version>" and stop.

## 2. What changed?

- Read the new entries at the top of `docs/VERSION.md` on `origin/main` (`git -C docs show origin/main:VERSION.md`), from the current version up.
- `git -C docs diff HEAD origin/main --stat` shows which files changed.
- Classify each entry. **MAJOR** is breaking: a field or table renamed or removed, a type, length or enum changed, or an approved flow's behaviour changed. **MINOR** is added: a new table, field or flow, or a draft approved. **PATCH** is wording only.

## 3. What does it affect here?

For every changed field, table, enum or flow, search this repo (excluding `docs/` and `node_modules/`) for the old and new names, e.g. `grep -rn "<old_field>" src`. List the files that need changes. Note any flow that went 📝 → ✅, because its proposed decisions are now settled.

## 4. Report

| Version | Type | Change | Affects in this repo |
|---|---|---|---|

Then recommend:

- **PATCH / MINOR only:** safe to update now.
- **Any MAJOR:** update in a pull request together with the code changes it needs (`docs/GUIDE.md` §3.4).

## 5. Update (only when the user says so)

```bash
git submodule update --remote docs
git diff --submodule
git add docs
git commit -m "Update project docs to <version>"
```

Don't push unless asked.

## Never

- Edit files inside `docs/`. Proposed spec changes go through a pull request on `ledgerai-project-docs` (`docs/GUIDE.md` §7).
- Update the submodule to a version with MAJOR changes without telling the user what breaks.
