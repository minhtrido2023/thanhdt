SELECT t.ticker, t.time, t.Open, t.High, t.Low, t.Close, t.Price, t.Volume
FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
WHERE t.ticker = 'SCL' AND t.time BETWEEN '2025-08-01' AND '2026-11-06'
ORDER BY t.time
