SELECT t.ticker, t.time, t.Close, t.Price, t.Volume
FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
WHERE t.ticker = 'TCH' AND t.time BETWEEN '2025-08-01' AND '2026-11-06'
ORDER BY t.ticker, t.time
