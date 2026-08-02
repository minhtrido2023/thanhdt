-- RECONSTRUCTION TEST: which price basis reproduces the stored ratio's denominator?
-- PE: implied EPS_ttm = basis/PE  vs  target Sum(NP_P0..P3)/OShares
-- PB: implied BVPS    = basis/PB  vs  target BVPS column
WITH b AS (
  SELECT FORMAT_DATE('%Y', t.time) AS yr, t.ticker, t.time,
         t.Price, t.Close, t.PE, t.PB, t.OShares, t.BVPS,
         SAFE_DIVIDE(t.NP_P0 + t.NP_P1 + t.NP_P2 + t.NP_P3, t.OShares) AS eps_ttm
  FROM tav2_bq.ticker AS t
  WHERE t.time >= DATE '2007-01-01' AND t.Price > 0 AND t.Close > 0
)
SELECT yr,
  COUNTIF(PE > 0 AND eps_ttm > 0) AS n_pe,
  ROUND(100*SAFE_DIVIDE(COUNTIF(PE>0 AND eps_ttm>0 AND ABS(SAFE_DIVIDE(Price/PE, eps_ttm)-1) < 0.01),
                        COUNTIF(PE>0 AND eps_ttm>0)),1) AS pe_price_pct,
  ROUND(100*SAFE_DIVIDE(COUNTIF(PE>0 AND eps_ttm>0 AND ABS(SAFE_DIVIDE(Close/PE, eps_ttm)-1) < 0.01),
                        COUNTIF(PE>0 AND eps_ttm>0)),1) AS pe_close_pct,
  COUNTIF(PB > 0 AND BVPS > 0) AS n_pb,
  ROUND(100*SAFE_DIVIDE(COUNTIF(PB>0 AND BVPS>0 AND ABS(SAFE_DIVIDE(Price/PB, BVPS)-1) < 0.01),
                        COUNTIF(PB>0 AND BVPS>0)),1) AS pb_price_pct,
  ROUND(100*SAFE_DIVIDE(COUNTIF(PB>0 AND BVPS>0 AND ABS(SAFE_DIVIDE(Close/PB, BVPS)-1) < 0.01),
                        COUNTIF(PB>0 AND BVPS>0)),1) AS pb_close_pct,
  ROUND(APPROX_QUANTILES(SAFE_DIVIDE(Close,Price), 100)[OFFSET(50)],4) AS med_close_over_price
FROM b GROUP BY yr ORDER BY yr
