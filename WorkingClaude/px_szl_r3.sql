SELECT ticker, CAST(time AS STRING) AS time, Close, Price, Volume FROM `lithe-record-440915-m9.tav2_bq.ticker`
WHERE ticker IN ('SZL','SZC','SZB','SNZ') AND time BETWEEN '2025-06-01' AND '2026-11-06' ORDER BY ticker, time
