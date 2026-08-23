-- Daily point-in-time breadth + valuation on universe_pit (CANONICAL PIT universe).
-- No look-ahead: every column at date d uses only data <= d.
WITH uni AS (
  SELECT time, ticker FROM `tav2_mike.universe_pit`
  WHERE in_universe AND time >= '2007-01-01'
),
names AS (SELECT DISTINCT ticker FROM uni),
px AS (
  SELECT t.time, t.ticker, t.Close, t.MA200, t.Low, t.High, t.PE, t.PB, t.Volume, t.Price
  FROM `tav2_bq.ticker` t JOIN names n USING (ticker)
  WHERE t.time >= '2005-06-01' AND t.Close > 0
),
roll AS (
  SELECT time, ticker, Close, MA200, PE, PB, Volume, Price,
         MIN(Low)  OVER w52 AS lo52,
         MAX(High) OVER w52 AS hi52,
         COUNT(*)  OVER w52 AS nbars52,
         AVG(Price*Volume) OVER w20 AS tv20
  FROM px
  WINDOW w52 AS (PARTITION BY ticker ORDER BY UNIX_DATE(time) RANGE BETWEEN 364 PRECEDING AND CURRENT ROW),
         w20 AS (PARTITION BY ticker ORDER BY UNIX_DATE(time) RANGE BETWEEN 29 PRECEDING AND CURRENT ROW)
)
SELECT
  r.time,
  COUNT(*) AS n,
  COUNTIF(r.MA200 IS NOT NULL AND r.Close > r.MA200) AS n_above_ma200,
  COUNTIF(r.MA200 IS NOT NULL) AS n_has_ma200,
  COUNTIF(r.nbars52 >= 120 AND r.Close <= r.lo52*1.02) AS n_at_52wlow,
  COUNTIF(r.nbars52 >= 120) AS n_has_52w,
  COUNTIF(r.nbars52 >= 120 AND SAFE_DIVIDE(r.Close, r.hi52) - 1 <= -0.50) AS n_dd52_lt50,
  COUNTIF(r.nbars52 >= 120 AND SAFE_DIVIDE(r.Close, r.hi52) - 1 <= -0.35) AS n_dd52_lt35,
  COUNTIF(r.PE > 0) AS n_pe_pos,
  APPROX_QUANTILES(IF(r.PE>0, 1/r.PE, NULL), 100)[OFFSET(50)] AS ey_med,
  APPROX_QUANTILES(IF(r.PE>0, r.PE, NULL), 100)[OFFSET(50)] AS pe_med,
  APPROX_QUANTILES(IF(r.PB>0, r.PB, NULL), 100)[OFFSET(50)] AS pb_med,
  SUM(r.Price*r.Volume)/1e9 AS tv_bn_vnd,
  SUM(r.tv20)/1e9 AS tv20_bn_vnd
FROM roll r JOIN uni u ON u.time = r.time AND u.ticker = r.ticker
GROUP BY r.time ORDER BY r.time
