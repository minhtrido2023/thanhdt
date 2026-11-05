SELECT t.quarter, t.NP_P0, t.Revenue_P0, t.BVPS, t.OShares, t.ROE_Trailing
FROM tav2_bq.ticker_financial AS t
WHERE t.ticker = 'PVT' AND t.quarter >= '2014Q1'
ORDER BY t.quarter
