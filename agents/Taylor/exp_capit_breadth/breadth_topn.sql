WITH base AS (
  SELECT t.time, t.ticker, t.D_RSI,
         t.Volume_3M_P50 * COALESCE(t.Price, t.Close) AS liq
  FROM tav2_bq.ticker t
  JOIN `lithe-record-440915-m9.tav2_mike.universe_pit_q` u
    ON u.ticker = t.ticker AND u.time = t.time AND u.in_universe
  WHERE t.time >= DATE '2014-01-01' AND t.Close_T1 > 0
),
r AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY time ORDER BY liq DESC, ticker) rn
  FROM base
)
SELECT time,
  AVG(CASE WHEN rn<=100 THEN IF(D_RSI<0.3,1.0,0) END) br100,
  AVG(CASE WHEN rn<=150 THEN IF(D_RSI<0.3,1.0,0) END) br150,
  AVG(CASE WHEN rn<=200 THEN IF(D_RSI<0.3,1.0,0) END) br200,
  AVG(CASE WHEN rn<=250 THEN IF(D_RSI<0.3,1.0,0) END) br250,
  AVG(CASE WHEN rn<=300 THEN IF(D_RSI<0.3,1.0,0) END) br300,
  COUNT(*) n_universe
FROM r GROUP BY time ORDER BY time
