---
name: analyze-requirements
description: Read and summarise a LedgerVision feature's requirements from the docs (the source of truth) before building, changing or answering questions about it. Use when starting a feature, when asked what a feature should do, or when checking a behaviour, field or role rule.
---

# Analyze requirements

The `docs/` submodule (`ledgerai-project-docs`) is the source of truth for what to build. The flows act as the product and functional requirements, and `TRD.md` holds the technical requirements. There is no separate BRD or PRD. If someone refers to one, ask them for it rather than assuming its content.

| Source | Settles |
|---|---|
| `docs/flow/README.md` | Which flow covers the feature, and its status (✅ approved / 📝 draft) |
| `docs/flow/<feature>.md` | Behaviour, screens, states, messages, roles, decisions, open questions |
| `docs/data-dictionary/` (`README.md` maps tables to files) | Every table and field |
| `docs/TRD.md` | Technical requirements: stack, API, security, data, jobs, non-functional. Only ✅ items are settled |
| `docs/TEAM-RULES.md` | The rules every repo follows |
| `docs/VERSION.md` | What changed recently |

## Steps

1. Find the feature in `docs/flow/README.md` and note its status.
2. Read the whole flow doc, including its diagrams.
3. Separate what's settled from what isn't. In a 📝 draft, "Proposed decisions" and "Open questions" are not settled (see `docs/TEAM-RULES.md` §6).
4. Read the dictionary sections for every table the flow names.
5. Note every conflict between the flow and the dictionary, and every field the flow needs that the dictionary lacks (the flow's "Data dictionary gaps" section). Raise these. Don't resolve them yourself.
6. Check `docs/VERSION.md` for recent changes to the feature.

## Summary format

Quote the doc section for each point (e.g. `authentication.md §6c`) instead of paraphrasing it at length.

- **Feature / flow / status**
- **Screens and routes**, each with its states
- **Roles:** what each role can see and do, and the branch scope
- **Data:** tables and fields used, by dictionary name
- **Rules:** validations, limits, expiries and messages (with section references)
- **Not settled:** proposed decisions and open questions
- **Conflicts and gaps**

Never edit `docs/`. Changes go through a docs pull request (`docs/GUIDE.md` §7).
