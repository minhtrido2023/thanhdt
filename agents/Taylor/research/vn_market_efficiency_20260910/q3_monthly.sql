WITH u AS (
  SELECT time, ticker FROM `lithe-record-440915-m9.tav2_mike.universe_pit`
  WHERE in_universe = TRUE AND time >= '2006-01-01'
),
px AS (
  SELECT t.time, t.ticker, t.Close, t.Volume, t.Price
  FROM `lithe-record-440915-m9.tav2_bq.ticker` t
  JOIN u ON u.time = t.time AND u.ticker = t.ticker
  WHERE t.time >= '2006-01-01' AND t.Close > 0
),
m AS (
  SELECT DATE_TRUNC(time, MONTH) AS ym, ticker, time, Close,
         ROW_NUMBER() OVER (PARTITION BY ticker, DATE_TRUNC(time, MONTH) ORDER BY time DESC) AS rn,
         AVG(COALESCE(Price, Close) * Volume) OVER (
             PARTITION BY ticker, DATE_TRUNC(time, MONTH)) AS adv_vnd,
         COUNT(*) OVER (PARTITION BY ticker, DATE_TRUNC(time, MONTH)) AS ndays
  FROM px
)
SELECT ym, ticker, time AS asof, Close AS close_me, adv_vnd, ndays
FROM m WHERE rn = 1
ORDER BY ym, ticker
