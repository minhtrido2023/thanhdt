SELECT SUBSTR(quarter,1,4) yr, COUNT(DISTINCT quarter) nq, ROUND(SUM(NP_P0)/1e9,1) np_sum_ty
FROM (SELECT DISTINCT quarter, NP_P0 FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` t WHERE t.ticker='DCM')
GROUP BY yr ORDER BY yr
