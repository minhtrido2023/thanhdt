SELECT t.time, t.Close, t.Price, t.Volume FROM tav2_bq.ticker AS t
WHERE t.ticker = 'DCM' AND t.time BETWEEN '2025-09-01' AND '2026-11-06' ORDER BY t.time
