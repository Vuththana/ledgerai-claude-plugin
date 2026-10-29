---
name: migrate
description: Convert a v1 LedgerVision flow (flow/<feature>.md, plus its saved plan if any) into an SDD spec folder (specs/<feature>/) with requirement IDs, without changing any behaviour, and check the result against the original. One-time per feature. Usage /sdd:migrate <flow | all>.
argument-hint: <flow file or name, e.g. "branch-management", or "all" to list what's left>
disable-model-invocation: true
---

# Migrate: $ARGUMENTS

Load the `sdd:conventions` skill first. Migration **moves** behaviour into the new format; it never adds, drops or settles anything. A ✅ flow becomes a ✅ spec, a 📝 flow a 📝 spec.

**`all`:** list the flows in `flow/README.md` that have no `specs/<feature>/` yet, with status and size, suggest an order (✅ ones being built first), and stop.

## 1. Docs

Find a **writable** docs clone (conventions §1); switch to `spec/<feature>`, created from `origin/main` if needed (ask first if there are uncommitted changes). Read the whole `flow/<feature>.md`, and the saved plan if one exists: `plans/<feature>.md` on `origin/main`, or `git show origin/feature/saved-plans:plans/<feature>.md`.

## 2. Prefix

Reuse the prefix the team's QA reports already use for this feature (`grep -ho '^| [A-Z]\+-[CVM]-' <repo>/qa-reports/*<feature>*.md`), else 3 letters not used by another spec.

## 3. Write `specs/<feature>/spec.md`

From `specs/_templates/spec.md`, same status as the flow, version = the next PATCH:

- **§4 Journeys:** the flow's sections and Mermaid diagrams, as they are, renumbered `4a, 4b…`.
- **§3:** every decision ("Proposed decisions at a glance" in a 📝 flow keeps "Proposal:").
- **§5:** every rule, state and role rule as one testable `R` each, with its § — in flow order, so IDs follow the document.
- **§6:** every message and error code (from diagrams, tables and `api/`), each an `M`.
- **§7:** every edge case the flow states, each an `E`. Don't add new ones — that's for `/sdd:clarify`.
- **§8 / §9:** "Data dictionary gaps" as `proposed`, "Data dictionary changes (applied)" as `applied`; endpoints from the flow and `api/`.
- **§10:** open questions as `Q`s; resolved ones as `Q → D`.
- At the end, a **"Migrated from"** table: old flow § → new § and IDs, so old links still resolve.

Run `sddtool.py check` (conventions §7) and fix every ERROR.

## 4. Check it's faithful

Start `sdd:spec-auditor`:

> Mode `compare`, feature **<feature>**. Docs root: **<abs path>**. Old flow: `flow/<feature>.md`.

Fix everything **Lost**, **Invented** or **Changed**, then continue the same auditor: "Compare again." Repeat until it says **faithful**.

## 5. Plan (only if a v1 plan exists)

Write `specs/<feature>/plan.md` from `specs/_templates/plan.md`: the v1 plan's content, word for word where possible, with the IDs each item serves added, the **Spec:** line pointing at the commit you're about to make, and its Changes table kept plus one row "Migrated to SDD". Don't write `tasks.md` — `/sdd:tasks` does.

## 6. Record

1. Put this banner at the top of `flow/<feature>.md`, nothing else changed (v1 keeps working):
   `> **Superseded by [specs/<feature>/spec.md](../specs/<feature>/spec.md)** (SDD). Edit the spec, not this file.`
2. `specs/README.md`: the feature's row (status, stage `spec` or `plan`).
3. `VERSION.md`: PATCH — "Migrated `<feature>` to SDD (no behaviour change)".
4. Commit `Spec: migrate <feature> to SDD (v<X.Y.Z>)`; if you wrote `plan.md`, amend its **Spec:** commit to this commit's sha in a second commit. Don't push.

## 7. Reply

Counts of R / E / D / M / Q, the compare verdict, whether a plan was migrated, and the next step: `/sdd:clarify` for a 📝 spec, `/sdd:plan` (or `/sdd:tasks` if the plan was migrated) for a ✅ one.
