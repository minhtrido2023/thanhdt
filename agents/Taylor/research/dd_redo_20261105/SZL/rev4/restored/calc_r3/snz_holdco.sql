SELECT t.ticker, CAST(t.time AS STRING) AS time, t.Price, t.PB, t.PE, t.BVPS FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
WHERE t.ticker IN ('SNZ','SZL','SZC','SZB') AND t.time = '2026-11-06' ORDER BY t.ticker
