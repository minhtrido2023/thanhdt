-- Tài chính theo quý cho nhóm peer (để tính vốn hoá, LNST TTM, ROE, Oshares). Release_Date dùng cho PIT.
SELECT f.ticker, f.time, f.quarter, f.Release_Date, f.OShares, f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7,
       f.ROE_Trailing, f.ROE3Y, f.EPS, f.BVPS, f.Debt_Eq_P0, f.Revenue_P0, f.Revenue_P4, f.Dividend_1Y, f.Dividend_3Y
FROM tav2_bq.ticker_financial AS f
WHERE f.ticker IN (SELECT DISTINCT t.ticker FROM tav2_bq.ticker AS t WHERE t.ICB_Code = 7535 AND t.time >= '2019-01-01' UNION DISTINCT SELECT 'TV1')
  AND f.time >= '2017-01-01'
ORDER BY f.ticker, f.time
