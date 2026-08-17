
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
j AS (
  SELECT e.subtype, e.ticker, e.exright_date, e.listing_date,
    EXISTS(SELECT 1 FROM ais a WHERE a.ticker = e.ticker
             AND a.effective_date = e.listing_date) AS ais_exact,
    EXISTS(SELECT 1 FROM ais a WHERE a.ticker = e.ticker
             AND ABS(DATE_DIFF(a.effective_date, e.listing_date, DAY)) <= 3) AS ais_pm3
  FROM ev e WHERE e.listing_date IS NOT NULL
)
SELECT subtype, COUNT(*) AS n_with_listing,
  COUNTIF(ais_exact) AS n_ais_exact,
  ROUND(100 * COUNTIF(ais_exact) / COUNT(*), 1) AS pct_ais_exact,
  COUNTIF(ais_pm3) AS n_ais_pm3,
  ROUND(100 * COUNTIF(ais_pm3) / COUNT(*), 1) AS pct_ais_pm3
FROM j GROUP BY subtype ORDER BY n_with_listing DESC
