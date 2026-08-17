
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
ais AS (
  SELECT ticker, effective_date FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
  WHERE event_code = 'AIS' AND effective_date IS NOT NULL
),
cand AS (
  SELECT e.subtype, e.ticker, e.exright_date, e.listing_date
  FROM ev e WHERE e.listing_date IS NOT NULL AND e.exright_date IS NOT NULL
),
scoped AS (
  SELECT c.* FROM cand c
  WHERE EXISTS(SELECT 1 FROM ais a WHERE a.ticker = c.ticker
                 AND ABS(DATE_DIFF(a.effective_date, c.listing_date, DAY)) <= 365)
),
j AS (
  SELECT s.subtype,
    EXISTS(SELECT 1 FROM ais a WHERE a.ticker = s.ticker
             AND a.effective_date = s.listing_date) AS hit_listing,
    EXISTS(SELECT 1 FROM ais a WHERE a.ticker = s.ticker
             AND a.effective_date = s.exright_date) AS hit_exright
  FROM scoped s
)
SELECT subtype, COUNT(*) AS n_scoped,
  COUNTIF(hit_listing) AS n_hit_listing,
  ROUND(100 * COUNTIF(hit_listing) / COUNT(*), 1) AS pct_hit_listing,
  COUNTIF(hit_exright) AS n_hit_exright_placebo,
  ROUND(100 * COUNTIF(hit_exright) / COUNT(*), 1) AS pct_hit_exright_placebo
FROM j GROUP BY subtype ORDER BY n_scoped DESC
