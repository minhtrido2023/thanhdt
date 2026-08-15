
WITH div_dedup AS (
  SELECT c.ticker, c.exright_date AS ex_date,
         ROW_NUMBER() OVER (
           PARTITION BY c.ticker, c.exright_date, c.dividend_year, c.dividend_stage_vi
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action` AS c
  WHERE c.event_code = 'DIV' AND c.event_status = 'executed'
    AND c.exright_date IS NOT NULL AND c.value_per_share > 0
),
ev AS (
  SELECT DISTINCT ticker, ex_date FROM div_dedup WHERE rn = 1
  AND ex_date BETWEEN DATE '2014-01-01' AND DATE '2026-06-30'
)
SELECT e.ticker, e.ex_date,
       IFNULL(up.in_universe, FALSE) AS in_universe,
       IFNULL(up.backfilled, FALSE)  AS backfilled
FROM ev AS e
LEFT JOIN `lithe-record-440915-m9.tav2_mike.universe_pit` AS up
  ON up.ticker = e.ticker AND up.time = e.ex_date
