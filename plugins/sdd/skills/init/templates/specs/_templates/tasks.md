# Tasks: <Feature title>

**Spec:** `XXX` v<X.Y.Z> · **Plan:** approved <date> · **Progress:** 0 / <n>

<!--
HOW TO WRITE THIS FILE
- One line per task, exactly:
  - [ ] **T07** `repo` — <what, small enough to review> · covers XXX-R03, XXX-E02 · after T03 · done when: <check>
  then, when done, the lead appends:  · files: `path`, `path`
- [ ] open, [x] done. A task made stale by /sdd:amend gets ⟳ after its ID: - [ ] **T07** ⟳ …
- "covers" lists every live requirement / edge-case ID the task delivers. A task with no ID must say
  `covers: setup` (scaffolding, config). Every live XXX-R and XXX-E needs at least one task.
- "after" lists tasks that must finish first. Omit it when the task can start at once.
- `[P]` after the repo marks tasks that can run in parallel with their neighbours.
- "done when" names a check a reviewer can run: a test (named with the ID), a command, a screen state.
- IDs T01… are never renumbered. Removed tasks are struck through.
- Only the lead session edits this file. Developers report "T07 done → files".
- Check it with `sddtool.py check <docs> <feature>`.
-->

## Phase 1 — Contract and backend

- [ ] **T01** `<service>` — Flyway migration for `<table>` per the dictionary · covers XXX-R03 · done when: migration applies on a fresh DB; dictionary-checker clean
- [ ] **T02** `<service>` — `POST /path` with role check and uniqueness · covers XXX-R01, XXX-R02, XXX-E01 · after T01 · done when: `XXX-R01`/`XXX-R02`/`XXX-E01` tests green

## Phase 2 — web-ui static UI (M1)

- [ ] **T03** `web-ui` [P] — placeholder data `src/features/<x>/placeholder-data.ts`, typed with `src/lib/types/` · covers: setup · done when: lint + build pass
- [ ] **T04** `web-ui` [P] — `/path` screen and every state from Figma `<frame>`, on the placeholder data · covers XXX-R02, XXX-E02 · after T03 · done when: each state renders and matches its frame

## Phase 3 — web-ui integration (M2)

- [ ] **T05** `web-ui` — `src/lib/api/<x>` against the §3 contract, Server Action, `/path` on real data, placeholder data deleted · covers XXX-R01, XXX-R02, XXX-E02 · after T02, T04 · done when: each state reachable against the running service; `XXX-R02` test green
- [ ] **T06** `docs` — API reference entries for the new endpoints · covers: setup · after T02 · done when: entries confirmed by the user

---

Coverage: every live XXX-R / XXX-E has a task — checked by `sddtool.py check`.
