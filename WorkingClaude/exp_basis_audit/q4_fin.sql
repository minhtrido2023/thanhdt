-- ticker_financial: PS / PEG / DY reconstruction, incl. pre-2014
WITH b AS (
  SELECT f.ticker, f.time, FORMAT_DATE('%Y', f.time) AS yr, f.Price, f.Close,
         f.PS, f.PEG, f.PE, f.DY, f.OShares, f.Dividend_1Y, f.EPS_P0, f.BVPS, f.PB,
         (f.Revenue_P0+f.Revenue_P1+f.Revenue_P2+f.Revenue_P3) AS rev_ttm,
         SAFE_DIVIDE(f.NP_P0, f.NP_P4) - 1 AS g
  FROM tav2_bq.ticker_financial AS f
  WHERE f.Price > 0 AND f.Close > 0
)
SELECT yr,
  COUNTIF(PS>0 AND rev_ttm>0 AND OShares>0) AS n_ps,
  ROUND(100*SAFE_DIVIDE(COUNTIF(PS>0 AND rev_ttm>0 AND OShares>0 AND ABS(SAFE_DIVIDE(Price*OShares/rev_ttm, PS)-1)<0.01),
        COUNTIF(PS>0 AND rev_ttm>0 AND OShares>0)),1) AS ps_price_pct,
  ROUND(100*SAFE_DIVIDE(COUNTIF(PS>0 AND rev_ttm>0 AND OShares>0 AND ABS(SAFE_DIVIDE(Close*OShares/rev_ttm, PS)-1)<0.01),
        COUNTIF(PS>0 AND rev_ttm>0 AND OShares>0)),1) AS ps_close_pct,
  COUNTIF(DY>0 AND Dividend_1Y>0) AS n_dy,
  ROUND(100*SAFE_DIVIDE(COUNTIF(DY>0 AND Dividend_1Y>0 AND ABS(SAFE_DIVIDE(SAFE_DIVIDE(Dividend_1Y,Price)*100, DY)-1)<0.02),
        COUNTIF(DY>0 AND Dividend_1Y>0)),1) AS dy_price_pct100,
  ROUND(100*SAFE_DIVIDE(COUNTIF(DY>0 AND Dividend_1Y>0 AND ABS(SAFE_DIVIDE(SAFE_DIVIDE(Dividend_1Y,Close)*100, DY)-1)<0.02),
        COUNTIF(DY>0 AND Dividend_1Y>0)),1) AS dy_close_pct100,
  COUNTIF(PEG IS NOT NULL AND PE>0 AND g IS NOT NULL AND ABS(g)>0.01) AS n_peg,
  ROUND(100*SAFE_DIVIDE(COUNTIF(PEG IS NOT NULL AND PE>0 AND ABS(g)>0.01 AND ABS(SAFE_DIVIDE(SAFE_DIVIDE(PE, g*100), PEG)-1)<0.02),
        COUNTIF(PEG IS NOT NULL AND PE>0 AND g IS NOT NULL AND ABS(g)>0.01)),1) AS peg_from_pe_pct,
  COUNTIF(PB>0 AND BVPS>0) AS n_pb,
  ROUND(100*SAFE_DIVIDE(COUNTIF(PB>0 AND BVPS>0 AND ABS(SAFE_DIVIDE(Price/PB,BVPS)-1)<0.01), COUNTIF(PB>0 AND BVPS>0)),1) AS pb_price_pct
FROM b GROUP BY yr ORDER BY yr
