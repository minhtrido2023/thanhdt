SELECT EXTRACT(YEAR FROM observation_date) yr,
 ROUND(AVG(IF(metric_key='urea',value,NULL)),1) urea, ROUND(AVG(IF(metric_key='brent',value,NULL)),1) brent
FROM `lithe-record-440915-m9.tav2_bq.commodity_prices`
WHERE source='worldbank_cmo' AND metric_key IN ('urea','brent') AND observation_date>='2014-01-01'
GROUP BY yr ORDER BY yr
