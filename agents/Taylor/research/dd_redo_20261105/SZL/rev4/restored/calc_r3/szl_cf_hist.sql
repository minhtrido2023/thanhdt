SELECT f.quarter, f.NP_P0, f.CF_OA_P0, f.CF_Invest_P0 FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
WHERE f.ticker='SZL' AND f.quarter >= '2019Q1' ORDER BY f.quarter
