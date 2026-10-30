---
name: implement-feature
description: Build the web-ui tasks of an approved LedgerVision SDD plan step by step, from tasks.md, in the current milestone (M1 static UI from Figma, M2 integration with the real API, tests named by requirement ID). Use when asked to implement, build or continue a feature, page or screen in web-ui.
---

# Implement a feature (web-ui)

**What** to build comes from the spec (`specs/<feature>/spec.md`) and the data dictionary. **How** code is written comes from `CLAUDE.md` and `.claude/rules/` (they load when you touch matching files). **Which work, in what order** comes from `tasks.md`. This skill is how to do one task. Paths like `specs/` and `api/` are in the docs root (`sdd:conventions` §1).

## 0. Gate

- The spec is ✅ and `specs/<feature>/plan.md` exists. No plan → `/sdd:plan` first, and wait for approval.
- You have task IDs from `tasks.md` (or the user named them). Skip ⟳ stale tasks.
- If the plan or spec must change, that happens first (`/sdd:plan` change mode, `/sdd:amend`), then the code.
- One feature at a time (`workflow.md`).
- **The milestone** (`sdd:conventions` §1c, `TEAM-RULES.md` § "web-ui: two milestones"): build only tasks in the current milestone's phase of `tasks.md`.
  - **M1 — static UI:** every screen the task builds has its Figma frame in the plan's §4. No frame → stop and ask; don't build it from the spec alone. Branch `feature/<feature>`.
  - **M2 — integration:** the endpoints the task calls are built in their service. Branch `feature/<feature>-integration`.

## 1. Per task

Read the IDs the task covers in the spec — the requirement, its messages (`M`) and edge cases (`E`). Then, depending on the task:

### M1 — static UI

**Placeholder data** — one file, `src/features/<feature>/placeholder-data.ts`, typed with `src/lib/types/` (create the types from the dictionary if they're missing). Dictionary names and enum values, values that satisfy the dictionary's rules, enough rows to show every state in the plan's §4, both roles and more than one branch. Screens import it directly. **Don't touch** `src/lib/api`, `src/lib/mock` or Server Actions.

**Routes** — pages and layouts in the right route group, `<Suspense>` around dynamic parts (`nextjs.md`). No role checks yet.

**UI** — components in `src/features/<feature>/`, reusing `src/components/ui` and `src/components/shared` (`ui-components.md`, `forms.md`, `data-tables.md`, `drag-and-drop.md`). The look comes from the Figma frames (`figma-design` skill). Forms show their fields, labels and client-side validation messages but don't submit. Buttons that would call the server do nothing yet.

**States** — every state in the plan's §4 is built and renders from the placeholder data (an empty list, an error banner, each status). Every message by its `M` text, word for word.

**Roles** — build the owner and the manager variant of each screen as the Figma frames and spec §2 show them. Nav visibility, route checks and branch scoping are M2.

**Tests** — none in M1. Say which IDs need a test in M2.

### M2 — integration

**Data** — types and `src/lib/api` functions for the tables the plan lists (`data-layer.md`), against the real endpoints. Each function uses exactly its endpoint's method, path, fields and error `code`s from `api/<service>.md`, or the plan's §3 contract when it's **new** (say so in the PR). Never invent an endpoint. Then point the screens at `src/lib/api` and **delete** `placeholder-data.ts`.

**Forms and actions** — Server Actions that call `src/lib/api`; forms submit, show field errors from the API and roll back optimistic updates (`forms.md`, `data-layer.md`). Keep M1's layout; change it only where the plan says.

**Roles** — nav item, the route check for owner-only segments and `lib/api` scoping for both roles (`data-dictionary.md` § Roles).

**States and messages** — every state, and every message by its `M` text, word for word, now driven by the API's responses and error `code`s. Go through `identify-edge-cases` for the task's `E` IDs.

**Tests** — when a test runner exists, name each test with the ID it proves first (`test("BRN-R03 …")`). No runner yet: say which IDs need a QA scenario instead.

## 2. Check after each task

```bash
pnpm lint
pnpm build
```

The task's "done when" must hold. Report `T07 done → files` (an agent replies; in a session, tell the user so they can tick it via the lead).

## 3. Before the PR

- **M1:** open every screen and state next to its Figma frame, owner and manager variants, light and dark, phone and desktop.
- **M2:** against the running services, click through as the services' seeded owner (in "All branches" and in one branch) and manager, light and dark, phone and desktop.

Then `/sdd:verify <feature>`.

## When the spec doesn't answer something

Stop and ask. It's a **spec gap** (→ `/sdd:amend`). Don't invent behaviour or fields, and don't edit the docs.
