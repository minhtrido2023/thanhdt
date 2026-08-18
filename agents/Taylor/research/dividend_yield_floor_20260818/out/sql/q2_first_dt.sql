
SELECT t.ticker, MIN(t.time) AS first_dt, COUNT(*) AS n_rows
FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
WHERE t.Close IS NOT NULL AND t.Close > 0
GROUP BY t.ticker
