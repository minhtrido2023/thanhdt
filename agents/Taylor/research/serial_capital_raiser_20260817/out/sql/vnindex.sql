
SELECT time, Close FROM `lithe-record-440915-m9.tav2_bq.ticker`
WHERE ticker = 'VNINDEX' AND time >= DATE '2007-01-01' AND Close > 0
ORDER BY time
