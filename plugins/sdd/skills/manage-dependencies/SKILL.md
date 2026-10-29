---
name: manage-dependencies
description: Check whether a new package is really needed and evaluate it. In web-ui, draft the LedgerVision package request, find out which team member is asking and which browser they use, and file it as a row in the team's Package Requests sheet before anything is installed; backend repos and ai-service need no request. Use whenever a task seems to need a library that isn't in the project, or someone asks to add, upgrade or remove a dependency.
---

# Manage dependencies

In web-ui, the `sdd-web` plugin's **package gate** hook blocks every `pnpm` / `npm` / `yarn` / `bun` add, install or update of a named package that has no **Approved** row in the sheet. When it blocks you, its message says what to do: either follow this skill from §1 for packages with no request, or tell the user that the existing request is still waiting. Never work around it, for example by editing `package.json` by hand or using another package manager.

The rule is `TEAM-RULES.md` §7 (and the repo's packages rule, e.g. `.claude/rules/packages.md`):

- **`web-ui`:** nothing is installed, upgraded or removed until its request has **Status = Approved** in the team sheet (§4). Never run an install command before that.
- **Backend repos and `ai-service`:** no package request. Still do §1 and §2, add the dependency with the repo's build tool, and list it in the PR description. Never change the stack versions settled in `TRD.md` §2.

## 1. Is it needed?

- Look in the dependency file (`package.json`, or the backend's equivalent) and the repo's rules for what's already there. In web-ui, `.claude/rules/ui-components.md` lists what `@base-ui/react` already provides.
- Check whether the platform does it (`Intl.NumberFormat`, `Intl.DateTimeFormat`, `crypto.getRandomValues`, `URLSearchParams`).
- Check whether a small helper in the repo would do.

If something existing covers it, say so and stop.

## 2. Evaluate the candidate

Read-only commands, e.g. for pnpm:

```bash
pnpm view <pkg> version license peerDependencies dependencies time.modified repository.url homepage
```

Check maintenance (latest release, activity), license, size and transitive dependencies, compatibility with the repo's stack versions, TypeScript types, and known advisories. Compare at least one alternative, including "build it ourselves".

## 3. Draft the request (web-ui)

Fill in the template from `TEAM-RULES.md` §7 with what you found, and show it to the user. Then turn it into the sheet's row:

| Col | Header | Value |
|---|---|---|
| A | No. | **don't type it.** A holds a formula (`=IF(D<n>="","",ROW()-5)`) that numbers the row once D is filled. Typing would overwrite the formula. Use the number it will show (row − 5) in the confirmation |
| B | Date Requested | today, `dd/mm/yyyy` |
| C | Requested By | the member's name **exactly** as in the dropdown (§4.2) |
| D | 1. Package Name | the exact npm name (`@dnd-kit/react`) |
| E | 2. Package Resource Link | official docs or GitHub repo (`homepage` / `repository.url`) |
| F | 3. Package Registry Link | `https://www.npmjs.com/package/<name>` |
| G | 4. Purpose | what the package does, one sentence |
| H | 5. Reason for Adding | why the project needs it, plus the alternative you ruled out and why |
| I | 6. Usage Location | the feature, page or component (with the spec ID if there is one) |
| J | 7. Proposed Version | the exact version (`0.5.1`), never `latest` |

**Never write K–M** (Status, Decision Date, Approver Comments): they're for the approver only.

**An agent** (`web-dev`) stops here: it puts the draft and the row under **Needs confirmation** for the lead, who does §4 with the user.

## 4. File it in the team sheet (web-ui)

Sheet: **Package Requests** tab of https://docs.google.com/spreadsheets/d/16uJc2NUiDNs2TibBV1LMlVpkDdA5u65NxYen4Lo43Ew/edit?gid=438764700#gid=438764700 (member list: tab **Team Member Roles**, gid `209364481`).

### 4.1 Read the sheet's current structure

Both tabs can be read as CSV without signing in:

```bash
curl -sL "https://docs.google.com/spreadsheets/d/16uJc2NUiDNs2TibBV1LMlVpkDdA5u65NxYen4Lo43Ew/export?format=csv&gid=438764700"
curl -sL "https://docs.google.com/spreadsheets/d/16uJc2NUiDNs2TibBV1LMlVpkDdA5u65NxYen4Lo43Ew/export?format=csv&gid=209364481"
```

Parse with a CSV parser: one record is one sheet row, so record *n* is row *n*. Row 4 must be the headers of §3's table, in that order (A–J, then K–M Status / Decision Date / Approver Comments). Row 5 holds hints; requests start at row 6. **If the headers differ, stop and show the user what changed.** Don't guess where things go.

- **Target row:** the first row from 6 on whose A–J are all empty.
- **Its K–M must be empty too.** If the target row already has a Status (e.g. a stray "Approved" left in the template), **stop**. Tell the user the request would land pre-approved and the package gate would wave it through. Ask them, or the approver, to clear that cell first. Don't clear it yourself: K–M are the approver's.
- **No.:** the row number − 5 (column A's formula).
- **Duplicate:** a row with the same package name that isn't Rejected already exists → show it and ask whether to file another.

### 4.2 Who is asking

The request is always filed under **the team member using Claude**, never under Claude, and never under whoever filed the last row.

1. Take `git config user.email` in the repo and look it up in the **Name / Email** table in Team Member Roles, ignoring case.
2. **Exactly one match:** that member is the requester. Don't ask; name them in the §4.4 question so a wrong match can still be corrected there.
3. **No match, or more than one** (no email in the sheet, a different git email): try `git config user.name` against the names. If that doesn't give exactly one match either, ask with AskUserQuestion, "Who is requesting this package?", with the closest members of the **Web** team as options. Use the answer for the rest of the session; don't ask again.
4. The name goes in column C spelled exactly as in Team Member Roles, because C is a dropdown.

### 4.3 Which browser

Asked together with the confirmation, in §4.4. The options:

| Option | Then |
|---|---|
| **Chrome, with the Claude in Chrome extension** | Load the `anthropic-skills:chrome-browser` skill and follow it. Work in a new tab, in their signed-in Chrome |
| **Claude desktop app's built-in browser** | Load the `anthropic-skills:built-in-browser` skill and follow it |
| **A Playwright window** | Use the `mcp__playwright__*` tools. It's a separate browser, so the user signs in to Google in that window first. Wait until they say they're done, then check the page no longer shows a Sign in button. If it's held by another session's browser ("Browser is already in use"), ask the user before closing that browser |
| **Another browser** (Firefox, Safari, Brave…) | Claude can't control it. Open the link (`xdg-open`, or `open` on macOS) and give the user the row as one tab-separated line to paste into cell `B<row>` (§4.5) |

If the chosen tool isn't available in this session, say so and offer the next option.

### 4.4 ⏸ Confirm, then fill

The sheet is shared with the whole team, so **show the user the exact row** (row number and A–J values, requester included) before typing anything. Then ask one AskUserQuestion: "File this as row *n*, requested by **<member>**? Which browser should I open? (You need to be signed in to Google with edit access.)" The options are the §4.3 browsers, plus **"Don't file it"**. Picking a browser is the yes. If they say the requester is wrong (through "Other"), fix C and ask again.

Then, in the browser:

1. Open the sheet URL with `#gid=438764700&range=A<row>`. Check that the **Package Requests** tab is active and that `A<row>` is still empty. If someone filled it meanwhile, re-read the sheet (§4.1) and pick the next empty row.
2. For each cell **B–J** (never A, it's a formula): select it through the **Name Box** (the cell reference box at the top left). Type the cell (`D9`), press Enter, type the value, press Enter.
3. **Column C** is a dropdown: type the exact name and choose it from the list that appears. Don't leave free text that the validation rejects (a red corner or a warning).
4. Don't touch K–M, other rows, formatting or other tabs. If anything unexpected comes up (no edit access, a sign-in wall, a dialog), stop and tell the user.

### 4.5 Check it saved

Read the tab again with the CSV export (§4.1). Compare row *n* with what you meant to write, cell by cell (the export can lag a few seconds; retry up to 3 times). A should show the number from its formula, and K–M should be empty. Report: the row number, ✅ for each matching cell, and anything that differs.

For another browser, give the user this line to paste into `B<row>`. It spreads across B–J and leaves A's formula alone:

```
<dd/mm/yyyy>⇥<name>⇥<package>⇥<resource link>⇥<npm link>⇥<purpose>⇥<reason>⇥<usage>⇥<version>
```

Write it with real tab characters. Run the same check once they've pasted it.

## 5. After filing

- Tell the user the request is in row *n*, and that nothing gets installed until an approver sets **Status = Approved**.
- Ask how to go on without the package in the meantime (a stub, a small helper, or pause the task).

## 6. After approval

Before installing, read the row's Status from the CSV export (§4.1). Only **Approved** counts. Then install with the repo's package manager (web-ui: pnpm only), pinned to the approved version (column J). Commit the dependency file and the lockfile together, and name the sheet row in the PR ("Package request #<No.>").
