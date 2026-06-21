# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## BigQuery (Google Cloud)

- **Project ID**: `lithe-record-440915-m9`
- **Dataset**: `tav2_bq` (location: `asia-southeast1`)
- **CLI**: `bq` (authenticated, use `--use_legacy_sql=false` for standard SQL)
- **Column dictionary**: `bigquery_dictionary.json` — full semantic descriptions for every column (ranges, formulas, meaning). Always consult it before writing filters or queries.

### Tables

#### `tav2_bq.ticker`
Daily OHLCV + derived indicator data per ticker. Main feature table for ML training and evaluation.
- **Rows**: ~3.19M | **Size**: ~3 GB
- **Partitioned**: by `time` (DATE, DAY) | **Clustered**: by `ticker`
- **Date range**: 2014-01-02 → 2026-03-30 | **Tickers**: ~1,272
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
- **Rows**: ~63.6K | **Size**: ~51 MB | **Clustered**: by `ticker`
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
- **Rows**: ~252K | **Size**: ~5 MB | **Clustered**: by `ticker`
- **Quarter range**: 2000Q3 → 2025Q4 | **Tickers**: ~1,241
- **Key columns**: `quarter` (STRING), `ticker`, `Beta`, `D_Beta`, `Dev`, `D_Dev`, `Risk_Rating` (composite Beta+Dev bins)

#### `tav2_bq.ticker_1m`
Snapshot của ~1 tháng gần nhất — dùng cho live screening và evaluation theo ngày.
- **Rows**: ~26K | **Size**: ~28 MB | **Partitioned**: by `time` (DATE, DAY) | **Clustered**: by `ticker`
- **Date range**: 2026-03-16 → 2026-04-14 | **Tickers**: ~1,252
- **Schema**: giống `ticker` + thêm các cột:
  - Trading value: `Trading_Value`, `Trading_Value_1M_P50`, `Trading_Value_Total_1W`, `Trading_Value_Total_1W_Max6M`
  - Price change: `PC_6M`, `PC1W/2W/3W/1M/2M`, `Open_1D`, `Close_2Y_P90`
  - Outcome (OC) stats: `O1W`, `O2W`, `O3W`, `O1M`, `O2M`, `O3M`, `O6M`, `O1Y`, `O2Y`
  - Pattern stats (3Y lookback): `Pattern_Median_Profit_3Y`, `Pattern_Deal_Count_3Y`, `Pattern_Winrate_3Y`
  - Technical extras: `D_MACD`, `D_MACD_T1W`, `D_MFI`, `D_MFI_T1W`, `Volume_Max1Y`, `Volume_1M_P50`
  - Session/risk: `Trading_Session`, `Risk_Rating`
  - ML targets (training only): `profit_2W/1M/2M/3M` + centered smoothed variants

#### `tav2_bq.ticker_prune`
Subset ticker chất lượng cao — chỉ ~449 tickers được chọn lọc, có full lịch sử từ 2014.
- **Rows**: ~711K | **Size**: ~902 MB | **Partitioned**: by `time` (DATE, DAY) | **Clustered**: by `ticker`
- **Date range**: 2014-01-02 → 2026-04-14 | **Tickers**: ~449
- **Schema**: giống `ticker_1m` (đầy đủ tất cả cột mở rộng)
- **Dùng cho**: ML training, backtesting trên universe tickers chất lượng cao

### Naming conventions
- `_P0` = current quarter, `_P1` = 1 quarter ago, …, `_P4` = 4 quarters ago (≈1 year), `_P7` = 7 quarters ago
- `_R` suffix = reported raw value (e.g. `NP_R` = YoY ratio)
- `_T1` = 1 trading day ago, `_T1W` = 1 week ago, `_MinT3` = min over last 3 days
- `_Min3Y/5Y/10Y` = minimum over N years (quality floor)
- `_Trailing` = sum of last 4 quarters (TTM approximation)
- `_MA1Y/3M` = moving average; `_SD` = standard deviation; `_P50/P90` = percentile

### Example queries
```bash
# Preview ticker data for a stock
bq query --use_legacy_sql=false 'SELECT * FROM `lithe-record-440915-m9.tav2_bq.ticker` WHERE ticker="VNM" ORDER BY time DESC LIMIT 5'

# Get latest quarterly financials for a ticker
bq query --use_legacy_sql=false 'SELECT ticker, quarter, NP_P0, Revenue_P0, PE, PB, ROIC5Y, FSCORE FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` WHERE ticker="VNM" ORDER BY time DESC LIMIT 8'

# Get latest risk ratings
bq query --use_legacy_sql=false 'SELECT * FROM `lithe-record-440915-m9.tav2_bq.risk_rating` WHERE quarter=(SELECT MAX(quarter) FROM `lithe-record-440915-m9.tav2_bq.risk_rating`) ORDER BY Risk_Rating LIMIT 10'

# Join ticker with financial for fundamental screening
bq query --use_legacy_sql=false 'SELECT t.ticker, t.time, t.Close, f.PE, f.ROIC5Y, f.FSCORE FROM `lithe-record-440915-m9.tav2_bq.ticker` t JOIN `lithe-record-440915-m9.tav2_bq.ticker_financial` f USING(ticker, time) WHERE t.time = "2026-03-30" LIMIT 20'

# Dry-run cost estimate before large queries
bq query --use_legacy_sql=false --dry_run 'YOUR_QUERY'
```

