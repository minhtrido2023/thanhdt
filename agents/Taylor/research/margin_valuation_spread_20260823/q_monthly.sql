WITH mdays AS (
  SELECT DATE_TRUNC(time, MONTH) AS m, MAX(time) AS d
  FROM `tav2_bq.ticker`
  WHERE ticker = 'VNINDEX' AND time >= '2006-01-01'
  GROUP BY m
),
uni AS (
  SELECT u.time, u.ticker
  FROM `tav2_mike.universe_pit` u
  JOIN mdays ON u.time = mdays.d
  WHERE u.in_universe
),
px AS (
  SELECT t.time, t.ticker, t.Price, t.PE, t.DY
  FROM `tav2_bq.ticker` t
  JOIN uni USING (ticker, time)
),
fin AS (
  SELECT ticker, Release_Date, OShares
  FROM `tav2_bq.ticker_financial`
  WHERE OShares IS NOT NULL AND OShares > 0 AND Release_Date IS NOT NULL
),
j AS (
  SELECT p.time, p.ticker, p.Price, p.PE, p.DY, f.OShares,
         ROW_NUMBER() OVER (PARTITION BY p.ticker, p.time ORDER BY f.Release_Date DESC) AS rn
  FROM px p
  JOIN fin f ON f.ticker = p.ticker AND f.Release_Date <= p.time
),
panel AS (
  SELECT time, ticker, Price, PE, DY, Price * OShares AS mcap
  FROM j WHERE rn = 1 AND Price IS NOT NULL AND Price > 0
),
agg AS (
  SELECT
    time,
    COUNT(*) AS n_uni,
    COUNTIF(PE > 0) AS n_pe,
    COUNTIF(DY IS NULL) AS n_dy_null,
    COUNTIF(DY > 0) AS n_dy_pos,
    APPROX_QUANTILES(IF(PE > 0, 1.0/PE, NULL), 100)[OFFSET(50)] AS ey_med,
    APPROX_QUANTILES(IF(PE > 0, 1.0/PE, NULL), 100)[OFFSET(75)] AS ey_p75,
    SUM(IF(PE > 0, mcap/PE, 0)) / NULLIF(SUM(IF(PE > 0, mcap, 0)), 0) AS ey_agg,
    APPROX_QUANTILES(COALESCE(DY, 0), 100)[OFFSET(50)] AS dy_med_all,
    APPROX_QUANTILES(COALESCE(DY, 0), 100)[OFFSET(75)] AS dy_p75_all,
    APPROX_QUANTILES(IF(DY > 0, DY, NULL), 100)[OFFSET(50)] AS dy_med_payers,
    AVG(COALESCE(DY, 0)) AS dy_ew,
    SUM(COALESCE(DY, 0) * mcap) / NULLIF(SUM(mcap), 0) AS dy_agg,
    COUNTIF(COALESCE(DY, 0) >= 0.07) AS n_dy_ge7,
    COUNTIF(COALESCE(DY, 0) >= 0.10) AS n_dy_ge10,
    MAX(mcap) / NULLIF(SUM(mcap), 0) AS top1_w,
    SUM(mcap) / 1e12 AS mcap_tn_vnd
  FROM panel GROUP BY time
)
SELECT a.time, v.Close AS vnindex, a.n_uni, a.n_pe, a.n_dy_null, a.n_dy_pos,
       ROUND(a.ey_med,6) ey_med, ROUND(a.ey_p75,6) ey_p75, ROUND(a.ey_agg,6) ey_agg,
       ROUND(a.dy_med_all,6) dy_med_all, ROUND(a.dy_p75_all,6) dy_p75_all,
       ROUND(a.dy_med_payers,6) dy_med_payers, ROUND(a.dy_ew,6) dy_ew, ROUND(a.dy_agg,6) dy_agg,
       a.n_dy_ge7, a.n_dy_ge10, ROUND(a.top1_w,4) top1_w, ROUND(a.mcap_tn_vnd,1) mcap_tn_vnd
FROM agg a
JOIN `tav2_bq.ticker` v ON v.ticker = 'VNINDEX' AND v.time = a.time
ORDER BY a.time
