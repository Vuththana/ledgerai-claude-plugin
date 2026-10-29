---
name: document-feature
description: Write the plan for one LedgerVision feature from the docs, before any code is written, and save it in the docs repo's plans/ once approved. Usage /ledgerai:document-feature <feature>.
argument-hint: <feature name, e.g. "branch management">
disable-model-invocation: true
---

Write the plan for the LedgerVision feature: **$ARGUMENTS**

The `feature-planner` agent writes it, so the docs it reads stay out of this conversation. What a plan must contain is set by `docs/TEAM-RULES.md` §3 and the agent's instructions. Don't create or change code files here. The only file written is the approved plan, in a docs clone (step 3).

## 1. Run the planner

Start the agent with the Agent tool, `subagent_type` `ledgerai:feature-planner`, and this prompt:

> Plan the **$ARGUMENTS** feature. Repos: **<absolute path of this repo>** (docs at `<repo>/docs`). No requirements brief: follow `analyze-requirements` yourself.

If the user named other repos the feature touches, add their absolute paths to the prompt.

## 2. Reply

- **It listed features** (no clear match): show the list and ask which one is meant.
- **It returned a draft's questions:** show them, ask the user to answer them, and **stop**. The flow must be approved first (`docs/TEAM-RULES.md` §6).
- **It returned a plan:** show it as it is, and ask the user to approve it before any code is written. When the user asks for changes, continue the same agent with SendMessage and the changes, then show the new plan.

## 3. Save the approved plan

Once the user approves, the plan goes in the docs repo as `plans/<flow file>.md` (`docs/plans/README.md` has the format and the rules).

1. **A separate clone** of `ledgerai-project-docs`, never the `docs/` submodule (`docs/GUIDE.md` §7). In the workspace folder, that's the sibling `ledgerai-project-docs/`; otherwise ask the user where one is. If it has uncommitted changes, ask before touching it.
2. **Branch** `feature/<feature-slug>` from the latest `main`: `git -C <clone> fetch`, then `git -C <clone> switch -c feature/<feature-slug> origin/main` (or switch to it if it exists).
3. **Write** `plans/<flow file>.md`: the header from `plans/README.md` (the docs version is `git -C docs describe --tags --always` in this repo, the approver is the user), the plan as approved, word for word, and an empty Changes table.
4. **Commit** it with its `VERSION.md` entry (a PATCH): `Plan: <feature> (v<X.Y.Z>)`.
5. **Ask** whether to push the branch and open the docs pull request. Pushing is visible to the team: don't push without a yes.

Reply with the plan file's path and branch. If the plan changes later, continue the planner with SendMessage, show the change, and once it's approved update the file and add a row to its Changes table (`docs/TEAM-RULES.md` §3).
