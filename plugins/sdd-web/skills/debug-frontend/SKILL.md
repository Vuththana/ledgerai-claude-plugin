---
name: debug-frontend
description: Investigate and fix LedgerVision front-end bugs — Next.js 16 build/runtime errors, Suspense/Cache Components errors, hydration mismatches, base-ui vs Radix mistakes, styling/dark-mode issues, redirect loops, mock data problems and role leaks. Use when something errors, renders wrong, or behaves differently from the docs.
---

# Debug the front end

## Approach

1. **Reproduce.** Note the route, the role, the branch selection and the exact steps.
2. **Read the actual error:** the `pnpm dev` terminal, the browser console, and the Next.js error overlay. Run `pnpm build` for type and route errors that dev mode misses.
3. **Look up the API** in `node_modules/next/dist/docs/` or `node_modules/<package>/*.d.ts`, not in memory of older versions.
4. **Fix the cause.** Don't silence it with `@ts-ignore` or `eslint-disable`, and don't add a package to work around it.
5. **Not sure what's correct?** The spec (`specs/<feature>/spec.md`) defines the expected behaviour, by requirement ID.

## Common causes in this stack

| Symptom | Likely cause | Rule |
|---|---|---|
| Build error about dynamic or uncached data outside `<Suspense>` | Cache Components: wrap the dynamic part, or mark the data `"use cache"` | `nextjs.md` |
| `params.id` is undefined | `params` / `searchParams` are promises | `nextjs.md` |
| Middleware never runs | The file must be `proxy.ts` | `nextjs.md` |
| Redirect loop to `/sign-in` | The `proxy.ts` matcher includes auth routes or static files | `nextjs.md` |
| `asChild` does nothing, or a nested `<button>` | base-ui uses the `render` prop | `ui-components.md` |
| `data-[state=open]:` styles don't apply | base-ui uses `data-open` / `data-closed` | `ui-components.md` |
| Wrong colors in dark mode | A token missing from `.dark`, or a hard-coded color | `ui-components.md` |
| Hydration mismatch | Dates, relative times, `Math.random` or locale formatting rendered on the server | `ui-components.md` |
| Mock data resets or differs between requests | The mock store isn't a single module-level singleton | `data-layer.md` |
| Manager sees another branch's data | Scoping missing in `lib/api` | `data-layer.md` |
| A field shows `undefined` | A field name that isn't the dictionary's (camelCase vs snake_case). Run the `dictionary-checker` agent | `data-dictionary.md` |
| Drag-and-drop does nothing | Missing `"use client"`, `handleRef` not attached, or the old `@dnd-kit/core` API | `drag-and-drop.md` |

## After the fix

`pnpm lint` and `pnpm build` pass. Recheck as both roles if the bug touched data or navigation. If the bug came from the docs being unclear, note it as a spec gap (→ `/sdd:amend`).
