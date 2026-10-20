WITH a AS (SELECT ticker, quarter, NP_P0, ROIC3Y, CF_OA_P0, FSCORE, Release_Date FROM tav2_pin.ticker_financial_pin_202607 WHERE time BETWEEN '2010-01-01' AND '2014-12-31'),
b AS (SELECT ticker, quarter, NP_P0, ROIC3Y, CF_OA_P0, FSCORE, Release_Date FROM tav2_pin.ticker_financial_pin_202610 WHERE time BETWEEN '2010-01-01' AND '2014-12-31')
SELECT COUNT(*) AS n_pairs,
  COUNTIF(a.ticker IS NULL) AS only_in_202610, COUNTIF(b.ticker IS NULL) AS only_in_202607,
  COUNTIF(a.NP_P0 IS DISTINCT FROM b.NP_P0) AS np_changed, COUNTIF(a.ROIC3Y IS DISTINCT FROM b.ROIC3Y) AS roic3y_changed,
  COUNTIF(a.CF_OA_P0 IS DISTINCT FROM b.CF_OA_P0) AS cfoa_changed, COUNTIF(a.FSCORE IS DISTINCT FROM b.FSCORE) AS fscore_changed,
  COUNTIF(a.Release_Date IS DISTINCT FROM b.Release_Date) AS rd_changed
FROM a FULL OUTER JOIN b USING (ticker, quarter)
