WITH uni AS (
  SELECT ticker FROM tav2_mike.universe_pit
  WHERE time = (SELECT MAX(time) FROM tav2_mike.universe_pit) AND in_universe
)
SELECT t.time, t.ticker, t.Close
FROM tav2_bq.ticker AS t
JOIN uni ON uni.ticker = t.ticker
WHERE t.time >= '2018-01-01'
ORDER BY t.ticker, t.time
