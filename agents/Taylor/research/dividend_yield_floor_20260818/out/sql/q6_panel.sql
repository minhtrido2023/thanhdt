
WITH dd AS (
  SELECT c.ticker, c.exright_date AS ex, c.value_per_share,
         ROW_NUMBER() OVER (
           PARTITION BY c.ticker, c.exright_date, c.dividend_year, c.dividend_stage_vi
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action` AS c
  WHERE c.event_code = 'DIV'
    AND c.event_status = 'executed'
    AND c.exright_date IS NOT NULL
    AND c.value_per_share > 0
),
ev AS (
  SELECT ticker, ex, SUM(value_per_share) AS dv
  FROM dd WHERE rn = 1 AND ex >= DATE '2010-01-01'
  GROUP BY ticker, ex
),
steps_raw AS (
  SELECT ticker, DATE_ADD(ex, INTERVAL 365 * b DAY) AS d, b AS bk, dv, 1 AS ct
  FROM ev, UNNEST([0,1,2,3,4]) AS b
  UNION ALL
  SELECT ticker, DATE_ADD(ex, INTERVAL 365 * (b + 1) DAY) AS d, b AS bk, -dv, -1 AS ct
  FROM ev, UNNEST([0,1,2,3,4]) AS b
),
steps AS (
  SELECT ticker, d,
         SUM(IF(bk=0, dv, 0)) AS s_dv0, SUM(IF(bk=0, ct, 0)) AS s_ct0,
         SUM(IF(bk=1, ct, 0)) AS s_ct1, SUM(IF(bk=2, ct, 0)) AS s_ct2,
         SUM(IF(bk=3, ct, 0)) AS s_ct3, SUM(IF(bk=4, ct, 0)) AS s_ct4
  FROM steps_raw GROUP BY ticker, d
),
-- every exright_date of ANY corp-action for the ticker: PREREG §4.2 disqualifies those rows
-- because `ticker.Price` can sit at the T-1 reference frame exactly there (registry TRAP).
exd AS (
  SELECT DISTINCT ticker, exright_date AS d
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
  WHERE exright_date IS NOT NULL
),
px AS (
  SELECT t.ticker, t.time, t.Close, t.Price, t.Low, t.High, t.Volume, t.PE, t.PB, t.DY,
         t.ICB_Code,
         SAFE_DIVIDE(t.Close, LAG(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret
  FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
  WHERE t.time >= DATE '2012-06-01' AND t.time <= DATE '2026-06-15'
    AND t.Close IS NOT NULL AND t.Close > 0 AND t.ticker != 'VNINDEX'
),
pxw AS (
  SELECT ticker, time, Close, Price, Low, High, Volume, PE, PB, DY, ICB_Code, ret,
         ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time) AS si,
         STDDEV(ret) OVER (PARTITION BY ticker ORDER BY time
                           ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) AS rvol60,
         AVG(Volume * Price) OVER (PARTITION BY ticker ORDER BY time
                           ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) AS advnd60,
         LEAD(Close,  20) OVER (PARTITION BY ticker ORDER BY time) AS c_p20,
         LEAD(time,   20) OVER (PARTITION BY ticker ORDER BY time) AS d_p20,
         LEAD(Close,  60) OVER (PARTITION BY ticker ORDER BY time) AS c_p60,
         LEAD(time,   60) OVER (PARTITION BY ticker ORDER BY time) AS d_p60,
         LEAD(Close, 120) OVER (PARTITION BY ticker ORDER BY time) AS c_p120,
         LEAD(time,  120) OVER (PARTITION BY ticker ORDER BY time) AS d_p120,
         MIN(Close) OVER (PARTITION BY ticker ORDER BY time
                          ROWS BETWEEN 1 FOLLOWING AND 60 FOLLOWING) AS minc60,
         MAX(Close) OVER (PARTITION BY ticker ORDER BY time
                          ROWS BETWEEN 1 FOLLOWING AND 60 FOLLOWING) AS maxc60,
         COUNT(Close) OVER (PARTITION BY ticker ORDER BY time
                            ROWS BETWEEN 1 FOLLOWING AND 60 FOLLOWING) AS n_fwd60
  FROM px
),
tl AS (
  SELECT ticker, time AS d, 1 AS is_px,
         0.0 AS s_dv0, 0 AS s_ct0, 0 AS s_ct1, 0 AS s_ct2, 0 AS s_ct3, 0 AS s_ct4,
         si, Close, Price, Low, High, Volume, PE, PB, DY, ICB_Code, ret, rvol60, advnd60,
         c_p20, d_p20, c_p60, d_p60, c_p120, d_p120, minc60, maxc60, n_fwd60
  FROM pxw
  UNION ALL
  SELECT ticker, d, 0 AS is_px,
         s_dv0, s_ct0, s_ct1, s_ct2, s_ct3, s_ct4,
         NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
         NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
  FROM steps
),
cum AS (
  SELECT ticker, d, is_px, si, Close, Price, Low, High, Volume, PE, PB, DY, ICB_Code, ret,
         rvol60, advnd60, c_p20, d_p20, c_p60, d_p60, c_p120, d_p120, minc60, maxc60, n_fwd60,
         SUM(s_dv0) OVER w AS div0,
         SUM(s_ct0) OVER w AS n0, SUM(s_ct1) OVER w AS n1, SUM(s_ct2) OVER w AS n2,
         SUM(s_ct3) OVER w AS n3, SUM(s_ct4) OVER w AS n4
  FROM tl
  WINDOW w AS (PARTITION BY ticker ORDER BY d, is_px ROWS UNBOUNDED PRECEDING)
)
SELECT c.ticker, c.d AS dt, c.si, c.Close AS close, c.Price AS price, c.Low AS low,
       c.High AS high, c.Volume AS volume, c.PE AS pe, c.PB AS pb, c.DY AS dy,
       c.ICB_Code AS icb, c.ret, c.rvol60, c.advnd60,
       c.c_p20, c.d_p20, c.c_p60, c.d_p60, c.c_p120, c.d_p120,
       c.minc60, c.maxc60, c.n_fwd60,
       ROUND(c.div0, 6) AS div0, c.n0, c.n1, c.n2, c.n3, c.n4,
       IF(x.d IS NULL, 0, 1) AS is_exdate
FROM cum AS c
JOIN `lithe-record-440915-m9.tav2_mike.universe_pit` AS u
  ON u.ticker = c.ticker AND u.time = c.d AND u.in_universe
LEFT JOIN exd AS x ON x.ticker = c.ticker AND x.d = c.d
WHERE c.is_px = 1
  AND c.d BETWEEN DATE '2014-01-01' AND DATE '2026-06-15'
  AND c.Price IS NOT NULL AND c.Price > 0
  -- PREREG §2: keep only STABLE-3 rows and clean NON-PAYER rows; the grey zone is dropped
  -- rather than assigned to whichever group would be convenient.
  AND ((c.n0 >= 1 AND c.n1 >= 1 AND c.n2 >= 1) OR (c.n0 = 0 AND c.n1 = 0 AND c.n2 = 0))
ORDER BY c.ticker, c.d
