
WITH raw AS (
  SELECT c.*,
    CASE c.issue_method_code WHEN 'DIV' THEN 'STOCK_DIVIDEND'
                             WHEN 'Bonus' THEN 'BONUS' END AS subtype,
    ROW_NUMBER() OVER (
      PARTITION BY c.ticker, c.exright_date, c.issue_method_code,
                   CAST(c.exercise_ratio AS STRING), CAST(c.issue_volumn AS STRING)
      ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action` c
  WHERE c.event_code='ISS' AND c.event_status='executed'
    AND c.issue_method_code IN ('DIV','Bonus')
    AND c.exright_date BETWEEN DATE '2014-01-01' AND DATE '2026-06-30'
    AND c.exercise_ratio > 0
), ev AS (
  SELECT ticker, exright_date AS ex_date,
    SUM(exercise_ratio) AS ratio_total,
    SUM(IFNULL(issue_volumn,0)) AS issue_volume,
    MAX(listing_date) AS listing_date,
    COUNT(DISTINCT subtype) AS n_subtypes,
    STRING_AGG(DISTINCT subtype ORDER BY subtype) AS subtype_list,
    COUNT(*) AS n_components
  FROM raw WHERE rn=1 GROUP BY ticker, ex_date
)

SELECT e.ticker,e.ex_date,IFNULL(u.in_universe,FALSE) in_universe,
  IFNULL(u.backfilled,FALSE) backfilled
FROM ev e LEFT JOIN `lithe-record-440915-m9.tav2_mike.universe_pit` u
ON u.ticker=e.ticker AND u.time=e.ex_date
