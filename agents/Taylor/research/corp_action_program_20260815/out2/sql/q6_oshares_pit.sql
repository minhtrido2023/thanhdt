
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
),
j AS (
  SELECT e.ticker, e.ex_date, tf.OShares, tf.Release_Date,
         ROW_NUMBER() OVER (PARTITION BY e.ticker, e.ex_date
                            ORDER BY tf.Release_Date DESC) AS rn
  FROM ev AS e
  JOIN `lithe-record-440915-m9.tav2_bq.ticker_financial` AS tf
    ON tf.ticker = e.ticker
   AND tf.Release_Date IS NOT NULL
   AND tf.Release_Date < e.ex_date
   AND tf.OShares IS NOT NULL AND tf.OShares > 0
)
SELECT ticker, ex_date, OShares AS oshares, Release_Date AS oshares_release
FROM j WHERE rn = 1
