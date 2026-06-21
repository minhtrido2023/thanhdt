# ZIP 1 — DT5G State Engine (`dt5g_state_engine.zip`)

> Includes the **breadth-decoupling guard** on the US pillar (added 2026-05-29): suppress
> the US cap when VN breadth is broadly healthy while the US panics — fail-safe, free
> insurance. **System name: DT5G** (now includes the gate). Gates: 1-4 DT 4-gate · 5 Macro
> (SBV money + US panic) · breadth-decoupling guard.

LAYER 1 of the go-live system. Self-updates the Vietnam market 5-state from the freshest
BigQuery `ticker` data, applies the macro overlay (SBV money + US panic) **+ the breadth
decoupling guard**, health-checks the feeds, and publishes a **fail-safe gated state** to
BQ for the recommender (ZIP 2) to consume.

## Contents
```
publish_gated_state.py        ENTRY — gated state -> BQ vnindex_5state_dt5g_live + json
macro_state_live.py           DT5G state + get_gated_state() fail-safe gate
macro_healthcheck.py          feed staleness/sanity/heartbeat -> data/macro_health.json (exit 0/1/2)
rebuild_state_from_ticker.bat orchestrates the state chain (BQ ticker -> v3.4b -> DT4-gate), LOCAL only
pull_us_market.py             US VIX/SPX (Pillar B) -> us_market_history.csv
sbv_macro_overlay.py          SBV refi events (Pillar A)
build_dt_4gate.py             DT 4-gate causal commit
simulate_holistic_nav.py      provides bq() + BQ_BIN (BigQuery CLI wrapper)
telegram_recommend.py         optional alert channel (send_telegram_text)
telegram_config.template.json fill in bot_token + chat_id -> save as telegram_config.json (NOT shipped)
chain/                        vnindex_5state_ew_v1.py, build_concentration_history.py, vnindex_5state_dual_v3.py
deploy_v3_4b_package/         build_v3_1_clean.py, build_v3_4_bull_aware.py
requirements.txt
```

## ⚠️ SETUP (must do before running — these are from a research repo)
1. **Hardcoded paths**: every `*.py` and `*.bat` here sets `WORKDIR = r"C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude"` (and `simulate_holistic_nav.BQ_BIN` points at a gcloud `bq.cmd`). **Edit these to your environment** (one constant near the top of each file; `rebuild_state_from_ticker.bat` sets `WORKDIR`/`STATE_WORKDIR`). The chain builders honor the `STATE_WORKDIR` env var.
2. **BigQuery**: install Google Cloud SDK, `gcloud auth login`, project `lithe-record-440915-m9`, dataset `tav2_bq` (asia-southeast1). Set `BQ_BIN` to your `bq.cmd`/`bq` path.
3. **Python**: `pip install -r requirements.txt` (pandas, numpy, yfinance).
4. **Alerts (optional)**: copy `telegram_config.template.json` → `telegram_config.json`, fill bot_token + chat_id.

## Daily run order
```
python pull_us_market.py
rebuild_state_from_ticker.bat          (or call the chain steps it lists)
python macro_healthcheck.py            # writes data/macro_health.json (HEALTHY/DEGRADED/FAILED)
python publish_gated_state.py          # publishes gated state to BQ + golive_state_today.json
```

## What it guarantees
- The state **tracks BQ `ticker`** (no dependence on a pre-baked, possibly-stale state table).
- `get_gated_state()` serves the macro DT5G state **only when feeds are healthy**; otherwise it
  **fails closed to DT4-only** — never trusts a stale macro cap.
- Output consumed by ZIP 2: BQ table `tav2_bq.vnindex_5state_dt5g_live` + `golive_state_today.json`.

## Reconciliation kit (reproduce + diagnose the ~1% gap)
Shipped in this zip:
- **`dt5g_transitions.csv`** — every DT5G state transition 2000→now (date, from→to, driver,
  cap, breadth_decoupled, prev-state duration). 112 transitions; canonical NAV 20.13% / ~114B.
- **`dt5g_daily_reference.csv`** — per-day reference: `time, vnindex_close, dt4_state,
  dt5g_state, cap, easing_conf, breadth_decoupled, weight, nav, nav_rebased_1B`.
- **`reconcile_dt5g.py`** — point it at YOUR daily output to find the FIRST divergent
  date + the top dates driving the NAV gap:  `python reconcile_dt5g.py YOUR_daily.csv`
  (auto-detects date/state/weight/nav columns; reference defaults to the shipped CSV).

**Known gap (already diagnosed):** the live engine warms the DT-4gate commit from
2014-01-01, so the committed state in **May–Jun 2014 (≈11 sessions)** differs from the
full-history reference (live=CRISIS vs ref=NEUTRAL) — a warm-up boundary artifact, not a
bug. It accounts for most of the ~1% NAV gap. To match the reference exactly, warm the
DT-4gate from pre-2014 history (or ignore the first ~6 months of 2014). After mid-2014 the
two series are identical. Use `reconcile_dt5g.py` to confirm on any rebuild.
