SELECT t.quarter, t.NP_P0, t.Revenue_P0, t.GPM_P0, t.OShares, t.EBITDA_P0
FROM tav2_bq.ticker_financial AS t
WHERE t.ticker = 'DDV' AND t.quarter >= '2013Q1'
ORDER BY t.quarter
