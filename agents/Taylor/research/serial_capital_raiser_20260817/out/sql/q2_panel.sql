
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
me AS (  -- last session of each calendar month, per ticker
  SELECT ticker, time, Close, Price, Volume,
         DATE_TRUNC(time, MONTH) AS mth,
         ROW_NUMBER() OVER (PARTITION BY ticker, DATE_TRUNC(time, MONTH) ORDER BY time DESC) AS rn_m
  FROM px
),
mend AS (
  SELECT ticker, mth, time AS d_t, Close,
         LEAD(Close) OVER (PARTITION BY ticker ORDER BY mth) AS close_next,
         LEAD(mth)   OVER (PARTITION BY ticker ORDER BY mth) AS mth_next
  FROM me WHERE rn_m = 1
),
rets AS (
  SELECT ticker, mth, d_t, Close,
         -- only a CONSECUTIVE month counts as a 1-month forward return; a gap yields NULL
         IF(mth_next = DATE_ADD(mth, INTERVAL 1 MONTH),
            SAFE_DIVIDE(close_next, Close) - 1, NULL) AS fwd_ret_1m,
         IF(mth_next = DATE_ADD(mth, INTERVAL 1 MONTH), 0, 1) AS fwd_gap
  FROM mend
),
snap AS (  -- valuation + controls read AS STORED on the same session (PIT)
  -- DEVIATION D1: PREREG named ROE_Trailing and Revenue_YoY_P0; neither column exists in
  -- `tav2_bq.ticker` (they live in `ticker_financial`). Substituted the nearest available
  -- same-table columns rather than adding a second join whose PIT semantics I have not audited:
  -- ROIC_Trailing (trailing 4Q), NPM_P0, FSCORE (Piotroski, absorbs part of the growth/quality
  -- axis). Recorded in DEVIATIONS.md.
  SELECT t.ticker, t.time AS d_t, t.PE, t.PB, t.ICB_Code, t.ROIC_Trailing, t.NPM_P0,
         t.FSCORE, t.Debt_Eq_P0
  FROM `lithe-record-440915-m9.tav2_bq.ticker` t
  WHERE t.time >= DATE '2010-01-01' AND t.time <= DATE '2026-05-31'
),
advs AS (
  SELECT ticker, time AS d_t,
         AVG(Price * Volume) OVER (PARTITION BY ticker ORDER BY si
                                   ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) AS adv60
  FROM px
),
base AS (
  SELECT r.ticker, r.mth, r.d_t, r.Close, r.fwd_ret_1m, r.fwd_gap,
         s.PE, s.PB, s.ICB_Code, s.ROIC_Trailing, s.NPM_P0, s.FSCORE, s.Debt_Eq_P0, a.adv60
  FROM rets r
  JOIN `lithe-record-440915-m9.tav2_mike.universe_pit` u
    ON u.ticker = r.ticker AND u.time = r.d_t AND u.in_universe
  JOIN snap s ON s.ticker = r.ticker AND s.d_t = r.d_t
  LEFT JOIN advs a ON a.ticker = r.ticker AND a.d_t = r.d_t
  WHERE r.mth BETWEEN DATE '2010-01-01' AND DATE '2026-05-31'
),
-- raiser state: PIT by construction, only ex-dates at or before d_t enter the count
cnt AS (
  SELECT b.ticker, b.mth,
    COUNTIF(e.subtype IN ('RIGHTS','PRIVATE_PLACEMENT','AUCTION')) AS n_raise_3y,
    COUNTIF(e.subtype IN ('RIGHTS','PRIVATE_PLACEMENT','AUCTION','ESOP','CONVERTIBLE'))  AS n_wide_3y,
    COUNT(e.ticker)                        AS n_all_3y
  FROM base b LEFT JOIN ev_all e
    ON e.ticker = b.ticker
   AND e.exright_date >  DATE_SUB(b.d_t, INTERVAL 1095 DAY)
   AND e.exright_date <= b.d_t
  GROUP BY b.ticker, b.mth
),
-- FUTURE-window probe (falsification #3): events strictly AFTER d_t. Never used as a regressor
-- in the primary; it exists to show whether the "discount" is information or firm character.
fut AS (
  SELECT b.ticker, b.mth, COUNTIF(e.subtype IN ('RIGHTS','PRIVATE_PLACEMENT','AUCTION')) AS n_raise_fwd180
  FROM base b LEFT JOIN ev_all e
    ON e.ticker = b.ticker
   AND e.exright_date >  b.d_t
   AND e.exright_date <= DATE_ADD(b.d_t, INTERVAL 180 DAY)
  GROUP BY b.ticker, b.mth
)
SELECT b.ticker, b.mth, b.d_t, b.Close, b.fwd_ret_1m, b.fwd_gap,
       b.PE, b.PB, b.ICB_Code AS icb, b.ROIC_Trailing, b.NPM_P0, b.FSCORE, b.Debt_Eq_P0, b.adv60,
       c.n_raise_3y, c.n_wide_3y, c.n_all_3y, f.n_raise_fwd180
FROM base b
JOIN cnt c ON c.ticker = b.ticker AND c.mth = b.mth
JOIN fut f ON f.ticker = b.ticker AND f.mth = b.mth
ORDER BY b.mth, b.ticker
