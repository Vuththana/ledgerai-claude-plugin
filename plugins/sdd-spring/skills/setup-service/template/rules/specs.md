# Specs: approved vs draft (SDD)

`docs/specs/<feature>/` holds each feature's life: `spec.md` (what, with requirement IDs), `plan.md` (how), `tasks.md` (the work), `trace.md` (proof). `docs/specs/README.md` lists each spec's status and stage. **Read the feature's spec before you plan or build it.** Features not migrated yet are still in `docs/flow/` (v1); migrate them with `/sdd:migrate` before building.

| Status | Meaning | What you may do |
|---|---|---|
| ✅ Approved | Settled. | Plan and build against it. |
| 📝 Draft | Open `Q`s or "Proposal:" decisions. | Read it and raise its questions (`/sdd:clarify`). **Don't build on a guess.** |
| ⟳ Amending | An approved spec being changed. | Tasks marked ⟳ wait for the amendment. |

- **IDs.** Requirements `XXX-R01`, edge cases `XXX-E01`, messages `XXX-M01`, decisions `XXX-D01`. Every test's `@DisplayName` starts with the ID it proves, so `/sdd:trace` can count it.
- A spec never silently changes a field. Gaps sit in its §8 until `/sdd:clarify` applies them to the dictionary.
- If the backend must behave differently from an approved spec, **change the spec first** (`/sdd:amend`), then the code.
- Steps marked *server* in a spec are this backend's requirements, for the service that owns the feature (`docs/TRD.md` §1a). Message texts (`M` IDs) go into `messages.properties` word for word.
- Paths like `src/lib/api/auth` refer to the web UI's mock. The real endpoint must return what the plan's §3 contract says, with the same field names and error codes.
- Technical rules that aren't in a spec (stack, auth, errors, events, jobs) are in `docs/TRD.md`. Its ✅ rows are settled; 📝 and ❓ rows need the team's answer first.
