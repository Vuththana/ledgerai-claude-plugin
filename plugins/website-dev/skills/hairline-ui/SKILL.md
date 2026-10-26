---
name: hairline-ui
description: Hairline UI (shadcn base-nova on @base-ui/react) and Tailwind v4 rules for LedgerVision web repos. Use when building or styling any component, form, dialog, menu, table or layout, adding a shadcn component, or touching theme colors and dark mode.
---

# Hairline UI

The team's UI kit is shadcn's **`base-nova` style built on `@base-ui/react`**, not Radix. Most shadcn examples online are Radix-based and won't work as written.

## Components

- **Add a primitive:** `pnpm dlx shadcn add <component>`. It lands in `src/components/ui/`. Don't hand-copy shadcn code from the web.
- **Check what's there first:** `ls src/components/ui`. Reuse before you add.
- **Composition uses the `render` prop, not `asChild`:**

  ```tsx
  // ✗ Radix style
  <Button asChild><Link href="/bills">Bills</Link></Button>

  // ✓ base-ui style
  <Button render={<Link href="/bills" />}>Bills</Button>
  ```

- Props types come from the primitive, e.g. `ButtonPrimitive.Props` from `@base-ui/react/button` (see `src/components/ui/button.tsx`).
- base-ui state is exposed as data attributes (`data-open`, `data-disabled`, ...). Style those, not Radix's `data-[state=open]`.
- Don't edit files in `src/components/ui/` for one feature's needs. Wrap them in `src/components/shared/` or the feature folder.

## Where things go

| Kind | Folder |
|---|---|
| shadcn primitives | `src/components/ui/` |
| Reusable app pieces (data table, KPI card, money display) | `src/components/shared/` |
| App shell (sidebar, topbar, branch switcher) | `src/components/layout/` |
| One feature's components | `src/features/<feature>/` |

## Styling

- **`cn` comes from the `cn` npm package** and is re-exported from `@/lib/utils`. There is no clsx or tailwind-merge. Import `cn` from `@/lib/utils`.
- **Tailwind v4, no config file.** All tokens live in `src/app/globals.css`: `@theme inline` maps the `:root` and `.dark` oklch variables.
- Use the semantic tokens (`bg-primary`, `text-muted-foreground`, `border-border`, `bg-card`, `text-destructive`, chart `--chart-1..5`). Don't hard-code colors.
- **Theme:** the primary is deep blue / indigo. Change it in `globals.css` (both `:root` and `.dark`), never per component.
- **Dark mode is class-based** (`.dark` on an ancestor, `@custom-variant dark`). Check both themes.
- Variants use `class-variance-authority` (`cva`), as `button.tsx` does.
- Icons: `lucide-react`.

## Text

The UI is English only for now, but Khmer is coming (`users.language`). Keep user-facing strings as plain literals in one place per component, not built by string concatenation, so they're easy to extract later.

## Packages

Don't install new packages (`pnpm add`). New dependencies go through the team's package request report. Ask first.
