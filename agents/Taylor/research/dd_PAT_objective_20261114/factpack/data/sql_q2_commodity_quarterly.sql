SELECT c.metric_key, c.source, CONCAT(CAST(EXTRACT(YEAR FROM c.observation_date) AS STRING),'Q',CAST(EXTRACT(QUARTER FROM c.observation_date) AS STRING)) AS quarter,
 COUNT(*) AS n_obs, COUNT(DISTINCT c.value) AS n_distinct, AVG(c.value) AS mean_val, APPROX_QUANTILES(c.value,2)[OFFSET(1)] AS median_val, MIN(c.value) AS min_val, MAX(c.value) AS max_val,
 MIN(c.observation_date) AS first_d, MAX(c.observation_date) AS last_d
FROM tav2_bq.commodity_prices AS c
WHERE c.observation_date>='2020-01-01' AND EXTRACT(DAYOFWEEK FROM c.observation_date) NOT IN (1,7)
 AND ((c.metric_key='yellow_phosphorus' AND c.source='sunsirs' AND c.cadence='daily')
   OR (c.metric_key='coke' AND c.source='sunsirs' AND c.cadence='daily')
   OR (c.metric_key='coking_coal' AND c.source='trading_economics' AND c.cadence='daily')
   OR (c.metric_key='sulfur' AND c.source='trading_economics' AND c.cadence='daily')
   OR (c.metric_key='phosphate_rock_cny' AND c.source='trading_economics' AND c.cadence='daily')
   OR (c.metric_key='ferrosilicon' AND c.source='sunsirs' AND c.cadence='daily'))
GROUP BY 1,2,3 ORDER BY 1,3
