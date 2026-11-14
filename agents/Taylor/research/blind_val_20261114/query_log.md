# query_log.md — mọi truy vấn BQ (nguyên văn), lượt định giá mù PAT 14/11/2026

## Q1 — ticker_financial PAT (cột cơ bản; KHÔNG cột giá/PE/PB/PCF/PS/EV/MarketCap/DY/PEG/BVPS/EPS)
```sql
SELECT f.quarter, f.time, f.Release_Date, f.Revenue_P0, f.NP_P0, f.GPM_P0, f.ROE_Trailing, f.ROIC_Trailing, f.ROIC3Y, f.ROIC5Y, f.ROIC10Y, f.ROE3Y, f.ROE5Y, f.CF_OA_P0, f.CF_Invest_P0, f.totalAsset_P0, f.StLiab_P0, f.LtLiab_P0, f.StDebt_P0, f.LtDebt_P0, f.Cash_P0, f.OShares FROM tav2_bq.ticker_financial AS f WHERE f.ticker = 'PAT' ORDER BY f.time
```
Kết quả: calc/bq_tf_pat.csv (19 dòng, 2022Q1→2026Q3). Lần chạy đầu ghi file thất bại do đường dẫn tương đối (wc_env.sh đổi cwd) ⇒ chạy lại y nguyên lệnh với đường dẫn tuyệt đối.

## Q2 — commodity_prices sunsirs P4 + coke, TB theo quý (bỏ T7/CN)
```sql
SELECT c.metric_key, FORMAT_DATE('%Y', c.observation_date) AS y, EXTRACT(QUARTER FROM c.observation_date) AS q, ROUND(AVG(c.value),0) AS avg_v, COUNT(*) AS n, MIN(c.observation_date) AS d0, MAX(c.observation_date) AS d1 FROM tav2_bq.commodity_prices AS c WHERE c.source = 'sunsirs' AND c.metric_key IN ('yellow_phosphorus','coke') AND EXTRACT(DAYOFWEEK FROM c.observation_date) NOT IN (1,7) GROUP BY 1,2,3 ORDER BY 1,2,3
```
Kết quả: calc/bq_commod_q.csv

## Q3 — ticker PAT CHỈ time + Volume (số cổ phiếu khớp), từ 2026-05-01
```sql
SELECT t.time, t.Volume FROM tav2_bq.ticker AS t WHERE t.ticker = 'PAT' AND t.time >= '2026-05-01' ORDER BY t.time
```
Kết quả: calc/bq_vol_pat.csv
