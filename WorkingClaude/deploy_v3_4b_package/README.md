# v3.4b "Định Tâm" — Deploy Package (2026-05-21)

## TL;DR

This package replaces the LIVE 5-state market system (Tinh Tế = `v2g_pe3c_s3`) with **Tam Quan v3.4b "Định Tâm"** in the BigQuery table `tav2_bq.vnindex_5state`.

**No production code change needed.** `recommend_holistic.py` reads from the same table name; new values flow through automatically.

**v3.4b backtest improvement vs LIVE (V11 stack, 12y)**:
- FULL CAGR: +2.17pp (18.98% → 21.14%)
- OOS 24-26 CAGR: **+3.75pp** (25.13% → 28.88%)
- Y2022: **+12.0pp** (-10.5% → +1.5%)
- Q1 2026: **+18.5pp** (-10.16% → +8.30%)
- Wealth ×10.71 vs ×8.57 = **+25% wealth on 12y**

## What's in this package

```
deploy_v3_4b_package/
├── README.md                                          # This file
├── vnindex_5state_tam_quan_v3_4b_full_history.csv     # Current v3.4b state series (2000-07-28 → 2026-05-20, 6282 rows)
├── deploy_v3_4b_to_live.py                            # ONE-TIME: replace LIVE with v3.4b (backs up first)
├── pull_us_market.py                                  # Daily: pull SPX + VIX from yfinance
├── build_v3_1_clean.py                                # Daily: build v3.1 = v3 staging + US override
├── build_v3_4_bull_aware.py                           # Daily: build v3.4b = v3.1 + BTC bypass + RSI gate + conc filter
├── daily_refresh_v3_4b.sh                             # Linux/Mac orchestrator
└── daily_refresh_v3_4b.bat                            # Windows orchestrator
```

## Quick start (3 commands)

```bash
# 1. Verify package + dependencies
cd deploy_v3_4b_package
pip install yfinance pandas numpy   # if not already installed
# bq CLI must be on PATH and authenticated

# 2. Dry-run the deploy (shows plan, no changes)
python deploy_v3_4b_to_live.py --dry-run

# 3. Execute deploy (backs up current LIVE, then replaces)
python deploy_v3_4b_to_live.py
```

After step 3, `tav2_bq.vnindex_5state` contains v3.4b state values. The current LIVE values are preserved in `tav2_bq.vnindex_5state_archive_tinh_te_{TIMESTAMP}` for rollback.

## v11 BA strategy — does it need updating?

**NO.** v11 (`recommend_holistic.py`) reads market state via:

```sql
SELECT s.state FROM tav2_bq.vnindex_5state AS s WHERE s.time = '<today>'
```

The table name is unchanged. Only the **values** in the table change (from `pe3c_s3` smoothed states to v3.4b states). v11 logic — tier classification, sector limits, ETF parking, P3 overheat guard — all stays the same.

→ **Confirmation**: if v11 BA strategy was deployed to developer on 2026-05-19, this v3.4b package is the ONLY thing needed to upgrade. No v11 re-deploy required.

## Daily refresh — pipeline overview

```
                                  ┌───────────────────────────────────────┐
                                  │ Existing upstream pipeline (no change)│
                                  │  - Raw factor computation              │
                                  │  - vnindex_5state_dual_v3_staging.csv  │
                                  │  - vnindex_5state_dual_v3_full.csv     │
                                  │  - concentration_history.csv           │
                                  │  - vnindex_5state_ew_full.csv          │
                                  └─────────────────┬─────────────────────┘
                                                    │
                                                    ▼
[pull_us_market.py]              ┌──────────────────────────────┐
   yfinance ──→ SPX + VIX  ──→  │ us_market_history.csv         │
                                  └──────────────┬───────────────┘
                                                 │
                                                 ▼
                                  ┌──────────────────────────────────┐
[build_v3_1_clean.py]            │ v3.1 = v3_staging + US override   │
                                  │ → vnindex_5state_tam_quan_v3_1   │
                                  │   _clean.csv                      │
                                  └──────────────┬───────────────────┘
                                                 │
                                                 ▼ (copy → _full_history.csv)
                                  ┌──────────────────────────────────────┐
[build_v3_4_bull_aware.py]       │ v3.4b = v3.1 + BTC bypass            │
                                  │              + RSI gate              │
                                  │              + conc filter           │
                                  │ → vnindex_5state_tam_quan_v3_4b      │
                                  │   _full_history.csv                  │
                                  └──────────────┬───────────────────────┘
                                                 │
                                                 ▼
[deploy_v3_4b_to_live.py]        ┌──────────────────────────────────────┐
                                  │ Backup current LIVE → archive table  │
                                  │ Upload v3.4b CSV → LIVE BQ table     │
                                  │ Verify row count + last 5 rows       │
                                  └──────────────────────────────────────┘
```

Run daily:
```bash
./daily_refresh_v3_4b.sh        # Linux/Mac
daily_refresh_v3_4b.bat         # Windows
```

Schedule via cron (Linux) or Task Scheduler (Windows). Recommended: **18:00 ICT** (after market close).

## Upstream dependencies (must exist in WORKDIR before pipeline runs)

The v3.4b build chain needs these files, which are **already produced by the existing Tinh Tế pipeline**:

| File | Source | Notes |
|------|--------|-------|
| `vnindex_5state_dual_v3_staging.csv` | Raw factor pipeline → `vnindex_5state_dual_v3.py` | 3 cols: time, state, state_raw |
| `vnindex_5state_dual_v3_full.csv` | Same | Full driver columns (Close, r_score_raw, r_score_ew, alpha, concentration_smooth) |

If your developer is already maintaining LIVE Tinh Tế, these files exist. Otherwise, the raw factor pipeline must be set up first (out of scope of this package).

## Logic summary

### v3.4b = v3.1 + 3 layers

```python
# Layer A: Bull-Trend-Confirmed (BTC) US override bypass
BTC[t] = (VNINDEX 6-month return > 15%) AND (VNINDEX > MA200)
if BTC[t]:
    base[t] = state_v3_staging[t]    # bypass US override
else:
    base[t] = state_v31[t]            # use v3.1 (with US override)

# Re-smooth (mode(3) + min_stay(2))
base = smooth(base)

# Layer B: RSI uptrend gate
if base fires 1-step downgrade at t AND RSI(14)[t] >= 55 AND conc[t] <= 0.55:
    state[t] = state[t-1]  # block downgrade
    gate_active = True

# Layer C: Gate exit conditions
while gate_active:
    if RSI < 55: release
    elif base[t] >= block_at: release
    elif (block_at - base[t]) >= 2: release  # real 2-step bear
    else: hold state at block_at
```

### Why each layer

| Layer | Problem solved | Evidence |
|-------|----------------|----------|
| **A. BTC US bypass** | US override fires 100% wrong during VN bull (43 fires post-2014 in bull regime → T+60 mean +17.45%, 100% positive) | Walk-forward 14 variants, plateau 6M T=5-20% |
| **B. RSI gate** | 30/138 downgrades on RSI≥55 + conc≤0.55 are noise (T+20 mean +2.97%, T+60 +6.23%) | F6 diagnostic, V11 +1.04pp CAGR |
| **C. Exit conditions** | Prevent stale gate holds | Backtest confirmed |

## Rollback

If anything goes wrong after deploy:

```bash
# Find your backup table name
bq ls tav2_bq | grep vnindex_5state_archive_tinh_te

# Restore (replace TIMESTAMP with actual)
bq cp tav2_bq.vnindex_5state_archive_tinh_te_{TIMESTAMP} tav2_bq.vnindex_5state
```

LIVE goes back to Tinh Tế within seconds. No code change needed.

## Monitoring after deploy

Recommended 2-week shadow tracking before promoting v3.4b to "permanent LIVE":

```bash
# Run daily; compares v3.4b output to backup table
python shadow_track_v3_4b.py  # (in main WORKDIR — not in this package)
```

Decision criteria after 2 weeks:
- Cum alpha between [-3%, +3%]: ✓ promote permanent
- Gate fired ≥ 1 time: ✓ rule active
- No catastrophic behavior in bull regime: ✓

## Contacts / questions

| Topic | Resource |
|-------|----------|
| v3.4b spec | `memory/tam_quan_v3_4b_dinh_tam.md` |
| Bull psychology insight | `memory/feedback_bull_market_psychology.md` |
| Walk-forward validation | `test_v3_4_btc_walkforward.py` outputs |
| Transitions visualizer | `vnindex_transitions_v3_4b.html` |

## Critical reminders

- **Existing v11 deployment**: NO changes needed. State table swap is transparent.
- **Backup before deploy**: `deploy_v3_4b_to_live.py` does this automatically.
- **Schedule daily refresh**: replace the existing Tinh Tế refresh job with `daily_refresh_v3_4b.sh`.
- **Don't run both**: the OLD Tinh Tế refresh (`deploy_v2g_pe3c_s3.py`) and the new v3.4b refresh both write to `tav2_bq.vnindex_5state` — last one wins. Disable the old job.
