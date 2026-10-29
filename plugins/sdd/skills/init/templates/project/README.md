# <Project> docs

<One-line description of the product and who it's for.>

These docs are the source of truth for **what** to build. Code repos read them; nothing here is code. Features are built spec-first with the `sdd` Claude Code plugin.

## Layout

| Folder / file | Holds |
|---|---|
| [`specs/`](specs/README.md) | One folder per feature: `spec.md` (what, with requirement IDs), `plan.md` (how), `tasks.md` (the work), `trace.md` (proof) |
| [`data-dictionary/`](data-dictionary/README.md) | Every table and field: name, type, length, required, default, rules |
| [`api/`](api/README.md) | Every endpoint, per service: method, path, who, body, response, error codes |
| [`TRD.md`](TRD.md) | Technical requirements: services, stack, API, security, data, jobs |
| [`TEAM-RULES.md`](TEAM-RULES.md) | The rules every team member and every repo follows |
| [`VERSION.md`](VERSION.md) | What changed, newest first |

## Start here

1. Settle the stack and services in [`TRD.md`](TRD.md) (📝 items are proposals; ❓ items are open).
2. Write the first feature: `/sdd:specify <the feature in a sentence>`.
3. Answer its questions and approve it: `/sdd:clarify <feature>`.
4. Build it: `/sdd:run <feature>` (needs the code repos next to this folder).

`/sdd:status` shows where every feature stands.

## Contributing

Every change is a pull request with an entry in [`VERSION.md`](VERSION.md). An approved (✅) spec changes only through `/sdd:amend`.
