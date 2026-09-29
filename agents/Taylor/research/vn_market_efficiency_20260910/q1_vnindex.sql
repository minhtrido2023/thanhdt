SELECT time, Close
FROM `lithe-record-440915-m9.tav2_bq.ticker`
WHERE ticker = 'VNINDEX' AND Close IS NOT NULL AND Close > 0
ORDER BY time
