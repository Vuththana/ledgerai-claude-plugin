---
name: init
description: Set up SDD in a folder. In an empty or new workspace folder, create a new project's docs repo from a few questions (specs/ with its templates, data-dictionary/, api/, TRD.md, TEAM-RULES.md, VERSION.md, README.md), ready for /sdd:specify. In an existing docs repo without specs/, add only specs/ and its templates. Usage /sdd:init [project name — one-line description].
argument-hint: "[project name — what it does, in one line]"
disable-model-invocation: true
---

# Init: $ARGUMENTS

Load the `sdd:conventions` skill first. This skill's files are in `${CLAUDE_SKILL_DIR}/templates/`: `specs/` (the spec index and the spec / plan / tasks templates) and `project/` (the other starting files). Never overwrite an existing file: if one is in the way, show it and ask.

## 1. What's here?

Look at the current directory:

- **It, or a subfolder, has `specs/README.md`:** SDD is already set up. Run `/sdd:status`'s check (`python3 -I "${CLAUDE_SKILL_DIR}/../trace/scripts/sddtool.py" status <that folder>`), show it, and stop.
- **It, or a subfolder, is a docs repo without `specs/`** (it has `TRD.md`, `data-dictionary/` or `flow/`): **existing docs** → §2.
- **Otherwise** (empty, or only code repos): **new project** → §3.

## 2. Existing docs: add specs/

1. If it's a git repo with uncommitted changes, ask first. Create the branch `sdd-setup` from its main branch.
2. Copy `templates/specs/` to `<docs>/specs/`.
3. In `specs/README.md`, under the Features table, note that the features in `flow/` (if any) aren't migrated yet and `/sdd:migrate all` lists them.
4. Add a `VERSION.md` entry (MINOR: "SDD: `specs/` index and templates"). Commit: `SDD: specs/ index and templates`. Don't push.
5. Reply: what was added, and the next step `/sdd:migrate all` (or `/sdd:specify` for a new feature).

## 3. New project

### 3a. Ask

The project name and its one-line description come from **$ARGUMENTS** (`name — description`). If the description is missing, ask the user to type it in one sentence, and wait.

Then one AskUserQuestion, the recommended option first:

| Question | Options |
|---|---|
| **Docs folder name** | `<name-slug>-docs` (Recommended) · `docs` |
| **Stack** | Next.js web + Spring Boot API (the stack the `sdd-web` and `sdd-spring` plugins support) · Next.js only (route handlers as the API) · Spring Boot API only · Decide later |
| **Who uses it** | Owner and staff, staff limited to their own branch or team · One kind of user · Admin and users |

Anything they type under "Other" is used as written.

### 3b. Create

1. Create `<workspace>/<docs folder>/`. Copy `templates/project/` into it (keeping `data-dictionary/` and `api/`) and `templates/specs/` into `specs/`.
2. Fill the placeholders in every copied file:

   | Placeholder | Value |
   |---|---|
   | `<Project>` | the project name |
   | `<One-line description…>` / `<One-line description.>` | the description |
   | `<date>` | today, `YYYY-MM-DD` |
   | `<author>` | `git config user.name` (ask if empty) |
   | `<roles>` (TEAM-RULES §1) | one table row per role from the answer, with a short "Can" you can infer from the description, marked "(to confirm)" |
   | `<stack>` (TRD §2) | rows for the chosen stack, every one 📝. "Decide later" → one row per area (web, API, database, hosting) with ❓ |
   | `<parts>` (TRD §1a) | the repos the stack implies, 📝: `<slug>-web` (web UI), `<slug>-service` (API, owns every table to start). Next.js only → just `<slug>-web`. Decide later → one ❓ row |

   Leave `<Add a stricter rule here …>` in TEAM-RULES §6 as it is: it's for the team.
3. `git init -b main` in the docs folder and commit everything: `Docs: initial structure (v0.1.0)`. Don't add a remote and don't push.
4. Check it: `python3 -I "${CLAUDE_SKILL_DIR}/../trace/scripts/sddtool.py" status <docs folder>` must print the (empty) feature table without an error.

### 3c. Reply

- The tree of what was created.
- What's still open: the 📝 and ❓ rows in `TRD.md`, and the roles marked "(to confirm)".
- Next steps:
  1. Read `TRD.md` and `TEAM-RULES.md`; change anything that's wrong.
  2. `/sdd:specify <the first feature, in a sentence>`.
  3. The code repos come when you build: create them next to the docs folder with the names in TRD §1a (`/sdd:plan` asks for them). A Spring service then gets `/sdd-spring:setup-service`. A stack other than Next.js or Spring Boot has no developer agent yet, so `/sdd:build` stops there.
