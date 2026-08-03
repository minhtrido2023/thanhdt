# tbot

**tbot** is minhtrido's dedicated bot (Discord: `minhtrido`; runs as OS user `trido`). Distinct
from `mike/` (Mike fleet, trading-domain operations) — tbot owns a separate scope: general
cross-cutting KB, its own memory, its own code, its own published HTML.

## Write-scope rule (standing, set by minhtrido 2026-08-04)

**tbot keeps everything inside this folder.** Other bots (Mike fleet, etc.) may *read* anything
under `tbot/`, but do not write here. Symmetrically, tbot avoids writing outside `tbot/` unless
there's a real reason and minhtrido has confirmed it. If a task seems to need a file outside this
tree, stop and ask first.

## Layout

```
tbot/
├── kb/            versioned concept nodes (OKF: yaml frontmatter + markdown), fact-status lifecycle
│   ├── _schema/     frontmatter JSON Schema, checked by kb_lint.py
│   ├── _index/      GENERATED — never hand-edit (aliases.json, by_status.md, graph.md)
│   ├── concepts/    <slug>/{node.yaml, v1.md, v2.md, ..., CHANGELOG.md}
│   └── process/     ask_to_verify/, conflict_review/, contradiction_sweeps/ — governance records
├── memory/        tbot's own working memory (mirrors mike/kb/memory/<id>.md pattern)
├── code/
│   ├── lib/         okf.py — shared read/write core for concept nodes
│   ├── kb_tools/    CLI scripts: kb_new_concept, kb_new_version, kb_verify, kb_ask_to_verify,
│   │                kb_dispute, kb_resolve_conflict, kb_reindex, kb_lint, kb_contradiction_sweep
│   └── tests/       selfchecks — run for real before calling anything "done"
├── projects/      tbot's own standalone deliverables (e.g. dnse_dashboard)
└── html/          published HTML only (dashboards, reports) — gitignored wholesale, may hold
                   real financial data
```

## Fact-status lifecycle

`unverified → verified` (ask-to-verify confirmed) · `{unverified,verified} → disputed` (new
contradicting evidence) · `disputed → verified` (winner) or `→ rejected` (loser) · any status
`→ superseded` (a newer version now exists — old version keeps its status forever, for audit).
Rejected/superseded versions are never deleted.

## Concept node shape

```
kb/concepts/<slug>/
  node.yaml     concept-level pointer: current_version, status, aliases, related, tags, owner
  v1.md         immutable version snapshot: yaml frontmatter (status, supersedes, change_reason,
  v2.md         author, verified_by/at, sources) + prose body
  CHANGELOG.md  one line per version bump, human-readable
```

`node.yaml`'s `status` mirrors the current version's status (fast filtering without opening every
file). `supersedes` in each version's frontmatter is the explicit change-edge — not inferred from
the filename, so a dispute (two competing candidate versions) is representable before it resolves.
`aliases`/`related` feed `kb_reindex.py`'s generated `_index/aliases.json` / `_index/graph.md`.

## Governance tools (`code/kb_tools/`)

- `kb_new_concept.py <slug> --title ... --body-file ...` — create v1, status `unverified`.
- `kb_new_version.py <slug> --body-file ... --reason ...` — add v(N+1), supersede current.
- `kb_ask_to_verify.py <slug> --note ...` — open a verification request.
- `kb_verify.py <slug> --by ... [--note ...]` — flip current version + node to `verified`, close
  matching ask-to-verify request.
- `kb_dispute.py <slug_a> <slug_b> --reason ...` — open a conflict-review record, set both
  `disputed`.
- `kb_resolve_conflict.py <review_id> --keep <slug> --reject <slug>` — close the review.
- `kb_reindex.py` — rebuild `_index/*` from every concept's `node.yaml`.
- `kb_lint.py` — validate frontmatter against schema, version-chain integrity, alias collisions.
- `kb_contradiction_sweep.py` — flag concepts sharing a `fact_key` tag with disagreeing
  `fact_value` among non-disputed/non-rejected/non-superseded versions; writes a dated report,
  never auto-resolves.

All scripts: stdlib + `pyyaml` only, `__file__`-relative paths (portable), `--help`, no side
effects beyond `tbot/kb/`.

## Relationship to `mike/kb/`

`mike/kb/` stays exactly as-is — it's Mike fleet's live operational trading-domain registry, wired
into its own dispatch/cron/CLAUDE.md imports. tbot's `kb/` is for tbot's own knowledge (may
overlap in subject matter, e.g. DNSE API mechanics, but is a separate, independently-versioned
copy — no shared mutable state between the two trees).
