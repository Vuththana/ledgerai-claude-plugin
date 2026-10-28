# ledgerai-claude-plugin

The shared Claude Code **workflows** for the LedgerVision AI team. Every repo (web-ui, backend, ...) installs plugins from here, so everyone runs the same step-by-step tasks the same way.

## Where things are defined

Each kind of information has one home, so nothing is written twice and nothing drifts:

| Layer | Where | Holds | Shared how |
|---|---|---|---|
| **What to build** (source of truth) | `docs/` submodule (`ledgerai-project-docs`): `flow/`, `data-dictionary/`, `TEAM-RULES.md` | Behaviour, screens, messages, roles, every table and field, team rules | The submodule, in every repo |
| **Project instructions** | `CLAUDE.md` in each repo | Commands, stack, architecture | Committed in each repo |
| **Rules: coding standards and constraints** | `.claude/rules/*.md` in each repo | Team rules (always loaded) and coding standards (loaded when matching files are touched, via `paths:`) | Committed in each repo |
| **Workflows** | **this repo**: plugin skills | Step-by-step tasks that *point to* the docs and rules | These plugins |

**Skills never restate the docs or the rules.** A skill like "implement authentication" would just copy `docs/flow/authentication.md`, then drift from it. Instead, `implement-feature` walks through the build, and the flow plus the rules supply the content.

Plugins can't ship `CLAUDE.md` or rules files: Claude Code only loads skills, agents, hooks and MCP servers from a plugin. That's why rules live in each repo. For Spring Boot services, `/springboot-dev:setup-service` copies them into the repo from its template.

## The plugins

| Plugin | Id | Enable it in |
|---|---|---|
| `ledgerai` | `ledgerai@ledgerai` | **every** repo |
| `website-dev` | `website-dev@ledgerai` | web front-end repos (web-ui) |
| `springboot-dev` | `springboot-dev@ledgerai` | Spring Boot service repos (identity, sales, finance, api-gateway) |

### 01. Requirements & Analysis

| Skill | Plugin | How | What it does |
|---|---|---|---|
| `analyze-requirements` | ledgerai | Auto | Reads the feature's flow and dictionary tables, separates settled from draft, and lists conflicts and gaps with doc references |
| `document-feature` | ledgerai | `/ledgerai:document-feature <feature>` | Writes the plan required by `TEAM-RULES.md` §3 before any code. Stops on 📝 draft flows and asks their open questions |
| `identify-edge-cases` | ledgerai | Auto | A checklist of *what to look for* (states, validation, permissions, limits). The values come from the docs |

### 02–03. UI and frontend implementation

| Skill | Plugin | How | What it does |
|---|---|---|---|
| `implement-feature` | website-dev | Auto | The build order, from the approved plan to the checks. Each step names the rule that applies |
| `figma-design` | website-dev | Auto | Finds a screen in the Figma design (section → node index, Owner and Branch Manager rows), reads it with the Figma plugin, adapts it to our components and tokens, and checks it against the flow and dictionary |

Components, forms, data tables, dashboards, API integration, authentication, roles, responsive and accessibility are **not skills**. They are web-ui rules (`ui-components.md`, `forms.md`, `data-tables.md`, `drag-and-drop.md`, `data-layer.md`, `nextjs.md`) plus the feature's flow doc.

### 02–03. Backend implementation (Spring Boot)

| Skill | Plugin | How | What it does |
|---|---|---|---|
| `setup-service` | springboot-dev | `/springboot-dev:setup-service [service]` | Installs `.claude/settings.json`, `CLAUDE.md`, `.claude/rules/` and the `docs` submodule in a service repo, fills them from `docs/TRD.md` §1a, and reports where the repo differs from the TRD |
| `implement-feature` | springboot-dev | Auto | The backend build order: migration → entities → endpoints → events, jobs, emails → tests → `./gradlew build` → run the stack and `curl` each role → reviews |
| `add-migration` | springboot-dev | Auto | A Flyway migration straight from the dictionary (types, NOT NULL, defaults, enums, unique, keys, indexes), only for tables this service owns |
| `add-endpoint` | springboot-dev | Auto | One endpoint: DTOs with dictionary validation, service with role and branch scope, controller, error codes, messages and tests |

Entities, security, error handling, ModelMapper, events and jobs are **not skills**. They are the Spring rules (`spring.md`, installed by `setup-service`) plus `docs/TRD.md`.

### 04. Security & Quality

| Skill | Plugin | How | What it does |
|---|---|---|---|
| `review-feature` | ledgerai | `/ledgerai:review-feature <feature>` | Checks the implementation requirement by requirement against the flow, plus the dictionary and role checks |
| `check-hardcoded-values` | website-dev | Auto, before every `git push` | Scans the commits about to be pushed for hardcoded URLs, hosts, client IDs and secrets, and secrets in `NEXT_PUBLIC_` variables. Stops the push and lists what must go in the `.env` (and `.env.example`) |

### 05. Testing

| Skill | Plugin | How | What it does |
|---|---|---|---|
| `write-unit-tests`, `write-component-tests`, `write-e2e-tests` | website-dev | Auto | **Placeholders.** There's no test runner yet. They say so, offer to draft a package request, and list what to cover |
| `debug-frontend` | website-dev | Auto | How to debug, plus a symptom → cause → rule table for this stack |
| `write-tests` | springboot-dev | Auto | JUnit 5 + Mockito unit tests and Testcontainers integration tests, with every error code and every role covered |
| `debug-backend` | springboot-dev | Auto | How to debug, plus a symptom → cause → rule table for Spring Boot, Flyway, Keycloak, Consul and RabbitMQ |
| `qa` | ledgerai | `/ledgerai:qa <feature> [base-url]` | Black-box QA of a built feature against its ✅ flow, in three kinds (correctness, validation, misuse). Picks the tester for the repo: `qa-web` in web-ui, `qa-api` in a service. Writes `qa-reports/<date>-<feature>.md` and replies with the counts and failures |
| `qa-method` | ledgerai | Preloaded by the QA agents | The shared method: find the spec, write every scenario first, run rules, report format. Not run directly |

### 06. Maintenance & Collaboration

| Skill | Plugin | How | What it does |
|---|---|---|---|
| `review-pull-request` | website-dev | `/website-dev:review-pull-request [PR \| branch]` | Checks the diff against `TEAM-RULES.md` §9 and the matching `.claude/rules/`, plus mechanical checks (dictionary, `lib/mock` imports, dependencies, `docs/`, lint, build) |
| `review-pull-request` | springboot-dev | `/springboot-dev:review-pull-request [PR \| branch]` | The same review for a service: dictionary, edited migrations, table ownership, scope in queries, dependencies, secrets, error format, `docs/`, tests, build |
| `manage-dependencies` | ledgerai | Auto | Checks whether a package is needed and evaluates it. In web-ui it fills in the `TEAM-RULES.md` §7 request template and never installs before approval; backend repos need no request |
| `sync-project-specs` | ledgerai | `/ledgerai:sync-project-specs` | Reports whether `docs/` is behind, what changed (MAJOR/MINOR/PATCH) and what it affects, and updates on request |

Use the built-in `/simplify` for refactoring and `/code-review` for a general bug hunt.

### Agent and hook

| | Plugin | What it does |
|---|---|---|
| `dictionary-checker` agent | ledgerai | Compares types, forms, validation, mock data, JPA entities, DTOs and Flyway migrations with `docs/data-dictionary/`, and reports mismatches. Never edits the dictionary |
| `qa-web` agent | website-dev | The web tester behind `/ledgerai:qa`: the running app in the browser (Playwright MCP), on the mock API, codes from the dev log, seeded accounts changed last. Never edits code |
| `qa-api` agent | springboot-dev | The service tester behind `/ledgerai:qa`: IDE diagnostics (`/ide`) and the feature's Gradle tests first, then every endpoint through Swagger UI (Playwright MCP), codes from Mailpit, database and Redis checked read-only. May start the local stack; never edits code |
| ESLint hook | website-dev | After Claude edits a `.ts/.tsx/.js/.jsx/.mjs/.cjs` file, runs `node_modules/.bin/eslint --fix` on it. Does nothing without ESLint. Needs `jq` |
| Compile-check hook | springboot-dev | After Claude edits a `.java` file, runs `./gradlew compileJava` (or `compileTestJava`) and hands any compiler errors back to Claude. Does nothing without a Gradle wrapper. Needs `jq` |

### Typical feature workflow

```
/ledgerai:sync-project-specs          docs up to date?
/ledgerai:document-feature <feature>  plan → team approves
  build: implement-feature (rules load as files are touched)
/ledgerai:review-feature <feature>    matches the flow?
/ledgerai:qa <feature>                works in the browser / through Swagger UI?
/website-dev:review-pull-request      follows the rules?     (web-ui)
/springboot-dev:review-pull-request   follows the rules?     (Spring services)
```

A new Spring service repo starts with `/springboot-dev:setup-service` once.

---

## Installing (team members)

### Automatic (recommended)

Each LedgerVision repo enables its plugins in its committed `.claude/settings.json`. In web-ui, that's both:

```json
"extraKnownMarketplaces": {
  "ledgerai": {
    "source": { "source": "github", "repo": "Vuththana/ledgerai-claude-plugin" }
  }
},
"enabledPlugins": {
  "ledgerai@ledgerai": true,
  "website-dev@ledgerai": true
}
```

1. Pull the repo and run `claude` in it.
2. Trust the folder when asked.
3. Claude Code asks you to install the `ledgerai` marketplace and its plugins. Accept.

Run `/plugin` and check that both show under **Installed**.

### Manual

```
/plugin marketplace add Vuththana/ledgerai-claude-plugin
/plugin install ledgerai@ledgerai
/plugin install website-dev@ledgerai      # web repos only
/plugin install springboot-dev@ledgerai   # Spring Boot service repos only
```

> **Private repo.** Claude Code clones it with your own git credentials. You need read access on GitHub (ask to be added as a collaborator) and a working login (`gh auth login`, or an SSH key / credential helper).

### Updates

```
/plugin marketplace update ledgerai
```

Then restart Claude Code. **You only get a plugin's changes when its `version` in `plugin.json` goes up.**

### Turning a plugin off

```
/plugin disable website-dev@ledgerai     # stop it running
/plugin uninstall website-dev@ledgerai   # remove it
```

Only for you, in one repo: `{ "enabledPlugins": { "website-dev@ledgerai": false } }` in `.claude/settings.local.json`.

---

## Adding the plugins to a new repo

**Spring Boot service** (identity, sales, finance, api-gateway):

1. Install the plugins once by hand (`/plugin install ledgerai@ledgerai` and `/plugin install springboot-dev@ledgerai`).
2. Run `/springboot-dev:setup-service`. It installs the settings, `CLAUDE.md`, rules and `docs` submodule from `plugins/springboot-dev/skills/setup-service/template/`.
3. Review and commit.

**Anything else:**

1. Copy a template to `<repo>/.claude/settings.json`: `templates/web-project-settings.json` for a web front end (both plugins), or `templates/project-settings.json` for anything else (`ledgerai` only). Adjust the permissions.
2. Add the `docs` submodule at `docs/`.
3. Write the repo's `CLAUDE.md` (commands, stack, architecture) and its `.claude/rules/`: the repo's version of `docs/TEAM-RULES.md`, plus its own coding standards.
4. Commit all of it.

---

## Changing the plugins (maintainers)

### Skill or rule?

| If it's... | Put it in |
|---|---|
| What a feature does, a field, a message, a limit | **The docs** (via a docs PR). Never in a skill or rule |
| How code is written in one repo: conventions, libraries, patterns | **That repo's `.claude/rules/`**, scoped with `paths:` |
| A team rule for every repo | **`docs/TEAM-RULES.md`**, mirrored in each repo's rules |
| A repeatable task with steps (plan, review, sync, build order) | **A skill here** that points to the docs and rules |

A skill that only lists facts or conventions is really a rule or a doc. Move it.

### Layout

```
.claude-plugin/marketplace.json
plugins/ledgerai/        .claude-plugin/plugin.json · agents/ · skills/<name>/SKILL.md            (8 skills)
plugins/website-dev/     .claude-plugin/plugin.json · agents/ · hooks/ · skills/<name>/SKILL.md  (8 skills)
plugins/springboot-dev/  .claude-plugin/plugin.json · agents/ · hooks/ · skills/<name>/SKILL.md  (7 skills)
                         skills/setup-service/template/   settings.json · CLAUDE.md · rules/ for a service repo
templates/               project-settings.json · web-project-settings.json
```

Skills sit directly at `skills/<name>/SKILL.md`, because Claude Code doesn't look in subfolders. The 01–06 grouping lives in this README.

### Writing a skill

```markdown
---
name: <skill-name>                       # same as the folder
description: <what it does>. Use when <situations that should trigger it>.
argument-hint: <args>                    # optional
disable-model-invocation: true           # optional: runs only when typed (/plugin:name)
---
```

- The description decides when Claude loads the skill. Name the situations.
- Auto skills keep their description in every session's context, so keep them few and short.
- Use `disable-model-invocation: true` for tasks people choose to run (plans, reviews, syncs).

Hooks run in every repo that enables the plugin. Make them check that they apply, and exit 0 when they don't.

### Test locally

```bash
claude plugin validate ../ledgerai-claude-plugin
claude plugin validate ../ledgerai-claude-plugin/plugins/ledgerai
claude plugin validate ../ledgerai-claude-plugin/plugins/website-dev
claude plugin validate ../ledgerai-claude-plugin/plugins/springboot-dev
claude --plugin-dir ../ledgerai-claude-plugin/plugins/ledgerai \
       --plugin-dir ../ledgerai-claude-plugin/plugins/website-dev
```

The icon and license warnings only matter for the public plugin directory, so ignore them.

### Release

1. Bump `version` in the changed plugin's `plugin.json`, and add a changelog line.
2. Commit and push to `main`.
3. Tell the team to run `/plugin marketplace update ledgerai`.

## Changelog

| Plugin | Version | Change |
|---|---|---|
| `website-dev` | 0.5.0 | New `check-hardcoded-values` skill: before every push, finds hardcoded URLs, hosts, client IDs and secrets (and secrets in `NEXT_PUBLIC_` variables) in the commits to push, and tells the user they must go in the `.env` |
| `ledgerai` | 0.8.0 | New `/ledgerai:qa <feature>` skill and the shared `qa-method` skill: one QA method for every repo (three kinds, scenarios first, report in `qa-reports/`), which picks the repo's tester. Each ❌ gets a severity (Blocker / Major / Minor) |
| `website-dev` | 0.4.0 | New `qa-web` agent: web-ui's QA tester, moved here from web-ui's `.claude/` and built on `qa-method`, with the browser misuse cases (URLs past the gate, back after sign-out, refresh mid-flow, tampered query strings). `implement-feature` and `review-pull-request` check each `src/lib/api` function and its mock against its endpoint in `docs/api/<service>.md` |
| `springboot-dev` | 0.8.0 | New `qa-api` agent: QA for a service through Swagger UI (Playwright MCP), after IDE diagnostics and the feature's Gradle tests; a checklist for each endpoint (every listed error code, required / length / enum / type, tokens, roles, other business's ids), owner + manager setup for role scenarios; Mailpit codes; read-only database and Redis checks. Merges identity-service's local `qa-tester` agent |
| `springboot-dev` | 0.7.0 | One shared infrastructure (docs v4.6.0): new `infrastructure.md` rule in the service template (identity-service owns `infra/`; other services never copy it, they hold only their service, Consul config and compose on `ledgervision-net`); `setup-service` checks the compose file, port and Consul name against `docs/TRD.md` §1b |
| `springboot-dev` | 0.6.0 | Endpoints go in the API reference (docs v4.5.0): `add-endpoint` step 6 lists each new or changed endpoint in `docs/api/<service>.md`; `implement-feature`, `review-pull-request` and the `workflow.md` template check it |
| `ledgerai` | 0.7.0 | `analyze-requirements` reads `docs/api/<service>.md` for the endpoints that exist |
| `website-dev` | 0.3.0 | New `figma-design` skill: the team's Figma file (Copy of FinSight), a section → node index, and how to read and adapt a screen. `implement-feature` step 3 points to it |
| `springboot-dev` | 0.5.0 | `spring.md` template follows docs v4.3.0: success `code` is the HTTP status name (`ApiResponse.ok` / `created`), no `204` without a body |
| `ledgerai` | 0.6.0 | Package requests are for web-ui only (docs v3.1.0): `manage-dependencies` and `document-feature` stop asking backend repos for one |
| `springboot-dev` | 0.4.0 | The same for the backend: `packages.md` and `workflow.md` templates, `setup-service`, `implement-feature`, `write-tests`, `review-pull-request` |
| `ledgerai` | 0.5.0 | `dictionary-checker` checks JSONB content against `docs/data-dictionary/jsonb-shapes.md` (docs v4.1.0): mismatches for ✅ shapes, notes for 📝 proposed ones. `analyze-requirements` reads the shapes too |
| `springboot-dev` | 0.3.0 | The `data-dictionary.md` rule template points to `jsonb-shapes.md` for the keys inside `jsonb` columns |
| `springboot-dev` | 0.2.0 | Follows `docs/TRD.md` v3.0.0: `ApiResponse` envelope with `code`, one schema per service, OpenFeign + Resilience4j, Consul KV config, S3/RustFS, Zipkin, springdoc. `setup-service` checks for them, and `debug-backend` covers Consul, Feign and schemas |
| `springboot-dev` | 0.1.0 | New: `setup-service` (installs the service template: settings, `CLAUDE.md`, `.claude/rules/` incl. `spring.md`, built from `docs/TRD.md` v2.0.0), `implement-feature`, `add-migration`, `add-endpoint`, `write-tests`, `debug-backend`, `review-pull-request`, and the compile-check hook |
| `ledgerai` | 0.4.0 | `dictionary-checker` also checks Java entities, DTOs and Flyway migrations |
| `ledgerai` | 0.3.0 | Workflow-only skills that point to the docs: `analyze-requirements`, `document-feature` (was `/ledgerai:plan-feature`), `identify-edge-cases`, `review-feature`, `manage-dependencies` (uses the `TEAM-RULES.md` §7 template), `sync-project-specs` |
| `website-dev` | 0.2.0 | Workflow-only skills: `implement-feature`, `debug-frontend`, `review-pull-request`, three test placeholders. Standards moved to web-ui `.claude/rules/`. Removed `nextjs-16`, `hairline-ui`, `mock-api-layer` |
| `ledgerai` | 0.2.0 | Added `dictionary-checker` agent and `/ledgerai:plan-feature`. ESLint hook moved to `website-dev` |
| `website-dev` | 0.1.0 | New: `nextjs-16`, `hairline-ui`, `mock-api-layer` skills and the ESLint hook |
| `ledgerai` | 0.1.0 | First release: ESLint hook |
