SELECT f.ticker, f.quarter, f.Cash_P0, f.NP_P0, f.Revenue_P0, f.EBITM_P0, f.NPM_P0, f.StDebt_P0, f.LtDebt_P0
FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
WHERE f.ticker = 'DDV' AND f.quarter BETWEEN '2014Q1' AND '2026Q4'
ORDER BY f.quarter
