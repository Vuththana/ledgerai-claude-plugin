---
name: figma-design
description: Find and read a LedgerVision screen in the team's Figma design (Copy of FinSight) and adapt it to web-ui. Use when building or changing a page, screen or component's look, or when asked what a screen should look like.
---

# Use the Figma design

The Figma file shows **how a screen looks**: layout, spacing, components, colours and type. **What** the screen holds still comes from the docs: its fields, labels, messages, states and roles come from the spec (`specs/<feature>/spec.md`: requirements, `M` messages, `E` edge cases) and the data dictionary. If the two disagree, the spec wins.

**File:** Copy of FinSight, file key `8BCo6msgQ39f1sjDgNtT5n`
https://www.figma.com/design/8BCo6msgQ39f1sjDgNtT5n/Copy-of-FinSight?node-id=963-315137

This needs the official Figma plugin, signed in with an account that can open the file.

## 1. Find the screen

Frames are named `<section>.<n> <Screen> — <state>`, e.g. `05.1 Dashboard — Business Owner (all branches)` or `08.8 Item Adjustments — Not enough stock`. The top row of the Workspace page is the Business Owner. The row below it is the Branch Manager.

Call `get_metadata` on a **section** node from the table below, not on the Workspace page itself. The whole page is millions of characters long.

| Section | Business Owner | Branch Manager |
|---|---|---|
| Landing page | `1038:396353` | `1054:334599` |
| 04 Authentication | `1038:426124` | `1038:424075` |
| 05 Dashboard | `1038:425437` | `1038:423532` |
| 06 Banking & Accounts | `1054:405688` | — |
| 08 Inventory & Items | `1038:373432` | — |
| 09 Sales & Customers | `1038:381690` | — |
| 10 Financial Records | `1038:397200` | `1054:378215` |
| 11 AI Financial Advisor | `1038:388810` | `1038:390127` |
| 12 Monthly Reports | `1038:418429` | `1038:421296` |
| 14 Notifications | `1038:394020` | `1038:395692` |
| 17 Profile & Settings (incl. 17.13 Integrations) | `1054:301665` | `1054:323131` |

The **Components** page (`3:2`) holds the style showcase (`1071:284750`), the sidebar (`672:256748`) and the component library (`1072:463714`): icons, data display, actions, feedback and overlays, forms, navigation, AI components and mobile.

The file has no screens for Branch Management or Forecasting. Build those from the spec, using the shell and components the other screens use.

## 2. Read it

1. `create_session` with the file key, once per task.
2. `get_screenshot` for the screen and for **each state frame** of it (loading, empty, errors, dialogs). The states are separate frames with the same number.
3. Load `figma:figma-design-to-code` before calling `get_design_context` on a frame.
4. Call `get_variable_defs` on a frame for its colour, spacing, radius and text tokens. They're named `--lf-*`.

## 3. Adapt it, don't paste it

`get_design_context` returns generic React with raw hex and px values. Treat it as a reference:

- Build from `src/components/ui` and `src/components/shared` (`ui-components.md`). Figma components such as buttons, inputs, tables, badges and dialogs map to the primitives already there. Use the `render` prop, not `asChild`.
- Use theme tokens from `src/app/globals.css`, never hex values or arbitrary px. Map each `--lf-*` token to its theme token. If a token isn't in `globals.css` yet, add it to the plan; don't inline it.
- Money goes through the shared money display (`data-dictionary.md` § Money), even when Figma shows plain text.
- The file only has light mode. Check the screen in dark mode too, using the `.dark` tokens.
- Keep the layout fluid. Frames are 1728px wide; also check phone width.

## 4. Check it against the docs

Go through each screen before building it:

- **Fields and columns:** every field must exist in `data-dictionary/` under the same name. If Figma shows a field that isn't in the dictionary, leave it out and note it as a gap. Don't add it.
- **Wording:** labels, messages and empty states use the spec's `M` text. Figma copy is placeholder text.
- **Roles:** compare the Branch Manager frames with the spec's §2 and its role requirements. Where they differ, the spec wins.
- **Screens with no spec** (e.g. 09 Sales & Customers): don't build them. They need `/sdd:specify` first.

List every mismatch as a spec gap (by nearest ID) for the lead or the plan. Don't change the docs from web-ui.
