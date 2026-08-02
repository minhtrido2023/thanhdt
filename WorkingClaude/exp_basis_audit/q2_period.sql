-- IN-PERIOD CONSTANCY TEST (same method used for PE/ps on 2026-08-02)
-- proportional cols (PE,PB,PCF): col/basis must be constant within a report period (ID_Release)
-- DY (inverse):                  col*basis must be constant
-- discriminating power:          how often does Close/Price itself move inside a period?
WITH b AS (
  SELECT t.ticker, t.ID_Release, t.time, t.Price, t.Close, t.PE, t.PB, t.PCF, t.DY,
         CASE WHEN t.time < DATE '2014-01-01' THEN 'A_2007_2013' ELSE 'B_2014_2026' END AS era
  FROM tav2_bq.ticker AS t
  WHERE t.time >= DATE '2007-01-01' AND t.Price > 0 AND t.Close > 0 AND t.ID_Release IS NOT NULL
),
p AS (
  SELECT era, ticker, ID_Release, COUNT(*) AS nd,
    -- relative spread of each hypothesis within the period
    SAFE_DIVIDE(MAX(SAFE_DIVIDE(Close,Price))-MIN(SAFE_DIVIDE(Close,Price)), AVG(SAFE_DIVIDE(Close,Price))) AS sp_adj,
    COUNTIF(PE>0) AS n_pe,
    SAFE_DIVIDE(MAX(SAFE_DIVIDE(PE,Price))-MIN(SAFE_DIVIDE(PE,Price)), AVG(SAFE_DIVIDE(PE,Price))) AS sp_pe_p,
    SAFE_DIVIDE(MAX(SAFE_DIVIDE(PE,Close))-MIN(SAFE_DIVIDE(PE,Close)), AVG(SAFE_DIVIDE(PE,Close))) AS sp_pe_c,
    COUNTIF(PB>0) AS n_pb,
    SAFE_DIVIDE(MAX(SAFE_DIVIDE(PB,Price))-MIN(SAFE_DIVIDE(PB,Price)), AVG(SAFE_DIVIDE(PB,Price))) AS sp_pb_p,
    SAFE_DIVIDE(MAX(SAFE_DIVIDE(PB,Close))-MIN(SAFE_DIVIDE(PB,Close)), AVG(SAFE_DIVIDE(PB,Close))) AS sp_pb_c,
    COUNTIF(PCF>0) AS n_pcf,
    SAFE_DIVIDE(MAX(SAFE_DIVIDE(PCF,Price))-MIN(SAFE_DIVIDE(PCF,Price)), AVG(SAFE_DIVIDE(PCF,Price))) AS sp_pcf_p,
    SAFE_DIVIDE(MAX(SAFE_DIVIDE(PCF,Close))-MIN(SAFE_DIVIDE(PCF,Close)), AVG(SAFE_DIVIDE(PCF,Close))) AS sp_pcf_c,
    COUNTIF(DY>0) AS n_dy,
    SAFE_DIVIDE(MAX(DY*Price)-MIN(DY*Price), AVG(DY*Price)) AS sp_dy_p,
    SAFE_DIVIDE(MAX(DY*Close)-MIN(DY*Close), AVG(DY*Close)) AS sp_dy_c
  FROM b GROUP BY era, ticker, ID_Release
  HAVING COUNT(*) >= 5
)
SELECT era, COUNT(*) AS n_periods,
  ROUND(100*AVG(CASE WHEN sp_adj > 1e-4 THEN 1 ELSE 0 END),1) AS pct_periods_adj_moves,
  COUNTIF(n_pe>=5) AS np_pe,
  ROUND(100*SAFE_DIVIDE(COUNTIF(n_pe>=5 AND sp_pe_p<1e-4), COUNTIF(n_pe>=5)),1) AS pe_price_pct,
  ROUND(100*SAFE_DIVIDE(COUNTIF(n_pe>=5 AND sp_pe_c<1e-4), COUNTIF(n_pe>=5)),1) AS pe_close_pct,
  COUNTIF(n_pb>=5) AS np_pb,
  ROUND(100*SAFE_DIVIDE(COUNTIF(n_pb>=5 AND sp_pb_p<1e-4), COUNTIF(n_pb>=5)),1) AS pb_price_pct,
  ROUND(100*SAFE_DIVIDE(COUNTIF(n_pb>=5 AND sp_pb_c<1e-4), COUNTIF(n_pb>=5)),1) AS pb_close_pct,
  COUNTIF(n_pcf>=5) AS np_pcf,
  ROUND(100*SAFE_DIVIDE(COUNTIF(n_pcf>=5 AND sp_pcf_p<1e-4), COUNTIF(n_pcf>=5)),1) AS pcf_price_pct,
  ROUND(100*SAFE_DIVIDE(COUNTIF(n_pcf>=5 AND sp_pcf_c<1e-4), COUNTIF(n_pcf>=5)),1) AS pcf_close_pct,
  COUNTIF(n_dy>=5) AS np_dy,
  ROUND(100*SAFE_DIVIDE(COUNTIF(n_dy>=5 AND sp_dy_p<1e-4), COUNTIF(n_dy>=5)),1) AS dy_price_pct,
  ROUND(100*SAFE_DIVIDE(COUNTIF(n_dy>=5 AND sp_dy_c<1e-4), COUNTIF(n_dy>=5)),1) AS dy_close_pct
FROM p GROUP BY era ORDER BY era
