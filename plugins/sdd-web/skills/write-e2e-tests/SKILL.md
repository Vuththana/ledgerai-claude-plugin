---
name: write-e2e-tests
description: End-to-end tests for LedgerVision user journeys (sign in, gate redirects, role access, feature flows). Placeholder — no e2e tool is installed yet. Use when asked to write or run end-to-end or browser tests.
---

# Write end-to-end tests (not set up yet)

**No end-to-end tool is installed.** Adding one needs an approved package request.

When asked for e2e tests:

1. Say that e2e testing isn't set up. **Don't install anything, and don't write test files** that assume a tool.
2. Offer to draft the package request with the `manage-dependencies` skill. A common choice for Next.js is Playwright (dev dependency). The team decides.
3. Meanwhile, walk through the journey by hand in `pnpm dev` as each seeded user, and write the steps down so they can become tests later.

## Journeys to cover once a tool is approved

Taken from the journeys (§4) and requirement IDs in `specs/<feature>/spec.md`. Name every test with the ID it proves first (`test("BRN-R03 …")`) so `/sdd:trace` finds it:

- The gate order: deactivated, soft-deleted business, unverified email, forced password change, no business
- Sign in (including the lockout), sign up with OTP, forgot password, accept invitation
- Manager access: owner-only URLs blocked, other branches' data never visible
- Owner branch switching: "All branches" versus a single branch
- Each feature's main flow once it's built (e.g. dashboard drag, save and reset)

When a tool is approved, replace this skill with the real setup: commands, seeded users, how the mock is reset between tests.
