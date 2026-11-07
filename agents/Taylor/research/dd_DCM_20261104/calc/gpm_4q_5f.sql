WITH q AS (SELECT DISTINCT ticker, quarter, GPM_P0 FROM tav2_bq.ticker_financial AS t WHERE t.ticker IN ('DCM','DPM','DHB') AND SUBSTR(t.quarter,1,4) BETWEEN '2016' AND '2025')
SELECT ticker, SUBSTR(quarter,1,4) AS yr, COUNT(*) n, ROUND(100*AVG(GPM_P0),1) gpm4q FROM q GROUP BY 1,2 ORDER BY 2,1
