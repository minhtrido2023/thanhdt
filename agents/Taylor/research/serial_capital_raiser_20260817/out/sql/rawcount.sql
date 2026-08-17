
SELECT COUNT(*) AS n_raw, COUNT(DISTINCT id) AS n_ids
FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
WHERE event_code = 'ISS' AND event_status = 'executed' AND exright_date IS NOT NULL
  AND exright_date BETWEEN DATE '2010-01-01' AND DATE '2026-06-15'
