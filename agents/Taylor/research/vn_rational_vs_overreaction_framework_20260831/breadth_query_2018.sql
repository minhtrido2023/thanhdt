SELECT
  t.time AS dt,
  COUNT(*) AS n_universe,
  COUNTIF(t.D_RSI < 0.30) AS n_oversold,
  SAFE_DIVIDE(COUNTIF(t.D_RSI < 0.30), COUNT(*)) * 100 AS pct_oversold
FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
JOIN `lithe-record-440915-m9.tav2_mike.universe_pit` AS u
  ON t.ticker = u.ticker AND t.time = u.time AND u.in_universe = TRUE
WHERE t.time BETWEEN '2018-02-01' AND '2018-12-31'
  AND t.D_RSI IS NOT NULL
GROUP BY dt
ORDER BY dt
