SELECT t.ticker, t.time, t.Close, t.Price, t.Volume
FROM tav2_bq.ticker AS t
WHERE t.ticker = 'DGC' AND t.time >= '2025-09-01' AND t.time <= '2026-11-06'
ORDER BY t.time
