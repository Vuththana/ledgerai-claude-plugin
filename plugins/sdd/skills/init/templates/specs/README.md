# LedgerVision Specs

One folder per feature. Each holds the whole life of the feature, from idea to shipped:

```
specs/<feature>/spec.md    WHAT  — requirements with IDs (📝 draft → ✅ approved)
specs/<feature>/plan.md    HOW   — the approved plan, against one version of the spec
specs/<feature>/tasks.md   WORK  — ordered, checkable tasks, each covering requirement IDs
specs/<feature>/trace.md   PROOF — generated: requirement → plan → task → test → QA, plus drift
```

The formats are defined once, in [`_templates/`](_templates/). The data dictionary, API reference, TRD and team rules stay shared at the top of this repo.

## Lifecycle

| Stage | Command (sdd plugin) | Output | Gate |
|---|---|---|---|
| Specify | `/sdd:specify <idea>` | `spec.md` 📝 | |
| Clarify | `/sdd:clarify <feature>` | answers applied to spec, dictionary, `api/`; spec ✅ | ⏸ team approves the spec |
| Plan | `/sdd:plan <feature>` | `plan.md` | ⏸ team approves the plan |
| Tasks | `/sdd:tasks <feature>` | `tasks.md` | |
| Build | `/sdd:build <feature>` | code + tests named with IDs | |
| Verify | `/sdd:verify <feature>` | review findings, fixes | |
| QA | `/sdd:qa <feature>` | `qa-reports/` in each repo | |
| Trace | `/sdd:trace <feature>` | `trace.md` | |
| Ship | `/sdd:ship <feature>` | commits, pushes | ⏸ team approves the push |

`/sdd:run <feature>` runs Plan → Ship with the gates. `/sdd:amend <feature>` is the only way to change an approved spec. `/sdd:status` shows where every feature is.

## IDs

Each spec has a prefix (below). `XXX-R` requirement · `XXX-E` edge case · `XXX-D` decision · `XXX-Q` open question · `XXX-M` message · `T` task · `XXX-R03-V1` QA scenario. IDs are never renumbered or reused. Tests put the ID first in their name so the trace can find them.

## Features

| # | Feature | Spec | Prefix | Status | Stage |
|---|---|---|---|---|---|

<!-- One row per feature, kept by the sdd commands. Status: ✅ Approved · 📝 Draft · ⟳ Amending.
     Stage: spec · plan · tasks · build · verify · qa · M1 shipped (web-ui static UI done, integration open) · shipped. Features not migrated yet are still in ../flow/. -->
