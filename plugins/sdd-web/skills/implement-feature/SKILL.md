---
name: implement-feature
description: Build the web-ui tasks of an approved LedgerVision SDD plan step by step, from tasks.md to a working, checked feature, with tests named by requirement ID. Use when asked to implement, build or continue a feature, page or screen in web-ui.
---

# Implement a feature (web-ui)

**What** to build comes from the spec (`specs/<feature>/spec.md`) and the data dictionary. **How** code is written comes from `CLAUDE.md` and `.claude/rules/` (they load when you touch matching files). **Which work, in what order** comes from `tasks.md`. This skill is how to do one task. Paths like `specs/` and `api/` are in the docs root (`sdd:conventions` §1).

## 0. Gate

- The spec is ✅ and `specs/<feature>/plan.md` exists. No plan → `/sdd:plan` first, and wait for approval.
- You have task IDs from `tasks.md` (or the user named them). Skip ⟳ stale tasks.
- If the plan or spec must change, that happens first (`/sdd:plan` change mode, `/sdd:amend`), then the code.
- One feature at a time (`workflow.md`).

## 1. Per task

Read the IDs the task covers in the spec — the requirement, its messages (`M`) and edge cases (`E`). Then, depending on the task:

**Data** — types, mock fixtures and `src/lib/api` functions for the tables the plan lists (`data-layer.md`). Each function and its mock use exactly its endpoint's method, path, fields and error `code`s from `api/<service>.md`, or the plan's §3 contract when it's **new** (say so in the PR). Never invent an endpoint.

**Routes** — pages and layouts in the right route group, the role check for owner-only segments, `<Suspense>` around dynamic parts (`nextjs.md`).

**UI** — components in `src/features/<feature>/`, reusing `src/components/ui` and `src/components/shared` (`ui-components.md`, `forms.md`, `data-tables.md`, `drag-and-drop.md`). The look comes from Figma (`figma-design` skill).

**Roles** — nav item, route check and `lib/api` scoping for both roles (`data-dictionary.md` § Roles).

**States and messages** — every state, and every message by its `M` text, word for word. Go through `identify-edge-cases` for the task's `E` IDs.

**Tests** — when a test runner exists, name each test with the ID it proves first (`test("BRN-R03 …")`). No runner yet: say which IDs need a QA scenario instead.

## 2. Check after each task

```bash
pnpm lint
pnpm build
```

The task's "done when" must hold. Report `T07 done → files` (an agent replies; in a session, tell the user so they can tick it via the lead).

## 3. Before the PR

Click through as both seeded users (owner in "All branches" and in one branch; manager), light and dark, phone and desktop. Then `/sdd:verify <feature>`.

## When the spec doesn't answer something

Stop and ask. It's a **spec gap** (→ `/sdd:amend`). Don't invent behaviour or fields, and don't edit the docs.
