---
name: document-feature
description: Write the plan for one LedgerVision feature from the docs, before any code is written. Usage /ledgerai:document-feature <feature>.
argument-hint: <feature name, e.g. "branch management">
disable-model-invocation: true
---

Write the plan for the LedgerVision feature: **$ARGUMENTS**

The `feature-planner` agent writes it, so the docs it reads stay out of this conversation. What a plan must contain is set by `docs/TEAM-RULES.md` §3 and the agent's instructions. Don't create or change code files here.

## 1. Run the planner

Start the agent with the Agent tool, `subagent_type` `ledgerai:feature-planner`, and this prompt:

> Plan the **$ARGUMENTS** feature. Repos: **<absolute path of this repo>** (docs at `<repo>/docs`). No requirements brief: follow `analyze-requirements` yourself.

If the user named other repos the feature touches, add their absolute paths to the prompt.

## 2. Reply

- **It listed features** (no clear match): show the list and ask which one is meant.
- **It returned a draft's questions:** show them, ask the user to answer them, and **stop**. The flow must be approved first (`docs/TEAM-RULES.md` §6).
- **It returned a plan:** show it as it is, and ask the user to approve it before any code is written. When the user asks for changes, continue the same agent with SendMessage and the changes, then show the new plan.
