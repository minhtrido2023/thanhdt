SELECT f.quarter, f.Release_Date, f.NP_P0, f.NP_P0+f.NP_P1+f.NP_P2+f.NP_P3 AS NP_TTM, f.PE, f.PB, f.BVPS, f.OShares, f.DY, f.EPS
FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f WHERE f.ticker="TV2" AND f.time>="2016-01-01" ORDER BY f.time
