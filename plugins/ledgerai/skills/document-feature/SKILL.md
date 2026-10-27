---
name: document-feature
description: Write the plan for one LedgerVision feature from the docs, before any code is written. Usage /ledgerai:document-feature <feature>.
argument-hint: <feature name, e.g. "branch management">
disable-model-invocation: true
---

Write the plan for the LedgerVision feature: **$ARGUMENTS**

What a plan must contain is set by `docs/TEAM-RULES.md` §3, plus this repo's workflow rule (e.g. `.claude/rules/workflow.md`) if it has one. Write the plan only. Don't create or change code files here.

## 1. Find the flow

Find "$ARGUMENTS" in `docs/flow/README.md`. If nothing matches clearly, list the features and ask which one is meant, then stop.

- **✅ Approved:** continue.
- **📝 Draft:** list its "Proposed decisions" and "Open questions", ask the user to answer them, and **stop**.

## 2. Gather

1. Follow the `analyze-requirements` skill for the feature.
2. Read this repo's `CLAUDE.md` and `.claude/rules/` for the architecture and coding standards the plan must follow.
3. Search the code for what already exists and can be reused.
4. Run the `identify-edge-cases` checklist against the flow.
5. If the flow and the dictionary conflict, list each conflict and ask. Don't pick one.

## 3. Write the plan

Cover every item `TEAM-RULES.md` §3 requires, using this layout. Reference doc sections rather than copying them.

1. **Scope:** in and out, with flow sections.
2. **Screens / routes / endpoints**, each with its states.
3. **Data:** tables and fields by dictionary name.
4. **Roles and branch scope.**
5. **Files:** what to create or change, following `CLAUDE.md` and the rules.
6. **Steps:** in build order, each small enough to review.
7. **Edge cases:** from step 2.4.
8. **Packages:** any needed, and why. In `web-ui`, with a drafted request (`manage-dependencies`). Default to none.
9. **Verification:** commands to run and what to check, per role.
10. **Questions and conflicts.**

End by asking the user to approve the plan before any code is written.
