-- r7: D&A TTM suy từ BQ = EBITDA_P0(TTM) − EBITM_P0(TTM %)×DT TTM(Revenue_P0..P3); quý 4 mỗi năm. Kiểm đối chiếu với BCTC KT 2024/2025.
SELECT DISTINCT t.quarter, t.EBITDA_P0/1e9 AS ebitda_ttm, t.EBITM_P0 AS ebitm_ttm_pct,
  (t.Revenue_P0+t.Revenue_P1+t.Revenue_P2+t.Revenue_P3)/1e9 AS rev_ttm, t.NP_P0/1e9 AS np_q
FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS t
WHERE t.ticker='DCM' AND t.quarter >= '2015Q1' ORDER BY t.quarter
