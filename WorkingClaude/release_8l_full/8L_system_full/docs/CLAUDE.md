# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## BigQuery (Google Cloud)

- **Project ID**: `lithe-record-440915-m9`
- **Dataset**: `tav2_bq` (location: `asia-southeast1`)
- **CLI**: `bq` — Google Cloud SDK installed at `C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\`. Must be on PATH before use (see invocation pattern below). Authenticated as `dtienthanh@gmail.com`. Always use `--use_legacy_sql=false` for standard SQL.
- **Column dictionary**: `bigquery_dictionary.json` — full semantic descriptions for every column (ranges, formulas, meaning). Always consult it before writing filters or queries.

### Tables

#### `tav2_bq.ticker`
Daily OHLCV + derived indicator data per ticker. Main feature table for ML training and evaluation.
- **Rows**: ~15.2M | **Size**: ~16.3 GB
- **Partitioned**: by `time` (DATE, DAY) | **Clustered**: by `ticker`
- **Date range**: 2014-01-02 → 2026-04-03 | **Tickers**: ~1,272
- **Column groups**:
  - Price/volume: `time`, `ticker`, `Open`, `High`, `Low`, `Close` (adj), `Price` (unadjusted), `Volume`, `Close_T1`, `Close_T1W`
  - Moving averages: `MA10/20/50/200` and `_T1` variants (prior-day MA)
  - RSI: `D_RSI` (0–1 daily), `D_RSI_T1/T1W`, `D_RSI_Max1W/3M` + `_Close/_MACD` at that peak, `D_RSI_Min1W/3M` + `_Close`, `D_RSI_MinT3`
  - CMF/MACD: `D_CMF` (0–1), `D_MACDdiff` (MACD − MACDsign)
  - CMB: `D_CMB` (−1..2 index), `D_CMB_XFast` (periods since CMB crossed fast line, 0=strong), `D_CMB_Peak_T1` (−1/0/1 weekly CMB top/bottom)
  - Price ratios: `C_L1W` (Close/Lowest 1W, 0–1), `C_L1M` (Close/Lowest 1M)
  - Volume analytics: `Volume_1M` (mean daily 1M), `Volume_3M_P50/P90`, `Volume_Max1Y_High/ID`, `Volume_Max5Y_High`, `Volume_MaxTop5_2Y_Close/ID`
  - VAP (volume-at-price): `VAP1W/1M/3M` — close in the largest trading area
  - Support/resistance: `Res_1Y`, `Sup_1Y` (lookback 1 year)
  - VAP crossdown indices: `ID_XVAP1M_Down_P2`, `ID_XVAP3M_Down_P0`
  - Price extremes: `HI_3M_T1`, `LO_3M_T1`, `ID_HI_3Y`, `ID_LO_3Y`
  - VNINDEX mirror: `VNINDEX`, `VNINDEX_RSI`, `VNINDEX_CMF`, `VNINDEX_MACDdiff`, `VNINDEX_RSI_MinT3`, `VNINDEX_RSI_Max1W/3M` + `_Close/_MACD`
  - Financial (joined from `ticker_financial`): `PE`, `PB`, `PS`, `PCF`, `EVEB`, `EPS`, `DY`, `PEG`, `BVPS`, `ROE5Y`, `ROIC5Y`, `ROIC3Y`, `ROIC_Min3Y/5Y`, `ROE_Min3Y/5Y`, `FSCORE`, `Debt_Eq_P0`, `NP_P0–P4`, `CF_OA_P0–P3`, `CF_Invest_P0–P3`, `NPM_P0`, `IntCov_P0`, `PE_MA5Y/1Y/3M`, `PE_SD5Y/1Y/3M`, `PB_MA5Y/1Y/3M`, `PB_SD5Y/1Y/3M`, `EVEB_MA5Y/1Y/3M`, `EVEB_SD5Y/1Y/3M`, `ROIC_Trailing`, `CF_OA_5Y`, `CF_Invest_5Y`
  - ML targets (**forward-looking — training only, never use for live filtering**): `profit_2W` (T+10), `profit_1M` (T+20), `profit_2M` (T+40), `profit_3M` (T+60) + centered smoothed variants (`profit_*_center_3/5/7/10/11/15/20`)
  - Meta: `Risk_Rating` (composite Beta+Dev score), `ICB_Code` (CT/NH/BH/CK industry), `ID_Release`, `ID_Current`, `Inflation_7` (7% annual inflation constant)

#### `tav2_bq.ticker_financial`
Quarterly fundamental financial data per ticker. Source of all financial ratios; joined into `ticker` by `(ticker, time)`.
- **Rows**: ~63.6K | **Size**: ~54 MB | **Clustered**: by `ticker`
- **Date range**: 2000-07-31 → 2026-04-03 | **Tickers**: ~1,255
- **Column groups**:
  - Identity: `ticker`, `time` (DATE), `quarter` (e.g. `"2025Q3"`), `Release_Date`, `ID_Release`
  - Net profit: `NP_R` (YoY ratio = NP_P4/NP_P0−1), `NP_P0–P7` (quarterly, 0=current), `NP_Q_Min5Y`
  - Revenue: `Revenue_P0–P7`, `Revenue_YoY_P0` (P0/P4−1), `Revenue_YoY_P4` (P4/P8−1)
  - Gross margin: `GPM_P0–P7` (%)
  - Margins: `NPM_P0/P4` (Net Profit Margin %), `EBITM_P0/P4` (EBIT Margin %), `ROA_P0/P4`
  - Liquidity: `CR_P0/P4` (Current Ratio), `QuickR_P0/P4`, `CashR_P0/P4`
  - Efficiency: `AssetTurn_P0/P4`, `FAssetTurn_P0/P4`, `InvTurn_P0/P4`, `DSO_P0/P4`, `DIO_P0/P4`, `DPO_P0/P4`, `CashCycle_P0/P4`
  - Leverage: `Debt_Eq_P0/P4`, `STLTDebt_Eq_P0/P4` (ST+LT debt/equity), `FinLev_P0/P4`, `FAsset_Eq_P0/P4`, `OwnEq_Cap_P0/P4`, `IntCov_P0/P4`
  - Balance sheet: `totalAsset_P0`, `StLiab_P0`, `LtLiab_P0`, `StDebt_P0`, `LtDebt_P0`, `AR_P0`, `EBITDA_P0`, `LtInvest_P0`, `Inventory_P0`, `Cash_P0` (cash + ST investments)
  - Valuation: `PE`, `PB`, `PS`, `PCF`, `EVEB` (EV/EBITDA), `EPS`, `EPS_P0` (VND/share), `BVPS`, `OShares`, `DY`, `PEG` (PE/growth where growth=(NP_P0/NP_P4−1)×100)
  - Valuation history: `PE_MA5Y/1Y/3M`, `PE_SD5Y/1Y/3M`, `PB_MA5Y/1Y/3M`, `PB_SD5Y/1Y/3M`, `EVEB_MA5Y/1Y/3M`, `EVEB_SD5Y/1Y/3M`
  - Quality (multi-year): `ROE3Y/5Y/10Y` (avg), `ROE_Min3Y/5Y/10Y`, `ROIC3Y/5Y/10Y` (avg), `ROIC_Min3Y/5Y/10Y`, `ROE_Trailing` (sum last 4Q), `ROIC_Trailing` (self-calc), `ROIC_Trailing_v1` (report-sourced)
  - Cash flow: `CF_OA_P0–P4` (operating/assets), `CF_OA_3Y/5Y` (sum), `CF_Invest_P0–P4` (capex), `CF_Invest_3Y/5Y` (sum)
  - Dividend: `DY`, `Dividend_Min3Y`, `Dividend_1Y`, `Dividend_3Y`
  - Piotroski: `FSCORE` (0–9, current), `FSCORE_P1` (prior quarter)

#### `tav2_bq.risk_rating`
Quarterly risk ratings per ticker.
- **Rows**: ~252K | **Size**: ~5.7 MB | **Clustered**: by `ticker`
- **Key columns**: `quarter` (STRING), `ticker`, `Beta`, `D_Beta`, `Dev`, `D_Dev`, `Risk_Rating` (composite Beta+Dev bins)

#### `tav2_bq.ticker_1m`
Rolling ~1-month snapshot — used for live screening and daily evaluation.
- **Rows**: ~26K | **Size**: ~28 MB | **Partitioned**: by `time` (DATE, DAY) | **Clustered**: by `ticker`
- **Schema**: Same as `ticker` plus extended columns:
  - Trading value: `Trading_Value`, `Trading_Value_1M_P50`, `Trading_Value_Total_1W`, `Trading_Value_Total_1W_Max6M`
  - Price change: `PC_6M`, `PC1W/2W/3W/1M/2M`, `Open_1D`, `Close_2Y_P90`
  - Outcome stats: `O1W`, `O2W`, `O3W`, `O1M`, `O2M`, `O3M`, `O6M`, `O1Y`, `O2Y`
  - Pattern stats (3Y lookback): `Pattern_Median_Profit_3Y`, `Pattern_Deal_Count_3Y`, `Pattern_Winrate_3Y`
  - Technical extras: `D_MACD`, `D_MACD_T1W`, `D_MFI`, `D_MFI_T1W`, `Volume_Max1Y`, `Volume_1M_P50`
  - Session/risk: `Trading_Session`, `Risk_Rating`

#### `tav2_bq.ticker_prune`
High-quality ticker subset — ~449 selected tickers with full history from 2014.
- **Rows**: ~711K | **Size**: ~902 MB | **Partitioned**: by `time` (DATE, DAY) | **Clustered**: by `ticker`
- **Schema**: Same as `ticker_1m` (all extended columns included)
- **Use for**: ML training and backtesting on a quality-filtered universe

### Naming conventions
- `_P0` = current quarter, `_P1` = 1 quarter ago, …, `_P4` = 4 quarters ago (≈1 year), `_P7` = 7 quarters ago
- `_R` suffix = reported raw value (e.g. `NP_R` = YoY ratio)
- `_T1` = 1 trading day ago, `_T1W` = 1 week ago, `_MinT3` = min over last 3 days
- `_Min3Y/5Y/10Y` = minimum over N years (quality floor)
- `_Trailing` = sum of last 4 quarters (TTM approximation)
- `_MA1Y/3M` = moving average; `_SD` = standard deviation; `_P50/P90` = percentile

### Invoking bq on Windows

The SDK `bin` and bundled Python are configured in `~/.bashrc` — `bq` works directly from bash:

```bash
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 "YOUR SQL HERE"
```

If for any reason the env vars are missing, they are:
```bash
export PATH="$PATH:/c/Users/hotro/AppData/Local/Google/Cloud SDK/google-cloud-sdk/bin"
export CLOUDSDK_PYTHON="/c/Users/hotro/AppData/Local/Google/Cloud SDK/google-cloud-sdk/platform/bundledpython/python.exe"
```

**Critical gotcha — table/column name collision**: Tables named `risk_rating`, `ticker`, etc. share names with columns. BigQuery will resolve an unqualified reference (e.g. `GROUP BY Risk_Rating`) to the *table* (returning a STRUCT) instead of the column. Always alias tables and qualify column references:

```sql
-- WRONG: GROUP BY Risk_Rating resolves to the row struct
SELECT Risk_Rating, COUNT(*) FROM tav2_bq.risk_rating GROUP BY Risk_Rating

-- CORRECT: alias the table and qualify columns
SELECT t.Risk_Rating, COUNT(*) FROM tav2_bq.risk_rating AS t GROUP BY t.Risk_Rating
```

### Example queries

```bash
# Preview ticker data for a stock
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 'SELECT * FROM tav2_bq.ticker AS t WHERE t.ticker="VNM" ORDER BY time DESC LIMIT 5'

# Get latest quarterly financials for a ticker
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 'SELECT t.ticker, t.quarter, t.NP_P0, t.PE, t.ROIC5Y, t.FSCORE FROM tav2_bq.ticker_financial AS t WHERE t.ticker="VNM" ORDER BY time DESC LIMIT 8'

# Dry-run cost estimate before large queries
bq query --use_legacy_sql=false --dry_run --project_id=lithe-record-440915-m9 'YOUR SQL'
```

### Known data quality notes
- `risk_rating` table contains **duplicate rows** (same ticker + quarter appears twice). Use `GROUP BY` or `SELECT DISTINCT` when aggregating.
- Forward-looking target columns (`profit_2W`, `profit_1M`, etc.) in `tav2_bq.ticker` must **never** be used as live filters — training use only.

## Codebase Architecture

This is a Vietnamese stock market analysis workspace — not a traditional software project. There is no build system, test suite, or package structure. Everything runs as standalone Python scripts.

### Strategy definition: `filter.json`

The single source of truth for all entry/exit signal logic. Keys use a naming convention:
- `_StrategyName` — buy entry filter expression (Python/pandas-style boolean syntax referencing `ticker` table columns)
- `~SignalName` — sell/exit signal expression
- `$StrategyName` — comma-separated list of sell signals that apply to that strategy
- `Init` — base date range guard applied to all buy filters via `{Init}` placeholder
- `MARKET_DICT_FILTER` — market-level VNINDEX filters (separate dict in the same file)

Filter expressions use column names directly (e.g., `Volume_3M_P50`, `PE`, `ROE_Min5Y`). `Inflation_7` is a 7% annual inflation constant used to normalize trading value to real VND.

### SQL generation: `gen_sql.py`

Reads `filter.json`, converts filter expressions from Python syntax to BigQuery SQL WHERE clauses, and writes `.sql` + `.csv` pair files to `sql_queries/`. The script handles:
- `{Init}` placeholder expansion
- Columns missing from `ticker_1m`/`ticker_prune` are stripped from conditions
- Output goes to `sql_queries/buy_StrategyName.sql` and `sell_SignalName.sql`

Run queries via the generated bash script or directly with `bq query`.

### Local data files

- **`VNINDEX.csv`** — full VNINDEX daily history including technical indicators and PE data; used by all market analysis scripts for offline analysis without hitting BigQuery
- **`bigquery_dictionary.json`** — column semantic dictionary; consult before writing filters
- **`filter.json`** — strategy/signal definitions (see above)
- **`sql_queries/*.csv`** — cached query results from last run

### Analysis scripts pattern

All scripts follow the same structure: load data from either BigQuery (via `bq` CLI subprocess or `google-cloud-bigquery` SDK) or local CSVs, compute signals/metrics with pandas/numpy, optionally output to `.png` (matplotlib) or `.csv`. Scripts are self-contained — `WORKDIR` is hardcoded as `C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude`.

Key script groups:
- `backtest_*.py` — strategy backtests (trailing stops, TP/SL, combined systems)
- `analyze_*.py` — signal quality analysis, pattern stats, market phase analysis
- `market_*.py` — market timing systems, state machines, allocation frameworks
- `score_live_signals.py` / `universe_scan.py` — live signal scoring and screening
- `extract_deals.py` — extracts deal records from portfolio data for analysis

### VNINDEX 5-State Market System — PRODUCTION = **DT5G** (`macro_state_live.py`)

**5 states** (shared by all versions): CRISIS(0%), BEAR(20%), NEUTRAL(70%), BULL(100%), EX-BULL(130%).

The LIVE production market-regime source as of 2026-06-02 is **DT5G**, computed by `macro_state_live.py` and published to BQ table **`tav2_bq.vnindex_5state_dt5g_live`**. Production consumers read DT5G via `get_gated_state()` (e.g. `golive_recommend`, `pt_v4_dt5g`, `dna_report.py`, `recommend_tomorrow.py`).

> ⚠️ **Table-label correction (verified by BQ, 2026-06-03):** the no-suffix table `tav2_bq.vnindex_5state` is **NOT DT5G**. It is byte-identical to `tav2_bq.vnindex_5state_tam_quan_v34b_clean` (0 diffs / 6291 rows) = the **v3.4b BASE** (TQ34b, ~153 transitions, **no DT-gate, no macro cap**, only light base smoothing). Real DT5G (49 transitions, DT-gate + macro) lives **only** in `vnindex_5state_dt5g_live`. Distribution gap (2014+): `vnindex_5state` has EX-BULL 194 / CRISIS 748 days; `dt5g_live` has EX-BULL 59 / CRISIS 525 (the DT-gate clamps the extremes hard). Many research scripts read bare `vnindex_5state` assuming it is DT5G — **it is the base only**; this is a known research trap. (An earlier note claimed the 2026-06-02 swap put DT5G into `vnindex_5state` — that was wrong; the no-suffix table still serves the v3.4b base. Archives `vnindex_5state_archive_pre_dt5g_20260602` / `vnindex_5state_archive_tinh_te_20260602_*` exist from that episode.)

**DT5G architecture** (do not change without explicit instruction — source: `macro_state_live.py`):
1. **Base state** = v3.4b ("Định Tâm"), read from BQ `tav2_bq.vnindex_5state_tam_quan_v34b_clean` (== the no-suffix `vnindex_5state` table), warmed up from 2014. (v3.4b itself = the ew_v1 → dual_v3 → v3.1 → v3.4b chain — the `dual_v3` stage carries the v2g **BearDvg gate, `min_dur=30`**; plus bull-aware US-override bypass + RSI/concentration gates.) This base alone runs ~153 transitions.
2. **DT 4-gate** (`_dt_4gate`, = `DT_10_25_25`) — **the primary smoother now** (replaces the Cổ Điển `mode(15) → min_stay_filter(7)` pipeline). Asymmetric causal commitment: a new state must persist `enC=25` sessions to commit INTO CRISIS and `enX=25` INTO EX-BULL (slow to panic / slow to euphoria), but only `exC=10`/`exX=10` to leave them, `default=10` for NEUTRAL/BEAR/BULL moves. Cuts whipsaw from the ~155 base transitions down to ~49–53.
3. **Macro gate** (fuses three rule families into ONE causal cap, no rule-sprawl):
   - **Pillar A — domestic money**: SBV refi-rate 6m momentum (`SBV_REFI_EVENTS` from `sbv_macro_overlay`), lagged 5d. Rising-rate → cap. (The cut-from-peak easing FLOOR is still *computed* but **no longer applied** — see `EASING_FLOOR_ENABLED=False`, changelog 2026-06-03.)
   - **Pillar B — US panic**: VIX + SPX 1y drawdown (`us_market_history.csv`, aligned to VN T-1). Thresholds: VIX>35 / SPX-DD<-25% → CRISIS cap, etc.
   - **v3.4b bull-aware bypass**: in a confirmed VN bull (6m return >15% AND Close>MA200), ignore Pillar B, keep Pillar A.
   - **Defensive action = CAP** the state ceiling on stress (the only active macro action). **Re-risk is now PURELY price-based** via the DT base (slow, price-confirmed) — the macro overlay no longer floors the state back up on a monetary-easing signal (asymmetry; easing FLOOR disabled 2026-06-03, was dormant in the live era since 2014-06 anyway).
   - `cap_commit=7`: a defensive cap must persist 7 sessions before committing (debounces VIX flicker).
4. **Breadth-decoupling guard** on Pillar B (added 2026-05-29, free insurance): suppress the US-panic cap ONLY when VN breadth is broadly healthy while the US panics (genuine US-VN decoupling, e.g. 2025 VIC-led). Fail-safe: weak/missing/small-universe breadth → NO suppression → US cap fires as usual. Breadth = % of `ticker_prune` above MA200, causal (T-1), needs ≥100 names.

**Production state source = `get_gated_state()`** (fail-safe wrapper): returns the DT5G macro state ONLY when `data/macro_health.json` is fresh (<1440 min) and says feeds are trustworthy (`recommended_state_source == "DT5G_macro"`); otherwise fails CLOSED to **DT4-only** (base + DT 4-gate, no macro cap). Consume the `state` column. `state_dt4` = base-without-macro is retained for ablation.

**BQ tables** (labels corrected 2026-06-03 — see ⚠️ note above):
- `tav2_bq.vnindex_5state_dt5g_live` — **DT5G production** (DT-gate + macro, 49 transitions). Read by `get_gated_state` consumers: `golive_recommend`, `pt_v4_dt5g`, `dna_report.py`, `recommend_tomorrow.py`.
- `tav2_bq.vnindex_5state` — **v3.4b BASE, NOT DT5G** (light base smoothing, ~153 transitions). Byte-identical to `vnindex_5state_tam_quan_v34b_clean`. Bare reads of this table get the base, not the production gated state.
- `tav2_bq.vnindex_5state_tam_quan_v34b_clean` — v3.4b base spec (== `vnindex_5state`; daily-refreshed; DT5G reads this as its base input).

**DT5G performance** (event-level audit, 2014→2026-05; source `data/audit_dt5g_events.md`): DT5G == DT4 in benign windows; it deviates on only **49 sessions / 4 de-risk episodes (1.6%)**, 0 re-risk. Integrated prod-spec ablation (DT4 vs DT5G, 50B): **V5 (Kelly) +0.43pp Full** (DT4 23.23% → DT5G 23.67%), **V4 (V121_ENS) +0.27pp Full**; **IS 2014-19 = +0.00pp exactly** (overlay dormant in-sample → walk-forward IS/OOS is the wrong tool here); OOS 2020-now V5 +0.88pp / V4 +0.54pp. Per-year LOO: the entire net edge = the single 2023 tightening (+5pp/yr V5); the 2025 bull COSTS −0.89pp. **Verdict: DT5G is a FAIL-SAFE RISK GATE (insurance), not a return-enhancer** — deploy via `get_gated_state`, do not re-tune to history (params are a robust plateau).

**Changelog**:
- **2026-06-03** — `macro_state_live.py`: set `EASING_FLOOR_ENABLED=False` — disabled the monetary-easing recovery floor (asymmetry: re-risk only via the price-based DT base, never on rate cuts alone). Dormant in the discrete live state since 2014-06 → zero live-behavior change; full-history backtest improved marginally (Full CAGR 19.93→20.05%, Sharpe 1.36→1.37, same MaxDD). `vnindex_5state_dt5g_live` re-published.
- **2026-06-03** — repointed `dna_report.py` (Telegram bot NOW-regime block) and `recommend_tomorrow.py` from bare `vnindex_5state` → `vnindex_5state_dt5g_live` so they report the true DT5G production regime instead of the v3.4b base.
- **2026-06-03** — doc fix: corrected the table labels above (`vnindex_5state` is the v3.4b base, not DT5G).

> **Cổ Điển (archived, NOT live)** — `vnindex_5state_system.py` is the original baseline ("Cổ Điển"), kept for historical reference only. Its smoothing pipeline was **EMA(0.40) → mode(15) → min_stay_filter(7)** over 7 expanding-percentile factors with BearDvg/BullDvg gates. It was superseded by Tinh Te (v2g_pe3c_s3), then v3.4b, then DT5G. The "EMA(0.40) → mode(15) → min_stay_filter(7)" pipeline and its ~16.1%/-62.3% full-period numbers describe this archived version, **not** current production. See [vnindex_5state_registry.md](vnindex_5state_registry.md) for the full lineage.

### Decision Logic — `state_transition_logic.py`

**File**: `state_transition_logic.py` | Self-contained explainer script, no output files. ⚠️ **Explains the archived Cổ Điển pipeline** (mode(15)/min_stay_filter/BearDvg gate), NOT the live DT5G chain. Kept as a historical walk-through of the original factor model; for current production state reasoning use `macro_state_live.py` (DT 4-gate + macro gate).

Explains step-by-step **why** the (Cổ Điển) system is in a given state on any date. Run directly to see:
1. All 7 factor raw values + expanding rank + contribution to composite score
2. EMA smoothing effect on r_score
3. Which classification threshold was crossed (raw state)
4. Which risk overrides fired (PE, DD, Vol)
5. BearDvg gate open/closed + reason
6. Rolling mode window (15 sessions): which state dominated
7. min_stay_filter: how long the current segment has been stable
8. Final state + conditions needed to transition to next state

Also prints last 25 transitions with root cause + full BearDvg gate history.

Use `explain_day("YYYY-MM-DD")` to analyze any specific date.

### Backtest Methodology — `backtest_workflow.py`

**File**: `backtest_workflow.py` | Self-contained explainer, no output files.

Documents the full backtest pipeline and all evaluation methods:

**NAV Simulation mechanics:**
- Single-path NAV, start 1B VND, T+1 execution delay (no look-ahead)
- Ramp 3 sessions to reach target weight (unless diff < 3% → snap immediately)
- Costs per session: TC=0.1% on traded portion, deposit=0%/yr on idle cash (default), borrow=10%/yr on margin (default)
- Formula: `pv[t] = pv[t-1] × (1 + w×r_market + max(0,1-w)×deposit - max(0,w-1)×borrow - |Δw|×TC)`

**7 evaluation dimensions (in order of importance):**
1. **Core metrics**: CAGR, Sharpe, Sortino, MaxDD, Calmar, DDdur — computed on calendar time (not session count), SPY = actual sessions/year (≠252 fixed, accounts for pre-2007 3-day weeks)
2. **Walk-forward IS/OOS** — IS: 2011–2019, OOS: 2020–present; OOS Calmar=1.09 > IS 0.52 → no overfit
3. **State-conditional returns** — forward T+5/T+20/T+60 VNINDEX returns per state; validates predictive ordering BULL>NEUTRAL>CRISIS>BEAR
4. **Annual breakdown** — per-year sys vs B&H; win rate 41% is expected (system protects in bear years, lags in strong bull years)
5. **TC analysis** — TC drag ~0.32%/yr at TC=0.1%; at realistic TC=0.3% → ~0.97%/yr
6. **Sensitivity** — EMA_ALPHA (0.25–0.50) and MIN_STAY (3–20) grid; confirm ms=7, α=0.40 are robust
7. **Known limitations** — no slippage model, no tax, VNINDEX proxy (not actual portfolio), 1B NAV may not scale

**Real-world adjustment**: CAGR_actual ≈ CAGR_backtest − 1.5% (TC + slippage + tax)  
→ 12.1% backtest → ~10.6% realistic, still beats B&H (~9.2%)

### Documentation files

- `market_timing_final_system.md` — backtest results for VNINDEX timing systems (MACD trend, MA200 cross, 5-state machine); important reference for market regime logic
- `market_rule.md` — rules for `MarketEvaluation` class in `webui/utils.py` (external codebase)
- `market_overheat.md` — explains overbuy/oversell detection logic in `webui/utils.py`