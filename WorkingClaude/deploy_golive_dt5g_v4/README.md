# V2.3 + DT5G — Go-Live Deploy Package (dev)

> **2026-06-12: Layer 2 swapped V4 → V2.3** (`golive_recommend_v23.py`). The V4 recommender
> (`golive_recommend.py`) is retired from production and kept as a paper-trade benchmark only.
> Delta notes for the production team: `README_zip3_v23.md`. Layer 1 (state engine) is unchanged.

Production deploy for the **V2.3** system (**BAL | LAG static two-book** + state-conditional
LAG/BAL allocator + parking `{3:0.7}` on both books + CAPIT v2 sleeves) running on the
**DT5G** market-state engine (DT 4-gate + macro overlay, fail-safe to DT4). Emits **daily
order/position recommendations** for the desk.

Two layers, exactly as scoped:

| Layer | What | Entry point |
|---|---|---|
| **1 — DT5G state engine** | Self-updates the market state from the freshest BQ `ticker`, applies the macro overlay, health-checks the feeds, and publishes a **fail-safe gated state** | `publish_gated_state.py` (+ `rebuild_state_from_ticker.bat`, `macro_healthcheck.py`, `pull_us_market.py`) |
| **2 — V2.3 recommender** | Consumes the gated state + live `SIGNAL_V11`, emits today's BAL picks, LAG/PEAD entries due, allocator w_LAG target, ETF parking, CAPIT washout monitor | `golive_recommend_v23.py` |

Run the whole thing daily with **`golive_daily.bat`** (one scheduled task, ~15:30 ICT after close).

---

## Daily flow (what golive_daily.bat does)

```
[1] pull_us_market.py            -> us_market_history.csv         (US VIX/SPX, Pillar B)
[2] rebuild_state_from_ticker.bat-> vnindex_5state_*v3_4b*.csv,    (state SELF-UPDATES from BQ ticker;
                                    vnindex_5state_dt_4gate.csv      ew_v1->dual_v3->v3.1->v3.4b->dt4gate; LOCAL only, no BQ deploy)
[3] macro_healthcheck.py         -> data/macro_health.json         (feed staleness/sanity/heartbeat; exit 0/1/2)
[4] publish_gated_state.py       -> BQ vnindex_5state_dt5g_live     (FAIL-SAFE gated state: DT5G if healthy else DT4)
                                    + golive_state_today.json
[5] golive_recommend_v23.py      -> out/golive_v23_recommendations_<DATE>.md / .csv
                                    + data/golive_v23_status.json (allocator/capit state for the report)
```

## The fail-safe (why this is safe to go live with)

- The macro overlay (DT5G) is a **de-risk** layer. Its dangerous failure is *silent staleness*
  (a dead feed keeps the cap from firing). `macro_healthcheck.py` makes that loud.
- `publish_gated_state.py` calls `macro_state_live.get_gated_state()`, which reads
  `data/macro_health.json` and **serves DT5G only when feeds are healthy; otherwise it reverts to
  DT4-only** (fail-closed). So a broken macro feed degrades gracefully to the plain DT4 state — it
  never trusts a stale cap.
- Health = **HEALTHY / DEGRADED / FAILED**; a Telegram alert fires on DEGRADED/FAILED (config in
  `../telegram_config.json`). INFO nudges (e.g. SBV refi verify-reminder) don't alert.

## Reading the daily recommendation

`out/golive_v23_recommendations_<DATE>.md`:
- **Market state (gated)** + **source** (`DT5G_macro` normal, `DT4_only` if the gate reverted).
- **Allocator w_LAG**: target by state (CRISIS 50% / BEAR 0% / NEUTRAL·BULL·EX-BULL 65%) vs current,
  rebalance ONLY when the gap exceeds ±10pp (band trigger — let the winner run).
- **ETF parking** (70% of idle cash in E1VFVN30 in NEUTRAL, BOTH books).
- **BAL book** (momentum): ranked BA-core picks, **10%/slot of the BAL book, max 12, Fin/RE cap 4**,
  hold 45d, stop −20%; 8L rating≥4 names half-size in BEAR/CRISIS; momentum tiers blocked in EX-BULL.
- **LAG book** (PEAD, always-on — no ensemble switch): entries due T+5 after a strong quarterly
  release, hold 25td, NO stop, LAG_HI 10% / LAG_LO 8% per slot.
- **CAPIT v2 monitor**: oversold breadth vs the 30% washout gate; when fired → state-routed size +
  quality-golden basket (hold 60td, stop/slot-exempt).
- A *quiet day* (NEUTRAL, no momentum signals, no PEAD due) correctly shows **no new entries →
  hold + park** — that is expected, not a bug.

## Prerequisites

1. **Python**: `pip install -r requirements.txt` (pandas, numpy, yfinance).
2. **Google Cloud SDK `bq` CLI** installed + authenticated (`dtienthanh@gmail.com`), project
   `lithe-record-440915-m9`, dataset `tav2_bq` (asia-southeast1). Path used:
   `C:\...\google-cloud-sdk\bin\bq.cmd` (see `simulate_holistic_nav.BQ_BIN`).
3. **Shared scripts/data in the repo root** (this package orchestrates them; it is not standalone):
   `macro_state_live.py`, `macro_healthcheck.py`, `pull_us_market.py`,
   `rebuild_state_from_ticker.bat`, `sbv_macro_overlay.py`, `signal_v11_sql.py`,
   `simulate_holistic_nav.py` (⚠️ use the copy from the V2.3 zip — carries the 0-row `bq()` fix),
   `earnings_events_classified.csv` + `earnings_surprise_data.pkl` (LAG/PEAD schedule inputs),
   plus the state-chain builders under `deploy_v3_4b_package/`. Optional Telegram report:
   `telegram_recommend.py`, `recommend_holistic.py`, `fundamental_rating_all.csv`, `data/rating_8l.csv`.
4. **BQ tables** beyond `ticker*`: `fa_ratings` (D1 gate), `fa_ratings_8l` (weak-size flag — stale
   ratings degrade gracefully to "no weak flag", never block the run).

## Config knobs

| Where | Knob | Default (V2.3) |
|---|---|---|
| `golive_recommend_v23.py` | `STATE_LAG_WEIGHT` allocator | `{1:.50, 2:0, 3:.65, 4:.65, 5:.65}` — do NOT retune to history |
| `golive_recommend_v23.py` | `ALLOC_BAND` rebalance trigger | 0.10 (±10pp; ±15 is too loose — CRISIS de-risk sits on the edge) |
| `golive_recommend_v23.py` | `ETF_PARK` parking | `{3: 0.7}` (both books) |
| `golive_recommend_v23.py` | `MAX_POS`, `POS_PCT`, `WEAK_PCT` | 12, 0.10, 0.05 |
| `golive_recommend_v23.py` | `WASHOUT_GATE` (CAPIT) | 0.30 |
| `macro_healthcheck.py` | `*_MAX_TDAYS` staleness thresholds | 3 trading days |
| `macro_state_live.py` | `get_gated_state(max_health_age_min=...)` | 1440 (24h) |

## Outputs / artifacts

- `out/golive_v23_recommendations_<DATE>.md` / `.csv` — the daily desk recommendation.
- `data/golive_v23_status.json` — allocator/capit/regime status (read by the Telegram report).
- `golive_state_today.json` — today's gated state + provenance (source, DT4 vs DT5G).
- repo root: `vnindex_5state_dt5g_live.csv` + BQ `tav2_bq.vnindex_5state_dt5g_live` (the published gated series).
- `data/macro_health.json`, `data/macro_health_last_success.txt`, `data/golive_run_<DATE>.log`.

## Provenance / validation

- **V2.3** faithful single-ledger backtest 2014→2026-06 (real fills, 50B): plain-sum champion
  (V2.3C) **25.77% CAGR / Sharpe 1.65 / MaxDD −20.1%**; with the live allocator + band (V2.3A,
  this package): **26.29% / Sharpe 1.80 / MaxDD −18.3% / Calmar 1.43**. Apply ~−1.5pp/yr
  real-world haircut.
- **V4 (replaced)**: the ensemble switch never survived a real ledger — faithful 14.20% / Sharpe 1.10.
  V4 keeps running as the paper-trade **control arm** of the forward OOS showdown, not production.
- DT5G macro overlay is **dormant** in benign regimes (≈1.9% of modern days change state; 0 since 2024);
  it engages mainly in stress (SBV-tighten / US-panic). Improves DD/Calmar; see `data/dt4g_macro_overlay_report.md`.
- Recommendation logic mirrors the validated `pt_v22_dt5g.py` engine (same SIGNAL_V11 + D1 + SV_TIGHT
  + overheat + AVOID_exbull + regime_size + LAG schedule + allocator + CAPIT v2), evaluated
  point-in-time for "today" instead of as a NAV backtest.
