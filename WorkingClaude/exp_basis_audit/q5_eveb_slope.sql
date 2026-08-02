-- EVEB EXACT test: EVEB = (basis*OShares + NetDebt)/EBITDA_P0  =>  dEVEB/dbasis = OShares/EBITDA_P0
-- (slope derived from the period's min/max rows; OShares & EBITDA_P0 constant inside a report period)
WITH b AS (
  SELECT t.ticker, t.ID_Release, t.Price, t.Close, t.EVEB, t.OShares, t.EBITDA_P0,
         CASE WHEN t.time < DATE '2014-01-01' THEN 'A_2007_2013' ELSE 'B_2014_2026' END AS era
  FROM tav2_bq.ticker AS t
  WHERE t.time >= DATE '2007-01-01' AND t.Price>0 AND t.Close>0 AND t.EVEB IS NOT NULL
    AND t.OShares>0 AND t.EBITDA_P0>0
),
p AS (
  SELECT era, ticker, ID_Release, COUNT(*) nd,
    SAFE_DIVIDE(MAX(EVEB)-MIN(EVEB), MAX(Price)-MIN(Price)) AS slope_p,
    SAFE_DIVIDE(MAX(EVEB)-MIN(EVEB), MAX(Close)-MIN(Close)) AS slope_c,
    ANY_VALUE(SAFE_DIVIDE(OShares, EBITDA_P0)) AS expect_slope
  FROM b GROUP BY era, ticker, ID_Release
  HAVING COUNT(*)>=10 AND MAX(Price)>MIN(Price) AND MAX(Close)>MIN(Close) AND MAX(EVEB)>MIN(EVEB)
)
SELECT era, COUNT(*) n_periods,
  ROUND(100*SAFE_DIVIDE(COUNTIF(ABS(SAFE_DIVIDE(slope_p,expect_slope)-1)<0.01), COUNT(*)),1) AS eveb_price_pct,
  ROUND(100*SAFE_DIVIDE(COUNTIF(ABS(SAFE_DIVIDE(slope_c,expect_slope)-1)<0.01), COUNT(*)),1) AS eveb_close_pct,
  ROUND(APPROX_QUANTILES(ABS(SAFE_DIVIDE(slope_p,expect_slope)-1),100)[OFFSET(50)],5) AS med_relerr_price,
  ROUND(APPROX_QUANTILES(ABS(SAFE_DIVIDE(slope_c,expect_slope)-1),100)[OFFSET(50)],5) AS med_relerr_close
FROM p GROUP BY era ORDER BY era
