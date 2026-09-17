SELECT c.id, COUNT(p.time) n_prune_days
FROM tav2_bq.corporate_action AS c
JOIN tav2_bq.ticker_prune AS p ON p.ticker=c.ticker AND p.time BETWEEN DATE_SUB(c.exright_date, INTERVAL 30 DAY) AND c.exright_date
WHERE c.event_code='DIV' AND c.exright_date >= '2014-01-01'
GROUP BY 1
