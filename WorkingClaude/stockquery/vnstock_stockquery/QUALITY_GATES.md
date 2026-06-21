# Quality Gates

This file defines the practical bar for changes in `vnstock`.

The goal is consistency and risk control, not paperwork.

## Default gate

Every non-trivial change should satisfy the relevant items below:

1. The changed path is validated by tests, or the absence of tests is explained.
2. Existing public behavior is preserved unless the task explicitly changes it.
3. Relevant docs are updated if the task changes architecture, testing guidance, or user-facing behavior.
4. Validation commands are proportional to the change.
5. Remaining risks are called out plainly.

## Required commands

Use the smallest set that gives real signal:

- Fast unit tests: `pytest tests/unit/ -m "not integration" -q`
- Focused file/test run: `pytest path/to/test_file.py -v`
- Integration tests: `pytest tests/integration/ -v --maxfail=5`
- Coverage run: `pytest tests/ --cov=vnstock --cov-report=term-missing`
- Lint: `flake8 vnstock`
- Format checks: `black --check vnstock` and `isort --check-only vnstock`
- Type checks: `mypy vnstock --ignore-missing-imports --no-error-summary`

For docs-only changes, a lightweight sanity check is enough.

## Testing expectations

- Add or update tests when behavior changes are practical to automate.
- For provider-specific fixes, prefer a focused regression test over broad unrelated edits.
- For risky compatibility fixes, add a test that would fail before the fix when feasible.
- Do not invent blanket coverage targets that the repo does not currently enforce.
- Treat `tests/docs/` and `.github/TESTING.md` as part of the testing source of truth.

## Review expectations

Before merge, a reviewer should be able to answer:

- Is the behavior change clear?
- Does it respect `ARCHITECTURE.md`?
- Does it preserve the public API or document the change?
- Are the important risks covered by tests or explicit notes?
- Were docs updated when a durable rule changed?

## Escalate instead of guessing

Do not self-approve changes that affect:

- security boundaries or secret handling
- public contracts and compatibility behavior
- release, packaging, or CI policy
- scraping posture, request identity, or proxy defaults

Those need human judgment even if the code is technically ready.
