---
name: dev-team
description: Run the LedgerVision dev team on one feature, across every repo it touches — analyst → planner → you approve the plan → backend and frontend developers in parallel → reviewers in parallel → fixes → QA → hardcoded-values check → you approve the push. Usage /ledgerai:dev-team <feature>.
argument-hint: <feature name, e.g. "dashboard">
disable-model-invocation: true
---

# Dev team: $ARGUMENTS

You are the **lead**. You don't write feature code. You start the teammates with the Agent tool, pass work between them, and hold the two approval gates. Anything a teammate can't do (ask the user, start another agent, get a doc change confirmed) comes back to you.

## The team

| Role | Agent (`subagent_type`) | Works in | Edits |
|---|---|---|---|
| Analyst | `ledgerai:requirements-analyst` | the docs | no |
| Planner | `ledgerai:feature-planner` | every repo involved | no |
| Backend dev | `springboot-dev:backend-dev`, one per service repo | a Spring Boot service | yes |
| Frontend dev | `website-dev:frontend-dev` | web-ui | yes |
| AI dev | `fastapi-dev:ai-dev` | ai-service | placeholder, not ready |
| Reviewers | `ledgerai:feature-reviewer`, `ledgerai:dictionary-checker`, `website-dev:pr-reviewer-web`, `springboot-dev:pr-reviewer-api` | every repo involved | no |
| QA | `springboot-dev:qa-api`, `website-dev:qa-web`, `fastapi-dev:qa-ai` (placeholder) | the running app | `qa-reports/` only |

## Rules for the lead

- **Teammates see only what you pass them.** Hand over the brief and the findings word for word, never a summary, and the approved plan as its file's absolute path (§2).
- **Name the absolute repo path(s)** in every prompt to a developer or reviewer.
- **Teammates can't ask the user.** When one comes back with questions or "needs confirmation" items, ask the user (with AskUserQuestion when the answers are choices). Then continue **the same teammate** with SendMessage and the answers, so it keeps its context.
- **One feature only** (`docs/TEAM-RULES.md` §2). Work runs in parallel inside the feature, never across features.
- **Never push, merge, comment on GitHub or edit the `docs/` submodule** yourself. Teammates don't either (see their instructions). The plan and the API reference entries go in a separate docs clone (§2), pushed only at Gate 2.
- A teammate that fails or returns something unusable: run it once more with the problem named. If it fails again, tell the user. Don't quietly do its work yourself.
- Keep the user posted in one line per step: what's running, what came back.

## 0. Repos

1. **Find the repos.** In a single repo, that's the current directory. In the workspace folder (e.g. `LedgerVisionAI/`, with the repos as subfolders), it's every subfolder that is a git repo with a `docs/` submodule. Name each repo's stack:

   | The repo has | Stack | Developer | Tester |
   |---|---|---|---|
   | `package.json` with `next` | web-ui | `website-dev:frontend-dev` | `website-dev:qa-web` |
   | `build.gradle` with `org.springframework.boot` | Spring service | `springboot-dev:backend-dev` | `springboot-dev:qa-api` |
   | `pyproject.toml` with `fastapi` | ai-service | `fastapi-dev:ai-dev` | `fastapi-dev:qa-ai` |

2. **Same docs everywhere.** `git -C <repo> submodule status docs` must show the same commit in every repo. If not, stop and suggest `/ledgerai:sync-project-specs` in the ones that are behind.

## 1. Requirements

Start `ledgerai:requirements-analyst`:

> Brief the **$ARGUMENTS** feature. Docs: **<absolute path of one repo's docs/>**.

- **The flow is 📝 draft,** or the brief has **Blocking** items: show them, and **stop**. Suggest `/ledgerai:audit-flow $ARGUMENTS` to prepare the questions for the team.
- The brief names a service whose repo isn't here: say so, and stop.

## 2. Plan

Start `ledgerai:feature-planner`:

> Plan the **$ARGUMENTS** feature. Repos: **<absolute path of each repo the brief names>**.
>
> Requirements brief:
> <the brief, word for word>

**⏸ Gate 1:** show the plan as it is, and ask the user to approve it or ask for changes. For changes, continue the planner with SendMessage. **Don't go on without an explicit approval.**

**Save the plan** as `plans/<flow file>.md` in the docs repo (`docs/plans/README.md` has the format and the rules):

1. Use a separate clone of `ledgerai-project-docs`, never a `docs/` submodule. In the workspace folder, that's the sibling `ledgerai-project-docs/`; otherwise ask the user where one is. If it has uncommitted changes, ask before touching it.
2. `git -C <clone> fetch`, then `git -C <clone> switch -c feature/<feature-slug> origin/main` (or switch to it if it exists). This **docs branch** also gets the feature's API reference entries (§3).
3. Write the file: the header from `plans/README.md` (docs version from `git -C <repo>/docs describe --tags --always`, approved by the user), the plan as approved, word for word, and an empty Changes table.
4. Commit it with its `VERSION.md` entry: `Plan: <feature> (v<X.Y.Z>)`. Don't push.

From here on, the **plan file** is the plan: developers and reviewers read it there.

Then check that each developer the plan needs is available (its plugin is enabled here). If one isn't, stop and say which plugin to enable, or suggest starting from the workspace folder with `templates/workspace-settings.json` (plugin README). An ai-service part means `fastapi-dev:ai-dev`, which is a placeholder: stop and say the AI side isn't ready, and list what it's waiting on (from the agent's instructions).

## 3. Build

Start one developer per repo **in one message**, so they work in parallel, with:

> Build your part of the **$ARGUMENTS** feature in **<absolute repo path>**. Your part: <its "Repos and parts" entry>.
>
> Requirements brief:
> <word for word>
>
> Approved plan: **<absolute path of the plan file>**. Read it in full before you start, and again whenever I tell you it changed.

- If the plan says something must come first (e.g. an endpoint another service calls), start that developer first and the others when it reports done. web-ui builds against the plan's API contract on the mock, so it doesn't wait for the backend.
- **Questions** from a developer: ask the user, then SendMessage the answers.
- **A change to the plan** (from an answer, or the user asks for one): continue the planner with SendMessage, and show the user the change. Once they approve it, update the plan file, add a row to its Changes table, commit, and tell every developer to read it again (`docs/TEAM-RULES.md` §3).
- **Endpoints to confirm** (`add-endpoint` §6): show the user each endpoint and its draft API reference entry. When the user confirms one, tell that backend developer to write the entry in the docs clone, on the docs branch, without committing. You commit them in §7.
- **Package requests** (web-ui): show the draft, then file it with the user as `ledgerai:manage-dependencies` §4 says (who's asking, which browser, confirm the row, fill the team sheet, check it saved). Nothing gets installed until the sheet says **Approved** (`docs/TEAM-RULES.md` §7). Ask the user how to go on without it.

## 4. Review

When every developer reports done, start the reviewers **in one message**:

- `ledgerai:feature-reviewer` once, with every repo path and the plan: *Review the **$ARGUMENTS** feature in <paths>. Approved plan: <plan file>.*
- per repo, `ledgerai:dictionary-checker`: *Check the files changed in <repo path> (working tree against `main`).*
- per repo, its PR reviewer (`website-dev:pr-reviewer-web` or `springboot-dev:pr-reviewer-api`): *Review the working tree of <repo path> against `main`.*

## 5. Fix

1. Sort the findings by repo. Send each developer its **Blocking** and **Should fix** findings, word for word, with SendMessage.
2. Keep the **Nits** and the **Flow gaps** for the final summary. Don't send them.
3. When the fixes are in, run again only the reviewers that had Blocking findings.
4. **At most two fix rounds.** After that, list what's left for the user.

## 6. QA

Only for a ✅ flow (`qa-method` requires it). Services first, then web-ui, **one tester at a time**: they share the Playwright browser.

> QA the **$ARGUMENTS** feature at **<base-url>**. Work in **<absolute repo path>**. Follow the preloaded `qa-method` skill: find the spec, write every scenario first, run them, write the report to `qa-reports/`, and reply with the summary only.

The base URLs are in the `/ledgerai:qa` skill. web-ui must be running on the mock (`MOCK_API=1`, see web-ui's `CLAUDE.md`). If it isn't, ask the user to start it.

Send each **Blocker** and **Major** ❌ to its developer (that counts as a fix round), then run that tester once more.

## 7. Before the push

1. In each repo, follow the `ledgerai:check-hardcoded-values` skill on the working tree. Show what it finds.
2. **Docs branch:** if API reference entries were written, add them to the plan's `VERSION.md` entry with their **Impact** (new endpoints make it a MINOR), and commit them.
3. Summarise, per repo: branch, files changed, checks run with their results, review verdicts, QA counts and report path, and what's still open (API reference entries not written yet, nits, flow gaps, dictionary gaps, findings left after two rounds). Then the docs branch: the plan file, its Changes rows, and the API reference entries on it.

**⏸ Gate 2:** ask the user whether to commit and push each repo, and whether to push the docs branch. Do it only for the ones they approve. Opening pull requests is a separate question: the docs pull request is merged no later than the code (`docs/plans/README.md`).
