# AGENTS.md

This file is the entrypoint for coding agents working in `vnstock`.

It is intentionally short. Use it as a map to the repository's real source of truth, not as a duplicate handbook.

## Operating model

- Humans own product intent, release judgment, and risk decisions.
- Codex can inspect, implement, test, and update docs inside the boundaries below.
- Prefer lightweight execution for local fixes. Use a written plan only when the task is cross-cutting, risky, or likely to span sessions.
- Keep durable knowledge in repository docs, not only in chat.

## Read order

For any non-trivial task, read these in order:

1. `README.md`
2. `ARCHITECTURE.md`
3. `PRODUCT_SENSE.md`
4. `QUALITY_GATES.md`
5. `SECURITY.md`
6. `docs/INDEX.md`
7. Relevant docs under `tests/docs/`, `.github/`, or `docs/`

If there is an active task brief or execution plan, read that before editing code.

## When a plan is required

Create or update a plan in `docs/exec-plans/` when work involves any of the following:

- changes across multiple package layers such as `api/`, `core/`, and one or more providers
- new data-source integrations or provider registration changes
- compatibility changes to public APIs exported from `vnstock/__init__.py`
- security-sensitive or network-behavior changes
- test or CI policy changes
- work expected to span more than one focused coding session

Small doc fixes, local bug fixes, or isolated test additions can proceed without a separate plan once the task is clear.

## Human approval gates

Pause for approval before making changes to:

- auth, tokens, secret handling, or API-key behavior
- proxy defaults, anti-bot behavior, or scraping posture that could change operational risk
- public API contracts, default parameters, or backward-compatibility shims
- packaging, release, or GitHub Actions policy
- destructive cleanup or removal of major code paths
- behavior that conflicts with `PRODUCT_SENSE.md`, `ARCHITECTURE.md`, or the README disclaimers

## Repo knowledge rules

- Prefer updating an existing source-of-truth doc over creating a duplicate explanation.
- Treat `tests/docs/` and `.github/TESTING.md` as real operational references, not disposable notes.
- Keep architecture docs aligned with observed code, especially around provider registration and lazy imports.
- If implementation depends on a newly discovered rule, write that rule down before finishing.

## Code and validation rules

- Respect package boundaries described in `ARCHITECTURE.md`.
- Keep network and scraping logic in provider modules, not in thin adapter layers.
- Preserve backward compatibility unless the task explicitly allows breaking changes.
- Run the smallest high-signal checks first, then broader checks when warranted.
- Do not claim completion without listing the checks you actually ran.

## Project commands

- Install deps: `python -m pip install -e ".[test]"`
- Run fast unit tests: `pytest tests/unit/ -m "not integration" -q`
- Run integration tests: `pytest tests/integration/ -v --maxfail=5`
- Run coverage: `pytest tests/ --cov=vnstock --cov-report=term-missing`
- Run lint: `flake8 vnstock`
- Run format checks: `black --check vnstock && isort --check-only vnstock`
- Run type checks: `mypy vnstock --ignore-missing-imports --no-error-summary`

Use judgment: docs-only changes do not need the full Python validation stack.

## Directory map

- `vnstock/__init__.py`: public package exports and lazy bootstrap
- `vnstock/common/client.py`: top-level `Vnstock` orchestration API
- `vnstock/api/`: thin adapters such as `Quote`, `Listing`, `Company`, `Finance`, `Trading`
- `vnstock/core/`: registry, types, settings, utilities, shared internals
- `vnstock/explorer/`: exchange- or site-specific providers, mostly scraping/browser-like access
- `vnstock/connector/`: API-style providers and integrations
- `tests/`: automated tests
- `tests/docs/`: test architecture and testing guidance
- `.github/workflows/`: CI, quality, performance, and release checks
- `docs/tasks/`: lightweight task briefs
- `docs/exec-plans/`: living plans for larger work
- `docs/templates/`: reusable templates for briefs, plans, and reviews

## If you are unsure

Do the smallest safe thing that increases clarity:

- read the nearest relevant doc
- inspect the real provider or adapter path
- write or update a plan
- ask for approval when the risk is genuinely human-owned

## Required Skill Usage: srcwalk

For any task that can be handled by the `srcwalk` skill, the agent MUST use it.

Use `srcwalk` for code reading, search, symbol lookup, reference tracing, dependency tracing, call-flow analysis, and debugging investigation.

Do not rely on manual reading, grep/ripgrep, or guesswork when `srcwalk` can perform the task.
Use srcwalk for: outlines of large files, symbol definitions, callers (single-hop or transitive BFS), file dependencies, codebase maps, jumping to a symbol body, call-chain tracing, comparing sizes of partial/overloaded definitions with the same name.

Don't use srcwalk for plain text search, reading small files whose path you know, listing paths to pipe, or complex regex. Use rg, cat, fd directly — they're faster and you already know how to read their output.

Before giving conclusions or editing code, use `srcwalk` to inspect the relevant files, symbols, and references.

