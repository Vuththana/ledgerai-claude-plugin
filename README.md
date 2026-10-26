# ledgerai-claude-plugin

The shared Claude Code setup for the LedgerVision AI team. Every repo (web-ui, backend, docs, ...) installs the same plugin from here, so everyone gets the same hooks, skills, agents and commands no matter which repo they work in.

This repo is a **plugin marketplace** named `ledgerai` that holds one plugin, also named `ledgerai`. Its full id is `ledgerai@ledgerai`.

```
ledgerai-claude-plugin/
├── .claude-plugin/
│   └── marketplace.json          # the marketplace: lists the plugins in this repo
├── plugins/
│   └── ledgerai/
│       ├── .claude-plugin/
│       │   └── plugin.json       # plugin name + version
│       └── hooks/
│           ├── hooks.json        # hook definitions
│           └── eslint-fix.sh     # runs ESLint --fix after Claude edits a JS/TS file
└── templates/
    └── project-settings.json     # starter .claude/settings.json for a repo
```

## What the plugin does today

| Piece | What it does |
|---|---|
| ESLint hook (`PostToolUse`, `Write\|Edit`) | After Claude writes or edits a `.ts/.tsx/.js/.jsx/.mjs/.cjs` file, it runs `node_modules/.bin/eslint --fix` on that file. In a repo without ESLint installed it does nothing, so it's safe to enable everywhere. Needs `jq` on your machine. |

## What can't go in the plugin

A plugin can't ship **permissions**, **env vars** or **`CLAUDE.md`**. These stay in each repo and are committed there:

| File (in each repo) | Holds |
|---|---|
| `.claude/settings.json` | Permissions (allow / ask / deny), `env`, and the lines that enable this plugin |
| `CLAUDE.md` | Instructions for Claude about that repo |
| `.claude/settings.local.json`, `CLAUDE.local.md` | Your personal overrides. Gitignored, never shared |

---

## Installing (team members)

### Automatic (recommended)

Every LedgerVision repo has this in its committed `.claude/settings.json`:

```json
"extraKnownMarketplaces": {
  "ledgerai": {
    "source": { "source": "github", "repo": "Vuththana/ledgerai-claude-plugin" }
  }
},
"enabledPlugins": { "ledgerai@ledgerai": true }
```

1. Pull the repo and run `claude` in it.
2. Trust the folder when asked.
3. Claude Code asks you to install the `ledgerai` marketplace and plugin. Accept.

That's it. Run `/plugin` and you should see `ledgerai` under **Installed**.

### Manual

If you skipped the prompt or want it everywhere, run this inside Claude Code:

```
/plugin marketplace add Vuththana/ledgerai-claude-plugin
/plugin install ledgerai@ledgerai
```

Or from your terminal:

```bash
claude plugin marketplace add Vuththana/ledgerai-claude-plugin
claude plugin install ledgerai@ledgerai
```

> **Private repo?** Claude Code clones it with your own git credentials, so you need read access on GitHub and a working login (`gh auth login`, or an SSH key / credential helper). Check with `git ls-remote https://github.com/Vuththana/ledgerai-claude-plugin`.

### Getting updates

When the plugin changes:

```
/plugin marketplace update ledgerai
```

Then restart Claude Code. The plugin has a `version` in `plugin.json`, so **you only get changes when that number goes up**. Maintainers: see below.

### Turning it off

```
/plugin disable ledgerai@ledgerai     # keep it installed, stop it running
/plugin uninstall ledgerai@ledgerai   # remove it
```

To turn it off only for yourself in one repo, add this to that repo's `.claude/settings.local.json`:

```json
{ "enabledPlugins": { "ledgerai@ledgerai": false } }
```

---

## Adding the plugin to a new repo

1. Copy `templates/project-settings.json` to `<repo>/.claude/settings.json`.
2. Add that repo's own permissions. For example, web-ui allows `pnpm lint` / `pnpm build`, asks before `pnpm add`, and denies edits to `pnpm-lock.yaml`.
3. Commit `.claude/settings.json` (and `CLAUDE.md`).

---

## Changing the plugin (maintainers)

### Add something

| To add | Put it in | Notes |
|---|---|---|
| A skill | `plugins/ledgerai/skills/<name>/SKILL.md` | Frontmatter `name` + `description`. Claude uses it when the description matches the task |
| A slash command | `plugins/ledgerai/commands/<name>.md` | Becomes `/ledgerai:<name>` |
| A subagent | `plugins/ledgerai/agents/<name>.md` | Frontmatter `name`, `description`, optional `tools` |
| A hook | `plugins/ledgerai/hooks/hooks.json` | Same format as `hooks` in settings.json. Reference scripts as `${CLAUDE_PLUGIN_ROOT}/hooks/...`; the project root is `$CLAUDE_PROJECT_DIR` |
| An MCP server | `plugins/ledgerai/.mcp.json` | Same format as a project `.mcp.json` |

Hooks run in **every** repo that enables the plugin. Make them check that they apply first, like `eslint-fix.sh` checks for `node_modules/.bin/eslint`, and exit 0 when they don't.

### Test locally before pushing

From a repo next to this one (e.g. `web-ui`):

```bash
claude plugin validate ../ledgerai-claude-plugin              # checks marketplace.json
claude plugin validate ../ledgerai-claude-plugin/plugins/ledgerai
claude --plugin-dir ../ledgerai-claude-plugin/plugins/ledgerai   # one session with your local copy loaded
```

You can also point the marketplace at your local folder for a while:

```
/plugin marketplace add ../ledgerai-claude-plugin
/plugin install ledgerai@ledgerai
```

Remove it with `/plugin marketplace remove ledgerai` when you're done, then add the GitHub one back.

The validator warns about a missing icon. Ignore it: icons only matter for the public plugin directory.

### Release

1. Bump `version` in `plugins/ledgerai/.claude-plugin/plugin.json` (`0.1.0` → `0.2.0`). **Without a bump, teammates won't receive the change.**
2. Commit and push to `main`.
3. Tell the team to run `/plugin marketplace update ledgerai`.

---

## First-time setup of this repo (done once)

```bash
cd ledgerai-claude-plugin
git init -b main
git add .
git commit -m "Add LedgerVision shared Claude Code plugin"
gh repo create Vuththana/ledgerai-claude-plugin --private --source . --push
```

Until it's pushed, repos that enable `ledgerai@ledgerai` show a "marketplace not found" message. Use the local `/plugin marketplace add ../ledgerai-claude-plugin` route until then.
