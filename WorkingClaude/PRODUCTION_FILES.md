# BA-system v11 — Production Files Manifest

This document lists every file required for a complete deployment, with its purpose and dependencies.

**Total files**: ~15 critical + ~6 validation scripts + ~5 docs

## Tier 1 — MUST DEPLOY (production runtime)

| File | Size approx | Purpose | Modifies | Sensitive |
|---|---|---|---|---|
| `recommend_holistic.py` | ~25 KB | **Main live engine** — generates daily watchlist | Output CSVs | No |
| `telegram_recommend.py` | ~13 KB | Telegram bot wrapper around live engine | Output CSVs, Telegram | No |
| `simulate_holistic_nav.py` | ~30 KB | Day-by-day NAV simulation engine (used by backtests) | — | No |
| `signal_v10_sql.py` | ~5 KB | Clean SIGNAL_V10 SQL constant (no side effects on import) | — | No |
| `requirements.txt` | <1 KB | Python dependencies pin | — | No |
| `fundamental_rating_all.csv` | ~1 MB | FA tier cache, ~12k rows (refreshed quarterly) | — | No |

## Tier 2 — Configuration / wrappers (per server)

| File | Purpose | Sensitive |
|---|---|---|
| `telegram_config.json` | Bot token + chat_id | **YES** (gitignore) |
| `telegram_config.template.json` | Template for above | No |
| `telegram_run_daily.sh` (Linux) | Cron wrapper that activates venv + runs script | No |
| `telegram_run_daily.bat` (Windows) | Task Scheduler wrapper equivalent | No |
| `.gitignore` | Exclude secrets + logs | No |

## Tier 3 — Validation backtests (optional but recommended)

| File | Run frequency | Validates |
|---|---|---|
| `test_state_var_with_p3.py` | Once per deployment | Full V11 stack (7 variants × 3 periods) |
| `quarterly_walkforward.py` | Each quarter end | System health vs baseline |
| `export_journal_v6_extended.py` | On demand | Specific period trade journal |
| `test_etf_parking.py` | On change | V6 ETF parking |
| `test_fresh_q_filter.py` | On change | Fresh-Q filter |
| `test_v2g_vs_baseline.py` | On state-change | Verify state regime is correct |

## Tier 4 — Documentation

| File | Audience |
|---|---|
| `DEPLOYMENT.md` | Developer deploying (main doc) |
| `README.md` | Quick-start, 5-minute setup |
| `BA_SYSTEM_WORKFLOW.md` | Technical/quant deep-dive |
| `TELEGRAM_SETUP.md` | Telegram bot specifics |
| `PRODUCTION_FILES.md` | This file — what to deploy |

## Tier 5 — Auto-deploy scripts

| File | Use |
|---|---|
| `deploy_linux.sh` | Linux server bootstrap (venv + paths + cron + Telegram register) |
| `deploy_windows.ps1` | Windows server bootstrap (venv + Task Scheduler + paths) |
| `telegram_register_task.ps1` | Windows Task Scheduler entry creation (alternative to ps1) |
| `telegram_fix_wake.ps1` | Windows wake-from-sleep fix |

## Generated artifacts (do NOT commit; regenerated daily)

| Pattern | Created by | Purpose |
|---|---|---|
| `holistic_YYYY-MM-DD.csv` | recommend_holistic.py | Full universe scoring + classification |
| `ba_book_bal_YYYY-MM-DD.csv` | recommend_holistic.py | BAL book (10-12 picks) |
| `ba_book_vn30_YYYY-MM-DD.csv` | recommend_holistic.py | VN30 book |
| `telegram_run_YYYY-MM-DD.log` | telegram_run_daily.sh | Daily run log (auto-rotated 30d) |
| `test_state_p3_cache.pkl` | test_state_var_with_p3.py | Backtest signals cache (~15MB) |
| `qwf_report_YYYY-MM-DD.csv` | quarterly_walkforward.py | Quarterly snapshot |
| `qwf_ba_nav_YYYY-MM-DD.csv` | quarterly_walkforward.py | NAV trace per snapshot |
| `qwf_tracking_log.csv` | quarterly_walkforward.py | Quarterly tracking history |

## Dependencies graph

```
recommend_holistic.py
  ├── pandas, numpy, requests
  ├── bq CLI (Google Cloud SDK)
  ├── tav2_bq.ticker (BQ)
  ├── tav2_bq.ticker_1m (BQ)
  ├── tav2_bq.ticker_prune (BQ)
  ├── tav2_bq.vnindex_5state (BQ)
  ├── tav2_bq.fa_ratings (BQ)
  ├── tav2_bq.ticker_financial (BQ)
  └── fundamental_rating_all.csv (local)

telegram_recommend.py
  ├── recommend_holistic.py (Python import — pulls all its deps)
  ├── telegram_config.json (file)
  └── api.telegram.org (HTTPS POST)

simulate_holistic_nav.py
  ├── pandas, numpy
  ├── bq CLI (for VNI dates, etc.)
  └── (used by tests, not daily run)

test_state_var_with_p3.py
  ├── simulate_holistic_nav.py
  ├── signal_v10_sql.py
  └── test_state_p3_cache.pkl (auto-generated)
```

## Initial deployment checklist

When provisioning a fresh server, copy these files:

```
ba-system/
├── DEPLOYMENT.md
├── BA_SYSTEM_WORKFLOW.md
├── README.md
├── PRODUCTION_FILES.md
├── TELEGRAM_SETUP.md
├── requirements.txt
├── .gitignore
│
├── recommend_holistic.py
├── telegram_recommend.py
├── simulate_holistic_nav.py
├── signal_v10_sql.py
│
├── telegram_config.template.json
│   (DO NOT copy telegram_config.json — create on server with real credentials)
│
├── fundamental_rating_all.csv
│
├── deploy_linux.sh        (use ONE: linux OR windows)
├── deploy_windows.ps1
│
└── test_state_var_with_p3.py
    quarterly_walkforward.py
    export_journal_v6_extended.py
    (other test_*.py as desired)
```

## Files NOT needed in production

These are research scripts created during the optimization rounds. Safe to skip:

- `test_round*.py` (rounds 11-17 backtests, superseded by V11)
- `test_*_v2.py`, `test_*_v3.py` (intermediate experiments)
- `test_etf_realistic.py` (validated, results in memory)
- `test_fresh_q_*.py` variants (validated, V11 SV_TIGHT is final)
- `analyze_*.py`, `backtest_*.py` (analytical, not production)
- `f_system_*.py` (F-system standalone — only F_HADAPTED_MAP is referenced in `recommend_holistic.py`)
- Generated CSVs from previous runs

When in doubt: deploy Tier 1-3 + Tier 5 (auto-deploy scripts). Skip everything else unless reviewing.
