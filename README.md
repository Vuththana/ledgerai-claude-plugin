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

Plugins can't ship `CLAUDE.md` or rules files: Claude Code only loads skills, agents, hooks and MCP servers from a plugin. That's why rules live in each repo.

## The plugins

| Plugin | Id | Enable it in |
|---|---|---|
| `ledgerai` | `ledgerai@ledgerai` | **every** repo |
| `website-dev` | `website-dev@ledgerai` | web front-end repos (web-ui) |

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

Components, forms, data tables, dashboards, API integration, authentication, roles, responsive and accessibility are **not skills**. They are web-ui rules (`ui-components.md`, `forms.md`, `data-tables.md`, `drag-and-drop.md`, `data-layer.md`, `nextjs.md`) plus the feature's flow doc.

### 04. Security & Quality

| Skill | Plugin | How | What it does |
|---|---|---|---|
| `review-feature` | ledgerai | `/ledgerai:review-feature <feature>` | Checks the implementation requirement by requirement against the flow, plus the dictionary and role checks |

### 05. Testing

| Skill | Plugin | How | What it does |
|---|---|---|---|
| `write-unit-tests`, `write-component-tests`, `write-e2e-tests` | website-dev | Auto | **Placeholders.** There's no test runner yet. They say so, offer to draft a package request, and list what to cover |
| `debug-frontend` | website-dev | Auto | How to debug, plus a symptom → cause → rule table for this stack |

### 06. Maintenance & Collaboration

| Skill | Plugin | How | What it does |
|---|---|---|---|
| `review-pull-request` | website-dev | `/website-dev:review-pull-request [PR \| branch]` | Checks the diff against `TEAM-RULES.md` §9 and the matching `.claude/rules/`, plus mechanical checks (dictionary, `lib/mock` imports, dependencies, `docs/`, lint, build) |
| `manage-dependencies` | ledgerai | Auto | Checks whether a package is needed, evaluates it, and fills in the `TEAM-RULES.md` §7 request template for you. Never installs before approval |
| `sync-project-specs` | ledgerai | `/ledgerai:sync-project-specs` | Reports whether `docs/` is behind, what changed (MAJOR/MINOR/PATCH) and what it affects, and updates on request |

Use the built-in `/simplify` for refactoring and `/code-review` for a general bug hunt.

### Agent and hook

| | Plugin | What it does |
|---|---|---|
| `dictionary-checker` agent | ledgerai | Compares types, forms, validation and mock data with `docs/data-dictionary/`, and reports mismatches. Never edits the dictionary |
| ESLint hook | website-dev | After Claude edits a `.ts/.tsx/.js/.jsx/.mjs/.cjs` file, runs `node_modules/.bin/eslint --fix` on it. Does nothing without ESLint. Needs `jq` |

### Typical feature workflow

```
/ledgerai:sync-project-specs          docs up to date?
/ledgerai:document-feature <feature>  plan → team approves
  build: implement-feature (rules load as files are touched)
/ledgerai:review-feature <feature>    matches the flow?
/website-dev:review-pull-request      follows the rules?
```

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
plugins/ledgerai/      .claude-plugin/plugin.json · agents/ · skills/<name>/SKILL.md   (6 skills)
plugins/website-dev/   .claude-plugin/plugin.json · hooks/ · skills/<name>/SKILL.md    (6 skills)
templates/             project-settings.json · web-project-settings.json
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
| `ledgerai` | 0.3.0 | Workflow-only skills that point to the docs: `analyze-requirements`, `document-feature` (was `/ledgerai:plan-feature`), `identify-edge-cases`, `review-feature`, `manage-dependencies` (uses the `TEAM-RULES.md` §7 template), `sync-project-specs` |
| `website-dev` | 0.2.0 | Workflow-only skills: `implement-feature`, `debug-frontend`, `review-pull-request`, three test placeholders. Standards moved to web-ui `.claude/rules/`. Removed `nextjs-16`, `hairline-ui`, `mock-api-layer` |
| `ledgerai` | 0.2.0 | Added `dictionary-checker` agent and `/ledgerai:plan-feature`. ESLint hook moved to `website-dev` |
| `website-dev` | 0.1.0 | New: `nextjs-16`, `hairline-ui`, `mock-api-layer` skills and the ESLint hook |
| `ledgerai` | 0.1.0 | First release: ESLint hook |
