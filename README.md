# ledgerai-claude-plugin

The shared Claude Code setup for the LedgerVision AI team. Every repo (web-ui, backend, docs, ...) installs plugins from here, so everyone gets the same hooks, skills, agents and commands no matter which repo they work in.

This repo is a **plugin marketplace** named `ledgerai` with two plugins:

| Plugin | Id | Enable it in | What it's for |
|---|---|---|---|
| `ledgerai` | `ledgerai@ledgerai` | **every** repo | Team-wide tooling built on the shared `docs` submodule (data dictionary + feature flows) |
| `website-dev` | `website-dev@ledgerai` | web front-end repos (web-ui) | Next.js 16, Hairline UI and mock-API know-how, plus the ESLint hook |

```
ledgerai-claude-plugin/
├── .claude-plugin/
│   └── marketplace.json                 # the marketplace: lists both plugins
├── plugins/
│   ├── ledgerai/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/dictionary-checker.md
│   │   └── commands/plan-feature.md
│   └── website-dev/
│       ├── .claude-plugin/plugin.json
│       ├── hooks/
│       │   ├── hooks.json
│       │   └── eslint-fix.sh
│       └── skills/
│           ├── nextjs-16/SKILL.md
│           ├── hairline-ui/SKILL.md
│           └── mock-api-layer/SKILL.md
└── templates/
    ├── project-settings.json            # .claude/settings.json for any repo (ledgerai only)
    └── web-project-settings.json        # .claude/settings.json for a web repo (both plugins)
```

## What's in each plugin

### `ledgerai` (every repo)

| Piece | How to use it | What it does |
|---|---|---|
| `/ledgerai:plan-feature <feature>` | Type it, e.g. `/ledgerai:plan-feature branch management` | Finds the feature in `docs/flow/README.md`. If the flow is 📝 draft, it lists the open questions and stops. If it's ✅ approved, it reads the flow and dictionary files and writes a plan (scope, roles, data, files, steps, edge cases, verification) before any code. |
| `dictionary-checker` agent | Claude uses it on its own after data-shaped changes, or ask: "run the dictionary checker on src/lib/types" | Compares types, forms, validation and mock data with `docs/data-dictionary/`: names, required flags, datatypes, lengths, defaults, enums, money fields. Reports mismatches and **never edits the dictionary**. |

Both expect the `docs` submodule mounted at `docs/`.

### `website-dev` (web repos)

| Piece | How to use it | What it does |
|---|---|---|
| `nextjs-16` skill | Automatic when Claude works on routes, layouts, proxy, caching | Points Claude at `node_modules/next/dist/docs/` first. Covers `proxy.ts`, `PageProps<"/route">`, Cache Components (`<Suspense>` / `"use cache"`), route groups and the `(app)` auth gate order. |
| `hairline-ui` skill | Automatic when Claude builds or styles components | Covers base-ui's `render` prop (not `asChild`), `pnpm dlx shadcn add`, `cn` from `@/lib/utils`, Tailwind v4 tokens in `globals.css`, dark mode, and where components go. |
| `mock-api-layer` skill | Automatic when Claude adds types, mock data or API functions | Covers the types → `lib/mock` → `lib/api` layering, dictionary-to-TypeScript mapping, role/branch filtering, and money fields. |
| ESLint hook | Automatic | After Claude writes or edits a `.ts/.tsx/.js/.jsx/.mjs/.cjs` file, runs `node_modules/.bin/eslint --fix` on it. Does nothing in a repo without ESLint. Needs `jq`. |

You can also call a skill directly: `/website-dev:hairline-ui`.

## What can't go in a plugin

A plugin can't ship **permissions**, **env vars** or **`CLAUDE.md`**. These stay in each repo and are committed there:

| File (in each repo) | Holds |
|---|---|
| `.claude/settings.json` | Permissions (allow / ask / deny), `env`, and the lines that enable the plugins |
| `CLAUDE.md` | Instructions for Claude about that repo (short rules; the plugin skills hold the how-to) |
| `.claude/settings.local.json`, `CLAUDE.local.md` | Your personal overrides. Gitignored, never shared |

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

Inside Claude Code:

```
/plugin marketplace add Vuththana/ledgerai-claude-plugin
/plugin install ledgerai@ledgerai
/plugin install website-dev@ledgerai      # web repos only
```

Or from your terminal:

```bash
claude plugin marketplace add Vuththana/ledgerai-claude-plugin
claude plugin install ledgerai@ledgerai
claude plugin install website-dev@ledgerai
```

> **Private repo.** Claude Code clones it with your own git credentials. You need read access on GitHub (ask to be added as a collaborator) and a working login (`gh auth login`, or an SSH key / credential helper). Check with `git ls-remote https://github.com/Vuththana/ledgerai-claude-plugin`.

### Getting updates

```
/plugin marketplace update ledgerai
```

Then restart Claude Code. Each plugin has a `version` in its `plugin.json`, and **you only get a plugin's changes when its version goes up**.

### Turning a plugin off

```
/plugin disable website-dev@ledgerai     # keep it installed, stop it running
/plugin uninstall website-dev@ledgerai   # remove it
```

To turn one off only for yourself in one repo, add this to that repo's `.claude/settings.local.json`:

```json
{ "enabledPlugins": { "website-dev@ledgerai": false } }
```

---

## Adding the plugins to a new repo

1. Copy a template to `<repo>/.claude/settings.json`:
   - a web front-end repo → `templates/web-project-settings.json` (both plugins, pnpm permissions)
   - any other repo (backend, ...) → `templates/project-settings.json` (`ledgerai` only)
2. Adjust the permissions for that repo's tools.
3. Make sure the repo has the `docs` submodule at `docs/`.
4. Commit `.claude/settings.json` (and `CLAUDE.md`).

---

## Changing the plugins (maintainers)

### Which plugin does it go in?

- Useful in **every** repo, or tied to the data dictionary or flow docs → `ledgerai`.
- Only makes sense in a **web front-end** repo (Next.js, UI, Tailwind, ESLint) → `website-dev`.
- A different kind of repo with its own tooling (e.g. backend) → add a new plugin, e.g. `plugins/backend-dev/`, and list it in `marketplace.json`. Don't split one repo's tooling into many small plugins.

### Add something

| To add | Put it in | Notes |
|---|---|---|
| A skill | `plugins/<plugin>/skills/<name>/SKILL.md` | Frontmatter `name` + `description`. The description decides when Claude loads it, so say *when* to use it |
| A slash command | `plugins/<plugin>/commands/<name>.md` | Becomes `/<plugin>:<name>`. `$ARGUMENTS` holds what the user typed after it |
| A subagent | `plugins/<plugin>/agents/<name>.md` | Frontmatter `name`, `description`, optional `tools` |
| A hook | `plugins/<plugin>/hooks/hooks.json` | Same format as `hooks` in settings.json. Reference scripts as `${CLAUDE_PLUGIN_ROOT}/hooks/...`; the project root is `$CLAUDE_PROJECT_DIR` |
| An MCP server | `plugins/<plugin>/.mcp.json` | Same format as a project `.mcp.json` |

Hooks run in every repo that enables the plugin. Make them check that they apply first, like `eslint-fix.sh` checks for `node_modules/.bin/eslint`, and exit 0 when they don't.

Keep skills about *how to do things*. Don't copy a repo's `CLAUDE.md` into a skill. If a rule changes in one place, the other goes stale.

### Test locally before pushing

From a repo next to this one (e.g. `web-ui`):

```bash
claude plugin validate ../ledgerai-claude-plugin                      # marketplace.json
claude plugin validate ../ledgerai-claude-plugin/plugins/ledgerai
claude plugin validate ../ledgerai-claude-plugin/plugins/website-dev

# one session with your local copies loaded
claude --plugin-dir ../ledgerai-claude-plugin/plugins/ledgerai \
       --plugin-dir ../ledgerai-claude-plugin/plugins/website-dev
```

The validator warns about a missing icon. Ignore it: icons only matter for the public plugin directory.

### Release

1. Bump `version` in the changed plugin's `.claude-plugin/plugin.json` (`0.1.0` → `0.2.0`). **Without a bump, teammates won't receive the change.**
2. Commit and push to `main`.
3. Tell the team to run `/plugin marketplace update ledgerai`.

## Changelog

| Plugin | Version | Change |
|---|---|---|
| `ledgerai` | 0.2.0 | Added `dictionary-checker` agent and `/ledgerai:plan-feature`. ESLint hook moved to `website-dev` |
| `website-dev` | 0.1.0 | New: `nextjs-16`, `hairline-ui`, `mock-api-layer` skills and the ESLint hook |
| `ledgerai` | 0.1.0 | First release: ESLint hook |
