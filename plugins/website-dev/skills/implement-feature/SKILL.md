---
name: implement-feature
description: Build an approved LedgerVision front-end feature step by step, from the approved plan to a working, checked feature. Use when asked to implement, build or continue a feature, page or screen.
---

# Implement a feature

**What** to build comes from the docs (`docs/flow/<feature>.md`, `docs/data-dictionary/`). **How** code is written comes from `CLAUDE.md` and `.claude/rules/`. Those rules load on their own when you touch matching files. This skill is the order of work.

## 0. Gate

- The feature has an **approved plan** (`/ledgerai:document-feature`). No plan → write one first and wait for approval.
- Its flow is ✅ approved, or the parts you build are settled (`feature-flows.md`).
- It's the one feature being worked on (`workflow.md`).

## 1. Data

Types, mock fixtures and `src/lib/api` functions for the tables the plan lists (`data-layer.md`). Then run the `dictionary-checker` agent on them.

## 2. Routes

Pages and layouts in the right route group. Add the role check for owner-only segments, and `<Suspense>` around dynamic parts (`nextjs.md`).

## 3. UI

Components in `src/features/<feature>/`, reusing `src/components/ui` and `src/components/shared` (`ui-components.md`, plus `forms.md`, `data-tables.md` and `drag-and-drop.md` where they apply).

## 4. Roles

Nav item, route check and `lib/api` scoping for both roles (`data-dictionary.md` § Roles).

## 5. States and messages

Every state and message the flow defines, using its wording. Go through the `identify-edge-cases` checklist.

## 6. Check

```bash
pnpm lint
pnpm build
```

- Click through as both seeded users (owner in "All branches" and in one branch; manager), in light and dark mode, at phone and desktop widths.
- Run `/ledgerai:review-feature <feature>` against the flow.
- Run `/website-dev:review-pull-request` before opening the PR.

## When the docs don't answer something

Stop and ask. Note it as a flow gap. Don't invent behaviour or fields, and don't edit `docs/`.
