# Feature flows: approved vs draft

`docs/flow/` holds the agreed behaviour of each feature: user journeys (Mermaid diagrams), field rules, permissions and decisions. **Read the feature's flow before you plan or build it.** `docs/flow/README.md` lists each flow's status.

| Status | Meaning | What you may do |
|---|---|---|
| ✅ Approved | Settled. | Build against it. |
| 📝 Draft | "Proposed decisions" and "Open questions" still need an answer. | Read it, plan with it, and raise its open questions. **Don't build on a guess.** Get the questions answered and the flow approved first. |

- Never treat a draft's "Proposed decisions" or "Recommended" answers as agreed. Ask.
- A flow never silently changes a field. Gaps sit under "Data dictionary gaps" in the flow until the team confirms them in the docs repo.
- If the backend needs to behave differently from an approved flow, change the flow first (a PR to the docs repo), then the code.
- **Steps marked *server*** in a flow are this backend's requirements, for the service that owns the feature (`docs/TRD.md` §1a).
- Paths like `src/lib/api/auth` in a flow refer to the web UI's mock services. The real endpoint must return what that mock returns, with the same field names and error codes.
- Technical rules that aren't in a flow (stack, auth, errors, events, jobs) are in `docs/TRD.md`. Its ✅ rows are settled. Its 📝 and ❓ rows need the team's answer before you build on them.
