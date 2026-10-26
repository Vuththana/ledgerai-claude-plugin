---
description: Plan a LedgerVision feature from its flow doc and the data dictionary, before writing any code
argument-hint: <feature name, e.g. "branch management">
---

Plan the LedgerVision feature: **$ARGUMENTS**

Features are built one at a time, and each one gets a detailed plan before any code is written. Write the plan only. Don't create or change code files in this command.

## 1. Find the flow

Read `docs/flow/README.md` and find the row for "$ARGUMENTS". If nothing matches clearly, list the features in that table and ask which one is meant. Then stop.

Note the flow's status:

- **✅ Approved:** its decisions are settled. Continue.
- **📝 Draft:** read the flow doc, then list its "Proposed decisions" and "Open questions" and ask the user to answer them. **Stop there.** Don't plan on top of unanswered questions.

## 2. Read the sources

- The feature's flow doc in `docs/flow/`.
- Every data dictionary file in `docs/data-dictionary/` that the flow references (`docs/data-dictionary/README.md` maps tables to files).
- The repo's `CLAUDE.md`, for this repo's stack and architecture.
- Existing code the feature will reuse or extend. Search before planning anything new.

If the flow and the dictionary disagree (a field name, required flag, enum value, a field the flow needs that the dictionary lacks), **list each conflict and ask.** Don't pick one, and don't edit `docs/data-dictionary/`.

## 3. Write the plan

Use these sections:

1. **Scope:** what's in and out, quoting the flow's sections.
2. **Roles:** what `BUSINESS_OWNER` and `BRANCH_MANAGER` can each see and do, and which branch filter applies.
3. **Data:** the tables and fields used, with exact dictionary names, required flags, lengths, defaults and enums. Include money fields (`original_amount`, `original_currency`, `exchange_rate`, `usd_equivalent`) where relevant.
4. **Files:** what to create or change, following the repo's `CLAUDE.md` architecture. Name the representative paths.
5. **Steps:** in build order, each small enough to review.
6. **Edge cases:** validation, empty and error states, expiries, permission failures.
7. **Verification:** how to check it works (commands to run, flows to click through for each role).
8. **Open items:** anything still unclear.

End by asking the user to approve the plan before any code is written.
