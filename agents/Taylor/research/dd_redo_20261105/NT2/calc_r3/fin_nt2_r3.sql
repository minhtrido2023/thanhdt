SELECT DISTINCT f.ticker, f.quarter, f.time, f.Revenue_P0, f.NP_P0, f.CF_Invest_P0, f.CF_OA_P0
FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
WHERE f.ticker = 'NT2' AND f.time >= '2014-10-01'
ORDER BY f.quarter
