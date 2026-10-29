---
name: write-component-tests
description: Component tests for LedgerVision UI (forms, tables, role variants, states). Placeholder — no component testing tools are installed yet. Use when asked to write or run component tests.
---

# Write component tests (not set up yet)

**No component testing tools are installed**: no test runner, no Testing Library, no DOM environment. Adding them needs an approved package request.

When asked for component tests:

1. Say that component testing isn't set up. **Don't install anything, and don't write test files** that assume a framework.
2. Offer to draft the package request with the `sdd:manage-dependencies` skill. A common choice for this stack is Vitest with React Testing Library and a DOM environment (all dev dependencies). The team decides.
3. Meanwhile, check the component by hand in `pnpm dev`, in both themes and with the keyboard.

## What to cover once tools are approved

- Every state: loading, empty, no results, error, and each status value
- Role variants: owner versus manager (owner-only actions hidden, branch filter only for "All branches")
- Forms: required, length and enum errors; server errors shown on the right field; no double submit
- Accessibility: labels, `aria-*` on base-ui parts, keyboard paths (including dashboard drag with the keyboard)

When tools are approved, replace this skill with the real setup. Every test names the spec ID it proves first (`test("BRN-R03 …")`, `sdd:conventions` §3) so `/sdd:trace` can count it.
