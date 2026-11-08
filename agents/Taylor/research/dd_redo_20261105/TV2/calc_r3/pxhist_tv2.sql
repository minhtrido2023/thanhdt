SELECT EXTRACT(YEAR FROM t.time) AS y, MIN(t.Price) AS min_price, MAX(t.Price) AS max_price, MIN(t.Close) AS min_close, APPROX_QUANTILES(t.PB,2)[OFFSET(1)] AS pb_med, MIN(t.PB) AS pb_min, MAX(t.PB) AS pb_max, APPROX_QUANTILES(t.PE,2)[OFFSET(1)] AS pe_med
FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t WHERE t.ticker='TV2' AND t.time>='2017-01-01' AND t.time<='2026-11-06' GROUP BY y ORDER BY y
