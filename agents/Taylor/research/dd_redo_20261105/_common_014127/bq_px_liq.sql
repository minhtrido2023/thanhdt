SELECT t.ticker, t.time, t.Close, t.Price, t.Volume
FROM tav2_bq.ticker AS t
WHERE t.ticker IN ('DGC','DDV','PVP','PVT') AND t.time >= '2025-09-01' AND t.time <= '2026-11-04'
ORDER BY t.ticker, t.time
