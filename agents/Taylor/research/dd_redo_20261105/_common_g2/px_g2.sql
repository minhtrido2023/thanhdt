SELECT t.ticker, t.time, t.Open, t.High, t.Low, t.Close, t.Price, t.Volume
FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
WHERE t.ticker IN ('SIP','SCL','TV1','TV2') AND t.time BETWEEN '2026-03-01' AND '2026-11-04'
ORDER BY t.ticker, t.time
