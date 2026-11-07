SELECT t.ticker, t.quarter, t.NP_P0, t.Revenue_P0, t.GPM_P0, t.ROIC5Y, t.ROIC_Min5Y, t.ROIC3Y, t.ROIC_Min3Y, t.ROIC10Y, t.ROIC_Min10Y, t.ROE5Y, t.ROE_Min5Y, t.ROE3Y
FROM tav2_bq.ticker_financial AS t
WHERE t.ticker IN ("DDV","DPM","DCM","LAS","BFC","VAF","NFC","SFG","DGC") AND t.quarter >= '2015Q1'
ORDER BY t.ticker, t.quarter
