WITH panel AS (
  SELECT t.ticker, t.time, t.Close,
         CAST(FLOOR(t.ICB_Code/1000)*1000 AS INT64) AS sector
  FROM tav2_bq.ticker AS t
  JOIN tav2_mike.universe_pit AS u ON t.ticker=u.ticker AND t.time=u.time AND u.in_universe
  WHERE t.time >= '2007-01-01' AND t.ICB_Code IS NOT NULL
),
ret21 AS (
  SELECT ticker, time, sector,
    LN(Close) - LN(LAG(Close, 21) OVER (PARTITION BY ticker ORDER BY time)) AS logret21
  FROM panel
),
sector_day AS (
  SELECT time, sector, COUNT(*) AS n, APPROX_QUANTILES(logret21,2)[OFFSET(1)] AS sector_median_ret21
  FROM ret21 WHERE logret21 IS NOT NULL
  GROUP BY time, sector
  HAVING n>=5
),
disp AS (
  SELECT time,
    MAX(sector_median_ret21) AS top_sector_ret21,
    APPROX_QUANTILES(sector_median_ret21,2)[OFFSET(1)] AS median_sector_ret21,
    COUNT(*) AS n_sectors
  FROM sector_day
  GROUP BY time
  HAVING n_sectors >= 5
)
SELECT time, top_sector_ret21, median_sector_ret21,
       top_sector_ret21 - median_sector_ret21 AS conc_spread, n_sectors
FROM disp ORDER BY time
