# ZIP 2 — V4 + DT5G Recommender (`v4_dt5g_recommender.zip`)

LAYER 2 of the go-live system. Consumes the gated DT5G state (published by ZIP 1) + the live
`SIGNAL_V11`, and emits **today's order/position recommendations** for the **V4** system
(`V121_ENS` + **BASE** parking `{3:0.7}`).

> Requires ZIP 1 (DT5G State Engine) deployed in the SAME working folder and run first each day —
> ZIP 2 reads BQ `tav2_bq.vnindex_5state_dt5g_live` and `golive_state_today.json` that ZIP 1 produces.

## Contents
```
golive_recommend.py                       ENTRY — V4+DT5G -> out/golive_recommendations_<DATE>.{md,csv}
golive_daily.bat                          full daily orchestrator (runs ZIP-1 steps then this)
signal_v11_sql.py                         live BA SIGNAL_V11 (point-in-time)
simulate_holistic_nav.py                  provides bq() + BQ_BIN
compare_v11_v12_concentration_switch.csv  cached M1 signal (ensemble switch input)
earnings_events_classified.csv            LAGGED earnings-drift schedule input
README.md                                 full architecture / fail-safe / config reference
requirements.txt
```

## ⚠️ SETUP
1. **Hardcoded paths**: edit `WORKDIR` in `golive_recommend.py` / `simulate_holistic_nav.py` (and `BQ_BIN`) to your environment. `golive_daily.bat` sets `ROOT`/`PKG` — edit those.
2. Same **BigQuery** + **Python deps** prerequisites as ZIP 1.
3. Place ZIP 1 and ZIP 2 files in the **same folder** (the orchestrator + state publish expect it).

## Run
```
python golive_recommend.py        # after ZIP-1 published today's gated state
# or, end-to-end (ZIP1 + ZIP2):
golive_daily.bat                  # 1 scheduled task ~15:30 ICT after market close
```

## Output — `out/golive_recommendations_<DATE>.md` / `.csv`
- **Market state (gated)** + **source** (`DT5G_macro` normal / `DT4_only` if gate reverted) + **ETF parking %**.
- **Ensemble mode today** → 2nd-leg book = **VN30** (V11-mode) or **LAGGED** (V12-mode).
- **BAL book** (50%): ranked BA-core picks, 10% NAV/slot, max 12, Fin/RE cap 4, hold 45d, stop −20%.
- **2nd leg** (50%): VN30 picks or LAGGED entries due.
- A NEUTRAL "quiet day" correctly shows **no new entries → hold + park** (not an error).

## Switch V4 → V5 (KELLY)
One knob: in `golive_recommend.py` set `ETF_BASE = {3: 1.0}` (KELLY parking). V4 = balanced
(better Calmar/DD, recommended); V5 = higher raw return, deeper DD.

## Validation (backtest, full 2014→2026-05-15, real E1VFVN30, prod-spec)
V4: CAGR ~22.5% / Sharpe 1.56 / MaxDD −16.7% / Calmar 1.24. Apply ~−1.5pp/yr real-world haircut.
Logic mirrors the validated `run_5systems_dt4.py` V4 leg, evaluated point-in-time for "today".
