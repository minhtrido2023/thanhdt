WITH uni AS (
  SELECT ticker FROM tav2_mike.universe_pit
  WHERE time = (SELECT MAX(time) FROM tav2_mike.universe_pit) AND in_universe
),
latest_fin AS (
  SELECT f.ticker, f.OShares,
         ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) rn
  FROM tav2_bq.ticker_financial AS f
  JOIN uni ON uni.ticker = f.ticker
  WHERE f.OShares IS NOT NULL
),
latest_px AS (
  SELECT t.ticker, t.Close,
         ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) rn
  FROM tav2_bq.ticker AS t
  JOIN uni ON uni.ticker = t.ticker
)
SELECT p.ticker, p.Close, fi.OShares, p.Close*fi.OShares AS mktcap
FROM latest_px p JOIN latest_fin fi ON fi.ticker=p.ticker AND fi.rn=1
WHERE p.rn=1
