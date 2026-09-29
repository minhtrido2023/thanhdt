
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
  SELECT subtype, ticker, exright_date, listing_date, public_date, record_date, event_title_vi,
         DATE_DIFF(exright_date, listing_date, DAY) AS gap_ex_minus_listing
  FROM ev
  WHERE subtype IN ('RIGHTS', 'PRIVATE_PLACEMENT') AND listing_date IS NOT NULL
    AND exright_date IS NOT NULL
),
s AS (
  SELECT *,
    CASE WHEN ABS(gap_ex_minus_listing) BETWEEN 5 AND 15 THEN 'A_gap_small_5_15'
         WHEN ABS(gap_ex_minus_listing) > 30 THEN 'B_gap_large_gt30' END AS stratum
  FROM g
),
r AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY stratum
             ORDER BY FARM_FINGERPRINT(CONCAT(ticker, CAST(exright_date AS STRING)))) AS rk
  FROM s WHERE stratum IS NOT NULL
)
SELECT stratum, ticker, subtype, exright_date, listing_date, record_date, public_date,
       gap_ex_minus_listing, event_title_vi
FROM r WHERE rk <= 10 ORDER BY stratum, rk
