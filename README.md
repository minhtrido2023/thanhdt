# thanhdt — Vietnamese quant trading workspace (backup)

Private backup of the `WorkingClaude` quant-trading workspace so development and
context can be resumed on any machine. **Status: proof-of-concept, not live.**

## Layout

```
WorkingClaude/
├── *.py, *.md, *.sh, *.sql      code, docs, cron scripts  (tracked)
├── CLAUDE.md                    project guide for Claude Code (tracked)
├── .claude/                     skills + context           (tracked)
├── data/                        all market data — csv/pkl/xlsx/logs (gitignored;
│                                regenerable from BigQuery). *.md reports & *.py
│                                helpers inside data/ ARE tracked.
└── secrets/                     credentials (gitignored; see secrets/README.md)
```

## What is NOT in git (must be restored to resume runtime)

- **`WorkingClaude/data/`** bulk data (csv/pkl/xlsx/json/logs) — regenerate from
  BigQuery (`lithe-record-440915-m9.tav2_bq`, see `CLAUDE.md`).
- **`WorkingClaude/secrets/`** — recreate credential files (see
  `WorkingClaude/secrets/README.md`).
- **`wc_venv/`**, **`gcloud_dtienthanh/`** (top-level) — Python venv and gcloud
  ADC config; recreate locally.

## Resume checklist on a fresh machine

1. `git clone` this repo.
2. Recreate `wc_venv` and install deps; restore `gcloud_dtienthanh` ADC.
3. Refill `WorkingClaude/secrets/` from the table in `secrets/README.md`.
4. Regenerate `WorkingClaude/data/` caches from BigQuery as scripts need them.
5. `source WorkingClaude/wc_env.sh` for cron/env wiring.

Paths in code resolve via `WORKDIR = /home/trido/thanhdt/WorkingClaude`; data is
read from `WORKDIR/data/`, secrets from `WORKDIR/secrets/`.
