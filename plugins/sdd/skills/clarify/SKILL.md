---
name: clarify
description: Settle a 📝 LedgerVision spec and approve it — audits it, asks the user every open question, applies the answers to the spec, the data dictionary and the API reference, re-audits, and on the user's approval flips it to ✅ with its VERSION entry. Usage /sdd:clarify <feature | drafts>.
argument-hint: <feature slug or prefix, or "drafts" to audit every 📝 spec>
disable-model-invocation: true
---

# Clarify: $ARGUMENTS

Load the `sdd:conventions` skill first and follow it. You are the lead: the auditor finds, the user decides, you write.

## 1. Docs and spec

Find a **writable** docs clone (conventions §1) and the feature. The spec must be 📝 or ⟳. A ✅ spec: say so and suggest `/sdd:amend`.

**`drafts`:** start one `sdd:spec-auditor` per 📝 spec **in one message** (mode `audit`), then reply with a table — feature, readiness, open questions, blocked by — plus questions shared across specs, and stop. The user picks one to clarify.

Switch the clone to `spec/<feature>` (create it from `origin/main` if needed; ask first if there are uncommitted changes).

## 2. Audit

Start `sdd:spec-auditor`:

> Mode `audit`, feature **<slug>**. Docs root: **<abs path>**.

Apply its **Fixes** to the spec yourself (they're mechanical). Add its new questions to §10 as `Q`s with their options.

## 3. Ask

Ask every open `Q` with AskUserQuestion, up to 4 per call, each question starting with its ID (`BRN-Q04 · …`), options from the spec, the suggested one first marked "(Recommended)". Add one option **"Leave open for the team"**. Keep going until every `Q` is answered or left open.

## 4. Apply each answer

For every answered `Q`, in the spec:

1. The `Q` line gets `→ <PFX>-Dnn (answered <date> by <user>)`; the decision goes in §3 with the next free `D`.
2. Add or change the `R`, `E` and `M` lines the decision implies. An approved meaning never changes in place: changing a requirement's meaning = withdraw it (strike through) + a new ID. Wording-only fixes stay in place.
3. "Proposal:" decisions the user confirmed lose the word "Proposal:".

Then the shared docs, **only for what the user just confirmed**:

- **Dictionary (§8):** edit `data-dictionary/<file>.md` (and `jsonb-shapes.md`) exactly as agreed; mark the §8 row `applied in v<X.Y.Z>`.
- **API (§9):** add each new endpoint to `api/<service>.md` as `📝 planned` (summary row + a stub section with method, path, who, body, response, error codes — linked to the spec IDs); mark §9 `📝 planned`.

Show the user a short diff summary of the shared-doc edits before you commit them.

## 5. Re-audit

Run `sddtool.py check` (conventions §7) and continue **the same** auditor with SendMessage: "Re-audit; the spec changed." Loop 3–5 until the auditor says **ready to approve** and `check` is clean, or only "left open" questions remain.

## 6. ⏸ Approve

- **Questions left open:** commit the progress (`Spec: <title> clarified (v<X.Y.Z>)`, PATCH), list them for the team, and stop. The spec stays 📝.
- **Ready:** ask the user: "Approve `<feature>` spec v<X.Y.Z>?" Only on an explicit yes:
  1. Status ✅ Approved, version = next MINOR.
  2. `specs/README.md`: ✅, stage `plan`. If `flow/<feature>.md` exists, make sure it has the "superseded" banner (see `/sdd:migrate`).
  3. `VERSION.md`: one bullet per file touched (spec, dictionary, `api/`) and **Impact** per repo.
  4. `sddtool.py check` clean, then commit `Spec: <title> approved (v<X.Y.Z>)`. Don't push; the docs PR is the team's review.

## 7. Reply

Status, decisions made (ID → one line), shared docs changed, questions still open, and the next step: `/sdd:plan <feature>` (or the team review of the docs PR first, if the user wants it reviewed before planning).
