SELECT DISTINCT f.quarter, f.AR_P0, f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3
FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
WHERE f.ticker = 'NT2' AND f.time >= '2015-01-01'
ORDER BY f.quarter
