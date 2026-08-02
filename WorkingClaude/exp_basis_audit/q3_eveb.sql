-- EVEB is AFFINE in price (EV = mcap + netdebt), so ratio-constancy does not apply.
-- Within a report period netdebt/EBITDA is constant => EVEB = (OShares/EBITDA)*basis + const
-- => the correct basis gives CORR(EVEB, basis) = 1 EXACTLY.
WITH b AS (
  SELECT t.ticker, t.ID_Release, t.Price, t.Close, t.EVEB,
         CASE WHEN t.time < DATE '2014-01-01' THEN 'A_2007_2013' ELSE 'B_2014_2026' END AS era
  FROM tav2_bq.ticker AS t
  WHERE t.time >= DATE '2007-01-01' AND t.Price > 0 AND t.Close > 0
    AND t.ID_Release IS NOT NULL AND t.EVEB IS NOT NULL
),
p AS (
  SELECT era, ticker, ID_Release, COUNT(*) nd,
         CORR(EVEB, Price) AS c_p, CORR(EVEB, Close) AS c_c,
         SAFE_DIVIDE(MAX(SAFE_DIVIDE(Close,Price))-MIN(SAFE_DIVIDE(Close,Price)), AVG(SAFE_DIVIDE(Close,Price))) AS sp_adj
  FROM b GROUP BY era, ticker, ID_Release HAVING COUNT(*) >= 10
)
SELECT era, COUNT(*) n_periods,
  ROUND(100*SAFE_DIVIDE(COUNTIF(sp_adj>1e-4), COUNT(*)),1) AS pct_adj_moves,
  ROUND(100*SAFE_DIVIDE(COUNTIF(ABS(c_p) > 0.99999), COUNT(*)),1) AS eveb_price_pct,
  ROUND(100*SAFE_DIVIDE(COUNTIF(ABS(c_c) > 0.99999), COUNT(*)),1) AS eveb_close_pct,
  ROUND(AVG(ABS(c_p)),5) AS avg_corr_price, ROUND(AVG(ABS(c_c)),5) AS avg_corr_close
FROM p GROUP BY era ORDER BY era
