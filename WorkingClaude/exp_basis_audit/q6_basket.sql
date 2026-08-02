-- Impact of the adjusted-Close basis inside custom_basket.py:
--   (a) PIT member ranking  AVG(Volume_3M_P50*Close)  vs  AVG(Volume_3M_P50*Price)
--   (b) cap weights         mcap = Close*OShares      vs  Price*OShares
-- Universe filter mirrors custom_basket (real companies = ICB_Code not null); quarterly, 2008+.
WITH d AS (
  SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q, t.time, t.Close, t.Price,
         t.Volume_3M_P50, t.OShares, t.ICB_Code
  FROM tav2_bq.ticker AS t
  WHERE t.time >= DATE '2008-01-01' AND t.ICB_Code IS NOT NULL
    AND t.Close > 0 AND t.Price > 0 AND t.Volume_3M_P50 IS NOT NULL
),
agg AS (
  SELECT ticker, q, COUNT(*) nd,
         AVG(Volume_3M_P50*Close) AS liq_close,
         AVG(Volume_3M_P50*Price) AS liq_price,
         -- mcap at the LAST session of the quarter (weight basis at a rebalance)
         ARRAY_AGG(Close*OShares  IGNORE NULLS ORDER BY time DESC LIMIT 1)[SAFE_OFFSET(0)] AS mcap_close,
         ARRAY_AGG(Price*OShares  IGNORE NULLS ORDER BY time DESC LIMIT 1)[SAFE_OFFSET(0)] AS mcap_price
  FROM d GROUP BY ticker, q HAVING COUNT(*) >= 20
),
r AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY q ORDER BY liq_close DESC) rk_close,
    ROW_NUMBER() OVER (PARTITION BY q ORDER BY liq_price DESC) rk_price
  FROM agg
)
SELECT q, ticker, nd, liq_close, liq_price, mcap_close, mcap_price, rk_close, rk_price
FROM r WHERE rk_close <= 40 OR rk_price <= 40
ORDER BY q, rk_price
