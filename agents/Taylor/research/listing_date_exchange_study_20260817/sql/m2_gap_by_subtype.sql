
WITH 
raw AS (
  SELECT c.ticker, c.exright_date, c.listing_date, c.public_date, c.record_date, c.id,
         c.exercise_ratio, c.event_title_vi, CASE c.issue_method_code
  WHEN 'DIV' THEN 'STOCK_DIVIDEND' WHEN 'Bonus' THEN 'BONUS' WHEN 'Rights' THEN 'RIGHTS'
  WHEN 'EMPL' THEN 'ESOP' WHEN 'PP' THEN 'PRIVATE_PLACEMENT' WHEN 'TRANS' THEN 'CONVERTIBLE'
  WHEN 'ICRE' THEN 'CONVERTIBLE' WHEN 'PUBL' THEN 'AUCTION' WHEN 'MERGER' THEN 'MERGER'
  ELSE 'UNKNOWN' END AS subtype,
         ROW_NUMBER() OVER (PARTITION BY c.ticker, c.exright_date, c.issue_method_code,
             CAST(c.exercise_ratio AS STRING), CAST(c.issue_volumn AS STRING),
             CAST(c.total_value AS STRING)
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action` c
  WHERE c.event_code = 'ISS' AND c.event_status = 'executed'
),
ev AS (SELECT * FROM raw WHERE rn = 1 AND subtype <> 'UNKNOWN')
,
g AS (
  SELECT subtype, ticker, exright_date, listing_date,
         DATE_DIFF(exright_date, listing_date, DAY) AS gap
  FROM ev
)
SELECT subtype,
  COUNT(*) AS n_events,
  COUNT(DISTINCT ticker) AS n_issuers,
  COUNTIF(listing_date IS NULL) AS n_null_listing,
  COUNTIF(exright_date IS NULL) AS n_null_exright,
  COUNTIF(gap IS NOT NULL) AS n_both,
  COUNTIF(gap > 0) AS n_listing_before_ex,
  COUNTIF(gap = 0) AS n_listing_eq_ex,
  COUNTIF(gap < 0) AS n_listing_after_ex,
  COUNTIF(gap BETWEEN 3 AND 30) AS n_gap_in_3_30,
  ROUND(100 * COUNTIF(gap BETWEEN 3 AND 30) / NULLIF(COUNTIF(gap IS NOT NULL), 0), 1)
    AS pct_gap_in_3_30,
  APPROX_QUANTILES(gap, 100)[OFFSET(5)]  AS p05_gap,
  APPROX_QUANTILES(gap, 100)[OFFSET(25)] AS p25_gap,
  APPROX_QUANTILES(gap, 100)[OFFSET(50)] AS median_gap,
  APPROX_QUANTILES(gap, 100)[OFFSET(75)] AS p75_gap,
  APPROX_QUANTILES(gap, 100)[OFFSET(95)] AS p95_gap
FROM g GROUP BY subtype ORDER BY n_events DESC
