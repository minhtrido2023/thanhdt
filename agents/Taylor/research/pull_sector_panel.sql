WITH base AS (
  SELECT t.ticker, t.time, t.ICB_Code, t.PE, t.profit_2M,
         t.NP_P0+t.NP_P1+t.NP_P2+t.NP_P3 AS ttm_np,
         t.CF_OA_P0+t.CF_OA_P1+t.CF_OA_P2+t.CF_OA_P3 AS ttm_cfo
  FROM tav2_bq.ticker_prune AS t
  WHERE EXTRACT(MONTH FROM t.time) IN (1,4,7,10)
    AND EXTRACT(DAY FROM t.time) <= 7
    AND t.time >= '2014-01-01' AND t.time <= '2025-12-31'
    AND t.PE > 0
    AND t.NP_P0 IS NOT NULL AND t.NP_P1 IS NOT NULL AND t.NP_P2 IS NOT NULL AND t.NP_P3 IS NOT NULL
    AND t.CF_OA_P0 IS NOT NULL AND t.CF_OA_P1 IS NOT NULL AND t.CF_OA_P2 IS NOT NULL AND t.CF_OA_P3 IS NOT NULL
    AND t.profit_2M IS NOT NULL
    AND NOT (t.ICB_Code = 8355)
    AND NOT (t.ICB_Code >= 8530 AND t.ICB_Code <= 8579)
    AND NOT (t.ICB_Code = 8777)
    AND NOT (t.ICB_Code = 8633)
),
dedup AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY ticker, EXTRACT(YEAR FROM time), EXTRACT(QUARTER FROM time) ORDER BY time ASC) AS rn
  FROM base
)
SELECT ticker, time, ICB_Code, PE, profit_2M, ttm_np, ttm_cfo,
       1.0/PE AS ey,
       (ttm_np - ttm_cfo)/ABS(ttm_np) AS accrual_ratio
FROM dedup
WHERE rn = 1 AND ttm_np > 0
ORDER BY time, ticker
