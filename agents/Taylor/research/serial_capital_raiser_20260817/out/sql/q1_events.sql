
WITH 
raw AS (
  SELECT c.ticker, c.exright_date, c.id, c.public_date, c.exercise_ratio, c.issue_volumn,
         c.total_value, CASE c.issue_method_code
  WHEN 'DIV' THEN 'STOCK_DIVIDEND' WHEN 'Bonus' THEN 'BONUS' WHEN 'Rights' THEN 'RIGHTS'
  WHEN 'EMPL' THEN 'ESOP' WHEN 'PP' THEN 'PRIVATE_PLACEMENT' WHEN 'TRANS' THEN 'CONVERTIBLE'
  WHEN 'ICRE' THEN 'CONVERTIBLE' WHEN 'PUBL' THEN 'AUCTION' WHEN 'MERGER' THEN 'MERGER'
  ELSE 'UNKNOWN' END AS subtype,
         ROW_NUMBER() OVER (PARTITION BY c.ticker, c.exright_date, c.issue_method_code,
             CAST(c.exercise_ratio AS STRING), CAST(c.issue_volumn AS STRING),
             CAST(c.total_value AS STRING)
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action` c
  WHERE c.event_code = 'ISS' AND c.event_status = 'executed' AND c.exright_date IS NOT NULL
),
ev_all AS (SELECT * FROM raw WHERE rn = 1 AND subtype <> 'UNKNOWN')
,

px AS (
  SELECT t.ticker, t.time, t.Close, t.Price, t.Volume, t.ICB_Code,
         SAFE_DIVIDE(t.Close, LAG(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret,
         ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time) AS si
  FROM `lithe-record-440915-m9.tav2_bq.ticker` t
  WHERE t.time >= DATE '2007-01-01' AND t.Close > 0 AND t.ticker <> 'VNINDEX'
)
,
ev AS (
  SELECT ticker, exright_date AS t0, subtype,
         COUNT(*) AS n_components,
         SUM(SAFE_CAST(exercise_ratio AS FLOAT64)) AS ratio_total,
         SUM(SAFE_CAST(issue_volumn AS FLOAT64)) AS issue_volume,
         SUM(SAFE_CAST(total_value AS FLOAT64)) AS total_value
  FROM ev_all
  WHERE exright_date BETWEEN DATE '2010-01-01' AND DATE '2026-06-15'
  GROUP BY ticker, t0, subtype
),
-- PIT universe gate: in_universe must be TRUE on the anchor date itself.
gated AS (
  SELECT e.* FROM ev e
  JOIN `lithe-record-440915-m9.tav2_mike.universe_pit` u
    ON u.ticker = e.ticker AND u.time = e.t0 AND u.in_universe
),
anchored AS (
  SELECT g.*, p.si AS si0 FROM gated g JOIN px p ON p.ticker = g.ticker AND p.time = g.t0
),
w AS (
  SELECT a.*, p.si - a.si0 AS k, p.time AS dt, p.Close, p.Price, p.Volume, p.ICB_Code, p.ret
  FROM anchored a JOIN px p
    ON p.ticker = a.ticker AND p.si BETWEEN a.si0 - 500 AND a.si0 + 750
)
SELECT ticker, t0, ANY_VALUE(subtype) AS subtype,
       ANY_VALUE(n_components) AS n_components, ANY_VALUE(ratio_total) AS ratio_total,
       ANY_VALUE(issue_volume) AS issue_volume, ANY_VALUE(total_value) AS total_value,
       MAX(IF(k = -500, Close, NULL)) AS c_m500, MAX(IF(k = -500, dt, NULL)) AS d_m500,
       MAX(IF(k = -250, Close, NULL)) AS c_m250, MAX(IF(k = -250, dt, NULL)) AS d_m250,
       MAX(IF(k =    0, Close, NULL)) AS c_0,    MAX(IF(k =    0, dt, NULL)) AS d_0,
       MAX(IF(k =  250, Close, NULL)) AS c_250,  MAX(IF(k =  250, dt, NULL)) AS d_250,
       MAX(IF(k =  500, Close, NULL)) AS c_500,  MAX(IF(k =  500, dt, NULL)) AS d_500,
       MAX(IF(k =  750, Close, NULL)) AS c_750,  MAX(IF(k =  750, dt, NULL)) AS d_750,
       MAX(IF(k =   -1, ICB_Code, NULL)) AS icb,
       AVG(IF(k BETWEEN -60 AND -6, Price * Volume, NULL)) AS adv60,
       STDDEV(IF(k BETWEEN -60 AND -1, ret, NULL)) AS rvol60,
       EXP(SUM(IF(k BETWEEN -126 AND -21, LN(1 + ret), 0))) - 1 AS mom6m,
       COUNTIF(k >= 0) AS n_sessions_fwd
FROM w
GROUP BY ticker, t0
ORDER BY ticker, t0
