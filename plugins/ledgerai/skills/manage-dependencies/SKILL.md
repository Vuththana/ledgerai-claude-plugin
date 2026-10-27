---
name: manage-dependencies
description: Check whether a new package is really needed, evaluate it, and draft the LedgerVision package request report before anything is installed, upgraded or removed. Use whenever a task seems to need a library that isn't in the project, or someone asks to add, upgrade or remove a dependency.
---

# Manage dependencies

The rule is in `docs/TEAM-RULES.md` §7 (and the repo's own packages rule, e.g. `.claude/rules/packages.md`): **nothing is installed until its package request is approved.** The person who needs the package submits the report. This skill gathers the facts and drafts it for them.

Never run an install command or change dependencies until the user says the request was approved.

## 1. Is it needed?

- Look in the project's dependency file (`package.json`, or the backend's equivalent) and its rules for what's already available. In web-ui, `.claude/rules/ui-components.md` lists what `@base-ui/react` already provides.
- Check whether the platform does it (e.g. `Intl.NumberFormat` and `Intl.DateTimeFormat`, `crypto.getRandomValues`, `URLSearchParams`).
- Check whether a small helper in the repo would do.

If something existing covers it, say so and stop.

## 2. Evaluate the candidate

Use read-only commands for the repo's package manager, e.g. for pnpm:

```bash
pnpm view <pkg> version license peerDependencies dependencies time.modified repository.url
```

Check maintenance (latest release, activity), license, size and transitive dependencies, compatibility with the repo's stack versions, TypeScript types, and known advisories. Compare at least one alternative, including "build it ourselves".

## 3. Draft the report

Fill in the **template from `docs/TEAM-RULES.md` §7** (or the repo's packages rule, which uses the same template) with what you found. Give it to the user to post.

## 4. After approval

Install with the repo's package manager (web-ui: pnpm only), pinned to the approved version. Commit the dependency file and lockfile together, and mention the approved request in the PR.
