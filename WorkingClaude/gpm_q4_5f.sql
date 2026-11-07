SELECT t.ticker, SUBSTR(t.quarter,1,4) AS yr, ROUND(100*MAX(t.GPM_P0),1) AS gpm_q4
FROM tav2_bq.ticker_financial AS t
WHERE t.ticker IN ('DCM','DPM','DHB') AND SUBSTR(t.quarter,1,4) BETWEEN '2016' AND '2025' AND SUBSTR(t.quarter,5,2)='Q4'
GROUP BY 1,2 ORDER BY 2,1
