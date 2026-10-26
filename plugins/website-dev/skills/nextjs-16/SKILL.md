---
name: nextjs-16
description: Next.js 16 rules for LedgerVision web repos. Use before writing or changing any route, layout, page, proxy, data fetching, caching, Suspense boundary, route handler or next.config — anything that touches a Next.js API.
---

# Next.js 16

This is not the Next.js in your training data. APIs and file conventions changed. **Read the matching guide in `node_modules/next/dist/docs/` before using a Next API**, and follow any deprecation notice it gives.

## Where to look

| Topic | Doc (under `node_modules/next/dist/docs/01-app/`) |
|---|---|
| Layouts, pages, typed props | `01-getting-started/03-layouts-and-pages.md`, `03-api-reference/03-file-conventions/page.md` |
| Proxy (was middleware) | `01-getting-started/16-proxy.md` |
| Fetching / caching / revalidating | `01-getting-started/06-fetching-data.md`, `08-caching.md`, `09-revalidating.md` |
| `"use cache"` | `03-api-reference/01-directives/use-cache.md` |
| Server vs client components | `01-getting-started/05-server-and-client-components.md` |
| Everything else | `grep -rl "<keyword>" node_modules/next/dist/docs/01-app` |

Use the App Router docs (`01-app`), never `02-pages`.

## Rules that differ from older Next.js

- **`proxy.ts`, not `middleware.ts`.** Keep it thin: in LedgerVision it only checks for the session cookie and redirects to `/sign-in` when it is missing. The full auth gate lives in the `(app)` layout.
- **Typed props are global helpers.** Write `export default async function Page(props: PageProps<"/branches/[id]">)` and `LayoutProps<"/route">`. Don't hand-write `{ params: { id: string } }`. `params` and `searchParams` are promises, so `await` them.
- **Cache Components are on** (`cacheComponents` in `next.config.ts`):
  - Anything dynamic (cookies, headers, `searchParams`, uncached data) must render inside a `<Suspense>` boundary with a fallback, or the build fails.
  - Data that can be cached is marked with `"use cache"` (function or component level).
  - Reading the branch-switcher cookie makes that subtree dynamic, so wrap it in `<Suspense>`.
- **`partialPrefetching`** is enabled. Keep the static shell meaningful so prefetches are useful.

## LedgerVision route layout

```
src/app/
  (auth)/        sign-in, sign-up, forgot-password, accept-invitation
  (onboarding)/  business-setup
  (app)/         authenticated shell: sidebar, topbar, branch switcher
```

The `(app)` layout runs the gate in this order: `is_active` → business soft-deleted (`/restore-business`) → `is_email_verified` (owner → `/verify-email`) → `requires_password_change` (`/change-password`) → `business_id` (`/business-setup`). Owner-only routes also check the role in the layout, not just in the sidebar.

## Before you finish

Run `pnpm build`. It does the full type-check, including the `PageProps` / `LayoutProps` route types and Cache Components errors. `pnpm lint` alone does not catch these.
