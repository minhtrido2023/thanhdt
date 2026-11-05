SELECT t.ticker, t.time, t.Close, t.Price, t.Volume
FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
WHERE t.ticker IN ('MBB','FPT','HPG','HHS') AND t.time BETWEEN '2025-09-01' AND '2026-11-04'
ORDER BY t.ticker, t.time
