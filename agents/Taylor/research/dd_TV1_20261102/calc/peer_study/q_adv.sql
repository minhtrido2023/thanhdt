SELECT t.ticker, DATE_TRUNC(t.time, MONTH) AS m, t.time, t.Price, t.PE, t.PB
FROM tav2_bq.ticker AS t
WHERE t.ticker IN ('TV2','TV3','TV4') AND t.time >= '2019-01-01'
QUALIFY ROW_NUMBER() OVER (PARTITION BY t.ticker, DATE_TRUNC(t.time, MONTH) ORDER BY t.time DESC)=1
ORDER BY 1,2
