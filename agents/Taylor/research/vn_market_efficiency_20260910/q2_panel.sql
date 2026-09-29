WITH u AS (
  SELECT time, ticker
  FROM `lithe-record-440915-m9.tav2_mike.universe_pit`
  WHERE in_universe = TRUE AND time >= '2006-01-01'
),
px AS (
  SELECT t.time, t.ticker, t.Close
  FROM `lithe-record-440915-m9.tav2_bq.ticker` t
  JOIN u ON u.time = t.time AND u.ticker = t.ticker
  WHERE t.time >= '2006-01-01' AND t.Close IS NOT NULL AND t.Close > 0
),
r AS (
  SELECT time, ticker,
         SAFE_DIVIDE(Close, LAG(Close) OVER (PARTITION BY ticker ORDER BY time)) - 1 AS ret,
         DATE_DIFF(time, LAG(time) OVER (PARTITION BY ticker ORDER BY time), DAY) AS gap
  FROM px
),
rr AS (
  SELECT time, ticker, ret,
         LAG(ret) OVER (PARTITION BY ticker ORDER BY time) AS ret_lag,
         LAG(gap) OVER (PARTITION BY ticker ORDER BY time) AS gap_lag,
         gap
  FROM r
  WHERE ret IS NOT NULL AND gap <= 7
)
SELECT DATE_TRUNC(time, MONTH) AS ym, ticker,
       COUNT(*) AS n,
       SUM(ret) AS sx, SUM(ret_lag) AS sy,
       SUM(ret*ret_lag) AS sxy,
       SUM(ret*ret) AS sxx, SUM(ret_lag*ret_lag) AS syy
FROM rr
WHERE ret_lag IS NOT NULL AND gap_lag <= 7
  AND ABS(ret) < 0.5 AND ABS(ret_lag) < 0.5
GROUP BY ym, ticker
ORDER BY ym, ticker
