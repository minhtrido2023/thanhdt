# query_log.md — mọi truy vấn BQ (nguyên văn)

## Q1 (2026-11-14T20:03:59+07:00) ticker_financial PAT — cột cơ bản, không cột giá
```sql
SELECT f.quarter, f.time, f.Release_Date, f.Revenue_P0, f.NP_P0, f.GPM_P0, f.ROE_Trailing, f.ROIC_Trailing, f.ROIC3Y, f.ROIC5Y, f.ROIC10Y, f.ROE3Y, f.ROE5Y, f.CF_OA_P0, f.CF_Invest_P0, f.totalAsset_P0, f.StLiab_P0, f.LtLiab_P0, f.StDebt_P0, f.LtDebt_P0, f.Cash_P0, f.OShares FROM tav2_bq.ticker_financial AS f WHERE f.ticker = 'PAT' ORDER BY f.time
```
