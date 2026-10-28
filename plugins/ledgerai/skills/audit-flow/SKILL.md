---
name: audit-flow
description: Check whether 📝 draft LedgerVision flows are ready to approve, and list what the team must settle — open questions with options, conflicts, dictionary gaps, missing endpoints, uncovered edge cases. Runs one flow-auditor agent per flow, in parallel. Usage /ledgerai:audit-flow <flow | drafts>.
argument-hint: <flow name, e.g. "forecasting", or "drafts" for every 📝 flow>
disable-model-invocation: true
---

Audit: **$ARGUMENTS**

## 1. Find the docs and the flows

- The docs root is `docs/` in a code repo, or the current directory in a clone of `ledgerai-project-docs` (it has `flow/README.md` at the top).
- From `flow/README.md`, take the flow named in **$ARGUMENTS**, or every 📝 flow if it says `drafts`. If nothing matches, list the features and stop.
- A ✅ flow is already approved: say so and leave it out.

## 2. Run the auditors

In one message, start one agent per flow with the Agent tool, `subagent_type` `ledgerai:flow-auditor`, and this prompt:

> Audit the **<flow file>** flow. Docs root: **<absolute path>**.

## 3. Reply

1. A table of the flows: readiness, what blocks each, and how many questions it has.
2. Each auditor's reply as it is, ordered ready → needs answers → blocked.
3. **Across flows:** questions that appear in more than one flow, and flows waiting on each other.

Report only. Never edit the docs. Changes go through a docs pull request (`GUIDE.md` §7).
