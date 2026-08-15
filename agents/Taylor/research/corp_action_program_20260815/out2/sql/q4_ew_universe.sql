
WITH u AS (
  SELECT up.time, up.ticker
  FROM `lithe-record-440915-m9.tav2_mike.universe_pit` AS up
  WHERE up.in_universe AND up.time >= DATE '2013-01-01'
),
p AS (
  SELECT t.ticker, t.time, t.Close,
         LAG(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c_prev,
         LAG(t.time)  OVER (PARTITION BY t.ticker ORDER BY t.time) AS t_prev
  FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
  WHERE t.time >= DATE '2013-01-01' AND t.Close IS NOT NULL AND t.Close > 0
),
r AS (
  SELECT p.time AS dt, p.ticker, p.Close / p.c_prev - 1 AS ret
  FROM p
  JOIN u        ON u.ticker = p.ticker AND u.time = p.time
  JOIN u AS upv ON upv.ticker = p.ticker AND upv.time = p.t_prev
  WHERE p.c_prev IS NOT NULL AND p.c_prev > 0
)
SELECT dt,
       AVG(ret) AS ew_ret_raw,
       AVG(IF(ABS(ret) <= 0.5, ret, NULL)) AS ew_ret,
       COUNT(*) AS n_names,
       COUNTIF(ABS(ret) > 0.5) AS n_impossible
FROM r GROUP BY dt ORDER BY dt
