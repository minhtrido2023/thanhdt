# Execution Plan Rules

Use an execution plan when work is large enough that repository state alone should let another engineer or agent resume safely.

This repo uses a lightweight planning style on purpose. Plans are for clarity and restartability, not process theater.

## When a plan is required

Write or update a plan when the work involves:

- more than one package layer
- a new provider or source integration
- public API or compatibility changes
- security- or network-sensitive behavior
- CI, packaging, or release workflow changes
- work expected to continue across multiple sessions

## When a plan is optional

You usually do not need a formal plan for:

- typo and doc fixes
- isolated bug fixes in one file or one provider
- small test additions
- narrow refactors with obvious local scope

## Required sections

Every plan in `docs/exec-plans/` should contain these sections:

1. `# Title`
2. `## Purpose / Big Picture`
3. `## Scope`
4. `## Progress`
5. `## Open Questions`
6. `## Decision Log`
7. `## Context and Orientation`
8. `## Plan of Work`
9. `## Validation and Acceptance`
10. `## Risks and Rollback`
11. `## Approvals`
12. `## Outcomes and Retrospective`

## Writing guidance

- Write in plain language.
- Name repository paths and modules precisely.
- Prefer concrete prose over giant checklists.
- Keep `Progress`, `Decision Log`, and `Outcomes and Retrospective` current as work proceeds.
- Record human approvals or unresolved decisions explicitly.

## Progress rules

The `Progress` section must reflect the real state of work.

Use entries like:

- [x] 2026-04-24 08:30Z - Inspected provider registration and identified affected adapters.
- [ ] Implement provider changes in `vnstock/api/quote.py` and `vnstock/explorer/vci/quote.py`.
- [ ] Run focused tests and document results.

If work stops mid-step, split the item so completed and remaining parts are obvious.

## Naming convention

- Active plans: `docs/exec-plans/active/YYYY-MM-DD-short-task-name.md`
- Completed plans: `docs/exec-plans/completed/YYYY-MM-DD-short-task-name.md`

## Minimal template

Use `docs/templates/EXEC_PLAN_TEMPLATE.md` as the starting point.
