# Agent Docs Index

This index maps the lightweight agent workflow added to `vnstock`.

The goal is to help contributors and coding agents work consistently without duplicating the library's user documentation.

## Start here

- `../AGENTS.md`: agent entrypoint and repo map
- `../ARCHITECTURE.md`: package boundaries and invariants
- `../PRODUCT_SENSE.md`: developer-experience and compatibility principles
- `../QUALITY_GATES.md`: validation bar
- `../SECURITY.md`: risk and approval gates
- `../PLANS.md`: when and how to write execution plans

## Working docs

- `templates/TASK_BRIEF_TEMPLATE.md`: small task brief template
- `templates/EXEC_PLAN_TEMPLATE.md`: plan template for larger work
- `templates/PR_REVIEW_TEMPLATE.md`: review template focused on behavior, risk, and validation
- `tasks/README.md`: where to keep lightweight task briefs
- `exec-plans/README.md`: how plans are organized in this repo

## Existing repo docs worth reading

- `../tests/docs/INDEX.md`: testing docs map
- `../tests/docs/ARCHITECTURE.md`: test-suite structure and patterns
- `../tests/docs/AI_GUIDE.md`: practical test editing guide
- `../tests/docs/COVERAGE_STRATEGY.md`: current coverage posture
- `../.github/TESTING.md`: CI and workflow-level testing guide
- `../docs/PROXY_GUIDE.md`: proxy usage and related operational notes

## What this intentionally does not add

- No mandatory ADR process for every change
- No heavyweight review loop docs
- No duplicate architecture manual for user-facing notebooks

If a process document stops helping execution, simplify it.
