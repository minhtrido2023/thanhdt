SELECT t.time, t.Price, t.Close, t.Volume FROM tav2_bq.ticker AS t WHERE t.ticker="CSV" AND t.time >= "2025-09-01" ORDER BY t.time
