
WITH div_dedup AS (
  SELECT c.ticker, c.exright_date AS ex_date, c.value_per_share,
         ROW_NUMBER() OVER (
           PARTITION BY c.ticker, c.exright_date, c.dividend_year, c.dividend_stage_vi
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action` AS c
  WHERE c.event_code = 'DIV'
    AND c.event_status = 'executed'
    AND c.exright_date IS NOT NULL
    AND c.value_per_share > 0
)
SELECT ticker, ex_date, SUM(value_per_share) AS div_total, COUNT(*) AS n_tranche
FROM div_dedup
WHERE rn = 1
GROUP BY ticker, ex_date
HAVING ex_date BETWEEN DATE '2014-01-01' AND DATE '2026-06-30'
ORDER BY ticker, ex_date
