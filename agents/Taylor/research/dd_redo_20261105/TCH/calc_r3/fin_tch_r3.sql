SELECT f.ticker, f.time, f.quarter, f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.CF_OA_3Y, f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3, f.OShares, f.ROE_Min3Y
FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
WHERE f.ticker = 'TCH' AND f.time >= '2025-06-01'
ORDER BY f.time
