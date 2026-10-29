---
name: specify
description: Turn a LedgerVision feature idea into a new 📝 draft spec (specs/<feature>/spec.md) with requirement, edge-case, decision, message and question IDs, dictionary gaps and the endpoints it needs. Interviews the user. Usage /sdd:specify <idea in a sentence or two>.
argument-hint: <feature idea, e.g. "export the cash-flow statement to CSV">
disable-model-invocation: true
---

# Specify: $ARGUMENTS

Load the `sdd:conventions` skill first and follow it. You are the lead: you write the spec; the `sdd:spec-auditor` agent does the reading.

## 1. Docs

Find a **writable** docs clone (conventions §1). Check it's SDD-ready. `git fetch`, then switch to `spec/<slug>` from `origin/main` once you have the slug (step 3); if the clone has uncommitted changes, ask first.

## 2. Scout

Start `sdd:spec-auditor`:

> Mode `scout`. Idea: **$ARGUMENTS**. Docs root: **<abs path>**. Repos for QA prefixes: **<abs paths of code repos in the workspace, if any>**.

If it says **"this is an amendment of <feature>"**, tell the user and suggest `/sdd:amend <feature>` instead. Go on only if they want a separate spec.

## 3. Interview

Ask the user the scout's questions with AskUserQuestion: at most 3 rounds of up to 4 questions, the suggested option first and marked "(Recommended)". Add your own only for what a spec can't be written without:

- who uses it (`BUSINESS_OWNER`, `BRANCH_MANAGER`) and the branch scope
- the journeys, in the user's words; what's out of scope
- money (currencies, `usd_equivalent`), limits, expiries, empty / error states that matter to them

Then propose the **slug** (kebab-case) and **prefix** (the scout's suggestion) in one line; the user can change them.

**Don't invent answers.** Anything the user didn't settle becomes a `Q` with its options — never a quiet assumption.

## 4. Write the spec

Read `specs/_templates/spec.md` and write `specs/<slug>/spec.md` from it, **📝 Draft**, version = the next MINOR in `VERSION.md`:

- What the user settled → `D` decisions; what you propose → `D` with "Proposal:"; what's open → `Q`.
- Every rule is a numbered `R`: one testable sentence with role and §. Every message goes in §6 with an `M`.
- Run the `sdd:identify-edge-cases` categories and write each relevant case as an `E` with its expected result (or a `Q` when that's a choice).
- Fields only by dictionary name. Missing fields go in §8 as `proposed` — never edit `data-dictionary/` here.
- §9: every *server* step's endpoint, with the owning service, `📝 planned` unless it's in `api/`.

Run `python3 -I "${CLAUDE_SKILL_DIR}/../trace/scripts/sddtool.py" check <docs> <slug>` and fix every ERROR.

## 5. Record

1. Add the feature's row to `specs/README.md` (📝, stage `spec`).
2. Add the `VERSION.md` entry (MINOR: new spec; **Impact:** none until approved).
3. Commit: `Spec: <title> draft (v<X.Y.Z>)`. Don't push.

## 6. Reply

The spec path; counts of R / E / D / M / open Q; the open questions in one line each; and the next step: `/sdd:clarify <slug>`.
