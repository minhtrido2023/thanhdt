
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
vni AS (
  SELECT time,
         SAFE_DIVIDE(Close, LAG(Close) OVER (ORDER BY time)) - 1 AS vret
  FROM `lithe-record-440915-m9.tav2_bq.ticker`
  WHERE ticker = 'VNINDEX' AND Close > 0
),
ev AS (
  SELECT ticker, exright_date AS t0, subtype
  FROM ev_all
  WHERE exright_date BETWEEN DATE '2010-01-01' AND DATE '2026-06-15'
  GROUP BY ticker, t0, subtype
),
gated AS (
  SELECT e.* FROM ev e
  JOIN `lithe-record-440915-m9.tav2_mike.universe_pit` u
    ON u.ticker = e.ticker AND u.time = e.t0 AND u.in_universe
),
-- DISTINCT on (ticker, t0), NOT on (ticker, t0, subtype): the prior program's Q1_SQL ends in
-- `GROUP BY ticker, t0` with ANY_VALUE(subtype), so a ticker with two different ISS subtypes on
-- one ex-date is ONE row there (3,246 -> 2,953). Keying on subtype here would fan the joins out
-- and break CC5. Every field below depends only on (ticker, date), so the collapse loses nothing;
-- `subtype` itself is taken from q1_bhar.csv at merge time, never from this pull.
anchored AS (
  SELECT DISTINCT g.ticker, g.t0, p.si AS si0
  FROM gated g JOIN px p ON p.ticker = g.ticker AND p.time = g.t0
),
-- pre-event window only: [-250, -1]. Nothing at or after the ex-date is read here, by construction.
w AS (
  SELECT a.ticker, a.t0, p.si - a.si0 AS k, p.time AS dt, p.ret
  FROM anchored a JOIN px p
    ON p.ticker = a.ticker AND p.si BETWEEN a.si0 - 250 AND a.si0 - 1
),
beta AS (
  SELECT w.ticker, w.t0,
         COUNT(*) AS beta_n,
         SAFE_DIVIDE(COVAR_POP(w.ret, v.vret), NULLIF(VAR_POP(v.vret), 0)) AS beta_pop,
         CORR(w.ret, v.vret) AS beta_corr
  FROM w JOIN vni v ON v.time = w.dt
  WHERE w.ret IS NOT NULL AND v.vret IS NOT NULL
  GROUP BY 1, 2
),
d_m1 AS (SELECT ticker, t0, MAX(IF(k = -1, dt, NULL)) AS dt_m1 FROM w GROUP BY 1, 2),
fund AS (
  SELECT d.ticker, d.t0, d.dt_m1,
         t.ROIC_Trailing AS roic_trailing, t.FSCORE AS fscore, t.NPM_P0 AS npm_p0,
         t.Debt_Eq_P0 AS debt_eq, t.PE AS pe, t.PB AS pb, t.ICB_Code AS icb_m1
  FROM d_m1 d JOIN `lithe-record-440915-m9.tav2_bq.ticker` t
    ON t.ticker = d.ticker AND t.time = d.dt_m1
),
-- risk_rating: DISTINCT is defensive (CLAUDE.md trap #3), and the quarter must be STRICTLY before
-- the calendar quarter containing t0 so no rating computed during the event quarter leaks in.
rr AS (
  SELECT DISTINCT ticker, quarter, Beta AS rr_beta_bin, Dev AS rr_dev_bin,
         Risk_Rating AS rr_rating
  FROM `lithe-record-440915-m9.tav2_bq.risk_rating`
  WHERE Beta IS NOT NULL
),
rr_pick AS (
  SELECT ticker, t0, rr_beta_bin, rr_dev_bin, rr_rating, rr_quarter, t0_quarter
  FROM (
    SELECT a.ticker, a.t0, r.rr_beta_bin, r.rr_dev_bin, r.rr_rating,
           r.quarter AS rr_quarter,
           FORMAT('%dQ%d', EXTRACT(YEAR FROM a.t0), EXTRACT(QUARTER FROM a.t0)) AS t0_quarter,
           ROW_NUMBER() OVER (PARTITION BY a.ticker, a.t0 ORDER BY r.quarter DESC) AS rn
    FROM anchored a JOIN rr r ON r.ticker = a.ticker
     AND r.quarter < FORMAT('%dQ%d', EXTRACT(YEAR FROM a.t0), EXTRACT(QUARTER FROM a.t0))
  )
  WHERE rn = 1
)
SELECT a.ticker, a.t0,
       f.dt_m1, f.roic_trailing, f.fscore, f.npm_p0, f.debt_eq, f.pe, f.pb, f.icb_m1,
       b.beta_n, IF(b.beta_n >= 150, b.beta_pop, NULL) AS beta_raw, b.beta_corr,
       p.rr_beta_bin, p.rr_dev_bin, p.rr_rating, p.rr_quarter, p.t0_quarter
FROM anchored a
LEFT JOIN fund f ON f.ticker = a.ticker AND f.t0 = a.t0
LEFT JOIN beta b ON b.ticker = a.ticker AND b.t0 = a.t0
LEFT JOIN rr_pick p ON p.ticker = a.ticker AND p.t0 = a.t0
ORDER BY a.ticker, a.t0
