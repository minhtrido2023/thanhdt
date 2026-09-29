
SELECT t.time AS dt, t.Close AS c
FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
WHERE t.ticker = 'VNINDEX' AND t.time >= DATE '2012-06-01' AND t.Close > 0
ORDER BY t.time
