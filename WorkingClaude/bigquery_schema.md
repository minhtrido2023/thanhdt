# BigQuery — schema chi tiết bảng `tav2_bq`

> Tách khỏi `CLAUDE.md` 2026-08-10: đây là TRA CỨU, không phải chỉ dẫn. Trước đó nó nằm
> trong file luôn-được-nạp nên mọi agent đều phải mang, kể cả Wendy (luật) và Wags (fleet ops).
> Agent nào cần schema thì `@import` file này (Taylor, Winston) hoặc `Read` khi cần.
> Từ điển ngữ nghĩa từng cột đầy đủ: `bigquery_dictionary.json` (file máy đọc, gen_sql.py dùng).

### Tables

#### `tav2_bq.ticker`
Daily OHLCV + derived indicator data per ticker. Main feature table for ML training and evaluation.
- **Rows**: ~15.2M | **Size**: ~16.3 GB
- **Partitioned**: by `time` (DATE, DAY) | **Clustered**: by `ticker`
- **Date range**: 2000-07-28 → 2026-06-15 (backfilled to 2000; VNINDEX also from 2000-07-28. ~648 tickers exist pre-2014-06, but the market was thin pre-2007 — see ticker_prune note) | **Tickers**: ~1,272
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
High-quality ticker subset. Backfilled to **2000-12-15** but the VN market was thin early — distinct names per year: 2000≈2, 2006≈19, **2007≈74, 2008≈105** (crosses ~100), 2014≈203. So breadth/universe signals are only meaningful from ~2008 (pre-2008 too few names; pre-2007 effectively un-investable).
- **Rows**: ~711K | **Size**: ~902 MB | **Partitioned**: by `time` (DATE, DAY) | **Clustered**: by `ticker`
- **Date range**: 2000-12-15 → 2026-06-15
- **Schema**: Same as `ticker_1m` (all extended columns included)
- **Use for**: ML training and backtesting on a quality-filtered universe

