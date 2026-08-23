WITH mdays AS (
  SELECT DATE_TRUNC(time, MONTH) AS m, MAX(time) AS d
  FROM `tav2_bq.ticker` WHERE ticker='VNINDEX' AND time >= '2008-01-01' GROUP BY m
),
uni AS (SELECT u.time, u.ticker FROM `tav2_mike.universe_pit` u JOIN mdays ON u.time = mdays.d WHERE u.in_universe),
px AS (SELECT t.time, t.ticker, COALESCE(t.DY,0) AS DY, t.PE FROM `tav2_bq.ticker` t JOIN uni USING (ticker, time))
SELECT time, COUNT(*) n,
  COUNTIF(DY>=0.04) n_dy04, COUNTIF(DY>=0.05) n_dy05, COUNTIF(DY>=0.06) n_dy06,
  COUNTIF(DY>=0.07) n_dy07, COUNTIF(DY>=0.08) n_dy08, COUNTIF(DY>=0.10) n_dy10,
  COUNTIF(DY>=0.12) n_dy12, COUNTIF(DY>=0.15) n_dy15,
  COUNTIF(PE>0 AND 1/PE>=0.10) n_ey10, COUNTIF(PE>0 AND 1/PE>=0.125) n_ey125,
  COUNTIF(PE>0 AND 1/PE>=0.15) n_ey15, COUNTIF(PE>0 AND 1/PE>=0.20) n_ey20
FROM px GROUP BY time ORDER BY time
